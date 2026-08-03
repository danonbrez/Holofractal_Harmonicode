"""Hydrated Pass 203 storybook/game functions for universal mainframe use."""
from __future__ import annotations

from typing import Any, Dict, Mapping

from hhs_backend.runtime.hhs_storybook_reel_v3 import STORYBOOK_REEL_RUNTIME


def status_storybook_renderer() -> Dict[str, Any]:
    """Return the cumulative high-fidelity storybook/game renderer status."""
    return STORYBOOK_REEL_RUNTIME.status()


def get_storybook_parameter_catalog() -> Dict[str, Any]:
    """Return every mutable render parameter and read-only compiled native constant."""
    return STORYBOOK_REEL_RUNTIME.parameter_catalog()


def get_storybook_quality_presets() -> Dict[str, Any]:
    """Return production, integer-scale, and lossless native quality profiles."""
    return STORYBOOK_REEL_RUNTIME.presets()


def contextual_storybook_direction(text: str) -> Dict[str, Any]:
    """Return ranked creative templates, reasons, palette planes, and render defaults."""
    return STORYBOOK_REEL_RUNTIME.contextual_defaults(text)


def resolve_storybook_parameters(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate and resolve the complete style, native-layer, and presentation request."""
    return STORYBOOK_REEL_RUNTIME.resolve_parameters(payload)


def render_storybook_filter_graph(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Resolve parameters and return the deterministic FFmpeg presentation graph."""
    resolved = STORYBOOK_REEL_RUNTIME.resolve_parameters(payload)
    return {
        "schema": "HHS_PASS_203_STORYBOOK_FILTER_GRAPH_V1",
        "quality_profile": resolved["quality_profile"],
        "resolution_hash72": resolved["resolution_hash72"],
        "render": resolved["render"],
        "filter_graph": STORYBOOK_REEL_RUNTIME.video_filter_graph(resolved["render"]),
        "ffmpeg_is_transport_authority": False,
        "native_frame_identity_preserved": True,
    }


def validate_storybook_parameter_catalog() -> Dict[str, Any]:
    """Validate parameter enumeration, layer coverage, and production profiles."""
    catalog = STORYBOOK_REEL_RUNTIME.parameter_catalog()
    presets = STORYBOOK_REEL_RUNTIME.presets()
    failures = []
    if not catalog.get("all_parameters_publicly_enumerated"):
        failures.append("parameter catalog is not closed")
    if len(catalog.get("native_layer_fields") or []) != 10:
        failures.append("native layer catalog must contain ten fields")
    if len(presets.get("quality_profiles") or {}) < 5:
        failures.append("quality profile catalog is incomplete")
    return {
        "schema": "HHS_PASS_203_STORYBOOK_PARAMETER_VALIDATION_V1",
        "ok": not failures,
        "failures": failures,
        "parameter_count": catalog.get("parameter_count"),
        "catalog_hash72": catalog.get("catalog_hash72"),
        "quality_profile_count": len(presets.get("quality_profiles") or {}),
        "native_layer_count": len(catalog.get("native_layer_fields") or []),
    }
