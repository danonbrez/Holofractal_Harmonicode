from __future__ import annotations

from copy import deepcopy

import pytest

from hhs_python.runtime.hhs_pass219_lane5_unified_training_bridge import (
    Pass219Lane5UnifiedTrainingBridge,
)
from hhs_runtime.pass219.lane5_nine_loop_generalization_1_73 import run_generalization
from hhs_runtime.pass219.lane5_bounded_generalization_training_adapter_1_74 import (
    METHOD_ID,
    Pass219Lane5BoundedGeneralizationTrainingAdapterError,
    build_unified_specimen,
    frozen_parent_receipts,
    load_parent_contract,
    parent_evidence_identity216,
    verify_frozen_parent_receipts,
)


def _vm5184_frame() -> bytes:
    words = [
        0x9E3779B97F4A7C15 ^ (i * 0x100000001B3)
        for i in range(81)
    ]
    return b"".join(
        (word & ((1 << 64) - 1)).to_bytes(8, "little")
        for word in words
    )


def test_merged_parent_receipts_are_frozen_and_reproducible() -> None:
    contract = load_parent_contract()
    frozen = frozen_parent_receipts(contract)
    observed = run_generalization()

    assert frozen["model_root_hash72"] == observed["model_root_hash72"]
    assert frozen["validation_receipt_root_hash72"] == observed[
        "validation_receipt_root_hash72"
    ]
    assert frozen["replay_bundle_sha256"] == observed["replay_bundle_sha256"]
    assert frozen["native_hash216_composition_frozen"] is True

    verified = verify_frozen_parent_receipts(contract)
    assert verified == frozen


def test_native_evidence_identity_is_deterministic() -> None:
    frozen = verify_frozen_parent_receipts()
    first = parent_evidence_identity216(frozen)
    second = parent_evidence_identity216(frozen)
    assert len(first) == 216
    assert first == second


def test_frozen_parent_builds_method_19_specimen() -> None:
    specimen = build_unified_specimen(
        adapter_signature64=0x1001,
        executor_signature64=0x2001,
        validator_signature64=0x3001,
        negative_control_signature64=0x4001,
        replay_signature64=0x5001,
    )
    assert specimen["method_id"] == METHOD_ID == "BOUNDED_TOKEN_GENERALIZATION"
    assert specimen["mode"] == 19
    assert specimen["temporal"] == 3
    assert specimen["target"] == 1
    assert len(specimen["source_identity216"]) == 216
    assert specimen["source_identity216"] == specimen["oracle_identity216"]
    assert specimen["parent_native_hash216_composition_frozen"] is True

    observed = run_generalization()
    assert specimen["parent_model_root_hash72"] == observed["model_root_hash72"]
    assert specimen["parent_validation_receipt_root_hash72"] == observed[
        "validation_receipt_root_hash72"
    ]
    assert specimen["parent_replay_bundle_sha256"] == observed["replay_bundle_sha256"]
    assert specimen["oracle_verified"] is True
    assert specimen["negative_controls_verified"] is True
    assert specimen["replay_verified"] is True
    assert specimen["candidate_only_acknowledged"] is True


def test_missing_native_freeze_fails_closed() -> None:
    contract = deepcopy(load_parent_contract())
    contract["frozen_receipts"]["native_hash216_composition_frozen"] = False
    with pytest.raises(
        Pass219Lane5BoundedGeneralizationTrainingAdapterError,
        match="UNFROZEN_PARENT_RECEIPTS",
    ):
        frozen_parent_receipts(contract)


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
        )

    frozen = verify_frozen_parent_receipts()
    supervisor = parent_evidence_identity216(frozen)
    specimen = build_unified_specimen(
        adapter_signature64=1,
        executor_signature64=2,
        validator_signature64=3,
        negative_control_signature64=4,
        replay_signature64=5,
        natural_language_training=True,
        ethical_text_supervisor_identity216=supervisor,
        ethical_text_supervisor_signature64=6,
        ethical_text_supervision_verified=True,
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
        )


def test_frozen_receipts_must_match_recomputed_pass123_discovery() -> None:
    contract = deepcopy(load_parent_contract())
    contract["frozen_receipts"]["replay_bundle_sha256"] = "f" * 64
    with pytest.raises(
        Pass219Lane5BoundedGeneralizationTrainingAdapterError,
        match="FROZEN_PARENT_RECEIPT_MISMATCH",
    ):
        verify_frozen_parent_receipts(contract)


def test_merged_1_73_specimen_executes_through_unified_vm5184_route() -> None:
    specimen = build_unified_specimen(
        adapter_signature64=0x7101,
        executor_signature64=0x7102,
        validator_signature64=0x7103,
        negative_control_signature64=0x7104,
        replay_signature64=0x7105,
    )
    bridge = Pass219Lane5UnifiedTrainingBridge()
    receipt = bridge.evaluate_raw(specimen, _vm5184_frame())

    assert receipt["accepted"] is True
    assert receipt["mode"] == 19
    assert receipt["method_index"] == 18
    assert receipt["source_identity216"] == specimen["source_identity216"]
    assert receipt["oracle_identity216"] == specimen["oracle_identity216"]
    assert receipt["vm5184_routed"] is True
    assert receipt["hash216_candidate_derived"] is True
    assert len(receipt["training_candidate_hash216"]) == 216
    assert receipt["candidate_only"] is True
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash72_authority"] is False
    assert receipt["canonical_hash216_authority"] is False
    assert receipt["canonical_persistence_authority"] is False
    assert receipt["floating_point_canonical_authority"] is False


def test_natural_language_1_73_specimen_keeps_ethical_supervisor_through_vm5184() -> None:
    frozen = verify_frozen_parent_receipts()
    supervisor = parent_evidence_identity216(frozen)
    specimen = build_unified_specimen(
        adapter_signature64=0x7201,
        executor_signature64=0x7202,
        validator_signature64=0x7203,
        negative_control_signature64=0x7204,
        replay_signature64=0x7205,
        natural_language_training=True,
        ethical_text_supervisor_identity216=supervisor,
        ethical_text_supervisor_signature64=0x7206,
        ethical_text_supervision_verified=True,
    )
    receipt = Pass219Lane5UnifiedTrainingBridge().evaluate_raw(
        specimen,
        _vm5184_frame(),
    )
    assert receipt["accepted"] is True
    assert receipt["natural_language_training"] is True
    assert receipt["ethical_text_supervision_required"] is True
    assert receipt["ethical_text_supervision_verified"] is True
    assert receipt["ethical_text_supervisor_identity216"] == supervisor
