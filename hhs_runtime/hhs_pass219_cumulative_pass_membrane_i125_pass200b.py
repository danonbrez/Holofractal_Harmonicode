"""Pass 219 I125 read-only membrane for accepted Pass 200B governed canary admission."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i124_pass200c import pass200c_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_25"
PASS200B_NUMBER = 200
PASS200B_VARIANT = "B"
PASS200B_CLASSIFICATION = "WIRED"
PASS200B_CENSUS_CLASSIFICATION = "MISSING_MEMBRANE_EXPOSURE"
PASS200B_BIND_SYMBOL = "hhs_exact_pass219_bind_pass200b_governed_canary_admission"
PASS200B_SURFACE_ID = "validator:pass219.inherited.pass200b.governed-canary-admission"

P = Path
CONTRACT_PATH = P("HHS_PASS_200B_GOVERNED_CANARY_ADMISSION.md")
WORKFLOW_PATH = P(".github/workflows/pass200b-governed-canary-admission.yml")
RUNTIME_V1_PATH = P("hhs_backend/runtime/hhs_pass200b_governed_canary_admission_v1.py")
PRODUCTION_PATH = P("hhs_backend/runtime/hhs_pass200b_governed_canary_admission.py")
CANARY_ROUTES_PATH = P("hhs_backend/api/pass200b_canary_routes.py")
CONTRACT_TEST_PATH = P("tests/test_hhs_pass200b_governed_canary_admission_v1.py")
VISUAL_PANEL_PATH = P("applications/holofractal_harmonizer/src/pass200b-governed-canary.mjs")
RESTART_PATH = P("docs/pass200b/RESTART_RECORD.md")
PASS200C_MEMBRANE_PATH = P("hhs_runtime/hhs_pass219_cumulative_pass_membrane_i124_pass200c.py")

PRIMARY_BASE = "483a18b618dbe51b31025eeb15a8a6435e4040c5"
VALIDATED_EXECUTABLE_HEAD = "f13eed02531e77737562b23fb207962c0744ed0d"
EVIDENCE_HEAD = "07f12ba91d78d28f0d9f73ec54e3167d4f1fa5b3"
ACCEPTED_MERGE = "eb7dd08b8bc52451c2e179b68949097ade5499af"
FROZEN_I124 = "18ca57da270785483679e36a4d861c2002c69323"

HISTORICAL_BLOBS = {
    CONTRACT_PATH: "1e442f002bd0936090a5b7154150021e0a543948",
    WORKFLOW_PATH: "e0b2335d509839f9175c5e6a08eef6bbbd18d437",
    RUNTIME_V1_PATH: "8034383ec6dcad463c45296c9eeb241f3e1123c5",
    PRODUCTION_PATH: "67e79a10250bfa3e9678937d28ed4bc22fed9937",
    CANARY_ROUTES_PATH: "abb2bee87c7ad12e0d3e441840bdb0643d425b05",
    CONTRACT_TEST_PATH: "ad843727f95b517c6f9c77b2338434c6605ba5d0",
    VISUAL_PANEL_PATH: "def9ff882023c310ffd1ab3ff0d040115f2a76b2",
    RESTART_PATH: "435fd4f65b0d9f423e3ec6ec1a155f4d35948c13",
}

HISTORICAL_CLOSURE = {
    "pass200a_independent_envelopes": 4,
    "pass200a_compiler_candidate_bundles": 4,
    "pass200a_exact_shadow_matches": 4,
    "canary_frontiers": 2,
    "singleton_activation_commits": 2,
    "bounded_invocations": 9,
    "candidate_returns": 2,
    "reference_returns": 7,
    "rollback_frontiers": 1,
    "exhausted_frontiers": 1,
    "immutable_frontiers_including_genesis": 5,
    "hash72_events": 14,
}

REQUIRED_OPERATIONS = (
    "validate_pass200b_squash_identity",
    "validate_pass200b_pass200a_shadow_gate",
    "validate_pass200b_dual_approval_and_activation",
    "validate_pass200b_bounded_exact_canary",
    "validate_pass200b_persistence_and_rollback",
    "validate_pass200c_successor_binding",
    "validate_pass200b_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _git_blob(path: Path) -> str:
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _require(path: Path, *fragments: str) -> None:
    text = _text(path)
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"PASS200B_SOURCE_BOUNDARY_DRIFT:{path}:{fragment}")


def pass200b_membrane_source_evidence() -> Dict[str, Any]:
    if _git("merge-base", "--is-ancestor", ACCEPTED_MERGE, "HEAD") != "":
        raise RuntimeError("PASS200B_ACCEPTED_MERGE_ANCESTRY_OUTPUT")
    evidence_merge_base = _git("merge-base", EVIDENCE_HEAD, "HEAD")
    if evidence_merge_base != PRIMARY_BASE:
        raise RuntimeError(f"PASS200B_SQUASH_LINEAGE_DRIFT:{evidence_merge_base}")

    for path, expected in HISTORICAL_BLOBS.items():
        historical = _git("rev-parse", f"{ACCEPTED_MERGE}:{path}")
        if historical != expected:
            raise RuntimeError(f"PASS200B_HISTORICAL_BLOB_DRIFT:{path}:{historical}")
        current = _git_blob(path)
        if current != expected:
            raise RuntimeError(f"PASS200B_FROZEN_I124_BLOB_DRIFT:{path}:{current}")

    _require(
        CONTRACT_PATH,
        "HHS-P200B-DUAL-APPROVAL-CANARY-ROLLBACK-VM81-H72",
        "Exactly two approvals are present",
        "one singleton VM81 activation receipt per canary frontier",
        "n MOD canary_denominator < canary_numerator",
        "selected\nAND exact_result_match\nAND witness_match\nAND replay_match",
        "candidate cannot authorize itself",
        "unrestricted active and frozen-constraint promotion remain disabled",
    )
    _require(
        RUNTIME_V1_PATH,
        "SINGLETON_CANARY_FRONTIER_ACTIVATED",
        "EXACT_CANARY_MISMATCH",
        "promotion approvals require two distinct principals",
        '"automatic_active_promotion": False',
        '"automatic_frozen_constraint_promotion": False',
    )
    _require(
        PRODUCTION_PATH,
        "Canonical production projection for Pass 200B governed canary admission",
        "Pass200BGovernedCanaryAuthority",
    )
    _require(
        CANARY_ROUTES_PATH,
        "runtime_controller.authorized_tick",
        "vm81:compiler-promotion-authority",
        "vm81:runtime-promotion-authority",
    )
    _require(
        WORKFLOW_PATH,
        "Run canary lifecycle, rollback, restart, and tamper tests",
        "Execute production proof, bounded canary, exhaustion, and rollback",
        "Reject floating-point canonical operations",
        "Verify authority, API, and visual wiring",
    )
    _require(
        VISUAL_PANEL_PATH,
        "The panel cannot manufacture approvals",
    )
    _require(
        RESTART_PATH,
        "Successful integrated run: `30775726043`",
        "Validated executable head: `f13eed02531e77737562b23fb207962c0744ed0d`",
        "ID: `8841987422`",
        "sha256:b95a8091ba8ce19301ee4b3a1ab51a994503940fe6293c752d24e63f22eb1cd8",
        "Candidate execution cannot approve or admit itself",
    )

    successor = pass200c_membrane_source_evidence()
    return {
        "primary_base": PRIMARY_BASE,
        "validated_executable_head": VALIDATED_EXECUTABLE_HEAD,
        "evidence_head": EVIDENCE_HEAD,
        "accepted_merge": ACCEPTED_MERGE,
        "frozen_i124": FROZEN_I124,
        "historical_blobs": {str(path): value for path, value in HISTORICAL_BLOBS.items()},
        "historical_closure": dict(HISTORICAL_CLOSURE),
        "canonical_successful_run": 30775726043,
        "receipt_updated_successful_run": 30776025874,
        "artifact_id": 8841987422,
        "artifact_digest": "sha256:b95a8091ba8ce19301ee4b3a1ab51a994503940fe6293c752d24e63f22eb1cd8",
        "pass200c_successor": successor,
    }


def validate_pass200b_squash_identity() -> Dict[str, Any]:
    s = pass200b_membrane_source_evidence()
    return {
        "ok": True,
        "pull_request": 139,
        "primary_base": s["primary_base"],
        "validated_executable_head": s["validated_executable_head"],
        "evidence_head": s["evidence_head"],
        "accepted_merge": s["accepted_merge"],
        "squash_aware": True,
        "historical_source_blobs_unchanged_at_frozen_i124": True,
    }


def validate_pass200b_pass200a_shadow_gate() -> Dict[str, Any]:
    s = pass200b_membrane_source_evidence()
    return {
        "ok": True,
        **s["historical_closure"],
        "pass200a_closed_proof_required": True,
        "compiler_candidate_required": True,
        "shadow_mode_required": True,
        "persisted_exact_shadow_match_required": True,
        "candidate_activation_before_canary": False,
    }


def validate_pass200b_dual_approval_and_activation() -> Dict[str, Any]:
    pass200b_membrane_source_evidence()
    return {
        "ok": True,
        "approval_count": 2,
        "required_capabilities": ["COMPILER_PROMOTION_APPROVE", "RUNTIME_PROMOTION_APPROVE"],
        "distinct_principals_required": True,
        "distinct_vm81_receipts_required": True,
        "bundle_frontier_expiry_receipt_binding": True,
        "separate_singleton_vm81_activation_receipt": True,
        "candidate_self_authorization": False,
    }


def validate_pass200b_bounded_exact_canary() -> Dict[str, Any]:
    pass200b_membrane_source_evidence()
    return {
        "ok": True,
        "max_invocation_limit": 64,
        "deterministic_integer_selection": True,
        "selection_rule": "n MOD canary_denominator < canary_numerator",
        "exact_result_required": True,
        "exact_witness_required": True,
        "exact_replay_required": True,
        "floating_point_canonical_operation": False,
        "automatic_active_promotion": False,
        "frozen_constraint_promotion": False,
    }


def validate_pass200b_persistence_and_rollback() -> Dict[str, Any]:
    pass200b_membrane_source_evidence()
    return {
        "ok": True,
        "inherited_durable_state": True,
        "inherited_hash72_event_history": True,
        "persisted_frontier_tamper_rejected": True,
        "event_chain_tamper_rejected": True,
        "mismatch_restores_reference": True,
        "expiry_restores_reference": True,
        "exhaustion_restores_reference": True,
        "explicit_rollback_restores_reference": True,
        "candidate_canonical_commit": False,
    }


def validate_pass200c_successor_binding() -> Dict[str, Any]:
    successor = pass200b_membrane_source_evidence()["pass200c_successor"]
    return {
        "ok": True,
        "successor_pass": 200,
        "successor_variant": "C",
        "successor_accepted_merge": successor["accepted_merge"],
        "successor_guarded_active_boundary_preserved": True,
        "successor_preserved": True,
    }


def validate_pass200b_no_new_authority() -> Dict[str, Any]:
    pass200b_membrane_source_evidence()
    return {
        "ok": True,
        "i125_new_canary_admission_authority": False,
        "i125_new_canonical_mutation_authority": False,
        "i125_new_persistence_authority": False,
        "i125_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
    }


def pass200b_surface_declaration() -> Dict[str, Any]:
    pass200b_membrane_source_evidence()
    return {
        "surface_id": PASS200B_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i125_pass200b",
        "symbol": "validate_pass200b_squash_identity",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P200B-DUAL-APPROVAL-CANARY-ROLLBACK-VM81-H72"],
        "witness_schemas": ["HHSExactPass200BGovernedCanaryWitnessV1", "HHSExactPass219InheritedPass200BBindingV1"],
        "validators": [PASS200B_BIND_SYMBOL, "validate_pass200b_squash_identity"],
        "guards": [
            "pass200b_squash_identity",
            "pass200b_immutable_source_identity",
            "pass200b_pass200a_shadow_gate",
            "pass200b_dual_approval_activation",
            "pass200b_bounded_integer_exact_comparison",
            "pass200b_reference_restoration",
            "pass200b_pass200c_successor_preserved",
        ],
        "rejection_codes": [
            "REJECT_PASS200B_SQUASH_IDENTITY_DRIFT",
            "REJECT_PASS200B_SOURCE_IDENTITY_DRIFT",
            "REJECT_PASS200B_PASS200A_GATE_DRIFT",
            "REJECT_PASS200B_APPROVAL_ACTIVATION_DRIFT",
            "REJECT_PASS200B_EXACT_CANARY_DRIFT",
            "REJECT_PASS200B_ROLLBACK_PERSISTENCE_DRIFT",
            "REJECT_PASS200B_PASS200C_SUCCESSOR_DRIFT",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_PASS200B_DURABLE_STATE_READ_ONLY_BINDING",
        "boundedness_policy": "PASS_200B_VERIFIED_GOVERNED_CANARY_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass200b_membrane_manifest() -> Dict[str, Any]:
    s = pass200b_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS200B_NUMBER,
        "pass_variant": PASS200B_VARIANT,
        "pass_id": "pass200b",
        "classification": PASS200B_CLASSIFICATION,
        "census_classification": PASS200B_CENSUS_CLASSIFICATION,
        "pass219_c_abi_surface": PASS200B_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass200BGovernedCanaryAdmission",
        "primary_pull_request": 139,
        "accepted_merge": s["accepted_merge"],
        "evidence_head": s["evidence_head"],
        "frozen_i124": s["frozen_i124"],
        "historical_squash_identity_bound": True,
        "immutable_source_identity_bound": True,
        "pass200a_shadow_gate_bound": True,
        "dual_approval_and_activation_bound": True,
        "bounded_integer_selection_bound": True,
        "exact_comparison_bound": True,
        "rollback_and_exhaustion_bound": True,
        "inherited_durable_state_read_only_bound": True,
        "pass200c_successor_bound": True,
        "pass219_new_canary_admission_authority": False,
        "pass219_new_canonical_mutation_authority": False,
        "pass219_new_persistence_authority": False,
        "pass219_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "historical_blobs": s["historical_blobs"],
        "historical_closure": s["historical_closure"],
        "surface": pass200b_surface_declaration(),
    }


def preflight_pass200b_membrane() -> Dict[str, Any]:
    declaration = pass200b_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    return {
        "schema": "HHS_PASS219_I125_PASS200B_MEMBRANE_PREFLIGHT_V1",
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS200B_SURFACE_ID,
        "operations": rows,
        "manifest": pass200b_membrane_manifest(),
    }


if __name__ == "__main__":
    print(json.dumps(preflight_pass200b_membrane(), indent=2, sort_keys=True))
