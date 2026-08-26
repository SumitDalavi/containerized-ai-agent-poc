"""File tool — sandboxed read/write within a workspace directory."""
from __future__ import annotations
import os, pathlib

WORKSPACE = os.path.abspath(os.getenv("AGENT_WORKSPACE", "/tmp/agent-workspace"))
MAX_READ_BYTES = 50_000
MAX_WRITE_BYTES = 100_000


def _safe_path(relative_path: str) -> pathlib.Path:
    """Resolve and validate a path is within WORKSPACE (path traversal guard)."""
    resolved = (pathlib.Path(WORKSPACE) / relative_path).resolve()
    if not str(resolved).startswith(WORKSPACE):
        raise PermissionError(f"Access denied: path outside workspace: {resolved}")
    return resolved


def read_file(relative_path: str) -> str:
    p = _safe_path(relative_path)
    if not p.exists():
        return f"[error] File not found: {relative_path}"
    if p.stat().st_size > MAX_READ_BYTES:
        return f"[error] File too large to read (max {MAX_READ_BYTES} bytes)"
    return p.read_text(encoding="utf-8", errors="replace")


def write_file(relative_path: str, content: str) -> str:
    if len(content.encode()) > MAX_WRITE_BYTES:
        return f"[error] Content too large (max {MAX_WRITE_BYTES} bytes)"
    p = _safe_path(relative_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"[ok] Written {len(content)} chars to {relative_path}"


def list_files(relative_path: str = ".") -> list:
    p = _safe_path(relative_path)
    if not p.is_dir():
        return [f"[error] Not a directory: {relative_path}"]
    return [str(f.relative_to(WORKSPACE)) for f in p.iterdir()]


def describe() -> dict:
    return {
        "name": "file",
        "description": "Read/write files within the agent workspace",
        "workspace": WORKSPACE,
        "operations": ["read_file", "write_file", "list_files"],
        "limits": {"read_bytes": MAX_READ_BYTES, "write_bytes": MAX_WRITE_BYTES},
    }
