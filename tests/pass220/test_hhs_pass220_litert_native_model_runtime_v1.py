from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest

from hhs_backend.runtime.hhs_pass220_native_litert_runtime_v1 import (
    NativeLiteRTModelRegistry,
    NativeLiteRTTensorSpec,
    litert1_contract,
    tensor_specs_from_litert_details,
)

ROOT = Path(__file__).resolve().parents[2]
MODEL_NATIVE = ROOT / "native_projects" / "hhs_pass220_litert_native_model_runtime"
MODEL_SOURCE = MODEL_NATIVE / "src" / "hhs_pass220_litert_native_model_runtime_v1.c"
EXACT_SOURCE = ROOT / "hhs_runtime" / "c" / "hhs_runtime_exact_abi.c"
EXACT_INCLUDE = ROOT / "hhs_runtime" / "include"


@pytest.fixture()
def native_libraries(tmp_path: Path) -> tuple[Path, Path]:
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("C compiler unavailable")

    model_shared = tmp_path / "libhhs_litert_native_model_runtime_v1.so"
    exact_shared = tmp_path / "libhhs_runtime_exact_abi.so"

    subprocess.run(
        [
            cc,
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-fPIC",
            "-shared",
            f"-I{MODEL_NATIVE / 'include'}",
            str(MODEL_SOURCE),
            "-o",
            str(model_shared),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    subprocess.run(
        [
            cc,
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-fPIC",
            "-shared",
            f"-I{EXACT_INCLUDE}",
            str(EXACT_SOURCE),
            "-o",
            str(exact_shared),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return model_shared, exact_shared


def _registry(native_libraries: tuple[Path, Path]) -> NativeLiteRTModelRegistry:
    model_shared, exact_shared = native_libraries
    return NativeLiteRTModelRegistry(model_shared, exact_shared)


def _tensors() -> tuple[NativeLiteRTTensorSpec, ...]:
    return (
        NativeLiteRTTensorSpec(
            name="tokens",
            role="input",
            dtype="int32",
            shape=(1, 4096),
        ),
        NativeLiteRTTensorSpec(
            name="logits",
            role="output",
            dtype="float32",
            shape=(1, 1, 256000),
        ),
    )


def test_litert1_registers_model_and_shared_rna_runtime_class(
    native_libraries: tuple[Path, Path],
) -> None:
    registration = _registry(native_libraries).register(
        model_id="gemma4-12b",
        source_identity="litert-community/gemma-4-12B-it-litert-lm",
        generation=1,
        backend="native",
        context_tokens=8192,
        max_output_tokens=2048,
        tensors=_tensors(),
    )

    assert registration.schema == "HHS_PASS_220_LITERT1_NATIVE_MODEL_RUNTIME_V1"
    assert registration.model_id == "gemma4-12b"
    assert len(registration.model_identity_hash216) == 216
    assert len(registration.source_sha256) == 64
    assert registration.tensor_count == 2
    assert registration.input_count == 1
    assert registration.output_count == 1
    assert registration.registration_fingerprint64 != 0
    assert len(registration.rna_runtime_class_hash216) == 216
    assert registration.rna_runtime_class_fingerprint64 != 0
    assert registration.model_output_advisory_only is True
    assert registration.vm81_mutation_authority is False
    assert registration.hash72_commit_authority is False
    assert registration.hash216_persistence_authority is False
    assert registration.floating_point_canonical_authority is False
    assert registration.external_litert_compatibility_supported is True


def test_litert1_model_identity_changes_but_runtime_class_identity_is_shared(
    native_libraries: tuple[Path, Path],
) -> None:
    registry = _registry(native_libraries)
    first = registry.register(
        model_id="gemma4-12b",
        source_identity="artifact-generation-1",
        generation=1,
        backend="native",
        context_tokens=8192,
        max_output_tokens=2048,
        tensors=_tensors(),
    )
    second = registry.register(
        model_id="gemma4-12b",
        source_identity="artifact-generation-2",
        generation=2,
        backend="native",
        context_tokens=8192,
        max_output_tokens=2048,
        tensors=_tensors(),
    )

    assert first.model_identity_hash216 != second.model_identity_hash216
    assert first.registration_fingerprint64 != second.registration_fingerprint64
    assert first.rna_runtime_class_hash216 == second.rna_runtime_class_hash216
    assert (
        first.rna_runtime_class_fingerprint64
        == second.rna_runtime_class_fingerprint64
    )


def test_litert1_external_tensor_metadata_can_enter_native_registry(
    native_libraries: tuple[Path, Path],
) -> None:
    tensors = tensor_specs_from_litert_details(
        [
            {
                "name": "serving_default_tokens:0",
                "shape": [1, 2048],
                "dtype": "int32",
            }
        ],
        [
            {
                "name": "StatefulPartitionedCall:0",
                "shape": [1, 1, 32000],
                "dtype": "float32",
            }
        ],
    )
    registration = _registry(native_libraries).register(
        model_id="external-compatible-model",
        source_identity=b"external-model-bytes",
        generation=3,
        backend="external",
        context_tokens=4096,
        max_output_tokens=1024,
        tensors=tensors,
    )
    assert registration.backend == "external"
    assert registration.tensor_count == 2
    assert registration.external_litert_compatibility_supported is True


def test_litert1_contract_makes_external_cli_optional() -> None:
    contract = litert1_contract()
    assert contract["internal_runtime"] == "HHS_NATIVE"
    assert contract["external_litert_lm_cli_required_for_default_runtime"] is False
    assert contract["external_litert_lm_compatibility_retained"] is True
    assert contract["external_openai_compatible_http_retained"] is True
    assert contract["pass153_litert_interpreter_adapter_retained"] is True
    assert contract["python2_rna_runtime_class_binding"] is True
    assert contract["model_output_advisory_only"] is True
    assert contract["vm81_mutation_authority"] is False
    assert contract["tensor_numeric_execution_next"] == "NUMPY1_HARMONICODE"


def test_default_repository_dependency_closure_excludes_external_litert_package() -> None:
    root_requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    compatibility_requirements = (
        ROOT / "requirements-litert-lm.txt"
    ).read_text(encoding="utf-8")
    assert "-r requirements-litert-lm.txt" not in root_requirements
    assert "litert-lm==0.14.0" in compatibility_requirements


def test_launcher_defaults_to_native_but_retains_explicit_compatibility_modes() -> None:
    source = (ROOT / "start.sh").read_text(encoding="utf-8")
    assert 'HHS_LITERT_LM_PROVIDER_MODE:-native' in source
    assert 'native|auto|local|external|disabled' in source
    assert 'Using repository-native LiteRT-compatible language provider' in source
    assert '"$litert_bin" serve' in source
    assert 'bootstrap_litert_lm.sh" --print-bin' in source


def test_production_assistant_has_native_first_mode_without_external_probe() -> None:
    source = (
        ROOT / "hhs_backend" / "runtime" / "hhs_production_assistant_v1.py"
    ).read_text(encoding="utf-8")
    assert 'os.getenv("HHS_LITERT_LM_PROVIDER_MODE", "native")' in source
    assert 'self.native_first = self.provider_mode == "native" and model_service is None' in source
    assert '"EXTERNAL_LITERT_COMPATIBILITY_NOT_SELECTED"' in source


def test_native_litert_runtime_has_no_external_litert_package_import() -> None:
    source = (
        ROOT
        / "hhs_backend"
        / "runtime"
        / "hhs_pass220_native_litert_runtime_v1.py"
    ).read_text(encoding="utf-8").lower()
    assert "import litert_lm" not in source
    assert "from litert_lm" not in source
    assert "ai_edge_litert" not in source
    assert "tflite_runtime" not in source
