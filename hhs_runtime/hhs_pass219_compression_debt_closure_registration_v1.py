"""Pass 219 exact reciprocal 3/25 compression-debt closure registration.

Compression debt is conserved computational obligation. Physical elapsed time is
not debt and is never credited back. Every compatible Pass 219 surface that
defers work must close at the native 5184-bit boundary with either physically
settled work, retained typed compressed debt, or reciprocal typed transfer.
"""

from __future__ import annotations

from typing import Any, Dict

VERSION = "PASS_219_COMPRESSION_DEBT_CLOSURE_3_25_1_0"
SCHEMA = "HHS_PASS219_COMPRESSION_DEBT_CLOSURE_3_25_1_0"
SURFACE_ID = "guard:pass219.compression_debt.native_5184"

MANDATORY_COMPRESSION_DEBT_GUARD = "pass219_compression_debt_native_5184_zero_sum_closure"

POLICY_SYMBOL = "hhs_exact_pass219_compression_debt_policy"
POLICY_VALIDATE_SYMBOL = "hhs_exact_pass219_compression_debt_policy_validate"
EXCHANGE_SYMBOL = "hhs_exact_pass219_compression_debt_exchange"
LAYER_CLOSE_SYMBOL = "hhs_exact_pass219_compression_debt_layer_close"
TRANSFER_VERIFY_SYMBOL = "hhs_exact_pass219_compression_debt_transfer_pair_verify"
TRANSFER_BOUND_SYMBOL = "hhs_exact_pass219_compression_debt_transfer_pair_verify_bound"
GLOBAL_CLOSE_SYMBOL = "hhs_exact_pass219_compression_debt_global_close"
SCHEDULE_SYMBOL = "hhs_exact_pass219_compression_debt_schedule_evaluate"
BOUNDARY_SYMBOL = "hhs_exact_pass219_native_5184_closure_boundary_verify"


def pass219_compression_debt_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": SURFACE_ID,
        "surface_type": "GUARD",
        "module": "hhs_runtime_exact_abi",
        "symbol": BOUNDARY_SYMBOL,
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
            "HHS_PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0",
        ],
        "witness_schemas": [
            "HHS_PASS219_COMPRESSION_DEBT_LAYER_RESULT_V1",
            "HHS_PASS219_COMPRESSION_DEBT_TRANSFER_PAIR_V1",
            "HHS_PASS219_NATIVE_5184_CLOSURE_BOUNDARY_RESULT_V1",
            "HHS_PASS219_HASH216_TRANSITION_VIEW_V1",
        ],
        "validators": [
            POLICY_SYMBOL,
            POLICY_VALIDATE_SYMBOL,
            EXCHANGE_SYMBOL,
            LAYER_CLOSE_SYMBOL,
            TRANSFER_VERIFY_SYMBOL,
            TRANSFER_BOUND_SYMBOL,
            GLOBAL_CLOSE_SYMBOL,
            SCHEDULE_SYMBOL,
            BOUNDARY_SYMBOL,
        ],
        "guards": [
            "physical_time_monotonic_no_time_credit",
            "exact_3_over_25_debt_25_over_3_capacity_reciprocal",
            "local_compression_debt_zero_sum",
            "reciprocal_transfer_debit_credit_pair",
            "no_anonymous_debt_cross_native_boundary",
            "native_81_times_64_equals_5184_boundary",
            "hash72_times_3_hash216_lane_order",
            "all_216_sha256_positional_indexes_required",
            "ordered_octonion_phase_witness_required",
            "lo_shu_sudoku_qudit_genesis_required",
            "immediate_active_surface_at_most_7_of_81",
            "full_vm81_frame_preserved",
            "single_c_vm81_mutation_authority",
            "existing_hash72_hash216_authority_only",
        ],
        "rejection_codes": [
            "REJECT_PASS219_ORPHAN_COMPRESSION_DEBT",
            "REJECT_PASS219_TRANSFER_WITHOUT_RECIPROCAL_ENTRY",
            "REJECT_PASS219_TRANSFER_WITHOUT_COMPLETE_HASH216_INDEX",
            "REJECT_PASS219_TRANSFER_WITHOUT_NATIVE_5184_ADDRESS",
            "REJECT_PASS219_ACTIVE_SURFACE_ABOVE_7_OF_81",
            "REJECT_PASS219_DEBT_AS_ELAPSED_TIME",
            "REJECT_PASS219_COMPRESSION_DEBT_CANONICAL_AUTHORITY",
        ],
        "mutation_policy": "INHERITED_SINGLETON_VM81_ONLY",
        "persistence_policy": "INHERITED_HASH72_HASH216_PATHS_ONLY",
        "boundedness_policy": "PASS219_7_OF_81_IMMEDIATE_ACTIVE_SURFACE_WITH_EXACT_DEBT_TRANSFER",
        "declared_operations": [
            LAYER_CLOSE_SYMBOL,
            TRANSFER_BOUND_SYMBOL,
            GLOBAL_CLOSE_SYMBOL,
            SCHEDULE_SYMBOL,
            BOUNDARY_SYMBOL,
        ],
    }


