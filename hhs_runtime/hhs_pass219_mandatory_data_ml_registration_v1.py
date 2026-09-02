"""Pass 219 mandatory Sudoku-qudit Genesis + deterministic scaling registration.

Every Pass 219 data-processing or machine-learning execution surface must
declare this guard.  The guard is a registration/admission prerequisite; it
does not grant mutation authority and it does not replace singleton VM81.
"""

from __future__ import annotations

from typing import Any, Dict

from hhs_runtime.hhs_pass219_cross_modal_reversible_state_registration_v1 import (
    MANDATORY_GUARD as CROSS_MODAL_MANIFOLD_GUARD,
    SCHEMA as CROSS_MODAL_MANIFOLD_SCHEMA,
    STATE_VALIDATE_SYMBOL as CROSS_MODAL_STATE_VALIDATE_SYMBOL,
    WORK_PLAN_SYMBOL as CROSS_MODAL_WORK_PLAN_SYMBOL,
)

from hhs_runtime.hhs_pass219_raw5184_octonion_audio_hydration_registration_v1 import (
    BIT_EXPORT_SYMBOL as AUDIO5184_BIT_EXPORT_SYMBOL,
    BIT_IMPORT_SYMBOL as AUDIO5184_BIT_IMPORT_SYMBOL,
    FRAME_TO_PCM_SYMBOL as AUDIO5184_FRAME_TO_PCM_SYMBOL,
    HYDRATE_SYMBOL as AUDIO5184_HYDRATE_SYMBOL,
    MANDATORY_GUARD as AUDIO5184_GUARD,
    PCM_TO_FRAME_SYMBOL as AUDIO5184_PCM_TO_FRAME_SYMBOL,
    PIPELINE_SYMBOL as AUDIO5184_PIPELINE_SYMBOL,
    SCHEMA as AUDIO5184_SCHEMA,
    VALIDATE_SYMBOL as AUDIO5184_VALIDATE_SYMBOL,
)

from hhs_runtime.hhs_pass219_global_latency_policy_registration_v1 import (
    CLASSIFY_SYMBOL as LATENCY_CLASSIFY_SYMBOL,
    MANDATORY_LATENCY_GUARD,
    POLICY_VALIDATE_SYMBOL as LATENCY_POLICY_VALIDATE_SYMBOL,
    SCHEMA as LATENCY_POLICY_SCHEMA,
    SELECT_SYMBOL as LATENCY_SELECT_SYMBOL,
    WINDOW_SYMBOL as LATENCY_WINDOW_SYMBOL,
)

VERSION = "PASS_219_MANDATORY_GENESIS_SCALING_DATA_ML_1_22"
SCHEMA = "HHS_PASS219_MANDATORY_GENESIS_SCALING_DATA_ML_1_22"
SURFACE_ID = "guard:pass219.mandatory.genesis_scaling.data_ml"

MANDATORY_GUARD = "pass219_mandatory_sudoku_genesis_scaling_data_ml"
PLAN_SYMBOL = "hhs_exact_pass219_mandatory_scaling_plan"
VERIFY_SYMBOL = "hhs_exact_pass219_mandatory_scaling_verify"
GENESIS_SYMBOL = "hhs_exact_pass219_genesis_descriptor"
GENESIS_VALIDATE_SYMBOL = "hhs_exact_pass219_genesis_validate"

WORK_CLASSES = (
    "DATA_INGEST",
    "DATA_TRANSFORM",
    "DATA_INDEX",
    "FEATURE_HYDRATION",
    "VECTOR_RETRIEVAL",
    "ML_TRAIN",
    "ML_INFERENCE",
    "ML_UPDATE",
    "ML_EVALUATION",
    "MULTIMODAL_PROCESSING",
    "SERIALIZATION",
    "REPLAY",
)

STAGE_ORDER = (
    "GENESIS_NORMALIZE",
    "PHASE_LOCALITY",
    "PASS207_BATCH_CACHE",
    "PASS208_CANDIDATE_EXPANSION",
    "EXACT_CPU_VM_ORACLE",
    "SINGLETON_VM81_ADMISSION",
    "I7_SELECTIVE_PROJECTION",
    "I8_SPARSE_DIRTY_DERIVED",
    "HASH72_HASH216_EXISTING_PATH",
)


