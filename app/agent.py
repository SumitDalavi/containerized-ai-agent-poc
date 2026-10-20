import os
import asyncio
from typing import Dict
from .models import TaskRequest, TaskResponse

def is_live_openai_key(key: str = None) -> bool:
    if key is None:
        key = os.getenv("OPENAI_API_KEY", "")
    return bool(key) and key.startswith("sk-") and not key.startswith("sk-dummy") and len(key) >= 20

def detect_mode():
    return {
        "ai": "live" if is_live_openai_key() else "mock",
        "agent": "containerized-poc"
    }

class SimpleAIAgent:
    """
    Progressive Credential Loading (PCL) AI Agent:
    - Default (Mock Mode): Runs locally with rule-based heuristics and zero dependencies.
    - Live Mode: When OPENAI_API_KEY is supplied, automatically queries OpenAI chat completions.
    """
    
    def __init__(self, agent_name: str = "MockAgent-01"):
        self.agent_name = agent_name
        self.history: Dict[str, TaskResponse] = {}

    async def process_task(self, request: TaskRequest) -> TaskResponse:
        """
        Process a task asynchronously (live OpenAI if key provided, rule-based mock otherwise).
        """
        apiKey = os.getenv("OPENAI_API_KEY", "")
        if is_live_openai_key(apiKey):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=apiKey)
                loop = asyncio.get_event_loop()
                completion = await loop.run_in_executor(
                    None,
                    lambda: client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": request.prompt}],
                        max_tokens=500
                    )
                )
                result_text = completion.choices[0].message.content or ""
                response = TaskResponse(task_id=request.task_id, status="completed", result=result_text)
                self.history[request.task_id] = response
                return response
            except Exception:
                # Graceful fallback to mock logic on provider failure
                pass

        # Simulate thinking delay (non-blocking)
        await asyncio.sleep(0.05)
        
        # A very basic rule-based mock logic
        lower_prompt = request.prompt.lower()
        
        if "hello" in lower_prompt or "hi" in lower_prompt:
            result_text = f"Hello! I am {self.agent_name}, your containerized AI agent. How can I help you today?"
        elif "summarize" in lower_prompt:
            result_text = f"[{self.agent_name}] Here is a summary of your text: 'This is a mock summary of the provided content.'"
        elif "analyze" in lower_prompt:
            result_text = f"[{self.agent_name}] Analysis complete. The data indicates positive trends with a high degree of confidence."
        else:
            result_text = f"[{self.agent_name}] I have received your prompt: '{request.prompt}'. As a PoC agent, my capabilities are limited to mock responses, but I successfully processed the request!"
            
        response = TaskResponse(
            task_id=request.task_id,
            status="completed",
            result=result_text
        )
        
        # Store in history (in memory)
        self.history[request.task_id] = response
        
        return response

# Create a singleton instance to be used by the API
agent_instance = SimpleAIAgent(agent_name="FastAPI-PoC-Agent")
