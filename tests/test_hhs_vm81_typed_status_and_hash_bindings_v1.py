from pathlib import Path
import shutil
import subprocess

import pytest

from native_projects.hhs_vm81_native_development.hhs_hash_native_binding_registry_v1 import (
    EXPECTED_SYMBOLS,
    build_registry,
)
from native_projects.hhs_vm81_native_development.hhs_vm81_native_development_v1 import (
    TYPED_EXECUTION_STATUSES,
    build_architecture_surface,
)

ROOT = Path(__file__).resolve().parents[1]


def test_hash_binding_registry_is_complete_and_deterministic():
    first = build_registry(ROOT)
    assert first == build_registry(ROOT)
    assert first["registered_bindings"] == first["expected_bindings"] == 8
    assert first["all_expected_bindings_present"] is True
    assert {entry["abi_symbol"] for entry in first["entries"]} == set(EXPECTED_SYMBOLS)
    assert all(entry["binding_root_hash72"] for entry in first["entries"])
    assert all(entry["callable"] is True for entry in first["entries"])
    assert all(entry["compiler_may_synthesize"] is False for entry in first["entries"])


def test_typed_execution_result_abi_declares_required_statuses_and_guards():
    surface = build_architecture_surface(ROOT)
    typed = surface["typed_execution_result_abi"]
    assert set(typed["statuses"]) == set(TYPED_EXECUTION_STATUSES)
    assert typed["checked_integer_multiplication"] is True
    assert typed["checked_integer_addition"] is True
    assert typed["rejected_request_state_restoration"] is True
    assert typed["authority_admission_marker"] == "PREVALIDATED_MARKER_NOT_SINGLE_USE_MUTATION_CAPABILITY"
    assert surface["closure"]["typed_invalid_opcode_status_declared"] is True
    assert surface["closure"]["typed_invalid_operand_status_declared"] is True
    assert surface["closure"]["typed_arithmetic_overflow_status_declared"] is True


def test_completed_gaps_are_removed_without_claiming_single_use_capability():
    gaps = set(build_architecture_surface(ROOT)["explicit_missing_capabilities"])
    assert "invalid_opcode_dispatch_status" not in gaps
    assert "typed_invalid_operand_status" not in gaps
    assert "hash216_functions_absent_from_pass079_native_opcode_registry" not in gaps
    assert "single_use_vm81_mutation_capability" in gaps


def test_typed_status_and_rejection_state_preservation_native_smoke(tmp_path: Path):
    compiler = shutil.which("cc") or shutil.which("gcc")
    if compiler is None:
        pytest.skip("C compiler unavailable")
    binary = tmp_path / "hhs_vm81_typed_status_smoke"
    command = [
        compiler,
        "-std=c11",
        "-O2",
        "-Wall",
        "-Wextra",
        f"-I{ROOT / 'hhs_runtime/c'}",
        f"-I{ROOT / 'native_projects/hhs_vm81_native_development/c'}",
        str(ROOT / "native_projects/hhs_vm81_native_development/c/hhs_vm81_typed_status_smoke.c"),
        str(ROOT / "native_projects/hhs_vm81_native_development/c/hhs_vm81_native_dev_abi.c"),
        str(ROOT / "hhs_runtime/c/hhs_runtime_abi.c"),
        "-lm",
        "-o",
        str(binary),
    ]
    compiled = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    executed = subprocess.run([str(binary)], cwd=ROOT, text=True, capture_output=True)
    assert executed.returncode == 0, executed.stdout + executed.stderr
    assert "VM81_TYPED_STATUS_AND_REJECTION_STATE_PRESERVATION_PASSED" in executed.stdout
