"""Pass 219 Lane 5 1.73 — bounded cross-representation generalization.

Uses the repository's Pass 123 BoundedTokenGeneralizationEngine to learn only
from the exact 1.72 invariant relation records and validate on disjoint held-out
representations. No weight update, learning commit, execution authority, or
canonical runtime mutation is granted.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass123_bounded_token_generalization_v1 import (
    BoundedTokenGeneralizationEngine,
    GeneralizationBounds,
    Pass123Error,
)
from hhs_runtime.pass219.lane5_nine_loop_relation_dataset_1_72 import (
    DATASET_SHA256,
    RECORD_CHAIN_SHA256,
    build_relation_training_records,
    verify_dataset,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "contracts/pass219/PASS_219_LANE5_NINE_LOOP_GENERALIZATION_1_73.json"
SCHEMA = "HHS_PASS219_LANE5_NINE_LOOP_GENERALIZATION_1_73"
FROZEN_MODEL_ROOT_HASH72 = "0000000000000000000000000000002rd>Jdh(*jXM9IMuM^931?)TxIUlEV>A5MH81cDfqL"
FROZEN_VALIDATION_ROOT_HASH72 = "0000000000000000000000000000004uxkwBpAEdc+=PCnAuM+5cGH26usFYmSWD3kSLSkPM"
FROZEN_REPLAY_BUNDLE_SHA256 = "238556f95e17e77d01a9e37e4be4cbbd56181982f3599dc941cfe77be32aaf69"

LABEL_BY_CLASS = {
    1: "LANE5_ADDITIVE_VALIDATED",
    0: "LANE5_TYPED_NEUTRAL",
    -1: "LANE5_REJECTED_OR_INCOMPLETE",
}

TOKEN_CLASS_PAIRS = {
    "source_manifest_identity": ("JSON", "CODE"),
    "matrix_geometry": ("MATHEMATICS", "TENSOR_CELL"),
    "shared_member_roles": ("JSON", "SYMBOLIC_EXPRESSION"),
    "prime_dependent_roles": ("JSON", "CODE"),
    "support_geometry": ("MATHEMATICS", "TENSOR_CELL"),
    "comparison_stream_identity": ("JSON", "MATHEMATICS"),
    "literal_container_identity_rejected": ("JSON", "CODE"),
    "rational_reconstruction_partition": ("MATHEMATICS", "JSON"),
    "modular_residue_closure": ("MATHEMATICS", "SYMBOLIC_EXPRESSION"),
    "genesis_constructor": ("SYMBOLIC_EXPRESSION", "MATHEMATICS"),
    "foreign_delta_quarantine": ("SYMBOLIC_EXPRESSION", "TEXT"),
    "authority_boundary": ("VM81_STATE", "JSON"),
}


class Lane5NineLoopGeneralizationError(ValueError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Lane5NineLoopGeneralizationError(f"floating value forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    _reject_float(contract)
    if contract.get("schema") != SCHEMA:
        raise Lane5NineLoopGeneralizationError("1.73 contract schema mismatch")
    return contract


def _engine() -> BoundedTokenGeneralizationEngine:
    return BoundedTokenGeneralizationEngine(
        GeneralizationBounds(
            max_examples=64,
            max_features_per_example=32,
            max_rules=32,
            max_model_bits=1_000_000,
            max_entropy_growth_bits=4096,
        )
    )


def _semantic_root(record: Mapping[str, Any]) -> str:
    return _hash(
        "hhs_pass219_lane5_nine_loop_1_73_semantic_v1",
        {
            "parent_dataset_sha256": DATASET_SHA256,
            "record_id": record["record_id"],
            "relation_type": record["relation_type"],
            "deviation_class": record["deviation_class"],
            "observed_features": record["observed_features"],
            "expected_mapping": record["expected_mapping"],
        },
    )


def _provenance_root(record: Mapping[str, Any]) -> str:
    return _hash(
        "hhs_pass219_lane5_nine_loop_1_73_provenance_v1",
        {
            "parent_dataset_sha256": DATASET_SHA256,
            "parent_record_chain_sha256": RECORD_CHAIN_SHA256,
            "record_id": record["record_id"],
            "record_sha256": record["record_sha256"],
            "chain_sha256": record["chain_sha256"],
        },
    )


def _invariant_features(record: Mapping[str, Any], *, projection: str) -> dict[str, Any]:
    return {
        "relation_type": record["relation_type"],
        "deviation_class": int(record["deviation_class"]),
        "observed_features": record["observed_features"],
        "expected_mapping": record["expected_mapping"],
        "training_labels": record["training_labels"],
        "parent_dataset_sha256": DATASET_SHA256,
        "local_projection": projection,
        "local_record_identity": record["record_id"],
    }


def build_examples() -> dict[str, list[dict[str, Any]]]:
    verify_dataset()
    records = build_relation_training_records()
    engine = _engine()
    training: list[dict[str, Any]] = []
    holdout: list[dict[str, Any]] = []

    for record in records:
        record_id = str(record["record_id"])
        train_class, holdout_class = TOKEN_CLASS_PAIRS[record_id]
        label = LABEL_BY_CLASS[int(record["deviation_class"])]
        semantic_root = _semantic_root(record)
        provenance_root = _provenance_root(record)

        training.append(
            engine.make_example(
                token_class=train_class,
                token_identity=f"1.73:train:{record_id}",
                features=_invariant_features(record, projection="TRAIN_SOURCE"),
                label=label,
                provenance_root_hash72=provenance_root,
                semantic_root_hash72=semantic_root,
            )
        )
        holdout.append(
            engine.make_example(
                token_class=holdout_class,
                token_identity=f"1.73:holdout:{record_id}",
                features=_invariant_features(record, projection="HOLDOUT_REENCODED"),
                label=label,
                provenance_root_hash72=provenance_root,
                semantic_root_hash72=semantic_root,
            )
        )

    return {"training": training, "holdout": holdout}


def run_generalization() -> dict[str, Any]:
    contract = load_contract()
    examples = build_examples()
    training = examples["training"]
    holdout = examples["holdout"]
    engine = _engine()

    train_roots = {x["example_root_hash72"] for x in training}
    holdout_roots = {x["example_root_hash72"] for x in holdout}
    if train_roots & holdout_roots:
        raise Lane5NineLoopGeneralizationError("training/holdout roots overlap")

    model = engine.train(
        training,
        holdout_example_roots=sorted(holdout_roots),
    )
    validated = engine.validate(
        model,
        holdout,
        require_all_classes=False,
    )
    validated_model = validated["validated_model"]
    validation_receipt = validated["validation_receipt"]

    applications: list[dict[str, Any]] = []
    replays: list[dict[str, Any]] = []
    for example in holdout:
        application = engine.apply(validated_model, example)
        replay = engine.replay(validated_model, example, application)
        applications.append(application)
        replays.append(replay)

    replay_bundle = {
        "schema": SCHEMA + "_REPLAY_BUNDLE",
        "model_root_hash72": validated_model["model_root_hash72"],
        "validation_receipt_root_hash72": validation_receipt[
            "validation_receipt_root_hash72"
        ],
        "application_roots": [
            item["application_root_hash72"] for item in applications
        ],
        "replay_roots": [
            item["replay_receipt_root_hash72"] for item in replays
        ],
    }
    replay_bundle_sha256 = hashlib.sha256(
        _canonical_bytes(replay_bundle)
    ).hexdigest()

    g = contract["generalization"]
    checks = {
        "parent_dataset": DATASET_SHA256 == contract["parent_dataset_sha256"],
        "parent_record_chain": (
            RECORD_CHAIN_SHA256 == contract["parent_record_chain_sha256"]
        ),
        "training_count": len(training) == g["training_examples"] == 12,
        "holdout_count": len(holdout) == g["holdout_examples"] == 12,
        "disjoint_roots": not bool(train_roots & holdout_roots),
        "rule_count": validated_model["rule_count"] == g["expected_rule_count"] == 12,
        "exact_accuracy": validation_receipt["accuracy"] == {
            "numerator": 12,
            "denominator": 12,
        },
        "semantic_drift_zero": (
            validation_receipt["semantic_drift_count"]
            == g["semantic_drift_count_expected"]
            == 0
        ),
        "replay_count": len(replays) == g["expected_replay_count"] == 12,
        "all_replays_validated": all(
            item["replay_status"]
            == "DETERMINISTIC_GENERALIZATION_REPLAY_VALIDATED"
            for item in replays
        ),
        "model_root_frozen": (
            validated_model["model_root_hash72"]
            == contract["frozen_receipts"]["model_root_hash72"]
            == FROZEN_MODEL_ROOT_HASH72
        ),
        "validation_root_frozen": (
            validation_receipt["validation_receipt_root_hash72"]
            == contract["frozen_receipts"]["validation_receipt_root_hash72"]
            == FROZEN_VALIDATION_ROOT_HASH72
        ),
        "replay_bundle_frozen": (
            replay_bundle_sha256
            == contract["frozen_receipts"]["replay_bundle_sha256"]
            == FROZEN_REPLAY_BUNDLE_SHA256
        ),
        "authority_boundary": (
            contract["authority"]["validated_knowledge_model_only"] is True
            and contract["authority"]["execution_authority"] is False
            and contract["authority"]["source_mutation_authority"] is False
            and contract["authority"]["runtime_mutation_authority"] is False
            and contract["authority"]["model_weight_update_authority"] is False
            and contract["authority"]["learning_commit_authority"] is False
            and contract["authority"]["canonical_vm81_mutation_authority"] is False
            and contract["authority"]["canonical_hash72_authority"] is False
            and contract["authority"]["canonical_hash216_authority"] is False
            and contract["authority"]["canonical_persistence_authority"] is False
            and contract["authority"]["floating_point_canonical_authority"] is False
        ),
    }
    if not all(checks.values()):
        failed = sorted(k for k, v in checks.items() if not v)
        raise Lane5NineLoopGeneralizationError(
            "1.73 generalization failed: " + ",".join(failed)
        )

    return {
        "schema": SCHEMA + "_DISCOVERY_RECEIPT",
        "checks": checks,
        "training_example_count": len(training),
        "holdout_example_count": len(holdout),
        "rule_count": validated_model["rule_count"],
        "accuracy": validation_receipt["accuracy"],
        "covered_token_classes": validation_receipt["covered_token_classes"],
        "semantic_drift_count": validation_receipt["semantic_drift_count"],
        "entropy_growth_bits": validation_receipt["entropy_growth_bits"],
        "model_root_hash72": validated_model["model_root_hash72"],
        "validation_receipt_root_hash72": validation_receipt[
            "validation_receipt_root_hash72"
        ],
        "replay_bundle_sha256": replay_bundle_sha256,
        "replay_count": len(replays),
        "validated_model_only": True,
        "model_weight_update_authority": False,
        "learning_commit_authority": False,
        "canonical_transition_ready": False,
        "candidate_only": True,
    }


def assert_pass123_leakage_rejected() -> str:
    examples = build_examples()
    engine = _engine()
    leaked = examples["training"][0]
    try:
        engine.train(
            examples["training"],
            holdout_example_roots=[leaked["example_root_hash72"]],
        )
    except Pass123Error as exc:
        if exc.code != "REJECT_TRAINING_HOLDOUT_LEAKAGE":
            raise
        return exc.code
    raise Lane5NineLoopGeneralizationError("Pass123 leakage gate did not reject")
