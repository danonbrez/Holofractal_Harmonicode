"""Registration for Pass 219 I147 bounded self-reference closure."""

from __future__ import annotations

from typing import Any, Dict

VERSION = "PASS_219_I147_DYNAMIC_PARADOX_PHASE_CYCLE_1_0"
SCHEMA = "HHS_PASS219_DYNAMIC_PARADOX_PHASE_CYCLE_V1"
SURFACE_ID = "guard:pass219.dynamic_paradox_phase_cycle"
ANALYZE_SYMBOL = "hhs_exact_pass219_paradox_analyze"
VALIDATE_SYMBOL = "hhs_exact_pass219_paradox_witness_validate"
H36_SYMBOL = "hhs_exact_pass219_h36_closure_identity"
H36_VALIDATE_SYMBOL = "hhs_exact_pass219_h36_closure_identity_validate"


def surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": SURFACE_ID,
        "surface_type": "GUARD",
        "module": "hhs_runtime_exact_abi",
        "symbol": ANALYZE_SYMBOL,
        "contract_schemas": [
            SCHEMA,
            "HHS_PASS219_H36_CLOSURE_IDENTITY_V1",
        ],
        "validators": [
            ANALYZE_SYMBOL,
            VALIDATE_SYMBOL,
            H36_SYMBOL,
            H36_VALIDATE_SYMBOL,
        ],
        "guards": [
            "object_level_fixed_point_census",
            "finite_state_cycle_detection",
            "typed_meta_level_empty_set_closure",
            "reject_meta_zero_object_truth_promotion",
            "ordered_trajectory_witness",
            "exact_h36_identity",
            "finite_5184_pow4_cardinality_only",
            "no_unbounded_recursion",
            "no_new_vm81_hash72_hash216_authority",
        ],
        "rejection_codes": [
            "REJECT_PARADOX_UNBOUNDED_VISIT_BOUND",
            "REJECT_PARADOX_META_ZERO_OBJECT_LEVEL_CONFLATION",
            "REJECT_PARADOX_MISSING_FINITE_CLOSURE",
            "REJECT_PARADOX_ORDERED_TRAJECTORY_DRIFT",
            "REJECT_H36_IDENTITY_DRIFT",
            "REJECT_H36_NONCANONICAL_FLOAT",
        ],
        "applicability": "SELF_REFERENTIAL_OR_RECURSIVE_CONSTRAINT_EVALUATION",
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "WITNESS_ONLY",
        "declared_operations": [
            ANALYZE_SYMBOL,
            VALIDATE_SYMBOL,
            H36_SYMBOL,
            H36_VALIDATE_SYMBOL,
        ],
    }


def manifest() -> Dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "surface_id": SURFACE_ID,
        "fixed_point_semantics": "OBJECT_LEVEL_ONLY",
        "cycle_semantics": "FINITE_ORDERED_TRAJECTORY",
        "meta_zero_semantics": "EMPTY_OBJECT_LEVEL_VALID_SET_ONLY",
        "meta_zero_promotes_object_option": False,
        "canonical_random_guess_orbit": ["0", "1/4", "1/2", "1/4"],
        "canonical_random_guess_preperiod": 1,
        "canonical_random_guess_period": 2,
        "trinary": {
            "invalid_fixed_point_candidate": -1,
            "meta_closure": 0,
            "active_periodic_motion": 1,
        },
        "h36": {
            "a2": 1,
            "b2": 2,
            "c2": 3,
            "value": 36,
            "manifold_base": 5184,
            "manifold_power": 4,
            "manifold_cardinality": 722204136308736,
        },
        "canonical_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }


__all__ = [
    "VERSION",
    "SCHEMA",
    "SURFACE_ID",
    "ANALYZE_SYMBOL",
    "VALIDATE_SYMBOL",
    "H36_SYMBOL",
    "H36_VALIDATE_SYMBOL",
    "surface_declaration",
    "manifest",
]
