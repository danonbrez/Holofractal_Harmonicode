from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess

import pytest

from hhs_installer.acquisition import AcquisitionError, SourceAcquirer
from hhs_installer.execution import CompleteInstallationTransaction
from hhs_installer.model_assets import ModelAssetError, ModelAssetRequest
from hhs_installer.native_builder import NativeBuilder, NativeToolchain
from hhs_installer.planner import InstallationPlan, PlanStep
from hhs_installer.probe import Capability, ProbeReport
from hhs_installer.provider import ProviderResolver, ProviderState
from hhs_installer.schema import CompatibilityClass, InstallationRequest, NetworkPolicy, Profile, SourceKind, SourceSpec
from hhs_installer.transaction import CommandResult


def _probe(*, profile: Profile = Profile.CORE) -> ProbeReport:
    return ProbeReport(
        platform="Linux",
        platform_release="test",
        architecture="x86_64",
        python_version="3.11",
        capabilities=(Capability("python_3_11", True, "3.11", ">=3.11"),),
        compatible_profiles=(profile,),
        primary_classification=CompatibilityClass.CORE_ONLY,
        selected_ports={"api": 8000, "provider": 9379},
    )


def _transaction(tmp_path: Path, *, profile: Profile = Profile.CORE, network: NetworkPolicy = NetworkPolicy.ONLINE) -> CompleteInstallationTransaction:
    source = tmp_path / "repo"
    source.mkdir(exist_ok=True)
    request = InstallationRequest(
        source=SourceSpec(SourceKind.LOCAL, str(source)),
        profile=profile,
        network_policy=network,
        hhs_home=str(tmp_path / "home"),
    )
    plan = InstallationPlan(
        request=request,
        probe_identity=_probe(profile=profile).probe_identity,
        requested_profile=profile,
        resolved_profile=profile,
        steps=(),
        external_packages=(),
        excluded_dependency_classes=(),
    )
    return CompleteInstallationTransaction(plan, _probe(profile=profile), repository_root=source)


def test_model_request_rejects_path_components() -> None:
    with pytest.raises(ModelAssetError) as raised:
        ModelAssetRequest(
            registry_id="../escape",
            source_reference="model.bin",
            source_kind=SourceKind.LOCAL,
            filename="model.bin",
            version="1",
            license_id="test",
            expected_sha256="0" * 64,
            provider="test",
        )
    assert raised.value.code == "P172_MODEL_PATH_COMPONENT_INVALID"


@pytest.mark.parametrize("filename", ["../model.bin", "/tmp/model.bin", "folder/model.bin"])
def test_model_request_rejects_unsafe_filenames(filename: str) -> None:
    with pytest.raises(ModelAssetError) as raised:
        ModelAssetRequest(
            registry_id="model",
            source_reference="model.bin",
            source_kind=SourceKind.LOCAL,
            filename=filename,
            version="1",
            license_id="test",
            expected_sha256="0" * 64,
            provider="test",
        )
    assert raised.value.code == "P172_MODEL_PATH_COMPONENT_INVALID"


def test_local_digest_mismatch_is_acquisition_error(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"payload")
    with pytest.raises(AcquisitionError) as raised:
        SourceAcquirer(tmp_path / "cache").acquire(
            SourceSpec(SourceKind.LOCAL, str(source), "0" * 64),
            network_policy=NetworkPolicy.OFFLINE,
        )
    assert raised.value.code == "P172_SOURCE_IDENTITY_MISMATCH"


def test_layout_stages_runtime_source_and_launcher(tmp_path: Path) -> None:
    transaction = _transaction(tmp_path)
    source = transaction.source_root
    (source / "hhs-bootstrap.py").write_text("print('hhs')\n", encoding="utf-8")
    for name in transaction.CONTRACT_NAMES:
        (source / name).write_text("contract\n", encoding="utf-8")
    step = PlanStep("layout-stage", "create_layout", (), 30, "none")
    result = transaction.handlers["create_layout"](step)
    assert result.result == "SUCCESS"
    assert (transaction.stage_root / "runtime-source" / "hhs-bootstrap.py").is_file()
    assert (transaction.stage_root / "bin" / "hhs").is_file()


