from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
import json
import os
import shutil
import subprocess
import tempfile
import time

from hhs_installer.canonical import hash216, stable


@dataclass(frozen=True)
class CleanInstallRequest:
    case_id: str
    command: tuple[str, ...]
    repository_root: str
    profile: str
    platform: str
    architecture: str
    timeout_seconds: int = 1800
    environment: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        if not self.case_id or not self.command:
            raise ValueError("P173_CLEAN_INSTALL_REQUEST_INVALID")
        if not 1 <= self.timeout_seconds <= 14_400:
            raise ValueError("P173_CLEAN_INSTALL_TIMEOUT_INVALID")

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


@dataclass(frozen=True)
class CleanInstallResult:
    case_id: str
    status: str
    classification: str
    exit_status: int | None
    timed_out: bool
    duration_ns: int
    stdout: str
    stderr: str
    workspace_identity: str
    output_identity: str
    recovery_receipt: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class CleanInstallRunner:
    def run(self, request: CleanInstallRequest) -> CleanInstallResult:
        repository_root = Path(request.repository_root).resolve()
        if not repository_root.is_dir():
            raise ValueError("P173_CLEAN_INSTALL_REPOSITORY_MISSING")
        workspace = Path(tempfile.mkdtemp(prefix=f"hhs-pass173-{request.case_id}-"))
        hhs_home = workspace / "hhs-home"
        logs = workspace / "logs"
        logs.mkdir(parents=True)
        environment = {
            **os.environ,
            "HHS_HOME": str(hhs_home),
            "PYTHONPATH": str(repository_root),
            **dict(request.environment or {}),
        }
        started = time.monotonic_ns()
        exit_status: int | None = None
        timed_out = False
        stdout = ""
        stderr = ""
        try:
            completed = subprocess.run(
                list(request.command),
                cwd=str(repository_root),
                check=False,
                capture_output=True,
                text=True,
                timeout=request.timeout_seconds,
                env=environment,
            )
            exit_status = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
            status = "SUCCESS" if completed.returncode == 0 else "FAILURE"
            classification = "P173_CLEAN_INSTALL_COMPLETED" if completed.returncode == 0 else "P173_CLEAN_INSTALL_COMMAND_FAILED"
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else str(exc.stdout or "")
            stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else str(exc.stderr or "")
            status = "BLOCKED"
            classification = "P173_CLEAN_INSTALL_TIMEOUT"
        except OSError as exc:
            status = "FAILURE"
            classification = "P173_CLEAN_INSTALL_EXECUTION_FAILED"
            stderr = f"{type(exc).__name__}:{exc}"
        duration = time.monotonic_ns() - started
        (logs / "stdout.log").write_text(stdout, encoding="utf-8")
        (logs / "stderr.log").write_text(stderr, encoding="utf-8")
        records: list[dict[str, Any]] = []
        for path in sorted(workspace.rglob("*")):
            if path.is_file():
                records.append({"path": str(path.relative_to(workspace)).replace("\\", "/"), "size": path.stat().st_size})
        workspace_identity = hash216(records, domain="HHS-P173-CLEAN-INSTALL-WORKSPACE-V1")
        output_identity = hash216({"stdout": stdout, "stderr": stderr, "exit": exit_status}, domain="HHS-P173-CLEAN-INSTALL-OUTPUT-V1")
        recovery = {
            "status": status,
            "repository": "danonbrez/Holofractal_Harmonicode",
            "base_commit": "repository-visible caller ref",
            "branch": "repository-visible caller branch",
            "latest_commit": "repository-visible caller head",
            "worktree_clean": True,
            "completed_scope": ["bounded clean-install command execution"],
            "remaining_scope": [] if status == "SUCCESS" else ["correct blocker and rerun identical case"],
            "last_command": list(request.command),
            "last_exit_status": exit_status,
            "blocker": None if status == "SUCCESS" else classification,
            "next_command": list(request.command),
            "merge_status": "not_applicable_test_workspace",
            "workspace": str(workspace),
        }
        return CleanInstallResult(
            case_id=request.case_id,
            status=status,
            classification=classification,
            exit_status=exit_status,
            timed_out=timed_out,
            duration_ns=duration,
            stdout=stdout,
            stderr=stderr,
            workspace_identity=workspace_identity,
            output_identity=output_identity,
            recovery_receipt=recovery,
        )

    @staticmethod
    def cleanup(result: CleanInstallResult) -> None:
        workspace = result.recovery_receipt.get("workspace")
        if workspace:
            shutil.rmtree(str(workspace), ignore_errors=True)
