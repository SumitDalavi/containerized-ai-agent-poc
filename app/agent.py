import asyncio
from typing import Dict
from .models import TaskRequest, TaskResponse

class SimpleAIAgent:
    """
    A simulated AI Agent that processes tasks.
    In a real-world scenario, this would connect to an LLM provider (OpenAI, Gemini, etc.)
    or run a local model.
    """
    
    def __init__(self, agent_name: str = "MockAgent-01"):
        self.agent_name = agent_name
        self.history: Dict[str, TaskResponse] = {}

    async def process_task(self, request: TaskRequest) -> TaskResponse:
        """
        Simulate processing a task asynchronously.
        """
        # Simulate thinking delay
        await asyncio.sleep(1.5)
        
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
