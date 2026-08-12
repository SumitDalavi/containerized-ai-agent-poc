from fastapi import FastAPI, HTTPException
from .models import TaskRequest, TaskResponse
from .agent import agent_instance

app = FastAPI(
    title="Containerized AI Agent PoC",
    description="A Proof of Concept for a containerized AI Agent using FastAPI. Perfect for demonstrating backend and containerization skills.",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Containerized AI Agent API. Visit /docs for the interactive API documentation."}

@app.get("/health")
async def health_check():
    """
    Health check endpoint for Docker and orchestration tools.
    """
    return {"status": "healthy", "agent_name": agent_instance.agent_name}

@app.post("/agent/task", response_model=TaskResponse)
async def submit_task(request: TaskRequest):
    """
    Submit a task (prompt) to the AI Agent.
    """
    try:
        response = await agent_instance.process_task(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/history/{task_id}", response_model=TaskResponse)
async def get_task_history(task_id: str):
    """
    Retrieve the result of a previously processed task.
    """
    if task_id not in agent_instance.history:
        raise HTTPException(status_code=404, detail="Task ID not found in history.")
    return agent_instance.history[task_id]
