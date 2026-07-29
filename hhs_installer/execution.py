from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import json
import os
import platform
import shutil
import subprocess
import sys
import time

from .acquisition import AcquisitionError, SourceAcquirer
from .canonical import hash216
from .dependencies import requirement_files_for_profile
from .journal import atomic_write_json
from .model_assets import ModelAssetManager, ModelAssetRequest, ModelAssetError
from .native_builder import NativeBuildError, NativeBuilder, NativeTarget
from .offline import OfflineBundleError, OfflineBundleVerification, OfflineBundleVerifier
from .planner import PlanStep
from .provider import ProviderResolver, ProviderState
from .schema import NetworkPolicy, SourceKind
from .security import ArchivePolicy, SecurityError, extract_archive
from .transaction import InstallationTransaction, StepResult, TransactionState
from .verification import VerificationError


class CompleteInstallationTransaction(InstallationTransaction):
    """Complete Pass 172 adapters bound to the one inherited transaction authority."""

    CONTRACT_NAMES = (
        "HHS_PASS_172_UNIVERSAL_COMPATIBLE_ENVIRONMENT_ONE_COMMAND_INSTALLATION_DEPENDENCY_RESOLUTION_VERIFIED_BOOTSTRAP_AND_RUNTIME_ACTIVATION_SYSTEM.md",
        "HHS_PASS_173_UNIVERSAL_INSTALLATION_FULL_COVERAGE_REDUNDANT_VERIFICATION_CALIBRATION_REPAIR_AND_REPLAY_CLOSURE_RUNTIME.md",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.acquired_source: dict[str, Any] | None = None
        self.source_root = self.repository_root
        self.offline_verification: OfflineBundleVerification | None = None
        self.offline_bundle_root: Path | None = None
        self.native_builds: list[dict[str, Any]] = []
        self.provider_probe: dict[str, Any] | None = None
        self.provider_executable: Path | None = None
        self.provider_endpoint: str | None = None
        self.provider_process: subprocess.Popen[bytes] | None = None
        self._provider_log_handle: Any | None = None
        self.handlers.update(
            {
                "acquire_source": self._acquire_source_complete,
                "verify_source": self._verify_source_complete,
                "verify_offline_bundle": self._verify_offline_bundle_complete,
                "create_layout": self._create_layout_complete,
                "install_profile_dependencies": self._install_profile_dependencies_complete,
                "build_native_runtime": self._build_native_runtime_complete,
                "verify_native_runtime": self._verify_native_runtime_complete,
                "verify_external_provider": self._verify_external_provider_complete,
                "verify_or_install_gpu_loader": self._verify_gpu_substrate,
                "install_local_provider": self._install_local_provider,
                "acquire_verify_import_model": self._govern_model,
                "verify_local_provider": self._verify_local_provider,
                "build_android_projection": self._build_android_projection,
                "activate_staged_version": self._activate_complete,
                "verify_active_installation": self._verify_active_complete,
            }
        )

    @staticmethod
    def _normal(value: str) -> str:
        lowered = value.strip().lower().replace("-", "_")
        aliases = {
            "amd64": "x86_64",
            "x64": "x86_64",
            "aarch64": "arm64",
            "macos": "darwin",
            "win32": "windows",
        }
        return aliases.get(lowered, lowered)

    @classmethod
    def _supported(cls, value: str, declared: tuple[str, ...]) -> bool:
        normalized = {cls._normal(item) for item in declared}
        return bool(normalized & {"*", "any", "all"}) or cls._normal(value) in normalized

    def _contracts_present(self, root: Path) -> bool:
        return all((root / name).is_file() for name in self.CONTRACT_NAMES)

    def _resolve_offline_source_root(self) -> Path | None:
        root = self.offline_bundle_root
        if root is None:
            return None
        descriptor_path = root / "offline-bundle.json"
        descriptor: dict[str, Any] = {}
        if descriptor_path.is_file():
            try:
                descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                descriptor = {}
        candidates: list[Path] = []
        declared = descriptor.get("source_root")
        if declared:
            candidate = (root / str(declared)).resolve()
            if candidate == root or root in candidate.parents:
                candidates.append(candidate)
        candidates.extend(root / name for name in ("source", "repository", "repo"))
        candidates.append(root)
        for candidate in candidates:
            if candidate.is_dir() and self._contracts_present(candidate):
                return candidate
        return None

    def _acquire_source_complete(self, step: PlanStep) -> StepResult:
        cache = self.hhs_home / "install" / "cache" / "sources"
        try:
            result = SourceAcquirer(cache).acquire(
                self.plan.request.source,
                network_policy=self.plan.request.network_policy,
            )
        except (AcquisitionError, VerificationError) as exc:
            code = getattr(exc, "code", "P172_SOURCE_ACQUISITION_FAILED")
            details = exc.to_dict() if hasattr(exc, "to_dict") else {"error": str(exc)}
            return self._result(
                step,
                result="BLOCKED" if code in {
                    "P172_DOWNLOAD_RETRIES_EXHAUSTED",
                    "P172_GIT_ACQUISITION_ADAPTER_REQUIRED",
                    "P172_CACHED_SOURCE_UNAVAILABLE",
                } else "FAILURE",
                classification=code,
                details=details,
            )
        self.acquired_source = result.to_dict()
        local_path = Path(result.local_path)
        outputs = {"acquisition_identity": result.acquisition_identity}
        if self.plan.request.source.kind is SourceKind.OFFLINE_BUNDLE:
            offline_source = self._resolve_offline_source_root()
            if offline_source is None:
                return self._result(
                    step,
                    result="FAILURE",
                    classification="P172_OFFLINE_SOURCE_PAYLOAD_MISSING",
                    details={"bundle": str(local_path), "required_contracts": list(self.CONTRACT_NAMES)},
                )
            self.source_root = offline_source
            outputs["offline_source_identity"] = hash216(
                {"root": str(offline_source.relative_to(self.offline_bundle_root))},
                domain="HHS-P172-OFFLINE-SOURCE-ROOT-V1",
            )
        elif local_path.is_file() and self.plan.request.source.kind is SourceKind.RELEASE:
            source_stage = self.hhs_home / "install" / "staging" / self.transaction_id / "source"
            try:
                inspection = extract_archive(local_path, source_stage, policy=ArchivePolicy())
            except SecurityError as exc:
                return self._result(step, result="FAILURE", classification=exc.code, details=exc.to_dict())
            children = [path for path in source_stage.iterdir()]
            self.source_root = children[0] if len(children) == 1 and children[0].is_dir() else source_stage
            outputs["archive_inspection_identity"] = inspection.inspection_identity
        else:
            self.source_root = local_path
        self.repository_root = self.source_root
        self.state = TransactionState.SOURCE_ACQUIRED
        return self._result(step, details=self.acquired_source, outputs=outputs)

    def _verify_source_complete(self, step: PlanStep) -> StepResult:
        if self.acquired_source is None:
            return self._result(step, result="FAILURE", classification="P172_SOURCE_NOT_ACQUIRED")
        contracts = tuple(self.source_root / name for name in self.CONTRACT_NAMES)
        missing = [str(path) for path in contracts if not path.is_file()]
        if missing:
            return self._result(step, result="FAILURE", classification="P172_SOURCE_CONTRACTS_MISSING", details={"missing": missing})
        source_identity = hash216(
            {"pass172": contracts[0].read_bytes(), "pass173": contracts[1].read_bytes(), "acquisition": self.acquired_source["acquisition_identity"]},
            domain="HHS-P172-VERIFIED-SOURCE-V1",
        )
        self.state = TransactionState.SOURCE_VERIFIED
        return self._result(step, outputs={"source_identity": source_identity})

    def _verify_offline_bundle_complete(self, step: PlanStep) -> StepResult:
        if self.plan.request.source.kind is not SourceKind.OFFLINE_BUNDLE:
            return self._result(step, result="NOOP", classification="P172_OFFLINE_BUNDLE_NOT_SELECTED")
        expected = self.plan.request.source.expected_identity
        if not expected:
            return self._result(step, result="FAILURE", classification="P172_OFFLINE_BUNDLE_EXPECTED_IDENTITY_REQUIRED")
        try:
            result = OfflineBundleVerifier().verify(self.plan.request.source.reference, expected_sha256=expected)
        except (OfflineBundleError, SecurityError, VerificationError) as exc:
            code = getattr(exc, "code", "P172_OFFLINE_BUNDLE_VERIFICATION_FAILED")
            details = exc.to_dict() if hasattr(exc, "to_dict") else {"error": str(exc)}
            return self._result(step, result="FAILURE", classification=code, details=details)
        mismatches: dict[str, Any] = {}
        if not self._supported(self.plan.resolved_profile.value, result.supported_profiles):
            mismatches["profile"] = {"target": self.plan.resolved_profile.value, "supported": result.supported_profiles}
        if not self._supported(self.probe.platform, result.supported_platforms):
            mismatches["platform"] = {"target": self.probe.platform, "supported": result.supported_platforms}
        if not self._supported(self.probe.architecture, result.supported_architectures):
            mismatches["architecture"] = {"target": self.probe.architecture, "supported": result.supported_architectures}
        if mismatches:
            return self._result(
                step,
                result="FAILURE",
                classification="P172_OFFLINE_BUNDLE_TARGET_INCOMPATIBLE",
                details={"mismatches": mismatches, "verification": result.to_dict()},
            )
        persistent_root = self.hhs_home / "install" / "staging" / self.transaction_id / "offline-bundle"
        try:
            extract_archive(self.plan.request.source.reference, persistent_root, policy=ArchivePolicy())
        except SecurityError as exc:
            return self._result(step, result="FAILURE", classification=exc.code, details=exc.to_dict())
        self.offline_verification = result
        self.offline_bundle_root = persistent_root
        return self._result(
            step,
            outputs={"offline_verification_identity": result.verification_identity},
            details=result.to_dict(),
        )

    def _copy_source_to_stage(self) -> Path:
        destination = self.stage_root / "runtime-source"
        if destination.exists():
            shutil.rmtree(destination)
        excluded_roots = {self.hhs_home.resolve(), self.stage_root.resolve()}

        def ignore(directory: str, names: list[str]) -> set[str]:
            ignored = {name for name in names if name in {".git", ".venv", "venv", "__pycache__"}}
            base = Path(directory)
            for name in names:
                candidate = (base / name).resolve()
                if candidate in excluded_roots:
                    ignored.add(name)
            return ignored

        shutil.copytree(self.source_root, destination, symlinks=False, ignore=ignore)
        return destination

    @staticmethod
    def _stage_launcher(stage_root: Path) -> Path:
        bin_root = stage_root / "bin"
        bin_root.mkdir(parents=True, exist_ok=True)
        if platform.system() == "Windows":
            launcher = bin_root / "hhs.cmd"
            launcher.write_text(
                "@echo off\r\n\"%~dp0..\\python\\Scripts\\python.exe\" \"%~dp0..\\runtime-source\\hhs-bootstrap.py\" %*\r\n",
                encoding="utf-8",
            )
        else:
            launcher = bin_root / "hhs"
            launcher.write_text(
                "#!/bin/sh\nset -eu\nROOT=$(CDPATH= cd -- \"$(dirname -- \"$0\")/..\" && pwd)\nexec \"$ROOT/python/bin/python\" \"$ROOT/runtime-source/hhs-bootstrap.py\" \"$@\"\n",
                encoding="utf-8",
            )
            launcher.chmod(0o755)
        return launcher

    def _create_layout_complete(self, step: PlanStep) -> StepResult:
        base = super()._create_layout(step)
        if base.result != "SUCCESS":
            return base
        try:
            staged_source = self._copy_source_to_stage()
            launcher = self._stage_launcher(self.stage_root)
        except OSError as exc:
            return self._result(
                step,
                result="FAILURE",
                classification="P172_RUNTIME_SOURCE_STAGING_FAILED",
                details={"error": f"{type(exc).__name__}:{exc}"},
            )
        if not (staged_source / "hhs-bootstrap.py").is_file():
            return self._result(
                step,
                result="FAILURE",
                classification="P172_STAGED_BOOTSTRAP_MISSING",
                details={"staged_source": str(staged_source)},
            )
        return self._result(
            step,
            outputs={
                "staged_source_identity": hash216(
                    {"contracts": [str((staged_source / name).is_file()) for name in self.CONTRACT_NAMES]},
                    domain="HHS-P172-STAGED-SOURCE-V1",
                ),
                "staged_launcher_identity": hash216(launcher.read_bytes(), domain="HHS-P172-STAGED-LAUNCHER-V1"),
            },
            details={"hhs_home": str(self.hhs_home), "stage_root": str(self.stage_root), "staged_source": str(staged_source), "launcher": str(launcher)},
        )

    def _offline_wheelhouse(self) -> Path | None:
        if self.offline_bundle_root is None:
            return None
        for name in ("wheels", "wheelhouse"):
            candidate = self.offline_bundle_root / name
            if candidate.is_dir():
                return candidate
        wheels = sorted(self.offline_bundle_root.rglob("*.whl"))
        return wheels[0].parent if wheels else None

    @staticmethod
    def _requirements_are_offline_safe(path: Path) -> bool:
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "://" in line or line.startswith(("git+", "hg+", "svn+", "bzr+")):
                return False
        return True

    def _install_profile_dependencies_complete(self, step: PlanStep) -> StepResult:
        python = self._venv_python()
        if not python.exists():
            return self._result(step, result="FAILURE", classification="P172_PYTHON_ENVIRONMENT_MISSING")
        wheelhouse = self._offline_wheelhouse() if self.plan.request.network_policy is NetworkPolicy.OFFLINE else None
        if self.plan.request.network_policy is NetworkPolicy.OFFLINE and wheelhouse is None:
            return self._result(step, result="FAILURE", classification="P172_OFFLINE_WHEELHOUSE_MISSING")
        commands = []
        for requirement_name in requirement_files_for_profile(self.plan.resolved_profile):
            requirement = self.source_root / requirement_name
            if not requirement.is_file():
                return self._result(step, result="BLOCKED", classification="P172_PROFILE_REQUIREMENTS_MISSING", commands=commands, details={"missing": requirement_name})
            argv = [str(python), "-m", "pip", "install"]
            environment: dict[str, str] = {"PIP_DISABLE_PIP_VERSION_CHECK": "1"}
            if wheelhouse is not None:
                if not self._requirements_are_offline_safe(requirement):
                    return self._result(step, result="FAILURE", classification="P172_OFFLINE_REQUIREMENT_NETWORK_REFERENCE", details={"requirements": requirement_name})
                argv.extend(["--no-index", "--find-links", str(wheelhouse)])
                environment.update({"PIP_NO_INDEX": "1", "PIP_FIND_LINKS": str(wheelhouse)})
            argv.extend(["--requirement", str(requirement)])
            command = self.runner.run(argv, cwd=self.source_root, timeout_seconds=step.timeout_seconds, environment=environment)
            commands.append(command)
            if command.classification != "SUCCESS":
                return self._result(step, result=command.classification, classification="P172_DEPENDENCY_INSTALL_FAILED", commands=commands, details={"requirements": requirement_name, "offline": wheelhouse is not None})
        self.state = TransactionState.DEPENDENCIES_READY
        return self._result(
            step,
            commands=commands,
            outputs={"dependency_execution_identity": hash216([item.to_dict() for item in commands], domain="HHS-P172-DEPENDENCY-INSTALL-V1")},
            details={"offline": wheelhouse is not None, "wheelhouse": None if wheelhouse is None else str(wheelhouse)},
        )

    def _build_native_runtime_complete(self, step: PlanStep) -> StepResult:
        builder = NativeBuilder(self.source_root, timeout_seconds=step.timeout_seconds)
        output = self.stage_root / "native"
        targets = (
            NativeTarget(
                target_id="hhs-runtime-abi",
                sources=("hhs_runtime/c/hhs_runtime_abi.c", "hhs_runtime/src/hhs_hash216.c"),
                include_dirs=("hhs_runtime/c", "hhs_runtime/include"),
                required_symbols=("hhs_runtime_init", "hhs_runtime_step", "hhs_validate_abi", "hhs_hash216_compute"),
                artifact_basename="hhs_runtime",
                executable=False,
            ),
            NativeTarget(
                target_id="hhs-vm81",
                sources=("hhs_runtime/HARMONICODE_VM_RUNTIME.c",),
                include_dirs=("hhs_runtime/include",),
                required_symbols=(),
                artifact_basename="hhs_vm81",
                executable=True,
            ),
        )
        results = []
        try:
            for target in targets:
                results.append(builder.build(target, output_directory=output))
        except NativeBuildError as exc:
            return self._result(step, result="BLOCKED" if exc.code.endswith("_MISSING") else "FAILURE", classification=exc.code, details=exc.to_dict())
        self.native_builds = [item.to_dict() for item in results]
        self.state = TransactionState.NATIVE_READY
        return self._result(
            step,
            outputs={item.target_id: item.build_identity for item in results},
            details={"builds": self.native_builds},
        )

    def _verify_native_runtime_complete(self, step: PlanStep) -> StepResult:
        if self.state is not TransactionState.NATIVE_READY or len(self.native_builds) != 2:
            return self._result(step, result="FAILURE", classification="P172_NATIVE_STATE_NOT_READY")
        missing = [item["artifact_path"] for item in self.native_builds if not Path(item["artifact_path"]).is_file()]
        if missing:
            return self._result(step, result="FAILURE", classification="P172_NATIVE_ARTIFACT_MISSING", details={"missing": missing})
        return self._result(
            step,
            outputs={"native_verification_identity": hash216(self.native_builds, domain="HHS-P172-NATIVE-VERIFICATION-V1")},
            details={"portable_builder": True, "builds": self.native_builds},
        )

    def _verify_external_provider_complete(self, step: PlanStep) -> StepResult:
        endpoint = os.environ.get("HHS_LITERT_LM_BASE_URL")
        model = os.environ.get("HHS_LITERT_LM_MODEL", "gemma4-12b")
        authenticated = os.environ.get("HHS_LITERT_LM_AUTHENTICATED", "0") == "1"
        result = ProviderResolver(timeout_seconds=min(step.timeout_seconds, 30)).classify(
            mode="external", endpoint=endpoint, model_id=model, authentication_configured=authenticated
        )
        self.provider_probe = result.to_dict()
        if result.state is not ProviderState.EXTERNAL_READY:
            return self._result(step, result="BLOCKED", classification=result.blocker or "P172_EXTERNAL_PROVIDER_NOT_READY", details=result.to_dict())
        return self._result(step, outputs={"provider_probe_identity": result.probe_identity}, details=result.to_dict())

    def _verify_gpu_substrate(self, step: PlanStep) -> StepResult:
        result = ProviderResolver(timeout_seconds=min(step.timeout_seconds, 30)).classify(
            mode="local",
            endpoint=os.environ.get("HHS_LITERT_LM_BASE_URL", "http://127.0.0.1:9379/v1"),
            model_id=os.environ.get("HHS_LITERT_LM_MODEL", "gemma4-12b"),
            require_gpu=True,
            executable_override=self.provider_executable,
        )
        self.provider_probe = result.to_dict()
        if not result.physical_accelerator or result.substrate == "absent":
            return self._result(step, result="BLOCKED", classification="P172_LOCAL_GPU_SUBSTRATE_MISSING", details=result.to_dict())
        return self._result(step, outputs={"gpu_probe_identity": result.probe_identity}, details=result.to_dict())

    def _install_local_provider(self, step: PlanStep) -> StepResult:
        venv_executable = self.stage_root / "python" / ("Scripts/litert-lm.exe" if platform.system() == "Windows" else "bin/litert-lm")
        executable = venv_executable if venv_executable.is_file() else Path(shutil.which("litert-lm") or "")
        if not executable or not executable.is_file():
            return self._result(step, result="BLOCKED", classification="P172_LITERT_LM_EXECUTABLE_MISSING")
        port = int(self.probe.selected_ports.get("provider", 9379))
        endpoint = os.environ.get("HHS_LITERT_LM_BASE_URL", f"http://127.0.0.1:{port}/v1")
        raw_command = os.environ.get("HHS_LITERT_LM_START_COMMAND")
        if raw_command:
            try:
                values = json.loads(raw_command)
                if not isinstance(values, list) or not values:
                    raise ValueError("start command must be a nonempty JSON list")
                command = [
                    str(item).replace("{executable}", str(executable)).replace("{host}", "127.0.0.1").replace("{port}", str(port))
                    for item in values
                ]
            except (json.JSONDecodeError, ValueError) as exc:
                return self._result(step, result="FAILURE", classification="P172_PROVIDER_START_COMMAND_INVALID", details={"error": str(exc)})
        else:
            command = [str(executable), "serve", "--host", "127.0.0.1", "--port", str(port)]
        log_path = self.stage_root / "provider" / "litert-lm.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._provider_log_handle = log_path.open("ab", buffering=0)
            kwargs: dict[str, Any] = {
                "cwd": str(self.source_root),
                "stdin": subprocess.DEVNULL,
                "stdout": self._provider_log_handle,
                "stderr": subprocess.STDOUT,
                "env": {**os.environ, "PATH": str(executable.parent) + os.pathsep + os.environ.get("PATH", "")},
            }
            if platform.system() == "Windows":
                kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            else:
                kwargs["start_new_session"] = True
            self.provider_process = subprocess.Popen(command, **kwargs)
        except OSError as exc:
            return self._result(step, result="FAILURE", classification="P172_PROVIDER_START_FAILED", details={"error": f"{type(exc).__name__}:{exc}", "command": command})
        time.sleep(0.25)
        if self.provider_process.poll() is not None:
            return self._result(
                step,
                result="FAILURE",
                classification="P172_PROVIDER_EXITED_DURING_STARTUP",
                details={"exit_status": self.provider_process.returncode, "log": str(log_path), "command": command},
            )
        self.provider_executable = executable.resolve()
        self.provider_endpoint = endpoint
        return self._result(
            step,
            outputs={"provider_executable_identity": hash216({"name": executable.name, "command": command}, domain="HHS-P172-PROVIDER-EXECUTABLE-V1")},
            details={"executable": str(executable), "command": command, "endpoint": endpoint, "pid": self.provider_process.pid, "log": str(log_path)},
        )

    def _govern_model(self, step: PlanStep) -> StepResult:
        config_path = os.environ.get("HHS_MODEL_ASSET_REQUEST")
        if not config_path:
            if step.optional:
                return self._result(step, result="NOOP", classification="P172_MODEL_IMPORT_SKIPPED_BY_POLICY")
            return self._result(step, result="BLOCKED", classification="P172_MODEL_ASSET_REQUEST_REQUIRED")
        try:
            payload = json.loads(Path(config_path).read_text(encoding="utf-8"))
            request = ModelAssetRequest(
                registry_id=str(payload["registry_id"]),
                source_reference=str(payload["source_reference"]),
                source_kind=SourceKind(str(payload["source_kind"])),
                filename=str(payload["filename"]),
                version=str(payload["version"]),
                license_id=str(payload["license_id"]),
                expected_sha256=str(payload["expected_sha256"]),
                provider=str(payload["provider"]),
                expected_size=None if payload.get("expected_size") is None else int(payload["expected_size"]),
                authentication_required=bool(payload.get("authentication_required", False)),
            )
            receipt = ModelAssetManager(self.hhs_home / "runtime" / "models").import_asset(
                request,
                network_policy=self.plan.request.network_policy,
                license_accepted=os.environ.get("HHS_MODEL_LICENSE_ACCEPTED", "0") == "1",
                authentication_available=os.environ.get("HHS_MODEL_AUTH_AVAILABLE", "0") == "1",
                available_bytes=shutil.disk_usage(self.hhs_home).free,
            )
        except (OSError, KeyError, ValueError, json.JSONDecodeError, ModelAssetError, AcquisitionError, VerificationError) as exc:
            code = getattr(exc, "code", "P172_MODEL_IMPORT_FAILED")
            details = exc.to_dict() if hasattr(exc, "to_dict") else {"error": f"{type(exc).__name__}:{exc}"}
            return self._result(step, result="FAILURE", classification=code, details=details)
        return self._result(step, outputs={"model_identity": receipt.model_identity, "model_receipt_identity": receipt.receipt_identity}, details=receipt.to_dict())

    def _verify_local_provider(self, step: PlanStep) -> StepResult:
        require_gpu = self.plan.resolved_profile.value == "assistant-local-gpu"
        expected = ProviderState.LOCAL_GPU_READY if require_gpu else ProviderState.LOCAL_CPU_READY
        endpoint = self.provider_endpoint or os.environ.get("HHS_LITERT_LM_BASE_URL", "http://127.0.0.1:9379/v1")
        result = None
        attempts = min(12, max(1, step.timeout_seconds))
        for attempt in range(1, attempts + 1):
            if self.provider_process is not None and self.provider_process.poll() is not None:
                return self._result(
                    step,
                    result="FAILURE",
                    classification="P172_PROVIDER_EXITED_BEFORE_READINESS",
                    details={"exit_status": self.provider_process.returncode, "attempt": attempt},
                )
            result = ProviderResolver(timeout_seconds=min(step.timeout_seconds, 10)).classify(
                mode="local",
                endpoint=endpoint,
                model_id=os.environ.get("HHS_LITERT_LM_MODEL", "gemma4-12b"),
                require_gpu=require_gpu,
                executable_override=self.provider_executable,
            )
            if result.state is expected:
                break
            time.sleep(0.5)
        assert result is not None
        self.provider_probe = result.to_dict()
        if result.state is not expected:
            return self._result(step, result="BLOCKED", classification=result.blocker or "P172_LOCAL_PROVIDER_NOT_READY", details={**result.to_dict(), "attempts": attempts})
        return self._result(
            step,
            outputs={"provider_probe_identity": result.probe_identity},
            details={**result.to_dict(), "pid": None if self.provider_process is None else self.provider_process.pid},
        )

    def _build_android_projection(self, step: PlanStep) -> StepResult:
        project = self.source_root / "android" / "pass145"
        script = project / "build_android.sh"
        gradlew = project / ("gradlew.bat" if platform.system() == "Windows" else "gradlew")
        if script.is_file() and shutil.which("bash"):
            command = self.runner.run([shutil.which("bash") or "bash", str(script)], cwd=project, timeout_seconds=step.timeout_seconds, environment={"GRADLE_OPTS": "-Dorg.gradle.daemon=false"})
        elif gradlew.is_file():
            argv = [str(gradlew), "assembleDebug", "--no-daemon"]
            command = self.runner.run(argv, cwd=project, timeout_seconds=step.timeout_seconds, environment={"GRADLE_OPTS": "-Dorg.gradle.daemon=false"})
        else:
            return self._result(
                step,
                result="BLOCKED",
                classification="P172_ANDROID_PROJECT_ADAPTER_MISSING",
                details={"project": str(project), "script": str(script), "gradlew": str(gradlew)},
            )
        if command.classification != "SUCCESS":
            return self._result(step, result=command.classification, classification="P172_ANDROID_BUILD_FAILED", commands=(command,))
        outputs = sorted(project.rglob("*.apk")) + sorted(project.rglob("*.aab"))
        if not outputs:
            return self._result(step, result="FAILURE", classification="P172_ANDROID_PACKAGE_NOT_PRODUCED", commands=(command,))
        identities = {str(path.relative_to(project)): hash216(path.read_bytes(), domain="HHS-P172-ANDROID-PACKAGE-V1") for path in outputs}
        return self._result(step, commands=(command,), outputs=identities, details={"packages": [str(path) for path in outputs], "project": str(project)})

    def _provider_state_for_pointer(self) -> str:
        if self.provider_probe and self.provider_probe.get("state"):
            return str(self.provider_probe["state"])
        profile = self.plan.resolved_profile.value
        if profile in {"core", "offline", "android-build"}:
            return ProviderState.DISABLED.value
        return ProviderState.DEGRADED.value

    def _write_top_level_launcher(self) -> Path:
        bin_root = self.hhs_home / "bin"
        bin_root.mkdir(parents=True, exist_ok=True)
        launcher_py = bin_root / "hhs_launcher.py"
        launcher_py.write_text(
            "from pathlib import Path\nimport json, os, sys\nroot = Path(__file__).resolve().parents[1]\npointer = json.loads((root / 'current.json').read_text(encoding='utf-8'))\nactive = root / 'versions' / str(pointer['active_version'])\npython = active / 'python' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')\nbootstrap = active / 'runtime-source' / 'hhs-bootstrap.py'\nos.execv(str(python), [str(python), str(bootstrap), *sys.argv[1:]])\n",
            encoding="utf-8",
        )
        if platform.system() == "Windows":
            launcher = bin_root / "hhs.cmd"
            launcher.write_text('@echo off\r\npy -3 "%~dp0hhs_launcher.py" %*\r\n', encoding="utf-8")
        else:
            launcher = bin_root / "hhs"
            launcher.write_text('#!/bin/sh\nexec python3 "$(dirname -- "$0")/hhs_launcher.py" "$@"\n', encoding="utf-8")
            launcher.chmod(0o755)
        return launcher

    def _activate_complete(self, step: PlanStep) -> StepResult:
        result = super()._activate(step)
        if result.result != "SUCCESS":
            return result
        pointer_path = self.hhs_home / "current.json"
        payload = json.loads(pointer_path.read_text(encoding="utf-8"))
        payload.update(
            {
                "requested_profile": self.plan.requested_profile.value,
                "resolved_profile": self.plan.resolved_profile.value,
                "provider_state": self._provider_state_for_pointer(),
                "provider_endpoint": self.provider_endpoint,
                "provider_pid": None if self.provider_process is None else self.provider_process.pid,
                "plan_identity": self.plan.plan_identity,
                "platform": self.probe.platform,
                "architecture": self.probe.architecture,
            }
        )
        atomic_write_json(pointer_path, payload)
        try:
            launcher = self._write_top_level_launcher()
        except OSError as exc:
            return self._result(step, result="FAILURE", classification="P172_ACTIVE_LAUNCHER_CREATION_FAILED", details={"error": f"{type(exc).__name__}:{exc}"})
        outputs = dict(result.output_identities)
        outputs["active_pointer_identity"] = hash216(payload, domain="HHS-P172-ACTIVE-POINTER-V1")
        outputs["active_launcher_identity"] = hash216(launcher.read_bytes(), domain="HHS-P172-ACTIVE-LAUNCHER-V1")
        return self._result(step, outputs=outputs, details={**result.details, "pointer": payload, "launcher": str(launcher)})

    def _verify_active_complete(self, step: PlanStep) -> StepResult:
        base = super()._verify_active(step)
        if base.result != "SUCCESS":
            return base
        pointer = json.loads((self.hhs_home / "current.json").read_text(encoding="utf-8"))
        active = self.hhs_home / "versions" / str(pointer["active_version"])
        required = [
            active / "runtime-source" / "hhs-bootstrap.py",
            active / "python" / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python"),
            self.hhs_home / "bin" / ("hhs.cmd" if platform.system() == "Windows" else "hhs"),
        ]
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            return self._result(step, result="FAILURE", classification="P172_ACTIVE_INSTALLATION_INCOMPLETE", details={"missing": missing})
        return self._result(
            step,
            outputs={"active_installation_identity": hash216({"pointer": pointer, "required": [str(path) for path in required]}, domain="HHS-P172-ACTIVE-INSTALLATION-V1")},
            details={"active": str(active), "required": [str(path) for path in required]},
        )
