"""Pass 219 global 25/3 latency-policy registration.

The latency policy is a mandatory guard for compatible latency-sensitive
Pass 219 runtime, data-processing, and machine-learning execution surfaces.
Timing remains observational/noncanonical: the guard may select only between
independently exact semantic-equivalent candidate routes and never creates
VM81, persistence, Hash72, or Hash216 authority.
"""

from __future__ import annotations

from typing import Any, Dict

from hhs_runtime.hhs_pass219_compression_debt_closure_registration_v1 import (
    MANDATORY_COMPRESSION_DEBT_GUARD,
    SCHEMA as COMPRESSION_DEBT_SCHEMA,
    SCHEDULE_SYMBOL as DEBT_SCHEDULE_SYMBOL,
)

VERSION = "PASS_219_GLOBAL_LATENCY_POLICY_25_3_1_0"
SCHEMA = "HHS_PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0"
SURFACE_ID = "guard:pass219.global_latency.25_over_3"

MANDATORY_LATENCY_GUARD = "pass219_global_latency_policy_25_over_3"
POLICY_SYMBOL = "hhs_exact_pass219_global_latency_policy"
POLICY_VALIDATE_SYMBOL = "hhs_exact_pass219_global_latency_policy_validate"
CLASSIFY_SYMBOL = "hhs_exact_pass219_global_latency_classify_ns"
WINDOW_SYMBOL = "hhs_exact_pass219_global_latency_window_evaluate"
SELECT_SYMBOL = "hhs_exact_pass219_global_latency_select_route"

TIER_FPS = (120, 60, 30)
TIER_MULTIPLIERS = (1, 2, 4)


def pass219_global_latency_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": SURFACE_ID,
        "surface_type": "GUARD",
        "module": "hhs_runtime_exact_abi",
        "symbol": SELECT_SYMBOL,
        "invariant_ids": [
            "HHS-I001",
            "HHS-I005",
            "HHS-I006",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
        ],
        "contract_schemas": [
            SCHEMA,
            "HHS_PASS219_GLOBAL_CANONICAL_DEFAULTS_V1",
            "HHS_PASS219_MANDATORY_GENESIS_SCALING_DATA_ML_1_22",
            COMPRESSION_DEBT_SCHEMA,
        ],
        "witness_schemas": [
            "HHS_PASS219_LATENCY_WINDOW_RESULT_V1",
            "HHS_PASS219_LATENCY_SELECTION_V1",
            "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1",
            "HHS_PASS219_COMPRESSION_DEBT_LAYER_RESULT_V1",
        ],
        "validators": [
            POLICY_SYMBOL,
            POLICY_VALIDATE_SYMBOL,
            CLASSIFY_SYMBOL,
            WINDOW_SYMBOL,
            SELECT_SYMBOL,
            DEBT_SCHEDULE_SYMBOL,
        ],
        "guards": [
            "exact_25_over_3_latency_quantum",
            "tier_120_60_30_exact_cross_product_gate",
            "exact_semantic_equality_before_latency_route_selection",
            "exact_selector_or_complete_fallback",
            "latency_budget_unmet_preserves_complete_correct_route",
            "timing_noncanonical",
            "candidate_acceleration_only",
            "single_c_vm81_mutation_authority",
            "existing_hash72_hash216_authority_only",
            MANDATORY_COMPRESSION_DEBT_GUARD,
            "physical_time_monotonic_no_time_credit",
        ],
        "rejection_codes": [
            "REJECT_PASS219_LATENCY_POLICY_ALGEBRA_DRIFT",
            "REJECT_PASS219_LATENCY_ROUTE_WITHOUT_EXACT_SEMANTIC_EQUALITY",
            "REJECT_PASS219_LATENCY_ROUTE_WITHOUT_EXACT_SELECTOR_OR_COMPLETE_FALLBACK",
            "REJECT_PASS219_LATENCY_CANDIDATE_CANONICAL_AUTHORITY",
            "REJECT_PASS219_LATENCY_AS_COMPRESSION_DEBT_CREDIT",
        ],
        "mutation_policy": "INHERITED_SINGLETON_VM81_ONLY",
        "persistence_policy": "INHERITED_HASH72_HASH216_PATHS_ONLY",
        "boundedness_policy": "PASS_219_GLOBAL_LATENCY_25_OVER_3_WINDOW_POLICY",
        "declared_operations": [
            CLASSIFY_SYMBOL,
            WINDOW_SYMBOL,
            SELECT_SYMBOL,
        ],
    }


def pass219_global_latency_manifest() -> Dict[str, Any]:
    return {
        "schema": "HHS_PASS219_GLOBAL_LATENCY_POLICY_REGISTRATION_V1",
        "version": VERSION,
        "contract_schema": SCHEMA,
        "surface_id": SURFACE_ID,
        "mandatory_guard": MANDATORY_LATENCY_GUARD,
        "mandatory_for_compatible_latency_sensitive_pass219_surfaces": True,
        "exact_latency_quantum_ms": {"numerator": 25, "denominator": 3},
        "tiers": [
            {"tier": 1, "fps": 120, "multiplier": 1},
            {"tier": 2, "fps": 60, "multiplier": 2},
            {"tier": 3, "fps": 30, "multiplier": 4},
        ],
        "window_policy": {
            "mean_max_tier": 1,
            "p95_max_tier": 2,
            "max_max_tier": 3,
        },
        "route_policy": {
            "exact_semantic_equality_required": True,
            "exact_selector_or_complete_fallback_required": True,
            "unmet_budget_preserves_correct_route": True,
            "timing_can_change_semantic_identity": False,
        },
        "canonical_authority": {
            "latency_policy": False,
            "pass207": False,
            "pass208": False,
            "singleton_vm81": "INHERITED_C_ONLY",
            "hash72_hash216": "INHERITED_PATHS_ONLY",
        },
        "compression_debt_coupling": {
            "mandatory_guard": MANDATORY_COMPRESSION_DEBT_GUARD,
            "schema": COMPRESSION_DEBT_SCHEMA,
            "conserved_quantity": "COMPRESSION_DEBT",
            "elapsed_time_is_debt": False,
            "physical_time_monotonic": True,
            "over_budget_scheduler_action": "TRANSFER_OR_RECOMPRESS_UNSETTLED_DEBT",
        },
        "floating_point_authority": False,
        "timing_is_noncanonical": True,
        "performance_guarantee": False,
        "policy_enforcement_required": True,
    }


__all__ = [
    "VERSION",
    "SCHEMA",
    "SURFACE_ID",
    "MANDATORY_LATENCY_GUARD",
    "POLICY_SYMBOL",
    "POLICY_VALIDATE_SYMBOL",
    "CLASSIFY_SYMBOL",
    "WINDOW_SYMBOL",
    "SELECT_SYMBOL",
    "TIER_FPS",
    "TIER_MULTIPLIERS",
    "pass219_global_latency_surface_declaration",
    "pass219_global_latency_manifest",
]
