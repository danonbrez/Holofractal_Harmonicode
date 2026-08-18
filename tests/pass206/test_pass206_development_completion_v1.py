from __future__ import annotations

import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def load(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def artifact_hash(value: dict) -> str:
    payload = dict(value)
    payload.pop("artifact_sha256", None)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def test_pass206_development_completion_receipt_is_self_consistent() -> None:
    receipt = load("artifacts/pass206/PASS_206_COMPLETION_RECEIPT.json")
    assert receipt["artifact_sha256"] == artifact_hash(receipt)
    assert receipt["status"] == "DEVELOPMENT_IMPLEMENTATION_AND_FINAL_REPLAY_COMPLETE_CANONICAL_MAIN_VERIFICATION_PENDING"
    assert receipt["completion_claimed"] is False
    assert receipt["canonical_main"] == {
        "completion_claimed": False,
        "promotion_authorized": False,
        "status": "PENDING_EXPLICIT_CANONICAL_MAIN_AUTHORIZATION",
        "verified": False,
    }
    assert receipt["development_closure"]["ready_for_pass219_inherited_membrane"] is True
    assert receipt["enforcement_decision"]["canonical_mutation_authority"] == "VM81_KERNEL"
    assert receipt["enforcement_decision"]["canonical_mutation_authority_count"] == 1
    assert receipt["enforcement_decision"]["canonical_hash72_commit_stream_count"] == 1
    assert receipt["enforcement_decision"]["pass206_new_mutation_authority"] is False
    assert receipt["enforcement_decision"]["pass206_new_persistence_authority"] is False
    assert receipt["enforcement_decision"]["pass206_new_hash72_clock"] is False


def test_pass206_post_receipt_matrix_preserves_canonical_main_pending() -> None:
    matrix = load("artifacts/pass206/VALIDATION_MATRIX.json")
    receipt = load("artifacts/pass206/PASS_206_COMPLETION_RECEIPT.json")
    assert matrix["artifact_sha256"] == artifact_hash(matrix)
    assert matrix["stage"] == "DEVELOPMENT_COMPLETE_CANONICAL_MAIN_VERIFICATION_PENDING"
    assert matrix["completion_claimed"] is False
    assert matrix["canonical_main_verified"] is False
    assert matrix["development_completion_receipt_emitted"] is True
    row = next(item for item in matrix["checks"] if item["name"] == "completion_receipt_emitted")
    assert row["status"] == "PASS"
    assert row["receipt_artifact_sha256"] == receipt["artifact_sha256"]
    main_row = next(item for item in matrix["checks"] if item["name"] == "canonical_main_verification")
    assert main_row["status"] == "PENDING"
    assert main_row["promotion_authorized"] is False


def test_pass206_final_replay_evidence_is_complete() -> None:
    receipt = load("artifacts/pass206/PASS_206_COMPLETION_RECEIPT.json")
    expected = {
        "pass206", "pass207", "pass208", "pass209", "pass210", "pass211",
        "pass212", "pass213", "pass214", "pass215", "pass216_217_218",
    }
    assert set(receipt["final_cumulative_replay"]) == expected
    for value in receipt["final_cumulative_replay"].values():
        assert value["run"] > 0
        assert value["exact_job"] > 0
        assert value["synthetic_job"] > 0


def test_completion_document_does_not_claim_canonical_main() -> None:
    text = (ROOT / "docs/pass206/COMPLETION.md").read_text(encoding="utf-8")
    assert "CANONICAL MAIN VERIFICATION PENDING" in text
    assert "canonical_main.verified = false" in text
    assert "completion_claimed = false" in text
