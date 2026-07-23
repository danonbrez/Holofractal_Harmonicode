from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from math import log2
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash

PASS_ID = "PASS_123"
EXAMPLE_SCHEMA = "HHS_TYPED_TOKEN_GENERALIZATION_EXAMPLE_V1"
MODEL_SCHEMA = "HHS_INVARIANT_TOKEN_GENERALIZATION_MODEL_V1"
VALIDATION_SCHEMA = "HHS_CROSS_TOKEN_GENERALIZATION_VALIDATION_V1"
APPLICATION_SCHEMA = "HHS_TOKEN_GENERALIZATION_APPLICATION_V1"
REPLAY_SCHEMA = "HHS_TOKEN_GENERALIZATION_REPLAY_RECEIPT_V1"

TOKEN_CLASSES = (
    "TEXT", "MATHEMATICS", "CODE", "JSON", "IMAGE_REGION", "AUDIO_SEGMENT",
    "VIDEO_INTERVAL", "VM81_STATE", "TENSOR_CELL", "SYMBOLIC_EXPRESSION",
)

REJECTION_CODES = {
    "REJECT_UNKNOWN_TOKEN_CLASS",
    "REJECT_MISSING_TOKEN_PROVENANCE",
    "REJECT_EXAMPLE_ROOT_MISMATCH",
    "REJECT_LABEL_CONFLICT",
    "REJECT_CLASS_COLLAPSE",
    "REJECT_TRAINING_HOLDOUT_LEAKAGE",
    "REJECT_OVERFIT_RULE",
    "REJECT_SEMANTIC_DRIFT",
    "REJECT_ENTROPY_BUDGET_EXCEEDED",
    "REJECT_UNSUPPORTED_FEATURE_VALUE",
    "REJECT_UNVALIDATED_GENERALIZATION",
    "REJECT_MODEL_ROOT_MISMATCH",
    "REJECT_REPLAY_MISMATCH",
    "REJECT_UNBOUNDED_GENERALIZATION_REQUEST",
}


class Pass123Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


