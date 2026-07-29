from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
import json
import os
import shutil
import subprocess
import sys
import time
import uuid

from .canonical import hash216, installation_identity, stable
from .dependencies import requirement_files_for_profile
from .journal import TaskCheckpoint, append_jsonl, atomic_write_json
from .planner import InstallationPlan, PlanStep
from .probe import ProbeReport
from .receipts import ReceiptChain
from .schema import InstallerSchemaError, SourceKind


class TransactionState(str, Enum):
    PLANNED = "PLANNED"
    SOURCE_ACQUIRED = "SOURCE_ACQUIRED"
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    STAGED = "STAGED"
    PYTHON_READY = "PYTHON_READY"
    DEPENDENCIES_READY = "DEPENDENCIES_READY"
    NATIVE_READY = "NATIVE_READY"
    RUNTIME_READY = "RUNTIME_READY"
    VALIDATED = "VALIDATED"
    ACTIVATED = "ACTIVATED"
    RECEIPT_CLOSED = "RECEIPT_CLOSED"
    FAILED = "FAILED"
    INTERRUPTED = "INTERRUPTED"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"


@dataclass(frozen=True)
class CommandResult:
    argv: tuple[str, ...]
    cwd: str
    exit_status: int | None
    classification: str
    stdout: str
    stderr: str
    duration_ns: int
    timed_out: bool

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


@dataclass(frozen=True)
class StepResult:
    step_id: str
    result: str
    classification: str
    output_identities: Mapping[str, str]
    command_results: tuple[CommandResult, ...]
    details: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return stable(asdict(self))


class InstallationLock:
    def __init__(self, path: Path, *, stale_after_seconds: int = 3600) -> None:
        self.path = path
        self.stale_after_seconds = stale_after_seconds
        self.acquired = False

    def __enter__(self) -> "InstallationLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            descriptor = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            try:
                age_seconds = max(0, int(time.time() - self.path.stat().st_mtime))
            except OSError:
                age_seconds = 0
            raise InstallerSchemaError(
                "HHS_INSTALLATION_TRANSACTION_ALREADY_ACTIVE",
                "another mutating transaction holds the installation lock",
                {
                    "lock": str(self.path),
                    "age_seconds": age_seconds,
                    "stale_threshold_seconds": self.stale_after_seconds,
                },
            ) from exc
        try:
            os.write(descriptor, json.dumps({"pid": os.getpid(), "created_unix_ns": time.time_ns()}).encode("utf-8"))
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        self.acquired = True
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self.acquired:
            self.path.unlink(missing_ok=True)
            self.acquired = False


