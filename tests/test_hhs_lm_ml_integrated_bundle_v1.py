from hhs_lm_ml_integrated_bundle_v1 import (
    build_lm_ml_integrated_bundle_report,
)


def test_lm_ml_integrated_bundle_report(tmp_path):
    report = build_lm_ml_integrated_bundle_report(
        tmp_path / "hhs_lm_ml_integrated_bundle_v1_report.json"
    )

    assert report["all_ok"] is True
    assert report["status"] == "CERTIFIED_LOCKED"
    assert report["frozen_state_preserved"] is True
    assert report["bundled_service_count"] >= 13
    assert report["registry_status"]["authority_ok"] is True
