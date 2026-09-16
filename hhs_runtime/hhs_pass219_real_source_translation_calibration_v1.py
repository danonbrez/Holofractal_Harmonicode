"""Pass 219 real-source translation-invariance calibration v1.

Calibrates the merged translation-invariant multimodal candidate ingress against
immutable, permissively licensed upstream observations. Empirical scores are
exact-rational diagnostics only: they cannot change admission thresholds, mint
truth, or create VM81/Hash72/Hash216 authority.
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
from hhs_runtime.hhs_pass219_translation_invariant_multimodal_ingress_v1 import ALLOWED_LICENSES

VERSION = "HHS-P219-REAL-SOURCE-TRANSLATION-CALIBRATION-V1"
SCHEMA = "HHS-P219-REAL-SOURCE-TRANSLATION-CALIBRATION-REPORT-V1"
OBSERVATION_SCHEMA = "HHS-P219-REAL-SOURCE-CALIBRATION-OBSERVATION-V1"
MANIFEST_SCHEMA = "HHS-P219-REAL-SOURCE-TRANSLATION-CALIBRATION-MANIFEST-V1"
DEFAULT_THRESHOLDS: Mapping[str, Fraction] = {
    "TEXT_COSINE_DISPLAYED": Fraction(3, 4),
    "MULTILINGUAL_CLIP_SOFTMAX_DISPLAYED": Fraction(3, 4),
}
SEMANTIC_SCOPES = frozenset({"FAMILY", "SCENE_DETAIL", "IDENTITY"})
PROVIDERS = frozenset({"GITHUB", "HUGGING_FACE"})
_REVISION = re.compile(r"^[0-9a-f]{40}$")


class RealSourceCalibrationError(RuntimeError):
    pass


def _license(value: str) -> str:
    return str(value).strip().lower()


def _fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, Mapping):
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and len(value) == 2:
        return Fraction(int(value[0]), int(value[1]))
    raise RealSourceCalibrationError("P219_RSC_NONCANONICAL_FRACTION")


def _frac(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _required(value: Any, code: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise RealSourceCalibrationError(code)
    return text


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
        if _license(self.license_id) not in ALLOWED_LICENSES:
            raise RealSourceCalibrationError("P219_RSC_LICENSE_NOT_PRODUCTION_OPEN_SOURCE")
        if self.semantic_scope not in SEMANTIC_SCOPES:
            raise RealSourceCalibrationError("P219_RSC_SCOPE_INVALID")
        if not Fraction(0) <= self.displayed_score <= Fraction(1):
            raise RealSourceCalibrationError("P219_RSC_SCORE_OUT_OF_RANGE")
        if self.model_repository:
            if _REVISION.fullmatch(self.model_revision) is None:
                raise RealSourceCalibrationError("P219_RSC_MODEL_REVISION_NOT_IMMUTABLE")
        elif self.model_revision:
            raise RealSourceCalibrationError("P219_RSC_MODEL_REPOSITORY_REQUIRED")

    def to_record(self) -> dict[str, Any]:
        body = {
            "schema": OBSERVATION_SCHEMA,
            "case_id": self.case_id,
            "provider": self.provider,
            "repository": self.repository,
            "revision": self.revision,
            "evidence_path": self.evidence_path,
            "license_id": _license(self.license_id),
            "metric_family": self.metric_family,
            "semantic_scope": self.semantic_scope,
            "subject_id": self.subject_id,
            "candidate_id": self.candidate_id,
            "expected_positive": self.expected_positive,
            "displayed_score": _frac(self.displayed_score),
            "expected_family": self.expected_family,
            "observed_label": self.observed_label,
            "source_media_path": self.source_media_path,
            "language": self.language,
            "modality": self.modality,
            "excluded_claims": list(self.excluded_claims),
            "evidence_excerpt_sha256": sha256(self.evidence_excerpt.encode()).hexdigest(),
            "model_repository": self.model_repository,
            "model_revision": self.model_revision,
            "score_semantics": "ROUNDED_UPSTREAM_OBSERVATION_NOT_CANONICAL_PROOF",
            "candidate_only": True,
            "truth_promotion": False,
            "threshold_change_authorized": False,
        }
        body["observation_hash72"] = hash72_digest({"domain": OBSERVATION_SCHEMA}, body)
        return body


@dataclass(frozen=True)
class Confusion:
    true_positive: int = 0
    false_positive: int = 0
    true_negative: int = 0
    false_negative: int = 0

    def to_dict(self) -> dict[str, Any]:
        pden = self.true_positive + self.false_positive
        rden = self.true_positive + self.false_negative
        fden = self.false_positive + self.true_negative
        return {
            "true_positive": self.true_positive,
            "false_positive": self.false_positive,
            "true_negative": self.true_negative,
            "false_negative": self.false_negative,
            "precision": _frac(Fraction(self.true_positive, pden) if pden else Fraction(0)),
            "recall": _frac(Fraction(self.true_positive, rden) if rden else Fraction(0)),
            "false_positive_rate": _frac(Fraction(self.false_positive, fden) if fden else Fraction(0)),
        }


def load_calibration_manifest(path: str | Path) -> tuple[CalibrationObservation, ...]:
    payload = json.loads(Path(path).read_text("utf-8"))
    if payload.get("schema") != MANIFEST_SCHEMA:
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
    counts = [0, 0, 0, 0]  # tp, fp, tn, fn
    for item in rows:
        predicted = item.displayed_score >= threshold
        if item.expected_positive and predicted:
            counts[0] += 1
        elif not item.expected_positive and predicted:
            counts[1] += 1
        elif not item.expected_positive:
            counts[2] += 1
        else:
            counts[3] += 1
    return Confusion(*counts)


def _separability(rows: Sequence[CalibrationObservation]) -> dict[str, Any]:
    positives = [x.displayed_score for x in rows if x.expected_positive]
    negatives = [x.displayed_score for x in rows if not x.expected_positive]
    if not positives or not negatives:
        return {"exact_sample_separable": False, "lower_open": None, "upper_inclusive": None}
    lower, upper = max(negatives), min(positives)
    return {
        "exact_sample_separable": lower < upper,
        "lower_open": _frac(lower),
        "upper_inclusive": _frac(upper),
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
    for family, raw in (thresholds or {}).items():
        value = _fraction(raw)
        if not Fraction(0) <= value <= Fraction(1):
            raise RealSourceCalibrationError("P219_RSC_THRESHOLD_OUT_OF_RANGE")
        effective[str(family).upper()] = value

    grouped: dict[tuple[str, str], list[CalibrationObservation]] = {}
    for item in observations:
        grouped.setdefault((item.metric_family, item.semantic_scope), []).append(item)

    reports: list[dict[str, Any]] = []
    warm: list[dict[str, Any]] = []
    for (metric, scope), rows in sorted(grouped.items()):
        threshold = effective.get(metric)
        if threshold is None:
            reports.append({"metric_family": metric, "semantic_scope": scope, "classification": "HOLD_NO_REGISTERED_THRESHOLD", "sample_count": len(rows), "threshold_change_authorized": False})
            continue
        reports.append({
            "metric_family": metric,
            "semantic_scope": scope,
            "threshold": _frac(threshold),
            "sample_count": len(rows),
            "confusion": _confusion(rows, threshold).to_dict(),
            "empirical_separability_interval": _separability(rows),
            "threshold_change_authorized": False,
        })
        if scope == "FAMILY":
            for item in rows:
                if item.expected_positive and item.displayed_score >= threshold:
                    warm.append({
                        "case_id": item.case_id,
                        "expected_family": item.expected_family,
                        "metric_family": item.metric_family,
                        "observation_hash72": item.to_record()["observation_hash72"],
                        "excluded_claims": list(item.excluded_claims),
                        "candidate_only": True,
                        "requires_i29_or_equivalent_validation": True,
                        "canonical_hash216": None,
                    })

    body = {
        "schema": SCHEMA,
        "version": VERSION,
        "observation_count": len(observations),
        "observations": [x.to_record() for x in observations],
        "metric_reports": reports,
        "source_revisions": sorted({f"{x.provider}:{x.repository}@{x.revision}" for x in observations}),
        "model_revisions": sorted({f"HUGGING_FACE:{x.model_repository}@{x.model_revision}" for x in observations if x.model_repository}),
        "modifier_or_identity_boundaries": [
            {"case_id": x.case_id, "excluded_claims": list(x.excluded_claims), "semantic_scope": x.semantic_scope}
            for x in observations if x.excluded_claims
        ],
        "warm_hydration_candidates": warm,
        "warm_hydration_candidate_count": len(warm),
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


__all__ = ["CalibrationObservation", "Confusion", "DEFAULT_THRESHOLDS", "RealSourceCalibrationError", "SCHEMA", "VERSION", "calibrate_manifest", "calibrate_observations", "load_calibration_manifest"]
