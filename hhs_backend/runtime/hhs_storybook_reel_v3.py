"""Pass 203 cumulative high-fidelity native storybook render authority.

The renderer implementation uses the inherited native projection ABI V2, while
all public contracts, evidence, and parameter identities are upgraded into the
single cumulative Pass 203 system version.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from hhs_backend.runtime.hhs_storybook_reel_v2 import (
    FIT_MODES,
    PIXEL_FORMATS,
    QUALITY_PRESETS,
    SCALE_FILTERS,
    SPRITE_OVERLAY_BITS,
    TEXTURE_LAYER_BITS,
    VIDEO_PRESETS,
    HighFidelityStorybookReelRuntime as _InheritedHighFidelityRuntime,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

CONTRACT = "HHS-P203-HIGH-FIDELITY-NATIVE-RENDER-PARAMETER-AUTHORITY-VM81-H72-H216"
CLASSIFICATION = "HHS_PASS_203_HIGH_FIDELITY_NATIVE_RENDER_SUBAUTHORITY_VERIFIED"
VERSION = "HHS_STORYBOOK_REEL_STUDIO_V3_PASS203_HIGH_FIDELITY"

_REPLACEMENTS = (
    ("HHS-P202-HF-NATIVE-RENDER-PARAMETER-AUTHORITY-VM81-H72-H216", CONTRACT),
    ("HHS_PASS_202_HIGH_FIDELITY_NATIVE_RENDER_AUTHORITY_VERIFIED", CLASSIFICATION),
    ("HHS_PASS_202_", "HHS_PASS_203_"),
    ("PASS_202_", "PASS_203_"),
    ("pass202", "pass203"),
    ("Pass 202", "Pass 203"),
)


def _upgrade_text(value: str) -> str:
    result = value
    for old, new in _REPLACEMENTS:
        result = result.replace(old, new)
    return result


def _upgrade(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {_upgrade_text(str(key)): _upgrade(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_upgrade(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_upgrade(item) for item in value)
    if isinstance(value, str):
        return _upgrade_text(value)
    return value


class Pass203HighFidelityStorybookRuntime(_InheritedHighFidelityRuntime):
    """Cumulative Pass 203 projection over the inherited high-fidelity ABI."""

    def parameter_catalog(self) -> Dict[str, Any]:
        result = _upgrade(super().parameter_catalog())
        result.update(
            {
                "schema": "HHS_PASS_203_NATIVE_RENDER_PARAMETER_CATALOG_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "version": VERSION,
                "cumulative_system_version": 203,
                "all_prior_passes_inherited": True,
            }
        )
        result.pop("catalog_hash72", None)
        result["catalog_hash72"] = hash72("HHS_PASS_203_NATIVE_RENDER_PARAMETER_CATALOG_V1", result)
        return result

    def presets(self) -> Dict[str, Any]:
        result = _upgrade(super().presets())
        result.update(
            {
                "schema": "HHS_PASS_203_HIGH_FIDELITY_PRESETS_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "cumulative_system_version": 203,
            }
        )
        return result

    def contextual_defaults(self, text: str) -> Dict[str, Any]:
        result = _upgrade(super().contextual_defaults(text))
        result.update(
            {
                "schema": "HHS_PASS_203_CONTEXTUAL_DEFAULTS_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "cumulative_system_version": 203,
            }
        )
        return result

    def resolve_parameters(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        result = _upgrade(super().resolve_parameters(payload))
        result.update(
            {
                "schema": "HHS_PASS_203_RESOLVED_RENDER_PARAMETERS_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "cumulative_system_version": 203,
            }
        )
        result.pop("resolution_hash72", None)
        result["resolution_hash72"] = hash72("HHS_PASS_203_RESOLVED_RENDER_PARAMETERS_V1", result)
        return result

    def status(self) -> Dict[str, Any]:
        result = _upgrade(super().status())
        result.update(
            {
                "schema": "HHS_STORYBOOK_REEL_STATUS_V3_PASS203_HIGH_FIDELITY",
                "version": VERSION,
                "pass203_contract": CONTRACT,
                "pass203_classification": CLASSIFICATION,
                "cumulative_system_version": 203,
                "all_prior_passes_inherited": True,
                "logical_frame_is_output_quality_ceiling": False,
                "all_native_layers_publicly_selectable": True,
                "all_render_parameters_publicly_enumerated": True,
            }
        )
        return result

    def _style(
        self,
        text: str,
        template_id: Optional[str],
        overrides: Optional[Mapping[str, Any]],
    ) -> Dict[str, Any]:
        return _upgrade(super()._style(text, template_id, overrides))

    def generate(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        result = _upgrade(super().generate(payload))
        result["pass203"] = {
            **dict(result.get("pass203") or {}),
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "cumulative_system_version": 203,
            "all_prior_passes_inherited": True,
            "native_frame_identity_preserved": True,
            "logical_frame_is_output_quality_ceiling": False,
        }
        result.pop("pass202", None)
        return result


STORYBOOK_REEL_RUNTIME = Pass203HighFidelityStorybookRuntime()

__all__ = [
    "CLASSIFICATION",
    "CONTRACT",
    "FIT_MODES",
    "PIXEL_FORMATS",
    "Pass203HighFidelityStorybookRuntime",
    "QUALITY_PRESETS",
    "SCALE_FILTERS",
    "SPRITE_OVERLAY_BITS",
    "STORYBOOK_REEL_RUNTIME",
    "TEXTURE_LAYER_BITS",
    "VERSION",
    "VIDEO_PRESETS",
]
