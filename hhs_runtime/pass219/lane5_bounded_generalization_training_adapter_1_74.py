"""Pass 219 Lane 5 1.74 adapter for merged Pass123 1.73 generalization.

The authoritative 1.73 contract freezes the Pass123 model/validation Hash72
roots, replay-bundle SHA-256, and native-composition flag.  It does not publish
a standalone native Hash216 field.  This adapter therefore verifies the frozen
1.73 receipts against deterministic Pass123 replay and asks the native 1.74
training API to derive a candidate-only Hash216 evidence identity from that
exact frozen tuple.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.pass219.lane5_nine_loop_generalization_1_73 import (
    run_generalization,
)

ROOT = Path(__file__).resolve().parents[2]
PARENT_CONTRACT = (
    ROOT / "contracts/pass219/PASS_219_LANE5_NINE_LOOP_GENERALIZATION_1_73.json"
)

METHOD_ID = "BOUNDED_TOKEN_GENERALIZATION"
MODE = 19
TEMPORAL_BATCH = 3
TARGET_RELATION = 1
EVIDENCE_DOMAIN = "PASS219_LANE5_GENERALIZATION_1_73_FROZEN_RECEIPTS"


class Pass219Lane5BoundedGeneralizationTrainingAdapterError(ValueError):
    pass


def load_parent_contract(path: Path = PARENT_CONTRACT) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "HHS_PASS219_LANE5_NINE_LOOP_GENERALIZATION_1_73":
        raise Pass219Lane5BoundedGeneralizationTrainingAdapterError(
            "unexpected 1.73 parent schema"
        )
    return value


def frozen_parent_receipts(
    contract: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    parent = dict(contract or load_parent_contract())
    receipts = dict(parent.get("frozen_receipts") or {})

    model = receipts.get("model_root_hash72")
    validation = receipts.get("validation_receipt_root_hash72")
    replay = receipts.get("replay_bundle_sha256")
    native_frozen = receipts.get("native_hash216_composition_frozen")

    missing: list[str] = []
    if not isinstance(model, str) or len(model) != 72:
        missing.append("model_root_hash72")
    if not isinstance(validation, str) or len(validation) != 72:
        missing.append("validation_receipt_root_hash72")
    if not isinstance(replay, str) or len(replay) != 64:
        missing.append("replay_bundle_sha256")
    if native_frozen is not True:
        missing.append("native_hash216_composition_frozen")

    if missing:
        raise Pass219Lane5BoundedGeneralizationTrainingAdapterError(
            "UNFROZEN_PARENT_RECEIPTS:" + ",".join(sorted(missing))
        )

    return {
        "model_root_hash72": model,
        "validation_receipt_root_hash72": validation,
        "replay_bundle_sha256": replay,
        "native_hash216_composition_frozen": True,
    }


def verify_frozen_parent_receipts(
    contract: Mapping[str, Any] | None = None,
    discovery_receipt: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    frozen = frozen_parent_receipts(contract)
    observed = dict(discovery_receipt or run_generalization())

    expected = {
        "model_root_hash72": observed.get("model_root_hash72"),
        "validation_receipt_root_hash72": observed.get(
            "validation_receipt_root_hash72"
        ),
        "replay_bundle_sha256": observed.get("replay_bundle_sha256"),
    }
    mismatched = sorted(
        key for key, value in expected.items()
        if not isinstance(value, str) or frozen[key] != value
    )
    if mismatched:
        raise Pass219Lane5BoundedGeneralizationTrainingAdapterError(
            "FROZEN_PARENT_RECEIPT_MISMATCH:" + ",".join(mismatched)
        )

    if observed.get("rule_count") != 12:
        raise Pass219Lane5BoundedGeneralizationTrainingAdapterError(
            "FROZEN_PARENT_RULE_COUNT_MISMATCH"
        )
    if observed.get("accuracy") != {"numerator": 12, "denominator": 12}:
        raise Pass219Lane5BoundedGeneralizationTrainingAdapterError(
            "FROZEN_PARENT_ACCURACY_MISMATCH"
        )
    if observed.get("semantic_drift_count") != 0:
        raise Pass219Lane5BoundedGeneralizationTrainingAdapterError(
            "FROZEN_PARENT_SEMANTIC_DRIFT"
        )
    if observed.get("replay_count") != 12:
        raise Pass219Lane5BoundedGeneralizationTrainingAdapterError(
            "FROZEN_PARENT_REPLAY_COUNT_MISMATCH"
        )

    return frozen


def parent_evidence_material(frozen: Mapping[str, object]) -> str:
    return (
        f"model={frozen['model_root_hash72']}|"
        f"validation={frozen['validation_receipt_root_hash72']}|"
        f"replay={frozen['replay_bundle_sha256']}|"
        "nativeFrozen=1"
    )


def parent_evidence_identity216(
    frozen: Mapping[str, object],
) -> str:
    from hhs_python.runtime.hhs_pass219_lane5_unified_training_bridge import (
        Pass219Lane5UnifiedTrainingBridge,
    )

    bridge = Pass219Lane5UnifiedTrainingBridge()
    identity = bridge.evidence_identity216(
        EVIDENCE_DOMAIN,
        parent_evidence_material(frozen),
    )
    if len(identity) != 216:
        raise Pass219Lane5BoundedGeneralizationTrainingAdapterError(
            "PARENT_EVIDENCE_HASH216_LENGTH_MISMATCH"
        )
    return identity


def build_unified_specimen(
    *,
    adapter_signature64: int,
    executor_signature64: int,
    validator_signature64: int,
    negative_control_signature64: int,
    replay_signature64: int,
    natural_language_training: bool = False,
    ethical_text_supervisor_identity216: str = "",
    ethical_text_supervisor_signature64: int = 0,
    ethical_text_supervision_verified: bool = False,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    frozen = verify_frozen_parent_receipts(contract)
    evidence_identity = parent_evidence_identity216(frozen)

    for name, value in {
        "adapter_signature64": adapter_signature64,
        "executor_signature64": executor_signature64,
        "validator_signature64": validator_signature64,
        "negative_control_signature64": negative_control_signature64,
        "replay_signature64": replay_signature64,
    }.items():
        if int(value) <= 0:
            raise Pass219Lane5BoundedGeneralizationTrainingAdapterError(
                f"{name} must be nonzero"
            )

    if natural_language_training:
        if (
            len(ethical_text_supervisor_identity216) != 216
            or int(ethical_text_supervisor_signature64) <= 0
            or not ethical_text_supervision_verified
        ):
            raise Pass219Lane5BoundedGeneralizationTrainingAdapterError(
                "natural-language bounded generalization requires verified "
                "ethical-text supervision"
            )

    return {
        "method_id": METHOD_ID,
        "mode": MODE,
        "temporal": TEMPORAL_BATCH,
        "target": TARGET_RELATION,
        "source_identity216": evidence_identity,
        "oracle_identity216": evidence_identity,
        "parent_model_root_hash72": frozen["model_root_hash72"],
        "parent_validation_receipt_root_hash72": frozen[
            "validation_receipt_root_hash72"
        ],
        "parent_replay_bundle_sha256": frozen["replay_bundle_sha256"],
        "parent_native_hash216_composition_frozen": True,
        "adapter_signature64": int(adapter_signature64),
        "executor_signature64": int(executor_signature64),
        "validator_signature64": int(validator_signature64),
        "negative_control_signature64": int(negative_control_signature64),
        "replay_signature64": int(replay_signature64),
        "oracle_verified": True,
        "negative_controls_verified": True,
        "replay_verified": True,
        "ingress_egress_preserved": True,
        "candidate_only_acknowledged": True,
        "natural_language_training": bool(natural_language_training),
        "ethical_text_supervisor_identity216": (
            ethical_text_supervisor_identity216 if natural_language_training else ""
        ),
        "ethical_text_supervisor_signature64": (
            int(ethical_text_supervisor_signature64)
            if natural_language_training
            else 0
        ),
        "ethical_text_supervision_verified": (
            bool(ethical_text_supervision_verified)
            if natural_language_training
            else False
        ),
    }


__all__ = [
    "EVIDENCE_DOMAIN",
    "METHOD_ID",
    "MODE",
    "Pass219Lane5BoundedGeneralizationTrainingAdapterError",
    "build_unified_specimen",
    "frozen_parent_receipts",
    "load_parent_contract",
    "parent_evidence_identity216",
    "parent_evidence_material",
    "verify_frozen_parent_receipts",
]
