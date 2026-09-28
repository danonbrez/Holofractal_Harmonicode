"""Pass 220 I053 ExactRat universal equivalence proof manifest.

No runtime arithmetic implementation changes in I053. The module records the
Lean proof surface that closes cross-product equivalence over the existing
I049 unreduced positive-denominator representation.
"""
from __future__ import annotations

from dataclasses import dataclass

SCHEMA = "HHS_PASS_220_I053_NATIVE_MATHLIB_EXACTRAT_EQUIVALENCE_V1"
LEAN_MODULE = "HHS.Mathlib.Rat.Equivalence"


@dataclass(frozen=True)
class ExactRatTheoremSpec:
    theorem: str
    property: str
    universal: bool


THEOREMS: tuple[ExactRatTheoremSpec, ...] = (
    ExactRatTheoremSpec("denominator_cast_ne_zero", "positive_denominator_nonzero", True),
    ExactRatTheoremSpec("eqv_refl", "equivalence_reflexive", True),
    ExactRatTheoremSpec("eqv_symm", "equivalence_symmetric", True),
    ExactRatTheoremSpec("eqv_trans", "equivalence_transitive", True),
    ExactRatTheoremSpec("eqv_neg_congr", "negation_congruence", True),
)


def exactrat_equivalence_contract() -> dict:
    return {
        "schema": SCHEMA,
        "lean_module": LEAN_MODULE,
        "representation": "UNREDUCED_ORDERED_NUMERATOR_POSITIVE_DENOMINATOR_PAIR",
        "equivalence": "a.num*b.den == b.num*a.den",
        "equivalence_relation_universal": True,
        "neg_congruence_universal": True,
        "add_congruence_universal": False,
        "mul_congruence_universal": False,
        "quotient_constructed": False,
        "pair_identity_collapsed_into_equivalence": False,
        "local_int_commutation_dependency": "THREE_FACTOR_SWAP_RIGHT_ONLY",
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
    "ExactRatTheoremSpec",
    "exactrat_equivalence_contract",
]
