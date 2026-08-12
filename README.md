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

## 👨‍💻 Author

*Created as a Proof of Concept to demonstrate production-ready AI deployment architectures.*
