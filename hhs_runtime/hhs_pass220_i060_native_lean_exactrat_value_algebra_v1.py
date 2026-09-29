"""Pass 220 I060 native Lean ExactRat value-algebra proof identity.

I060 is a proof/identity layer. It changes no Python1/C++ arithmetic and grants
no VM81, Hash72 commit, or Hash216 persistence authority.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any
import json

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72

VERSION = "HHS-P220-I060-NATIVE-LEAN-EXACTRAT-VALUE-ALGEBRA-V1"
SCHEMA = "HHS_PASS_220_I060_NATIVE_LEAN_EXACTRAT_VALUE_ALGEBRA_V1"
LEAN_MODULE = "HHS.Mathlib.Rat.ValueAlgebra"
BASE_MAIN = "08bc57b2f9eb075af14fb3bf700c637832f2b566"

LEAN_THEOREMS = (
    "pair_add_assoc_eqv",
    "pair_mul_assoc_eqv",
    "pair_left_distrib_eqv",
    "pair_right_distrib_eqv",
    "value_add_assoc",
    "value_mul_assoc",
    "value_left_distrib",
    "value_right_distrib",
    "ordered_algebra_closure_completed",
    "commutation_not_promoted",
    "provenance_not_rewritten",
    "runtime_arithmetic_unchanged",
    "proof_identity_receipt_forbids_vm81_mutation",
    "proof_identity_receipt_forbids_hash72_commit",
    "proof_identity_receipt_forbids_hash216_persistence",
)

LEAN_DEPENDENCIES = (
    "HHS.Mathlib.Rat.Equivalence",
    "HHS.Mathlib.Rat.Congruence",
    "HHS.Mathlib.Rat.Value",
    "HHS.Mathlib.Rat.ValueLaws",
    "Int.add_mul",
    "Int.mul_add",
    "Int.add_assoc",
    "Int.mul_assoc",
    "Int.add_comm",
    "Int.mul_comm",
    "Quotient.inductionOn₃",
    "Quotient.sound",
)

REPOSITORY_LINEAGE = (
    "PASS_220_I057_FROZEN_PARTICLE_SIMULATION",
    "PASS_220_I058_FROZEN_WHITE_PAPER_EQUATION_MECHANICS",
    "PASS_220_I059_FROZEN_NATIVE_3D_ENGINE_CELL_WALL",
    "PASS_220_I060_NATIVE_LEAN_EXACTRAT_VALUE_ALGEBRA",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _hash72(label: str, value: Any) -> str:
    return hash72_digest({"domain": VERSION, "label": label}, _canonical(value))


@lru_cache(maxsize=1)
def lean_identity_receipt() -> dict[str, Any]:
    theorem_hash72 = _hash72(
        "lean-theorem-identity",
        {"module": LEAN_MODULE, "theorems": LEAN_THEOREMS},
    )
    dependency_hash72 = _hash72(
        "lean-dependency-identity",
        {
            "module": LEAN_MODULE,
            "dependencies": LEAN_DEPENDENCIES,
            "repository_lineage": REPOSITORY_LINEAGE,
            "base_main": BASE_MAIN,
        },
    )
    return {
        "schema": SCHEMA,
        "module": LEAN_MODULE,
        "base_main": BASE_MAIN,
        "theorems": list(LEAN_THEOREMS),
        "dependencies": list(LEAN_DEPENDENCIES),
        "repository_lineage": list(REPOSITORY_LINEAGE),
        "theorem_identity_hash72": theorem_hash72,
        "dependency_identity_hash72": dependency_hash72,
        "theorem_identity_valid": validate_hash72(theorem_hash72),
        "dependency_identity_valid": validate_hash72(dependency_hash72),
        "kernel_validation_scope": "BUILD_LEANCHECKER_AXIOM_AUDIT",
        "runtime_claims_live_kernel_execution": False,
        "intrinsic_successor_binding_required": True,
        "intended_successor": "PASS_220_I061_UNIFIED_SCIENTIFIC_PHYSICS_SYNTHESIS",
        "post_hoc_proof_attachment_satisfies_successor": False,
        "runtime_arithmetic_changed": False,
        "generic_hhs_commutation_authorized": False,
        "vm81_mutation_authority": "VM81_ONLY",
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "BASE_MAIN",
    "LEAN_DEPENDENCIES",
    "LEAN_MODULE",
    "LEAN_THEOREMS",
    "REPOSITORY_LINEAGE",
    "SCHEMA",
    "VERSION",
    "lean_identity_receipt",
]
