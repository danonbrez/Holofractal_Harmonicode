from __future__ import annotations

from pathlib import Path
import json
import sys

from hhs_installer.planner import InstallationPlan, PlanStep
from hhs_installer.probe import Capability, ProbeReport
from hhs_installer.schema import (
    CompatibilityClass,
    InstallMode,
    InstallationRequest,
    Profile,
    SourceKind,
    SourceSpec,
)
from hhs_installer.transaction import CommandRunner, InstallationTransaction, TransactionState


def _probe() -> ProbeReport:
    return ProbeReport(
        platform="Linux",
        platform_release="test",
        architecture="x86_64",
        python_version="3.11",
        capabilities=(Capability("python_3_11", True, "3.11", ">=3.11"),),
        compatible_profiles=(Profile.CORE,),
        primary_classification=CompatibilityClass.CORE_ONLY,
        selected_ports={"api": 8000},
    )


def test_command_runner_has_terminal_timeout(tmp_path: Path) -> None:
    result = CommandRunner().run(
        [sys.executable, "-c", "import time; time.sleep(2)"],
        cwd=tmp_path,
        timeout_seconds=1,
    )
    assert result.classification == "BLOCKED"
    assert result.timed_out is True
    assert result.exit_status is None


def test_unsupported_network_source_closes_blocked_with_checkpoint(tmp_path: Path) -> None:
    home = tmp_path / "home"
    request = InstallationRequest(
        source=SourceSpec(SourceKind.RELEASE, "https://example.invalid/hhs.tar"),
        profile=Profile.CORE,
        install_mode=InstallMode.USER,
        hhs_home=str(home),
    )
    plan = InstallationPlan(
        request=request,
        probe_identity=_probe().probe_identity,
        requested_profile=Profile.CORE,
        resolved_profile=Profile.CORE,
        steps=(PlanStep("source-acquire", "acquire_source", ("install/staging/source",), 5, "delete staging"),),
        external_packages=(),
        excluded_dependency_classes=(),
    )
    transaction = InstallationTransaction(plan, _probe(), repository_root=tmp_path)
    summary = transaction.execute()
    assert summary["state"] == TransactionState.RECOVERY_REQUIRED.value
    checkpoint = json.loads(Path(summary["checkpoint"]).read_text(encoding="utf-8"))
    assert checkpoint["status"] == "BLOCKED"
    assert "resume transaction" in checkpoint["next_action"]
    assert checkpoint["blocker"] == "P172_NETWORK_SOURCE_ADAPTER_REQUIRED"
    assert Path(summary["journal"]).is_file()
