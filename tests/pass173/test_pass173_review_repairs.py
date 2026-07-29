from __future__ import annotations

from pathlib import Path
import sys

from hhs_verification.pass173.calibration import CalibrationCorpus, CalibrationMeasurement, default_boundaries
from hhs_verification.pass173.repair_executor import RepairExecutor
from hhs_verification.pass173.repair_planner import RepairPlan


def _measurement(metric: str, maximum: int, unit: str) -> CalibrationMeasurement:
    return CalibrationMeasurement(
        fixture_id=f"fixture-{metric}",
        metric=metric,
        integer_value=maximum,
        unit=unit,
        expected_classification="PASS",
        observed_classification="PASS",
        evidence=(f"evidence/{metric}.json",),
    )


def test_empty_calibration_corpus_cannot_pass() -> None:
    result = CalibrationCorpus(default_boundaries()).to_dict()
    assert result["passed"] is False
    assert result["coverage_complete"] is False
    assert result["missing_metrics"]


def test_partial_calibration_corpus_cannot_pass() -> None:
    boundaries = default_boundaries()
    corpus = CalibrationCorpus(boundaries)
    first = boundaries[0]
    corpus.record(_measurement(first.metric, first.maximum_integer_value, first.unit))
    result = corpus.to_dict()
    assert result["passed"] is False
    assert result["coverage_complete"] is False


def test_complete_calibration_corpus_passes_exact_boundaries() -> None:
    boundaries = default_boundaries()
    corpus = CalibrationCorpus(boundaries)
    for boundary in boundaries:
        corpus.record(_measurement(boundary.metric, boundary.maximum_integer_value, boundary.unit))
    result = corpus.to_dict()
    assert result["passed"] is True
    assert result["coverage_complete"] is True
    assert result["missing_metrics"] == []


def _write_contracts(root: Path) -> None:
    for name in (
        "HHS_PASS_172_UNIVERSAL_COMPATIBLE_ENVIRONMENT_ONE_COMMAND_INSTALLATION_DEPENDENCY_RESOLUTION_VERIFIED_BOOTSTRAP_AND_RUNTIME_ACTIVATION_SYSTEM.md",
        "HHS_PASS_173_UNIVERSAL_INSTALLATION_FULL_COVERAGE_REDUNDANT_VERIFICATION_CALIBRATION_REPAIR_AND_REPLAY_CLOSURE_RUNTIME.md",
    ):
        (root / name).write_text("protected contract\n", encoding="utf-8")


def test_repair_executor_runs_planned_tests_before_revalidation(tmp_path: Path) -> None:
    _write_contracts(tmp_path)
    tests = tmp_path / "tests"
    tests.mkdir()
    passing = tests / "test_scope.py"
    passing.write_text("def test_scope():\n    assert True\n", encoding="utf-8")
    plan = RepairPlan(
        defect_id="D1",
        repair_class="TEST_CONFIGURATION_REPAIR",
        implementation_paths=("implementation.py",),
        unit_tests=("tests/test_scope.py",),
        integration_tests=(),
        prohibited_changes=("contract source modification",),
        expected_receipts=("P173_DEPENDENCY_SCOPE_REVALIDATION_RECEIPT",),
    )
    result = RepairExecutor(tmp_path, timeout_seconds=60).execute(
        plan,
        repair_commands=((sys.executable, "-c", "pass"),),
        checkpoint_path=tmp_path / "checkpoint.json",
    )
    assert result.status == "SUCCESS"
    assert result.affected_scope_revalidated is True
    assert result.commands[-1].argv[:4] == (sys.executable, "-m", "pytest", "-q")
    assert "tests/test_scope.py" in result.commands[-1].argv


def test_repair_executor_does_not_revalidate_failed_planned_test(tmp_path: Path) -> None:
    _write_contracts(tmp_path)
    tests = tmp_path / "tests"
    tests.mkdir()
    failing = tests / "test_scope.py"
    failing.write_text("def test_scope():\n    assert False\n", encoding="utf-8")
    plan = RepairPlan(
        defect_id="D2",
        repair_class="TEST_CONFIGURATION_REPAIR",
        implementation_paths=("implementation.py",),
        unit_tests=("tests/test_scope.py",),
        integration_tests=(),
        prohibited_changes=("contract source modification",),
        expected_receipts=("P173_DEPENDENCY_SCOPE_REVALIDATION_RECEIPT",),
    )
    result = RepairExecutor(tmp_path, timeout_seconds=60).execute(
        plan,
        repair_commands=((sys.executable, "-c", "pass"),),
        checkpoint_path=tmp_path / "checkpoint.json",
    )
    assert result.status == "FAILURE"
    assert result.affected_scope_revalidated is False
