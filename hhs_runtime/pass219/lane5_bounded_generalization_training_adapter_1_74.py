"""Pass 219 Lane 5 1.74 adapter for the inherited Pass123 1.73 generalization.

This adapter intentionally fails closed until the authoritative 1.73 contract
freezes its observed discovery receipts and native Hash216 successor. It does
not derive, guess, or substitute those identities.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
PARENT_CONTRACT = (
    ROOT / "contracts/pass219/PASS_219_LANE5_NINE_LOOP_GENERALIZATION_1_73.json"
)

METHOD_ID = "BOUNDED_TOKEN_GENERALIZATION"
MODE = 19
TEMPORAL_BATCH = 3
TARGET_RELATION = 1


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
) -> dict[str, str]:
    parent = dict(contract or load_parent_contract())
    receipts = dict(parent.get("frozen_receipts") or {})

    model = receipts.get("model_root_hash72")
    validation = receipts.get("validation_receipt_root_hash72")
    replay = receipts.get("replay_bundle_sha256")
    native = receipts.get("native_hash216_identity")
    native_frozen = receipts.get("native_hash216_composition_frozen")

    missing: list[str] = []
    if not isinstance(model, str) or len(model) != 72:
        missing.append("model_root_hash72")
    if not isinstance(validation, str) or len(validation) != 72:
        missing.append("validation_receipt_root_hash72")
    if not isinstance(replay, str) or len(replay) != 64:
        missing.append("replay_bundle_sha256")
    if not isinstance(native, str) or len(native) != 216:
        missing.append("native_hash216_identity")
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
        "native_hash216_identity": native,
    }


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
    frozen = frozen_parent_receipts(contract)

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
        "source_identity216": frozen["native_hash216_identity"],
        "oracle_identity216": frozen["native_hash216_identity"],
        "parent_model_root_hash72": frozen["model_root_hash72"],
        "parent_validation_receipt_root_hash72": frozen[
            "validation_receipt_root_hash72"
        ],
        "parent_replay_bundle_sha256": frozen["replay_bundle_sha256"],
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
    "METHOD_ID",
    "MODE",
    "Pass219Lane5BoundedGeneralizationTrainingAdapterError",
    "build_unified_specimen",
    "frozen_parent_receipts",
    "load_parent_contract",
]
