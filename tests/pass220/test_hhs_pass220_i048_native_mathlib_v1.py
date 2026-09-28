from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest

from hhs_runtime.hhs_pass220_i048_native_mathlib_v1 import (
    FOUNDATION_CLASSES,
    NativeMathlibFoundation,
    native_mathlib_contract,
)

ROOT = Path(__file__).resolve().parents[2]
PYTHON1_NATIVE = ROOT / "native_projects" / "hhs_pass220_python_native_execution"
MATHLIB_NATIVE = ROOT / "native_projects" / "hhs_pass220_mathlib_native"
EXACT_C = ROOT / "hhs_runtime" / "c" / "hhs_runtime_exact_abi.c"
RUNTIME_INCLUDE = ROOT / "hhs_runtime" / "include"


@pytest.fixture()
def native_libraries(tmp_path: Path) -> tuple[Path, Path]:
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("C compiler unavailable")

    python1 = tmp_path / "libhhs_python1.so"
    exact = tmp_path / "libhhs_exact.so"

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
            f"-I{PYTHON1_NATIVE / 'include'}",
            str(PYTHON1_NATIVE / "src" / "hhs_pass220_python_native_execution_v1.c"),
            "-o",
            str(python1),
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
            f"-I{RUNTIME_INCLUDE}",
            str(EXACT_C),
            "-o",
            str(exact),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return python1, exact


def test_i048_contract_keeps_mathlib_compatibility_without_upstream_runtime_authority() -> None:
    contract = native_mathlib_contract()
    assert contract["coverage"] == "FOUNDATION_SLICE"
    assert contract["complete_mathlib_rebuild_claimed"] is False
    assert contract["integer_execution_authority"] == (
        "HHS_PASS_220_PYTHON1_C11_BIGINT"
    )
    assert contract["class_identity_authority"] == (
        "HHS_PASS_220_PYTHON2_CPP_RNA_CELL_WALL"
    )
    assert contract["formal_proof_checker"] == "LEAN4_KERNEL"
    assert contract["vm81_mutation_authority"] == "VM81_ONLY"
    assert contract["upstream_mathlib_runtime_dependency"] is False
    assert contract["host_python_evaluator_authority"] is False


def test_i048_foundation_covers_nat_int_and_eq() -> None:
    assert tuple(spec.class_name for spec in FOUNDATION_CLASSES) == (
        "Nat",
        "Int",
        "Eq",
    )
    assert tuple(spec.upstream_namespace for spec in FOUNDATION_CLASSES) == (
        "Mathlib.Data.Nat.Basic",
        "Mathlib.Data.Int.Basic",
        "Mathlib.Logic.Basic",
    )


def test_i048_python1_executes_native_integer_probe_and_rna_registers_classes(
    native_libraries: tuple[Path, Path],
) -> None:
    python1, exact = native_libraries
    native = NativeMathlibFoundation(
        python1_library=python1,
        exact_abi_library=exact,
    )

    result = native.execute_integer_program(
        "a=999999999999999999999999999999\n"
        "b=888888888888888888888888888888\n"
        "result=a*b"
    )
    assert result.result_decimal == (
        "888888888888888888888888888887"
        "111111111111111111111111111112"
    )
    assert result.host_python_evaluator_used is False

    registrations = native.register_foundation()
    assert len(registrations) == 3
    assert all(reg.rna_cell_wall_bound for reg in registrations)
    assert all(reg.registration_only for reg in registrations)
    assert all(not reg.vm81_mutation_authority for reg in registrations)
    assert all(not reg.hash72_commit_authority for reg in registrations)
    assert all(not reg.hash216_persistence_authority for reg in registrations)
    assert len({reg.class_identity_hash216 for reg in registrations}) == 3


def test_i048_cpp_native_mathlib_harness() -> None:
    if not (shutil.which("cc") or shutil.which("gcc")):
        pytest.skip("C compiler unavailable")
    if not (shutil.which("c++") or shutil.which("g++")):
        pytest.skip("C++ compiler unavailable")

    completed = subprocess.run(
        ["make", "-C", str(MATHLIB_NATIVE), "clean", "test"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "hhs_pass220_mathlib_native_v1_test" in completed.stdout


def test_i048_lean_native_module_has_no_mathlib_dependency_or_placeholders() -> None:
    source = (
        ROOT / "formal" / "lean" / "HHS" / "Mathlib" / "Native.lean"
    ).read_text(encoding="utf-8")
    lowered = source.lower()
    assert "import mathlib" not in lowered
    assert "sorry" not in lowered
    assert "admit" not in lowered
    assert "foundationclasses" in lowered
    assert "completeMathlibCoverage : Bool := false" in source
