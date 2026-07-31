"""Typed native reconstruction recipes and residual reports for HHS Pass 181.

Recipes bind native scene, sprite-map, texture-map, caption, palette, camera,
lighting, transition, particle, foreground, and audio instructions to a canonical
reference timeline. Residual reports compare a native output decode manifest to
that reference without allowing reference frames, packets, textures, or audio to
become rendering inputs.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

from hhs_installer.canonical import canonical_bytes, hash72, hash216, stable

CONTRACT = "HHS-P181-NCSR-GHIR-VM81-H72-H216"
AUTHORITY = "HHS_VM81_SINGLETON_GRAPHICS_HYDRATION_AUTHORITY_V1"
RECIPE_IDENTITY_DOMAIN = "HHS-P181-NATIVE-RECONSTRUCTION-RECIPE-V1"
RESIDUAL_IDENTITY_DOMAIN = "HHS-P181-NATIVE-RECONSTRUCTION-RESIDUAL-V1"
RECIPE_RECEIPT_DOMAIN = "HHS-P181-NATIVE-RECONSTRUCTION-RECEIPT-V1"

ALLOWED_LAYER_TYPES = frozenset(
    {
        "scene",
        "background",
        "midground",
        "sprite_map",
        "texture_map",
        "caption",
        "camera",
        "lighting",
        "transition",
        "particle",
        "foreground",
        "audio_visualizer",
        "residual_asset",
    }
)
ALLOWED_AUDIO_MODES = frozenset({"native_synthesis", "native_pcm_recipe", "silence"})
ALLOWED_CAMERA_MODES = frozenset({"static", "pan", "tilt", "zoom", "parallax", "orbit", "path"})
FORBIDDEN_SOURCE_VALUES = frozenset(
    {
        "reference_frame",
        "reference_texture",
        "reference_audio",
        "encoded_packet",
        "decoded_packet",
        "passthrough",
        "copied_frame",
        "copied_audio",
    }
)
FORBIDDEN_KEYS = frozenset(
    {
        "reference_frame",
        "reference_frames",
        "reference_texture",
        "reference_textures",
        "reference_audio",
        "encoded_packets",
        "decoded_packets",
        "passthrough_bytes",
    }
)
SEMANTIC_RESIDUAL_FIELDS = {
    "palette_phase_mismatches": "PALETTE_PHASE_RESIDUAL",
    "caption_layout_mismatches": "CAPTION_LAYOUT_RESIDUAL",
    "caption_timing_mismatches": "CAPTION_TIMING_RESIDUAL",
    "camera_motion_mismatches": "CAMERA_MOTION_RESIDUAL",
    "lighting_mismatches": "LIGHTING_RESIDUAL",
    "provenance_mismatches": "UNEXPLAINED_PIXEL_PROVENANCE",
}


class NativeRecipeError(ValueError):
    """Raised when a recipe or residual report violates Pass 181 authority."""


def _artifact_filename(canonical_identity: str) -> str:
    return hashlib.sha256(canonical_identity.encode("utf-8")).hexdigest() + ".json"


def _mapping(value: Any, code: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise NativeRecipeError(code)
    return value


def _list(value: Any, code: str) -> list[Any]:
    if not isinstance(value, list):
        raise NativeRecipeError(code)
    return value


def _integer(value: Any, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise NativeRecipeError(code)
    return value


def _reject_reference_passthrough(value: Any, *, path: str = "recipe") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            lexical_key = str(key).lower()
            if lexical_key in FORBIDDEN_KEYS:
                raise NativeRecipeError(f"P181_REFERENCE_PASSTHROUGH_KEY_PROHIBITED:{path}.{lexical_key}")
            _reject_reference_passthrough(item, path=f"{path}.{lexical_key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _reject_reference_passthrough(item, path=f"{path}[{index}]")
        return
    if isinstance(value, str) and value.lower() in FORBIDDEN_SOURCE_VALUES:
        raise NativeRecipeError(f"P181_REFERENCE_PASSTHROUGH_VALUE_PROHIBITED:{path}")


def _media_timelines(manifest: Mapping[str, Any], media_type: str) -> list[Mapping[str, Any]]:
    timelines = manifest.get("decoded_timelines")
    if not isinstance(timelines, list):
        raise NativeRecipeError("P181_DECODED_TIMELINES_REQUIRED")
    matches = []
    for timeline in timelines:
        if not isinstance(timeline, Mapping):
            raise NativeRecipeError("P181_DECODED_TIMELINE_INVALID")
        projection = timeline.get("canonical_projection")
        if isinstance(projection, Mapping) and projection.get("media_type") == media_type:
            matches.append(timeline)
    return sorted(matches, key=lambda item: int(item.get("source_stream_index", 0)))


def _reference_video_frame_count(reference_manifest: Mapping[str, Any]) -> int:
    videos = _media_timelines(reference_manifest, "video")
    if not videos:
        raise NativeRecipeError("P181_REFERENCE_VIDEO_TIMELINE_REQUIRED")
    return sum(_integer(video.get("record_count"), "P181_VIDEO_RECORD_COUNT_INVALID") for video in videos)


def _normalize_palette(value: Any) -> Dict[str, int]:
    palette = _mapping(value, "P181_SCENE_PALETTE_REQUIRED")
    normalized = {}
    for key in ("x", "y", "z", "w"):
        phase = _integer(palette.get(key), f"P181_PALETTE_{key.upper()}_INVALID")
        if phase < 0 or phase >= 72:
            raise NativeRecipeError(f"P181_PALETTE_{key.upper()}_OUT_OF_RANGE")
        normalized[key] = phase
    if normalized["z"] != (normalized["x"] + 36) % 72:
        raise NativeRecipeError("P181_PALETTE_RECIPROCAL_INVARIANT_FAILED")
    return normalized


def _normalize_layer(value: Any, *, scene_index: int, layer_index: int) -> Dict[str, Any]:
    layer = _mapping(value, "P181_NATIVE_LAYER_INVALID")
    layer_type = str(layer.get("type") or "")
    source_type = str(layer.get("source_type") or "")
    authority = str(layer.get("authority") or "")
    layer_id = str(layer.get("layer_id") or "").strip()
    if layer_type not in ALLOWED_LAYER_TYPES:
        raise NativeRecipeError(f"P181_NATIVE_LAYER_TYPE_REJECTED:{layer_type}")
    if source_type.lower() in FORBIDDEN_SOURCE_VALUES:
        raise NativeRecipeError(f"P181_REFERENCE_PASSTHROUGH_PROHIBITED:{source_type}")
    if not source_type.startswith("native_") and source_type != "hydrated_native_asset":
        raise NativeRecipeError(f"P181_NATIVE_LAYER_SOURCE_REQUIRED:{source_type}")
    if authority != "HHS_NATIVE_ABI":
        raise NativeRecipeError(f"P181_NATIVE_LAYER_AUTHORITY_REQUIRED:{authority}")
    if not layer_id:
        raise NativeRecipeError(f"P181_NATIVE_LAYER_ID_REQUIRED:{scene_index}:{layer_index}")
    parameters = stable(layer.get("parameters") or {})
    normalized = {
        "layer_id": layer_id,
        "type": layer_type,
        "source_type": source_type,
        "authority": authority,
        "parameters": parameters,
    }
    _reject_reference_passthrough(normalized, path=f"scenes[{scene_index}].layers[{layer_index}]")
    return normalized


def _normalize_caption(value: Any, *, scene_start: int, scene_end: int) -> Dict[str, Any]:
    caption = _mapping(value, "P181_CAPTION_INVALID")
    start = _integer(caption.get("start_frame"), "P181_CAPTION_START_INVALID")
    end = _integer(caption.get("end_frame"), "P181_CAPTION_END_INVALID")
    text = caption.get("text")
    if not isinstance(text, str) or not text:
        raise NativeRecipeError("P181_CAPTION_TEXT_REQUIRED")
    if start < scene_start or end <= start or end > scene_end:
        raise NativeRecipeError("P181_CAPTION_FRAME_RANGE_INVALID")
    style = stable(_mapping(caption.get("style") or {}, "P181_CAPTION_STYLE_INVALID"))
    normalized = {
        "caption_id": str(caption.get("caption_id") or f"caption-{start}-{end}"),
        "start_frame": start,
        "end_frame": end,
        "text": text,
        "style": style,
        "authority": "HHS_NATIVE_ABI",
        "source_type": "native_caption_layout",
    }
    _reject_reference_passthrough(normalized, path="caption")
    return normalized


def validate_native_reconstruction_recipe(
    recipe: Mapping[str, Any],
    reference_manifest: Mapping[str, Any],
) -> Dict[str, Any]:
    """Validate and canonicalize a full-frame native rendering recipe."""

    recipe = _mapping(recipe, "P181_NATIVE_RECIPE_REQUIRED")
    reference_manifest = _mapping(reference_manifest, "P181_REFERENCE_MANIFEST_REQUIRED")
    _reject_reference_passthrough(recipe)
    reference_id = str(reference_manifest.get("reference_id") or "")
    timeline_hash216 = str(reference_manifest.get("timeline_hash216") or "")
    if not reference_id or not timeline_hash216:
        raise NativeRecipeError("P181_REFERENCE_TIMELINE_IDENTITY_REQUIRED")
    if str(recipe.get("reference_id") or "") != reference_id:
        raise NativeRecipeError("P181_RECIPE_REFERENCE_IDENTITY_MISMATCH")
    if str(recipe.get("target_timeline_hash216") or "") != timeline_hash216:
        raise NativeRecipeError("P181_RECIPE_TIMELINE_IDENTITY_MISMATCH")

    frame_count = _reference_video_frame_count(reference_manifest)
    scenes = _list(recipe.get("scenes"), "P181_RECIPE_SCENES_REQUIRED")
    if not scenes:
        raise NativeRecipeError("P181_RECIPE_SCENES_REQUIRED")

    normalized_scenes = []
    expected_start = 0
    for scene_index, raw_scene in enumerate(scenes):
        scene = _mapping(raw_scene, "P181_SCENE_INVALID")
        start = _integer(scene.get("start_frame"), "P181_SCENE_START_INVALID")
        end = _integer(scene.get("end_frame"), "P181_SCENE_END_INVALID")
        if start != expected_start or end <= start or end > frame_count:
            raise NativeRecipeError(f"P181_SCENE_COVERAGE_INVALID:{scene_index}")
        layers = _list(scene.get("layers"), "P181_SCENE_LAYERS_REQUIRED")
        if not layers:
            raise NativeRecipeError("P181_SCENE_LAYERS_REQUIRED")
        normalized_layers = [
            _normalize_layer(layer, scene_index=scene_index, layer_index=layer_index)
            for layer_index, layer in enumerate(layers)
        ]
        if not any(layer["type"] in {"scene", "background", "midground", "sprite_map", "texture_map"} for layer in normalized_layers):
            raise NativeRecipeError("P181_SCENE_VISUAL_LAYER_REQUIRED")

        camera = stable(_mapping(scene.get("camera") or {}, "P181_CAMERA_REQUIRED"))
        camera_mode = str(camera.get("mode") or "")
        if camera_mode not in ALLOWED_CAMERA_MODES:
            raise NativeRecipeError(f"P181_CAMERA_MODE_REJECTED:{camera_mode}")
        captions = [
            _normalize_caption(caption, scene_start=start, scene_end=end)
            for caption in _list(scene.get("captions") or [], "P181_CAPTIONS_INVALID")
        ]
        normalized_scene = {
            "scene_id": str(scene.get("scene_id") or f"scene-{scene_index}"),
            "start_frame": start,
            "end_frame": end,
            "palette": _normalize_palette(scene.get("palette")),
            "layers": normalized_layers,
            "captions": captions,
            "camera": camera,
            "lighting": stable(_mapping(scene.get("lighting") or {}, "P181_LIGHTING_INVALID")),
            "transition": stable(_mapping(scene.get("transition") or {}, "P181_TRANSITION_INVALID")),
        }
        _reject_reference_passthrough(normalized_scene, path=f"scenes[{scene_index}]")
        normalized_scenes.append(normalized_scene)
        expected_start = end
    if expected_start != frame_count:
        raise NativeRecipeError("P181_RECIPE_DOES_NOT_COVER_COMPLETE_VIDEO_TIMELINE")

    audio = _mapping(recipe.get("audio"), "P181_NATIVE_AUDIO_RECIPE_REQUIRED")
    audio_mode = str(audio.get("mode") or "")
    if audio_mode not in ALLOWED_AUDIO_MODES:
        raise NativeRecipeError(f"P181_NATIVE_AUDIO_MODE_REJECTED:{audio_mode}")
    normalized_audio = {
        "mode": audio_mode,
        "authority": "HHS_NATIVE_ABI",
        "parameters": stable(audio.get("parameters") or {}),
    }
    _reject_reference_passthrough(normalized_audio, path="audio")

    canonical_recipe = {
        "schema": "HHS_P181_NATIVE_RECONSTRUCTION_RECIPE_V1",
        "contract": CONTRACT,
        "authority": AUTHORITY,
        "reference_id": reference_id,
        "target_timeline_hash216": timeline_hash216,
        "frame_count": frame_count,
        "scenes": normalized_scenes,
        "audio": normalized_audio,
        "threejs_role": "preview_enhancement_only",
        "final_frame_authority": "HHS_NATIVE_ABI",
        "single_commit_authority": True,
    }
    recipe_hash216 = hash216(canonical_recipe, domain=RECIPE_IDENTITY_DOMAIN)
    canonical_recipe["recipe_hash216"] = recipe_hash216
    canonical_recipe["receipt_hash72"] = hash72(canonical_recipe, domain=RECIPE_RECEIPT_DOMAIN)
    return canonical_recipe


def _compare_records(
    reference_timelines: Sequence[Mapping[str, Any]],
    native_timelines: Sequence[Mapping[str, Any]],
) -> Dict[str, int]:
    content_mismatches = 0
    timing_mismatches = 0
    missing_records = 0
    extra_records = 0
    paired_streams = min(len(reference_timelines), len(native_timelines))
    for stream_index in range(paired_streams):
        reference_records = _list(reference_timelines[stream_index].get("records"), "P181_REFERENCE_RECORDS_INVALID")
        native_records = _list(native_timelines[stream_index].get("records"), "P181_NATIVE_RECORDS_INVALID")
        paired_records = min(len(reference_records), len(native_records))
        for record_index in range(paired_records):
            reference_record = _mapping(reference_records[record_index], "P181_REFERENCE_RECORD_INVALID")
            native_record = _mapping(native_records[record_index], "P181_NATIVE_RECORD_INVALID")
            if reference_record.get("sha256") != native_record.get("sha256"):
                content_mismatches += 1
            if any(reference_record.get(field) != native_record.get(field) for field in ("dts", "pts", "duration", "size_bytes")):
                timing_mismatches += 1
        if len(reference_records) > len(native_records):
            missing_records += len(reference_records) - len(native_records)
        elif len(native_records) > len(reference_records):
            extra_records += len(native_records) - len(reference_records)
    if len(reference_timelines) > len(native_timelines):
        missing_records += sum(
            len(_list(timeline.get("records"), "P181_REFERENCE_RECORDS_INVALID"))
            for timeline in reference_timelines[paired_streams:]
        )
    elif len(native_timelines) > len(reference_timelines):
        extra_records += sum(
            len(_list(timeline.get("records"), "P181_NATIVE_RECORDS_INVALID"))
            for timeline in native_timelines[paired_streams:]
        )
    return {
        "content_mismatches": content_mismatches,
        "timing_mismatches": timing_mismatches,
        "missing_records": missing_records,
        "extra_records": extra_records,
        "reference_streams": len(reference_timelines),
        "native_streams": len(native_timelines),
    }


def build_native_reconstruction_residual_report(
    reference_manifest: Mapping[str, Any],
    native_manifest: Mapping[str, Any],
    validated_recipe: Mapping[str, Any],
    *,
    semantic_metrics: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Compare canonical decode manifests and emit typed exact residual counts."""

    reference_manifest = _mapping(reference_manifest, "P181_REFERENCE_MANIFEST_REQUIRED")
    native_manifest = _mapping(native_manifest, "P181_NATIVE_MANIFEST_REQUIRED")
    validated_recipe = _mapping(validated_recipe, "P181_VALIDATED_RECIPE_REQUIRED")
    _reject_reference_passthrough(validated_recipe)
    if validated_recipe.get("recipe_hash216") is None:
        raise NativeRecipeError("P181_VALIDATED_RECIPE_IDENTITY_REQUIRED")
    if validated_recipe.get("target_timeline_hash216") != reference_manifest.get("timeline_hash216"):
        raise NativeRecipeError("P181_RESIDUAL_RECIPE_REFERENCE_MISMATCH")

    video = _compare_records(
        _media_timelines(reference_manifest, "video"),
        _media_timelines(native_manifest, "video"),
    )
    audio = _compare_records(
        _media_timelines(reference_manifest, "audio"),
        _media_timelines(native_manifest, "audio"),
    )
    metrics = stable(semantic_metrics or {})
    residuals = []
    if video["content_mismatches"] or video["missing_records"] or video["extra_records"]:
        residuals.append({"class": "FRAME_CONTENT_RESIDUAL", **video})
    if audio["content_mismatches"] or audio["missing_records"] or audio["extra_records"]:
        residuals.append({"class": "AUDIO_CONTENT_RESIDUAL", **audio})
    timing_total = video["timing_mismatches"] + audio["timing_mismatches"]
    if timing_total:
        residuals.append(
            {
                "class": "TIMELINE_RESIDUAL",
                "video_timing_mismatches": video["timing_mismatches"],
                "audio_timing_mismatches": audio["timing_mismatches"],
            }
        )
    for field, residual_class in SEMANTIC_RESIDUAL_FIELDS.items():
        count = metrics.get(field, 0)
        count = _integer(count, f"P181_{field.upper()}_INVALID")
        if count < 0:
            raise NativeRecipeError(f"P181_{field.upper()}_NEGATIVE")
        if count:
            residuals.append({"class": residual_class, "mismatch_count": count})

    exact_match = not residuals
    identity_payload = {
        "reference_timeline_hash216": reference_manifest.get("timeline_hash216"),
        "native_timeline_hash216": native_manifest.get("timeline_hash216"),
        "recipe_hash216": validated_recipe.get("recipe_hash216"),
        "video": video,
        "audio": audio,
        "semantic_metrics": metrics,
        "residuals": residuals,
    }
    report = {
        "schema": "HHS_P181_NATIVE_RECONSTRUCTION_RESIDUAL_REPORT_V1",
        "contract": CONTRACT,
        "authority": AUTHORITY,
        "exact_decoded_audiovisual_match": exact_match,
        **identity_payload,
    }
    report["residual_report_hash216"] = hash216(identity_payload, domain=RESIDUAL_IDENTITY_DOMAIN)
    report["receipt_hash72"] = hash72(report, domain=RECIPE_RECEIPT_DOMAIN)
    return report


