"""Pass 220 I055 quotient-compatible ExactRat value manifest.

The quotient is a Lean proof/value layer only. Native arithmetic remains the
I049 Python1/C++ unreduced-pair implementation.
"""
from __future__ import annotations

SCHEMA = "HHS_PASS_220_I055_NATIVE_MATHLIB_EXACTRAT_VALUE_V1"
LEAN_MODULE = "HHS.Mathlib.Rat.Value"


def exactrat_value_contract() -> dict:
    return {
        "schema": SCHEMA,
        "lean_module": LEAN_MODULE,
        "setoid_relation": "I053_CROSS_PRODUCT_EQUIVALENCE",
        "quotient_type": "ExactRatValue",
        "quotient_constructed": True,
        "operations_lifted": ("neg", "add", "mul"),
        "operation_congruence": {
            "neg": "I053",
            "add": "I054",
            "mul": "I054",
        },
        "pair_identity_is_value_identity": False,
        "representative_recoverable_from_quotient": False,
        "provenance_wrapper": "ExactRatProvenance",
        "unreduced_pair_provenance_preserved_separately": True,
        "runtime_arithmetic_changed": False,
        "runtime_arithmetic_authority": "INHERITED_PYTHON1_C11_EXACT_BIGINT",
        "generic_hhs_commutation_authorized": False,
        "vm81_mutation_authority": "VM81_ONLY",
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "LEAN_MODULE",
    "SCHEMA",
    "exactrat_value_contract",
]
