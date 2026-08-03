"""Pass 202 high-fidelity native storybook render and parameter authority."""
from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from hhs_backend.runtime.hhs_storybook_reel_timing_v1 import (
    DURATION_SECONDS,
    FPS,
    FRAME_COUNT,
    STYLE_TEMPLATES,
    contextual_defaults as v1_contextual_defaults,
)
from hhs_backend.runtime.hhs_storybook_reel_v1 import (
    COLOR_KEYS,
    STYLE_INTEGER_RANGES,
    StorybookReelRuntime,
    _decimal_fraction,
    _fraction_decimal,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

CONTRACT = "HHS-P202-HF-NATIVE-RENDER-PARAMETER-AUTHORITY-VM81-H72-H216"
CLASSIFICATION = "HHS_PASS_202_HIGH_FIDELITY_NATIVE_RENDER_AUTHORITY_VERIFIED"
VERSION = "HHS_STORYBOOK_REEL_STUDIO_V2_HIGH_FIDELITY"

TEXTURE_LAYER_BITS: Dict[str, int] = {
    "field": 1,
    "midground": 2,
    "materials": 4,
    "semantic": 8,
    "player": 16,
}
SPRITE_OVERLAY_BITS: Dict[str, int] = {
    "atmosphere": 1,
    "phase": 2,
    "glows": 4,
    "vignette": 8,
    "hud": 16,
}
FIT_MODES = (
    "cinematic_blur",
    "soft_storybook",
    "full_bleed_crop",
    "contain",
    "native_integer",
)
SCALE_FILTERS = ("lanczos", "spline", "bicubic", "bilinear", "neighbor")
VIDEO_PRESETS = ("veryslow", "slower", "slow", "medium", "fast")
PIXEL_FORMATS = ("yuv420p", "yuv422p", "yuv444p")

QUALITY_PRESETS: Dict[str, Dict[str, Any]] = {
    "production_vertical_1080": {
        "label": "Production Vertical 1080",
        "description": "Full-height derived background with a high-quality native foreground composition.",
        "output_width": 1080,
        "output_height": 1920,
        "fit_mode": "cinematic_blur",
        "scale_filter": "lanczos",
        "background_blur": 30,
        "foreground_width": 1080,
        "foreground_height": 972,
        "background_color": "#0b0910",
        "contrast": "1.06",
        "saturation": "1.16",
        "brightness": "-0.02",
        "gamma": "1.00",
        "sharpen_luma": "0.48",
        "vignette_strength": "0.20",
        "video_codec": "libx264",
        "video_preset": "slow",
        "crf": 16,
        "pixel_format": "yuv420p",
        "audio_bitrate": "192k",
        "movflags": "+faststart",
    },
    "production_vertical_1440": {
        "label": "Production Vertical 1440",
        "description": "Higher-resolution portrait master with cinematic native-frame compositing.",
        "output_width": 1440,
        "output_height": 2560,
        "fit_mode": "cinematic_blur",
        "scale_filter": "lanczos",
        "background_blur": 36,
        "foreground_width": 1440,
        "foreground_height": 1296,
        "background_color": "#0b0910",
        "contrast": "1.07",
        "saturation": "1.18",
        "brightness": "-0.02",
        "gamma": "1.00",
        "sharpen_luma": "0.52",
        "vignette_strength": "0.22",
        "video_codec": "libx264",
        "video_preset": "slow",
        "crf": 15,
        "pixel_format": "yuv420p",
        "audio_bitrate": "224k",
        "movflags": "+faststart",
    },
    "production_vertical_2160": {
        "label": "Production Vertical 2160",
        "description": "4K portrait delivery master preserving exact native-frame lineage.",
        "output_width": 2160,
        "output_height": 3840,
        "fit_mode": "cinematic_blur",
        "scale_filter": "lanczos",
        "background_blur": 48,
        "foreground_width": 2160,
        "foreground_height": 1944,
        "background_color": "#0b0910",
        "contrast": "1.08",
        "saturation": "1.20",
        "brightness": "-0.02",
        "gamma": "1.00",
        "sharpen_luma": "0.56",
        "vignette_strength": "0.24",
        "video_codec": "libx264",
        "video_preset": "slower",
        "crf": 14,
        "pixel_format": "yuv420p",
        "audio_bitrate": "256k",
        "movflags": "+faststart",
    },
    "native_integer_1080": {
        "label": "Native Integer 1080",
        "description": "Intentional crisp pixel presentation without treating it as the production quality ceiling.",
        "output_width": 1080,
        "output_height": 1920,
        "fit_mode": "native_integer",
        "scale_filter": "neighbor",
        "background_blur": 0,
        "foreground_width": 960,
        "foreground_height": 864,
        "background_color": "#0b0910",
        "contrast": "1.00",
        "saturation": "1.00",
        "brightness": "0.00",
        "gamma": "1.00",
        "sharpen_luma": "0.00",
        "vignette_strength": "0.00",
        "video_codec": "libx264",
        "video_preset": "medium",
        "crf": 18,
        "pixel_format": "yuv420p",
        "audio_bitrate": "192k",
        "movflags": "+faststart",
    },
    "native_lossless_rgba": {
        "label": "Native Lossless RGBA",
        "description": "Exact 160×144 RGBA source stream and manifest; MP4 transport remains optional.",
        "output_width": 160,
        "output_height": 144,
        "fit_mode": "contain",
        "scale_filter": "neighbor",
        "background_blur": 0,
        "foreground_width": 160,
        "foreground_height": 144,
        "background_color": "#000000",
        "contrast": "1.00",
        "saturation": "1.00",
        "brightness": "0.00",
        "gamma": "1.00",
        "sharpen_luma": "0.00",
        "vignette_strength": "0.00",
        "video_codec": "libx264",
        "video_preset": "medium",
        "crf": 0,
        "pixel_format": "yuv444p",
        "audio_bitrate": "192k",
        "movflags": "+faststart",
    },
}

TEMPLATE_SIGNALS: Dict[str, Tuple[str, ...]] = {
    "serif_fable": ("fable", "candle", "clock", "bell", "town", "book", "quiet", "legend"),
    "platformer_quest": ("quest", "game", "jump", "level", "run", "battle", "gate", "world"),
    "cinematic_parallax": ("cinematic", "journey", "mountain", "city", "memory", "dream", "shadow"),
    "chromatic_orbit": ("space", "orbit", "star", "planet", "cosmic", "galaxy", "moon"),
    "phase_wave": ("music", "wave", "phase", "rhythm", "dance", "signal", "frequency"),
    "bold_caption": ("urgent", "fast", "announcement", "lesson", "explainer", "action"),
    "minimal_ink": ("minimal", "still", "silence", "simple", "meditation", "clean"),
    "reciprocal_storybook": ("color", "reciprocal", "harmony", "lantern", "forest", "river", "story"),
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _decimal_value(value: Any, minimum: str, maximum: str, name: str) -> str:
    try:
        decimal = Decimal(str(value))
        low = Decimal(minimum)
        high = Decimal(maximum)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"render {name} must be a decimal value") from exc
    if decimal < low or decimal > high:
        raise ValueError(f"render {name} must be between {minimum} and {maximum}")
    normalized = format(decimal.normalize(), "f")
    if "." not in normalized:
        normalized += ".00"
    return normalized


def _color(value: Any, name: str) -> str:
    candidate = str(value or "").lower()
    if not re.fullmatch(r"#[0-9a-f]{6}", candidate):
        raise ValueError(f"render {name} must be #RRGGBB")
    return candidate


def _integer(value: Any, minimum: int, maximum: int, name: str) -> int:
    try:
        resolved = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"render {name} must be an integer") from exc
    if resolved < minimum or resolved > maximum:
        raise ValueError(f"render {name} must be between {minimum} and {maximum}")
    return resolved


