from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
import hashlib
import os
import subprocess
import sys
import time

from hhs_installer.canonical import hash216, stable
from hhs_installer.journal import TaskCheckpoint
from .repair_planner import RepairPlan


@dataclass(frozen=True)
class RepairCommandResult:
    argv: tuple[str, ...]
    exit_status: int | None
    classification: str
    stdout: str
    stderr: str
    duration_ns: int
    timed_out: bool

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


@dataclass(frozen=True)
class RepairExecutionResult:
    plan_identity: str
    status: str
    commands: tuple[RepairCommandResult, ...]
    protected_contracts_unchanged: bool
    affected_scope_revalidated: bool
    execution_identity: str

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class RepairExecutor:
    def __init__(self, repository_root: str | Path, *, timeout_seconds: int = 900) -> None:
        self.root = Path(repository_root).resolve()
        if not 1 <= timeout_seconds <= 7200:
            raise ValueError("P173_REPAIR_TIMEOUT_INVALID")
        self.timeout_seconds = timeout_seconds
        self.contract_paths = (
            self.root / "HHS_PASS_172_UNIVERSAL_COMPATIBLE_ENVIRONMENT_ONE_COMMAND_INSTALLATION_DEPENDENCY_RESOLUTION_VERIFIED_BOOTSTRAP_AND_RUNTIME_ACTIVATION_SYSTEM.md",
            self.root / "HHS_PASS_173_UNIVERSAL_INSTALLATION_FULL_COVERAGE_REDUNDANT_VERIFICATION_CALIBRATION_REPAIR_AND_REPLAY_CLOSURE_RUNTIME.md",
        )

    @staticmethod
    def _digest(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    def _run(self, argv: tuple[str, ...]) -> RepairCommandResult:
        if not argv or any("\x00" in item for item in argv):
            raise ValueError("P173_REPAIR_COMMAND_INVALID")
        started = time.monotonic_ns()
        try:
            completed = subprocess.run(
                list(argv),
                cwd=str(self.root),
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                env=os.environ.copy(),
            )
            classification = "SUCCESS" if completed.returncode == 0 else "FAILURE"
            return RepairCommandResult(
                argv,
                completed.returncode,
                classification,
                completed.stdout,
                completed.stderr,
                time.monotonic_ns() - started,
                False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else str(exc.stdout or "")
            stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else str(exc.stderr or "")
            return RepairCommandResult(
                argv,
                None,
                "BLOCKED",
                stdout,
                stderr,
                time.monotonic_ns() - started,
                True,
            )

    def execute(
        self,
        plan: RepairPlan,
        *,
        repair_commands: Sequence[Sequence[str]],
        checkpoint_path: str | Path,
    ) -> RepairExecutionResult:
        before = {str(path): self._digest(path) for path in self.contract_paths if path.is_file()}
        results: list[RepairCommandResult] = []
        commands = [tuple(str(item) for item in command) for command in repair_commands]
        if not commands:
            raise ValueError("P173_REPAIR_COMMAND_REQUIRED")
        planned_tests = tuple(dict.fromkeys(plan.unit_tests + plan.integration_tests))
        if not planned_tests:
            raise ValueError("P173_REPAIR_HAS_NO_REVALIDATION_SCOPE")
        checkpoint = TaskCheckpoint(
            repository="danonbrez/Holofractal_Harmonicode",
            authoritative_base_commit="repository-visible caller base",
            active_branch="repository-visible caller branch",
            intended_merge_target="main",
            status="ACTIVE",
            files_changed=plan.implementation_paths,
            commands_executed=(),
            validation_results={},
            remaining_checks=planned_tests,
            environment_state={"open_processes": 0},
            next_action="execute bounded repair commands then dependency-scoped revalidation",
            blocker=None,
            merge_status="unmerged",
        )
        checkpoint.write(checkpoint_path)

        repair_succeeded = True
        for argv in commands:
            result = self._run(argv)
            results.append(result)
            if result.classification != "SUCCESS":
                repair_succeeded = False
                break

        after = {str(path): self._digest(path) for path in self.contract_paths if path.is_file()}
        contracts_unchanged = before == after
        validation_result: RepairCommandResult | None = None
        if repair_succeeded and contracts_unchanged:
            validation_argv = (sys.executable, "-m", "pytest", "-q", *planned_tests)
            validation_result = self._run(validation_argv)
            results.append(validation_result)

        revalidated = bool(
            repair_succeeded
            and contracts_unchanged
            and validation_result is not None
            and validation_result.classification == "SUCCESS"
        )
        if revalidated:
            status = "SUCCESS"
        elif any(item.classification == "BLOCKED" for item in results):
            status = "BLOCKED"
        else:
            status = "FAILURE"
        payload = {
            "plan_identity": plan.plan_identity,
            "status": status,
            "commands": [item.to_dict() for item in results],
            "planned_tests": list(planned_tests),
            "protected_contracts_unchanged": contracts_unchanged,
            "affected_scope_revalidated": revalidated,
        }
        result = RepairExecutionResult(
            plan_identity=plan.plan_identity,
            status=status,
            commands=tuple(results),
            protected_contracts_unchanged=contracts_unchanged,
            affected_scope_revalidated=revalidated,
            execution_identity=hash216(payload, domain="HHS-P173-REPAIR-EXECUTION-V1"),
        )
        TaskCheckpoint(
            repository="danonbrez/Holofractal_Harmonicode",
            authoritative_base_commit="repository-visible caller base",
            active_branch="repository-visible caller branch",
            intended_merge_target="main",
            status=status,
            files_changed=plan.implementation_paths,
            commands_executed=tuple(item.to_dict() for item in results),
            validation_results={
                "contracts_unchanged": contracts_unchanged,
                "affected_scope_revalidated": revalidated,
                "planned_tests": list(planned_tests),
                "validation_exit_status": None if validation_result is None else validation_result.exit_status,
            },
            remaining_checks=() if revalidated else planned_tests,
            environment_state={"open_processes": 0},
            next_action="commit and open ready PR" if revalidated else "correct blocker and rerun identical repair scope",
            blocker=None if revalidated else next(
                (item.classification for item in results if item.classification != "SUCCESS"),
                "P173_CONTRACT_MODIFICATION_DETECTED" if not contracts_unchanged else "P173_REVALIDATION_NOT_EXECUTED",
            ),
            merge_status="unmerged",
        ).write(checkpoint_path)
        return result
