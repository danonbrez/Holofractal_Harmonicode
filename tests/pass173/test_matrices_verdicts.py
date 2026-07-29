from __future__ import annotations

from pathlib import Path
import sys

from hhs_verification.pass173.clean_install_runner import CleanInstallRequest, CleanInstallRunner
from hhs_verification.pass173.environment_matrix import EnvironmentCase, EnvironmentMatrix
from hhs_verification.pass173.profile_matrix import ProfileExpectation, ProfileMatrix
from hhs_verification.pass173.verdicts import Verdict, VerdictEngine, VerdictInput


def test_environment_matrix_does_not_promote_unexecuted_runner() -> None:
    matrix = EnvironmentMatrix(
        (
            EnvironmentCase(
                "gpu",
                "Linux",
                "x86_64",
                "assistant-local-gpu",
                True,
                "HHS_ENVIRONMENT_FULLY_COMPATIBLE",
                ("gpu_device",),
            ),
        )
    )
    result = matrix.record(
        "gpu",
        executed=False,
        observed_classification="HHS_ENVIRONMENT_FULLY_COMPATIBLE",
    )
    assert result.observed_classification == "P173_PLATFORM_NOT_VERIFIED"
    assert result.matched is False
    assert matrix.to_dict()["terminal_complete"] is False


def test_profile_matrix_checks_exclusions() -> None:
    matrix = ProfileMatrix(
        (
            ProfileExpectation(
                "core",
                ("core",),
                ("litert-lm",),
                ("hhs",),
                "DISABLED",
            ),
        )
    )
    result = matrix.record(
        "core",
        included_dependencies=("core",),
        installed_dependencies=("core", "litert-lm"),
        callable_surfaces=("hhs",),
        provider_state="DISABLED",
    )
    assert result.excluded_match is False
    assert result.classification == "P173_PROFILE_CLOSURE_MISMATCH"


def test_clean_runner_captures_success_and_recovery_receipt(tmp_path: Path) -> None:
    runner = CleanInstallRunner()
    result = runner.run(
        CleanInstallRequest(
            case_id="success",
            command=(sys.executable, "-c", "print('ok')"),
            repository_root=str(tmp_path),
            profile="core",
            platform="test",
            architecture="test",
            timeout_seconds=30,
        )
    )
    try:
        assert result.status == "SUCCESS"
        assert result.exit_status == 0
        assert result.recovery_receipt["worktree_clean"] is True
        assert result.output_identity
    finally:
        runner.cleanup(result)


def test_clean_runner_timeout_is_blocked(tmp_path: Path) -> None:
    runner = CleanInstallRunner()
    result = runner.run(
        CleanInstallRequest(
            case_id="timeout",
            command=(sys.executable, "-c", "import time; time.sleep(2)"),
            repository_root=str(tmp_path),
            profile="core",
            platform="test",
            architecture="test",
            timeout_seconds=1,
        )
    )
    try:
        assert result.status == "BLOCKED"
        assert result.timed_out is True
        assert result.classification == "P173_CLEAN_INSTALL_TIMEOUT"
    finally:
        runner.cleanup(result)


def test_verdict_requires_all_terminal_conditions() -> None:
    partial = VerdictEngine.classify(VerdictInput(contract_fully_mapped=True))
    assert partial.verdict is Verdict.G
    assert partial.terminal is False

    terminal = VerdictEngine.classify(
        VerdictInput(
            contract_fully_mapped=True,
            executed_cases=10,
            required_cases=10,
            full_matrix_executed=True,
            redundant_lane_agreement=True,
            calibration_passed=True,
            final_replay_match=True,
            receipt_mismatches=0,
            authority_bypasses=0,
            data_loss_events=0,
            unrepaired_defects=0,
        )
    )
    assert terminal.verdict is Verdict.A_PLUS
    assert terminal.terminal is True
    assert terminal.omega_173 is True
