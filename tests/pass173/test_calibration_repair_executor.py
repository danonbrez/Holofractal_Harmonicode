from __future__ import annotations

from pathlib import Path
import sys

from hhs_verification.pass173.calibration import CalibrationCorpus, CalibrationMeasurement, default_boundaries
from hhs_verification.pass173.repair_executor import RepairExecutor
from hhs_verification.pass173.repair_planner import RepairPlan


def test_calibration_uses_exact_integer_boundaries() -> None:
    corpus = CalibrationCorpus(default_boundaries())
    result = corpus.record(
        CalibrationMeasurement(
            fixture_id="probe",
            metric="probe_retries",
            integer_value=3,
            unit="attempts",
            expected_classification="PASS",
            observed_classification="PASS",
            evidence=("probe.json",),
        )
    )
    assert result["within_boundary"] is True
    assert corpus.to_dict()["passed"] is True


def test_calibration_detects_boundary_excess() -> None:
    corpus = CalibrationCorpus(default_boundaries())
    corpus.record(
        CalibrationMeasurement(
            fixture_id="ports",
            metric="port_selection_attempts",
            integer_value=17,
            unit="attempts",
            expected_classification="PASS",
            observed_classification="PASS",
            evidence=(),
        )
    )
    assert corpus.to_dict()["passed"] is False


def test_repair_executor_preserves_contracts_and_runs_bounded_command(tmp_path: Path) -> None:
    p172 = tmp_path / "HHS_PASS_172_UNIVERSAL_COMPATIBLE_ENVIRONMENT_ONE_COMMAND_INSTALLATION_DEPENDENCY_RESOLUTION_VERIFIED_BOOTSTRAP_AND_RUNTIME_ACTIVATION_SYSTEM.md"
    p173 = tmp_path / "HHS_PASS_173_UNIVERSAL_INSTALLATION_FULL_COVERAGE_REDUNDANT_VERIFICATION_CALIBRATION_REPAIR_AND_REPLAY_CLOSURE_RUNTIME.md"
    p172.write_text("contract-172", encoding="utf-8")
    p173.write_text("contract-173", encoding="utf-8")
    plan = RepairPlan(
        defect_id="D1",
        repair_class="DOCUMENTATION_REPAIR",
        implementation_paths=("docs.md",),
        unit_tests=("test_unit.py",),
        integration_tests=(),
        prohibited_changes=("contract source modification",),
        expected_receipts=("P173_REPAIR_PLAN_RECEIPT",),
    )
    result = RepairExecutor(tmp_path, timeout_seconds=30).execute(
        plan,
        repair_commands=((sys.executable, "-c", "print('validated')"),),
        checkpoint_path=tmp_path / "checkpoint.json",
    )
    assert result.status == "SUCCESS"
    assert result.protected_contracts_unchanged is True
    assert result.affected_scope_revalidated is True
    assert (tmp_path / "checkpoint.json").is_file()
