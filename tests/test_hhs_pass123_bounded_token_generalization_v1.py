from copy import deepcopy
import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass123_bounded_token_generalization_v1 import (
    BoundedTokenGeneralizationEngine, GeneralizationBounds, Pass123Error,
    TOKEN_CLASSES, _demo_examples, pass123_self_test,
)


def build():
    e = BoundedTokenGeneralizationEngine()
    train = _demo_examples(e, "train")
    hold = _demo_examples(e, "hold")
    model = e.train(train, holdout_example_roots=[x["example_root_hash72"] for x in hold])
    validated = e.validate(model, hold)
    return e, train, hold, model, validated


def test_all_token_classes_are_declared_and_covered():
    _, _, _, _, v = build()
    assert len(TOKEN_CLASSES) == 10
    assert v["validation_receipt"]["all_declared_classes_covered"] is True


def test_generalization_ignores_representation_local_features():
    e, _, hold, _, v = build()
    x = deepcopy(hold[0]); x.pop("example_root_hash72"); x["features"]["local_encoding"] = "completely-different"
    x["example_root_hash72"] = _hash("hhs_pass123_example_v1", x)
    result = e.apply(v["validated_model"], x)
    assert result["predicted_label"] == "ADMISSIBLE_CLOSED_RELATION"


def test_semantic_root_is_preserved_on_application():
    e, _, hold, _, v = build(); r=e.apply(v["validated_model"], hold[0])
    assert r["semantic_root_hash72"] == hold[0]["semantic_root_hash72"]


def test_training_holdout_leakage_rejected():
    e=BoundedTokenGeneralizationEngine(); xs=_demo_examples(e,"same")
    with pytest.raises(Pass123Error) as z: e.train(xs, holdout_example_roots=[xs[0]["example_root_hash72"]])
    assert z.value.code == "REJECT_TRAINING_HOLDOUT_LEAKAGE"


def test_conflicting_labels_for_same_invariant_rejected():
    e=BoundedTokenGeneralizationEngine(); xs=_demo_examples(e,"a")[:2]
    y=deepcopy(xs[1]); y.pop("example_root_hash72"); y["label"]="REJECT"; y["example_root_hash72"]=_hash("hhs_pass123_example_v1",y)
    with pytest.raises(Pass123Error) as z: e.train([xs[0],y])
    assert z.value.code == "REJECT_LABEL_CONFLICT"


def test_class_collapse_rejected_when_holdout_omits_declared_classes():
    e=BoundedTokenGeneralizationEngine(); train=_demo_examples(e,"t"); hold=_demo_examples(e,"h")[:2]
    m=e.train(train,holdout_example_roots=[x["example_root_hash72"] for x in hold])
    with pytest.raises(Pass123Error) as z: e.validate(m,hold,require_all_classes=True)
    assert z.value.code == "REJECT_CLASS_COLLAPSE"


def test_semantic_drift_rejected_on_unseen_invariant():
    e,_,hold,m,_=build(); bad=deepcopy(hold); x=bad[0]; x.pop("example_root_hash72"); x["features"]["relation"]="DIFFERENT"; x["example_root_hash72"]=_hash("hhs_pass123_example_v1",x)
    with pytest.raises(Pass123Error) as z: e.validate(m,bad)
    assert z.value.code == "REJECT_SEMANTIC_DRIFT"


def test_unvalidated_model_cannot_apply():
    e,_,hold,m,_=build()
    with pytest.raises(Pass123Error) as z: e.apply(m,hold[0])
    assert z.value.code == "REJECT_UNVALIDATED_GENERALIZATION"


def test_model_tamper_rejected():
    e,_,hold,_,v=build(); bad=deepcopy(v["validated_model"]); bad["rules"][0]["label"]="tampered"
    with pytest.raises(Pass123Error) as z: e.apply(bad,hold[0])
    assert z.value.code == "REJECT_MODEL_ROOT_MISMATCH"


def test_example_tamper_rejected():
    e,_,hold,_,v=build(); bad=deepcopy(hold[0]); bad["features"]["arity"]=99
    with pytest.raises(Pass123Error) as z: e.apply(v["validated_model"],bad)
    assert z.value.code == "REJECT_EXAMPLE_ROOT_MISMATCH"


def test_entropy_budget_enforced():
    e=BoundedTokenGeneralizationEngine(GeneralizationBounds(max_model_bits=128))
    with pytest.raises(Pass123Error) as z: e.train(_demo_examples(e,"train"))
    assert z.value.code == "REJECT_ENTROPY_BUDGET_EXCEEDED"


def test_deterministic_replay():
    e,_,hold,_,v=build(); a=e.apply(v["validated_model"],hold[0]); r=e.replay(v["validated_model"],hold[0],a)
    assert r["replay_status"] == "DETERMINISTIC_GENERALIZATION_REPLAY_VALIDATED"


def test_unknown_token_class_rejected():
    e=BoundedTokenGeneralizationEngine()
    with pytest.raises(Pass123Error) as z: e.make_example(token_class="UNKNOWN",token_identity="x",features={},label="x",provenance_root_hash72="p",semantic_root_hash72="s")
    assert z.value.code == "REJECT_UNKNOWN_TOKEN_CLASS"


def test_self_test(): assert pass123_self_test()["ok"] is True


def test_registry():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    svc=next(x for x in make_default_service_registry().services() if x["name"]=="runtime.bounded_token_generalization.pass123")
    assert svc["conformance_decision"]["derivation_complete"] is True
