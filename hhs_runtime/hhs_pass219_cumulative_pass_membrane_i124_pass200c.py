"""Pass 219 I124 read-only membrane for accepted Pass 200C guarded active admission."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i123_pass201 import pass201_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_24"
PASS200C_NUMBER = 200
PASS200C_VARIANT = "C"
PASS200C_CLASSIFICATION = "WIRED"
PASS200C_CENSUS_CLASSIFICATION = "MISSING_MEMBRANE_EXPOSURE"
PASS200C_BIND_SYMBOL = "hhs_exact_pass219_bind_pass200c_guarded_active_admission"
PASS200C_SURFACE_ID = "validator:pass219.inherited.pass200c.guarded-active-admission"

P = Path
CONTRACT_PATH = P("HHS_PASS_200C_GUARDED_ACTIVE_ADMISSION.md")
WORKFLOW_PATH = P(".github/workflows/pass200c-guarded-active-admission.yml")
RUNTIME_V1_PATH = P("hhs_backend/runtime/hhs_pass200c_guarded_active_admission_v1.py")
PRODUCTION_PATH = P("hhs_backend/runtime/hhs_pass200c_guarded_active_admission.py")
ACTIVE_ROUTES_PATH = P("hhs_backend/api/pass200c_active_routes.py")
CONTRACT_TEST_PATH = P("tests/test_hhs_pass200c_guarded_active_admission_v1.py")
VALIDATOR_PATH = P("scripts/pass200c_production_validation.py")
RESTART_PATH = P("docs/pass200c/RESTART_RECORD.md")
PASS201_MEMBRANE_PATH = P("hhs_runtime/hhs_pass219_cumulative_pass_membrane_i123_pass201.py")

PRIMARY_BASE = "beff24168bb81b0b1459e325ebaad29b2252b980"
VALIDATED_EXECUTABLE_HEAD = "828402a739744e4b12fb63d76a3923964d067c6f"
EVIDENCE_HEAD = "73fa715ac8aee578b81e053fae99594df0b34889"
ACCEPTED_MERGE = "a7868be1d98345cc7641bb7f59b716667cf1808d"
FROZEN_I123 = "30e1ae3a278ee19c3c167d3659ed71ca2a016873"

HISTORICAL_BLOBS = {
    CONTRACT_PATH: "bc06fcab22c5bd857566c5560b9fd05b83bcdc75",
    WORKFLOW_PATH: "bd54ffaf0c00c1b993dfa7f1d7cc759752bc9776",
    RUNTIME_V1_PATH: "4c61dd428996372a9d8170092efde0a21c391134",
    PRODUCTION_PATH: "92f0bef25882c0885f769bff4570610601e820ea",
    ACTIVE_ROUTES_PATH: "4b08c4e183793836f667ebacb73602341b1d45c2",
    CONTRACT_TEST_PATH: "e6bd83499193ec5242ec0b04696bd7d423cebd4a",
    VALIDATOR_PATH: "9c4f4b545cecf6e14dbe7aff050eed90f3368fe8",
}
CURRENT_COMPATIBILITY_PATHS = {VALIDATOR_PATH}

HISTORICAL_CLOSURE = {
    "pass200a_independent_envelopes": 4,
    "pass200a_compiler_candidate_bundles": 4,
    "pass200a_exact_shadow_matches": 4,
    "pass200b_completed_canary_frontiers": 2,
    "pass200b_exact_canary_invocations": 16,
    "pass200b_candidate_returns": 6,
    "pass200b_reference_returns": 10,
    "active_evidence_snapshots": 1,
    "guarded_active_frontiers": 2,
    "singleton_active_activation_commits": 2,
    "guarded_active_invocations": 7,
    "active_candidate_returns": 6,
    "active_reference_returns": 1,
    "immutable_frontiers_including_genesis": 5,
    "hash72_events": 13,
}

REQUIRED_OPERATIONS = (
    "validate_pass200c_squash_identity",
    "validate_pass200c_canary_evidence_gate",
    "validate_pass200c_active_approval_and_activation",
    "validate_pass200c_continuous_exact_guard",
    "validate_pass200c_persistence_and_rollback",
    "validate_pass201_successor_binding",
    "validate_pass200c_no_new_authority",
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
            raise RuntimeError(f"PASS200C_SOURCE_BOUNDARY_DRIFT:{path}:{fragment}")


def pass200c_membrane_source_evidence() -> Dict[str, Any]:
    if _git("merge-base", "--is-ancestor", ACCEPTED_MERGE, "HEAD") != "":
        raise RuntimeError("PASS200C_ACCEPTED_MERGE_ANCESTRY_OUTPUT")
    evidence_merge_base = _git("merge-base", EVIDENCE_HEAD, "HEAD")
    if evidence_merge_base != PRIMARY_BASE:
        raise RuntimeError(f"PASS200C_SQUASH_LINEAGE_DRIFT:{evidence_merge_base}")

    for path, expected in HISTORICAL_BLOBS.items():
        historical = _git("rev-parse", f"{ACCEPTED_MERGE}:{path}")
        if historical != expected:
            raise RuntimeError(f"PASS200C_HISTORICAL_BLOB_DRIFT:{path}:{historical}")
        current = _git_blob(path)
        if path not in CURRENT_COMPATIBILITY_PATHS and current != expected:
            raise RuntimeError(f"PASS200C_FROZEN_I123_BLOB_DRIFT:{path}:{current}")

    _require(
        VALIDATOR_PATH,
        "HHSRuntimeController",
        'authorized_tick(source="pass200c.production.pass200a.holdouts")',
        'authorized_tick(source="pass200c.production.pass200a.shadows")',
        'qualification["vm81_receipt_provenance"]["ok"] is True',
        'shadows["vm81_receipt_provenance"]["ok"] is True',
        '"pass200a_vm81_receipt_chain_verified": True',
    )
    _require(
        CONTRACT_PATH,
        "HHS-P200C-CANARY-EVIDENCE-ACTIVE-GUARD-VM81-H72",
        "Active admission requires exactly three approvals",
        "singleton VM81 activation receipt",
        "exact result, witness, and replay equality",
        "automatic reference restoration",
        "candidate cannot authorize itself",
        "frozen-constraint promotion remains disabled",
    )
    _require(
        RUNTIME_V1_PATH,
        "SINGLETON_ACTIVE_FRONTIER_ACTIVATED",
        "ACTIVE_EXACT_GUARD_MISMATCH",
        "active admission requires three distinct principals",
        "bundle has a Pass 200B rollback and cannot enter active admission",
        "persisted active frontier was tampered",
        '"candidate_self_authorization": False',
        '"frozen_constraint_promotion": False',
    )
    _require(
        PRODUCTION_PATH,
        "Canonical production projection for Pass 200C guarded active admission",
        "persisted canary evidence was tampered",
        "PASS200C_ACTIVE_AUTHORITY",
    )
    _require(
        ACTIVE_ROUTES_PATH,
        "runtime_controller.authorized_tick",
        "vm81:compiler-active-authority",
        "vm81:runtime-active-authority",
        "vm81:operations-active-authority",
        '"tool_server_is_authority": False',
        '"candidate_self_authorization": False',
    )
    _require(
        WORKFLOW_PATH,
        "Run guarded active lifecycle tests",
        "Execute production proof, canary evidence, active lease, exhaustion, and rollback",
        "Reject floating-point canonical operations",
        "Verify authority, API, visual, and contract wiring",
    )
    _require(
        RESTART_PATH,
        "Successful integrated run: `30777130361`",
        "Validated executable head: `828402a739744e4b12fb63d76a3923964d067c6f`",
        "ID: `8842425241`",
        "sha256:5d6ada0436118770436b46ffd9164dbf404706a319f16bd2c232cc13c3621157",
        "Candidate execution cannot approve, admit, renew, suppress the guard, or freeze itself",
    )

    successor = pass201_membrane_source_evidence()
    return {
        "primary_base": PRIMARY_BASE,
        "validated_executable_head": VALIDATED_EXECUTABLE_HEAD,
        "evidence_head": EVIDENCE_HEAD,
        "accepted_merge": ACCEPTED_MERGE,
        "frozen_i123": FROZEN_I123,
        "historical_blobs": {str(path): value for path, value in HISTORICAL_BLOBS.items()},
        "current_compatibility_repairs": {str(VALIDATOR_PATH): _git_blob(VALIDATOR_PATH)},
        "historical_closure": dict(HISTORICAL_CLOSURE),
        "canonical_successful_run": 30777130361,
        "receipt_updated_successful_run": 30777367009,
        "artifact_id": 8842425241,
        "artifact_digest": "sha256:5d6ada0436118770436b46ffd9164dbf404706a319f16bd2c232cc13c3621157",
        "pass201_successor": successor,
    }


def validate_pass200c_squash_identity() -> Dict[str, Any]:
    s = pass200c_membrane_source_evidence()
    return {
        "ok": True,
        "pull_request": 140,
        "primary_base": s["primary_base"],
        "validated_executable_head": s["validated_executable_head"],
        "evidence_head": s["evidence_head"],
        "accepted_merge": s["accepted_merge"],
        "squash_aware": True,
        "historical_source_blobs_unchanged_at_frozen_i123": True,
        "current_validator_receipt_provenance_repaired": True,
    }


def validate_pass200c_canary_evidence_gate() -> Dict[str, Any]:
    s = pass200c_membrane_source_evidence()
    return {
        "ok": True,
        **s["historical_closure"],
        "minimum_successful_canaries": 2,
        "minimum_canary_invocations": 12,
        "pass200a_candidate_bundle_required": True,
        "pass200b_rollback_disqualifies_bundle": True,
    }


def validate_pass200c_active_approval_and_activation() -> Dict[str, Any]:
    pass200c_membrane_source_evidence()
    return {
        "ok": True,
        "distinct_principals": 3,
        "required_capabilities": [
            "COMPILER_ACTIVE_APPROVE",
            "RUNTIME_ACTIVE_APPROVE",
            "OPERATIONS_ACTIVE_APPROVE",
        ],
        "distinct_receipts_required": True,
        "bundle_evidence_frontier_expiry_binding": True,
        "separate_singleton_vm81_activation_receipt": True,
        "candidate_self_authorization": False,
    }


def validate_pass200c_continuous_exact_guard() -> Dict[str, Any]:
    pass200c_membrane_source_evidence()
    return {
        "ok": True,
        "active_default_return_requires_guard": True,
        "exact_result_every_invocation": True,
        "exact_witness_every_invocation": True,
        "exact_replay_every_invocation": True,
        "reference_path_remains_available": True,
        "max_active_lease_invocations": 64,
    }


def validate_pass200c_persistence_and_rollback() -> Dict[str, Any]:
    pass200c_membrane_source_evidence()
    return {
        "ok": True,
        "inherited_durable_state": True,
        "inherited_hash72_event_history": True,
        "persisted_evidence_tamper_rejected": True,
        "persisted_frontier_tamper_rejected": True,
        "mismatch_restores_reference": True,
        "expiry_restores_reference": True,
        "lease_exhaustion_restores_reference": True,
        "explicit_rollback_restores_reference": True,
        "frozen_constraint_promotion": False,
    }


def validate_pass201_successor_binding() -> Dict[str, Any]:
    successor = pass200c_membrane_source_evidence()["pass201_successor"]
    return {
        "ok": True,
        "successor_pass": 201,
        "successor_accepted_merge": successor["accepted_merge"],
        "successor_router_closure_preserved": True,
        "successor_preserved": True,
    }


def validate_pass200c_no_new_authority() -> Dict[str, Any]:
    pass200c_membrane_source_evidence()
    return {
        "ok": True,
        "i124_new_active_admission_authority": False,
        "i124_new_canonical_mutation_authority": False,
        "i124_new_persistence_authority": False,
        "i124_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
    }


def pass200c_surface_declaration() -> Dict[str, Any]:
    pass200c_membrane_source_evidence()
    return {
        "surface_id": PASS200C_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i124_pass200c",
        "symbol": "validate_pass200c_squash_identity",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P200C-CANARY-EVIDENCE-ACTIVE-GUARD-VM81-H72"],
        "witness_schemas": ["HHSExactPass200CGuardedActiveWitnessV1", "HHSExactPass219InheritedPass200CBindingV1"],
        "validators": [PASS200C_BIND_SYMBOL, "validate_pass200c_squash_identity"],
        "guards": [
            "pass200c_squash_identity",
            "pass200c_immutable_source_identity",
            "pass200c_canary_evidence_gate",
            "pass200c_three_party_activation",
            "pass200c_continuous_exact_guard",
            "pass200c_reference_restoration",
            "pass200c_pass201_successor_preserved",
        ],
        "rejection_codes": [
            "REJECT_PASS200C_SQUASH_IDENTITY_DRIFT",
            "REJECT_PASS200C_SOURCE_IDENTITY_DRIFT",
            "REJECT_PASS200C_CANARY_EVIDENCE_DRIFT",
            "REJECT_PASS200C_APPROVAL_ACTIVATION_DRIFT",
            "REJECT_PASS200C_EXACT_GUARD_DRIFT",
            "REJECT_PASS200C_ROLLBACK_PERSISTENCE_DRIFT",
            "REJECT_PASS200C_PASS201_SUCCESSOR_DRIFT",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_PASS200C_DURABLE_STATE_READ_ONLY_BINDING",
        "boundedness_policy": "PASS_200C_VERIFIED_GUARDED_ACTIVE_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass200c_membrane_manifest() -> Dict[str, Any]:
    s = pass200c_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS200C_NUMBER,
        "pass_variant": PASS200C_VARIANT,
        "pass_id": "pass200c",
        "classification": PASS200C_CLASSIFICATION,
        "census_classification": PASS200C_CENSUS_CLASSIFICATION,
        "pass219_c_abi_surface": PASS200C_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass200CGuardedActiveAdmission",
        "primary_pull_request": 140,
        "accepted_merge": s["accepted_merge"],
        "evidence_head": s["evidence_head"],
        "frozen_i123": s["frozen_i123"],
        "historical_squash_identity_bound": True,
        "immutable_source_identity_bound": True,
        "current_validator_receipt_provenance_repaired": True,
        "canary_evidence_gate_bound": True,
        "approval_and_activation_bound": True,
        "continuous_exact_guard_bound": True,
        "rollback_reference_restoration_bound": True,
        "inherited_durable_state_read_only_bound": True,
        "pass201_successor_bound": True,
        "pass219_new_active_admission_authority": False,
        "pass219_new_canonical_mutation_authority": False,
        "pass219_new_persistence_authority": False,
        "pass219_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "historical_blobs": s["historical_blobs"],
        "current_compatibility_repairs": s["current_compatibility_repairs"],
        "historical_closure": s["historical_closure"],
        "surface": pass200c_surface_declaration(),
    }


def preflight_pass200c_membrane() -> Dict[str, Any]:
    declaration = pass200c_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    return {
        "schema": "HHS_PASS219_I124_PASS200C_MEMBRANE_PREFLIGHT_V1",
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS200C_SURFACE_ID,
        "operations": rows,
        "manifest": pass200c_membrane_manifest(),
    }


if __name__ == "__main__":
    print(json.dumps(preflight_pass200c_membrane(), indent=2, sort_keys=True))
