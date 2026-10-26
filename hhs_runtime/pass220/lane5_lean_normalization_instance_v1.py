"""Exact rational instantiation of existing Lean I060 normalization identities.

Candidate proof evidence only. The Lean kernel checks the generic theorem in CI;
this evaluator checks a concrete rational instance without claiming a new proof.
"""
from __future__ import annotations
from fractions import Fraction
from hhs_runtime.pass220.lane5_lean_normalization_lookup_v1 import (
    NORMALIZATION_DECLARATIONS, lookup_existing_normalization,
    LeanNormalizationLookupError,
)

class NormalizationInstantiationError(ValueError):
    pass

def _exact_fraction(value):
    if not isinstance(value, dict) or set(value) != {"numerator", "denominator"}:
        raise NormalizationInstantiationError("EXACT_RATIONAL_RECORD_REQUIRED")
    n, d = value["numerator"], value["denominator"]
    if type(n) is not int or type(d) is not int or d == 0:
        raise NormalizationInstantiationError("EXACT_RATIONAL_COMPONENT_REJECTED")
    return Fraction(n, d)

def _record(f):
    return {"numerator": f.numerator, "denominator": f.denominator}

def instantiate_existing_normalization(theorem: str, operands: list[dict]) -> dict:
    if theorem not in NORMALIZATION_DECLARATIONS:
        raise NormalizationInstantiationError("LEAN_NORMALIZATION_UNKNOWN_THEOREM")
    if type(operands) is not list or len(operands) != 3:
        raise NormalizationInstantiationError("LEAN_NORMALIZATION_THREE_OPERANDS_REQUIRED")
    a, b, c = (_exact_fraction(v) for v in operands)
    carrier, relation, operator = NORMALIZATION_DECLARATIONS[theorem]
    try:
        binding = lookup_existing_normalization(theorem, carrier=carrier,
                                                relation=relation, operator=operator)
    except LeanNormalizationLookupError as exc:
        raise NormalizationInstantiationError("LEAN_NORMALIZATION_IDENTITY_REJECTED") from exc
    if theorem.endswith("add_assoc") or theorem.endswith("add_assoc_eqv"):
        lhs, rhs = (a+b)+c, a+(b+c)
    elif theorem.endswith("mul_assoc") or theorem.endswith("mul_assoc_eqv"):
        lhs, rhs = (a*b)*c, a*(b*c)
    elif "left_distrib" in theorem:
        lhs, rhs = a*(b+c), a*b+a*c
    elif "right_distrib" in theorem:
        lhs, rhs = (a+b)*c, a*c+b*c
    else:
        raise NormalizationInstantiationError("LEAN_NORMALIZATION_RULE_UNSUPPORTED")
    if lhs != rhs:
        raise NormalizationInstantiationError("LEAN_NORMALIZATION_EXACT_CONSTRAINT_FAILED")
    return {
        "schema": "HHS_LANE5_EXACT_LEAN_NORMALIZATION_INSTANCE_V1",
        "theorem": binding,
        "operands": list(operands),
        "lhs_exact": _record(lhs),
        "rhs_exact": _record(rhs),
        "exact_rational_constraint_verified": True,
        "lean_theorem_application_kernel_checked_in_ci": True,
        "runtime_lean_kernel_invoked": False,
        "ordered_hnan_rewrite_authorized": False,
        "candidate_only": True,
        "canonical_vm81_admission": False,
    }
