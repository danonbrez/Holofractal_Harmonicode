from __future__ import annotations

from pathlib import Path

import pytest

from hhs_backend.runtime.hhs_graphics_hydration_v1 import (
    GraphicsHydrationError,
    GraphicsHydrationRuntime,
    PROMOTION_STAGES,
    classify_fidelity,
    graphics_hydration_self_test,
    reciprocal_palette_phases,
    validate_native_frame_provenance,
)


def test_reciprocal_palette_phase_is_exact() -> None:
    assert reciprocal_palette_phases(0, 12, 48) == {"x": 0, "y": 12, "z": 36, "w": 48}
    assert reciprocal_palette_phases(71, 3, 35)["z"] == 35
    with pytest.raises(GraphicsHydrationError, match="PHASE_OUT_OF_RANGE"):
        reciprocal_palette_phases(72, 1, 2)


def test_reference_ingestion_is_read_only_and_content_addressed(tmp_path: Path) -> None:
    source = tmp_path / "reference.mp4"
    source.write_bytes(b"synthetic-reference-mp4-evidence")
    before = source.stat()
    runtime = GraphicsHydrationRuntime(tmp_path / "hydration")

    first = runtime.ingest_reference(source, logical_name="Reference Reel")
    second = runtime.ingest_reference(source, logical_name="Reference Reel")
    after = source.stat()

    assert first["identity"]["reference_id"] == second["identity"]["reference_id"]
    assert first["read_only"] is True
    assert first["copied_into_hydration_store"] is False
    assert source.read_bytes() == b"synthetic-reference-mp4-evidence"
    assert before.st_size == after.st_size
    assert before.st_mtime_ns == after.st_mtime_ns
    assert Path(first["manifest_path"]).is_file()


def test_non_mp4_reference_fails_closed(tmp_path: Path) -> None:
    source = tmp_path / "reference.mov"
    source.write_bytes(b"not-mp4")
    runtime = GraphicsHydrationRuntime(tmp_path / "hydration")
    with pytest.raises(GraphicsHydrationError, match="REQUIRES_MP4"):
        runtime.ingest_reference(source)


def test_native_frame_provenance_accepts_native_layers() -> None:
    result = validate_native_frame_provenance(
        {
            "frame_index": 7,
            "layers": [
                {
                    "type": "scene",
                    "source_type": "native_scene_recipe",
                    "authority": "HHS_NATIVE_ABI",
                    "recipe_hash216": "scene-root",
                },
                {
                    "type": "caption",
                    "source_type": "native_caption_recipe",
                    "authority": "HHS_NATIVE_ABI",
                    "recipe_hash216": "caption-root",
                },
            ],
        }
    )
    assert result["ok"] is True
    assert result["status"] == "HHS_MP4_ORIGINAL_FRAME_PASSTHROUGH_PROHIBITED"


def test_native_frame_provenance_rejects_reference_passthrough() -> None:
    with pytest.raises(GraphicsHydrationError, match="PASSTHROUGH_PROHIBITED"):
        validate_native_frame_provenance(
            {
                "frame_index": 0,
                "layers": [
                    {
                        "type": "texture",
                        "source_type": "reference_frame",
                        "authority": "HHS_NATIVE_ABI",
                        "recipe_hash216": "invalid-root",
                    }
                ],
            }
        )


def test_fidelity_levels_do_not_conflate_visual_and_bitstream_identity() -> None:
    result = classify_fidelity(
        {
            "semantic_match": True,
            "perceptual_match": True,
            "decoded_frames_equal": True,
            "decoded_pcm_equal": True,
            "pts_equal": True,
            "encoder_state_available": False,
            "mp4_bytes_equal": True,
        }
    )
    assert result["strongest"] == "NATIVE_DECODED_AUDIOVISUAL_EXACTNESS"
    assert "MP4_BITSTREAM_IDENTITY_WHEN_ENCODER_STATE_IS_AVAILABLE" not in result["levels"]


def test_constraint_promotion_requires_complete_validation_chain(tmp_path: Path) -> None:
    runtime = GraphicsHydrationRuntime(tmp_path / "hydration")
    stages = {stage: True for stage in PROMOTION_STAGES}
    stages["adversarial_tested"] = False
    candidate = {
        "family": "PROVENANCE",
        "predicate": "all_authoritative_layers_use_native_abi",
        "evidence": ["test-pass-root"],
        "stages": stages,
    }
    rejected = runtime.promote_constraint(candidate)
    assert rejected["ok"] is False
    assert rejected["missing_stages"] == ["adversarial_tested"]

    candidate["stages"]["adversarial_tested"] = True
    accepted = runtime.promote_constraint(candidate)
    assert accepted["ok"] is True
    assert accepted["constraint"]["state"] == "FROZEN"
    assert Path(accepted["record_path"]).is_file()


def test_trial_residual_classes_are_typed(tmp_path: Path) -> None:
    runtime = GraphicsHydrationRuntime(tmp_path / "hydration")
    accepted = runtime.record_trial(
        reference_id="reference-root",
        native_recipe={"scene": "native"},
        residuals=[{"class": "LIGHTING_RESIDUAL", "magnitude": {"numerator": 1, "denominator": 72}}],
    )
    assert accepted["state"] == "OBSERVED"

    with pytest.raises(GraphicsHydrationError, match="RESIDUAL_CLASS_REJECTED"):
        runtime.record_trial(
            reference_id="reference-root",
            native_recipe={"scene": "native"},
            residuals=[{"class": "UNKNOWN_RESIDUAL"}],
        )


def test_pass181_self_test() -> None:
    assert graphics_hydration_self_test()["ok"] is True
