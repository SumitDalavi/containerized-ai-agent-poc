# Containerized AI Agent PoC 🚀

> A microservice-based architecture for deploying AI Agents. Built with FastAPI, Python, and Docker to demonstrate scalable, production-ready AI deployment patterns.

## The Problem

AI experiments in Jupyter notebooks don't scale. To be useful in a production environment, an AI agent needs to be stateless, accessible via a standardized API, and easily deployable across different environments without dependency hell.

## The Solution

This PoC wraps an AI agent's logic in a high-performance **FastAPI** REST interface and containerizes the entire application using **Docker**. This ensures the agent is easily deployable, testable, and capable of integrating into larger, cloud-native systems.

Currently, the agent uses a simulated asynchronous logic engine, making it perfect for demonstrating architectural patterns without requiring external API keys or heavy local models.

## Why This Over the Obvious Alternative

Many developers just use Flask for AI APIs. By choosing **FastAPI**, we get asynchronous request handling out of the box (crucial for long-running LLM inferences), automatic OpenAPI/Swagger documentation, and strict type validation via Pydantic. By fully Dockerizing it, we solve the "works on my machine" problem that plagues Python AI development.

## 🛠️ Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Containerization**: Docker & Docker Compose

## Decision Log

| Decision | Rationale |
|----------|-----------|
| FastAPI over Flask/Django | Native async support is critical for I/O bound AI workloads; Pydantic ensures type-safe LLM inputs. |
| Docker Compose orchestration | Provides a single command to spin up the agent and any future dependencies (like a vector DB or Redis cache). |
| Layered Architecture | Separates API routing, data modeling, and core agent logic, allowing the AI model to be swapped without changing the API contract. |

## 🚀 Getting Started

```bash
docker-compose up -d --build
```
Access the interactive Swagger UI at `http://localhost:8000/docs` to interact with the agent.

## 📁 Project Structure

For a detailed breakdown of the codebase and technical design decisions, please refer to the [Architecture Documentation](docs/ARCHITECTURE.md).


## ðŸ“‹ Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| [Docker](https://www.docker.com/) | >= 24.x | Container runtime |
| [Docker Compose](https://docs.docker.com/compose/) | >= 2.x | Multi-container orchestration |
| [curl](https://curl.se/) or [Postman](https://www.postman.com/) | Any | API testing |

## ðŸš€ Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/SumitDalavi/containerized-ai-agent-poc.git
cd containerized-ai-agent-poc

# 2. Build and start the service
docker-compose up -d --build

# 3. Verify it's running
docker ps | grep fastapi-ai-agent
```

The API is now available at **http://localhost:8000**

## ðŸ§ª Usage & Demo

### Interactive API Docs
Open **http://localhost:8000/docs** in your browser for the Swagger UI.

### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Submit a task to the AI Agent
curl -X POST http://localhost:8000/agent/task \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze the security posture of my Kubernetes cluster", "context": "production"}'

# Retrieve task history
curl http://localhost:8000/agent/history/{task_id}
```

## âœ… Verification

```bash
# 1. Check container is healthy
curl -s http://localhost:8000/health | jq .
# Expected: {"status": "healthy", "agent_name": "..."}

# 2. Submit a test task and verify response
curl -s -X POST http://localhost:8000/agent/task \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}' | jq .

# 3. Stop the service
docker-compose down
```

## 👨‍💻 Author

*Created as a Proof of Concept to demonstrate production-ready AI deployment architectures.*
