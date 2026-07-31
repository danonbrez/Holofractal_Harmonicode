"""Pass 181 native graphics inverse-render hydration authority core.

This implementation slice establishes immutable MP4 identity, native-frame
provenance enforcement, exact reciprocal palette phases, typed optimization
records, fidelity classification, and gated runtime-constraint promotion. It
makes no claim that media decomposition or native reconstruction is complete.
"""
from __future__ import annotations

import hashlib
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from hhs_installer.canonical import canonical_bytes, hash72, hash216, stable

VERSION = "HHS_GRAPHICS_HYDRATION_RUNTIME_V1"
AUTHORITY = "HHS_VM81_SINGLETON_GRAPHICS_HYDRATION_AUTHORITY_V1"
CONTRACT = "HHS-P181-NCSR-GHIR-VM81-H72-H216"
REFERENCE_IDENTITY_DOMAIN = "HHS-P181-REFERENCE-MP4-IDENTITY-V1"
TRIAL_IDENTITY_DOMAIN = "HHS-P181-GRAPHICS-HYDRATION-TRIAL-V1"
CONSTRAINT_IDENTITY_DOMAIN = "HHS-P181-GRAPHICS-CONSTRAINT-V1"
RECEIPT_DOMAIN = "HHS-P181-GRAPHICS-HYDRATION-RECEIPT-V1"
MAX_REFERENCE_BYTES = 4 * 1024 * 1024 * 1024

PROMOTION_STAGES: Sequence[str] = (
    "reproduced",
    "cross_sample_verified",
    "positive_tested",
    "negative_tested",
    "adversarial_tested",
    "replay_verified",
    "calibrated",
    "contradiction_scan_passed",
)

FIDELITY_LEVELS: Sequence[str] = (
    "NATIVE_SEMANTIC_REPRODUCTION",
    "NATIVE_PERCEPTUAL_REPRODUCTION",
    "NATIVE_DECODED_FRAME_EXACTNESS",
    "NATIVE_DECODED_AUDIOVISUAL_EXACTNESS",
    "MP4_BITSTREAM_IDENTITY_WHEN_ENCODER_STATE_IS_AVAILABLE",
)

RESIDUAL_CLASSES: Sequence[str] = (
    "BACKGROUND_GEOMETRY_RESIDUAL",
    "SPRITE_SHAPE_RESIDUAL",
    "TEXTURE_DETAIL_RESIDUAL",
    "PALETTE_PHASE_RESIDUAL",
    "LIGHTING_RESIDUAL",
    "CAMERA_MOTION_RESIDUAL",
    "CAPTION_LAYOUT_RESIDUAL",
    "CAPTION_TIMING_RESIDUAL",
    "AUDIO_ALIGNMENT_RESIDUAL",
    "ENCODING_RESIDUAL",
    "UNEXPLAINED_PIXEL_PROVENANCE",
)

ALLOWED_NATIVE_LAYER_TYPES = frozenset(
    {
        "scene",
        "background",
        "midground",
        "sprite",
        "texture",
        "caption",
        "lighting",
        "overlay",
        "particle",
        "foreground",
        "residual_asset",
    }
)
FORBIDDEN_REFERENCE_SOURCES = frozenset(
    {
        "reference_frame",
        "reference_texture",
        "encoded_packet",
        "decoded_packet",
        "passthrough",
        "copied_frame",
    }
)


class GraphicsHydrationError(ValueError):
    """Raised when Pass 181 authority rules reject an operation."""


@dataclass(frozen=True)
class ReferenceIdentity:
    reference_id: str
    sha256: str
    size_bytes: int
    logical_name: str
    suffix: str
    source_path: str
    stat_mode: int
    stat_mtime_ns: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference_id": self.reference_id,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "logical_name": self.logical_name,
            "suffix": self.suffix,
            "source_path": self.source_path,
            "stat_mode": self.stat_mode,
            "stat_mtime_ns": self.stat_mtime_ns,
        }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def _artifact_filename(canonical_identity: str) -> str:
    """Map arbitrary canonical glyph identities to portable filesystem names."""

    return hashlib.sha256(canonical_identity.encode("utf-8")).hexdigest() + ".json"


