"""Registration contract for the Pass 219 cross-modal reversible manifold guard."""

from __future__ import annotations

from typing import Any, Dict

VERSION = "PASS_219_CROSS_MODAL_REVERSIBLE_STATE_MANIFOLD_1_0"
SCHEMA = "HHS_PASS219_CROSS_MODAL_REVERSIBLE_STATE_MANIFOLD_V1"
SURFACE_ID = "guard:pass219.cross_modal_reversible_state_manifold"
MANDATORY_GUARD = "pass219_cross_modal_reversible_state_manifold"
STATE_VALIDATE_SYMBOL = "hhs_exact_pass219_cross_modal_state_validate"
WORK_PLAN_SYMBOL = "hhs_exact_pass219_cross_modal_work_plan"


def surface_declaration() -> Dict[str, Any]:
    return {
        "surface_id": SURFACE_ID,
        "surface_type": "GUARD",
        "module": "hhs_runtime_exact_abi",
        "symbol": STATE_VALIDATE_SYMBOL,
        "invariant_ids": ["HHS-I001", "HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": [SCHEMA],
        "witness_schemas": [
            "HHS_PASS219_CROSS_MODAL_STATE_WITNESS_V1",
            "HHS_PASS219_CROSS_MODAL_WORK_PLAN_V1",
        ],
        "validators": [STATE_VALIDATE_SYMBOL, WORK_PLAN_SYMBOL],
        "guards": [
            "genesis_lineage_required",
            "ordered_noncommutative_phase_path_required",
            "required_modality_coverage_required",
            "lossless_adapters_require_exact_roundtrip",
            "global_constraint_root_binding_required",
            "modality_registry_root_binding_required",
            "sealed_prefix_reuse_requires_exact_identity",
            "candidate_optimizer_has_no_mutation_authority",
            "singleton_vm81_admission_required",
        ],
        "rejection_codes": [
            "REJECT_CROSS_MODAL_LINEAGE_MISSING",
            "REJECT_CROSS_MODAL_PHASE_ORDER_DRIFT",
            "REJECT_CROSS_MODAL_MAPPING_INCOMPLETE",
            "REJECT_CROSS_MODAL_ROUNDTRIP_MISMATCH",
            "REJECT_CROSS_MODAL_CONSTRAINT_ROOT_DRIFT",
            "REJECT_CROSS_MODAL_PREFIX_PROOF_STALE",
            "REJECT_CROSS_MODAL_CANDIDATE_AUTHORITY",
        ],
        "mutation_policy": "INHERITED_SINGLETON_VM81_ONLY",
        "persistence_policy": "INHERITED_HASH72_HASH216_PATHS_ONLY",
        "boundedness_policy": "PASS_219_CROSS_MODAL_EXACT_BOUNDED_WORK_V1",
        "declared_operations": [STATE_VALIDATE_SYMBOL, WORK_PLAN_SYMBOL],
    }


def manifest() -> Dict[str, Any]:
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "surface_id": SURFACE_ID,
        "mandatory_guard": MANDATORY_GUARD,
        "vm81_cells": 81,
        "operations_per_cell": 64,
        "addresses": 5184,
        "branch_model": "IMMUTABLE_PARENT_DAG_WITH_EXACT_REPLAY",
        "phase_order": "NONCOMMUTATIVE_ORDER_IS_STATE_IDENTITY",
        "translation_model": "CANONICAL_VM81_5184_HUB_WITH_EXACT_ROUNDTRIP_WITNESSES",
        "optimization_model": "SEALED_PREFIX_REUSE_PLUS_HUB_TRANSLATION",
        "optimization_fallback": "COMPLETE_ALL_TO_ALL_VALIDATION",
        "candidate_mutation_authority": False,
        "singleton_vm81_authority_required": True,
        "floating_point_authority": False,
    }


__all__ = [
    "VERSION",
    "SCHEMA",
    "SURFACE_ID",
    "MANDATORY_GUARD",
    "STATE_VALIDATE_SYMBOL",
    "WORK_PLAN_SYMBOL",
    "surface_declaration",
    "manifest",
]
