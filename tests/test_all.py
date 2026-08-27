import pytest
import asyncio
from unittest.mock import patch, MagicMock
import os
import pathlib

from app.models import TaskRequest, TaskResponse
from app.agent import SimpleAIAgent, agent_instance
from app.main import run_agent

import tools.shell_tool as shell_tool
import tools.file_tool as file_tool

@pytest.mark.asyncio
async def test_agent_process_task():
    agent = SimpleAIAgent(agent_name="TestAgent")
    
    # "hello"
    req1 = TaskRequest(task_id="t1", prompt="hello world")
    resp1 = await agent.process_task(req1)
    assert resp1.task_id == "t1"
    assert "Hello! I am TestAgent" in resp1.result
    
    # "summarize"
    req2 = TaskRequest(task_id="t2", prompt="Please summarize the report")
    resp2 = await agent.process_task(req2)
    assert "summary" in resp2.result
    
    # "analyze"
    req3 = TaskRequest(task_id="t3", prompt="Please analyze the data")
    resp3 = await agent.process_task(req3)
    assert "Analysis complete" in resp3.result
    
    # Other
    req4 = TaskRequest(task_id="t4", prompt="Perform another task")
    resp4 = await agent.process_task(req4)
    assert "PoC agent" in resp4.result
    
    # Check history
    assert len(agent.history) == 4
    assert agent.history["t1"].result == resp1.result

def test_run_agent(capsys):
    os.environ["AGENT_PROMPT"] = "test prompt"
    run_agent()
    captured = capsys.readouterr()
    assert "Initializing Containerized AI Agent..." in captured.out
    assert "test prompt" in captured.out
    assert "Paris" in captured.out

def test_models():
    req = TaskRequest(task_id="1", prompt="p")
    assert req.task_id == "1"
    assert req.prompt == "p"
    
    resp = TaskResponse(task_id="1", status="s", result="r")
    assert resp.task_id == "1"
    assert resp.status == "s"
    assert resp.result == "r"

def test_shell_tool():
    with patch("tools.shell_tool.run_in_sandbox") as mock_run:
        mock_result = MagicMock()
        mock_run.return_value = mock_result
        res = shell_tool.execute_command("echo hello")
        assert res == mock_result
    
    desc = shell_tool.describe()
    assert desc["name"] == "shell"
    assert "allowlist" in desc

def test_file_tool(tmp_path):
    os.environ["AGENT_WORKSPACE"] = str(tmp_path)
    # Important: reload or monkeypatch file_tool.WORKSPACE
    file_tool.WORKSPACE = str(tmp_path)
    
    # Write file success
    res = file_tool.write_file("test.txt", "hello")
    assert "Written" in res
    
    # Write file too large
    res = file_tool.write_file("big.txt", "a" * (file_tool.MAX_WRITE_BYTES + 1))
    assert "[error]" in res
    
    # Read file success
    res = file_tool.read_file("test.txt")
    assert res == "hello"
    
    # Read file not found
    res = file_tool.read_file("missing.txt")
    assert "[error]" in res
    
    # List files success
    res = file_tool.list_files(".")
    assert "test.txt" in res
    
    # List files not a dir
    res = file_tool.list_files("test.txt")
    assert "[error]" in res[0]
    
    # Describe
    desc = file_tool.describe()
    assert desc["name"] == "file"

def test_file_tool_path_traversal(tmp_path):
    file_tool.WORKSPACE = str(tmp_path)
    
    with pytest.raises(PermissionError):
        file_tool._safe_path("../outside.txt")
    
def test_file_tool_large_read(tmp_path):
    file_tool.WORKSPACE = str(tmp_path)
    p = tmp_path / "large.txt"
    with open(p, "wb") as f:
        # Seek past max bytes and write 1 byte to make file large efficiently
        f.seek(file_tool.MAX_READ_BYTES + 10)
        f.write(b"0")
    
    res = file_tool.read_file("large.txt")
    assert "[error]" in res
