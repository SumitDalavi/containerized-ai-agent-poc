"""
Containerized AI Agent
======================
An AI agent with sandboxed tool execution, resource limits, and full audit logging.
"""
from __future__ import annotations
import os, uuid
from dataclasses import dataclass, field
from typing import List, Optional

from sandbox.executor import run_in_sandbox, ALLOWED_COMMANDS
from tools.file_tool import read_file, write_file, list_files
from monitoring.audit_log import log_tool_call, log_agent_decision, log_session_start, log_session_end

def is_live_openai_key(key: str = None) -> bool:
    if key is None:
        key = os.getenv("OPENAI_API_KEY", "")
    return bool(key) and key.startswith("sk-") and not key.startswith("sk-dummy") and len(key) >= 20

try:
    from openai import OpenAI
    _LLM = is_live_openai_key()
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "")) if _LLM else None
except Exception:
    _LLM = False
    _client = None


SYSTEM_PROMPT = """You are a sandboxed AI agent. You can use tools to complete tasks.
Available tools:
- shell(command): Run a command. Allowed: {allowed}
- read_file(path): Read a file from the workspace
- write_file(path, content): Write content to a file in the workspace
- list_files(path): List files in a directory

Always think step by step. State your reasoning before each tool call.
When done, respond with FINAL_ANSWER: <your answer>
""".format(allowed=", ".join(sorted(ALLOWED_COMMANDS)))


@dataclass
class AgentStep:
    thought: str
    tool: str
    tool_input: str
    output: str
    success: bool


@dataclass
class AgentResult:
    agent_id: str
    task: str
    steps: List[AgentStep] = field(default_factory=list)
    final_answer: str = ""
    success: bool = False
    total_steps: int = 0


class ContainerizedAgent:
    def __init__(self, agent_id: Optional[str] = None, max_steps: int = 10):
        self.agent_id = agent_id or str(uuid.uuid4())[:8]
        self.max_steps = max_steps

    def run(self, task: str) -> AgentResult:
        result = AgentResult(agent_id=self.agent_id, task=task)
        log_session_start(self.agent_id, task)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Task: {task}"},
        ]

        for step_num in range(self.max_steps):
            if _LLM:
                response = _client.chat.completions.create(
                    model="gpt-4o-mini", messages=messages, max_tokens=500, temperature=0.1
                )
                content = response.choices[0].message.content
            else:
                # Deterministic mock for testing without API key
                content = self._mock_step(task, step_num)

            messages.append({"role": "assistant", "content": content})

            if "FINAL_ANSWER:" in content:
                result.final_answer = content.split("FINAL_ANSWER:")[-1].strip()
                result.success = True
                break

            # Parse tool call from response
            tool, tool_input, output = self._dispatch_tool(content)
            step = AgentStep(
                thought=content[:200], tool=tool,
                tool_input=tool_input, output=output, success=True,
            )
            result.steps.append(step)
            log_agent_decision(self.agent_id, content[:200], tool, tool_input)
            messages.append({"role": "user", "content": f"Tool output: {output}"})

        result.total_steps = len(result.steps)
        log_session_end(self.agent_id, "success" if result.success else "max_steps", result.total_steps)
        return result

    def _dispatch_tool(self, content: str):
        """Parse and dispatch a tool call from agent response."""
        import re
        shell_m = re.search(r"shell\((.+?)\)", content, re.DOTALL)
        read_m  = re.search(r"read_file\((.+?)\)", content, re.DOTALL)
        write_m = re.search(r"write_file\((.+?),\s*(.+?)\)", content, re.DOTALL)
        list_m  = re.search(r"list_files\((.*)\)", content, re.DOTALL)

        start_t = __import__("time").time()
        if shell_m:
            cmd = shell_m.group(1).strip().strip("'"")
            exec_r = run_in_sandbox(cmd)
            dur = (__import__("time").time() - start_t) * 1000
            log_tool_call(self.agent_id, "shell", cmd, exec_r.output,
                          exec_r.success, dur, sandboxed=exec_r.sandboxed, error=exec_r.error)
            return "shell", cmd, exec_r.output or exec_r.error or ""
        elif read_m:
            path = read_m.group(1).strip().strip("'"")
            out = read_file(path)
            log_tool_call(self.agent_id, "read_file", path, out, True, 0)
            return "read_file", path, out
        elif write_m:
            path, content_arg = write_m.group(1).strip().strip("'""), write_m.group(2).strip().strip("'"")
            out = write_file(path, content_arg)
            log_tool_call(self.agent_id, "write_file", path, out, True, 0)
            return "write_file", path, out
        elif list_m:
            path = list_m.group(1).strip().strip("'"") or "."
            out = str(list_files(path))
            log_tool_call(self.agent_id, "list_files", path, out, True, 0)
            return "list_files", path, out
        else:
            return "no_tool", "", ""

    def _mock_step(self, task: str, step: int) -> str:
        if step == 0:
            return f"I'll start by checking the current date.\nshell('date')"
        return f"FINAL_ANSWER: Task '{task}' completed (mock mode — no LLM API key configured)."
