from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from hhs_backend.runtime.hhs_graphics_constraint_registry_v1 import (
    AUTHORITY,
    PROMOTION_STAGES,
    GraphicsConstraintRegistry,
    GraphicsConstraintRegistryError,
)


def _candidate(
    predicate_id: str,
    *,
    candidate_hash: str,
    track: str = "RUNTIME_CONSTRAINT",
    candidate_class: str = "HARD_INVARIANT",
    counterexamples: list[str] | None = None,
    eligible: bool = True,
) -> dict:
    support = [f"record-{candidate_hash}-1", f"record-{candidate_hash}-2"]
    jobs = [f"job-{candidate_hash}-1", f"job-{candidate_hash}-2"]
    return {
        "schema": "HHS_P181_GRAPHICS_INVARIANT_CANDIDATE_V1",
        "contract": "HHS-P181-NCSR-GHIR-VM81-H72-H216",
        "authority": AUTHORITY,
        "predicate_id": predicate_id,
        "candidate_class": candidate_class,
        "proposition": f"validated proposition for {predicate_id}",
        "domain": "GRAPHICS_RUNTIME" if track == "RUNTIME_CONSTRAINT" else "GRAPHICS_STYLE",
        "promotion_track": track,
        "support_count": len(support),
        "distinct_job_count": len(jobs),
        "supporting_record_hash216": support,
        "supporting_job_ids": jobs,
        "counterexample_record_hash216": list(counterexamples or []),
        "minimum_support": 2,
        "minimum_distinct_jobs": 2,
        "eligible_for_promotion": eligible,
        "validation_state": "CANDIDATE",
        "runtime_constraint_authority": False,
        "frozen": False,
        "evidence_root_hash216": f"evidence-{candidate_hash}",
        "candidate_hash216": candidate_hash,
        "receipt_hash72": f"candidate-receipt-{candidate_hash}",
    }


def _promotion_evidence(label: str = "v1") -> dict:
    return {
        "stages": {stage: True for stage in PROMOTION_STAGES},
        "stage_evidence": {
            stage: [f"{label}-{stage}-positive-root", f"{label}-{stage}-receipt-root"]
            for stage in PROMOTION_STAGES
        },
        "contradiction_scan_result": "PASSED",
        "calibration_profile": {
            "profile": f"graphics-calibration-{label}",
            "sample_count": 72,
            "distinct_jobs": 2,
        },
        "validator_versions": {
            "native_renderer": "HHS_NATIVE_ABI_V1",
            "canonical_decoder": "HHS_P181_CANONICAL_MP4_DECODE_MANIFEST_V1",
            "residual_analyzer": "HHS_P181_NATIVE_RECONSTRUCTION_RESIDUAL_REPORT_V1",
        },
        "operator": "HHS_VM81_PROMOTION_AUTHORITY",
    }


def test_incomplete_promotion_evidence_and_counterexamples_fail_closed(tmp_path: Path) -> None:
    registry = GraphicsConstraintRegistry(tmp_path / "registry")
    evidence = _promotion_evidence()
    evidence["stages"]["adversarial_tested"] = False
    with pytest.raises(GraphicsConstraintRegistryError, match="STAGES_INCOMPLETE"):
        registry.freeze_candidate(
            _candidate("NO_REFERENCE_PASSTHROUGH", candidate_hash="candidate-incomplete"),
            evidence,
        )

    evidence = _promotion_evidence()
    evidence["stage_evidence"]["negative_tested"] = []
    with pytest.raises(GraphicsConstraintRegistryError, match="STAGE_EVIDENCE_EMPTY"):
        registry.freeze_candidate(
            _candidate("NO_REFERENCE_PASSTHROUGH", candidate_hash="candidate-empty-evidence"),
            evidence,
        )

    with pytest.raises(GraphicsConstraintRegistryError, match="HAS_COUNTEREXAMPLES"):
        registry.freeze_candidate(
            _candidate(
                "NO_REFERENCE_PASSTHROUGH",
                candidate_hash="candidate-counterexample",
                counterexamples=["counterexample-root"],
            ),
            _promotion_evidence(),
        )

    with pytest.raises(GraphicsConstraintRegistryError, match="NOT_ELIGIBLE"):
        registry.freeze_candidate(
            _candidate(
                "NO_REFERENCE_PASSTHROUGH",
                candidate_hash="candidate-ineligible",
                eligible=False,
            ),
            _promotion_evidence(),
        )


