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


def test_architecture_surface_is_deterministic():
    assert build_architecture_surface(ROOT) == build_architecture_surface(ROOT)


def test_architecture_dimensions_are_exact():
    surface = build_architecture_surface(ROOT)
    assert surface["vm81_cell_count"] == 81
    assert surface["hash216_position_count"] == 216


def test_legacy_public_abi_count_matches_pass079():
    surface = build_architecture_surface(ROOT)
    assert surface["capability_counts"]["legacy_public_c_abi_callable"] == 29
    assert surface["capability_counts"]["pass079_registered_native_opcodes"] == 29
    assert surface["closure"]["all_legacy_direct_abi_capabilities_bound"] is True


def test_hash72_hash216_linked_abi_is_bound():
    surface = build_architecture_surface(ROOT)
    assert surface["capability_counts"]["hash72_hash216_public_c_abi_callable"] == 8
    assert surface["capability_counts"]["hash_native_registered_bindings"] == 8
    assert surface["capability_counts"]["total_public_c_abi_callable"] == 37
    assert surface["closure"]["all_hash72_hash216_direct_abi_capabilities_bound"] is True
    assert surface["closure"]["all_current_linked_direct_abi_capabilities_bound"] is True


def test_hash72_compare_schema_erratum_preserves_frozen_c_semantics():
    surface = build_architecture_surface(ROOT)
    compare = next(
        entry for entry in surface["entries"]
        if entry["symbol"] == "hhs_hash72_compare"
    )
    assert compare["declared_output_schema"] == {
        "type": "integer",
        "enum": [-1, 0, 1],
    }
    assert compare["effective_output_schema"] == {
        "type": "integer",
        "minimum": 0,
        "maximum": 72,
    }
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
        assert by_symbol[symbol]["numeric_authority"] == (
            "NON_AUTHORITATIVE_FLOAT_CONTROL_ONLY"
        )


def test_resolver_is_closed_while_mutation_gaps_remain_explicit():
    surface = build_architecture_surface(ROOT)
    assert set(LEVEL_0_EXPLICIT_GAPS) == set(
        surface["explicit_missing_capabilities"]
    )
    assert "hash216_logical_address_resolver" not in (
        surface["explicit_missing_capabilities"]
    )
    assert "vector_write_append_resize_release_operations" in (
        surface["explicit_missing_capabilities"]
    )
    assert "single_use_vm81_mutation_capability" in (
        surface["explicit_missing_capabilities"]
    )
    assert set(LEVEL_1_INITIAL_EXECUTION_SYMBOLS) <= {
        entry["symbol"] for entry in surface["entries"]
    }
    assert surface["closure"]["hash216_logical_address_resolver_implemented"] is True
    assert surface["closure"]["bounded_immutable_vector_descriptor_implemented"] is True
    assert surface["closure"]["bounded_vresolve_implemented"] is True
    assert surface["closure"]["bounded_vread_implemented"] is True
    assert surface["closure"]["vector_mutation_capability_implemented"] is False
    assert surface["implementation_status"] == (
        "LEVEL_0_1_HASH216_IMMUTABLE_VECTOR_RESOLVER_IMPLEMENTED_"
        "TERMINAL_VERIFICATION_NOT_YET_CLAIMED"
    )
    assert surface["closure"]["level0_terminal_classification_emitted"] is False
    assert surface["closure"]["level1_terminal_classification_emitted"] is False


def _compile_and_run(
    tmp_path: Path,
    source: Path,
    implementation: Path,
    include_dir: Path,
    expected: str,
) -> None:
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


def test_complete_hash72_hash216_linked_abi_smoke(tmp_path: Path):
    _compile_and_run(
        tmp_path,
        ROOT / "native_projects/hhs_vm81_native_development/c/hhs_hash216_level0_smoke.c",
        ROOT / "hhs_runtime/src/hhs_hash216.c",
        ROOT / "hhs_runtime/include",
        "HASH72_HASH216_COMPLETE_LINKED_ABI_SMOKE_PASSED",
    )