def reciprocal_palette_phases(x_phase: int, y_phase: int, w_phase: int) -> Dict[str, int]:
    phases = {"x": int(x_phase), "y": int(y_phase), "w": int(w_phase)}
    if any(value < 0 or value >= 72 for value in phases.values()):
        raise GraphicsHydrationError("P181_PALETTE_PHASE_OUT_OF_RANGE")
    return {
        "x": phases["x"],
        "y": phases["y"],
        "z": (phases["x"] + 36) % 72,
        "w": phases["w"],
    }


def classify_fidelity(metrics: Mapping[str, Any]) -> Dict[str, Any]:
    """Return the strongest truthfully supported reproduction classification."""

    semantic = bool(metrics.get("semantic_match"))
    perceptual = semantic and bool(metrics.get("perceptual_match"))
    frames = perceptual and bool(metrics.get("decoded_frames_equal"))
    audiovisual = frames and bool(metrics.get("decoded_pcm_equal")) and bool(metrics.get("pts_equal"))
    encoder_state = bool(metrics.get("encoder_state_available"))
    bitstream = audiovisual and encoder_state and bool(metrics.get("mp4_bytes_equal"))

    levels = []
    if semantic:
        levels.append(FIDELITY_LEVELS[0])
    if perceptual:
        levels.append(FIDELITY_LEVELS[1])
    if frames:
        levels.append(FIDELITY_LEVELS[2])
    if audiovisual:
        levels.append(FIDELITY_LEVELS[3])
    if bitstream:
        levels.append(FIDELITY_LEVELS[4])

    return {
        "schema": "HHS_P181_FIDELITY_CLASSIFICATION_V1",
        "ok": bool(levels),
        "levels": levels,
        "strongest": levels[-1] if levels else "NO_REPRODUCTION_CLASSIFICATION",
        "bitstream_identity_eligible": audiovisual and encoder_state,
    }


def validate_native_frame_provenance(frame_manifest: Mapping[str, Any]) -> Dict[str, Any]:
    """Reject reference passthrough and unexplained authoritative frame layers."""

    frame_index = frame_manifest.get("frame_index")
    layers = frame_manifest.get("layers")
    if not isinstance(frame_index, int) or frame_index < 0:
        raise GraphicsHydrationError("P181_FRAME_INDEX_INVALID")
    if not isinstance(layers, list) or not layers:
        raise GraphicsHydrationError("P181_FRAME_LAYERS_REQUIRED")

    seen_types = set()
    roots = []
    for index, layer in enumerate(layers):
        if not isinstance(layer, Mapping):
            raise GraphicsHydrationError(f"P181_FRAME_LAYER_INVALID:{index}")
        layer_type = str(layer.get("type") or "")
        source_type = str(layer.get("source_type") or "")
        authority = str(layer.get("authority") or "")
        if layer_type not in ALLOWED_NATIVE_LAYER_TYPES:
            raise GraphicsHydrationError(f"P181_FRAME_LAYER_TYPE_REJECTED:{layer_type}")
        if source_type in FORBIDDEN_REFERENCE_SOURCES:
            raise GraphicsHydrationError(f"P181_REFERENCE_PASSTHROUGH_PROHIBITED:{source_type}")
        if authority != "HHS_NATIVE_ABI":
            raise GraphicsHydrationError(f"P181_NON_NATIVE_FRAME_AUTHORITY:{authority}")
        recipe_root = str(layer.get("recipe_hash216") or "")
        if not recipe_root:
            raise GraphicsHydrationError(f"P181_LAYER_RECIPE_IDENTITY_REQUIRED:{index}")
        seen_types.add(layer_type)
        roots.append(recipe_root)

    if not seen_types.intersection({"scene", "background", "midground", "sprite", "texture"}):
        raise GraphicsHydrationError("P181_NATIVE_VISUAL_LAYER_REQUIRED")

    manifest_root = hash216(
        {"frame_index": frame_index, "layer_recipe_roots": roots, "layer_types": sorted(seen_types)},
        domain=TRIAL_IDENTITY_DOMAIN,
    )
    return {
        "schema": "HHS_P181_NATIVE_FRAME_PROVENANCE_V1",
        "ok": True,
        "status": "HHS_MP4_ORIGINAL_FRAME_PASSTHROUGH_PROHIBITED",
        "frame_index": frame_index,
        "layer_types": sorted(seen_types),
        "frame_provenance_hash216": manifest_root,
    }


