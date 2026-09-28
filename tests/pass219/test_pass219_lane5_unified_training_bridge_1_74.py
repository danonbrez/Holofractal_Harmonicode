from __future__ import annotations

import pytest

from hhs_python.runtime.hhs_pass219_lane5_unified_training_bridge import (
    METHOD_COUNT,
    VERSION,
    Pass219Lane5UnifiedTrainingBridge,
)


def _frame() -> bytes:
    words = [
        0x9E3779B97F4A7C15 ^ (i * 0x100000001B3)
        for i in range(81)
    ]
    return b"".join((word & ((1 << 64) - 1)).to_bytes(8, "little") for word in words)


def _specimen(method: dict[str, object], identity: str, salt: int) -> dict[str, object]:
    natural = bool(method["natural_language_native"])
    specimen: dict[str, object] = {
        "mode": int(method["mode"]),
        "temporal": int(method["temporal"]),
        "target": int(method["primary_target"]),
        "source_identity216": identity,
        "oracle_identity216": identity,
        "adapter_signature64": 0x1000 + salt,
        "executor_signature64": 0x2000 + salt,
        "validator_signature64": 0x3000 + salt,
        "negative_control_signature64": 0x4000 + salt,
        "replay_signature64": 0x5000 + salt,
        "oracle_verified": True,
        "negative_controls_verified": True,
        "replay_verified": True,
        "ingress_egress_preserved": True,
        "candidate_only_acknowledged": True,
        "natural_language_training": natural,
    }
    if natural:
        specimen.update(
            {
                "ethical_text_supervisor_identity216": identity,
                "ethical_text_supervisor_signature64": 0x6000 + salt,
                "ethical_text_supervision_verified": True,
            }
        )
    return specimen


def test_registry_and_realtime_route_use_native_class() -> None:
    bridge = Pass219Lane5UnifiedTrainingBridge()
    assert bridge.version() == VERSION

    evidence_a = bridge.evidence_identity216(
        "TEST_DOMAIN", "model=A|validation=B|replay=C|nativeFrozen=1"
    )
    evidence_b = bridge.evidence_identity216(
        "TEST_DOMAIN", "model=A|validation=B|replay=C|nativeFrozen=1"
    )
    assert len(evidence_a) == 216
    assert evidence_a == evidence_b

    methods = bridge.methods()
    assert len(methods) == METHOD_COUNT == 19
    assert len({item["method_id"] for item in methods}) == METHOD_COUNT
    assert all(item["routes_through_vm5184"] for item in methods)
    assert all(item["emits_candidate_hash216"] for item in methods)
    assert all(item["candidate_only"] for item in methods)
    bounded = next(
        item for item in methods
        if item["method_id"] == "BOUNDED_TOKEN_GENERALIZATION"
    )
    assert bounded["requires_oracle"] is True
    assert bounded["candidate_only"] is True

    identity = bridge.genesis_identity216()
    assert len(identity) == 216

    realtime = next(item for item in methods if item["method_id"] == "REALTIME_HASH216")
    receipt = bridge.evaluate_raw(_specimen(realtime, identity, 1), _frame())
    assert receipt["accepted"] is True
    assert receipt["vm5184_routed"] is True
    assert receipt["hash216_candidate_derived"] is True
    assert receipt["candidate_only"] is True
    assert receipt["canonical_vm81_mutation_authority"] is False
    assert receipt["canonical_hash72_authority"] is False
    assert receipt["canonical_hash216_authority"] is False
    assert receipt["canonical_persistence_authority"] is False
    assert receipt["floating_point_canonical_authority"] is False
    assert len(receipt["training_candidate_hash216"]) == 216


def test_linguistic_route_requires_ethical_text_supervisor() -> None:
    bridge = Pass219Lane5UnifiedTrainingBridge()
    methods = bridge.methods()
    linguistic = next(item for item in methods if item["method_id"] == "LINGUISTIC_OPERATOR")
    ethical = next(item for item in methods if item["method_id"] == "ETHICAL_TEXT")

    assert linguistic["natural_language_native"] is True
    assert ethical["natural_language_native"] is True
    assert ethical["ethical_text_supervisor"] is True

    identity = bridge.genesis_identity216()
    specimen = _specimen(linguistic, identity, 2)
    receipt = bridge.evaluate_raw(specimen, _frame())
    assert receipt["accepted"] is True
    assert receipt["natural_language_training"] is True
    assert receipt["ethical_text_supervision_required"] is True
    assert receipt["ethical_text_supervision_verified"] is True
    assert receipt["ethical_text_supervisor_identity216"] == identity

    missing = dict(specimen)
    missing["ethical_text_supervision_verified"] = False
    with pytest.raises(ValueError, match="rejected"):
        bridge.evaluate_raw(missing, _frame())

    missing = dict(specimen)
    missing["ethical_text_supervisor_signature64"] = 0
    with pytest.raises(ValueError, match="rejected"):
        bridge.evaluate_raw(missing, _frame())


def test_general_mode_becomes_supervised_when_specimen_is_language() -> None:
    bridge = Pass219Lane5UnifiedTrainingBridge()
    methods = bridge.methods()
    multimodal = next(item for item in methods if item["method_id"] == "MULTIMODAL_INGRESS")
    assert multimodal["natural_language_native"] is False

    identity = bridge.genesis_identity216()
    specimen = _specimen(multimodal, identity, 3)
    specimen.update(
        {
            "natural_language_training": True,
            "ethical_text_supervisor_identity216": identity,
            "ethical_text_supervisor_signature64": 0x7003,
            "ethical_text_supervision_verified": True,
        }
    )
    receipt = bridge.evaluate_raw(specimen, _frame())
    assert receipt["ethical_text_supervision_required"] is True
    assert receipt["ethical_text_supervision_verified"] is True

    missing = dict(specimen)
    missing["ethical_text_supervisor_identity216"] = ""
    with pytest.raises(ValueError, match="rejected"):
        bridge.evaluate_raw(missing, _frame())
