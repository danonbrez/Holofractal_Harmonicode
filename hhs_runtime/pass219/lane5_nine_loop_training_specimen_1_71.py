"""Pass 219 Lane 5 1.71 — deterministic nine-loop training specimen admission.

This is dataset preparation, not model training. It validates a source-bound
specimen derived from the green 1.70 feedback layer and binds it to the native
candidate-only Hash216 lineage without granting model-weight or learning-commit
authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "contracts/pass219/PASS_219_LANE5_NINE_LOOP_TRAINING_SPECIMEN_1_71.json"
SPECIMEN_PATH = ROOT / "training_specimens/HHS_NINE_LOOP_FOREIGN_EQUIVALENCE_FEEDBACK_SPECIMEN_1_71.json"
SCHEMA = "HHS_PASS219_LANE5_NINE_LOOP_TRAINING_SPECIMEN_1_71"
SPECIMEN_SCHEMA = "HHS_NINE_LOOP_FOREIGN_EQUIVALENCE_FEEDBACK_SPECIMEN_1_71"
HASH216_LEN = 216
SPECIMEN_SHA256 = "96a9f686a1ab35c8600ba7a38a367af38339b51a70182c3d7981ee529ff50191"
PARENT_FEEDBACK_PAYLOAD_SHA256 = "78f2cc37e9304017cf0b6a233f2cb5ab080757fec57e6eb5897295bf0d2bed70"
PARENT_RELATION_SHA256 = "4acc66c250129d5a42f976d673027313707633012b2de6f85d6491a4083ed73a"
PARENT_SUPPORT_SHA256 = "64cd7ae9027ef41969948efc35b1273ba03ba3f759c076700d8a09940ebbf54d"
GENESIS_IDENTITY = "F(x,y,a,b)=(x+y)^2+(xy-a^2)^2+(a^2-b)^2+(a^4-2)^2"

class Lane5NineLoopTrainingSpecimenError(ValueError):
    pass

def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Lane5NineLoopTrainingSpecimenError(f"floating value forbidden at {path}")
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

def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    _reject_float(contract)
    if contract.get("schema") != SCHEMA:
        raise Lane5NineLoopTrainingSpecimenError("1.71 contract schema mismatch")
    return contract

def load_specimen() -> dict[str, Any]:
    specimen = json.loads(SPECIMEN_PATH.read_text(encoding="utf-8"))
    _reject_float(specimen)
    if specimen.get("schema") != SPECIMEN_SCHEMA:
        raise Lane5NineLoopTrainingSpecimenError("1.71 specimen schema mismatch")
    return specimen

def verify_specimen(
    specimen: Mapping[str, Any] | None = None,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    s = dict(load_specimen() if specimen is None else specimen)
    c = dict(load_contract() if contract is None else contract)
    _reject_float(s)
    _reject_float(c)

    digest = hashlib.sha256(canonical_bytes(s)).hexdigest()
    lineage = s["source_lineage"]
    exact = s["exact_features"]
    dev = s["deviation_features"]
    admission = s["admission"]

    checks = {
        "specimen_sha256": digest == SPECIMEN_SHA256 == c["training_specimen"]["canonical_sha256"],
        "parent_feedback_payload": lineage["feedback_payload_sha256"] == PARENT_FEEDBACK_PAYLOAD_SHA256,
        "parent_relation": lineage["relation_sha256"] == PARENT_RELATION_SHA256,
        "parent_support": lineage["e0_support_sha256"] == PARENT_SUPPORT_SHA256,
        "matrix_entries_close": exact["matrix_geometry"]["rows"] * exact["matrix_geometry"]["columns"] == exact["matrix_geometry"]["entries"],
        "coverage_closes": (
            exact["coordinate_coverage"]["certified_rational"]["numerator"]
            + exact["coordinate_coverage"]["two_prime_only"]["numerator"]
            == exact["matrix_geometry"]["nonzero_coordinates"]
            == exact["coordinate_coverage"]["certified_rational"]["denominator"]
            == exact["coordinate_coverage"]["two_prime_only"]["denominator"]
        ),
        "genesis_verbatim": exact["genesis_identity_verbatim"] == GENESIS_IDENTITY,
        "trinary_only": set(dev.values()) <= {-1, 0, 1},
        "negative_example_preserved": (
            dev["literal_container_identity_assumption"] == -1
            and dev["foreign_rational_reconstruction_complete"] == -1
        ),
        "validated_additions_preserved": (
            dev["logical_representation_equivalence"] == 1
            and dev["support_geometry"] == 1
            and dev["hash216_replay"] == 1
        ),
        "labels_exact": s["training_feedback_labels"] == c["required_labels"],
        "objectives_exact": s["learning_objectives"] == c["required_learning_objectives"],
        "counts_exact": (
            len(s["training_feedback_labels"]) == 13
            and len(s["learning_objectives"]) == 5
            and len(dev) == 16
        ),
        "dataset_only_authority": (
            admission["dataset_preparation_only"] is True
            and admission["model_weight_update_authority"] is False
            and admission["learning_commit_authority"] is False
            and admission["canonical_vm81_mutation_authority"] is False
            and admission["canonical_hash72_authority"] is False
            and admission["canonical_hash216_authority"] is False
            and admission["canonical_persistence_authority"] is False
            and admission["floating_point_canonical_authority"] is False
        ),
    }
    if not all(checks.values()):
        failed = sorted(k for k, v in checks.items() if not v)
        raise Lane5NineLoopTrainingSpecimenError(
            "1.71 specimen verification failed: " + ",".join(failed)
        )

    return {
        "schema": SCHEMA + "_RECEIPT",
        "checks": checks,
        "training_specimen_sha256": digest,
        "training_feedback_label_count": len(s["training_feedback_labels"]),
        "learning_objective_count": len(s["learning_objectives"]),
        "deviation_feature_count": len(dev),
        "dataset_preparation_only": True,
        "model_weight_update_authority": False,
        "learning_commit_authority": False,
        "candidate_only": True,
        "canonical_transition_ready": False,
    }

def build_training_record() -> dict[str, Any]:
    specimen = load_specimen()
    receipt = verify_specimen(specimen=specimen)
    return {
        "schema": SCHEMA + "_TRAINING_RECORD",
        "input_type": specimen["input_type"],
        "corpus_classification": specimen["corpus_classification"],
        "benchmark": specimen["benchmark"],
        "source_lineage": specimen["source_lineage"],
        "exact_features": specimen["exact_features"],
        "deviation_features": specimen["deviation_features"],
        "training_feedback_labels": specimen["training_feedback_labels"],
        "learning_objectives": specimen["learning_objectives"],
        "training_specimen_sha256": receipt["training_specimen_sha256"],
        "native_hash216_required": True,
        "native_hash216_replay_verified": False,
        "dataset_preparation_only": True,
        "model_weight_update_authority": False,
        "learning_commit_authority": False,
        "canonical_transition_ready": False,
        "candidate_only": True,
    }

def bind_native_hash216(
    record: Mapping[str, Any],
    *,
    candidate_hash216: str,
    replay_hash216: str,
    native_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    left = str(candidate_hash216)
    right = str(replay_hash216)
    if len(left) != HASH216_LEN or len(right) != HASH216_LEN:
        raise Lane5NineLoopTrainingSpecimenError("native Hash216 must contain exactly 216 symbols")
    if left != right:
        raise Lane5NineLoopTrainingSpecimenError("native Hash216 replay mismatch")
    if str(native_receipt.get("training_candidate_hash216", "")) != left:
        raise Lane5NineLoopTrainingSpecimenError("native receipt Hash216 mismatch")

    required = (
        "accepted", "parent_1_70_verified", "specimen_identity_verified",
        "source_lineage_verified", "negative_example_verified",
        "dataset_scope_verified", "hash216_replay_verified", "candidate_only",
    )
    if not all(bool(native_receipt.get(key, False)) for key in required):
        raise Lane5NineLoopTrainingSpecimenError("native 1.71 receipt is incomplete")

    forbidden = (
        "model_weight_update_authority", "learning_commit_authority",
        "canonical_vm81_mutation_authority", "canonical_hash72_authority",
        "canonical_hash216_authority", "canonical_persistence_authority",
        "floating_point_canonical_authority",
    )
    for key in forbidden:
        if bool(native_receipt.get(key, False)):
            raise Lane5NineLoopTrainingSpecimenError(f"forbidden authority exposed: {key}")

    bound = dict(record)
    bound["native_training_candidate_hash216"] = left
    bound["native_hash216_replay_verified"] = True
    bound["dataset_preparation_only"] = True
    bound["model_weight_update_authority"] = False
    bound["learning_commit_authority"] = False
    bound["canonical_transition_ready"] = False
    bound["candidate_only"] = True
    return bound
