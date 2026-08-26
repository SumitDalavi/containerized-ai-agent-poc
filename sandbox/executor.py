"""
Sandboxed tool executor.
Runs tool calls inside a Docker container with strict resource limits,
network restrictions, and a read-only filesystem.
"""
from __future__ import annotations
import json, os, subprocess, tempfile, time, uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ExecutionResult:
    tool: str
    input: Any
    output: str
    exit_code: int
    duration_ms: float
    sandboxed: bool
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and self.error is None


# Allowlisted commands the sandbox may run
ALLOWED_COMMANDS = frozenset(["echo", "cat", "ls", "grep", "wc", "head", "tail", "date", "python3"])

# Docker sandbox image — minimal Python
SANDBOX_IMAGE = os.getenv("SANDBOX_IMAGE", "python:3.11-alpine")


def run_in_sandbox(command: str, timeout_s: int = 10) -> ExecutionResult:
    """
    Execute a shell command inside a Docker sandbox with:
    - CPU: 0.5 cores
    - Memory: 64 MB
    - No network
    - Read-only filesystem (with /tmp tmpfs)
    - Non-root user
    - Dropped capabilities
    """
    tool_name = command.split()[0] if command else "unknown"
    if tool_name not in ALLOWED_COMMANDS:
        return ExecutionResult(
            tool=tool_name, input=command, output="",
            exit_code=1, duration_ms=0, sandboxed=True,
            error=f"Command '{tool_name}' is not in the allowlist: {sorted(ALLOWED_COMMANDS)}",
        )

    docker_cmd = [
        "docker", "run", "--rm",
        "--network", "none",           # no network
        "--read-only",                 # read-only root FS
        "--tmpfs", "/tmp:size=10m",    # writable /tmp only
        "--memory", "64m",             # 64 MB RAM limit
        "--cpus", "0.5",               # 0.5 vCPU
        "--user", "65534",             # nobody user
        "--cap-drop", "ALL",           # drop all Linux capabilities
        "--security-opt", "no-new-privileges",
        SANDBOX_IMAGE,
        "sh", "-c", command,
    ]

    start = time.time()
    try:
        proc = subprocess.run(
            docker_cmd, capture_output=True, text=True, timeout=timeout_s
        )
        duration = (time.time() - start) * 1000
        return ExecutionResult(
            tool=tool_name, input=command,
            output=(proc.stdout + proc.stderr).strip(),
            exit_code=proc.returncode,
            duration_ms=round(duration, 2),
            sandboxed=True,
            error=proc.stderr.strip() if proc.returncode != 0 else None,
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            tool=tool_name, input=command, output="",
            exit_code=124, duration_ms=timeout_s * 1000,
            sandboxed=True, error=f"Execution timed out after {timeout_s}s",
        )
    except FileNotFoundError:
        # Docker not available — run locally with allowlist check only
        return _run_local_fallback(tool_name, command)


def _run_local_fallback(tool_name: str, command: str) -> ExecutionResult:
    """Fallback: run without Docker (dev environment without Docker daemon)."""
    start = time.time()
    try:
        proc = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=5
        )
        duration = (time.time() - start) * 1000
        return ExecutionResult(
            tool=tool_name, input=command,
            output=(proc.stdout + proc.stderr).strip(),
            exit_code=proc.returncode,
            duration_ms=round(duration, 2),
            sandboxed=False,
        )
    except Exception as e:
        return ExecutionResult(
            tool=tool_name, input=command, output="",
            exit_code=1, duration_ms=0, sandboxed=False, error=str(e),
        )
