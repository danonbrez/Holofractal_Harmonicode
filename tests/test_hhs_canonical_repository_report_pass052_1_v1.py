from hhs_runtime.hhs_canonical_repository_report_v1 import build_authoritative_report, markdown_projection

def test_canonical_report_uses_authoritative_artifacts():
    built = build_authoritative_report()
    report = built["report"]
    assert report["metrics"]["service_count"]["value"] >= 109
    assert report["metrics"]["surface_count"]["value"] >= 132
    assert report["metrics"]["conformance_edge_count"]["value"] >= 1842
    assert report["metrics"]["orphan_count"]["value"] == 0
    assert report["canonical_report_input_root_hash72"]

def test_unknown_metrics_are_unavailable_not_zero():
    built = build_authoritative_report()
    metric = built["report"]["metrics"]["service_count"]
    assert metric["availability"] == "AVAILABLE"
    assert "UNAVAILABLE" in built["report"]["unknown_metric_policy"]
    assert markdown_projection(built["report"]).startswith("# Integration Report — Pass 052.1")
