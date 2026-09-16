"""Pass 219 real-source translation-invariance calibration v1.

This module calibrates the already-merged translation-invariant multimodal
candidate ingress against immutable, permissively licensed upstream observations.
It is deliberately noncanonical: empirical scores may diagnose thresholds and
semantic granularity, but they cannot change admission thresholds, mint truth,
or create VM81/Hash72/Hash216 authority.

The calibration distinguishes three semantic scopes:

    FAMILY       coarse entity/concept family closure
    SCENE_DETAIL modifier/attribute preservation
    IDENTITY     exact identity preservation

That distinction prevents a high-confidence coarse correspondence (for example,
"Paris" for an Eiffel Tower image) from laundering an unsupported modifier or
identity claim into canonical state.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence
import json
import re

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_pass219_translation_invariant_multimodal_ingress_v1 import (
    PERMISSIVE_LICENSES,
    normalize_license,
)

VERSION = "HHS-P219-REAL-SOURCE-TRANSLATION-CALIBRATION-V1"
SCHEMA = "HHS-P219-REAL-SOURCE-TRANSLATION-CALIBRATION-REPORT-V1"
OBSERVATION_SCHEMA = "HHS-P219-REAL-SOURCE-CALIBRATION-OBSERVATION-V1"
DEFAULT_THRESHOLDS: Mapping[str, Fraction] = {
    "TEXT_COSINE_DISPLAYED": Fraction(3, 4),
    "MULTILINGUAL_CLIP_SOFTMAX_DISPLAYED": Fraction(3, 4),
}
SEMANTIC_SCOPES = frozenset({"FAMILY", "SCENE_DETAIL", "IDENTITY"})
PROVIDERS = frozenset({"GITHUB", "HUGGING_FACE"})
_REVISION = re.compile(r"^[0-9a-f]{7,64}$")


class RealSourceCalibrationError(RuntimeError):
    """Fail-closed validation error for the calibration surface."""


def _fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) == 2:
        return Fraction(int(value[0]), int(value[1]))
    if isinstance(value, Mapping):
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    raise RealSourceCalibrationError("P219_RSC_NONCANONICAL_FRACTION")


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _required(value: Any, code: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise RealSourceCalibrationError(code)
    return text


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    ).encode("utf-8")


@dataclass(frozen=True)
class CalibrationObservation:
    case_id: str
    provider: str
    repository: str
    revision: str
    evidence_path: str
    license_id: str
    metric_family: str
    semantic_scope: str
    subject_id: str
    candidate_id: str
    expected_positive: bool
    displayed_score: Fraction
    expected_family: str
    observed_label: str = ""
    source_media_path: str = ""
    language: str = "und"
    modality: str = "TEXT"
    excluded_claims: tuple[str, ...] = ()
    evidence_excerpt: str = ""
    model_repository: str = ""
    model_revision: str = ""

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "CalibrationObservation":
        item = cls(
            case_id=_required(raw.get("case_id"), "P219_RSC_CASE_ID_REQUIRED"),
            provider=_required(raw.get("provider"), "P219_RSC_PROVIDER_REQUIRED").upper(),
            repository=_required(raw.get("repository"), "P219_RSC_REPOSITORY_REQUIRED"),
            revision=_required(raw.get("revision"), "P219_RSC_REVISION_REQUIRED").lower(),
            evidence_path=_required(raw.get("evidence_path"), "P219_RSC_EVIDENCE_PATH_REQUIRED"),
            license_id=_required(raw.get("license_id"), "P219_RSC_LICENSE_REQUIRED"),
            metric_family=_required(raw.get("metric_family"), "P219_RSC_METRIC_REQUIRED").upper(),
            semantic_scope=_required(raw.get("semantic_scope"), "P219_RSC_SCOPE_REQUIRED").upper(),
            subject_id=_required(raw.get("subject_id"), "P219_RSC_SUBJECT_REQUIRED"),
            candidate_id=_required(raw.get("candidate_id"), "P219_RSC_CANDIDATE_REQUIRED"),
            expected_positive=bool(raw.get("expected_positive")),
            displayed_score=_fraction(raw.get("displayed_score")),
            expected_family=_required(raw.get("expected_family"), "P219_RSC_EXPECTED_FAMILY_REQUIRED").upper(),
            observed_label=str(raw.get("observed_label") or "").strip(),
            source_media_path=str(raw.get("source_media_path") or "").strip(),
            language=str(raw.get("language") or "und").strip().lower(),
            modality=str(raw.get("modality") or "TEXT").strip().upper(),
            excluded_claims=tuple(str(x).strip() for x in raw.get("excluded_claims", ()) if str(x).strip()),
            evidence_excerpt=str(raw.get("evidence_excerpt") or "").strip(),
            model_repository=str(raw.get("model_repository") or "").strip(),
            model_revision=str(raw.get("model_revision") or "").strip().lower(),
        )
        item.validate()
        return item

    def validate(self) -> None:
        if self.provider not in PROVIDERS:
            raise RealSourceCalibrationError("P219_RSC_PROVIDER_INVALID")
        if _REVISION.fullmatch(self.revision) is None:
            raise RealSourceCalibrationError("P219_RSC_REVISION_NOT_IMMUTABLE")
        if normalize_license(self.license_id) not in PERMISSIVE_LICENSES:
            raise RealSourceCalibrationError("P219_RSC_LICENSE_NOT_PRODUCTION_OPEN_SOURCE")
        if self.semantic_scope not in SEMANTIC_SCOPES:
            raise RealSourceCalibrationError("P219_RSC_SCOPE_INVALID")
        if not Fraction(0, 1) <= self.displayed_score <= Fraction(1, 1):
            raise RealSourceCalibrationError("P219_RSC_SCORE_OUT_OF_RANGE")
        if self.model_repository:
            if not self.model_revision or _REVISION.fullmatch(self.model_revision) is None:
                raise RealSourceCalibrationError("P219_RSC_MODEL_REVISION_NOT_IMMUTABLE")
        elif self.model_revision:
            raise RealSourceCalibrationError("P219_RSC_MODEL_REPOSITORY_REQUIRED")

    @property
    def evidence_excerpt_sha256(self) -> str:
        return sha256(self.evidence_excerpt.encode("utf-8")).hexdigest()

    def to_record(self) -> dict[str, Any]:
        body = {
            "schema": OBSERVATION_SCHEMA,
            "case_id": self.case_id,
            "provider": self.provider,
            "repository": self.repository,
            "revision": self.revision,
            "evidence_path": self.evidence_path,
            "license_id": normalize_license(self.license_id),
            "metric_family": self.metric_family,
            "semantic_scope": self.semantic_scope,
            "subject_id": self.subject_id,
            "candidate_id": self.candidate_id,
            "expected_positive": self.expected_positive,
            "displayed_score": _fraction_record(self.displayed_score),
            "expected_family": self.expected_family,
            "observed_label": self.observed_label,
            "source_media_path": self.source_media_path,
            "language": self.language,
            "modality": self.modality,
            "excluded_claims": list(self.excluded_claims),
            "evidence_excerpt_sha256": self.evidence_excerpt_sha256,
            "model_repository": self.model_repository,
            "model_revision": self.model_revision,
            "score_semantics": "ROUNDED_UPSTREAM_OBSERVATION_NOT_CANONICAL_PROOF",
            "candidate_only": True,
            "truth_promotion": False,
            "threshold_change_authorized": False,
        }
        body["observation_hash72"] = hash72_digest(
            {"domain": OBSERVATION_SCHEMA}, body
        )
        return body


@dataclass(frozen=True)
class Confusion:
    true_positive: int = 0
    false_positive: int = 0
    true_negative: int = 0
    false_negative: int = 0

    @property
    def precision(self) -> Fraction:
        denominator = self.true_positive + self.false_positive
        return Fraction(self.true_positive, denominator) if denominator else Fraction(0, 1)

    @property
    def recall(self) -> Fraction:
        denominator = self.true_positive + self.false_negative
        return Fraction(self.true_positive, denominator) if denominator else Fraction(0, 1)

    @property
    def false_positive_rate(self) -> Fraction:
        denominator = self.false_positive + self.true_negative
        return Fraction(self.false_positive, denominator) if denominator else Fraction(0, 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "true_positive": self.true_positive,
            "false_positive": self.false_positive,
            "true_negative": self.true_negative,
            "false_negative": self.false_negative,
            "precision": _fraction_record(self.precision),
            "recall": _fraction_record(self.recall),
            "false_positive_rate": _fraction_record(self.false_positive_rate),
        }


def load_calibration_manifest(path: str | Path) -> tuple[CalibrationObservation, ...]:
    payload = json.loads(Path(path).read_text("utf-8"))
    if payload.get("schema") != "HHS-P219-REAL-SOURCE-TRANSLATION-CALIBRATION-MANIFEST-V1":
        raise RealSourceCalibrationError("P219_RSC_MANIFEST_SCHEMA_INVALID")
    rows = payload.get("observations")
    if not isinstance(rows, list) or not rows:
        raise RealSourceCalibrationError("P219_RSC_MANIFEST_EMPTY")
    observations = tuple(CalibrationObservation.from_mapping(row) for row in rows)
    ids = [item.case_id for item in observations]
    if len(ids) != len(set(ids)):
        raise RealSourceCalibrationError("P219_RSC_DUPLICATE_CASE_ID")
    return observations


def _confusion(rows: Sequence[CalibrationObservation], threshold: Fraction) -> Confusion:
    tp = fp = tn = fn = 0
    for item in rows:
        predicted = item.displayed_score >= threshold
        if item.expected_positive and predicted:
            tp += 1
        elif not item.expected_positive and predicted:
            fp += 1
        elif not item.expected_positive and not predicted:
            tn += 1
        else:
            fn += 1
    return Confusion(tp, fp, tn, fn)


def _separability(rows: Sequence[CalibrationObservation]) -> dict[str, Any]:
    positives = [item.displayed_score for item in rows if item.expected_positive]
    negatives = [item.displayed_score for item in rows if not item.expected_positive]
    if not positives or not negatives:
        return {
            "exact_sample_separable": False,
            "lower_open": None,
            "upper_inclusive": None,
            "reason": "POSITIVE_AND_NEGATIVE_SAMPLES_REQUIRED",
        }
    lower = max(negatives)
    upper = min(positives)
    return {
        "exact_sample_separable": lower < upper,
        "lower_open": _fraction_record(lower),
        "upper_inclusive": _fraction_record(upper),
        "semantics": "SAMPLE_ONLY_THRESHOLD_INTERVAL_NOT_PRODUCTION_AUTHORITY",
    }


def calibrate_observations(
    observations: Sequence[CalibrationObservation],
    *,
    thresholds: Mapping[str, Fraction] | None = None,
) -> dict[str, Any]:
    if not observations:
        raise RealSourceCalibrationError("P219_RSC_OBSERVATIONS_REQUIRED")
    for item in observations:
        item.validate()
    effective = dict(DEFAULT_THRESHOLDS)
    if thresholds:
        for family, threshold in thresholds.items():
            value = _fraction(threshold)
            if not Fraction(0, 1) <= value <= Fraction(1, 1):
                raise RealSourceCalibrationError("P219_RSC_THRESHOLD_OUT_OF_RANGE")
            effective[str(family).upper()] = value

    grouped: dict[tuple[str, str], list[CalibrationObservation]] = {}
    for item in observations:
        grouped.setdefault((item.metric_family, item.semantic_scope), []).append(item)

    metric_reports: list[dict[str, Any]] = []
    warm_candidates: list[dict[str, Any]] = []
    for (metric_family, scope), rows in sorted(grouped.items()):
        threshold = effective.get(metric_family)
        if threshold is None:
            metric_reports.append({
                "metric_family": metric_family,
                "semantic_scope": scope,
                "classification": "HOLD_NO_REGISTERED_THRESHOLD",
                "sample_count": len(rows),
                "threshold_change_authorized": False,
            })
            continue
        confusion = _confusion(rows, threshold)
        report = {
            "metric_family": metric_family,
            "semantic_scope": scope,
            "threshold": _fraction_record(threshold),
            "sample_count": len(rows),
            "confusion": confusion.to_dict(),
            "empirical_separability_interval": _separability(rows),
            "threshold_change_authorized": False,
        }
        metric_reports.append(report)
        if scope == "FAMILY":
            for item in rows:
                if item.expected_positive and item.displayed_score >= threshold:
                    warm_candidates.append({
                        "case_id": item.case_id,
                        "expected_family": item.expected_family,
                        "metric_family": item.metric_family,
                        "observation_hash72": item.to_record()["observation_hash72"],
                        "excluded_claims": list(item.excluded_claims),
                        "candidate_only": True,
                        "requires_i29_or_equivalent_validation": True,
                        "canonical_hash216": None,
                    })

    source_revisions = sorted({
        f"{item.provider}:{item.repository}@{item.revision}" for item in observations
    })
    model_revisions = sorted({
        f"HUGGING_FACE:{item.model_repository}@{item.model_revision}"
        for item in observations if item.model_repository
    })
    modifier_conflicts = [
        {
            "case_id": item.case_id,
            "excluded_claims": list(item.excluded_claims),
            "semantic_scope": item.semantic_scope,
        }
        for item in observations if item.excluded_claims
    ]
    body = {
        "schema": SCHEMA,
        "version": VERSION,
        "observation_count": len(observations),
        "observations": [item.to_record() for item in observations],
        "metric_reports": metric_reports,
        "source_revisions": source_revisions,
        "model_revisions": model_revisions,
        "modifier_or_identity_boundaries": modifier_conflicts,
        "warm_hydration_candidates": warm_candidates,
        "warm_hydration_candidate_count": len(warm_candidates),
        "calibration_semantics": "EMPIRICAL_CANDIDATE_DIAGNOSTIC_NOT_CANONICAL_THRESHOLD_AUTHORITY",
        "threshold_change_authorized": False,
        "network_fetch_performed": False,
        "canonical_learning_commit_invoked": False,
        "vm81_mutation_invoked": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "permanent_prune_authorized": False,
    }
    body["calibration_hash72"] = hash72_digest({"domain": SCHEMA}, body)
    return body


def calibrate_manifest(path: str | Path) -> dict[str, Any]:
    return calibrate_observations(load_calibration_manifest(path))


__all__ = [
    "CalibrationObservation",
    "Confusion",
    "DEFAULT_THRESHOLDS",
    "RealSourceCalibrationError",
    "SCHEMA",
    "VERSION",
    "calibrate_manifest",
    "calibrate_observations",
    "load_calibration_manifest",
]