def test_offline_dependency_install_forces_no_index(tmp_path: Path) -> None:
    transaction = _transaction(tmp_path, network=NetworkPolicy.OFFLINE)
    (transaction.source_root / "requirements-core.txt").write_text("example-package==1.0\n", encoding="utf-8")
    venv_python = transaction.stage_root / "python" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text("", encoding="utf-8")
    wheelhouse = tmp_path / "bundle" / "wheels"
    wheelhouse.mkdir(parents=True)
    transaction.offline_bundle_root = wheelhouse.parent
    captured: dict[str, object] = {}

    def fake_run(argv, *, cwd, timeout_seconds, environment=None):
        captured["argv"] = list(argv)
        captured["environment"] = dict(environment or {})
        return CommandResult(tuple(argv), str(cwd), 0, "SUCCESS", "", "", 1, False)

    transaction.runner.run = fake_run  # type: ignore[method-assign]
    step = PlanStep("dependencies-install", "install_profile_dependencies", (), 30, "none")
    result = transaction.handlers["install_profile_dependencies"](step)
    assert result.result == "SUCCESS"
    assert "--no-index" in captured["argv"]
    assert captured["environment"]["PIP_NO_INDEX"] == "1"


def test_offline_requirements_reject_direct_network_reference(tmp_path: Path) -> None:
    transaction = _transaction(tmp_path, network=NetworkPolicy.OFFLINE)
    (transaction.source_root / "requirements-core.txt").write_text("package @ https://example.invalid/package.whl\n", encoding="utf-8")
    venv_python = transaction.stage_root / "python" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text("", encoding="utf-8")
    wheelhouse = tmp_path / "bundle" / "wheels"
    wheelhouse.mkdir(parents=True)
    transaction.offline_bundle_root = wheelhouse.parent
    step = PlanStep("dependencies-install", "install_profile_dependencies", (), 30, "none")
    result = transaction.handlers["install_profile_dependencies"](step)
    assert result.classification == "P172_OFFLINE_REQUIREMENT_NETWORK_REFERENCE"


def test_complete_transaction_uses_portable_native_builder(tmp_path: Path) -> None:
    transaction = _transaction(tmp_path)
    handler = transaction.handlers["build_native_runtime"]
    assert getattr(handler, "__func__", None) is CompleteInstallationTransaction._build_native_runtime_complete


def test_android_handler_does_not_use_unrelated_root_gradle_wrapper(tmp_path: Path) -> None:
    transaction = _transaction(tmp_path, profile=Profile.ANDROID_BUILD)
    (transaction.source_root / "gradlew").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    step = PlanStep("android-build", "build_android_projection", (), 30, "none")
    result = transaction.handlers["build_android_projection"](step)
    assert result.classification == "P172_ANDROID_PROJECT_ADAPTER_MISSING"


def test_provider_resolver_accepts_staged_executable_override(tmp_path: Path, monkeypatch) -> None:
    executable = tmp_path / "litert-lm"
    executable.write_text("", encoding="utf-8")
    resolver = ProviderResolver(timeout_seconds=1)
    monkeypatch.setattr(resolver, "_verify_endpoint", lambda endpoint, model_id: (True, True, None))
    result = resolver.classify(
        mode="local",
        endpoint="http://127.0.0.1:9379/v1",
        model_id="gemma4-12b",
        executable_override=executable,
    )
    assert result.state is ProviderState.LOCAL_CPU_READY
    assert result.executable == str(executable.resolve())


def test_symbol_inspection_tries_next_available_tool(tmp_path: Path, monkeypatch) -> None:
    artifact = tmp_path / "libtest.so"
    artifact.write_bytes(b"binary")
    toolchain = NativeToolchain(
        compiler="cc",
        symbol_inspector="/fake/llvm-nm",
        platform="Linux",
        architecture="x86_64",
        library_suffix=".so",
        executable_suffix="",
        compiler_identity="identity",
    )
    monkeypatch.setattr("hhs_installer.native_builder.shutil.which", lambda name: "/usr/bin/nm" if name == "nm" else None)

    def fake_run(argv, **kwargs):
        if argv[0] == "/fake/llvm-nm":
            return subprocess.CompletedProcess(argv, 1, "", "broken")
        return subprocess.CompletedProcess(argv, 0, "00000000 T hhs_runtime_version\n", "")

    monkeypatch.setattr("hhs_installer.native_builder.subprocess.run", fake_run)
    symbols = NativeBuilder(tmp_path).inspect_symbols(artifact, toolchain=toolchain)
    assert symbols == ("hhs_runtime_version",)


def test_offline_target_normalization() -> None:
    assert CompleteInstallationTransaction._supported("AMD64", ("x86_64",)) is True
    assert CompleteInstallationTransaction._supported("Linux", ("Darwin",)) is False


def test_hosted_evidence_workflow_preserves_pipeline_status() -> None:
    workflow = Path(".github/workflows/pass172-173-phase2-evidence.yml").read_text(encoding="utf-8")
    assert "set -o pipefail" in workflow
    assert "python -m pytest -q tests/pass172 tests/pass173 | tee" in workflow
