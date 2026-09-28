"""Pass 220 I048 native Lean4/Mathlib1 compatibility nucleus.

Mathlib compatibility is rebuilt over existing HHS execution surfaces:
- Python1/C11 owns exact bounded integer execution.
- Python2/C++ RNA class registration owns deterministic class/type identity.
- Lean 4 checks formal proof terms.
- VM81 remains the only mutation/admission authority.

Upstream Mathlib is a differential/API reference only for this checkpoint.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from hhs_runtime.hhs_pass220_python_native_execution_v1 import (
    HHSPythonNativeExecutor,
    HHSPythonNativeResult,
)
from hhs_runtime.hhs_pass220_python_rna_class_registration_v1 import (
    MEMBER_CONSTRUCTOR,
    MEMBER_METHOD,
    ROLE_HAIRPIN,
    ROLE_TOEHOLD,
    PythonClassMemberSpec,
    PythonRNAClassRegistration,
    PythonRNAClassRegistry,
)

SCHEMA = "HHS_PASS_220_I048_LEAN4_NATIVE_MATHLIB_REBUILD_V1"
LEAN_NAMESPACE = "HHS.Mathlib.Native"


@dataclass(frozen=True)
class MathlibNativeClassSpec:
    upstream_namespace: str
    native_module: str
    class_name: str
    source_text: str
    members: tuple[PythonClassMemberSpec, ...]


FOUNDATION_CLASSES: tuple[MathlibNativeClassSpec, ...] = (
    MathlibNativeClassSpec(
        upstream_namespace="Mathlib.Data.Nat.Basic",
        native_module="HHS.Mathlib.Data.Nat.Basic",
        class_name="Nat",
        source_text=(
            "class Nat:\n"
            "    def __init__(self, value): self.value = value\n"
            "    def add(self, rhs): return self.value + rhs.value\n"
            "    def mul(self, rhs): return self.value * rhs.value\n"
        ),
        members=(
            PythonClassMemberSpec("__init__", MEMBER_CONSTRUCTOR, 0, 0, ROLE_TOEHOLD),
            PythonClassMemberSpec("add", MEMBER_METHOD, 1, 0, 0),
            PythonClassMemberSpec("mul", MEMBER_METHOD, 2, 1, ROLE_HAIRPIN),
        ),
    ),
    MathlibNativeClassSpec(
        upstream_namespace="Mathlib.Data.Int.Basic",
        native_module="HHS.Mathlib.Data.Int.Basic",
        class_name="Int",
        source_text=(
            "class Int:\n"
            "    def __init__(self, value): self.value = value\n"
            "    def add(self, rhs): return self.value + rhs.value\n"
            "    def sub(self, rhs): return self.value - rhs.value\n"
            "    def mul(self, rhs): return self.value * rhs.value\n"
        ),
        members=(
            PythonClassMemberSpec("__init__", MEMBER_CONSTRUCTOR, 0, 0, ROLE_TOEHOLD),
            PythonClassMemberSpec("add", MEMBER_METHOD, 1, 0, 0),
            PythonClassMemberSpec("sub", MEMBER_METHOD, 2, 1, 0),
            PythonClassMemberSpec("mul", MEMBER_METHOD, 3, 0, ROLE_HAIRPIN),
        ),
    ),
    MathlibNativeClassSpec(
        upstream_namespace="Mathlib.Logic.Basic",
        native_module="HHS.Mathlib.Logic.Basic",
        class_name="Eq",
        source_text=(
            "class Eq:\n"
            "    def __init__(self, lhs): self.lhs = lhs\n"
            "    def refl(self): return self\n"
        ),
        members=(
            PythonClassMemberSpec("__init__", MEMBER_CONSTRUCTOR, 0, 0, ROLE_TOEHOLD),
            PythonClassMemberSpec("refl", MEMBER_METHOD, 4, 1, ROLE_HAIRPIN),
        ),
    ),
)


class NativeMathlibFoundation:
    def __init__(
        self,
        *,
        python1_library: str | Path,
        exact_abi_library: str | Path,
    ) -> None:
        self.python1 = HHSPythonNativeExecutor(python1_library)
        self.classes = PythonRNAClassRegistry(exact_abi_library)

    def execute_integer_program(self, source: str) -> HHSPythonNativeResult:
        """Execute admitted native integer source using Python1, never CPython eval."""
        return self.python1.execute(source)

    def register_class(
        self,
        spec: MathlibNativeClassSpec,
    ) -> PythonRNAClassRegistration:
        return self.classes.register(
            module_name=spec.native_module,
            class_name=spec.class_name,
            source_text=spec.source_text,
            members=spec.members,
        )

    def register_foundation(
        self,
    ) -> tuple[PythonRNAClassRegistration, ...]:
        return tuple(self.register_class(spec) for spec in FOUNDATION_CLASSES)


def iter_foundation_classes() -> Iterable[MathlibNativeClassSpec]:
    return FOUNDATION_CLASSES


def native_mathlib_contract() -> dict:
    return {
        "schema": SCHEMA,
        "lean_namespace": LEAN_NAMESPACE,
        "coverage": "FOUNDATION_SLICE",
        "complete_mathlib_rebuild_claimed": False,
        "foundation_upstream_namespaces": tuple(
            spec.upstream_namespace for spec in FOUNDATION_CLASSES
        ),
        "integer_execution_authority": "HHS_PASS_220_PYTHON1_C11_BIGINT",
        "class_identity_authority": "HHS_PASS_220_PYTHON2_CPP_RNA_CELL_WALL",
        "formal_proof_checker": "LEAN4_KERNEL",
        "vm81_mutation_authority": "VM81_ONLY",
        "upstream_mathlib_role": "DIFFERENTIAL_AND_API_REFERENCE_ONLY",
        "upstream_mathlib_runtime_dependency": False,
        "host_python_evaluator_authority": False,
        "floating_point_canonical_authority": False,
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
        "expansion_rule": (
            "ADD_NATIVE_SLICE_ONLY_AFTER_INTERFACE_EQUIVALENCE_AND_PROOF_VALIDATION"
        ),
    }


__all__ = [
    "FOUNDATION_CLASSES",
    "LEAN_NAMESPACE",
    "MathlibNativeClassSpec",
    "NativeMathlibFoundation",
    "SCHEMA",
    "iter_foundation_classes",
    "native_mathlib_contract",
]
