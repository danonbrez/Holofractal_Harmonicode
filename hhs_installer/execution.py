from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import json
import os
import platform
import shutil

from .acquisition import AcquisitionError, SourceAcquirer
from .canonical import hash216
from .model_assets import ModelAssetManager, ModelAssetRequest, ModelAssetError
from .offline import OfflineBundleError, OfflineBundleVerifier
from .planner import PlanStep
from .provider import ProviderResolver, ProviderState
from .schema import NetworkPolicy, PrivilegePolicy, SourceKind
from .security import ArchivePolicy, SecurityError, extract_archive
from .transaction import InstallationTransaction, StepResult, TransactionState
from .verification import VerificationError


class CompleteInstallationTransaction(InstallationTransaction):
    """Pass 172 transaction with all implemented adapter handlers.

    It extends the single Pass 172 transaction authority; it is not a parallel
    installer. All canonical Runtime authority remains outside this class.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.acquired_source: dict[str, Any] | None = None
        self.source_root = self.repository_root
        self.provider_probe: dict[str, Any] | None = None
        self.handlers.update(
            {
                "acquire_source": self._acquire_source_complete,
                "verify_source": self._verify_source_complete,
                "verify_offline_bundle": self._verify_offline_bundle_complete,
                "build_native_runtime": self._build_native_runtime,
                "verify_external_provider": self._verify_external_provider_complete,
                "verify_or_install_gpu_loader": self._verify_gpu_substrate,
                "install_local_provider": self._install_local_provider,
                "acquire_verify_import_model": self._govern_model,
                "verify_local_provider": self._verify_local_provider,
                "build_android_projection": self._build_android_projection,
            }
        )

    def _acquire_source_complete(self, step: PlanStep) -> StepResult:
        cache = self.hhs_home / "install" / "cache" / "sources"
        try:
            result = SourceAcquirer(cache).acquire(
                self.plan.request.source,
                network_policy=self.plan.request.network_policy,
            )
        except AcquisitionError as exc:
            return self._result(
                step,
                result="BLOCKED" if exc.code in {
                    "P172_DOWNLOAD_RETRIES_EXHAUSTED",
                    "P172_GIT_ACQUISITION_ADAPTER_REQUIRED",
                    "P172_CACHED_SOURCE_UNAVAILABLE",
                } else "FAILURE",
                classification=exc.code,
                details=exc.to_dict(),
            )
        self.acquired_source = result.to_dict()
        local_path = Path(result.local_path)
        if local_path.is_file() and self.plan.request.source.kind in {SourceKind.RELEASE, SourceKind.OFFLINE_BUNDLE}:
            source_stage = self.hhs_home / "install" / "staging" / self.transaction_id / "source"
            try:
                inspection = extract_archive(local_path, source_stage, policy=ArchivePolicy())
            except SecurityError as exc:
                return self._result(step, result="FAILURE", classification=exc.code, details=exc.to_dict())
            children = [path for path in source_stage.iterdir()]
            self.source_root = children[0] if len(children) == 1 and children[0].is_dir() else source_stage
            outputs = {
                "acquisition_identity": result.acquisition_identity,
                "archive_inspection_identity": inspection.inspection_identity,
            }
        else:
            self.source_root = local_path
            outputs = {"acquisition_identity": result.acquisition_identity}
        self.repository_root = self.source_root
        self.state = TransactionState.SOURCE_ACQUIRED
        return self._result(step, details=self.acquired_source, outputs=outputs)

    def _verify_source_complete(self, step: PlanStep) -> StepResult:
        if self.acquired_source is None:
            return self._result(step, result="FAILURE", classification="P172_SOURCE_NOT_ACQUIRED")
        contracts = (
            self.source_root / "HHS_PASS_172_UNIVERSAL_COMPATIBLE_ENVIRONMENT_ONE_COMMAND_INSTALLATION_DEPENDENCY_RESOLUTION_VERIFIED_BOOTSTRAP_AND_RUNTIME_ACTIVATION_SYSTEM.md",
            self.source_root / "HHS_PASS_173_UNIVERSAL_INSTALLATION_FULL_COVERAGE_REDUNDANT_VERIFICATION_CALIBRATION_REPAIR_AND_REPLAY_CLOSURE_RUNTIME.md",
        )
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
        return self._result(step, outputs={"offline_verification_identity": result.verification_identity}, details=result.to_dict())

    def _verify_external_provider_complete(self, step: PlanStep) -> StepResult:
        endpoint = os.environ.get("HHS_LITERT_LM_BASE_URL")
        model = os.environ.get("HHS_LITERT_LM_MODEL", "gemma4-12b")
        authenticated = os.environ.get("HHS_LITERT_LM_AUTHENTICATED", "0") == "1"
        result = ProviderResolver(timeout_seconds=min(step.timeout_seconds, 30)).classify(
            mode="external",
            endpoint=endpoint,
            model_id=model,
            authentication_configured=authenticated,
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
        )
        self.provider_probe = result.to_dict()
        if not result.physical_accelerator or result.substrate == "absent":
            return self._result(step, result="BLOCKED", classification="P172_LOCAL_GPU_SUBSTRATE_MISSING", details=result.to_dict())
        return self._result(step, outputs={"gpu_probe_identity": result.probe_identity}, details=result.to_dict())

    def _install_local_provider(self, step: PlanStep) -> StepResult:
        venv_executable = self.stage_root / "python" / ("Scripts/litert-lm.exe" if platform.system() == "Windows" else "bin/litert-lm")
        executable = venv_executable if venv_executable.exists() else Path(shutil.which("litert-lm") or "")
        if not executable or not executable.exists():
            return self._result(step, result="BLOCKED", classification="P172_LITERT_LM_EXECUTABLE_MISSING")
        return self._result(
            step,
            outputs={"provider_executable_identity": hash216({"name": executable.name}, domain="HHS-P172-PROVIDER-EXECUTABLE-V1")},
            details={"executable": str(executable)},
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
        result = ProviderResolver(timeout_seconds=min(step.timeout_seconds, 30)).classify(
            mode="local",
            endpoint=os.environ.get("HHS_LITERT_LM_BASE_URL", "http://127.0.0.1:9379/v1"),
            model_id=os.environ.get("HHS_LITERT_LM_MODEL", "gemma4-12b"),
            require_gpu=require_gpu,
        )
        self.provider_probe = result.to_dict()
        expected = ProviderState.LOCAL_GPU_READY if require_gpu else ProviderState.LOCAL_CPU_READY
        if result.state is not expected:
            return self._result(step, result="BLOCKED", classification=result.blocker or "P172_LOCAL_PROVIDER_NOT_READY", details=result.to_dict())
        return self._result(step, outputs={"provider_probe_identity": result.probe_identity}, details=result.to_dict())

    def _build_android_projection(self, step: PlanStep) -> StepResult:
        gradlew = self.source_root / "gradlew"
        if not gradlew.is_file():
            return self._result(step, result="BLOCKED", classification="P172_ANDROID_GRADLE_WRAPPER_MISSING")
        command = self.runner.run(
            [str(gradlew), "assembleDebug", "--no-daemon"],
            cwd=self.source_root,
            timeout_seconds=step.timeout_seconds,
            environment={"GRADLE_OPTS": "-Dorg.gradle.daemon=false"},
        )
        if command.classification != "SUCCESS":
            return self._result(step, result=command.classification, classification="P172_ANDROID_BUILD_FAILED", commands=(command,))
        outputs = sorted(self.source_root.rglob("*.apk")) + sorted(self.source_root.rglob("*.aab"))
        if not outputs:
            return self._result(step, result="FAILURE", classification="P172_ANDROID_PACKAGE_NOT_PRODUCED", commands=(command,))
        identities = {path.name: hash216(path.read_bytes(), domain="HHS-P172-ANDROID-PACKAGE-V1") for path in outputs}
        return self._result(step, commands=(command,), outputs=identities, details={"packages": [str(path) for path in outputs]})
