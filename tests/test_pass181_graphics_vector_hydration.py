from __future__ import annotations

from pathlib import Path

import pytest

from hhs_backend.runtime.hhs_graphics_vector_hydration_v1 import (
    GraphicsVectorHydrationError,
    GraphicsVectorHydrationStore,
)

AUTHORITY = "HHS_VM81_SINGLETON_GRAPHICS_HYDRATION_AUTHORITY_V1"


def _recipe(recipe_hash: str, *, camera_mode: str, layer_type: str) -> dict:
    return {
        "schema": "HHS_P181_NATIVE_RECONSTRUCTION_RECIPE_V1",
        "contract": "HHS-P181-NCSR-GHIR-VM81-H72-H216",
        "authority": AUTHORITY,
        "reference_id": "reference-root",
        "target_timeline_hash216": "timeline-root",
        "frame_count": 4,
        "scenes": [
            {
                "scene_id": recipe_hash,
                "start_frame": 0,
                "end_frame": 4,
                "palette": {"x": 5, "y": 17, "z": 41, "w": 53},
                "layers": [
                    {
                        "layer_id": f"layer-{recipe_hash}",
                        "type": layer_type,
                        "source_type": "native_sprite_map",
                        "authority": "HHS_NATIVE_ABI",
                        "parameters": {"variant": recipe_hash},
                    }
                ],
                "captions": [],
                "camera": {"mode": camera_mode},
                "lighting": {"mode": "phase_glow"},
                "transition": {"mode": "cut"},
            }
        ],
        "audio": {
            "mode": "native_synthesis",
            "authority": "HHS_NATIVE_ABI",
            "parameters": {"frequency": 440},
        },
        "threejs_role": "preview_enhancement_only",
        "final_frame_authority": "HHS_NATIVE_ABI",
        "single_commit_authority": True,
        "recipe_hash216": recipe_hash,
        "receipt_hash72": f"receipt-{recipe_hash}",
    }


def _job(job_suffix: str) -> dict:
    recipes = [
        _recipe(f"recipe-{job_suffix}-0", camera_mode="pan", layer_type="background"),
        _recipe(f"recipe-{job_suffix}-1", camera_mode="zoom", layer_type="sprite_map"),
        _recipe(f"recipe-{job_suffix}-2", camera_mode="pan", layer_type="background"),
    ]
    history = [
        {
            "candidate_index": 0,
            "recipe_hash216": recipes[0]["recipe_hash216"],
            "decision": "ACCEPTED_STRICT_IMPROVEMENT",
            "result": {
                "recipe_hash216": recipes[0]["recipe_hash216"],
                "score": [0, 2, 0, 4, 1, 0],
                "residual_report_hash216": f"residual-{job_suffix}-0",
            },
        },
        {
            "candidate_index": 1,
            "recipe_hash216": recipes[1]["recipe_hash216"],
            "decision": "ACCEPTED_STRICT_IMPROVEMENT",
            "result": {
                "recipe_hash216": recipes[1]["recipe_hash216"],
                "score": [0, 0, 0, 0, 0, 0],
                "residual_report_hash216": f"residual-{job_suffix}-1",
            },
        },
        {
            "candidate_index": 2,
            "recipe_hash216": recipes[2]["recipe_hash216"],
            "decision": "REJECTED_NO_STRICT_IMPROVEMENT",
            "result": {
                "recipe_hash216": recipes[2]["recipe_hash216"],
                "score": [0, 3, 0, 4, 1, 0],
                "residual_report_hash216": f"residual-{job_suffix}-2",
            },
        },
    ]
    return {
        "schema": "HHS_P181_GRAPHICS_OPTIMIZATION_JOB_V1",
        "job_id": f"opt:{job_suffix}",
        "contract": "HHS-P181-NCSR-GHIR-VM81-H72-H216",
        "authority": AUTHORITY,
        "state": "SUCCEEDED",
        "completion_status": "HHS_GRAPHICS_OPTIMIZATION_BOUNDED_CLOSURE_VERIFIED",
        "request_hash216": f"request-{job_suffix}",
        "request": {
            "reference_manifest": {
                "schema": "HHS_P181_CANONICAL_MP4_DECODE_MANIFEST_V1",
                "reference_id": "reference-root",
                "timeline_hash216": "timeline-root",
                "decoded_timelines": [],
            },
            "candidate_recipes": recipes,
            "baseline_residual_report": None,
            "timeout_seconds": 300,
            "render_timeout_seconds": 120,
            "stop_on_exact": False,
            "parent_job_id": None,
        },
        "next_candidate_index": 3,
        "accepted_count": 2,
        "rejected_count": 1,
        "cancel_requested": False,
        "incumbent_score": [0, 0, 0, 0, 0, 0],
        "incumbent_recipe_hash216": recipes[1]["recipe_hash216"],
        "incumbent_residual_hash216": f"residual-{job_suffix}-1",
        "incumbent_candidate_index": 1,
        "incumbent_native_output_id": f"output-{job_suffix}-1",
        "incumbent_decode_manifest_id": f"decode-{job_suffix}-1",
        "history": history,
        "failure_reason": None,
    }


