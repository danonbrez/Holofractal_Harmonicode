from __future__ import annotations

import pytest

from hhs_runtime.pass219.lane5_bounded_generalization_training_adapter_1_74 import (
    METHOD_ID,
    Pass219Lane5BoundedGeneralizationTrainingAdapterError,
    build_unified_specimen,
    frozen_parent_receipts,
    load_parent_contract,
)


def _frozen_contract() -> dict[str, object]:
    contract = load_parent_contract()
    contract = dict(contract)
    contract["frozen_receipts"] = {
        "model_root_hash72": "0" * 72,
        "validation_receipt_root_hash72": "1" * 72,
        "replay_bundle_sha256": "a" * 64,
        "native_hash216_identity": "2" * 216,
        "native_hash216_composition_frozen": True,
    }
    return contract


def test_current_parent_is_intentionally_unfrozen() -> None:
    contract = load_parent_contract()
    with pytest.raises(
        Pass219Lane5BoundedGeneralizationTrainingAdapterError,
        match="UNFROZEN_PARENT_RECEIPTS",
    ):
        frozen_parent_receipts(contract)


def test_frozen_parent_builds_method_19_specimen() -> None:
    specimen = build_unified_specimen(
        adapter_signature64=0x1001,
        executor_signature64=0x2001,
        validator_signature64=0x3001,
        negative_control_signature64=0x4001,
        replay_signature64=0x5001,
        contract=_frozen_contract(),
    )
    assert specimen["method_id"] == METHOD_ID == "BOUNDED_TOKEN_GENERALIZATION"
    assert specimen["mode"] == 19
    assert specimen["temporal"] == 3
    assert specimen["target"] == 1
    assert specimen["source_identity216"] == "2" * 216
    assert specimen["oracle_identity216"] == "2" * 216
    assert specimen["parent_model_root_hash72"] == "0" * 72
    assert specimen["parent_validation_receipt_root_hash72"] == "1" * 72
    assert specimen["parent_replay_bundle_sha256"] == "a" * 64
    assert specimen["oracle_verified"] is True
    assert specimen["negative_controls_verified"] is True
    assert specimen["replay_verified"] is True
    assert specimen["candidate_only_acknowledged"] is True


def test_natural_language_generalization_requires_ethical_supervisor() -> None:
    with pytest.raises(
        Pass219Lane5BoundedGeneralizationTrainingAdapterError,
        match="ethical-text supervision",
    ):
        build_unified_specimen(
            adapter_signature64=1,
            executor_signature64=2,
            validator_signature64=3,
            negative_control_signature64=4,
            replay_signature64=5,
            natural_language_training=True,
            contract=_frozen_contract(),
        )

    specimen = build_unified_specimen(
        adapter_signature64=1,
        executor_signature64=2,
        validator_signature64=3,
        negative_control_signature64=4,
        replay_signature64=5,
        natural_language_training=True,
        ethical_text_supervisor_identity216="3" * 216,
        ethical_text_supervisor_signature64=6,
        ethical_text_supervision_verified=True,
        contract=_frozen_contract(),
    )
    assert specimen["natural_language_training"] is True
    assert specimen["ethical_text_supervision_verified"] is True


def test_zero_execution_signatures_fail_closed() -> None:
    with pytest.raises(
        Pass219Lane5BoundedGeneralizationTrainingAdapterError,
        match="adapter_signature64 must be nonzero",
    ):
        build_unified_specimen(
            adapter_signature64=0,
            executor_signature64=2,
            validator_signature64=3,
            negative_control_signature64=4,
            replay_signature64=5,
            contract=_frozen_contract(),
        )
