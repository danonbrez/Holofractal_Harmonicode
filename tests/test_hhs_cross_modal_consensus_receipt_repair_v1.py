from __future__ import annotations

from hhs_realtime_phase_certification_v1 import RealtimePhaseCertificationV1


def test_realtime_phase_certification_closes_after_consensus_receipt_repair() -> None:
    report = RealtimePhaseCertificationV1().run_all()
    assert report["all_ok"] is True, report
    assert report["failed"] == 0, report
    assert report["passed"] == 3, report
    assert report["status"] == "CERTIFIED_REALTIME_PHASE_LOCKED", report