def pass219_mandatory_data_ml_surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": SURFACE_ID,
        "surface_type": "GUARD",
        "module": "hhs_runtime_exact_abi",
        "symbol": PLAN_SYMBOL,
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
            "HHS_PASS219B_UNIVERSAL_PHASE_LOCALITY_INVARIANT_1_0",
            "HHS_PASS219_RNA_EXECUTION_COMPOSER_ABI_1_14",
            LATENCY_POLICY_SCHEMA,
            CROSS_MODAL_MANIFOLD_SCHEMA,
            AUDIO5184_SCHEMA,
        ],
        "witness_schemas": [
            "HHS_PASS219_MANDATORY_SCALING_PLAN_V1",
            "HHS_PASS219_MANDATORY_SCALING_WITNESS_V1",
            "HHS_KERNEL_RUNTIME_COMPOSITION_WITNESS_V1",
            "HHS_PASS219_LATENCY_WINDOW_RESULT_V1",
            "HHS_PASS219_LATENCY_SELECTION_V1",
        ],
        "validators": [
            GENESIS_SYMBOL,
            GENESIS_VALIDATE_SYMBOL,
            PLAN_SYMBOL,
            VERIFY_SYMBOL,
            LATENCY_POLICY_VALIDATE_SYMBOL,
            LATENCY_CLASSIFY_SYMBOL,
            LATENCY_WINDOW_SYMBOL,
            LATENCY_SELECT_SYMBOL,
            CROSS_MODAL_STATE_VALIDATE_SYMBOL,
            CROSS_MODAL_WORK_PLAN_SYMBOL,
            AUDIO5184_BIT_IMPORT_SYMBOL,
            AUDIO5184_BIT_EXPORT_SYMBOL,
            AUDIO5184_FRAME_TO_PCM_SYMBOL,
            AUDIO5184_PCM_TO_FRAME_SYMBOL,
            AUDIO5184_HYDRATE_SYMBOL,
            AUDIO5184_VALIDATE_SYMBOL,
            AUDIO5184_PIPELINE_SYMBOL,
        ],
        "guards": [
            "exact_sudoku_qudit_genesis_normalization",
            "exact_phase_selector_or_dense_fallback",
            "pass207_candidate_acceleration_only",
            "pass208_candidate_expansion_only",
            "exact_cpu_vm_oracle_before_vm81",
            "single_c_vm81_mutation_authority",
            "i7_post_admission_projection_only",
            "i8_complete_dirty_witness_or_full_derived_path",
            "existing_hash72_hash216_authority_only",
            MANDATORY_LATENCY_GUARD,
            CROSS_MODAL_MANIFOLD_GUARD,
            AUDIO5184_GUARD,
        ],
        "rejection_codes": [
            "REJECT_PASS219_DATA_ML_WITHOUT_GENESIS_NORMALIZATION",
            "REJECT_PASS219_PHASE_LOCALITY_WITHOUT_EXACT_SELECTOR",
            "REJECT_PASS219_SPARSE_DERIVED_WITHOUT_COMPLETE_DIRTY_WITNESS",
            "REJECT_PASS219_CANDIDATE_ACCELERATOR_CANONICAL_AUTHORITY",
            "REJECT_PASS219_DATA_ML_WITHOUT_EXACT_CPU_VM_EQUALITY",
            "REJECT_PASS219_DATA_ML_WITHOUT_GLOBAL_LATENCY_POLICY",
            "REJECT_PASS219_DATA_ML_WITHOUT_CROSS_MODAL_MANIFOLD_PROOF",
            "REJECT_PASS219_SERIALIZATION_WITHOUT_RAW5184_PCM64_HYDRATION",
        ],
        "mutation_policy": "INHERITED_SINGLETON_VM81_ONLY",
        "persistence_policy": "INHERITED_HASH72_HASH216_PATHS_ONLY",
        "boundedness_policy": "PASS_219_EXACT_WORKLOAD_BOUND_SCALING_1_22",
        "declared_operations": [PLAN_SYMBOL, VERIFY_SYMBOL],
    }


def pass219_mandatory_data_ml_manifest() -> Dict[str, Any]:
    return {
        "schema": "HHS_PASS219_MANDATORY_DATA_ML_REGISTRATION_V1",
        "version": VERSION,
        "contract_schema": SCHEMA,
        "surface_id": SURFACE_ID,
        "mandatory_guard": MANDATORY_GUARD,
        "mandatory_for_all_pass219_data_processing": True,
        "mandatory_for_all_pass219_machine_learning": True,
        "mandatory_latency_guard": MANDATORY_LATENCY_GUARD,
        "mandatory_latency_schema": LATENCY_POLICY_SCHEMA,
        "mandatory_cross_modal_manifold_guard": CROSS_MODAL_MANIFOLD_GUARD,
        "mandatory_cross_modal_manifold_schema": CROSS_MODAL_MANIFOLD_SCHEMA,
        "mandatory_audio5184_guard": AUDIO5184_GUARD,
        "mandatory_audio5184_schema": AUDIO5184_SCHEMA,
        "work_classes": list(WORK_CLASSES),
        "stage_order": list(STAGE_ORDER),
        "genesis": {
            "side": 9,
            "cells": 81,
            "operations_per_cell": 64,
            "addresses": 5184,
            "trit_rule": "(sudoku_symbol mod 3) - 1",
            "zero_sum_units": ["rows", "columns", "blocks", "diagonals"],
            "hydration_rom_empty_state": True,
        },
        "fallbacks": {
            "missing_exact_phase_selector": "DENSE_COMPLETE_PATH",
            "incomplete_dirty_witness": "FULL_DERIVED_PROJECTION_PATH",
            "failed_exact_cpu_vm_equality": "DENY_CANONICAL_ADMISSION",
        },
        "canonical_authority": {
            "pass207": False,
            "pass208": False,
            "i7_projection": False,
            "i8_sparse_projection": False,
            "singleton_vm81": "INHERITED_C_ONLY",
            "hash72_hash216": "INHERITED_PATHS_ONLY",
        },
        "latency_policy": {
            "quantum_ms": {"numerator": 25, "denominator": 3},
            "tiers_fps": [120, 60, 30],
            "mean_max_tier": 1,
            "p95_max_tier": 2,
            "max_max_tier": 3,
            "timing_is_noncanonical": True,
            "unmet_budget_preserves_complete_correct_route": True,
        },
        "floating_point_authority": False,
    }


__all__ = [
    "VERSION",
    "SCHEMA",
    "SURFACE_ID",
    "MANDATORY_GUARD",
    "PLAN_SYMBOL",
    "VERIFY_SYMBOL",
    "GENESIS_SYMBOL",
    "GENESIS_VALIDATE_SYMBOL",
    "WORK_CLASSES",
    "STAGE_ORDER",
    "pass219_mandatory_data_ml_surface_declaration",
    "pass219_mandatory_data_ml_manifest",
]
