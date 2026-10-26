"""Lane 5 read-only normalization lookup over existing I060 Lean declarations.

Uses the authoritative theorem/dependency identities and exact native Lean
declaration names. Lookup is NOT proof replay or HNAN operator rewrite.
"""
from __future__ import annotations

from hhs_runtime.hhs_pass220_i060_native_lean_exactrat_value_algebra_v1 import (
    LEAN_MODULE, LEAN_THEOREMS, lean_identity_receipt,
)

SCHEMA = "HHS_PASS220_LANE5_LEAN_NORMALIZATION_LOOKUP_V1"
# Signature is the native Lean expression head, not an opaque substitution ID.
NORMALIZATION_DECLARATIONS = {
    "pair_add_assoc_eqv": ("ExactRat", "eqv", "addExactRat"),
    "pair_mul_assoc_eqv": ("ExactRat", "eqv", "mulExactRat"),
    "pair_left_distrib_eqv": ("ExactRat", "eqv", "mulExactRat/addExactRat"),
    "pair_right_distrib_eqv": ("ExactRat", "eqv", "mulExactRat/addExactRat"),
    "value_add_assoc": ("ExactRatValue", "Eq", "ExactRatValue.add"),
    "value_mul_assoc": ("ExactRatValue", "Eq", "ExactRatValue.mul"),
    "value_left_distrib": ("ExactRatValue", "Eq", "ExactRatValue.mul/ExactRatValue.add"),
    "value_right_distrib": ("ExactRatValue", "Eq", "ExactRatValue.mul/ExactRatValue.add"),
}


LEAN_APPLICATION_MODULE = "HHS.Pass220.Lane5NormalizationApplications"
LEAN_APPLICATION_SOURCE = "formal/lean/HHS/Pass220/Lane5NormalizationApplications.lean"
APPLICATION_DECLARATIONS = {
    theorem: f"{theorem}_application" for theorem in NORMALIZATION_DECLARATIONS
}


class LeanNormalizationLookupError(ValueError):
    pass


def lookup_existing_normalization(theorem: str, *, carrier: str,
                                  relation: str, operator: str) -> dict:
    """Return source-bound candidate metadata, never mint proof authority."""
    if type(theorem) is not str or theorem not in NORMALIZATION_DECLARATIONS:
        raise LeanNormalizationLookupError("LEAN_NORMALIZATION_NOT_REGISTERED")
    expected = NORMALIZATION_DECLARATIONS[theorem]
    if (carrier, relation, operator) != expected:
        raise LeanNormalizationLookupError("LEAN_NORMALIZATION_TYPE_MISMATCH")
    if theorem not in LEAN_THEOREMS:
        raise LeanNormalizationLookupError("LEAN_THEOREM_IDENTITY_MISSING")
    receipt = lean_identity_receipt()
    if (receipt["module"] != LEAN_MODULE
        or theorem not in receipt["theorems"]
        or not receipt["theorem_identity_valid"]
        or not receipt["dependency_identity_valid"]
        or receipt["generic_hhs_commutation_authorized"]
        or receipt["hash72_commit_authority"]
        or receipt["hash216_persistence_authority"]):
        raise LeanNormalizationLookupError("LEAN_NORMALIZATION_RECEIPT_REJECTED")
    return {
        "schema": SCHEMA,
        "module": LEAN_MODULE,
        "declaration": theorem,
        "application_module": LEAN_APPLICATION_MODULE,
        "application_declaration": APPLICATION_DECLARATIONS[theorem],
        "application_source": LEAN_APPLICATION_SOURCE,
        "carrier": carrier,
        "relation": relation,
        "operator": operator,
        "theorem_identity_hash72": receipt["theorem_identity_hash72"],
        "dependency_identity_hash72": receipt["dependency_identity_hash72"],
        "proof_scope": "I060_LEAN_EXACT_RATIONAL",
        "source_theorem_hypotheses_required": True,
        "ordered_hnan_rewrite_authorized": False,
        "kernel_validation_reused_not_executed": True,
        "candidate_only": True,
        "canonical_vm81_admission": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
