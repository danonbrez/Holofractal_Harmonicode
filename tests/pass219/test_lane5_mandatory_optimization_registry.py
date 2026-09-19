from __future__ import annotations

import json
from pathlib import Path

import pytest

from hhs_runtime.pass219.lane5_mandatory_optimization_dispatcher import (
    Pass219Lane5MandatoryOptimizationDispatcher,
)
from hhs_runtime.pass219.lane5_mandatory_optimization_registry import (
    Lane5MandatoryOptimizationRegistryError,
    build_mandatory_optimization_registry,
)


def test_repository_generalization_manifests_are_visible_to_lane5_agent():
    registry = build_mandatory_optimization_registry()
    assert registry["manifest_count"] > 0
    assert registry["generalize_required_count"] > 0
    assert registry["typed_applicability_preserved"] is True
    assert registry["unvalidated_targets_are_not_promoted"] is True
    assert registry["bounded_local_exceptions_preserved"] is True
    assert registry["canonical_authority_granted"] is False
    assert len(registry["registry_sha256"]) == 64

    by_id = {row["optimization_id"]: row for row in registry["manifests"]}
    branch = by_id["H36_BRANCH_REFERENCE_CACHE_1_17"]
    assert "h36-branch-reference-cache-1-17-linux-x86_64" in branch[
        "generalize_required"
    ]
    assert len(branch["manifest_sha256"]) == 64


def test_agent_status_contains_validated_manifest_registry(tmp_path: Path):
    with Pass219Lane5MandatoryOptimizationDispatcher(
        backend="CPU_REFERENCE",
        state_root=tmp_path / "lane5",
    ) as dispatcher:
        status = dispatcher.status()
    registry = status["optimization_generalization_registry"]
    assert status["manifest_proven_optimizations_visible"] is True
    assert registry["generalize_required_count"] > 0
    assert any(
        row["optimization_id"] == "H36_BRANCH_REFERENCE_CACHE_1_17"
        for row in registry["manifests"]
    )


def test_manifest_coverage_drift_fails_closed(tmp_path: Path):
    root = tmp_path
    directory = root / "contracts" / "pass219" / "optimization_generalization"
    directory.mkdir(parents=True)
    manifest = {
        "schema": "HHS_PASS_219_OPTIMIZATION_GENERALIZATION_MANIFEST_V1",
        "local_only": False,
        "optimization": {
            "optimization_id": "BROKEN",
            "compatible_object_classes": ["route"],
            "required_operations": [],
            "required_port_types": [],
        },
        "source": {
            "descriptor_schema_id": "HHS_PASS_187_OBJECT_DESCRIPTOR_V1",
            "object_class": "route",
            "runtime_authority": "REFERENCE_ONLY",
            "exactness_domain": "EXACT_INTEGER",
            "logical_object_id": "source",
            "operations": [],
            "inputs": [],
            "outputs": [],
        },
        "targets": [
            {
                "descriptor_schema_id": "HHS_PASS_187_OBJECT_DESCRIPTOR_V1",
                "object_class": "route",
                "runtime_authority": "REFERENCE_ONLY",
                "exactness_domain": "EXACT_INTEGER",
                "logical_object_id": "target",
                "operations": [],
                "inputs": [],
                "outputs": [],
            }
        ],
        "target_evidence": [
            {
                "logical_object_id": "target",
                "validation_executed": True,
                "safe": True,
                "benefit": True,
            }
        ],
        # Deliberately omit the actually-required target.
        "declared_generalize_required": [],
    }
    (directory / "broken.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(
        Lane5MandatoryOptimizationRegistryError,
        match="LANE5_OPTIMIZATION_MANIFEST_INVALID",
    ):
        build_mandatory_optimization_registry(root)
