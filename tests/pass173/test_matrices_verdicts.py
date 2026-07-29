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


def test_profile_matrix_requires_planned_dependencies_to_be_installed() -> None:
    matrix = ProfileMatrix(
        (
            ProfileExpectation("core", ("core",), (), ("hhs",), "DISABLED"),
        )
    )
    result = matrix.record(
        "core",
        included_dependencies=("core",),
        installed_dependencies=(),
        callable_surfaces=("hhs",),
        provider_state="DISABLED",
    )
    assert result.included_match is False
    assert result.classification == "P173_PROFILE_CLOSURE_MISMATCH"


def test_clean_runner_captures_success_and_isolates_source(tmp_path: Path) -> None:
    marker = tmp_path / "marker.txt"
    runner = CleanInstallRunner()
    result = runner.run(
        CleanInstallRequest(
            case_id="success",
            command=(sys.executable, "-c", "from pathlib import Path; Path('marker.txt').write_text('isolated'); print('ok')"),
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
        assert result.recovery_receipt["caller_worktree_untouched"] is True
        assert result.recovery_receipt["isolated_source_changed"] is True
        assert marker.exists() is False
        assert result.output_identity
    finally:
        runner.cleanup(result)


def test_clean_runner_reserves_hhs_home_and_pythonpath(tmp_path: Path) -> None:
    runner = CleanInstallRunner()
    result = runner.run(
        CleanInstallRequest(
            case_id="reserved-environment",
            command=(
                sys.executable,
                "-c",
                "import os; print(os.environ['HHS_HOME']); print(os.environ['PYTHONPATH'])",
            ),
            repository_root=str(tmp_path),
            profile="core",
            platform="test",
            architecture="test",
            timeout_seconds=30,
            environment={"HHS_HOME": "/real/home", "PYTHONPATH": "/caller/source", "SAFE_CUSTOM": "preserved"},
        )
    )
    try:
        lines = result.stdout.strip().splitlines()
        assert lines == [
            result.recovery_receipt["isolated_hhs_home"],
            result.recovery_receipt["isolated_pythonpath"],
        ]
        assert result.recovery_receipt["ignored_reserved_environment"] == ["HHS_HOME", "PYTHONPATH"]
        assert "/real/home" not in result.stdout
        assert "/caller/source" not in result.stdout
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


def test_verdict_does_not_promote_redundant_lane_without_prerequisites() -> None:
    result = VerdictEngine.classify(VerdictInput(redundant_lane_agreement=True))
    assert result.verdict is Verdict.H
    assert result.terminal is False