class CommandRunner:
    def run(
        self,
        argv: Sequence[str],
        *,
        cwd: Path,
        timeout_seconds: int,
        environment: Mapping[str, str] | None = None,
    ) -> CommandResult:
        if not argv or any("\x00" in item for item in argv):
            raise InstallerSchemaError("P172_COMMAND_INVALID", "command argv is invalid")
        started = time.monotonic_ns()
        try:
            completed = subprocess.run(
                list(argv),
                cwd=str(cwd),
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env={**os.environ, **dict(environment or {})},
            )
            classification = "SUCCESS" if completed.returncode == 0 else "FAILURE"
            return CommandResult(
                argv=tuple(argv),
                cwd=str(cwd),
                exit_status=completed.returncode,
                classification=classification,
                stdout=completed.stdout,
                stderr=completed.stderr,
                duration_ns=time.monotonic_ns() - started,
                timed_out=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else str(exc.stdout or "")
            stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else str(exc.stderr or "")
            return CommandResult(
                argv=tuple(argv),
                cwd=str(cwd),
                exit_status=None,
                classification="BLOCKED",
                stdout=stdout,
                stderr=stderr,
                duration_ns=time.monotonic_ns() - started,
                timed_out=True,
            )
        except OSError as exc:
            return CommandResult(
                argv=tuple(argv),
                cwd=str(cwd),
                exit_status=None,
                classification="FAILURE",
                stdout="",
                stderr=f"{type(exc).__name__}:{exc}",
                duration_ns=time.monotonic_ns() - started,
                timed_out=False,
            )


class InstallationTransaction:
    """Bounded, restartable Pass 172 host-provisioning transaction.

    The transaction owns no HARMONICODE interpretation, VM81 execution, or
    canonical runtime mutation. It stages and verifies one inherited Runtime.
    """

    def __init__(self, plan: InstallationPlan, probe: ProbeReport, *, repository_root: str | Path) -> None:
        self.plan = plan
        self.probe = probe
        self.repository_root = Path(repository_root).expanduser().resolve()
        self.hhs_home = plan.request.resolved_home().resolve()
        self.transaction_id = hash216(
            {
                "plan_identity": plan.plan_identity,
                "probe_identity": probe.probe_identity,
                "nonce": uuid.uuid4().hex,
            },
            domain="HHS-P172-INSTALLATION-TRANSACTION-V1",
        )
        self.install_root = self.hhs_home / "install"
        self.journal_path = self.install_root / "journals" / f"{self.transaction_id}.jsonl"
        self.checkpoint_path = self.install_root / "journals" / f"{self.transaction_id}.checkpoint.json"
        self.stage_root = self.hhs_home / "versions" / f"staging-{self.transaction_id[:24]}"
        self.receipts = ReceiptChain(self.install_root / "receipts" / "installation-receipts.jsonl")
        self.runner = CommandRunner()
        self.state = TransactionState.PLANNED
        self.step_results: list[StepResult] = []
        self.handlers: dict[str, Callable[[PlanStep], StepResult]] = {
            "acquire_source": self._acquire_source,
            "verify_source": self._verify_source,
            "create_layout": self._create_layout,
            "create_python_environment": self._create_python_environment,
            "install_profile_dependencies": self._install_profile_dependencies,
            "build_native_runtime": self._build_native_runtime,
            "verify_native_runtime": self._verify_native_runtime,
            "generate_runtime_configuration": self._generate_runtime_configuration,
            "build_frontend": self._build_frontend,
            "verify_external_provider": self._verify_external_provider,
            "verify_offline_bundle": self._verify_offline_bundle,
            "run_dependency_scoped_validation": self._run_validation,
            "activate_staged_version": self._activate,
            "verify_active_installation": self._verify_active,
            "close_completion_receipt": self._close_receipt,
        }

    @staticmethod
    def _result(
        step: PlanStep,
        *,
        result: str = "SUCCESS",
        classification: str = "P172_STEP_COMPLETED",
        details: Mapping[str, Any] | None = None,
        commands: Sequence[CommandResult] = (),
        outputs: Mapping[str, str] | None = None,
    ) -> StepResult:
        return StepResult(
            step_id=step.step_id,
            result=result,
            classification=classification,
            output_identities=dict(outputs or {}),
            command_results=tuple(commands),
            details=dict(details or {}),
        )

    def _checkpoint(self, *, status: str, next_action: str, blocker: str | None = None) -> None:
        checkpoint = TaskCheckpoint(
            repository="danonbrez/Holofractal_Harmonicode",
            authoritative_base_commit="3fd4ca088039b1adc0d08a0644d62b979af8997d",
            active_branch="runtime-installation-transaction",
            intended_merge_target="installed-runtime",
            status=status,
            files_changed=tuple(sorted({scope for step in self.plan.steps for scope in step.mutation_scope})),
            commands_executed=tuple(
                command.to_dict()
                for result in self.step_results
                for command in result.command_results
            ),
            validation_results={result.step_id: result.result for result in self.step_results},
            remaining_checks=tuple(step.step_id for step in self.plan.steps[len(self.step_results):]),
            environment_state={
                "hhs_home": str(self.hhs_home),
                "transaction_id": self.transaction_id,
                "state": self.state.value,
                "open_processes": 0,
            },
            next_action=next_action,
            blocker=blocker,
            merge_status="not_applicable_host_installation",
        )
        checkpoint.write(self.checkpoint_path)

    def execute(self) -> dict[str, Any]:
        self.install_root.mkdir(parents=True, exist_ok=True)
        with InstallationLock(self.install_root / "locks" / "mutation.lock"):
            first_action = self.plan.steps[0].step_id if self.plan.steps else "close"
            self._checkpoint(status="ACTIVE", next_action=first_action)
            try:
                for index, step in enumerate(self.plan.steps):
                    append_jsonl(
                        self.journal_path,
                        {"event": "STEP_START", "step": step.to_dict(), "state": self.state.value, "unix_ns": time.time_ns()},
                    )
                    result = self.handlers.get(step.operation, self._unsupported_step)(step)
                    self.step_results.append(result)
                    append_jsonl(
                        self.journal_path,
                        {"event": "STEP_RESULT", "result": result.to_dict(), "state": self.state.value, "unix_ns": time.time_ns()},
                    )
                    if result.result not in {"SUCCESS", "NOOP"}:
                        self.state = TransactionState.RECOVERY_REQUIRED if result.result == "BLOCKED" else TransactionState.FAILED
                        next_action = (
                            f"resume transaction {self.transaction_id} at step {step.step_id} "
                            f"after correcting {result.classification}"
                        )
                        self._checkpoint(status=result.result, next_action=next_action, blocker=result.classification)
                        self.receipts.append(
                            receipt_class="P172_VALIDATION_RECEIPT",
                            operation=step.operation,
                            requested_profile=self.plan.requested_profile.value,
                            resolved_profile=self.plan.resolved_profile.value,
                            plan_identity=self.plan.plan_identity,
                            platform=self.probe.platform,
                            architecture=self.probe.architecture,
                            mutation_scope=step.mutation_scope,
                            result=result.result,
                            failure_classification=result.classification,
                            output_identities=result.output_identities,
                            execution_metadata={"transaction_id": self.transaction_id, "step_id": step.step_id},
                        )
                        return self.summary()
                    next_step = self.plan.steps[index + 1].step_id if index + 1 < len(self.plan.steps) else "verify completion receipt"
                    self._checkpoint(status="ACTIVE", next_action=next_step)
            except BaseException as exc:
                self.state = TransactionState.INTERRUPTED
                blocker = f"{type(exc).__name__}:{exc}"
                self._checkpoint(
                    status="BLOCKED",
                    next_action=f"resume transaction {self.transaction_id} from checkpoint",
                    blocker=blocker,
                )
                raise
        return self.summary()

    def summary(self) -> dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "state": self.state.value,
            "plan_identity": self.plan.plan_identity,
            "probe_identity": self.probe.probe_identity,
            "steps": [item.to_dict() for item in self.step_results],
            "checkpoint": str(self.checkpoint_path),
            "journal": str(self.journal_path),
            "receipt_tip": self.receipts.tip,
        }

    def _unsupported_step(self, step: PlanStep) -> StepResult:
        if step.optional:
            return self._result(
                step,
                result="NOOP",
                classification="P172_OPTIONAL_STEP_NOT_SELECTED",
                details={"operation": step.operation},
            )
        return self._result(
            step,
            result="BLOCKED",
            classification="P172_STEP_HANDLER_NOT_IMPLEMENTED",
            details={"operation": step.operation},
        )

    def _acquire_source(self, step: PlanStep) -> StepResult:
        source = self.plan.request.source
        if source.kind is not SourceKind.LOCAL:
            return self._result(
                step,
                result="BLOCKED",
                classification="P172_NETWORK_SOURCE_ADAPTER_REQUIRED",
                details={"source_kind": source.kind.value, "resumable": True},
            )
        source_path = Path(source.reference).expanduser().resolve()
        if not source_path.is_dir():
            return self._result(
                step,
                result="FAILURE",
                classification="P172_LOCAL_SOURCE_NOT_FOUND",
                details={"source": str(source_path)},
            )
        self.state = TransactionState.SOURCE_ACQUIRED
        return self._result(
            step,
            details={"source": str(source_path)},
            outputs={"source_path_identity": hash216(str(source_path), domain="HHS-P172-NONCANONICAL-SOURCE-PATH-V1")},
        )

    def _verify_source(self, step: PlanStep) -> StepResult:
        contract_paths = (
            self.repository_root / "HHS_PASS_172_UNIVERSAL_COMPATIBLE_ENVIRONMENT_ONE_COMMAND_INSTALLATION_DEPENDENCY_RESOLUTION_VERIFIED_BOOTSTRAP_AND_RUNTIME_ACTIVATION_SYSTEM.md",
            self.repository_root / "HHS_PASS_173_UNIVERSAL_INSTALLATION_FULL_COVERAGE_REDUNDANT_VERIFICATION_CALIBRATION_REPAIR_AND_REPLAY_CLOSURE_RUNTIME.md",
        )
        missing = [str(path) for path in contract_paths if not path.is_file()]
        if missing:
            return self._result(step, result="FAILURE", classification="P172_SOURCE_CONTRACTS_MISSING", details={"missing": missing})
        source_identity = hash216(
            {"pass172": contract_paths[0].read_bytes(), "pass173": contract_paths[1].read_bytes()},
            domain="HHS-P172-SOURCE-CONTRACT-PAIR-V1",
        )
        expected = self.plan.request.source.expected_identity
        if expected and expected != source_identity:
            return self._result(
                step,
                result="FAILURE",
                classification="P172_SOURCE_IDENTITY_MISMATCH",
                outputs={"observed": source_identity},
                details={"expected": expected},
            )
        self.state = TransactionState.SOURCE_VERIFIED
        return self._result(step, outputs={"source_identity": source_identity})

    def _create_layout(self, step: PlanStep) -> StepResult:
        directories = (
            "versions",
            "runtime/python",
            "runtime/native",
            "runtime/graphics",
            "runtime/provider",
            "runtime/models",
            "state/databases",
            "state/ledgers",
            "state/vector-store",
            "state/receipts",
            "state/workspaces",
            "install/probes",
            "install/plans",
            "install/journals",
            "install/locks",
            "install/receipts",
            "install/quarantine",
            "logs",
            "bin",
        )
        for relative in directories:
            (self.hhs_home / relative).mkdir(parents=True, exist_ok=True)
        self.stage_root.mkdir(parents=True, exist_ok=True)
        self.state = TransactionState.STAGED
        return self._result(step, details={"hhs_home": str(self.hhs_home), "stage_root": str(self.stage_root)})

    def _create_python_environment(self, step: PlanStep) -> StepResult:
        venv_path = self.stage_root / "python"
        command = self.runner.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            cwd=self.repository_root,
            timeout_seconds=step.timeout_seconds,
        )
        if command.classification != "SUCCESS":
            return self._result(
                step,
                result=command.classification,
                classification="P172_PYTHON_ENVIRONMENT_FAILED",
                commands=(command,),
            )
        self.state = TransactionState.PYTHON_READY
        return self._result(step, commands=(command,), details={"venv": str(venv_path)})

    def _venv_python(self) -> Path:
        windows = self.stage_root / "python" / "Scripts" / "python.exe"
        posix = self.stage_root / "python" / "bin" / "python"
        return windows if windows.exists() else posix

    def _install_profile_dependencies(self, step: PlanStep) -> StepResult:
        python = self._venv_python()
        if not python.exists():
            return self._result(step, result="FAILURE", classification="P172_PYTHON_ENVIRONMENT_MISSING")
        commands: list[CommandResult] = []
        for requirement_name in requirement_files_for_profile(self.plan.resolved_profile):
            requirement = self.repository_root / requirement_name
            if not requirement.exists():
                return self._result(
                    step,
                    result="BLOCKED",
                    classification="P172_PROFILE_REQUIREMENTS_MISSING",
                    commands=commands,
                    details={"missing": requirement_name},
                )
            command = self.runner.run(
                [str(python), "-m", "pip", "install", "--requirement", str(requirement)],
                cwd=self.repository_root,
                timeout_seconds=step.timeout_seconds,
            )
            commands.append(command)
            if command.classification != "SUCCESS":
                return self._result(
                    step,
                    result=command.classification,
                    classification="P172_DEPENDENCY_INSTALL_FAILED",
                    commands=commands,
                    details={"requirements": requirement_name},
                )
        self.state = TransactionState.DEPENDENCIES_READY
        return self._result(
            step,
            commands=commands,
            outputs={"dependency_execution_identity": hash216([item.to_dict() for item in commands], domain="HHS-P172-DEPENDENCY-INSTALL-V1")},
        )

    def _build_native_runtime(self, step: PlanStep) -> StepResult:
        make = shutil.which("make")
        if not make:
            return self._result(step, result="BLOCKED", classification="P172_BUILD_ORCHESTRATOR_UNAVAILABLE")
        command = self.runner.run([make, "verify-c"], cwd=self.repository_root, timeout_seconds=step.timeout_seconds)
        if command.classification != "SUCCESS":
            return self._result(
                step,
                result=command.classification,
                classification="P172_NATIVE_BUILD_FAILED",
                commands=(command,),
            )
        self.state = TransactionState.NATIVE_READY
        return self._result(
            step,
            commands=(command,),
            outputs={"native_build_log": hash216(command.to_dict(), domain="HHS-P172-NATIVE-BUILD-LOG-V1")},
        )

    def _verify_native_runtime(self, step: PlanStep) -> StepResult:
        if self.state is not TransactionState.NATIVE_READY:
            return self._result(step, result="FAILURE", classification="P172_NATIVE_STATE_NOT_READY")
        return self._result(step, details={"verification": "strict inherited make verify-c completed"})

    def _generate_runtime_configuration(self, step: PlanStep) -> StepResult:
        config = {
            "schema": "HHS_PASS_172_RUNTIME_CONFIG_V1",
            "profile": self.plan.resolved_profile.value,
            "api_port": self.probe.selected_ports.get("api"),
            "provider_port": self.probe.selected_ports.get("provider"),
            "provider_policy": self.plan.request.provider_policy.value,
            "vm81_authority": "singleton inherited runtime",
        }
        path = self.stage_root / "runtime-config.json"
        atomic_write_json(path, config)
        self.state = TransactionState.RUNTIME_READY
        return self._result(
            step,
            outputs={"runtime_config_identity": hash216(config, domain="HHS-P172-RUNTIME-CONFIG-V1")},
            details={"path": str(path)},
        )

    def _build_frontend(self, step: PlanStep) -> StepResult:
        npm = shutil.which("npm")
        app = self.repository_root / "applications" / "holofractal_harmonizer"
        if not npm or not app.is_dir():
            return self._result(step, result="BLOCKED", classification="P172_FRONTEND_BUILD_PREREQUISITE_MISSING")
        commands = (
            self.runner.run([npm, "ci"], cwd=app, timeout_seconds=step.timeout_seconds),
            self.runner.run([npm, "run", "build"], cwd=app, timeout_seconds=step.timeout_seconds),
        )
        failure = next((item for item in commands if item.classification != "SUCCESS"), None)
        if failure:
            return self._result(
                step,
                result=failure.classification,
                classification="P172_FRONTEND_BUILD_FAILED",
                commands=commands,
            )
        return self._result(
            step,
            commands=commands,
            outputs={"frontend_build_identity": hash216([item.to_dict() for item in commands], domain="HHS-P172-FRONTEND-BUILD-V1")},
        )

    def _verify_external_provider(self, step: PlanStep) -> StepResult:
        return self._result(
            step,
            result="BLOCKED",
            classification="P172_EXTERNAL_PROVIDER_CONFIGURATION_REQUIRED",
            details={"required": "protected endpoint URL, authorization classification, and model identity"},
        )

    def _verify_offline_bundle(self, step: PlanStep) -> StepResult:
        if self.plan.request.source.kind is not SourceKind.OFFLINE_BUNDLE:
            return self._result(step, result="NOOP", classification="P172_OFFLINE_BUNDLE_NOT_SELECTED")
        return self._result(
            step,
            result="BLOCKED",
            classification="P172_OFFLINE_BUNDLE_VERIFIER_REQUIRED",
            details={"network_fallback_permitted": False},
        )

    def _run_validation(self, step: PlanStep) -> StepResult:
        python = self._venv_python()
        if not python.exists():
            return self._result(step, result="FAILURE", classification="P172_VALIDATION_PYTHON_MISSING")
        candidates = (
            self.repository_root / "tests" / "pass172",
            self.repository_root / "tests" / "pass173",
        )
        selected = [str(path) for path in candidates if path.exists()]
        if not selected:
            return self._result(step, result="BLOCKED", classification="P172_DEPENDENCY_SCOPED_TESTS_MISSING")
        command = self.runner.run(
            [str(python), "-m", "pytest", "-q", *selected],
            cwd=self.repository_root,
            timeout_seconds=step.timeout_seconds,
        )
        if command.classification != "SUCCESS":
            return self._result(
                step,
                result=command.classification,
                classification="P172_DEPENDENCY_SCOPED_VALIDATION_FAILED",
                commands=(command,),
            )
        self.state = TransactionState.VALIDATED
        return self._result(
            step,
            commands=(command,),
            outputs={"validation_output_identity": hash216(command.to_dict(), domain="HHS-P172-VALIDATION-OUTPUT-V1")},
        )

    def _activate(self, step: PlanStep) -> StepResult:
        if self.state is not TransactionState.VALIDATED:
            return self._result(step, result="FAILURE", classification="P172_ACTIVATION_BEFORE_VALIDATION")
        version_id = hash216(
            {"plan": self.plan.plan_identity, "probe": self.probe.probe_identity},
            domain="HHS-P172-VERSION-ID-V1",
        )[:48]
        final_version = self.hhs_home / "versions" / version_id
        if final_version.exists():
            shutil.rmtree(self.stage_root, ignore_errors=True)
        else:
            os.replace(self.stage_root, final_version)
        pointer_path = self.hhs_home / "current.json"
        previous = None
        if pointer_path.exists():
            previous = json.loads(pointer_path.read_text(encoding="utf-8")).get("active_version")
        atomic_write_json(
            pointer_path,
            {
                "schema": "HHS_PASS_172_ACTIVE_VERSION_V1",
                "active_version": version_id,
                "previous_version": previous,
            },
        )
        self.state = TransactionState.ACTIVATED
        return self._result(
            step,
            outputs={"version_identity": version_id},
            details={"active": str(final_version), "previous": previous},
        )

    def _verify_active(self, step: PlanStep) -> StepResult:
        pointer_path = self.hhs_home / "current.json"
        if not pointer_path.exists():
            return self._result(step, result="FAILURE", classification="P172_ACTIVE_POINTER_MISSING")
        payload = json.loads(pointer_path.read_text(encoding="utf-8"))
        active = self.hhs_home / "versions" / str(payload.get("active_version", ""))
        if not active.is_dir():
            return self._result(
                step,
                result="FAILURE",
                classification="P172_ACTIVE_VERSION_MISSING",
                details={"active": str(active)},
            )
        return self._result(
            step,
            outputs={"active_pointer_identity": hash216(payload, domain="HHS-P172-ACTIVE-POINTER-V1")},
        )

    def _close_receipt(self, step: PlanStep) -> StepResult:
        def outputs_for(step_id: str) -> Mapping[str, str]:
            return next((result.output_identities for result in self.step_results if result.step_id == step_id), {})

        components = {
            "contract": "HHS-P172-UCEOCI-DRVBRAS",
            "source": outputs_for("source-verify").get("source_identity", "unknown"),
            "profile": self.plan.resolved_profile.value,
            "platform": self.probe.platform,
            "architecture": self.probe.architecture,
            "dependencies": outputs_for("dependencies-install"),
            "native": outputs_for("native-build"),
            "frontend": outputs_for("frontend-build"),
            "provider": self.plan.request.provider_policy.value,
            "model": self.plan.request.model_policy.value,
            "evidence": [result.output_identities for result in self.step_results],
        }
        identity = installation_identity(components)
        receipt = self.receipts.append(
            receipt_class="P172_COMPLETION_RECEIPT",
            operation="install",
            requested_profile=self.plan.requested_profile.value,
            resolved_profile=self.plan.resolved_profile.value,
            plan_identity=self.plan.plan_identity,
            platform=self.probe.platform,
            architecture=self.probe.architecture,
            mutation_scope=("current", "install/receipts"),
            result="SUCCESS",
            output_identities={"transaction": self.transaction_id},
            installation_identity=identity,
            execution_metadata={"step_count": len(self.step_results) + 1},
        )
        self.state = TransactionState.RECEIPT_CLOSED
        self._checkpoint(status="SUCCESS", next_action="installation complete")
        return self._result(
            step,
            outputs={"installation_identity": identity, "receipt_tip": receipt.receipt_tip},
        )
