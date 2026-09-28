"""Pass 219 Lane 5 1.72 — multi-record nine-loop relation dataset.

Expands the 1.71 source-bound specimen into deterministic recognition/mapping
records. This is dataset preparation only; it does not train or mutate a model.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.pass219.lane5_nine_loop_training_specimen_1_71 import (
    SPECIMEN_SHA256,
    verify_specimen,
)

ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "data/pass219/lane5_nine_loop_relation_dataset_1_72.json"
CONTRACT_PATH = ROOT / "contracts/pass219/PASS_219_LANE5_NINE_LOOP_RELATION_DATASET_1_72.json"
SCHEMA = "HHS_PASS219_LANE5_NINE_LOOP_RELATION_DATASET_1_72"
DATASET_SCHEMA = "HHS_NINE_LOOP_LANE5_RELATION_DATASET_1_72"
DATASET_SHA256 = "dd623f4fc778364274e7ba05c914fb441b724ca3ce41a4eb4df4cdc64935d587"
RECORD_CHAIN_SHA256 = "4a951f76afcd3f759e74263bc9cd0019b50f034bc07e93341b73200e0c85bd6a"
GENESIS_IDENTITY = "F(x,y,a,b)=(x+y)^2+(xy-a^2)^2+(a^2-b)^2+(a^4-2)^2"

EXPECTED_RECORD_IDS = (
    "source_manifest_identity",
    "matrix_geometry",
    "shared_member_roles",
    "prime_dependent_roles",
    "support_geometry",
    "comparison_stream_identity",
    "literal_container_identity_rejected",
    "rational_reconstruction_partition",
    "modular_residue_closure",
    "genesis_constructor",
    "foreign_delta_quarantine",
    "authority_boundary",
)

class Lane5NineLoopRelationDatasetError(ValueError):
    pass

def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Lane5NineLoopRelationDatasetError(f"floating value forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")

def canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")

def load_dataset() -> dict[str, Any]:
    data = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    _reject_float(data)
    if data.get("schema") != DATASET_SCHEMA:
        raise Lane5NineLoopRelationDatasetError("1.72 dataset schema mismatch")
    return data

def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    _reject_float(contract)
    if contract.get("schema") != SCHEMA:
        raise Lane5NineLoopRelationDatasetError("1.72 contract schema mismatch")
    return contract

def _record_chain(records: list[Mapping[str, Any]]) -> tuple[list[dict[str, str]], str]:
    previous = "0" * 64
    chain: list[dict[str, str]] = []
    for record in records:
        record_sha256 = hashlib.sha256(canonical_bytes(record)).hexdigest()
        chain_sha256 = hashlib.sha256(
            (previous + record_sha256).encode("ascii")
        ).hexdigest()
        chain.append({
            "record_id": str(record["record_id"]),
            "record_sha256": record_sha256,
            "previous_chain_sha256": previous,
            "chain_sha256": chain_sha256,
        })
        previous = chain_sha256
    return chain, previous

def verify_dataset(
    dataset: Mapping[str, Any] | None = None,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    verify_specimen()
    d = dict(load_dataset() if dataset is None else dataset)
    c = dict(load_contract() if contract is None else contract)
    _reject_float(d)
    _reject_float(c)

    digest = hashlib.sha256(canonical_bytes(d)).hexdigest()
    records = list(d.get("records") or [])
    ids = tuple(str(record.get("record_id")) for record in records)
    classes = [int(record.get("deviation_class")) for record in records]
    chain, chain_root = _record_chain(records)

    checks = {
        "dataset_sha256": digest == DATASET_SHA256 == c["dataset"]["canonical_sha256"],
        "parent_specimen_sha256": (
            d["parent_specimen_sha256"] == SPECIMEN_SHA256 == c["parent_specimen_sha256"]
        ),
        "record_order": ids == EXPECTED_RECORD_IDS,
        "record_count": len(records) == d["record_count"] == c["dataset"]["record_count"] == 12,
        "trinary_classes": set(classes) <= {-1, 0, 1},
        "partition": (
            classes.count(1) == c["dataset"]["additive_records"] == 6
            and classes.count(0) == c["dataset"]["neutral_records"] == 4
            and classes.count(-1) == c["dataset"]["negative_records"] == 2
        ),
        "ordered_chain": chain_root == RECORD_CHAIN_SHA256 == c["dataset"]["ordered_record_chain_sha256"],
        "negative_container_example": (
            records[6]["record_id"] == "literal_container_identity_rejected"
            and records[6]["deviation_class"] == -1
            and records[6]["observed_features"]["literal_container_identity_required"] is False
        ),
        "incomplete_reconstruction_example": (
            records[7]["record_id"] == "rational_reconstruction_partition"
            and records[7]["deviation_class"] == -1
            and records[7]["observed_features"]["complete"] is False
            and records[7]["observed_features"]["certified_rational"]["numerator"]
              + records[7]["observed_features"]["two_prime_only"]["numerator"]
              == records[7]["observed_features"]["certified_rational"]["denominator"]
              == records[7]["observed_features"]["two_prime_only"]["denominator"]
        ),
        "matrix_geometry": (
            records[1]["observed_features"]["rows"] == 424
            and records[1]["observed_features"]["columns"] == 5431
            and records[1]["observed_features"]["entries"] == 2302744
            and records[1]["observed_features"]["rows"] * records[1]["observed_features"]["columns"]
                == records[1]["observed_features"]["entries"]
        ),
        "genesis_verbatim": (
            records[9]["observed_features"]["genesis_identity_verbatim"] == GENESIS_IDENTITY
        ),
        "foreign_delta_quarantine": (
            records[10]["observed_features"]["foreign_delta_role"] == "kinematic_surface"
            and records[10]["observed_features"]["native_delta_alias_authorized"] is False
        ),
        "dataset_only_authority": (
            d["admission"]["dataset_preparation_only"] is True
            and d["admission"]["model_weight_update_authority"] is False
            and d["admission"]["learning_commit_authority"] is False
            and d["admission"]["canonical_transition_authority"] is False
        ),
    }
    if not all(checks.values()):
        failed = sorted(k for k, v in checks.items() if not v)
        raise Lane5NineLoopRelationDatasetError(
            "1.72 dataset verification failed: " + ",".join(failed)
        )

    return {
        "schema": SCHEMA + "_RECEIPT",
        "checks": checks,
        "dataset_sha256": digest,
        "ordered_record_chain_sha256": chain_root,
        "record_chain": chain,
        "record_count": len(records),
        "class_partition": {
            "additive": classes.count(1),
            "neutral": classes.count(0),
            "negative": classes.count(-1),
        },
        "dataset_preparation_only": True,
        "model_weight_update_authority": False,
        "learning_commit_authority": False,
        "candidate_only": True,
        "canonical_transition_ready": False,
    }

def build_relation_training_records() -> list[dict[str, Any]]:
    dataset = load_dataset()
    receipt = verify_dataset(dataset=dataset)
    chain_by_id = {entry["record_id"]: entry for entry in receipt["record_chain"]}
    out: list[dict[str, Any]] = []
    for sequence, record in enumerate(dataset["records"]):
        out.append({
            "sequence": sequence,
            "record_id": record["record_id"],
            "relation_type": record["relation_type"],
            "deviation_class": record["deviation_class"],
            "observed_features": record["observed_features"],
            "expected_mapping": record["expected_mapping"],
            "training_labels": record["training_labels"],
            "record_sha256": chain_by_id[record["record_id"]]["record_sha256"],
            "chain_sha256": chain_by_id[record["record_id"]]["chain_sha256"],
            "candidate_only": True,
            "model_weight_update_authority": False,
            "learning_commit_authority": False,
        })
    return out
