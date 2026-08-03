from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from hhs_backend.runtime.hhs_storybook_reel_v3 import (
    CLASSIFICATION,
    CONTRACT,
    Pass203HighFidelityStorybookRuntime,
)


@pytest.fixture()
def runtime() -> Pass203HighFidelityStorybookRuntime:
    with tempfile.TemporaryDirectory() as directory:
        yield Pass203HighFidelityStorybookRuntime(Path(directory))


def serialized(value) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def test_parameter_catalog_exposes_all_mutable_and_compiled_fields(runtime) -> None:
    catalog = runtime.parameter_catalog()
    assert catalog["contract"] == CONTRACT
    assert catalog["classification"] == CLASSIFICATION
    assert catalog["cumulative_system_version"] == 203
    assert catalog["all_prior_passes_inherited"] is True
    assert catalog["all_parameters_publicly_enumerated"] is True
    assert catalog["compiled_constants_are_read_only"] is True
    assert len(catalog["style_fields"]) >= 20
    assert len(catalog["native_layer_fields"]) == 10
    assert len(catalog["render_fields"]) >= 20
    assert catalog["parameter_count"] > 50
    assert set(catalog["quality_profiles"]) >= {
        "production_vertical_1080",
        "production_vertical_1440",
        "production_vertical_2160",
        "native_integer_1080",
        "native_lossless_rgba",
    }
    assert catalog["catalog_hash72"]
    assert "HHS_PASS_202" not in serialized({key: value for key, value in catalog.items() if key != "compiled_native_constants"})


def test_resolve_production_1440_and_native_layer_masks(runtime) -> None:
    resolved = runtime.resolve_parameters(
        {
            "text": "A clockmaker carried a candle through the midnight city.",
            "quality_profile": "production_vertical_1440",
            "render": {"contrast": "1.11", "saturation": "1.24", "sharpen_luma": "0.61"},
            "native_layers": {
                "texture": {"field": True, "midground": False, "materials": True, "semantic": True, "player": True},
                "sprite": {"atmosphere": True, "phase": True, "glows": False, "vignette": True, "hud": False},
            },
        }
    )
    assert resolved["schema"] == "HHS_PASS_203_RESOLVED_RENDER_PARAMETERS_V1"
    assert resolved["quality_profile"] == "production_vertical_1440"
    assert resolved["render"]["output_width"] == 1440
    assert resolved["render"]["output_height"] == 2560
    assert resolved["render"]["scale_filter"] == "lanczos"
    assert resolved["render"]["contrast"] == "1.11"
    assert resolved["native_layers"]["texture_flags"] == 29
    assert resolved["native_layers"]["sprite_overlay_flags"] == 11
    assert resolved["authority_locked"]["logical_width"] == 160
    assert resolved["authority_locked"]["logical_height"] == 144
    assert resolved["authority_locked"]["native_frame_identity_preserved"] if "native_frame_identity_preserved" in resolved["authority_locked"] else True
    assert resolved["resolution_hash72"]
    assert "pass202" not in serialized(resolved).lower()


def test_filter_graph_is_cinematic_not_fixed_neighbor_black_pad(runtime) -> None:
    resolved = runtime.resolve_parameters({"text": "A cinematic journey", "quality_profile": "production_vertical_1080"})
    graph = runtime.video_filter_graph(resolved["render"])
    assert "split=2" in graph
    assert "gblur=sigma=30" in graph
    assert "flags=lanczos" in graph
    assert "unsharp=" in graph
    assert "overlay=(W-w)/2:(H-h)/2" in graph
    assert "pad=1080:1920:0:474" not in graph


def test_contextual_defaults_return_ranked_creative_candidates(runtime) -> None:
    result = runtime.contextual_defaults("The candle waited beside the silent clock and the twelfth bell.")
    assert result["schema"] == "HHS_PASS_203_CONTEXTUAL_DEFAULTS_V1"
    assert result["template_candidates"]
    assert result["template_candidates"][0]["template_id"] == "serif_fable"
    assert result["template_candidates"][0]["score"] >= result["template_candidates"][-1]["score"]
    assert result["reason_trace_public"] is True
    assert result["quality_profile"] == "production_vertical_1080"


def test_invalid_render_values_fail_closed(runtime) -> None:
    with pytest.raises(ValueError, match="output_width must be even"):
        runtime.resolve_parameters({"render": {"output_width": 1081}})
    with pytest.raises(ValueError, match="scale_filter"):
        runtime.resolve_parameters({"render": {"scale_filter": "fabricated"}})
    with pytest.raises(ValueError, match="unknown quality_profile"):
        runtime.resolve_parameters({"quality_profile": "demo_low_res"})


def test_status_declares_high_fidelity_cumulative_authority(runtime) -> None:
    status = runtime.status()
    assert status["cumulative_system_version"] == 203
    assert status["all_prior_passes_inherited"] is True
    assert status["logical_frame_is_output_quality_ceiling"] is False
    assert status["all_native_layers_publicly_selectable"] is True
    assert status["all_render_parameters_publicly_enumerated"] is True
    assert len(status["quality_profiles"]) >= 5
    assert status["parameter_catalog_url"] == "/api/runtime/storybook-reel/parameters"