def pass219_compression_debt_manifest() -> Dict[str, Any]:
    return {
        "schema": "HHS_PASS219_COMPRESSION_DEBT_REGISTRATION_V1",
        "version": VERSION,
        "contract_schema": SCHEMA,
        "surface_id": SURFACE_ID,
        "mandatory_guard": MANDATORY_COMPRESSION_DEBT_GUARD,
        "conserved_quantity": "COMPRESSION_DEBT",
        "elapsed_time_is_conserved_debt": False,
        "physical_time_monotonic": True,
        "native_boundary": {
            "bits": 5184,
            "bytes": 648,
            "vm81_cells": 81,
            "x86_word_bits": 64,
            "hash72_lanes": 3,
            "hash216_occurrences": 216,
            "sha256_bytes_per_occurrence": 32,
        },
        "reciprocal_normalization": {
            "compression_debt": {"numerator": 3, "denominator": 25},
            "execution_capacity": {"numerator": 25, "denominator": 3},
        },
        "active_surface": {
            "immediate_cells_max": 7,
            "total_vm81_cells": 81,
            "materialized_fraction": {"numerator": 7, "denominator": 81},
            "reference_reduction": {"numerator": 81, "denominator": 7},
            "reference_reduction_x1000": 11571,
        },
        "local_closure": (
            "inbound + issued = executed_settled + retained_compressed + transferred_out"
        ),
        "global_closure": (
            "internal transfer debits cancel credits; created = settled + retained outstanding"
        ),
        "latency_coupling": {
            "quantum_ms": {"numerator": 25, "denominator": 3},
            "timing_is_noncanonical": True,
            "over_budget_does_not_credit_time_back": True,
            "over_budget_scheduler_action": "TRANSFER_OR_RECOMPRESS_UNSETTLED_DEBT",
        },
        "canonical_authority": {
            "debt_ledger": False,
            "scheduler": False,
            "cache": False,
            "gpu": False,
            "vector_store": False,
            "singleton_vm81": "INHERITED_C_ONLY",
            "hash72_hash216": "INHERITED_PATHS_ONLY",
        },
        "floating_point_authority": False,
    }


__all__ = [
    "VERSION",
    "SCHEMA",
    "SURFACE_ID",
    "MANDATORY_COMPRESSION_DEBT_GUARD",
    "POLICY_SYMBOL",
    "POLICY_VALIDATE_SYMBOL",
    "EXCHANGE_SYMBOL",
    "LAYER_CLOSE_SYMBOL",
    "TRANSFER_VERIFY_SYMBOL",
    "TRANSFER_BOUND_SYMBOL",
    "GLOBAL_CLOSE_SYMBOL",
    "SCHEDULE_SYMBOL",
    "BOUNDARY_SYMBOL",
    "pass219_compression_debt_surface_declaration",
    "pass219_compression_debt_manifest",
]
