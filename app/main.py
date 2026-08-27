import os
# from langchain.llms import OpenAI
# from langchain.agents import initialize_agent, AgentType

def run_agent():
    print("Initializing Containerized AI Agent...")
    
    # Mock behavior to show container runs
    prompt = os.getenv("AGENT_PROMPT", "What is the capital of France?")
    print(f"Agent received prompt: {prompt}")
    
    # In a real scenario, this would use the OpenAI API
    print("Agent mock response: Paris")

if __name__ == "__main__":
    run_agent()
