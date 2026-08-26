"""Tests for sandboxed agent tools."""
import pytest, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sandbox.executor import ALLOWED_COMMANDS
from tools.file_tool import read_file, write_file, list_files, _safe_path, WORKSPACE
from monitoring.audit_log import log_tool_call, get_session_logs


def test_allowed_commands_not_empty():
    assert len(ALLOWED_COMMANDS) > 0
    assert "echo" in ALLOWED_COMMANDS


def test_safe_path_blocks_traversal():
    with pytest.raises(PermissionError):
        _safe_path("../../etc/passwd")


def test_write_and_read_file(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.file_tool.WORKSPACE", str(tmp_path))
    write_file("hello.txt", "hello world")
    content = read_file("hello.txt")
    assert content == "hello world"


def test_write_file_too_large(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.file_tool.WORKSPACE", str(tmp_path))
    monkeypatch.setattr("tools.file_tool.MAX_WRITE_BYTES", 10)
    result = write_file("big.txt", "x" * 100)
    assert "error" in result.lower()


def test_list_files(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.file_tool.WORKSPACE", str(tmp_path))
    write_file("a.txt", "a")
    write_file("b.txt", "b")
    files = list_files(".")
    assert any("a.txt" in f for f in files)


def test_audit_log_records_entry(tmp_path, monkeypatch):
    log_path = str(tmp_path / "audit.jsonl")
    monkeypatch.setattr("monitoring.audit_log.LOG_PATH", log_path)
    log_tool_call("agent-test", "shell", "echo hi", "hi", True, 5.0, sandboxed=True)
    logs = get_session_logs("agent-test")
    assert len(logs) == 1
    assert logs[0]["tool"] == "shell"
    assert logs[0]["sandboxed"] is True


def test_audit_log_multiple_agents(tmp_path, monkeypatch):
    log_path = str(tmp_path / "audit.jsonl")
    monkeypatch.setattr("monitoring.audit_log.LOG_PATH", log_path)
    log_tool_call("agent-a", "shell", "ls", "file1", True, 1.0)
    log_tool_call("agent-b", "shell", "date", "Mon", True, 1.0)
    logs_a = get_session_logs("agent-a")
    assert all(l["agent_id"] == "agent-a" for l in logs_a)
