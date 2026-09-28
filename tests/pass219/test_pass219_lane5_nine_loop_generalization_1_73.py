from __future__ import annotations

import copy

import pytest

from hhs_runtime.hhs_pass123_bounded_token_generalization_v1 import Pass123Error
from hhs_runtime.pass219.lane5_nine_loop_generalization_1_73 import (
    Lane5NineLoopGeneralizationError,
    _engine,
    assert_pass123_leakage_rejected,
    build_examples,
    run_generalization,
)


def test_disjoint_generalization_closes_exactly():
    receipt = run_generalization()
    assert all(receipt["checks"].values())
    assert receipt["training_example_count"] == 12
    assert receipt["holdout_example_count"] == 12
    assert receipt["rule_count"] == 12
    assert receipt["accuracy"] == {"numerator": 12, "denominator": 12}
    assert receipt["semantic_drift_count"] == 0
    assert receipt["replay_count"] == 12
    assert receipt["validated_model_only"] is True
    assert receipt["model_weight_update_authority"] is False
    assert receipt["learning_commit_authority"] is False
    assert receipt["canonical_transition_ready"] is False


def test_training_holdout_leakage_is_rejected():
    assert assert_pass123_leakage_rejected() == "REJECT_TRAINING_HOLDOUT_LEAKAGE"


def test_identity_and_projection_do_not_enter_invariant_signature():
    examples = build_examples()
    engine = _engine()
    train = examples["training"][0]
    holdout = examples["holdout"][0]
    assert train["token_identity"] != holdout["token_identity"]
    assert train["token_class"] != holdout["token_class"]
    assert train["features"]["local_projection"] != holdout["features"]["local_projection"]
    assert engine._invariant_signature(train) == engine._invariant_signature(holdout)


def test_semantic_feature_tamper_rejects_holdout():
    examples = build_examples()
    engine = _engine()
    training = examples["training"]
    holdout = copy.deepcopy(examples["holdout"])
    model = engine.train(
        training,
        holdout_example_roots=[x["example_root_hash72"] for x in holdout],
    )
    # Rebuild the tampered example through the public constructor so its root is valid.
    original = holdout[0]
    tampered_features = copy.deepcopy(original["features"])
    tampered_features["expected_mapping"] = "TAMPERED_MAPPING"
    tampered = engine.make_example(
        token_class=original["token_class"],
        token_identity="1.73:holdout:tampered",
        features=tampered_features,
        label=original["label"],
        provenance_root_hash72=original["provenance_root_hash72"],
        semantic_root_hash72=original["semantic_root_hash72"],
    )
    with pytest.raises(Pass123Error) as exc:
        engine.validate(model, [tampered], require_all_classes=False)
    assert exc.value.code == "REJECT_SEMANTIC_DRIFT"


def test_unvalidated_model_cannot_apply():
    examples = build_examples()
    engine = _engine()
    model = engine.train(
        examples["training"],
        holdout_example_roots=[x["example_root_hash72"] for x in examples["holdout"]],
    )
    with pytest.raises(Pass123Error) as exc:
        engine.apply(model, examples["holdout"][0])
    assert exc.value.code == "REJECT_UNVALIDATED_GENERALIZATION"