def test_hard_constraint_and_style_profile_freeze_into_separate_frontiers(tmp_path: Path) -> None:
    registry = GraphicsConstraintRegistry(tmp_path / "registry")
    hard = registry.freeze_candidate(
        _candidate("RECIPROCAL_PALETTE", candidate_hash="hard-v1"),
        _promotion_evidence("hard"),
    )
    style = registry.freeze_candidate(
        _candidate(
            "STYLE_CAMERA_MODE:pan",
            candidate_hash="style-v1",
            track="STYLE_PROFILE",
            candidate_class="STYLE_PROFILE",
        ),
        _promotion_evidence("style"),
    )

    assert hard["status"] == "HHS_GRAPHICS_RUNTIME_CONSTRAINT_FROZEN"
    assert hard["record"]["record_kind"] == "RUNTIME_CONSTRAINT"
    assert hard["record"]["runtime_constraint_authority"] is True
    assert hard["record"]["style_profile_authority"] is False
    assert style["status"] == "HHS_GRAPHICS_STYLE_PROFILE_FROZEN"
    assert style["record"]["record_kind"] == "STYLE_PROFILE"
    assert style["record"]["runtime_constraint_authority"] is False
    assert style["record"]["style_profile_authority"] is True

    frontier = registry.active_frontier()
    assert frontier["active_runtime_constraints"] == {
        "RECIPROCAL_PALETTE": hard["record"]["record_hash216"]
    }
    assert frontier["active_style_profiles"] == {
        "STYLE_CAMERA_MODE:pan": style["record"]["record_hash216"]
    }
    assert registry.status()["active_runtime_constraint_count"] == 1
    assert registry.status()["active_style_profile_count"] == 1


def test_explicit_supersession_and_rollback_preserve_immutable_versions(tmp_path: Path) -> None:
    registry = GraphicsConstraintRegistry(tmp_path / "registry")
    first = registry.freeze_candidate(
        _candidate("ALL_LAYERS_NATIVE", candidate_hash="native-v1"),
        _promotion_evidence("v1"),
    )
    first_id = first["record"]["record_hash216"]

    with pytest.raises(GraphicsConstraintRegistryError, match="EXPLICIT_SUPERSESSION"):
        registry.freeze_candidate(
            _candidate("ALL_LAYERS_NATIVE", candidate_hash="native-v2-no-target"),
            _promotion_evidence("v2-no-target"),
        )

    second = registry.freeze_candidate(
        _candidate("ALL_LAYERS_NATIVE", candidate_hash="native-v2"),
        _promotion_evidence("v2"),
        supersedes=first_id,
    )
    second_id = second["record"]["record_hash216"]
    assert second["record"]["version"] == 2
    assert second["record"]["supersedes"] == first_id
    assert registry.active_frontier()["active_runtime_constraints"]["ALL_LAYERS_NATIVE"] == second_id

    rollback = registry.rollback("ALL_LAYERS_NATIVE")
    assert rollback["from_record_hash216"] == second_id
    assert rollback["target_record_hash216"] == first_id
    assert registry.active_frontier()["active_runtime_constraints"]["ALL_LAYERS_NATIVE"] == first_id

    records = registry.list_records(
        record_kind="RUNTIME_CONSTRAINT",
        predicate_id="ALL_LAYERS_NATIVE",
    )
    assert [record["version"] for record in records] == [1, 2]
    assert {record["record_hash216"] for record in records} == {first_id, second_id}
    assert all(record["state"] == "FROZEN_IMMUTABLE" for record in records)


