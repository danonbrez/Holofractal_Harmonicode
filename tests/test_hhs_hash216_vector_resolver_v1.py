from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest

from native_projects.hhs_vm81_native_development.hhs_hash216_vector_resolver_manifest_v1 import (
    build_manifest,
)
from native_projects.hhs_vm81_native_development.hhs_vm81_native_development_v1 import (
    build_architecture_surface,
)

ROOT = Path(__file__).resolve().parents[1]
C_ROOT = ROOT / "native_projects/hhs_vm81_native_development/c"


def test_resolver_manifest_is_deterministic_and_source_backed():
    first = build_manifest(ROOT)
    second = build_manifest(ROOT)
    assert first == second
    assert all(record["present"] for record in first["sources"])
    assert all(record["size"] > 0 for record in first["sources"])
    assert all(len(record["sha256"]) == 64 for record in first["sources"])
    assert len(first["resolver_manifest_root_hash72"]) == 72


def test_resolver_contract_freezes_exact_bounds_and_authority_partition():
    manifest = build_manifest(ROOT)
    assert manifest["limits"] == {
        "position_min": 0,
        "position_max": 215,
        "vm81_lane_min": 0,
        "vm81_lane_max": 80,
        "phase_min": 0,
        "phase_max": 71,
        "maximum_objects_per_snapshot": 8,
        "maximum_bytes_per_object": 4096,
        "minimum_version": 1,
        "minimum_generation": 1,
    }
    assert manifest["canonical_serialization"]["native_struct_bytes_used"] is False
    assert manifest["canonical_serialization"]["integer_encoding"] == (
        "FIXED_WIDTH_BIG_ENDIAN"
    )
    assert manifest["canonical_serialization"]["physical_pointer_included"] is False
    assert manifest["authority"]["vm81_execution_authority_transferred"] is False
    assert manifest["authority"]["host_physical_address_authority"] is False
    assert manifest["authority"]["runtime_mutation_surface_exposed"] is False
    assert manifest["authority"]["single_use_mutation_capability_implemented"] is False


def test_resolver_closure_is_integrated_without_mutation_promotion():
    manifest = build_manifest(ROOT)
    architecture = build_architecture_surface(ROOT)
    assert manifest["closure"]["canonical_hash216_address_implemented"] is True
    assert manifest["closure"]["bounded_immutable_vector_descriptor_implemented"] is True
    assert manifest["closure"]["immutable_resolver_snapshot_implemented"] is True
    assert manifest["closure"]["bounded_vresolve_implemented"] is True
    assert manifest["closure"]["bounded_vread_implemented"] is True
    assert manifest["closure"]["vector_mutation_implemented"] is False
    assert architecture["hash216_vector_resolver"]["manifest_root_hash72"] == (
        manifest["resolver_manifest_root_hash72"]
    )
    assert architecture["closure"]["hash216_logical_address_resolver_implemented"] is True
    assert architecture["closure"]["vector_mutation_capability_implemented"] is False


def test_no_write_append_resize_or_release_api_is_exposed():
    header = (C_ROOT / "hhs_hash216_vector_resolver_v1.h").read_text(
        encoding="utf-8"
    )
    for forbidden in (
        "hhs_hash216_vector_write",
        "hhs_hash216_vector_append",
        "hhs_hash216_vector_resize",
        "hhs_hash216_vector_release",
        "VWRITE_REQUEST",
        "VAPPEND",
        "VRESIZE",
        "VRELEASE",
    ):
        assert forbidden not in header
    assert "HHS_HASH216_VECTOR_STATUS_MUTATION_NOT_SUPPORTED" in header


def test_native_hash216_immutable_vector_resolver_smoke(tmp_path: Path):
    compiler = shutil.which("cc") or shutil.which("gcc")
    if compiler is None:
        pytest.skip("C compiler unavailable")
    binary = tmp_path / "hhs_hash216_vector_resolver_smoke"
    command = [
        compiler,
        "-std=c11",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Werror",
        f"-I{C_ROOT}",
        f"-I{ROOT / 'hhs_runtime/include'}",
        str(C_ROOT / "hhs_hash216_vector_resolver_smoke.c"),
        str(C_ROOT / "hhs_hash216_vector_resolver_v1.c"),
        str(ROOT / "hhs_runtime/src/hhs_hash216.c"),
        "-o",
        str(binary),
    ]
    compiled = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert compiled.returncode == 0, compiled.stdout + compiled.stderr
    executed = subprocess.run([str(binary)], cwd=ROOT, text=True, capture_output=True)
    assert executed.returncode == 0, executed.stdout + executed.stderr
    assert "HASH216_IMMUTABLE_VECTOR_RESOLVER_SMOKE_PASSED" in executed.stdout
