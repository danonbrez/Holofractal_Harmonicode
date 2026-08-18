from __future__ import annotations

import copy
import json
import pathlib

from hhs_runtime.hhs_pass206_cumulative_enforcement_v1 import (
    APPROVED_REPAIR_MERGE,
    APPROVED_REPAIR_VALIDATED_HEAD,
    APPROVED_REPAIR_JOB,
    APPROVED_REPAIR_RUN,
    APPROVED_RUNTIME_ABI_BLOB,
    BASELINE,
    _core_identity_reasons,
    _static_contract_reasons,
    _successor_reasons,
    validate_pass206_enforcement,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_pass206_enforcement_accepts_exact_current_lineage() -> None:
    decision = validate_pass206_enforcement(ROOT)
    assert decision["ok"] is True, decision
    assert decision["status"] == "ADMIT_PASS206_CUMULATIVE_ENFORCEMENT"
    assert decision["grounding_baseline"] == BASELINE
    assert decision["approved_repair_merge"] == APPROVED_REPAIR_MERGE
    assert decision["frozen_core_count"] == 10
    assert decision["approved_successor_count"] == 1
    assert decision["pass206_changed_frozen_core_paths"] == []
    assert decision["canonical_mutation_authority"] == "VM81_KERNEL"
    assert decision["canonical_mutation_authority_count"] == 1
    assert decision["canonical_hash72_commit_stream_count"] == 1
    assert decision["pass206_new_mutation_authority"] is False
    assert decision["pass206_new_persistence_authority"] is False
    assert decision["pass206_new_hash72_clock"] is False
    assert all(row["ok"] is True for row in decision["checks"])


def test_pass206_contract_rejects_second_canonical_authority() -> None:
    contract = load("contracts/pass206/PASS_206_CONTRACT.json")
    broken = copy.deepcopy(contract)
    broken["authority"]["canonical_mutation_authority_count"] = 2
    reasons = _static_contract_reasons(broken)
    assert "CANONICAL_MUTATION_AUTHORITY_COUNT_MISMATCH" in reasons


def test_pass206_contract_rejects_hash216_mutation_authority() -> None:
    contract = load("contracts/pass206/PASS_206_CONTRACT.json")
    broken = copy.deepcopy(contract)
    broken["hash216_authorizes_original_transformation"] = True
    reasons = _static_contract_reasons(broken)
    assert "HASH216_MUTATION_AUTHORITY_FORBIDDEN" in reasons


def test_pass206_contract_rejects_receipt_reordering() -> None:
    contract = load("contracts/pass206/PASS_206_CONTRACT.json")
    broken = copy.deepcopy(contract)
    broken["receipt_archival_order"] = list(reversed(broken["receipt_archival_order"]))
    reasons = _static_contract_reasons(broken)
    assert "RECEIPT_ARCHIVAL_ORDER_MISMATCH" in reasons


def test_pass206_core_rejects_unapproved_drift() -> None:
    freeze = load("artifacts/pass206/CORE_FUNCTION_FREEZE_MANIFEST.json")
    lineage = load("artifacts/pass206/CORE_SUCCESSOR_REPAIR_LINEAGE.json")
    entries = freeze["entries"]
    baseline_blobs = {row["repository_path"]: row["git_blob"] for row in entries}
    current_blobs = dict(baseline_blobs)
    baseline_hashes = {row["repository_path"]: row["file_sha256"] for row in entries}
    current_blobs["hhs_runtime/c/hhs_runtime_abi.c"] = APPROVED_RUNTIME_ABI_BLOB
    victim = "hhs_runtime/include/hhs_receipt.h"
    current_blobs[victim] = "0" * 40
    reasons = _core_identity_reasons(
        freeze,
        lineage,
        baseline_blobs,
        current_blobs,
        baseline_hashes,
        repair_ancestral=True,
        pass206_changed_paths=(),
    )
    assert f"UNAPPROVED_CORE_DRIFT:{victim}" in reasons


def test_pass206_core_rejects_missing_repair_ancestry() -> None:
    freeze = load("artifacts/pass206/CORE_FUNCTION_FREEZE_MANIFEST.json")
    lineage = load("artifacts/pass206/CORE_SUCCESSOR_REPAIR_LINEAGE.json")
    entries = freeze["entries"]
    baseline_blobs = {row["repository_path"]: row["git_blob"] for row in entries}
    current_blobs = dict(baseline_blobs)
    baseline_hashes = {row["repository_path"]: row["file_sha256"] for row in entries}
    current_blobs["hhs_runtime/c/hhs_runtime_abi.c"] = APPROVED_RUNTIME_ABI_BLOB
    reasons = _core_identity_reasons(
        freeze,
        lineage,
        baseline_blobs,
        current_blobs,
        baseline_hashes,
        repair_ancestral=False,
        pass206_changed_paths=(),
    )
    assert "APPROVED_REPAIR_NOT_ANCESTRAL" in reasons


def test_pass206_core_rejects_pass206_touching_frozen_core() -> None:
    freeze = load("artifacts/pass206/CORE_FUNCTION_FREEZE_MANIFEST.json")
    lineage = load("artifacts/pass206/CORE_SUCCESSOR_REPAIR_LINEAGE.json")
    entries = freeze["entries"]
    baseline_blobs = {row["repository_path"]: row["git_blob"] for row in entries}
    current_blobs = dict(baseline_blobs)
    baseline_hashes = {row["repository_path"]: row["file_sha256"] for row in entries}
    current_blobs["hhs_runtime/c/hhs_runtime_abi.c"] = APPROVED_RUNTIME_ABI_BLOB
    reasons = _core_identity_reasons(
        freeze,
        lineage,
        baseline_blobs,
        current_blobs,
        baseline_hashes,
        repair_ancestral=True,
        pass206_changed_paths=("hhs_runtime/c/hhs_pass205_continuation.c",),
    )
    assert "PASS206_REPAIR_TOUCHED_FROZEN_CORE" in reasons


def test_pass207_successor_rejects_core_modification() -> None:
    pass207 = load("contracts/pass207/PASS_207_CONTRACT.json")
    broken = copy.deepcopy(pass207)
    broken["core_preservation"]["modifies_pass206_frozen_core"] = True
    reasons = _successor_reasons(broken)
    assert "PASS207_CORE_PRESERVATION_MISMATCH" in reasons


def test_approved_repair_evidence_constants_are_exact() -> None:
    lineage = load("artifacts/pass206/CORE_SUCCESSOR_REPAIR_LINEAGE.json")
    row = lineage["approved_successors"][0]
    assert row["repair_merge_commit"] == APPROVED_REPAIR_MERGE
    assert row["validated_implementation_head"] == APPROVED_REPAIR_VALIDATED_HEAD
    assert row["validation_run"] == APPROVED_REPAIR_RUN
    assert row["validation_job"] == APPROVED_REPAIR_JOB
    assert row["approved_current_git_blob"] == APPROVED_RUNTIME_ABI_BLOB
