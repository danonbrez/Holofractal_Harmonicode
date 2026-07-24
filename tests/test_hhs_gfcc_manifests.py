from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from hhs_gfcc.core import CONTRACT_ID, canonical_spec, validate_spec
from hhs_gfcc.manifest import (
    REQUIRED_RECEIPTS,
    build_source_manifest,
    validate_inherited_pass152,
    validate_source_manifest,
)
from hhs_gfcc.pipeline import (
    replay_canonical_file_workload,
    run_canonical_file_workload,
)
from hhs_gfcc.receipts import build_receipt_chain, verify_receipt_chain
from hhs_gfcc.schema import canonical_spec_path, load_canonical_spec


def test_canonical_spec_is_ingested_from_repository_json():
    path = canonical_spec_path(ROOT)
    assert path.is_file()
    loaded = load_canonical_spec(ROOT)
    assert loaded == canonical_spec(8)
    validation = validate_spec(loaded)
    assert validation["valid"] is True
    assert len(validation["source_hash72"]) == 72


def test_file_ingested_workload_replays_exactly():
    first = run_canonical_file_workload(ROOT)
    second = run_canonical_file_workload(ROOT)
    assert first == second
    assert first["source_ingestion"]["mode"] == "JSON_FILE"
    replay = replay_canonical_file_workload(ROOT, first)
    assert replay["match"] is True


def test_inherited_pass152_gate_is_execution_evidence_backed():
    inherited = validate_inherited_pass152(ROOT)
    assert inherited["valid"] is True, inherited
    assert inherited["required_inherited_terminal"] == (
        "HHS_PASS_152_UNIVERSAL_ELASTIC_CLOSURE_INVARIANT_VERIFIED"
    )
    assert inherited["conditions"]["positive_matrix_30_of_30"] is True
    assert inherited["conditions"]["negative_matrix_30_of_30"] is True
    assert inherited["conditions"]["native_c_passed"] is True
    assert inherited["conditions"]["vm81_commit_present"] is True
    assert inherited["conditions"]["hash72_receipt_present"] is True
    assert inherited["conditions"]["deterministic_replay_match"] is True


def test_source_manifest_matches_every_gfcc_source():
    manifest = build_source_manifest(ROOT)
    validation = validate_source_manifest(ROOT, manifest)
    assert manifest["contract_id"] == CONTRACT_ID
    assert manifest["file_count"] > 30
    assert validation["valid"] is True, validation
    assert validation["matched"] == validation["total"]


def test_complete_receipt_ledger_is_continuous_and_digest_closed():
    operations = [
        {
            "operation_id": filename.removesuffix("_RECEIPT.json"),
            "inputs": {"sequence": index},
            "outputs": {"ok": True},
        }
        for index, filename in enumerate(REQUIRED_RECEIPTS, start=1)
    ]
    receipts = build_receipt_chain(operations)
    validation = verify_receipt_chain(receipts)
    assert len(receipts) == 18
    assert validation["valid"] is True, validation
    assert validation["receipt_count"] == 18
    assert validation["terminal_receipt_digest"] == receipts[-1]["receipt_digest"]


def test_receipt_ledger_detects_predecessor_tampering():
    operations = [
        {
            "operation_id": filename.removesuffix("_RECEIPT.json"),
            "inputs": {"sequence": index},
            "outputs": {"ok": True},
        }
        for index, filename in enumerate(REQUIRED_RECEIPTS, start=1)
    ]
    receipts = build_receipt_chain(operations)
    receipts[7]["predecessor_receipt_digest"] = "0" * 64
    validation = verify_receipt_chain(receipts)
    assert validation["valid"] is False
    assert any(
        item["error"] in {"PREDECESSOR_MISMATCH", "RECEIPT_DIGEST_MISMATCH"}
        for item in validation["errors"]
    )
