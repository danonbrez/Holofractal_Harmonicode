"""Pass 220 I054 ExactRat binary-congruence proof manifest.

I054 changes no runtime arithmetic implementation. It proves that the I049
unreduced exact addition and multiplication constructors respect the I053
cross-product equivalence relation.
"""
from __future__ import annotations

from dataclasses import dataclass

SCHEMA = "HHS_PASS_220_I054_NATIVE_MATHLIB_EXACTRAT_CONGRUENCE_V1"
LEAN_MODULE = "HHS.Mathlib.Rat.Congruence"


@dataclass(frozen=True)
class ExactRatCongruenceTheoremSpec:
    theorem: str
    operation: str
    universal: bool


THEOREMS: tuple[ExactRatCongruenceTheoremSpec, ...] = (
    ExactRatCongruenceTheoremSpec("eqv_add_congr", "add", True),
    ExactRatCongruenceTheoremSpec("eqv_mul_congr", "mul", True),
)


def exactrat_congruence_contract() -> dict:
    return {
        "schema": SCHEMA,
        "lean_module": LEAN_MODULE,
        "representation": "UNREDUCED_ORDERED_NUMERATOR_POSITIVE_DENOMINATOR_PAIR",
        "addition_formula": "(a.num*b.den+b.num*a.den)/(a.den*b.den)",
        "multiplication_formula": "(a.num*b.num)/(a.den*b.den)",
        "equivalence_relation_inherited": "I053_CROSS_PRODUCT_EQUIVALENCE",
        "neg_congruence_universal": True,
        "add_congruence_universal": True,
        "mul_congruence_universal": True,
        "quotient_constructed": False,
        "pair_identity_collapsed_into_equivalence": False,
        "local_int_commutation_dependency": "MUL_PAIR_SWAP_MIDDLE_ONLY",
        "generic_hhs_commutation_authorized": False,
        "runtime_arithmetic_changed": False,
        "runtime_arithmetic_authority": "INHERITED_PYTHON1_C11_EXACT_BIGINT",
        "vm81_mutation_authority": "VM81_ONLY",
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
        "theorem_count": len(THEOREMS),
    }


__all__ = [
    "LEAN_MODULE",
    "SCHEMA",
    "THEOREMS",
    "ExactRatCongruenceTheoremSpec",
    "exactrat_congruence_contract",
]
