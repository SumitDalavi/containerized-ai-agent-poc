"""Audit logger — records every tool call and agent decision to a structured log."""
from __future__ import annotations
import json, os, threading
from datetime import datetime, timezone
from typing import Any, Optional

LOG_PATH = os.getenv("AUDIT_LOG_PATH", "audit.jsonl")
_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_tool_call(
    agent_id: str,
    tool_name: str,
    input_data: Any,
    output: str,
    success: bool,
    duration_ms: float,
    sandboxed: bool = False,
    error: Optional[str] = None,
):
    """Append a tool execution event to the audit log."""
    record = {
        "ts": _now(), "type": "tool_call",
        "agent_id": agent_id, "tool": tool_name,
        "input": str(input_data)[:500],
        "output": output[:500] if output else "",
        "success": success, "duration_ms": duration_ms,
        "sandboxed": sandboxed, "error": error,
    }
    _append(record)


def log_agent_decision(agent_id: str, thought: str, action: str, action_input: Any):
    """Record an agent's reasoning step."""
    record = {
        "ts": _now(), "type": "agent_decision",
        "agent_id": agent_id, "thought": thought[:500],
        "action": action, "action_input": str(action_input)[:500],
    }
    _append(record)


def log_session_start(agent_id: str, task: str):
    _append({"ts": _now(), "type": "session_start", "agent_id": agent_id, "task": task[:500]})


def log_session_end(agent_id: str, status: str, total_steps: int):
    _append({"ts": _now(), "type": "session_end", "agent_id": agent_id,
             "status": status, "total_steps": total_steps})


def _append(record: dict):
    with _lock:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def get_session_logs(agent_id: str) -> list:
    """Read all log entries for a specific agent session."""
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip() and json.loads(l).get("agent_id") == agent_id]