def test_final_optimization_job_hydrates_typed_pass165_vectors_idempotently(tmp_path: Path) -> None:
    store = GraphicsVectorHydrationStore(tmp_path / "vector-store")
    job = _job("one")
    first = store.hydrate_optimization_job(job)
    second = store.hydrate_optimization_job(job)
    assert first["ok"] is True
    assert first["packet_count"] == 9
    assert first["new_record_count"] == 9
    assert first["reused_record_count"] == 0
    assert second["new_record_count"] == 0
    assert second["reused_record_count"] == 9
    assert first["runtime_constraint_authority"] is False
    records = store.list_records(source_job_id=job["job_id"])
    assert len(records) == 9
    assert all(record["runtime_constraint_authority"] is False for record in records)
    assert all(record["frozen"] is False for record in records)
    assert all(record["pass165"]["projection_hash72"] for record in records)


def test_support_counted_invariants_require_distinct_jobs_and_never_self_freeze(tmp_path: Path) -> None:
    store = GraphicsVectorHydrationStore(tmp_path / "vector-store")
    store.hydrate_optimization_job(_job("one"))
    one_job = store.extract_invariant_candidates(
        minimum_support=2,
        minimum_distinct_jobs=2,
    )
    assert one_job["runtime_constraints_frozen"] == 0
    assert one_job["eligible_count"] == 0

    store.hydrate_optimization_job(_job("two"))
    two_jobs = store.extract_invariant_candidates(
        minimum_support=2,
        minimum_distinct_jobs=2,
    )
    by_predicate = {candidate["predicate_id"]: candidate for candidate in two_jobs["candidates"]}
    for predicate in (
        "ALL_LAYERS_NATIVE",
        "NO_REFERENCE_PASSTHROUGH",
        "RECIPROCAL_PALETTE",
        "SINGLE_COMMIT_AUTHORITY",
        "STRICT_IMPROVEMENT_ADMISSION",
        "REJECTED_CANDIDATES_LACK_AUTHORITY",
    ):
        candidate = by_predicate[predicate]
        assert candidate["eligible_for_promotion"] is True
        assert candidate["distinct_job_count"] >= 2
        assert candidate["runtime_constraint_authority"] is False
        assert candidate["frozen"] is False

    style = by_predicate["STYLE_CAMERA_MODE:zoom"]
    assert style["candidate_class"] == "STYLE_PROFILE"
    assert style["promotion_track"] == "STYLE_PROFILE"
    assert style["runtime_constraint_authority"] is False

    proposal = store.build_promotion_proposal(by_predicate["RECIPROCAL_PALETTE"]["candidate_hash216"])
    assert proposal["runtime_constraint_authority"] is False
    assert proposal["frozen"] is False
    assert all(value is False for value in proposal["stages"].values())
    with pytest.raises(
        GraphicsVectorHydrationError,
        match="VECTOR_OBSERVATION_CANNOT_FREEZE_RUNTIME_CONSTRAINT",
    ):
        store.freeze_candidate(by_predicate["RECIPROCAL_PALETTE"]["candidate_hash216"])


def test_vector_hydration_recovers_catalog_and_replays_pass165_state(tmp_path: Path) -> None:
    root = tmp_path / "vector-store"
    original = GraphicsVectorHydrationStore(root)
    original.hydrate_optimization_job(_job("one"))
    original.hydrate_optimization_job(_job("two"))
    record_count = original.status()["vector_record_count"]

    recovered = GraphicsVectorHydrationStore(root)
    assert recovered.status()["vector_record_count"] == record_count
    replay = recovered.replay()
    assert replay["ok"] is True
    assert replay["status"] == "HHS_GRAPHICS_VECTOR_HYDRATION_REPLAY_VERIFIED"
    assert replay["catalog_records"] == record_count
    assert replay["runtime_constraints_frozen"] == 0
    assert replay["pass165_replay"]["deterministic_replay"] is True


def test_nonfinal_job_and_catalog_tampering_fail_closed(tmp_path: Path) -> None:
    root = tmp_path / "vector-store"
    store = GraphicsVectorHydrationStore(root)
    job = _job("one")
    job["state"] = "RUNNING"
    with pytest.raises(GraphicsVectorHydrationError, match="REQUIRES_FINAL_JOB"):
        store.hydrate_optimization_job(job)

    valid = _job("valid")
    store.hydrate_optimization_job(valid)
    with store.catalog_path.open("ab") as handle:
        handle.write(b"incomplete")
    with pytest.raises(GraphicsVectorHydrationError, match="INCOMPLETE_TAIL"):
        GraphicsVectorHydrationStore(root)
