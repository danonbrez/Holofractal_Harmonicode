from __future__ import annotations

import importlib

import pytest

from hhs_backend.runtime.hhs_pass214_iteration5_callable_corpus_v1 import (
    FAMILY_SPECS,
    STATUS_READY,
    _reject_float,
    build_iteration5_report,
    evaluate_pair,
)


@pytest.fixture(scope="module")
def corpus_report() -> dict[str, object]:
    return build_iteration5_report()


EXPECTED_FAMILIES = {
    "vector_cache",
    "wrapper_duplication",
    "numeric_lookup",
    "serialization_import",
    "coprime_lookup",
}


def test_manifest_covers_exact_five_family_boundary() -> None:
    assert {spec["family"] for spec in FAMILY_SPECS} == EXPECTED_FAMILIES
    assert len(FAMILY_SPECS) == 5


def test_every_pair_is_repository_callable_and_smaller() -> None:
    runtime = importlib.import_module(
        "hhs_backend.runtime.hhs_pass214_iteration5_callable_corpus_v1"
    )
    for spec in FAMILY_SPECS:
        assert spec["source_id"] in runtime.VIRTUAL_MODULE_SOURCES
        assert spec["target_id"] in runtime.VIRTUAL_MODULE_SOURCES
        result = evaluate_pair(spec)
        assert result["exact_result_parity"] is True
        assert result["positive_gain"] is True
        assert result["source_bytes"] > result["target_bytes"]


def test_three_consecutive_full_corpus_runs_are_exact_and_positive(
    corpus_report: dict[str, object],
) -> None:
    assert corpus_report["status"] == STATUS_READY
    assert corpus_report["completed_consecutive_runs"] == 3
    assert corpus_report["consecutive_exact_positive_gain"] is True
    assert all(run["exact_parity"] for run in corpus_report["runs"])
    assert all(run["positive_gain"] for run in corpus_report["runs"])
    assert all(len(run["pair_results"]) == 5 for run in corpus_report["runs"])


def test_non_promoting_policy_boundary_is_closed(
    corpus_report: dict[str, object],
) -> None:
    assert corpus_report["policy"] == {
        "migration_active": False,
        "authority_promoted": False,
        "terminal_roots_minted": False,
        "pass215_authorized": False,
        "live_pass213_surface_required_for_promotion": True,
    }


def test_cross_family_pair_is_rejected_by_exact_parity() -> None:
    mismatched = dict(FAMILY_SPECS[0])
    mismatched["target_id"] = FAMILY_SPECS[-1]["target_id"]
    result = evaluate_pair(mismatched)
    assert result["exact_result_parity"] is False


def test_float_output_rejection() -> None:
    with pytest.raises(TypeError, match="floating-point output is forbidden"):
        _reject_float({"bad": [1, 2.0, 3]})


def test_manifest_module_matches_runtime() -> None:
    module = importlib.import_module("tools.pass214_iteration5_manifest")
    assert module.MANIFEST["required_consecutive_runs"] == 3
    assert set(module.MANIFEST["required_families"]) == EXPECTED_FAMILIES
    assert module.MANIFEST["promotion_policy"]["maximum_status"] == "PILOT_READY"
