from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from hhs_backend.runtime.hhs_graphics_hydration_v1 import (
    GraphicsHydrationError,
    GraphicsHydrationRuntime,
)


def _timeline(media_type: str, hashes: list[str]) -> dict:
    records = [
        {
            "stream": 0,
            "dts": index,
            "pts": index,
            "duration": 1,
            "size_bytes": 4,
            "sha256": value,
        }
        for index, value in enumerate(hashes)
    ]
    projection = (
        {"media_type": "video", "codec": "rawvideo", "pixel_format": "rgba"}
        if media_type == "video"
        else {"media_type": "audio", "codec": "pcm_s32le", "sample_rate": "8000", "channels": 1}
    )
    return {
        "source_stream_index": 0 if media_type == "video" else 1,
        "source_stream": {"index": 0 if media_type == "video" else 1, "codec_type": media_type},
        "canonical_projection": projection,
        "headers": {"hash": "SHA256", "tb 0": "1/3" if media_type == "video" else "1/8000"},
        "records": records,
        "record_count": len(records),
        "timeline_hash216": f"{media_type}-timeline-root",
    }


def _reference_manifest() -> dict:
    return {
        "schema": "HHS_P181_CANONICAL_MP4_DECODE_MANIFEST_V1",
        "reference_id": "reference-root",
        "timeline_hash216": "reference-timeline-root",
        "decoded_timelines": [
            _timeline("video", ["v0", "v1", "v2", "v3"]),
            _timeline("audio", ["a0", "a1"]),
        ],
    }


def _native_recipe() -> dict:
    return {
        "reference_id": "reference-root",
        "target_timeline_hash216": "reference-timeline-root",
        "scenes": [
            {
                "scene_id": "archive-opening",
                "start_frame": 0,
                "end_frame": 2,
                "palette": {"x": 5, "y": 17, "z": 41, "w": 53},
                "layers": [
                    {
                        "layer_id": "archive-background",
                        "type": "background",
                        "source_type": "native_sprite_map",
                        "authority": "HHS_NATIVE_ABI",
                        "parameters": {"sprite_map": "archive-grid", "depth": 0},
                    },
                    {
                        "layer_id": "silver-receipt",
                        "type": "sprite_map",
                        "source_type": "native_sprite_map",
                        "authority": "HHS_NATIVE_ABI",
                        "parameters": {"sprite_map": "silver-receipt", "depth": 2},
                    },
                ],
                "captions": [
                    {
                        "caption_id": "caption-0",
                        "start_frame": 0,
                        "end_frame": 2,
                        "text": "Paper moved behind the wall.",
                        "style": {"preset": "archive-receipt", "depth": 3},
                    }
                ],
                "camera": {"mode": "pan", "x_step": {"numerator": 1, "denominator": 72}},
                "lighting": {"mode": "phase_glow", "intensity": 12},
                "transition": {"mode": "cut", "duration_frames": 0},
            },
            {
                "scene_id": "future-receipt",
                "start_frame": 2,
                "end_frame": 4,
                "palette": {"x": 11, "y": 23, "z": 47, "w": 59},
                "layers": [
                    {
                        "layer_id": "atrium-texture",
                        "type": "texture_map",
                        "source_type": "hydrated_native_asset",
                        "authority": "HHS_NATIVE_ABI",
                        "parameters": {"texture_map": "transit-atrium", "depth": 1},
                    }
                ],
                "captions": [],
                "camera": {"mode": "zoom", "scale_step": {"numerator": 1, "denominator": 216}},
                "lighting": {"mode": "reciprocal_rim", "intensity": 18},
                "transition": {"mode": "phase_dissolve", "duration_frames": 1},
            },
        ],
        "audio": {
            "mode": "native_pcm_recipe",
            "parameters": {"music_profile": "chromatic-story-beat", "sample_rate": 8000},
        },
    }


def test_native_recipe_validates_complete_timeline_and_native_layers(tmp_path: Path) -> None:
    runtime = GraphicsHydrationRuntime(tmp_path / "hydration")
    validated = runtime.validate_native_recipe(_native_recipe(), _reference_manifest())
    assert validated["schema"] == "HHS_P181_NATIVE_RECONSTRUCTION_RECIPE_V1"
    assert validated["frame_count"] == 4
    assert validated["final_frame_authority"] == "HHS_NATIVE_ABI"
    assert validated["threejs_role"] == "preview_enhancement_only"
    assert validated["scenes"][0]["palette"]["z"] == 41
    assert Path(validated["record_path"]).is_file()


