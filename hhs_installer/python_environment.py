from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence
import subprocess
import sys
import time

from .canonical import hash216, stable


@dataclass(frozen=True)
class PythonEnvironmentResult:
    path: str
    python: str
    status: str
    exit_status: int | None
    stdout: str
    stderr: str
    duration_ns: int
    environment_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


def create_environment(path: str | Path, *, timeout_seconds: int = 600) -> PythonEnvironmentResult:
    target = Path(path).expanduser().resolve()
    if not 1 <= timeout_seconds <= 3600:
        raise ValueError("P172_PYTHON_ENVIRONMENT_TIMEOUT_INVALID")
    started = time.monotonic_ns()
    try:
        completed = subprocess.run(
            [sys.executable, "-m", "venv", str(target)],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        status = "SUCCESS" if completed.returncode == 0 else "FAILURE"
        exit_status = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as exc:
        status = "BLOCKED"
        exit_status = None
        stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else str(exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else str(exc.stderr or "")
    python = target / ("Scripts/python.exe" if sys.platform.startswith("win") else "bin/python")
    payload = {"path": str(target), "python": str(python), "status": status, "exit_status": exit_status}
    return PythonEnvironmentResult(
        path=str(target),
        python=str(python),
        status=status,
        exit_status=exit_status,
        stdout=stdout,
        stderr=stderr,
        duration_ns=time.monotonic_ns() - started,
        environment_identity=hash216(payload, domain="HHS-P172-PYTHON-ENVIRONMENT-V1"),
    )
