"""Pass 219 I122 read-only membrane for accepted Pass 202 guarded deployment."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i116 import ROOT
from hhs_runtime.hhs_pass219_cumulative_pass_membrane_i121_pass203 import pass203_membrane_source_evidence

VERSION = "PASS_219_CUMULATIVE_PASS_MEMBRANE_1_22"
PASS202_NUMBER = 202
PASS202_CLASSIFICATION = "WIRED"
PASS202_CENSUS_CLASSIFICATION = "MISSING_MEMBRANE_EXPOSURE"
PASS202_BIND_SYMBOL = "hhs_exact_pass219_bind_pass202_guarded_deployment"
PASS202_SURFACE_ID = "validator:pass219.inherited.pass202.guarded-deployment"

P = Path
SPEC_PATH = P("docs/pass202/HHS_PASS_202_GUARDED_CONTINUOUS_INTEGRATION_DEPLOYMENT.md")
RESTART_PATH = P("docs/pass202/RESTART_RECORD.md")
WORKFLOW_PATH = P(".github/workflows/guarded-continuous-integration.yml")
UPDATER_PATH = P("deployment/digitalocean/guarded_auto_update/hhs-guarded-update.sh")
ENV_PATH = P("deployment/digitalocean/guarded_auto_update/hhs-guarded-update.env.example")
INSTALLER_PATH = P("deployment/digitalocean/guarded_auto_update/install.sh")
SERVICE_PATH = P("deployment/digitalocean/guarded_auto_update/hhs-guarded-update.service")
TIMER_PATH = P("deployment/digitalocean/guarded_auto_update/hhs-guarded-update.timer")
VALIDATOR_PATH = P("deployment/digitalocean/guarded_auto_update/validate-candidate.sh")
BUNDLE_PATH = P("deployment/digitalocean/guarded_auto_update/runtime-os-bundle.py")
DRIFT_PATH = P("deployment/digitalocean/guarded_auto_update/preserve-host-drift.sh")
CONTRACT_TEST_PATH = P("tests/test_hhs_guarded_auto_update_contract_v1.py")
PASS203_WORKFLOW_PATH = P(".github/workflows/pass203-hydrated-mainframe.yml")

PRIMARY_BASE = "bdf19276b0974481bd69d70ca1154f284f238e48"
PRIMARY_HEAD = "1eb9326f8024b37b9fc1425d910bc20cae50abbb"
PRIMARY_MERGE = "33ce89c7328180eb98d59f72df43f3036cf1edab"
BOOTSTRAP_HEAD = "8a8f1eaefa940f9416430f2746014e1716ddd23b"
BOOTSTRAP_MERGE = "83b6fd89cd8adb1962aeb159917fe24ee4485441"
FROZEN_I121 = "94a100766c582c83fa3e4f7cb815c08b0eacfa1a"

HISTORICAL_BLOBS = {
    str(WORKFLOW_PATH): "e6b4e7c7cda8a64ef59151eae0e33ff1a70c6cd4",
    str(UPDATER_PATH): "b1ad8ced814c8c58d3365c4f45cbb0cd338fb564",
    str(ENV_PATH): "2cf1d20f60d26d1b476ebd268fdc85b1db1a0764",
    str(INSTALLER_PATH): "97ab585e3e96122cbaded47e1a436fc0e143bac1",
    str(SERVICE_PATH): "1cc1dce920213df7c0a5f1ee4e9823a9dc727ec5",
    str(TIMER_PATH): "3296ee9787544542697d3915e01569562ef30046",
    str(VALIDATOR_PATH): "82250c50fa9d20a82d0b957d2637398760b1c416",
    str(CONTRACT_TEST_PATH): "709afe1c0d612ad91744a5cd71cb87d8a313aad6",
}

FROZEN_I121_BLOBS = {
    WORKFLOW_PATH: "e6b4e7c7cda8a64ef59151eae0e33ff1a70c6cd4",
    SPEC_PATH: "a0634353e26c186bc72e887bd1bbc6bdc5db42c3",
    SERVICE_PATH: "1cc1dce920213df7c0a5f1ee4e9823a9dc727ec5",
    TIMER_PATH: "3296ee9787544542697d3915e01569562ef30046",
    UPDATER_PATH: "c1815c56e5bceeca2a840c5a693bd22d6e85ef84",
    ENV_PATH: "7890657593b5d4dd03e4cf5eb2c4c1c7ba25e519",
    INSTALLER_PATH: "93dfbe6cc3a789de82b5249f32a129a31306aeb5",
    VALIDATOR_PATH: "729d8e571160239094aaef612a17d039f310ca03",
    BUNDLE_PATH: "23afbf9c99d77f57acd7334d767c483572d64e0a",
}

REQUIRED_OPERATIONS = (
    "validate_pass202_historical_identity",
    "validate_pass202_guarded_ci_gate",
    "validate_pass202_deployment_transition",
    "validate_pass202_dry_run_bootstrap",
    "validate_pass202_successor_hardening",
    "validate_pass203_successor_binding",
    "validate_pass202_no_new_authority",
)


def _text(path: Path) -> str:
    return (ROOT / path).read_text("utf-8")


def _git_blob(path: Path) -> str:
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _require(path: Path, *fragments: str) -> None:
    text = _text(path)
    for fragment in fragments:
        if fragment not in text:
            raise RuntimeError(f"PASS202_SOURCE_BOUNDARY_DRIFT:{path}:{fragment}")


def pass202_membrane_source_evidence() -> Dict[str, Any]:
    for path, expected in FROZEN_I121_BLOBS.items():
        actual = _git_blob(path)
        if actual != expected:
            raise RuntimeError(f"PASS202_FROZEN_I121_BLOB_DRIFT:{path}:{actual}")

    _require(
        SPEC_PATH,
        "HHS-P202-GCI-DOD-FFP-RB-HC-RCP",
        "main` is the only production source branch",
        "detached worktree before service interruption",
        "git merge --ff-only",
        "rollback to the exact previous commit",
        "JSONL receipt",
        "Host-local modifications block automation",
        "live promotion is enabled only after the dry run",
    )
    _require(
        WORKFLOW_PATH,
        "hhs-automerge",
        "head.repo.full_name == github.repository",
        '"OWNER","MEMBER","COLLABORATOR"',
        "validate-candidate.sh",
        "gh pr merge",
        "--merge --delete-branch",
    )
    _require(
        UPDATER_PATH,
        "HHS_EXPECTED_REPOSITORY",
        "flock -n",
        "merge-base --is-ancestor",
        "merge --ff-only",
        "rollback_live_checkout",
        "wait_for_health",
        "receipts.jsonl",
        "reconcile_host_drift source",
        "reconcile_host_drift final",
        "require_candidate_bundle",
        "activate_candidate_runtime_os",
        "restore_previous_runtime_os",
        "HHS_UPDATE_DRY_RUN",
    )
    _require(
        ENV_PATH,
        "HHS_GIT_BRANCH=main",
        "HHS_EXPECTED_REPOSITORY=danonbrez/Holofractal_Harmonicode",
        "HHS_RUNTIME_OS_BUNDLE_MODE=prebuilt",
        "HHS_UPDATE_DRY_RUN=1",
    )
    _require(
        INSTALLER_PATH,
        'ENABLE_PROMOTION=${HHS_INSTALL_ENABLE_PROMOTION:-0}',
        "promotion requires exact HHS_RUNTIME_OS_BUNDLE_SHA",
        "HHS_UPDATE_DRY_RUN=1",
        "HHS_UPDATE_DRY_RUN=0",
        "HHS_INSTALL_RECOVERY_MODE",
        "ROLLBACK_HEALTH_FAILED",
        "systemctl stop hhs-guarded-update.timer",
        "systemctl start hhs-guarded-update.service",
    )
    _require(SERVICE_PATH, "Type=oneshot", "NoNewPrivileges=true", "TimeoutStartSec=90min")
    _require(TIMER_PATH, "OnUnitActiveSec=5min", "RandomizedDelaySec=30s")
    _require(
        VALIDATOR_PATH,
        "HHS_RUNTIME_OS_BUNDLE_MODE",
        "runtime-os-bundle.py",
        "hhs_backend.runtime_os_application_server:app",
        "/api/system/status",
        "/api/runtime/workspace/session",
    )
    _require(DRIFT_PATH, "HHS_HOST_DRIFT_MODE", "host_edits_preserved_before_reset")
    _require(BUNDLE_PATH, "repository_sha", "expected-sha", "activate", "restore")
    _require(
        CONTRACT_TEST_PATH,
        "test_updater_is_fail_closed_fast_forward_only_drift_preserving_and_bundle_atomic",
        "test_installer_pins_prebuilt_bundle_and_repairs_failed_service_only_by_receipt",
        "HHS_UPDATE_DRY_RUN=1",
    )
    _require(PASS203_WORKFLOW_PATH, "Run inherited Pass 202 guarded deployment contract tests")

    successor = pass203_membrane_source_evidence()
    return {
        "primary_base": PRIMARY_BASE,
        "primary_head": PRIMARY_HEAD,
        "primary_merge": PRIMARY_MERGE,
        "bootstrap_head": BOOTSTRAP_HEAD,
        "bootstrap_merge": BOOTSTRAP_MERGE,
        "frozen_i121": FROZEN_I121,
        "historical_blobs": dict(HISTORICAL_BLOBS),
        "frozen_i121_blobs": {str(path): value for path, value in FROZEN_I121_BLOBS.items()},
        "pass203_successor": successor,
    }


def validate_pass202_historical_identity() -> Dict[str, Any]:
    s = pass202_membrane_source_evidence()
    return {
        "ok": True,
        "primary_pull_request": 143,
        "bootstrap_pull_request": 144,
        "primary_base": s["primary_base"],
        "primary_head": s["primary_head"],
        "primary_merge": s["primary_merge"],
        "bootstrap_head": s["bootstrap_head"],
        "bootstrap_merge": s["bootstrap_merge"],
        "initial_contract_test_count": 5,
        "bootstrap_contract_test_count": 6,
    }


def validate_pass202_guarded_ci_gate() -> Dict[str, Any]:
    pass202_membrane_source_evidence()
    return {
        "ok": True,
        "production_source_branch": "main",
        "trusted_label": "hhs-automerge",
        "same_repository_required": True,
        "trusted_author_association_required": True,
        "candidate_validation_before_merge": True,
    }


def validate_pass202_deployment_transition() -> Dict[str, Any]:
    pass202_membrane_source_evidence()
    return {
        "ok": True,
        "detached_candidate_validation": True,
        "fast_forward_only": True,
        "post_promotion_health_required": True,
        "rollback_to_exact_previous_commit": True,
        "durable_jsonl_receipts": True,
        "bounded_singleton_timer": True,
    }


def validate_pass202_dry_run_bootstrap() -> Dict[str, Any]:
    pass202_membrane_source_evidence()
    return {
        "ok": True,
        "environment_default_dry_run": True,
        "install_promotion_default_disabled": True,
        "explicit_operator_enable_required": True,
    }


def validate_pass202_successor_hardening() -> Dict[str, Any]:
    pass202_membrane_source_evidence()
    return {
        "ok": True,
        "historical_host_drift_blocked": True,
        "current_host_drift_preserved_and_reconciled": True,
        "runtime_os_bundle_sha_bound": True,
        "production_bundle_mode": "prebuilt",
        "exclusive_updater_ownership": True,
        "recovery_receipt_gated": True,
    }


def validate_pass203_successor_binding() -> Dict[str, Any]:
    successor = pass202_membrane_source_evidence()["pass203_successor"]
    return {
        "ok": True,
        "successor_pass": 203,
        "successor_merge_commit": successor["merge_commit"],
        "successor_pass202_inheritance_verified": True,
    }


def validate_pass202_no_new_authority() -> Dict[str, Any]:
    pass202_membrane_source_evidence()
    return {
        "ok": True,
        "i122_new_deployment_authority": False,
        "i122_new_canonical_mutation_authority": False,
        "i122_new_persistence_authority": False,
        "i122_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
    }


def pass202_surface_declaration() -> Dict[str, Any]:
    pass202_membrane_source_evidence()
    return {
        "surface_id": PASS202_SURFACE_ID,
        "surface_type": "VALIDATOR",
        "module": "hhs_runtime.hhs_pass219_cumulative_pass_membrane_i122_pass202",
        "symbol": "validate_pass202_historical_identity",
        "invariant_ids": ["HHS-I005", "HHS-I006", "HHS-I011", "HHS-I012", "HHS-I014"],
        "contract_schemas": ["HHS-P202-GCI-DOD-FFP-RB-HC-RCP"],
        "witness_schemas": ["HHSExactPass202GuardedDeploymentWitnessV1", "HHSExactPass219InheritedPass202BindingV1"],
        "validators": [PASS202_BIND_SYMBOL, "validate_pass202_historical_identity"],
        "guards": [
            "pass202_historical_pr_identity",
            "pass202_trusted_ci_gate_preserved",
            "pass202_fast_forward_rollback_receipt_boundary",
            "pass202_dry_run_bootstrap_preserved",
            "pass202_successor_deployment_hardening_preserved",
            "pass202_pass203_successor_preserved",
        ],
        "rejection_codes": [
            "REJECT_PASS202_HISTORICAL_IDENTITY_DRIFT",
            "REJECT_PASS202_GUARDED_CI_DRIFT",
            "REJECT_PASS202_DEPLOYMENT_TRANSITION_DRIFT",
            "REJECT_PASS202_DRY_RUN_BOOTSTRAP_DRIFT",
            "REJECT_PASS202_SUCCESSOR_HARDENING_DRIFT",
            "REJECT_PASS202_PASS203_SUCCESSOR_DRIFT",
        ],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
        "persistence_policy": "INHERITED_PASS202_DEPLOYMENT_STATE_READ_ONLY_BINDING",
        "boundedness_policy": "PASS_202_VERIFIED_DEPLOYMENT_EXPOSURE_ONLY",
        "declared_operations": list(REQUIRED_OPERATIONS),
    }


def pass202_membrane_manifest() -> Dict[str, Any]:
    s = pass202_membrane_source_evidence()
    return {
        "schema": "HHS_PASS219_CUMULATIVE_PASS_MEMBRANE_ENTRY_V1",
        "version": VERSION,
        "pass_number": PASS202_NUMBER,
        "classification": PASS202_CLASSIFICATION,
        "census_classification": PASS202_CENSUS_CLASSIFICATION,
        "pass219_c_abi_surface": PASS202_BIND_SYMBOL,
        "pass219_cpp_class": "hhs::rna::InheritedPass202GuardedDeployment",
        "primary_pull_request": 143,
        "bootstrap_pull_request": 144,
        "bootstrap_dry_run_bound": True,
        "fast_forward_only_bound": True,
        "rollback_and_health_bound": True,
        "durable_receipt_boundary_bound": True,
        "successor_hardening_bound": True,
        "pass203_successor_bound": True,
        "pass219_new_deployment_authority": False,
        "pass219_new_canonical_mutation_authority": False,
        "pass219_new_persistence_authority": False,
        "pass219_new_hash72_clock": False,
        "cxx_mutation_authority": False,
        "vm81_mutation_authority": False,
        "primary_merge": s["primary_merge"],
        "bootstrap_merge": s["bootstrap_merge"],
        "frozen_i121": s["frozen_i121"],
        "historical_blobs": s["historical_blobs"],
        "frozen_i121_blobs": s["frozen_i121_blobs"],
        "surface": pass202_surface_declaration(),
    }


def preflight_pass202_membrane() -> Dict[str, Any]:
    declaration = pass202_surface_declaration()
    rows = [execute_surface_preflight(declaration, operation=operation) for operation in REQUIRED_OPERATIONS]
    return {
        "schema": "HHS_PASS219_I122_PASS202_MEMBRANE_PREFLIGHT_V1",
        "ok": all(row.get("ok") is True for row in rows),
        "surface_id": PASS202_SURFACE_ID,
        "operations": rows,
        "manifest": pass202_membrane_manifest(),
    }


if __name__ == "__main__":
    print(json.dumps(preflight_pass202_membrane(), indent=2, sort_keys=True))
