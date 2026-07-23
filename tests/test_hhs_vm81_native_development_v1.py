from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest

from native_projects.hhs_vm81_native_development.hhs_vm81_native_development_v1 import (
    LEVEL_0_EXPLICIT_GAPS,
    LEVEL_1_INITIAL_EXECUTION_SYMBOLS,
    build_architecture_surface,
)

ROOT = Path(__file__).resolve().parents[1]


def test_architecture_surface_is_deterministic_and_truth_preserving():
    first = build_architecture_surface(ROOT)
    second = build_architecture_surface(ROOT)
    assert first == second
    assert first["vm81_cell_count"] == 81
    assert first["hash216_position_count"] == 216
    assert first["capability_counts"]["legacy_public_c_abi_callable"] == 29
    assert first["capability_counts"]["hash72_hash216_public_c_abi_callable"] == 8
    assert first["capability_counts"]["total_public_c_abi_callable"] == 37
    assert first["closure"]["all_legacy_direct_abi_capabilities_bound"] is True
    assert first["closure"]["all_current_linked_direct_abi_capabilities_bound"] is False
    assert first["closure"]["level0_terminal_classification_emitted"] is False
    assert first["closure"]["level1_terminal_classification_emitted"] is False


def test_hash72_compare_schema_erratum_preserves_frozen_c_semantics():
    surface = build_architecture_surface(ROOT)
    compare = next(entry for entry in surface["entries"] if entry["symbol"] == "hhs_hash72_compare")
    assert compare["declared_output_schema"] == {"type": "integer", "enum": [-1, 0, 1]}
    assert compare["effective_output_schema"] == {"type": "integer", "minimum": 0, "maximum": 72}
    erratum = surface["contract_errata"][0]
    assert erratum["native_semantics_modified"] is False
    assert erratum["frozen_c_semantics"] == "UINT64_POSITIONAL_MATCH_SCORE_0_TO_72"


def test_float_surfaces_are_explicitly_non_authoritative():
    surface = build_architecture_surface(ROOT)
    by_symbol = {entry["symbol"]: entry for entry in surface["entries"]}
    for symbol in (
        "hhs_srcg_init",
        "hhs_srcg_step",
        "hhs_srcg_validate",
        "hhs_sizeof_srcg_state",
        "hhs_vectorize_hash72",
    ):
        assert by_symbol[symbol]["numeric_authority"] == "NON_AUTHORITATIVE_FLOAT_CONTROL_ONLY"


def test_missing_capabilities_remain_explicit_and_unclaimed():
    surface = build_architecture_surface(ROOT)
    assert set(LEVEL_0_EXPLICIT_GAPS) <= set(surface["explicit_missing_capabilities"])
    assert set(LEVEL_1_INITIAL_EXECUTION_SYMBOLS) <= set(surface["initial_level1_execution_symbols"])
    assert surface["implementation_status"] == "FOUNDATION_IMPLEMENTED_TERMINAL_VERIFICATION_NOT_YET_CLAIMED"


def _compile_and_run(tmp_path: Path, source: Path, implementation: Path, include_dir: Path, expected: str) -> None:
    compiler = shutil.which("cc") or shutil.which("gcc")
    if compiler is None:
        pytest.skip("C compiler unavailable")
    binary = tmp_path / source.stem
    command = [
        compiler,
        "-std=c11",
        "-O2",
        "-Wall",
        "-Wextra",
        f"-I{include_dir}",
        str(source),
        str(implementation),
        "-lm",
        "-o",
        str(binary),
    ]
    compiled = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    executed = subprocess.run([str(binary)], cwd=ROOT, text=True, capture_output=True)
    assert executed.returncode == 0, executed.stdout + executed.stderr
    assert expected in executed.stdout


def test_direct_c_abi_exact_foundation_smoke(tmp_path: Path):
    _compile_and_run(
        tmp_path,
        ROOT / "native_projects/hhs_vm81_native_development/c/hhs_vm81_level1_abi_smoke.c",
        ROOT / "hhs_runtime/c/hhs_runtime_abi.c",
        ROOT / "hhs_runtime/c",
        "VM81_DIRECT_C_ABI_FOUNDATION_SMOKE_PASSED",
    )


def test_hash216_identity_foundation_smoke(tmp_path: Path):
    _compile_and_run(
        tmp_path,
        ROOT / "native_projects/hhs_vm81_native_development/c/hhs_hash216_level0_smoke.c",
        ROOT / "hhs_runtime/src/hhs_hash216.c",
        ROOT / "hhs_runtime/include",
        "HASH216_IDENTITY_FOUNDATION_SMOKE_PASSED",
    )
