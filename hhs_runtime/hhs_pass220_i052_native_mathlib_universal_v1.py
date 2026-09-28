"""Pass 220 I052 universal Lean theorem-promotion manifest.

This module describes proof promotion only. Runtime arithmetic remains owned by
Python1/C11 and the native C++ compatibility classes inherited from I048-I050.
"""
from __future__ import annotations

from dataclasses import dataclass

SCHEMA = "HHS_PASS_220_I052_NATIVE_MATHLIB_UNIVERSAL_V1"
LEAN_MODULE = "HHS.Mathlib.Algebra.Universal"


@dataclass(frozen=True)
class UniversalTheoremSpec:
    carrier: str
    theorem: str
    law: str
    ordered_expression: str


THEOREMS: tuple[UniversalTheoremSpec, ...] = (
    UniversalTheoremSpec("Nat", "nat_add_assoc", "add_assoc", "(a+b)+c=a+(b+c)"),
    UniversalTheoremSpec("Nat", "nat_add_left_identity", "add_left_identity", "0+a=a"),
    UniversalTheoremSpec("Nat", "nat_add_right_identity", "add_right_identity", "a+0=a"),
    UniversalTheoremSpec("Nat", "nat_mul_assoc", "mul_assoc", "(a*b)*c=a*(b*c)"),
    UniversalTheoremSpec("Nat", "nat_mul_left_identity", "mul_left_identity", "1*a=a"),
    UniversalTheoremSpec("Nat", "nat_mul_right_identity", "mul_right_identity", "a*1=a"),
    UniversalTheoremSpec("Nat", "nat_left_distrib", "left_distrib", "a*(b+c)=a*b+a*c"),
    UniversalTheoremSpec("Nat", "nat_right_distrib", "right_distrib", "(a+b)*c=a*c+b*c"),
    UniversalTheoremSpec("Int", "int_add_assoc", "add_assoc", "(a+b)+c=a+(b+c)"),
    UniversalTheoremSpec("Int", "int_add_left_identity", "add_left_identity", "0+a=a"),
    UniversalTheoremSpec("Int", "int_add_right_identity", "add_right_identity", "a+0=a"),
    UniversalTheoremSpec("Int", "int_add_left_inverse", "add_left_inverse", "-a+a=0"),
    UniversalTheoremSpec("Int", "int_add_right_inverse", "add_right_inverse", "a+-a=0"),
    UniversalTheoremSpec("Int", "int_mul_assoc", "mul_assoc", "(a*b)*c=a*(b*c)"),
    UniversalTheoremSpec("Int", "int_mul_left_identity", "mul_left_identity", "1*a=a"),
    UniversalTheoremSpec("Int", "int_mul_right_identity", "mul_right_identity", "a*1=a"),
    UniversalTheoremSpec("Int", "int_left_distrib", "left_distrib", "a*(b+c)=a*b+a*c"),
    UniversalTheoremSpec("Int", "int_right_distrib", "right_distrib", "(a+b)*c=a*c+b*c"),
)


def universal_promotion_contract() -> dict:
    return {
        "schema": SCHEMA,
        "lean_module": LEAN_MODULE,
        "coverage": "NAT_SEMIRING_AND_INT_RING_UNIVERSAL_LAWS",
        "nat_semiring_universal": True,
        "int_ring_universal": True,
        "exact_rat_ring_universal": False,
        "runtime_arithmetic_changed": False,
        "runtime_arithmetic_authority": "INHERITED_PYTHON1_C11_EXACT_BIGINT",
        "native_cpp_carriers": "INHERITED_I048_I049_I050",
        "ordered_operands_required": True,
        "generic_commutation_authorized": False,
        "commutativity_theorems_exported": False,
        "upstream_mathlib_runtime_dependency": False,
        "lean_role": "UNIVERSAL_PROOF_WITNESS",
        "vm81_mutation_authority": "VM81_ONLY",
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
        "theorem_count": len(THEOREMS),
    }


__all__ = [
    "LEAN_MODULE",
    "SCHEMA",
    "THEOREMS",
    "UniversalTheoremSpec",
    "universal_promotion_contract",
]
