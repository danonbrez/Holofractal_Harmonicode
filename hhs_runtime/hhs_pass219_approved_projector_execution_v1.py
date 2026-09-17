"""Pass 219 approved external projector execution v1.

Runs pinned open-source semantic projection models outside canonical VM81 authority
and emits the exact EXTERNAL_EVIDENCE_V1 row accepted by the persistent
acquisition job service.  Floating model output is empirical candidate evidence
only: non-finite values fail closed and similarity is serialized as a bounded
exact rational after explicit decimal quantization.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN
from hashlib import sha256
import argparse
import io
import json
import math
import os
import struct
import sys
from typing import Any, Mapping, Protocol, Sequence

from hhs_runtime.hhs_pass219_translation_invariant_multimodal_ingress_v1 import (
    OpenSourceRepositoryDescriptor,
)

VERSION = "HHS-P219-APPROVED-PROJECTOR-EXECUTION-V1"
EVIDENCE_SCHEMA = "HHS-P219-APPROVED-PROJECTOR-EVIDENCE-V1"
PROFILE_SCHEMA = "HHS-P219-APPROVED-PROJECTOR-PROFILES-V1"
QUANTIZATION_DENOMINATOR = 1_000_000_000
MAX_TEXT_CHARS = 20_000
MAX_SOURCE_BYTES = 24 * 1024 * 1024

TEXT_MODEL = OpenSourceRepositoryDescriptor(
    provider="HUGGING_FACE",
    repo_id="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    revision="79f2382ceacceacdf38563d7c5d16b9ff8d725d6",
    license_id="apache-2.0",
    repo_kind="MODEL",
    source_url="https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    modalities=("TEXT",),
).validated()

MULTILINGUAL_CLIP_TEXT_MODEL = OpenSourceRepositoryDescriptor(
    provider="HUGGING_FACE",
    repo_id="sentence-transformers/clip-ViT-B-32-multilingual-v1",
    revision="58edf8cada9e9f1df0dd8a8bc2ae891e7b1a983c",
    license_id="apache-2.0",
    repo_kind="MODEL",
    source_url="https://huggingface.co/sentence-transformers/clip-ViT-B-32-multilingual-v1",
    modalities=("TEXT",),
).validated()

# The original sentence-transformers/clip-ViT-B-32 model card does not declare
# an explicit license.  Do not silently promote that ambiguity into production
# admission.  The profile remains visible as a blocked calibration boundary
# until an explicitly licensed compatible image encoder is validated.
BLOCKED_CLIP_IMAGE_REVISION = "f41c38369690de9493a1c5e24e750e4adc1ac430"


class ApprovedProjectorExecutionError(RuntimeError):
    pass


class EmbeddingRuntime(Protocol):
    def encode_text(self, model: OpenSourceRepositoryDescriptor, text: str) -> Sequence[float]: ...
    def encode_image(self, model: OpenSourceRepositoryDescriptor, image_bytes: bytes) -> Sequence[float]: ...


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _vector_bytes(values: Sequence[float]) -> bytes:
    checked: list[float] = []
    for raw in values:
        value = float(raw)
        if not math.isfinite(value):
            raise ApprovedProjectorExecutionError("P219_APE_NONFINITE_VECTOR_REJECTED")
        checked.append(value)
    if not checked:
        raise ApprovedProjectorExecutionError("P219_APE_EMPTY_VECTOR_REJECTED")
    return struct.pack("<I", len(checked)) + b"".join(struct.pack("<f", value) for value in checked)


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        raise ApprovedProjectorExecutionError("P219_APE_VECTOR_DIMENSION_MISMATCH")
    numerator = 0.0
    left_norm = 0.0
    right_norm = 0.0
    for lraw, rraw in zip(left, right):
        left_value = float(lraw)
        right_value = float(rraw)
        if not math.isfinite(left_value) or not math.isfinite(right_value):
            raise ApprovedProjectorExecutionError("P219_APE_NONFINITE_VECTOR_REJECTED")
        numerator += left_value * right_value
        left_norm += left_value * left_value
        right_norm += right_value * right_value
    if left_norm <= 0.0 or right_norm <= 0.0:
        raise ApprovedProjectorExecutionError("P219_APE_ZERO_NORM_REJECTED")
    value = numerator / math.sqrt(left_norm * right_norm)
    if not math.isfinite(value):
        raise ApprovedProjectorExecutionError("P219_APE_NONFINITE_SIMILARITY_REJECTED")
    return value


def _bounded_rational(value: float) -> tuple[int, int, str]:
    if not math.isfinite(value):
        raise ApprovedProjectorExecutionError("P219_APE_NONFINITE_SIMILARITY_REJECTED")
    bounded = max(0.0, min(1.0, value))
    decimal_value = Decimal(format(bounded, ".12f"))
    quantum = Decimal(1) / Decimal(QUANTIZATION_DENOMINATOR)
    quantized = decimal_value.quantize(quantum, rounding=ROUND_HALF_EVEN)
    numerator = int((quantized * QUANTIZATION_DENOMINATOR).to_integral_exact())
    common = math.gcd(numerator, QUANTIZATION_DENOMINATOR)
    return numerator // common, QUANTIZATION_DENOMINATOR // common, format(quantized, "f")


def _clean_text(source: bytes) -> str:
    try:
        text = source.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ApprovedProjectorExecutionError("P219_APE_UTF8_SOURCE_REQUIRED") from exc
    normalized = " ".join(text.replace("\x00", " ").split())
    if not normalized:
        raise ApprovedProjectorExecutionError("P219_APE_EMPTY_TEXT_SOURCE")
    return normalized[:MAX_TEXT_CHARS]


@dataclass(frozen=True)
class ProjectionExecutionRequest:
    profile_id: str
    source_bytes: bytes
    source_sha256: str
    source_language: str
    source_modality: str
    pivot_text: str
    pivot_language: str = "en"
    semantic_labels: tuple[str, ...] = ()
    translation_chain: tuple[str, ...] = ()

    def validated(self) -> "ProjectionExecutionRequest":
        profile = str(self.profile_id).strip().upper()
        source = bytes(self.source_bytes)
        if not source or len(source) > MAX_SOURCE_BYTES:
            raise ApprovedProjectorExecutionError("P219_APE_SOURCE_BOUND")
        expected = str(self.source_sha256).strip().lower()
        if len(expected) != 64 or any(ch not in "0123456789abcdef" for ch in expected):
            raise ApprovedProjectorExecutionError("P219_APE_SOURCE_SHA256_INVALID")
        if sha256(source).hexdigest() != expected:
            raise ApprovedProjectorExecutionError("P219_APE_SOURCE_SHA256_MISMATCH")
        pivot = " ".join(str(self.pivot_text).split())
        if not pivot:
            raise ApprovedProjectorExecutionError("P219_APE_PIVOT_REQUIRED")
        source_language = str(self.source_language).strip().casefold()
        pivot_language = str(self.pivot_language).strip().casefold()
        source_modality = str(self.source_modality).strip().upper()
        if not source_language or not pivot_language or not source_modality:
            raise ApprovedProjectorExecutionError("P219_APE_METADATA_REQUIRED")
        labels = tuple(dict.fromkeys(str(x).strip() for x in self.semantic_labels if str(x).strip()))
        chain = tuple(dict.fromkeys(str(x).strip() for x in self.translation_chain if str(x).strip()))
        return ProjectionExecutionRequest(
            profile_id=profile,
            source_bytes=source,
            source_sha256=expected,
            source_language=source_language,
            source_modality=source_modality,
            pivot_text=pivot,
            pivot_language=pivot_language,
            semantic_labels=labels,
            translation_chain=chain,
        )


class SentenceTransformersRuntime:
    """Real model runtime; imports heavy ML dependencies only when executed."""

    def __init__(self, *, device: str | None = None) -> None:
        self.device = device or os.environ.get("HHS_P219_PROJECTOR_DEVICE") or None
        self._models: dict[tuple[str, str], Any] = {}

    def _model(self, descriptor: OpenSourceRepositoryDescriptor) -> Any:
        key = (descriptor.repo_id, descriptor.revision)
        if key not in self._models:
            try:
                from sentence_transformers import SentenceTransformer
            except Exception as exc:
                raise ApprovedProjectorExecutionError("P219_APE_SENTENCE_TRANSFORMERS_REQUIRED") from exc
            kwargs: dict[str, Any] = {
                "revision": descriptor.revision,
                "trust_remote_code": False,
                "model_kwargs": {"use_safetensors": True},
            }
            if self.device:
                kwargs["device"] = self.device
            self._models[key] = SentenceTransformer(descriptor.repo_id, **kwargs)
        return self._models[key]

    def encode_text(self, model: OpenSourceRepositoryDescriptor, text: str) -> Sequence[float]:
        encoded = self._model(model).encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]
        return [float(value) for value in encoded.tolist()]

    def encode_image(self, model: OpenSourceRepositoryDescriptor, image_bytes: bytes) -> Sequence[float]:
        try:
            from PIL import Image
        except Exception as exc:
            raise ApprovedProjectorExecutionError("P219_APE_PIL_REQUIRED") from exc
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.load()
            encoded = self._model(model).encode(
                [image.convert("RGB")],
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )[0]
        return [float(value) for value in encoded.tolist()]


def execution_profiles() -> dict[str, Any]:
    return {
        "schema": PROFILE_SCHEMA,
        "version": VERSION,
        "profiles": [
            {
                "profile_id": "MULTILINGUAL_MPNET_TEXT_V1",
                "production_approved": True,
                "source_modalities": ["TEXT", "MARKDOWN", "JSON", "CSV", "CODE"],
                "primary_model": TEXT_MODEL.receipt_body(),
                "model_execution_external_to_canonical_kernel": True,
                "trust_remote_code": False,
                "candidate_only": True,
            },
            {
                "profile_id": "MULTILINGUAL_CLIP_IMAGE_TEXT_V1",
                "production_approved": False,
                "source_modalities": ["IMAGE"],
                "primary_text_model": MULTILINGUAL_CLIP_TEXT_MODEL.receipt_body(),
                "blocked_image_model_repo_id": "sentence-transformers/clip-ViT-B-32",
                "blocked_image_model_revision": BLOCKED_CLIP_IMAGE_REVISION,
                "blocked_reason": "IMAGE_ENCODER_MODEL_CARD_LICENSE_NOT_EXPLICIT; REQUIRE_EXPLICITLY_LICENSED_COMPATIBILITY_PROOF_BEFORE_PRODUCTION_ADMISSION",
                "candidate_only": True,
            },
        ],
        "canonical_authority_minted": False,
    }


def execute_projection(
    request: ProjectionExecutionRequest,
    runtime: EmbeddingRuntime,
) -> dict[str, Any]:
    item = request.validated()
    if item.profile_id != "MULTILINGUAL_MPNET_TEXT_V1":
        if item.profile_id == "MULTILINGUAL_CLIP_IMAGE_TEXT_V1":
            raise ApprovedProjectorExecutionError("P219_APE_PROFILE_NOT_PRODUCTION_APPROVED")
        raise ApprovedProjectorExecutionError("P219_APE_PROFILE_UNKNOWN")
    if item.source_modality not in {"TEXT", "MARKDOWN", "JSON", "CSV", "CODE"}:
        raise ApprovedProjectorExecutionError("P219_APE_TEXT_PROFILE_MODALITY_MISMATCH")

    source_text = _clean_text(item.source_bytes)
    source_vector = runtime.encode_text(TEXT_MODEL, source_text)
    pivot_vector = runtime.encode_text(TEXT_MODEL, item.pivot_text)
    cosine = _cosine(source_vector, pivot_vector)
    numerator, denominator, quantized = _bounded_rational(cosine)
    source_vector_bytes = _vector_bytes(source_vector)
    pivot_vector_bytes = _vector_bytes(pivot_vector)
    vector_identity_bytes = source_vector_bytes + pivot_vector_bytes

    execution_record = {
        "schema": EVIDENCE_SCHEMA,
        "version": VERSION,
        "profile_id": item.profile_id,
        "source_sha256": item.source_sha256,
        "source_modality": item.source_modality,
        "source_language": item.source_language,
        "pivot_language": item.pivot_language,
        "primary_model": TEXT_MODEL.receipt_body(),
        "source_vector_sha256": sha256(source_vector_bytes).hexdigest(),
        "pivot_vector_sha256": sha256(pivot_vector_bytes).hexdigest(),
        "vector_dimension": len(source_vector),
        "cosine_float_observation": format(cosine, ".12f"),
        "bounded_similarity_decimal": quantized,
        "quantization_denominator": QUANTIZATION_DENOMINATOR,
        "trust_remote_code": False,
        "safetensors_required": True,
        "external_model_execution": True,
        "candidate_only": True,
        "canonical_authority_minted": False,
    }
    output_bytes = _canonical_bytes(execution_record)
    return {
        "model_repository": TEXT_MODEL.receipt_body(),
        "pivot_text": item.pivot_text,
        "source_language": item.source_language,
        "pivot_language": item.pivot_language,
        "source_modality": item.source_modality,
        "output_b64": b64encode(output_bytes).decode("ascii"),
        "vector_identity_b64": b64encode(vector_identity_bytes).decode("ascii"),
        "similarity": {"numerator": numerator, "denominator": denominator},
        "semantic_labels": list(item.semantic_labels),
        "translation_chain": list(item.translation_chain),
        "execution_record_sha256": sha256(output_bytes).hexdigest(),
        "projector_profile_id": item.profile_id,
        "projector_version": VERSION,
        "projector_id": "EXTERNAL_EVIDENCE_V1",
        "candidate_only": True,
    }


def _request_from_json(raw: Mapping[str, Any]) -> ProjectionExecutionRequest:
    try:
        source = b64decode(str(raw.get("source_b64") or ""), validate=True)
    except Exception as exc:
        raise ApprovedProjectorExecutionError("P219_APE_SOURCE_B64_INVALID") from exc
    return ProjectionExecutionRequest(
        profile_id=str(raw.get("profile_id") or ""),
        source_bytes=source,
        source_sha256=str(raw.get("source_sha256") or ""),
        source_language=str(raw.get("source_language") or ""),
        source_modality=str(raw.get("source_modality") or ""),
        pivot_text=str(raw.get("pivot_text") or ""),
        pivot_language=str(raw.get("pivot_language") or "en"),
        semantic_labels=tuple(str(x) for x in raw.get("semantic_labels", ()) if str(x).strip()),
        translation_chain=tuple(str(x) for x in raw.get("translation_chain", ()) if str(x).strip()),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HHS Pass 219 approved external projector")
    parser.add_argument("--profiles", action="store_true", help="print approved/blocked projector profiles")
    parser.add_argument("--input", help="JSON request path; '-' reads stdin")
    parser.add_argument("--device", default=None)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.profiles:
            print(json.dumps(execution_profiles(), indent=2, sort_keys=True))
            return 0
        if not args.input:
            raise ApprovedProjectorExecutionError("P219_APE_INPUT_REQUIRED")
        raw_text = sys.stdin.read() if args.input == "-" else open(args.input, "r", encoding="utf-8").read()
        raw = json.loads(raw_text)
        if not isinstance(raw, Mapping):
            raise ApprovedProjectorExecutionError("P219_APE_INPUT_OBJECT_REQUIRED")
        result = execute_projection(_request_from_json(raw), SentenceTransformersRuntime(device=args.device))
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"schema": "HHS-P219-APPROVED-PROJECTOR-ERROR-V1", "classification": str(exc) or type(exc).__name__, "candidate_only": True}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ApprovedProjectorExecutionError",
    "EmbeddingRuntime",
    "ProjectionExecutionRequest",
    "SentenceTransformersRuntime",
    "TEXT_MODEL",
    "VERSION",
    "execute_projection",
    "execution_profiles",
    "main",
]
