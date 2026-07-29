from __future__ import annotations

from hhs_verification.pass173.report import VerificationReportBuilder
from hhs_verification.pass173.verdicts import VerdictInput


def test_report_remains_nonterminal_without_full_evidence() -> None:
    report = VerificationReportBuilder().build(
        requirement_scan={"count": 1},
        dependency_scan={"count": 1},
        coverage={"terminal_complete": False},
        environments={"terminal_complete": False},
        profiles={"terminal_complete": False},
        receipts={"valid": True},
        replay={"matched": False},
        defects={"unrepaired": 0},
        verdict_input=VerdictInput(contract_fully_mapped=True, executed_cases=2, required_cases=20),
    )
    assert report["verdict"]["terminal"] is False
    assert report["verdict"]["omega_173"] is False
    assert report["report_identity"]
    assert any("unavailable platform" in item for item in report["honest_nonclaims"])
