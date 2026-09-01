"""Pass 219 holographic harmonic-window registration.

This guard binds exact recursive window scaling and direct layer-addressed
branch evaluation to the canonical 25/3 latency quantum. It is candidate /
routing logic only and cannot mutate VM81 or Hash72/Hash216 authority.
"""

from __future__ import annotations

from typing import Any, Dict

VERSION = "PASS_219_HOLOGRAPHIC_HARMONIC_WINDOW_25_3_1_0"
SCHEMA = "HHS_PASS219_HOLOGRAPHIC_HARMONIC_WINDOW_25_3_1_0"
SURFACE_ID = "guard:pass219.holographic_harmonic_window.25_over_3"

MANDATORY_HOLOGRAPHIC_WINDOW_GUARD = (
    "pass219_holographic_harmonic_window_25_over_3"
)
INVARIANT_SYMBOL = "hhs_exact_pass219_holographic_harmonic_window_invariant"
VALIDATE_SYMBOL = "hhs_exact_pass219_holographic_harmonic_window_validate"
BRANCH_SYMBOL = "hhs_exact_pass219_holographic_branch_evaluate"


def pass219_holographic_harmonic_window_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": SURFACE_ID,
        "surface_type": "GUARD",
        "module": "hhs_runtime_exact_abi",
        "symbol": BRANCH_SYMBOL,
        "invariant_ids": ["HHS-I001", "HHS-I005", "HHS-I006", "HHS-I011", "HHS-I014"],
        "contract_schemas": [
            SCHEMA,
            "HHS_PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0",
            "HHS_PASS219_MANDATORY_GENESIS_SCALING_DATA_ML_1_22",
        ],
        "witness_schemas": [
            "HHS_PASS219_HOLOGRAPHIC_WINDOW_RESIDUES_V1",
            "HHS_PASS219_HOLOGRAPHIC_WINDOW_INVARIANT_V1",
            "HHS_PASS219_HOLOGRAPHIC_BRANCH_RESULT_V1",
        ],
        "validators": [INVARIANT_SYMBOL, VALIDATE_SYMBOL, BRANCH_SYMBOL],
        "guards": [
            "exact_residue_witness_gate",
            "harmonic_25_over_3_closure_gate",
            "direct_layer_address_gate",
            "finite_depth_gate",
            "overflow_fail_closed_gate",
            "complete_fallback_gate",
            "single_c_vm81_mutation_authority",
        ],
        "rejection_codes": [
            "REJECT_HOLOGRAPHIC_WINDOW_RESIDUE_DRIFT",
            "REJECT_HOLOGRAPHIC_WINDOW_CLOSURE_FAILURE",
            "REJECT_HOLOGRAPHIC_WINDOW_DEPTH_RANGE",
            "REJECT_HOLOGRAPHIC_WINDOW_ARITHMETIC_OVERFLOW",
            "REJECT_HOLOGRAPHIC_WINDOW_CANONICAL_AUTHORITY",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "NO_PERSISTENCE_MUTATION",
        "boundedness_policy": "DIRECT_LAYER_FIXED_WIDTH_DEPTH_0_TO_9",
        "declared_operations": [INVARIANT_SYMBOL, BRANCH_SYMBOL],
    }


def pass219_holographic_harmonic_window_manifest() -> Dict[str, Any]:
    return {
        "schema": "HHS_PASS219_HOLOGRAPHIC_HARMONIC_WINDOW_REGISTRATION_V1",
        "version": VERSION,
        "contract_schema": SCHEMA,
        "surface_id": SURFACE_ID,
        "mandatory_guard": MANDATORY_HOLOGRAPHIC_WINDOW_GUARD,
        "algebra": {
            "a2": 1,
            "b2": 2,
            "c2": 3,
            "d2": 5,
            "residues": ["t^3-t", "m^2-m"],
            "closed_residue_reference": {"t^3-t": 1, "m^2-m": 1},
            "equation": (
                "d^4/c^2="
                "(b^2*(t^3-t)+(a^2+b^2)*(m^2-m))^2/(d^2-b^2)"
            ),
            "closed_ratio": {"numerator": 25, "denominator": 3},
        },
        "recursive_window": {
            "law": "W_k=W_0*(3/25)^k",
            "maximum_current_depth": 9,
            "direct_layer_addressed": True,
            "recursion_stack_required": False,
            "pointer_tree_traversal_required": False,
            "one_layer_fixed_width_work": True,
            "whole_path_depth_bounded": True,
            "unbounded_depth_constant_time_claim": False,
        },
        "branch": {
            "predicate": "phase_coordinate <= active_window (or strict <)",
            "evaluation": "exact rational cross multiplication",
            "floating_point_authority": False,
        },
        "authority": {
            "canonical_mutation": False,
            "canonical_persistence": False,
            "hash72_hash216": False,
            "singleton_vm81": "INHERITED_C_ONLY",
        },
        "fallback": "COMPLETE_INHERITED_PATH_ON_UNAVAILABLE_OR_INVALID_WINDOW_PROOF",
    }


__all__ = [
    "VERSION",
    "SCHEMA",
    "SURFACE_ID",
    "MANDATORY_HOLOGRAPHIC_WINDOW_GUARD",
    "INVARIANT_SYMBOL",
    "VALIDATE_SYMBOL",
    "BRANCH_SYMBOL",
    "pass219_holographic_harmonic_window_surface_declaration",
    "pass219_holographic_harmonic_window_manifest",
]
