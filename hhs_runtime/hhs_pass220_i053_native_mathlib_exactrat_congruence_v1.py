"""Pass 220 I053 ExactRat operation-congruence proof manifest."""
from __future__ import annotations

from dataclasses import dataclass

SCHEMA = "HHS_PASS_220_I053_NATIVE_MATHLIB_EXACTRAT_CONGRUENCE_V1"
LEAN_MODULE = "HHS.Mathlib.Algebra.ExactRatCongruence"


@dataclass(frozen=True)
class CongruenceTheoremSpec:
    operation: str
    theorem: str
    native_formula: str


CONGRUENCE_THEOREMS: tuple[CongruenceTheoremSpec, ...] = (
    CongruenceTheoremSpec(
        "add",
        "ratAdd_congr",
        "(a/b)+(c/d)=(a*d+c*b)/(b*d)",
    ),
    CongruenceTheoremSpec(
        "neg",
        "ratNeg_congr",
        "-(a/b)=(-a)/b",
    ),
    CongruenceTheoremSpec(
        "sub",
        "ratSub_congr",
        "(a/b)-(c/d)=(a*d-c*b)/(b*d)",
    ),
    CongruenceTheoremSpec(
        "mul",
        "ratMul_congr",
        "(a/b)*(c/d)=(a*c)/(b*d)",
    ),
)


def exactrat_congruence_contract() -> dict:
    return {
        "schema": SCHEMA,
        "lean_module": LEAN_MODULE,
        "coverage": "EXACTRAT_OPERATION_CONGRUENCE",
        "equivalence": "a.num*b.den == b.num*a.den",
        "operations": tuple(item.operation for item in CONGRUENCE_THEOREMS),
        "universal_operation_congruence": True,
        "quotient_ring_closed": False,
        "equivalence_transitivity_closed": False,
        "native_runtime_formulas_changed": False,
        "native_cpp_source": "I049_NATIVERAT",
        "carrier_local_int_commutation_used_in_proof": True,
        "generic_hhs_commutation_authorized": False,
        "upstream_mathlib_runtime_dependency": False,
        "lean_role": "UNIVERSAL_CONGRUENCE_PROOF_WITNESS",
        "vm81_mutation_authority": "VM81_ONLY",
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "CONGRUENCE_THEOREMS",
    "LEAN_MODULE",
    "SCHEMA",
    "CongruenceTheoremSpec",
    "exactrat_congruence_contract",
]
