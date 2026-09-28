from __future__ import annotations

from pathlib import Path
import os
import re
import shutil
import subprocess

import pytest

from hhs_runtime.hhs_pass220_i050_native_mathlib_algebra_v1 import (
    ALGEBRA_CLASSES,
    native_algebra_contract,
)
from hhs_runtime.hhs_pass220_python_rna_class_registration_v1 import (
    PythonRNAClassRegistry,
)

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "native_projects" / "hhs_pass220_mathlib_algebra"
EXACT_C = ROOT / "hhs_runtime" / "c" / "hhs_runtime_exact_abi.c"
RUNTIME_INCLUDE = ROOT / "hhs_runtime" / "include"


@pytest.fixture()
def exact_library(tmp_path: Path) -> Path:
    cc = shutil.which("cc") or shutil.which("gcc")
    cxx = shutil.which("c++") or shutil.which("g++")
    if not cc or not cxx:
        pytest.skip("C/C++ compiler unavailable")

    exact_obj = tmp_path / "exact_abi.o"
    support = tmp_path / "support"
    library = tmp_path / "libhhs_exact.so"

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
            f"-I{RUNTIME_INCLUDE}",
            "-c",
            str(EXACT_C),
            "-o",
            str(exact_obj),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    subprocess.run(
        [
            "bash",
            "tools/pass219/build_exact_abi_link_support.sh",
            str(support),
            "full",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
        env={**os.environ, "CC": cc, "CXX": cxx},
    )
    subprocess.run(
        [
            cxx,
            "-shared",
            str(exact_obj),
            str(support / "hhs_hash216.o"),
            str(support / "hhs_pass219_vm81_pqc_cell_wall.o"),
            "-lcrypto",
            "-pthread",
            "-lm",
            "-o",
            str(library),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return library


def test_i050_contract_preserves_exact_authority_and_ordering() -> None:
    contract = native_algebra_contract()
    assert contract["coverage"] == "ALGEBRAIC_STRUCTURE_CERTIFICATE_NUCLEUS"
    assert contract["carriers"] == ("Nat", "Int", "ExactRat")
    assert contract["universal_theorem_closure_claimed"] is False
    assert contract["arithmetic_authority"] == (
        "PYTHON1_C11_5184_DIGIT_EXACT_BIGINT"
    )
    assert contract["operand_order_preserved"] is True
    assert contract["implicit_commutation_authorized"] is False
    assert contract["host_float_authority"] is False
    assert contract["host_primitive_arithmetic_authority"] is False
    assert contract["vm81_mutation_authority"] == "VM81_ONLY"


def test_i050_class_surface_covers_algebraic_structure_nucleus() -> None:
    assert tuple(spec.class_name for spec in ALGEBRA_CLASSES) == (
        "AddMonoid",
        "MulMonoid",
        "Semiring",
        "Ring",
    )


def test_i050_cpp_exact_algebra_law_harness() -> None:
    if not (shutil.which("cc") or shutil.which("gcc")):
        pytest.skip("C compiler unavailable")
    if not (shutil.which("c++") or shutil.which("g++")):
        pytest.skip("C++ compiler unavailable")

    completed = subprocess.run(
        ["make", "-C", str(PROJECT), "clean", "test"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "hhs_pass220_mathlib_algebra_v1_test" in completed.stdout


def test_i050_rna_registration_is_distinct_and_non_authoritative(
    exact_library: Path,
) -> None:
    registry = PythonRNAClassRegistry(exact_library)
    registrations = tuple(
        registry.register(
            module_name=spec.native_module,
            class_name=spec.class_name,
            source_text=spec.source_text,
            members=spec.members,
        )
        for spec in ALGEBRA_CLASSES
    )
    assert len(registrations) == 4
    assert len({item.class_identity_hash216 for item in registrations}) == 4
    assert all(item.rna_cell_wall_bound for item in registrations)
    assert all(item.registration_only for item in registrations)
    assert all(not item.vm81_mutation_authority for item in registrations)
    assert all(not item.hash72_commit_authority for item in registrations)
    assert all(not item.hash216_persistence_authority for item in registrations)


def test_i050_lean_module_has_no_mathlib_dependency_or_placeholders() -> None:
    source = (
        ROOT / "formal" / "lean" / "HHS" / "Mathlib" / "Algebra" / "Native.lean"
    ).read_text(encoding="utf-8")
    lowered = source.lower()
    assert re.search(r"\bimport\s+mathlib\b", lowered) is None
    assert re.search(r"\bsorry\b", source, flags=re.IGNORECASE) is None
    assert re.search(r"\badmit\b", source, flags=re.IGNORECASE) is None
    assert "structure lawreceipt" in lowered
    assert "implicitcommutationauthorized" in lowered