def test_cold_restart_reconstructs_exact_active_frontier_and_event_chain(tmp_path: Path) -> None:
    root = tmp_path / "registry"
    registry = GraphicsConstraintRegistry(root)
    first = registry.freeze_candidate(
        _candidate("STRICT_IMPROVEMENT_ADMISSION", candidate_hash="strict-v1"),
        _promotion_evidence("strict-v1"),
    )
    registry.freeze_candidate(
        _candidate(
            "STYLE_LAYER_TYPE:sprite_map",
            candidate_hash="sprite-style-v1",
            track="STYLE_PROFILE",
            candidate_class="STYLE_PROFILE",
        ),
        _promotion_evidence("sprite-style-v1"),
    )
    second = registry.freeze_candidate(
        _candidate("STRICT_IMPROVEMENT_ADMISSION", candidate_hash="strict-v2"),
        _promotion_evidence("strict-v2"),
        supersedes=first["record"]["record_hash216"],
    )
    registry.rollback(
        "STRICT_IMPROVEMENT_ADMISSION",
        target_record_hash216=first["record"]["record_hash216"],
    )
    expected_frontier = registry.active_frontier()
    expected_records = registry.list_records()

    recovered = GraphicsConstraintRegistry(root)
    assert recovered.active_frontier() == expected_frontier
    assert recovered.list_records() == expected_records
    replay = recovered.verify_replay()
    assert replay["ok"] is True
    assert replay["status"] == "HHS_GRAPHICS_CONSTRAINT_COLD_RESTART_REPLAY_VERIFIED"
    assert replay["frontier_hash216"] == expected_frontier["frontier_hash216"]
    assert replay["active_runtime_constraints"]["STRICT_IMPROVEMENT_ADMISSION"] == first["record"]["record_hash216"]
    assert second["record"]["record_hash216"] in {
        record["record_hash216"] for record in replay and recovered.list_records()
    }


def test_journal_and_frontier_tampering_fail_closed(tmp_path: Path) -> None:
    journal_root = tmp_path / "journal-registry"
    journal_registry = GraphicsConstraintRegistry(journal_root)
    journal_registry.freeze_candidate(
        _candidate("REJECTED_CANDIDATES_LACK_AUTHORITY", candidate_hash="reject-v1"),
        _promotion_evidence("reject-v1"),
    )
    with journal_registry.journal_path.open("ab") as handle:
        handle.write(b"incomplete-tail")
    with pytest.raises(GraphicsConstraintRegistryError, match="INCOMPLETE_TAIL"):
        GraphicsConstraintRegistry(journal_root)

    frontier_root = tmp_path / "frontier-registry"
    frontier_registry = GraphicsConstraintRegistry(frontier_root)
    frontier_registry.freeze_candidate(
        _candidate("RECIPROCAL_PALETTE", candidate_hash="palette-v1"),
        _promotion_evidence("palette-v1"),
    )
    tampered = json.loads(frontier_registry.frontier_path.read_text(encoding="utf-8"))
    tampered["active_runtime_constraints"]["RECIPROCAL_PALETTE"] = "forged-record"
    frontier_registry.frontier_path.write_text(
        json.dumps(tampered, sort_keys=True),
        encoding="utf-8",
    )
    with pytest.raises(GraphicsConstraintRegistryError, match="FRONTIER_REPLAY_MISMATCH"):
        GraphicsConstraintRegistry(frontier_root)


def test_governed_router_shadows_legacy_direct_promotion() -> None:
    from hhs_backend.visual_server import app

    matching = [
        route
        for route in app.router.routes
        if getattr(route, "path", None)
        == "/api/runtime/graphics-hydration/constraints/promote"
        and "POST" in (getattr(route, "methods", None) or set())
    ]
    assert matching
    assert matching[0].endpoint.__name__ == "legacy_direct_graphics_constraint_promotion_disabled"

    response = matching[0].endpoint({"predicate": "forged-direct-promotion"})
    assert response["ok"] is False
    assert response["reason"] == (
        "P181_LEGACY_DIRECT_CONSTRAINT_PROMOTION_DISABLED_USE_REGISTRY_FREEZE"
    )