def test_native_recipe_rejects_reference_frame_passthrough(tmp_path: Path) -> None:
    runtime = GraphicsHydrationRuntime(tmp_path / "hydration")
    recipe = _native_recipe()
    recipe["scenes"][0]["layers"][0]["source_type"] = "reference_frame"
    with pytest.raises(GraphicsHydrationError, match="PASSTHROUGH.*PROHIBITED"):
        runtime.validate_native_recipe(recipe, _reference_manifest())


def test_native_recipe_rejects_nonreciprocal_palette_and_scene_gap(tmp_path: Path) -> None:
    runtime = GraphicsHydrationRuntime(tmp_path / "hydration")
    palette_recipe = _native_recipe()
    palette_recipe["scenes"][0]["palette"]["z"] = 40
    with pytest.raises(GraphicsHydrationError, match="RECIPROCAL_INVARIANT_FAILED"):
        runtime.validate_native_recipe(palette_recipe, _reference_manifest())

    gap_recipe = _native_recipe()
    gap_recipe["scenes"][1]["start_frame"] = 3
    with pytest.raises(GraphicsHydrationError, match="SCENE_COVERAGE_INVALID"):
        runtime.validate_native_recipe(gap_recipe, _reference_manifest())


def test_identical_native_output_has_no_decoded_residuals(tmp_path: Path) -> None:
    runtime = GraphicsHydrationRuntime(tmp_path / "hydration")
    reference = _reference_manifest()
    validated = runtime.validate_native_recipe(_native_recipe(), reference)
    report = runtime.build_residual_report(reference, deepcopy(reference), validated)
    assert report["exact_decoded_audiovisual_match"] is True
    assert report["residuals"] == []
    assert Path(report["record_path"]).is_file()


def test_residual_report_types_frame_audio_timing_and_semantic_mismatches(tmp_path: Path) -> None:
    runtime = GraphicsHydrationRuntime(tmp_path / "hydration")
    reference = _reference_manifest()
    native = deepcopy(reference)
    native["timeline_hash216"] = "native-timeline-root"
    native["decoded_timelines"][0]["records"][1]["sha256"] = "different-video-frame"
    native["decoded_timelines"][0]["records"][2]["pts"] = 72
    native["decoded_timelines"][1]["records"].pop()
    native["decoded_timelines"][1]["record_count"] = 1
    validated = runtime.validate_native_recipe(_native_recipe(), reference)
    report = runtime.build_residual_report(
        reference,
        native,
        validated,
        semantic_metrics={
            "palette_phase_mismatches": 1,
            "caption_layout_mismatches": 2,
            "caption_timing_mismatches": 3,
            "camera_motion_mismatches": 4,
            "lighting_mismatches": 5,
            "provenance_mismatches": 6,
        },
    )
    classes = {residual["class"] for residual in report["residuals"]}
    assert report["exact_decoded_audiovisual_match"] is False
    assert {
        "FRAME_CONTENT_RESIDUAL",
        "AUDIO_CONTENT_RESIDUAL",
        "TIMELINE_RESIDUAL",
        "PALETTE_PHASE_RESIDUAL",
        "CAPTION_LAYOUT_RESIDUAL",
        "CAPTION_TIMING_RESIDUAL",
        "CAMERA_MOTION_RESIDUAL",
        "LIGHTING_RESIDUAL",
        "UNEXPLAINED_PIXEL_PROVENANCE",
    }.issubset(classes)


def test_residual_report_requires_validated_recipe_identity(tmp_path: Path) -> None:
    runtime = GraphicsHydrationRuntime(tmp_path / "hydration")
    with pytest.raises(GraphicsHydrationError, match="VALIDATED_RECIPE_IDENTITY_REQUIRED"):
        runtime.build_residual_report(
            _reference_manifest(),
            _reference_manifest(),
            {"target_timeline_hash216": "reference-timeline-root"},
        )