def _canon(value: Any) -> Any:
    if isinstance(value, bool) or value is None or isinstance(value, (str, int)):
        return value
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, tuple):
        return [_canon(v) for v in value]
    if isinstance(value, list):
        return [_canon(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _canon(value[k]) for k in sorted(value)}
    raise Pass123Error("REJECT_UNSUPPORTED_FEATURE_VALUE", type(value).__name__)


@dataclass(frozen=True)
class GeneralizationBounds:
    max_examples: int = 4096
    max_features_per_example: int = 64
    max_rules: int = 256
    max_model_bits: int = 1_000_000
    max_entropy_growth_bits: int = 4096


class BoundedTokenGeneralizationEngine:
    """Deterministic invariant generalization across token classes with holdout and entropy controls."""

    def __init__(self, bounds: GeneralizationBounds | None = None):
        self.bounds = bounds or GeneralizationBounds()
        if min(self.bounds.max_examples, self.bounds.max_features_per_example, self.bounds.max_rules, self.bounds.max_model_bits) <= 0:
            raise Pass123Error("REJECT_UNBOUNDED_GENERALIZATION_REQUEST", "positive bounds required")

    def make_example(self, *, token_class: str, token_identity: str, features: Mapping[str, Any], label: str,
                     provenance_root_hash72: str, semantic_root_hash72: str) -> dict[str, Any]:
        if token_class not in TOKEN_CLASSES:
            raise Pass123Error("REJECT_UNKNOWN_TOKEN_CLASS", token_class)
        if not provenance_root_hash72 or not semantic_root_hash72:
            raise Pass123Error("REJECT_MISSING_TOKEN_PROVENANCE", token_identity)
        if len(features) > self.bounds.max_features_per_example:
            raise Pass123Error("REJECT_UNBOUNDED_GENERALIZATION_REQUEST", "feature count")
        obj = {
            "schema": EXAMPLE_SCHEMA,
            "pass_id": PASS_ID,
            "token_class": token_class,
            "token_identity": str(token_identity),
            "features": _canon(features),
            "label": str(label),
            "provenance_root_hash72": provenance_root_hash72,
            "semantic_root_hash72": semantic_root_hash72,
        }
        obj["example_root_hash72"] = _hash("hhs_pass123_example_v1", obj)
        return obj

    def train(self, examples: Sequence[Mapping[str, Any]], *, holdout_example_roots: Sequence[str] = ()) -> dict[str, Any]:
        if not examples or len(examples) > self.bounds.max_examples:
            raise Pass123Error("REJECT_UNBOUNDED_GENERALIZATION_REQUEST", "example count")
        verified = [self._verify_example(x) for x in examples]
        holdout = set(holdout_example_roots)
        if any(x["example_root_hash72"] in holdout for x in verified):
            raise Pass123Error("REJECT_TRAINING_HOLDOUT_LEAKAGE", "holdout example included in training")

        by_signature: dict[tuple[tuple[str, str], ...], dict[str, Any]] = {}
        for ex in verified:
            signature = self._invariant_signature(ex)
            key = tuple((k, repr(v)) for k, v in signature.items())
            prior = by_signature.get(key)
            if prior and prior["label"] != ex["label"]:
                raise Pass123Error("REJECT_LABEL_CONFLICT", ex["token_identity"])
            if prior is None:
                by_signature[key] = {
                    "signature": signature,
                    "label": ex["label"],
                    "support": 0,
                    "token_classes": set(),
                    "example_roots": [],
                }
            item = by_signature[key]
            item["support"] += 1
            item["token_classes"].add(ex["token_class"])
            item["example_roots"].append(ex["example_root_hash72"])

        if len(by_signature) > self.bounds.max_rules:
            raise Pass123Error("REJECT_OVERFIT_RULE", "rule count exceeds bound")

        rules = []
        for i, item in enumerate(sorted(by_signature.values(), key=lambda x: (repr(x["signature"]), x["label"]))):
            # Rules must be representation-invariant: no identity, provenance, class, or semantic-root keys.
            forbidden = {"token_identity", "token_class", "provenance_root_hash72", "semantic_root_hash72"}
            if forbidden.intersection(item["signature"]):
                raise Pass123Error("REJECT_OVERFIT_RULE", "identity-bearing feature")
            rule = {
                "rule_id": f"R{i:04d}",
                "invariant_signature": item["signature"],
                "label": item["label"],
                "support": item["support"],
                "observed_token_classes": sorted(item["token_classes"]),
                "training_example_roots": sorted(item["example_roots"]),
            }
            rule["rule_root_hash72"] = _hash("hhs_pass123_rule_v1", rule)
            rules.append(rule)

        labels = sorted({x["label"] for x in verified})
        classes = sorted({x["token_class"] for x in verified})
        model = {
            "schema": MODEL_SCHEMA,
            "pass_id": PASS_ID,
            "rules": rules,
            "rule_count": len(rules),
            "training_example_count": len(verified),
            "training_example_roots": sorted(x["example_root_hash72"] for x in verified),
            "label_vocabulary": labels,
            "observed_token_classes": classes,
            "identity_features_permitted": False,
            "class_specific_shortcuts_permitted": False,
            "validated": False,
        }
        model_bits = len(repr(_canon(model)).encode("utf-8")) * 8
        if model_bits > self.bounds.max_model_bits:
            raise Pass123Error("REJECT_ENTROPY_BUDGET_EXCEEDED", "model size")
        model["model_size_bits"] = model_bits
        model["model_root_hash72"] = _hash("hhs_pass123_model_v1", model)
        return model

    def validate(self, model: Mapping[str, Any], holdout_examples: Sequence[Mapping[str, Any]], *, require_all_classes: bool = True) -> dict[str, Any]:
        m = self._verify_model(model)
        if not holdout_examples or len(holdout_examples) > self.bounds.max_examples:
            raise Pass123Error("REJECT_UNBOUNDED_GENERALIZATION_REQUEST", "holdout count")
        examples = [self._verify_example(x) for x in holdout_examples]
        training_roots = set(m["training_example_roots"])
        if any(x["example_root_hash72"] in training_roots for x in examples):
            raise Pass123Error("REJECT_TRAINING_HOLDOUT_LEAKAGE", "training example reused")

        results = []
        correct = 0
        covered_classes = set()
        for ex in examples:
            app = self._apply_unvalidated(m, ex)
            predicted = app["predicted_label"]
            ok = predicted == ex["label"]
            correct += int(ok)
            covered_classes.add(ex["token_class"])
            results.append({
                "example_root_hash72": ex["example_root_hash72"],
                "token_class": ex["token_class"],
                "expected_label": ex["label"],
                "predicted_label": predicted,
                "correct": ok,
                "matched_rule_root_hash72": app["matched_rule_root_hash72"],
                "semantic_root_preserved": app["semantic_root_hash72"] == ex["semantic_root_hash72"],
            })
        if correct != len(examples):
            raise Pass123Error("REJECT_SEMANTIC_DRIFT", f"{correct}/{len(examples)} holdout correct")
        if require_all_classes and set(TOKEN_CLASSES) - covered_classes:
            raise Pass123Error("REJECT_CLASS_COLLAPSE", "holdout does not cover every declared token class")

        baseline_bits = sum(len(repr(_canon(x)).encode("utf-8")) * 8 for x in examples)
        receipt_bits = len(repr(_canon(results)).encode("utf-8")) * 8
        growth = max(0, receipt_bits - baseline_bits)
        if growth > self.bounds.max_entropy_growth_bits:
            raise Pass123Error("REJECT_ENTROPY_BUDGET_EXCEEDED", "validation receipt growth")

        receipt = {
            "schema": VALIDATION_SCHEMA,
            "model_root_hash72": m["model_root_hash72"],
            "holdout_example_roots": sorted(x["example_root_hash72"] for x in examples),
            "results": results,
            "accuracy": {"numerator": correct, "denominator": len(examples)},
            "covered_token_classes": sorted(covered_classes),
            "all_declared_classes_covered": set(TOKEN_CLASSES) <= covered_classes,
            "semantic_drift_count": 0,
            "entropy_growth_bits": growth,
            "validation_status": "CROSS_TOKEN_GENERALIZATION_VALIDATED",
        }
        receipt["validation_receipt_root_hash72"] = _hash("hhs_pass123_validation_v1", receipt)
        validated_model = deepcopy(m)
        validated_model.pop("model_root_hash72")
        validated_model["validated"] = True
        validated_model["validation_receipt_root_hash72"] = receipt["validation_receipt_root_hash72"]
        validated_model["model_root_hash72"] = _hash("hhs_pass123_model_v1", validated_model)
        return {"validated_model": validated_model, "validation_receipt": receipt}

    def apply(self, validated_model: Mapping[str, Any], example: Mapping[str, Any]) -> dict[str, Any]:
        model = self._verify_model(validated_model)
        if model.get("validated") is not True or not model.get("validation_receipt_root_hash72"):
            raise Pass123Error("REJECT_UNVALIDATED_GENERALIZATION", "model lacks validation receipt")
        ex = self._verify_example(example)
        result = self._apply_unvalidated(model, ex)
        result.update({"schema": APPLICATION_SCHEMA, "model_root_hash72": model["model_root_hash72"], "application_status": "INVARIANT_GENERALIZATION_APPLIED"})
        result["application_root_hash72"] = _hash("hhs_pass123_application_v1", result)
        return result

    def replay(self, validated_model: Mapping[str, Any], example: Mapping[str, Any], expected_application: Mapping[str, Any]) -> dict[str, Any]:
        actual = self.apply(validated_model, example)
        if actual["application_root_hash72"] != expected_application.get("application_root_hash72"):
            raise Pass123Error("REJECT_REPLAY_MISMATCH", "application root")
        receipt = {
            "schema": REPLAY_SCHEMA,
            "model_root_hash72": actual["model_root_hash72"],
            "example_root_hash72": actual["example_root_hash72"],
            "application_root_hash72": actual["application_root_hash72"],
            "replay_status": "DETERMINISTIC_GENERALIZATION_REPLAY_VALIDATED",
        }
        receipt["replay_receipt_root_hash72"] = _hash("hhs_pass123_replay_v1", receipt)
        return receipt

    def _apply_unvalidated(self, model: Mapping[str, Any], ex: Mapping[str, Any]) -> dict[str, Any]:
        signature = self._invariant_signature(ex)
        matches = [r for r in model["rules"] if r["invariant_signature"] == signature]
        if len(matches) != 1:
            raise Pass123Error("REJECT_SEMANTIC_DRIFT", f"rule match count {len(matches)}")
        rule = matches[0]
        return {
            "example_root_hash72": ex["example_root_hash72"],
            "token_class": ex["token_class"],
            "semantic_root_hash72": ex["semantic_root_hash72"],
            "predicted_label": rule["label"],
            "matched_rule_root_hash72": rule["rule_root_hash72"],
            "invariant_signature": signature,
        }

    @staticmethod
    def _invariant_signature(ex: Mapping[str, Any]) -> dict[str, Any]:
        # Features explicitly marked representation-local are excluded from generalization.
        return {k: deepcopy(v) for k, v in ex["features"].items() if not k.startswith("local_")}

    def _verify_example(self, example: Mapping[str, Any]) -> dict[str, Any]:
        body = deepcopy(dict(example)); root = body.pop("example_root_hash72", None)
        if root != _hash("hhs_pass123_example_v1", body):
            raise Pass123Error("REJECT_EXAMPLE_ROOT_MISMATCH", str(example.get("token_identity")))
        if body.get("token_class") not in TOKEN_CLASSES:
            raise Pass123Error("REJECT_UNKNOWN_TOKEN_CLASS", str(body.get("token_class")))
        body["example_root_hash72"] = root
        return body

    def _verify_model(self, model: Mapping[str, Any]) -> dict[str, Any]:
        body = deepcopy(dict(model)); root = body.pop("model_root_hash72", None)
        if root != _hash("hhs_pass123_model_v1", body):
            raise Pass123Error("REJECT_MODEL_ROOT_MISMATCH", "model root")
        body["model_root_hash72"] = root
        return body


def _demo_examples(engine: BoundedTokenGeneralizationEngine, suffix: str) -> list[dict[str, Any]]:
    out = []
    for token_class in TOKEN_CLASSES:
        out.append(engine.make_example(
            token_class=token_class,
            token_identity=f"{token_class}:{suffix}",
            features={"relation": "RECIPROCAL_CLOSED", "arity": 2, "local_encoding": f"{token_class}:{suffix}"},
            label="ADMISSIBLE_CLOSED_RELATION",
            provenance_root_hash72=_hash("hhs_pass123_demo_provenance", {"token_class": token_class, "suffix": suffix}),
            semantic_root_hash72=_hash("hhs_pass123_demo_semantic", {"relation": "RECIPROCAL_CLOSED", "suffix": suffix}),
        ))
    return out


def pass123_self_test() -> dict[str, Any]:
    engine = BoundedTokenGeneralizationEngine()
    train = _demo_examples(engine, "train")
    holdout = _demo_examples(engine, "holdout")
    model = engine.train(train, holdout_example_roots=[x["example_root_hash72"] for x in holdout])
    validated = engine.validate(model, holdout)
    application = engine.apply(validated["validated_model"], holdout[0])
    replay = engine.replay(validated["validated_model"], holdout[0], application)
    return {
        "ok": replay["replay_status"] == "DETERMINISTIC_GENERALIZATION_REPLAY_VALIDATED",
        "model_root_hash72": validated["validated_model"]["model_root_hash72"],
        "validation_receipt_root_hash72": validated["validation_receipt"]["validation_receipt_root_hash72"],
        "token_class_count": len(TOKEN_CLASSES),
        "semantic_drift_count": validated["validation_receipt"]["semantic_drift_count"],
        "entropy_growth_bits": validated["validation_receipt"]["entropy_growth_bits"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(pass123_self_test(), indent=2, sort_keys=True))
