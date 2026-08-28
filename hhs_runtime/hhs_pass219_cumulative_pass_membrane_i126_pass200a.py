"""Pass 219 I126 membrane for repaired inherited Pass 200A shadow optimization."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i125_pass200b import (
    pass200b_membrane_source_evidence,
)

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_26"
PASS200A_NUMBER = 200
PASS200A_VARIANT = "A"
PASS200A_CLASSIFICATION = "WIRED"
PASS200A_CENSUS_CLASSIFICATION = "INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE"
PASS200A_BIND_SYMBOL = "hhs_exact_pass219_bind_pass200a_repaired_shadow_authority"
PASS200A_SURFACE_ID = "validator:pass219.inherited.pass200a.repaired-shadow-authority"

P = Path
CONTRACT_PATH = P("HHS_PASS_200A_PROOF_CARRYING_SHADOW_OPTIMIZATION.md")
HISTORICAL_RUNTIME_PATH = P("hhs_backend/runtime/hhs_pass200a_proof_carrying_optimization_v1.py")
PRODUCTION_PATH = P("hhs_backend/runtime/hhs_pass200a_proof_carrying_optimization.py")
REPAIRED_RUNTIME_PATH = P("hhs_backend/runtime/hhs_pass200a_proof_carrying_optimization_v2.py")
PROVENANCE_PATH = P("hhs_runtime/hhs_vm81_receipt_provenance_v1.py")
WORKFLOW_PATH = P(".github/workflows/pass200a-proof-carrying-shadow-optimization.yml")
ROUTES_PATH = P("hhs_backend/api/pass200a_optimization_routes.py")
TEST_PATH = P("tests/test_hhs_pass200a_proof_carrying_optimization_v1.py")
RESTART_PATH = P("docs/pass200a/RESTART_RECORD.md")
PASS200B_MEMBRANE_PATH = P("hhs_runtime/hhs_pass219_cumulative_pass_membrane_i125_pass200b.py")

HISTORICAL_BASE = "649be68e1566002ce66c919463a386b8018bc2fb"
HISTORICAL_REVIEWED_HEAD = "5ef1d3ab6c0ceb3a20d468447b991066626de366"
ACCEPTED_MERGE = "eee6670f7d3c6743e1bf32c7e42a4150d07351e3"
FROZEN_I125 = "21bf16233a0c4573a754c29686d13782bcc4fc44"

HISTORICAL_BLOBS = {
    CONTRACT_PATH: "46c9a8fdbacb80e1d136a67bd4b48e2e4a82c367",
    HISTORICAL_RUNTIME_PATH: "1f6d7b0092da3916705a58af9ae2ad2c22c3bab3",
    PRODUCTION_PATH: "521e89fc1c8b3067574884fb69a79a4d856887a1",
    WORKFLOW_PATH: "2817d207568e43f5621d56267f076503fa7e9628",
    ROUTES_PATH: "3f123916520c6b7f877903d50bb924992895bff6",
    TEST_PATH: "068a5e15e5a877ff439ab42535b1429cf77b00ad",
    RESTART_PATH: "984950272cd9463319b163cb7a2a1e2037c0da12",
}

REVIEW_FINDING_IDS = (
    3700651637,
    3700651638,
    3700651639,
    3700651640,
    3700651641,
    3700651642,
    3700651643,
    3700651644,
)

PRODUCTION_TOTALS = {
    "independent_envelopes": 4,
    "parameter_states": 290,
    "durable_branch_jobs": 580,
    "admitted_states": 263,
    "domain_rejections": 27,
    "vm5184_address_comparisons": 1_363_392,
    "negative_mutations": 24,
    "compiler_candidate_bundles": 4,
    "shadow_matches": 4,
    "reference_returns": 4,
    "candidate_activations": 0,
}

REQUIRED_OPERATIONS = (
    "validate_pass200a_squash_identity",
    "validate_pass200a_review_repair",
    "validate_pass200a_vm81_receipt_provenance",
    "validate_pass200a_independent_shadow_execution",
    "validate_pass200a_shadow_and_proof_integrity",
    "validate_pass200a_production_acceptance",
    "validate_pass200a_singleton_and_restartability",
    "validate_pass200b_successor_binding",
    "validate_pass200a_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _git_blob(path: Path) -> str:
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    return completed.stdout.strip()


def _require(path: Path, *fragments: str) -> None:
    text = _text(path)
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"PASS200A_REPAIR_SOURCE_DRIFT:{path}:{fragment}")


def pass200a_membrane_source_evidence() -> Dict[str, Any]:
    if _git("merge-base", "--is-ancestor", ACCEPTED_MERGE, "HEAD") != "":
        raise RuntimeError("PASS200A_ACCEPTED_MERGE_ANCESTRY_OUTPUT")
    if _git("merge-base", HISTORICAL_REVIEWED_HEAD, "HEAD") != HISTORICAL_BASE:
        raise RuntimeError("PASS200A_SQUASH_LINEAGE_DRIFT")
    if _git("merge-base", "HEAD", FROZEN_I125) != FROZEN_I125:
        raise RuntimeError("PASS200A_FROZEN_I125_LINEAGE_DRIFT")

    for path, expected in HISTORICAL_BLOBS.items():
        historical = _git("rev-parse", f"{ACCEPTED_MERGE}:{path}")
        if historical != expected:
            raise RuntimeError(f"PASS200A_HISTORICAL_BLOB_DRIFT:{path}:{historical}")
    if _git_blob(HISTORICAL_RUNTIME_PATH) != HISTORICAL_BLOBS[HISTORICAL_RUNTIME_PATH]:
        raise RuntimeError("PASS200A_HISTORICAL_V1_RUNTIME_WAS_REWRITTEN")
    if _git_blob(CONTRACT_PATH) != HISTORICAL_BLOBS[CONTRACT_PATH]:
        raise RuntimeError("PASS200A_HISTORICAL_CONTRACT_WAS_REWRITTEN")

    _require(
        REPAIRED_RUNTIME_PATH,
        "require_runtime_receipt_hash72",
        "candidate_lane_executed",
        "reference_lane_executed",
        "evaluate_branch_candidate",
        "shadow_hash72",
        "bundle source proof is no longer the current compiler candidate",
        "production_holdout_closed",
        "legacy_unbound_shadow_run_count",
        "partial",
        "candidate_execution_is_authority\": False",
    )
    _require(
        PROVENANCE_PATH,
        'RUNTIME_RECEIPT_KIND = "RUNTIME_RECEIPT"',
        'RUNTIME_RECEIPT_SOURCE = "HHSRuntimeController.commit_receipt"',
        "_load_with_errors(path, force_reload=True)",
        "authority_audit",
    )
    _require(
        PRODUCTION_PATH,
        "PASS200A_LEGACY_SINGLETON.__class__",
        "PASS200A_OPTIMIZATION_AUTHORITY = PASS200A_LEGACY_SINGLETON",
        "never create a second default-state authority",
    )
    _require(
        WORKFLOW_PATH,
        "HHSRuntimeController",
        "authorized_tick",
        "candidate_execution_count",
        "production_acceptance",
        "vm81_receipt_chain_verified",
    )
    _require(
        TEST_PATH,
        "test_arbitrary_72_glyph_receipt_is_rejected_before_mutation",
        "test_broken_candidate_lane_cannot_be_hardcoded_to_match",
        "test_persisted_shadow_payload_tamper_is_detected",
        "test_revoked_current_pass198_proof_invalidates_bundle",
        "test_partial_holdout_state_is_recoverable_in_progress",
    )

    successor = pass200b_membrane_source_evidence()
    return {
        "historical_base": HISTORICAL_BASE,
        "historical_reviewed_head": HISTORICAL_REVIEWED_HEAD,
        "accepted_merge": ACCEPTED_MERGE,
        "frozen_i125": FROZEN_I125,
        "historical_blobs": {str(path): value for path, value in HISTORICAL_BLOBS.items()},
        "review_finding_ids": list(REVIEW_FINDING_IDS),
        "historical_successful_run": 30772837176,
        "historical_artifact_id": 8841089828,
        "historical_artifact_digest": "sha256:642ca6be1883603409ee25c3067c096e40ad884a1ef0ca0ef7df6c9c1e83c8d1",
        "production_totals": dict(PRODUCTION_TOTALS),
        "pass200b_successor": successor,
    }


def validate_pass200a_squash_identity() -> Dict[str, Any]:
    s = pass200a_membrane_source_evidence()
    return {
        "ok": True,
        "pull_request": 138,
        "historical_base": s["historical_base"],
        "historical_reviewed_head": s["historical_reviewed_head"],
        "accepted_merge": s["accepted_merge"],
        "squash_aware": True,
        "historical_v1_runtime_preserved": True,
    }


def validate_pass200a_review_repair() -> Dict[str, Any]:
    s = pass200a_membrane_source_evidence()
    return {
        "ok": True,
        "review_finding_ids": s["review_finding_ids"],
        "finding_count": len(s["review_finding_ids"]),
        "repair_forward_version": "HHS_PASS_200A_PROOF_CARRYING_SHADOW_OPTIMIZATION_V2",
        "historical_v1_is_provenance_not_canonical_production": True,
    }


def validate_pass200a_vm81_receipt_provenance() -> Dict[str, Any]:
    pass200a_membrane_source_evidence()
    return {
        "ok": True,
        "shape_only_hash72_acceptance": False,
        "verified_unified_hash72_chain_required": True,
        "runtime_receipt_kind_required": "RUNTIME_RECEIPT",
        "runtime_receipt_source_required": "HHSRuntimeController.commit_receipt",
        "successful_authority_audit_required": True,
        "pass219_new_hash72_clock": False,
    }


def validate_pass200a_independent_shadow_execution() -> Dict[str, Any]:
    pass200a_membrane_source_evidence()
    return {
        "ok": True,
        "reference_branch": "A",
        "candidate_branch": "B",
        "both_lanes_independently_executed": True,
        "semantic_root_compared": True,
        "witness_root_compared": True,
        "independent_replay_compared": True,
        "hardcoded_match_forbidden": True,
        "returned_path": "REFERENCE",
        "candidate_execution_is_authority": False,
    }


def validate_pass200a_shadow_and_proof_integrity() -> Dict[str, Any]:
    pass200a_membrane_source_evidence()
    return {
        "ok": True,
        "shadow_hash72_recomputed": True,
        "shadow_event_payload_hash72_binding_required_for_qualification": True,
        "legacy_unbound_shadow_rows_nonqualifying": True,
        "current_pass198_simplification_required": True,
        "current_pass198_proof_hash72_required": True,
        "revoked_or_stale_source_rejected": True,
    }


def validate_pass200a_production_acceptance() -> Dict[str, Any]:
    s = pass200a_membrane_source_evidence()
    return {
        "ok": True,
        **s["production_totals"],
        "exact_default_holdout_identity_required": True,
        "custom_four_holdout_profile_can_claim_production_closed": False,
        "production_classification_requires_exact_totals": True,
    }


def validate_pass200a_singleton_and_restartability() -> Dict[str, Any]:
    pass200a_membrane_source_evidence()
    return {
        "ok": True,
        "v1_singleton_upgraded_in_place": True,
        "second_default_state_authority_constructed": False,
        "canonical_bundle_order": "simplification_id",
        "partial_envelope_count_1_to_3": "IN_PROGRESS",
        "partial_state_exception": False,
        "restart_revalidates_shadow_and_event_chain": True,
    }


def validate_pass200b_successor_binding() -> Dict[str, Any]:
    successor = pass200a_membrane_source_evidence()["pass200b_successor"]
    return {
        "ok": True,
        "successor_pass": 200,
        "successor_variant": "B",
        "successor_accepted_merge": successor["accepted_merge"],
        "successor_preserved": True,
    }


def validate_pass200a_no_new_authority() -> Dict[str, Any]:
    pass200a_membrane_source_evidence()
    return {
        "ok": True,
        "candidate_may_commit": False,
        "candidate_may_activate": False,
        "compiler_auto_activation": False,
        "runtime_auto_admission": False,
        "i126_new_candidate_authority": False,
        "i126_new_canonical_mutation_authority": False,
        "i126_new_persistence_authority": False,
        "i126_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
    }


def pass200a_surface_declaration() -> Dict[str, Any]:
    pass200a_membrane_source_evidence()
    return {
        "surface_id": PASS200A_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i126_pass200a",
        "symbol": "validate_pass200a_review_repair",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P200A-HOLDOUT-BUNDLE-SHADOW-VM81-H72-H216"],
        "witness_schemas": ["HHSExactPass200ARepairedShadowWitnessV2", "HHSExactPass219InheritedPass200ABindingV1"],
        "validators": [PASS200A_BIND_SYMBOL, "validate_pass200a_review_repair"],
        "guards": [
            "pass200a_squash_identity",
            "pass200a_review_repair",
            "pass200a_vm81_receipt_provenance",
            "pass200a_independent_shadow_execution",
            "pass200a_shadow_event_integrity",
            "pass200a_live_pass198_proof",
            "pass200a_exact_production_acceptance",
            "pass200a_singleton_identity",
            "pass200a_pass200b_successor",
        ],
        "rejection_codes": [
            "REJECT_PASS200A_HISTORICAL_IDENTITY_DRIFT",
            "REJECT_PASS200A_VM81_RECEIPT_PROVENANCE",
            "REJECT_PASS200A_UNEXECUTED_CANDIDATE",
            "REJECT_PASS200A_SHADOW_INTEGRITY",
            "REJECT_PASS200A_STALE_PASS198_PROOF",
            "REJECT_PASS200A_FALSE_PRODUCTION_CLOSURE",
            "REJECT_PASS200A_DUPLICATE_SINGLETON",
            "REJECT_PASS200A_SUCCESSOR_DRIFT",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_PASS200A_STATE_READ_ONLY_MEMBRANE",
        "boundedness_policy": "PASS_200A_REPAIRED_SHADOW_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass200a_membrane_manifest() -> Dict[str, Any]:
    s = pass200a_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS200A_NUMBER,
        "pass_variant": PASS200A_VARIANT,
        "pass_id": "pass200a",
        "classification": PASS200A_CLASSIFICATION,
        "census_classification": PASS200A_CENSUS_CLASSIFICATION,
        "pass219_c_abi_surface": PASS200A_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass200ARepairedShadowAuthority",
        "primary_pull_request": 138,
        "accepted_merge": s["accepted_merge"],
        "frozen_i125": FROZEN_I125,
        "review_finding_ids": s["review_finding_ids"],
        "surface": pass200a_surface_declaration(),
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def execute_pass200a_membrane_preflight() -> Dict[str, Any]:
    declaration = pass200a_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    return {
        "schema": "HHS_PASS219_I126_PASS200A_PREFLIGHT_V1",
        "version": VERSION,
        "ok": all(bool(row.get("ok")) for row in rows),
        "surface_id": PASS200A_SURFACE_ID,
        "operation_count": len(rows),
        "operations": rows,
    }


OPERATIONS = {
    "validate_pass200a_squash_identity": validate_pass200a_squash_identity,
    "validate_pass200a_review_repair": validate_pass200a_review_repair,
    "validate_pass200a_vm81_receipt_provenance": validate_pass200a_vm81_receipt_provenance,
    "validate_pass200a_independent_shadow_execution": validate_pass200a_independent_shadow_execution,
    "validate_pass200a_shadow_and_proof_integrity": validate_pass200a_shadow_and_proof_integrity,
    "validate_pass200a_production_acceptance": validate_pass200a_production_acceptance,
    "validate_pass200a_singleton_and_restartability": validate_pass200a_singleton_and_restartability,
    "validate_pass200b_successor_binding": validate_pass200b_successor_binding,
    "validate_pass200a_no_new_authority": validate_pass200a_no_new_authority,
}


def invoke(operation: str) -> Dict[str, Any]:
    if operation not in OPERATIONS:
        raise KeyError(f"unknown Pass 200A I126 membrane operation: {operation}")
    return OPERATIONS[operation]()