def _even(value: int, name: str) -> int:
    if value % 2 != 0:
        raise ValueError(f"render {name} must be even")
    return value


def _mask(values: Mapping[str, Any], bits: Mapping[str, int]) -> Tuple[Dict[str, bool], int]:
    resolved: Dict[str, bool] = {}
    bitmask = 0
    for name, bit in bits.items():
        enabled = bool(values.get(name, True))
        resolved[name] = enabled
        if enabled:
            bitmask |= bit
    return resolved, bitmask


class HighFidelityStorybookReelRuntime(StorybookReelRuntime):
    """Integrated Pass 202 runtime preserving the inherited native authority."""

    def __init__(self, artifact_root: Optional[Path] = None) -> None:
        super().__init__(artifact_root=artifact_root)
        self._active_pass202_resolution: Optional[Dict[str, Any]] = None

    def _compiled_native_constants(self) -> List[Dict[str, Any]]:
        sources = (
            self.repo_root / "native_projects" / "hhs_vm81_game_level10" / "src" / "hhs_vm81_game_sprite.c",
            self.repo_root / "native_projects" / "hhs_vm81_game_level10" / "src" / "hhs_vm81_game_texture.c",
            self.repo_root / "native_projects" / "hhs_storybook_reel" / "include" / "hhs_storybook_reel_style_v2.h",
        )
        records: List[Dict[str, Any]] = []
        number_pattern = re.compile(r"(?<![A-Za-z0-9_])(0x[0-9A-Fa-f]+|[0-9]+)(?:U|UL|ULL|L)?")
        for source in sources:
            if not source.is_file():
                continue
            relative = source.relative_to(self.repo_root).as_posix()
            for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
                values = number_pattern.findall(line)
                if not values:
                    continue
                records.append(
                    {
                        "source": relative,
                        "line": line_number,
                        "values": values,
                        "expression": line.strip(),
                        "mutable": False,
                        "authority": "native_compile_time",
                    }
                )
        return records

    def parameter_catalog(self) -> Dict[str, Any]:
        style_default = STYLE_TEMPLATES["reciprocal_storybook"]
        style_fields = []
        for name, bounds in STYLE_INTEGER_RANGES.items():
            style_fields.append(
                {
                    "name": name,
                    "group": "native_style_v2",
                    "type": "integer",
                    "minimum": bounds[0],
                    "maximum": bounds[1],
                    "default": style_default[name],
                    "mutable": True,
                    "authority": "native_storybook_style_v2",
                }
            )
        for plane in ("x", "y", "z", "w"):
            for component in ("r", "g", "b"):
                style_fields.append(
                    {
                        "name": f"manual_{plane}.{component}",
                        "group": "reciprocal_palette",
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 255,
                        "default": None,
                        "mutable": True,
                        "authority": "native_storybook_style_v2",
                    }
                )
        native_layer_fields = [
            {
                "name": name,
                "group": "native_texture_layers",
                "type": "boolean",
                "bit": bit,
                "default": True,
                "mutable": True,
                "authority": "native_projection_bridge_v2",
            }
            for name, bit in TEXTURE_LAYER_BITS.items()
        ] + [
            {
                "name": name,
                "group": "native_sprite_overlays",
                "type": "boolean",
                "bit": bit,
                "default": True,
                "mutable": True,
                "authority": "native_projection_bridge_v2",
            }
            for name, bit in SPRITE_OVERLAY_BITS.items()
        ]
        render_fields = [
            {"name": "quality_profile", "type": "enum", "values": sorted(QUALITY_PRESETS), "default": "production_vertical_1080"},
            {"name": "output_width", "type": "integer", "minimum": 160, "maximum": 2160, "default": 1080},
            {"name": "output_height", "type": "integer", "minimum": 144, "maximum": 3840, "default": 1920},
            {"name": "fit_mode", "type": "enum", "values": list(FIT_MODES), "default": "cinematic_blur"},
            {"name": "scale_filter", "type": "enum", "values": list(SCALE_FILTERS), "default": "lanczos"},
            {"name": "foreground_width", "type": "integer", "minimum": 160, "maximum": 2160, "default": 1080},
            {"name": "foreground_height", "type": "integer", "minimum": 144, "maximum": 3840, "default": 972},
            {"name": "background_blur", "type": "integer", "minimum": 0, "maximum": 80, "default": 30},
            {"name": "background_color", "type": "color", "default": "#0b0910"},
            {"name": "contrast", "type": "decimal_string", "minimum": "0.50", "maximum": "2.00", "default": "1.06"},
            {"name": "saturation", "type": "decimal_string", "minimum": "0.00", "maximum": "3.00", "default": "1.16"},
            {"name": "brightness", "type": "decimal_string", "minimum": "-1.00", "maximum": "1.00", "default": "-0.02"},
            {"name": "gamma", "type": "decimal_string", "minimum": "0.10", "maximum": "10.00", "default": "1.00"},
            {"name": "sharpen_luma", "type": "decimal_string", "minimum": "0.00", "maximum": "2.00", "default": "0.48"},
            {"name": "vignette_strength", "type": "decimal_string", "minimum": "0.00", "maximum": "1.00", "default": "0.20"},
            {"name": "video_codec", "type": "enum", "values": ["libx264"], "default": "libx264"},
            {"name": "video_preset", "type": "enum", "values": list(VIDEO_PRESETS), "default": "slow"},
            {"name": "crf", "type": "integer", "minimum": 0, "maximum": 51, "default": 16},
            {"name": "pixel_format", "type": "enum", "values": list(PIXEL_FORMATS), "default": "yuv420p"},
            {"name": "audio_bitrate", "type": "string", "pattern": "^[0-9]{2,3}k$", "default": "192k"},
            {"name": "movflags", "type": "enum", "values": ["+faststart"], "default": "+faststart"},
        ]
        for field in render_fields:
            field.update({"group": "high_fidelity_presentation", "mutable": True, "authority": "pass202_compositor"})
        locked = [
            {"name": "logical_width", "value": 160},
            {"name": "logical_height", "value": 144},
            {"name": "fps", "value": FPS},
            {"name": "duration_seconds", "value": DURATION_SECONDS},
            {"name": "frame_count", "value": FRAME_COUNT},
            {"name": "single_threaded", "value": True},
            {"name": "parallel_computation_used", "value": False},
            {"name": "native_frame_identity_preserved", "value": True},
        ]
        for field in locked:
            field.update({"group": "authority_locked", "mutable": False, "authority": "inherited_vm81_storybook_authority"})
        compiled = self._compiled_native_constants()
        payload = {
            "schema": "HHS_PASS_202_NATIVE_RENDER_PARAMETER_CATALOG_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "version": VERSION,
            "style_fields": style_fields,
            "native_layer_fields": native_layer_fields,
            "render_fields": render_fields,
            "authority_locked_fields": locked,
            "compiled_native_constants": compiled,
            "quality_presets": self.presets()["presets"],
            "all_parameters_publicly_enumerated": True,
            "compiled_constants_are_read_only": True,
        }
        payload["parameter_count"] = len(style_fields) + len(native_layer_fields) + len(render_fields) + len(locked) + len(compiled)
        payload["catalog_hash72"] = hash72("HHS_PASS_202_NATIVE_RENDER_PARAMETER_CATALOG_V1", payload)
        return payload

    @staticmethod
    def presets() -> Dict[str, Any]:
        return {
            "schema": "HHS_PASS_202_HIGH_FIDELITY_PRESETS_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "default_profile": "production_vertical_1080",
            "preset_count": len(QUALITY_PRESETS),
            "presets": [{"id": preset_id, **values} for preset_id, values in QUALITY_PRESETS.items()],
        }

    @staticmethod
    def _template_candidates(text: str, selected_id: str) -> List[Dict[str, Any]]:
        normalized = str(text or "").lower()
        candidates: List[Dict[str, Any]] = []
        for template_id, template in STYLE_TEMPLATES.items():
            matched = [token for token in TEMPLATE_SIGNALS.get(template_id, ()) if token in normalized]
            score = 10 + len(matched) * 12 + (60 if template_id == selected_id else 0)
            reasons = []
            if template_id == selected_id:
                reasons.append("selected_by_contextual_default")
            if matched:
                reasons.append("matched:" + ",".join(matched))
            if not reasons:
                reasons.append("available_native_template")
            candidates.append(
                {
                    "template_id": template_id,
                    "label": template["label"],
                    "description": template["description"],
                    "score": score,
                    "reasons": reasons,
                    "style": {key: value for key, value in template.items() if key not in {"label", "description"}},
                }
            )
        candidates.sort(key=lambda item: (-int(item["score"]), str(item["template_id"])))
        return candidates[:3]

    def contextual_defaults(self, text: str) -> Dict[str, Any]:
        result = dict(v1_contextual_defaults(text))
        result["schema"] = "HHS_PASS_202_CONTEXTUAL_DEFAULTS_V1"
        result["contract"] = CONTRACT
        result["classification"] = CLASSIFICATION
        result["quality_profile"] = "production_vertical_1080"
        result["render"] = dict(QUALITY_PRESETS["production_vertical_1080"])
        result["native_layers"] = {
            "texture": {name: True for name in TEXTURE_LAYER_BITS},
            "sprite": {name: True for name in SPRITE_OVERLAY_BITS},
        }
        result["template_candidates"] = self._template_candidates(text, str(result["template_id"]))
        result["candidate_count"] = len(result["template_candidates"])
        result["reason_trace_public"] = True
        return result

    def resolve_parameters(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        text = str(payload.get("text") or "")
        defaults = self.contextual_defaults(text)
        profile_id = str(payload.get("quality_profile") or (payload.get("render") or {}).get("quality_profile") or defaults["quality_profile"])
        if profile_id not in QUALITY_PRESETS:
            raise ValueError(f"unknown quality_profile: {profile_id}")
        render = dict(QUALITY_PRESETS[profile_id])
        render.update(dict(payload.get("render") or {}))
        render["quality_profile"] = profile_id
        render["output_width"] = _even(_integer(render["output_width"], 160, 2160, "output_width"), "output_width")
        render["output_height"] = _even(_integer(render["output_height"], 144, 3840, "output_height"), "output_height")
        if render.get("fit_mode") not in FIT_MODES:
            raise ValueError(f"render fit_mode must be one of {', '.join(FIT_MODES)}")
        if render.get("scale_filter") not in SCALE_FILTERS:
            raise ValueError(f"render scale_filter must be one of {', '.join(SCALE_FILTERS)}")
        render["foreground_width"] = _even(
            _integer(render["foreground_width"], 160, render["output_width"], "foreground_width"),
            "foreground_width",
        )
        render["foreground_height"] = _even(
            _integer(render["foreground_height"], 144, render["output_height"], "foreground_height"),
            "foreground_height",
        )
        render["background_blur"] = _integer(render["background_blur"], 0, 80, "background_blur")
        render["background_color"] = _color(render["background_color"], "background_color")
        render["contrast"] = _decimal_value(render["contrast"], "0.50", "2.00", "contrast")
        render["saturation"] = _decimal_value(render["saturation"], "0.00", "3.00", "saturation")
        render["brightness"] = _decimal_value(render["brightness"], "-1.00", "1.00", "brightness")
        render["gamma"] = _decimal_value(render["gamma"], "0.10", "10.00", "gamma")
        render["sharpen_luma"] = _decimal_value(render["sharpen_luma"], "0.00", "2.00", "sharpen_luma")
        render["vignette_strength"] = _decimal_value(render["vignette_strength"], "0.00", "1.00", "vignette_strength")
        if render.get("video_codec") != "libx264":
            raise ValueError("render video_codec must be libx264")
        if render.get("video_preset") not in VIDEO_PRESETS:
            raise ValueError(f"render video_preset must be one of {', '.join(VIDEO_PRESETS)}")
        render["crf"] = _integer(render["crf"], 0, 51, "crf")
        if render.get("pixel_format") not in PIXEL_FORMATS:
            raise ValueError(f"render pixel_format must be one of {', '.join(PIXEL_FORMATS)}")
        if not re.fullmatch(r"[0-9]{2,3}k", str(render.get("audio_bitrate") or "")):
            raise ValueError("render audio_bitrate must match NN[k] or NNN[k]")
        if render.get("movflags") != "+faststart":
            raise ValueError("render movflags must be +faststart")

        native_request = dict(payload.get("native_layers") or {})
        texture_values, texture_mask = _mask(dict(native_request.get("texture") or {}), TEXTURE_LAYER_BITS)
        sprite_values, sprite_mask = _mask(dict(native_request.get("sprite") or {}), SPRITE_OVERLAY_BITS)

        style_resolution = StorybookReelRuntime._style(
            self,
            text,
            payload.get("template_id"),
            payload.get("style"),
        )
        resolved = {
            "schema": "HHS_PASS_202_RESOLVED_RENDER_PARAMETERS_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "quality_profile": profile_id,
            "style": style_resolution,
            "native_layers": {
                "texture": texture_values,
                "sprite": sprite_values,
                "texture_flags": texture_mask,
                "sprite_overlay_flags": sprite_mask,
            },
            "render": render,
            "authority_locked": {
                "logical_width": 160,
                "logical_height": 144,
                "fps": FPS,
                "duration_seconds": DURATION_SECONDS,
                "frame_count": FRAME_COUNT,
                "single_threaded": True,
                "parallel_computation_used": False,
            },
        }
        resolved["resolution_hash72"] = hash72("HHS_PASS_202_RESOLVED_RENDER_PARAMETERS_V1", resolved)
        return resolved

    def status(self) -> Dict[str, Any]:
        status = super().status()
        status.update(
            {
                "schema": "HHS_STORYBOOK_REEL_STATUS_V2_HIGH_FIDELITY",
                "version": VERSION,
                "pass202_contract": CONTRACT,
                "pass202_classification": CLASSIFICATION,
                "default_quality_profile": "production_vertical_1080",
                "fixed_neighbor_black_pad_default": False,
                "high_fidelity_compositor": True,
                "native_projection_bridge_v2": (
                    self.native_root / "src" / "hhs_storybook_reel_projection_v2.c"
                ).is_file(),
                "parameter_catalog_api": "/api/runtime/storybook-reel/parameters",
                "presets_api": "/api/runtime/storybook-reel/presets",
                "parameter_resolve_api": "/api/runtime/storybook-reel/parameters/resolve",
                "contextual_candidates_api": "/api/runtime/storybook-reel/defaults/candidates",
                "texture_layer_count": len(TEXTURE_LAYER_BITS),
                "sprite_overlay_count": len(SPRITE_OVERLAY_BITS),
                "quality_preset_count": len(QUALITY_PRESETS),
            }
        )
        return status

    def _style(self, text: str, template_id: Optional[str], overrides: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        style = super()._style(text, template_id, overrides)
        resolution = self._active_pass202_resolution
        if resolution:
            style["values"]["pass202_quality_profile"] = resolution["quality_profile"]
            style["values"]["pass202_render"] = resolution["render"]
            style["values"]["pass202_native_layers"] = resolution["native_layers"]
            style["values"]["pass202_resolution_hash72"] = resolution["resolution_hash72"]
        return style

    def _style_cli_arguments(self, style: Mapping[str, Any]) -> List[str]:
        arguments = super()._style_cli_arguments(style)
        resolution = self._active_pass202_resolution
        if resolution:
            arguments.extend(
                [
                    "--texture-flags",
                    str(resolution["native_layers"]["texture_flags"]),
                    "--sprite-overlay-flags",
                    str(resolution["native_layers"]["sprite_overlay_flags"]),
                ]
            )
        return arguments

    @staticmethod
    def video_filter_graph(render: Mapping[str, Any]) -> str:
        width = int(render["output_width"])
        height = int(render["output_height"])
        foreground_width = int(render["foreground_width"])
        foreground_height = int(render["foreground_height"])
        scale_filter = str(render["scale_filter"])
        fit_mode = str(render["fit_mode"])
        blur = int(render["background_blur"])
        color = str(render["background_color"]).replace("#", "0x")
        eq = (
            f"eq=contrast={render['contrast']}:saturation={render['saturation']}:"
            f"brightness={render['brightness']}:gamma={render['gamma']}"
        )
        sharpen = Decimal(str(render["sharpen_luma"]))
        vignette = Decimal(str(render["vignette_strength"]))
        fg_filters = [f"scale={foreground_width}:{foreground_height}:flags={scale_filter}", eq]
        if sharpen > 0:
            fg_filters.append(f"unsharp=5:5:{render['sharpen_luma']}:3:3:0.00")
        foreground = ",".join(fg_filters)
        tail = ""
        if vignette > 0:
            denominator = max(3, min(16, int(Decimal("4") + (Decimal("1") - vignette) * Decimal("8"))))
            tail = f",vignette=PI/{denominator}"

        if fit_mode in {"cinematic_blur", "soft_storybook"}:
            background = (
                f"scale={width}:{height}:force_original_aspect_ratio=increase:flags={scale_filter},"
                f"crop={width}:{height}"
            )
            if blur > 0:
                background += f",gblur=sigma={blur}"
            background += f",{eq}"
            if fit_mode == "soft_storybook":
                background += ",colorbalance=rs=.03:gs=.01:bs=-.02"
            return (
                f"[0:v]split=2[bg][fg];[bg]{background}[bgx];[fg]{foreground}[fgx];"
                f"[bgx][fgx]overlay=(W-w)/2:(H-h)/2[v0];[v0]{tail[1:] if tail else 'null'}[v]"
            )
        if fit_mode == "full_bleed_crop":
            return (
                f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase:flags={scale_filter},"
                f"crop={width}:{height},{eq}{tail}[v]"
            )
        if fit_mode == "native_integer":
            return (
                f"[0:v]scale={foreground_width}:{foreground_height}:flags=neighbor,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color={color}[v]"
            )
        return (
            f"[0:v]scale={foreground_width}:{foreground_height}:flags={scale_filter},{eq},"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color={color}{tail}[v]"
        )

    def _encode_mp4(self, styled_rgba: Path, narration_wav: Path, output: Path) -> None:
        resolution = self._active_pass202_resolution or self.resolve_parameters({"text": ""})
        render = resolution["render"]
        self._run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-f",
                "rawvideo",
                "-pixel_format",
                "rgba",
                "-video_size",
                "160x144",
                "-framerate",
                str(FPS),
                "-i",
                str(styled_rgba),
                "-i",
                str(narration_wav),
                "-filter_complex",
                self.video_filter_graph(render),
                "-map",
                "[v]",
                "-map",
                "1:a:0",
                "-frames:v",
                str(FRAME_COUNT),
                "-c:v",
                str(render["video_codec"]),
                "-preset",
                str(render["video_preset"]),
                "-crf",
                str(render["crf"]),
                "-pix_fmt",
                str(render["pixel_format"]),
                "-r",
                str(FPS),
                "-c:a",
                "aac",
                "-b:a",
                str(render["audio_bitrate"]),
                "-movflags",
                str(render["movflags"]),
                "-threads",
                "1",
                "-filter_threads",
                "1",
                "-filter_complex_threads",
                "1",
                str(output),
            ],
            timeout=3600,
        )

    def _probe_video(self, path: Path) -> Dict[str, Any]:
        resolution = self._active_pass202_resolution or self.resolve_parameters({"text": ""})
        expected = resolution["render"]
        result = self._run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration,size:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
                "-of",
                "json",
                str(path),
            ],
            timeout=120,
        )
        payload = json.loads(result.stdout or "{}")
        streams = payload.get("streams") or []
        video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
        audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
        if not video or not audio:
            raise RuntimeError("generated MP4 is missing video or audio stream")
        duration = _decimal_fraction(str((payload.get("format") or {}).get("duration") or "0"))
        if duration < Fraction(899, 10) or duration > Fraction(901, 10):
            raise RuntimeError(f"generated MP4 duration is outside 90-second acceptance: {_fraction_decimal(duration)}")
        if video.get("codec_name") != "h264":
            raise RuntimeError("generated MP4 video stream is not H.264")
        if int(video.get("width") or 0) != int(expected["output_width"]) or int(video.get("height") or 0) != int(expected["output_height"]):
            raise RuntimeError("generated MP4 dimensions do not match resolved Pass 202 parameters")
        if str(video.get("r_frame_rate")) != f"{FPS}/1":
            raise RuntimeError("generated MP4 frame rate is not 30 fps")
        return {
            "duration_seconds": _fraction_decimal(duration),
            "size_bytes": int((payload.get("format") or {}).get("size") or 0),
            "video_codec": video.get("codec_name"),
            "audio_codec": audio.get("codec_name"),
            "width": int(video.get("width") or 0),
            "height": int(video.get("height") or 0),
            "frame_rate": video.get("r_frame_rate"),
            "audio_sample_rate": int(audio.get("sample_rate") or 0),
            "audio_channels": int(audio.get("channels") or 0),
            "quality_profile": resolution["quality_profile"],
            "resolution_hash72": resolution["resolution_hash72"],
        }

    def generate(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        resolution = self.resolve_parameters(payload)
        request_payload = dict(payload)
        request_payload["template_id"] = resolution["style"]["template_id"]
        request_payload["style"] = resolution["style"]["values"]
        with self._authority_lock:
            prior = self._active_pass202_resolution
            self._active_pass202_resolution = resolution
            try:
                result = super().generate(request_payload)
            finally:
                self._active_pass202_resolution = prior
        result["pass202"] = {
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "quality_profile": resolution["quality_profile"],
            "resolution_hash72": resolution["resolution_hash72"],
            "render": resolution["render"],
            "native_layers": resolution["native_layers"],
            "native_frame_identity_preserved": True,
            "fixed_neighbor_black_pad_default": False,
        }
        return result


STORYBOOK_REEL_RUNTIME = HighFidelityStorybookReelRuntime()

__all__ = [
    "CLASSIFICATION",
    "CONTRACT",
    "QUALITY_PRESETS",
    "SPRITE_OVERLAY_BITS",
    "STORYBOOK_REEL_RUNTIME",
    "TEXTURE_LAYER_BITS",
    "VERSION",
    "HighFidelityStorybookReelRuntime",
]