class GraphicsHydrationRuntime:
    """Serialized first-stage authority for Pass 181 hydration operations."""

    def __init__(self, artifact_root: Optional[Path] = None) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        configured = os.environ.get("HHS_GRAPHICS_HYDRATION_ROOT")
        self.artifact_root = Path(artifact_root or configured or repo_root / "artifacts" / "graphics_hydration")
        self.reference_manifest_root = self.artifact_root / "references"
        self.trial_root = self.artifact_root / "trials"
        self.constraint_root = self.artifact_root / "constraints"
        self._authority_lock = threading.RLock()
        for path in (self.reference_manifest_root, self.trial_root, self.constraint_root):
            path.mkdir(parents=True, exist_ok=True)

    def status(self) -> Dict[str, Any]:
        return {
            "schema": "HHS_P181_GRAPHICS_HYDRATION_STATUS_V1",
            "ok": True,
            "version": VERSION,
            "contract": CONTRACT,
            "authority": AUTHORITY,
            "single_commit_authority": True,
            "parallel_state_mutation": False,
            "reference_mp4_read_only": True,
            "reference_frame_passthrough": False,
            "threejs_role": "preview_enhancement_only",
            "ffmpeg_role": "media_transport_only",
            "promotion_stages": list(PROMOTION_STAGES),
            "residual_classes": list(RESIDUAL_CLASSES),
            "implementation_stage": "PASS_181_PHASE_1_AUTHORITY_AND_IDENTITY_CORE",
        }

    def ingest_reference(self, source_path: Path | str, *, logical_name: Optional[str] = None) -> Dict[str, Any]:
        """Content-address an MP4 without copying or mutating the source file."""

        with self._authority_lock:
            path = Path(source_path).expanduser().resolve(strict=True)
            before = path.stat()
            if not path.is_file():
                raise GraphicsHydrationError("P181_REFERENCE_NOT_REGULAR_FILE")
            if path.suffix.lower() != ".mp4":
                raise GraphicsHydrationError("P181_REFERENCE_FORMAT_REQUIRES_MP4")
            if before.st_size <= 0 or before.st_size > MAX_REFERENCE_BYTES:
                raise GraphicsHydrationError("P181_REFERENCE_SIZE_REJECTED")

            sha256 = _sha256_file(path)
            after = path.stat()
            if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns:
                raise GraphicsHydrationError("P181_REFERENCE_CHANGED_DURING_INGESTION")

            identity_payload = {
                "sha256": sha256,
                "size_bytes": before.st_size,
                "suffix": path.suffix.lower(),
                "logical_name": logical_name or path.name,
            }
            reference_id = hash216(identity_payload, domain=REFERENCE_IDENTITY_DOMAIN)
            identity = ReferenceIdentity(
                reference_id=reference_id,
                sha256=sha256,
                size_bytes=before.st_size,
                logical_name=str(logical_name or path.name),
                suffix=path.suffix.lower(),
                source_path=str(path),
                stat_mode=before.st_mode,
                stat_mtime_ns=before.st_mtime_ns,
            )
            manifest = {
                "schema": "HHS_P181_REFERENCE_MP4_IDENTITY_V1",
                "contract": CONTRACT,
                "authority": AUTHORITY,
                "read_only": True,
                "copied_into_hydration_store": False,
                "identity": identity.to_dict(),
            }
            manifest["receipt_hash72"] = hash72(manifest, domain=RECEIPT_DOMAIN)
            output = self.reference_manifest_root / _artifact_filename(reference_id)
            output.write_bytes(canonical_bytes(manifest))
            return {**manifest, "manifest_path": str(output)}

    def record_trial(
        self,
        *,
        reference_id: str,
        native_recipe: Mapping[str, Any],
        residuals: Iterable[Mapping[str, Any]],
        parent_trial_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        with self._authority_lock:
            residual_records = []
            for residual in residuals:
                residual_class = str(residual.get("class") or "")
                if residual_class not in RESIDUAL_CLASSES:
                    raise GraphicsHydrationError(f"P181_RESIDUAL_CLASS_REJECTED:{residual_class}")
                residual_records.append(stable(residual))

            payload = {
                "reference_id": str(reference_id),
                "native_recipe": stable(native_recipe),
                "residuals": residual_records,
                "parent_trial_id": parent_trial_id,
            }
            trial_id = hash216(payload, domain=TRIAL_IDENTITY_DOMAIN)
            record = {
                "schema": "HHS_P181_GRAPHICS_HYDRATION_TRIAL_V1",
                "trial_id": trial_id,
                "authority": AUTHORITY,
                "state": "OBSERVED",
                **payload,
            }
            record["receipt_hash72"] = hash72(record, domain=RECEIPT_DOMAIN)
            output = self.trial_root / _artifact_filename(trial_id)
            output.write_bytes(canonical_bytes(record))
            return {**record, "record_path": str(output)}

    def promote_constraint(self, candidate: Mapping[str, Any]) -> Dict[str, Any]:
        """Freeze only executable candidates with the complete validation chain."""

        with self._authority_lock:
            predicate = str(candidate.get("predicate") or "").strip()
            family = str(candidate.get("family") or "").strip()
            evidence = candidate.get("evidence")
            stages = candidate.get("stages")
            if not predicate or not family:
                raise GraphicsHydrationError("P181_CONSTRAINT_PREDICATE_AND_FAMILY_REQUIRED")
            if not isinstance(evidence, list) or not evidence:
                raise GraphicsHydrationError("P181_CONSTRAINT_EVIDENCE_REQUIRED")
            if not isinstance(stages, Mapping):
                raise GraphicsHydrationError("P181_CONSTRAINT_STAGE_MAP_REQUIRED")

            missing = [stage for stage in PROMOTION_STAGES if stages.get(stage) is not True]
            canonical_candidate = {
                "family": family,
                "predicate": predicate,
                "arithmetic": str(candidate.get("arithmetic") or "EXACT_INTEGER_OR_RATIONAL"),
                "severity": str(candidate.get("severity") or "HARD_REJECTION"),
                "scope": str(candidate.get("scope") or "ALL_AUTHORITATIVE_STORY_REEL_FRAMES"),
                "evidence": stable(evidence),
                "stages": {stage: stages.get(stage) is True for stage in PROMOTION_STAGES},
                "supersedes": candidate.get("supersedes"),
            }
            constraint_id = hash216(canonical_candidate, domain=CONSTRAINT_IDENTITY_DOMAIN)
            if missing:
                return {
                    "schema": "HHS_P181_GRAPHICS_CONSTRAINT_PROMOTION_V1",
                    "ok": False,
                    "status": "REJECT_GRAPHICS_CONSTRAINT_NOT_FULLY_VALIDATED",
                    "constraint_id": constraint_id,
                    "missing_stages": missing,
                }

            record = {
                "schema": "HHS_GRAPHICS_RUNTIME_CONSTRAINT_V1",
                "constraint_id": constraint_id,
                "contract": CONTRACT,
                "authority": AUTHORITY,
                "state": "FROZEN",
                **canonical_candidate,
            }
            record["constraint_hash72"] = hash72(record, domain=RECEIPT_DOMAIN)
            output = self.constraint_root / _artifact_filename(constraint_id)
            output.write_bytes(canonical_bytes(record))
            return {
                "schema": "HHS_P181_GRAPHICS_CONSTRAINT_PROMOTION_V1",
                "ok": True,
                "status": "HHS_GRAPHICS_RUNTIME_CONSTRAINT_PROMOTION_VERIFIED",
                "constraint": record,
                "record_path": str(output),
            }


def graphics_hydration_self_test() -> Dict[str, Any]:
    palette = reciprocal_palette_phases(5, 17, 41)
    fidelity = classify_fidelity(
        {
            "semantic_match": True,
            "perceptual_match": True,
            "decoded_frames_equal": False,
            "decoded_pcm_equal": False,
            "pts_equal": False,
            "encoder_state_available": False,
            "mp4_bytes_equal": False,
        }
    )
    return {
        "schema": "HHS_P181_GRAPHICS_HYDRATION_SELF_TEST_V1",
        "ok": palette["z"] == 41 and fidelity["strongest"] == "NATIVE_PERCEPTUAL_REPRODUCTION",
        "palette": palette,
        "fidelity": fidelity,
    }


GRAPHICS_HYDRATION = GraphicsHydrationRuntime()
