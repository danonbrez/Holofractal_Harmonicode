from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass219_real_source_translation_calibration_v1 import (
    CalibrationObservation,
    RealSourceCalibrationError,
    calibrate_manifest,
    calibrate_observations,
    load_calibration_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "pass219" / "translation_invariant_real_source_calibration_v1.json"


def _report(metric: str, scope: str, result: dict):
    return next(
        item
        for item in result["metric_reports"]
        if item["metric_family"] == metric and item["semantic_scope"] == scope
    )


def test_manifest_is_revision_pinned_and_permissively_licensed():
    observations = load_calibration_manifest(MANIFEST)
    assert len(observations) == 10
    assert all(len(item.revision) == 40 for item in observations)
    assert all(item.license_id == "Apache-2.0" for item in observations)
    clip_rows = [item for item in observations if item.model_repository]
    assert clip_rows
    assert all(len(item.model_revision) == 40 for item in clip_rows)
    assert {item.provider for item in observations} == {"GITHUB"}


def test_text_readme_calibration_exposes_conservative_three_quarter_threshold():
    result = calibrate_manifest(MANIFEST)
    report = _report("TEXT_COSINE_DISPLAYED", "FAMILY", result)
    assert report["threshold"] == {"numerator": 3, "denominator": 4}
    assert report["confusion"]["true_positive"] == 0
    assert report["confusion"]["false_positive"] == 0
    assert report["confusion"]["true_negative"] == 2
    assert report["confusion"]["false_negative"] == 1
    assert report["confusion"]["recall"] == {"numerator": 0, "denominator": 1}
    interval = report["empirical_separability_interval"]
    assert interval["exact_sample_separable"] is True
    assert interval["lower_open"] == {"numerator": 1411, "denominator": 10000}
    assert interval["upper_inclusive"] == {"numerator": 333, "denominator": 500}
    assert result["threshold_change_authorized"] is False


def test_multilingual_clip_family_closure_has_no_false_matches_at_current_threshold():
    result = calibrate_manifest(MANIFEST)
    report = _report("MULTILINGUAL_CLIP_SOFTMAX_DISPLAYED", "FAMILY", result)
    assert report["confusion"]["true_positive"] == 3
    assert report["confusion"]["false_positive"] == 0
    assert report["confusion"]["true_negative"] == 2
    assert report["confusion"]["false_negative"] == 0
    assert report["confusion"]["precision"] == {"numerator": 1, "denominator": 1}
    assert report["confusion"]["recall"] == {"numerator": 1, "denominator": 1}


def test_scene_detail_is_calibrated_separately_from_family_semantics():
    result = calibrate_manifest(MANIFEST)
    report = _report("MULTILINGUAL_CLIP_SOFTMAX_DISPLAYED", "SCENE_DETAIL", result)
    assert report["confusion"]["true_positive"] == 0
    assert report["confusion"]["true_negative"] == 1
    assert report["confusion"]["false_negative"] == 1
    boundaries = result["modifier_or_identity_boundaries"]
    assert boundaries == [
        {
            "case_id": "st-clip-day-night-zh-negative",
            "excluded_claims": ["night"],
            "semantic_scope": "SCENE_DETAIL",
        }
    ]


def test_warm_hydration_candidates_only_include_threshold_closed_family_observations():
    result = calibrate_manifest(MANIFEST)
    candidates = result["warm_hydration_candidates"]
    assert len(candidates) == 3
    assert {item["expected_family"] for item in candidates} == {"PARIS_EIFFEL", "DOG", "CAT"}
    assert all(item["candidate_only"] is True for item in candidates)
    assert all(item["requires_i29_or_equivalent_validation"] is True for item in candidates)
    assert all(item["canonical_hash216"] is None for item in candidates)


def test_calibration_is_deterministic_and_has_zero_canonical_authority():
    first = calibrate_manifest(MANIFEST)
    second = calibrate_manifest(MANIFEST)
    assert first["calibration_hash72"] == second["calibration_hash72"]
    assert first["network_fetch_performed"] is False
    assert first["canonical_learning_commit_invoked"] is False
    assert first["vm81_mutation_invoked"] is False
    assert first["canonical_hash72_minted"] is False
    assert first["canonical_hash216_minted"] is False
    assert first["truth_promotion"] is False
    assert first["action_authority_minted"] is False
    assert first["permanent_prune_authorized"] is False


def test_noncommercial_license_fails_closed():
    with pytest.raises(RealSourceCalibrationError, match="P219_RSC_LICENSE_NOT_PRODUCTION_OPEN_SOURCE"):
        CalibrationObservation.from_mapping(
            {
                "case_id": "bad-license",
                "provider": "HUGGING_FACE",
                "repository": "example/model",
                "revision": "a" * 40,
                "evidence_path": "README.md",
                "license_id": "CC-BY-NC-4.0",
                "metric_family": "TEXT_COSINE_DISPLAYED",
                "semantic_scope": "FAMILY",
                "subject_id": "a",
                "candidate_id": "b",
                "expected_positive": True,
                "displayed_score": "9/10",
                "expected_family": "X",
            }
        )


def test_mutable_revision_fails_closed():
    with pytest.raises(RealSourceCalibrationError, match="P219_RSC_REVISION_NOT_IMMUTABLE"):
        CalibrationObservation.from_mapping(
            {
                "case_id": "mutable",
                "provider": "GITHUB",
                "repository": "example/repo",
                "revision": "main",
                "evidence_path": "README.md",
                "license_id": "MIT",
                "metric_family": "TEXT_COSINE_DISPLAYED",
                "semantic_scope": "FAMILY",
                "subject_id": "a",
                "candidate_id": "b",
                "expected_positive": False,
                "displayed_score": "1/10",
                "expected_family": "X",
            }
        )


def test_threshold_override_is_diagnostic_only():
    observations = load_calibration_manifest(MANIFEST)
    result = calibrate_observations(
        observations,
        thresholds={"TEXT_COSINE_DISPLAYED": Fraction(3, 5)},
    )
    report = _report("TEXT_COSINE_DISPLAYED", "FAMILY", result)
    assert report["threshold"] == {"numerator": 3, "denominator": 5}
    assert report["confusion"]["true_positive"] == 1
    assert report["confusion"]["false_positive"] == 0
    assert report["threshold_change_authorized"] is False
    assert result["threshold_change_authorized"] is False
