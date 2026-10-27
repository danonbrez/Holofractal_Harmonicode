"""Read-only Lane 5 normalization for inherited I056 Lean identity/inverse laws."""
from __future__ import annotations
from fractions import Fraction

from hhs_runtime.hhs_pass220_i060_native_lean_exactrat_value_algebra_v1 import lean_identity_receipt

SCHEMA = "HHS_PASS220_LANE5_I056_VALUE_LAWS_NORMALIZATION_V1"
LEAN_MODULE = "HHS.Mathlib.Rat.ValueLaws"
APPLICATION_MODULE = "HHS.Pass220.Lane5ValueLawApplications"
# Explicitly preserve pair-level equivalence vs quotient-value equality.
DECLARATIONS = {
    "add_zero_pair_eqv": ("ExactRat", "eqv", "add_right_zero"),
    "zero_add_pair_eqv": ("ExactRat", "eqv", "add_left_zero"),
    "mul_one_pair_eqv": ("ExactRat", "eqv", "mul_right_one"),
    "one_mul_pair_eqv": ("ExactRat", "eqv", "mul_left_one"),
    "add_neg_pair_eqv_zero": ("ExactRat", "eqv", "add_right_inverse"),
    "neg_add_pair_eqv_zero": ("ExactRat", "eqv", "add_left_inverse"),
    "value_add_zero": ("ExactRatValue", "Eq", "add_right_zero"),
    "value_zero_add": ("ExactRatValue", "Eq", "add_left_zero"),
    "value_mul_one": ("ExactRatValue", "Eq", "mul_right_one"),
    "value_one_mul": ("ExactRatValue", "Eq", "mul_left_one"),
    "value_add_neg": ("ExactRatValue", "Eq", "add_right_inverse"),
    "value_neg_add": ("ExactRatValue", "Eq", "add_left_inverse"),
}

class ValueLawNormalizationError(ValueError):
    pass

def instantiate_existing_value_law(theorem: str, operand: dict) -> dict:
    if type(theorem) is not str or theorem not in DECLARATIONS:
        raise ValueLawNormalizationError("LEAN_VALUE_LAW_UNKNOWN_DECLARATION")
    if type(operand) is not dict or set(operand) != {"numerator", "denominator"}:
        raise ValueLawNormalizationError("LEAN_VALUE_LAW_EXACT_OPERAND_REQUIRED")
    n, d = operand["numerator"], operand["denominator"]
    if type(n) is not int or type(d) is not int or d <= 0:
        raise ValueLawNormalizationError("LEAN_VALUE_LAW_POSITIVE_DENOMINATOR_REQUIRED")
    base = lean_identity_receipt()
    if (not base["theorem_identity_valid"] or not base["dependency_identity_valid"]
        or base["generic_hhs_commutation_authorized"]
        or base["hash72_commit_authority"] or base["hash216_persistence_authority"]):
        raise ValueLawNormalizationError("LEAN_INHERITED_IDENTITY_REJECTED")
    carrier, relation, rule = DECLARATIONS[theorem]
    value = Fraction(n, d)
    if rule == "add_right_zero":
        lhs, rhs = value + 0, value
    elif rule == "add_left_zero":
        lhs, rhs = 0 + value, value
    elif rule == "mul_right_one":
        lhs, rhs = value * 1, value
    elif rule == "mul_left_one":
        lhs, rhs = 1 * value, value
    elif rule == "add_right_inverse":
        lhs, rhs = value + -value, Fraction(0)
    else:
        lhs, rhs = -value + value, Fraction(0)
    if lhs != rhs:
        raise ValueLawNormalizationError("LEAN_VALUE_LAW_CONSTRAINT_FAILED")
    return {
        "schema": SCHEMA,
        "lean_module": LEAN_MODULE,
        "declaration": theorem,
        "application_module": APPLICATION_MODULE,
        "application_declaration": theorem + "_application",
        "carrier": carrier,
        "relation": relation,
        "rule": rule,
        "operand": dict(operand),
        "lhs_exact": {"numerator": lhs.numerator, "denominator": lhs.denominator},
        "rhs_exact": {"numerator": rhs.numerator, "denominator": rhs.denominator},
        "inherited_i060_theorem_identity_hash72": base["theorem_identity_hash72"],
        "inherited_i060_dependency_identity_hash72": base["dependency_identity_hash72"],
        "i056_kernel_application_checked_at_runtime": False,
        "candidate_only": True,
        "ordered_hnan_rewrite_authorized": False,
        "canonical_vm81_admission": False,
    }
