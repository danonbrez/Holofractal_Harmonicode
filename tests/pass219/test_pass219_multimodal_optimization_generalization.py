from __future__ import annotations

import copy
import json
from pathlib import Path

from hhs_runtime.pass219.multimodal_optimization_generalization import (
    GENERALIZE_REQUIRED,
    LOCAL_EXCEPTION_ALLOWED,
    NOT_APPLICABLE,
    OptimizationGeneralizationError,
    VALIDATION_REQUIRED,
    classify_target,
    validate_manifest,
)

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "contracts/pass219/optimization_generalization/PASS_219_OPTIMIZATION_GENERALIZATION_REFERENCE_V1.json"


def load():
    return json.loads(REFERENCE.read_text(encoding="utf-8"))


def main() -> int:
    manifest = load()
    result = validate_manifest(manifest)
    decisions = {row["target"]: row["classification"] for row in result["decisions"]}
    assert decisions["target-vector"] == GENERALIZE_REQUIRED
    assert decisions["target-calibration"] == VALIDATION_REQUIRED
    assert decisions["target-interface"] == LOCAL_EXCEPTION_ALLOWED
    assert decisions["target-other-schema"] == NOT_APPLICABLE

    bad = copy.deepcopy(manifest)
    bad["target_evidence"] = [
        {"logical_object_id":"target-vector","validation_executed":True,"safe":True,"benefit":False}
    ]
    try:
        validate_manifest(bad)
    except OptimizationGeneralizationError as exc:
        assert "REQUIRES_BOUNDED_EXCEPTION" in str(exc)
    else:
        raise AssertionError("negative compatible result bypassed bounded exception")

    target = manifest["targets"][1]
    decision = classify_target(manifest["source"], target, manifest["optimization"], None)
    assert decision["classification"] == VALIDATION_REQUIRED
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