class NativeRecipeRuntime:
    """Serialized artifact store for validated recipes and residual reports."""

    def __init__(self, artifact_root: Path) -> None:
        self.recipe_root = Path(artifact_root) / "recipes"
        self.residual_root = Path(artifact_root) / "residuals"
        self.recipe_root.mkdir(parents=True, exist_ok=True)
        self.residual_root.mkdir(parents=True, exist_ok=True)

    def validate_and_store(
        self,
        recipe: Mapping[str, Any],
        reference_manifest: Mapping[str, Any],
    ) -> Dict[str, Any]:
        validated = validate_native_reconstruction_recipe(recipe, reference_manifest)
        output = self.recipe_root / _artifact_filename(str(validated["recipe_hash216"]))
        output.write_bytes(canonical_bytes(validated))
        return {**validated, "record_path": str(output)}

    def compare_and_store(
        self,
        reference_manifest: Mapping[str, Any],
        native_manifest: Mapping[str, Any],
        validated_recipe: Mapping[str, Any],
        *,
        semantic_metrics: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        report = build_native_reconstruction_residual_report(
            reference_manifest,
            native_manifest,
            validated_recipe,
            semantic_metrics=semantic_metrics,
        )
        output = self.residual_root / _artifact_filename(str(report["residual_report_hash216"]))
        output.write_bytes(canonical_bytes(report))
        return {**report, "record_path": str(output)}
