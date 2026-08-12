# Containerized AI Agent PoC 🚀

A Proof of Concept (PoC) demonstrating a microservice-based architecture for deploying AI Agents. Built with **FastAPI**, **Python**, and **Docker**.

## 📖 Overview

This project showcases a scalable approach to building and deploying AI agents. By wrapping the agent's logic in a high-performance REST API (FastAPI) and containerizing the entire application (Docker), we ensure the agent is easily deployable, testable, and capable of integrating into larger, cloud-native systems.

Currently, the agent uses a simulated asynchronous logic engine, making it perfect for demonstrating architectural patterns without requiring external API keys or heavy local models.

## ✨ Features

- **FastAPI Backend**: High-performance, asynchronous REST API.
- **Automatic Documentation**: Interactive Swagger UI generated out-of-the-box.
- **Robust Validation**: Pydantic models ensure all inputs and outputs are strictly typed.
- **Containerized**: Fully Dockerized for "works on my machine" consistency.
- **Clean Architecture**: Separation of concerns between API routing, data modeling, and core agent logic.

## 🛠️ Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Containerization**: Docker & Docker Compose

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose installed on your system.

### Running the Application

1. **Clone the repository** (or navigate to the project directory).
2. **Start the container** using Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
3. **Access the API**: 
   The service will be running on `http://localhost:8000`.

### Interacting with the Agent

The easiest way to interact with the API is through the automatically generated Swagger UI.

1. Open your browser and navigate to: `http://localhost:8000/docs`
2. Locate the `POST /agent/task` endpoint.
3. Click "Try it out" and send a JSON payload like this:
   ```json
   {
     "task_id": "test-task-123",
     "prompt": "Hello! Can you summarize this?"
   }
   ```
4. Check the `GET /agent/history/{task_id}` endpoint to retrieve previous interactions.

## 📁 Project Structure

For a detailed breakdown of the codebase and technical design decisions, please refer to the [Architecture Documentation](docs/ARCHITECTURE.md).

## 👨‍💻 Author

*Created as a Proof of Concept for resume showcasing.*
