from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import shutil
import subprocess
import time

from .canonical import hash216, stable


@dataclass(frozen=True)
class FrontendBuildResult:
    application: str
    status: str
    commands: tuple[tuple[str, ...], ...]
    outputs: tuple[dict[str, Any], ...]
    build_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


def build_frontend(application: str | Path, *, timeout_seconds: int = 1200) -> FrontendBuildResult:
    root = Path(application).resolve()
    npm = shutil.which("npm")
    if not npm:
        raise ValueError("P172_NODE_PACKAGE_MANAGER_MISSING")
    if not (root / "package.json").is_file() or not (root / "package-lock.json").is_file():
        raise ValueError("P172_NODE_LOCKFILE_REQUIRED")
    commands = ((npm, "ci"), (npm, "run", "build"))
    outputs: list[dict[str, Any]] = []
    status = "SUCCESS"
    for argv in commands:
        started = time.monotonic_ns()
        try:
            completed = subprocess.run(
                list(argv),
                cwd=str(root),
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            classification = "SUCCESS" if completed.returncode == 0 else "FAILURE"
            outputs.append(
                {
                    "argv": list(argv),
                    "classification": classification,
                    "exit_status": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                    "duration_ns": time.monotonic_ns() - started,
                }
            )
        except subprocess.TimeoutExpired as exc:
            classification = "BLOCKED"
            outputs.append(
                {
                    "argv": list(argv),
                    "classification": classification,
                    "exit_status": None,
                    "stdout": str(exc.stdout or ""),
                    "stderr": str(exc.stderr or ""),
                    "duration_ns": time.monotonic_ns() - started,
                }
            )
        if classification != "SUCCESS":
            status = classification
            break
    payload = {"application": str(root), "commands": commands, "outputs": outputs, "status": status}
    return FrontendBuildResult(
        application=str(root),
        status=status,
        commands=commands,
        outputs=tuple(outputs),
        build_identity=hash216(payload, domain="HHS-P172-FRONTEND-BUILD-V1"),
    )
