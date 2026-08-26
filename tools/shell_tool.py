"""Shell tool — executes allowlisted shell commands in the sandbox."""
from __future__ import annotations
from sandbox.executor import run_in_sandbox, ExecutionResult


def execute_command(command: str, timeout_s: int = 10) -> ExecutionResult:
    """
    Run a shell command in the sandbox. Only allowlisted commands are permitted.
    Returns an ExecutionResult with output, exit code, and timing.
    """
    return run_in_sandbox(command, timeout_s=timeout_s)


def describe() -> dict:
    return {
        "name": "shell",
        "description": "Execute a sandboxed shell command",
        "parameters": {
            "command": "The shell command to run (must be in allowlist)",
            "timeout_s": "Maximum execution time in seconds (default: 10)",
        },
        "allowlist": ["echo", "cat", "ls", "grep", "wc", "head", "tail", "date", "python3"],
    }
