"""Pass 220 I056 ExactRat quotient-value law manifest.

I056 promotes a bounded identity/inverse nucleus on the I055 quotient value
layer. It does not change native arithmetic or stored-pair provenance.
"""
from __future__ import annotations

SCHEMA = "HHS_PASS_220_I056_NATIVE_MATHLIB_EXACTRAT_VALUE_LAWS_V1"
LEAN_MODULE = "HHS.Mathlib.Rat.ValueLaws"


def exactrat_value_laws_contract() -> dict:
    return {
        "schema": SCHEMA,
        "lean_module": LEAN_MODULE,
        "carrier": "ExactRatValue",
        "closed_universal_laws": (
            "add_left_identity",
            "add_right_identity",
            "mul_left_identity",
            "mul_right_identity",
            "add_left_inverse",
            "add_right_inverse",
        ),
        "deferred_universal_laws": (
            "add_assoc",
            "mul_assoc",
            "left_distrib",
            "right_distrib",
        ),
        "zero_pair": "0/1",
        "one_pair": "1/1",
        "quotient_value_identity_only": True,
        "provenance_objects_rewritten": False,
        "pair_provenance_preserved_separately": True,
        "generic_hhs_commutation_authorized": False,
        "runtime_arithmetic_changed": False,
        "runtime_arithmetic_authority": "INHERITED_PYTHON1_C11_EXACT_BIGINT",
        "vm81_mutation_authority": "VM81_ONLY",
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "LEAN_MODULE",
    "SCHEMA",
    "exactrat_value_laws_contract",
]
