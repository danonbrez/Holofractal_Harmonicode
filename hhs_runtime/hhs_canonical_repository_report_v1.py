"""Pass 052.1 canonical repository reporting repair.

One canonical input object is assembled from committed reachability and
conformance artifacts. JSON is authoritative; Markdown is a deterministic
projection. Missing metrics are typed UNAVAILABLE and are never coerced to 0.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_runtime_reachability_audit_v1 import write_reachability_artifacts
from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry

VERSION = "PASS_052_1_CANONICAL_REPORTING_REPAIR_V1"
INPUT_SCHEMA = "HHS_CANONICAL_REPOSITORY_REPORT_INPUT_V1"
REPORT_SCHEMA = "HHS_PASS_052_1_CANONICAL_REPOSITORY_REPORT_V1"
METRIC_SCHEMA = "HHS_TYPED_REPOSITORY_METRIC_V1"


def _root(root: Optional[str | Path] = None) -> Path:
    return Path(root).resolve() if root else Path(__file__).resolve().parents[1]


def _metric(value: Any, source: str) -> Dict[str, Any]:
    if value is None:
        return {"schema": METRIC_SCHEMA, "availability": "UNAVAILABLE", "value": None, "source": source}
    return {"schema": METRIC_SCHEMA, "availability": "AVAILABLE", "value": int(value), "source": source}


def _commit(label: str, payload: Any) -> Dict[str, Any]:
    return make_hash72_kernel_witness(label, payload, width=72).to_dict()


def build_canonical_report_input(root: Optional[str | Path] = None) -> Dict[str, Any]:
    repo = _root(root)
    reachability = write_reachability_artifacts(repo)
    surface_map = build_surface_map()
    registry_status = make_default_service_registry().status()

    reachability_commitment = _commit("hhs_committed_reachability_manifest_v1", reachability)
    conformance_snapshot = {
        "schema": "HHS_COMMITTED_CONFORMANCE_SNAPSHOT_V1",
        "surface_count": surface_map.get("surface_count"),
        "conformance_edge_count": surface_map.get("conformance_edge_count"),
        "underived_surface_count": len(surface_map.get("underived_surfaces", [])),
        "conformance_root_hash72": surface_map.get("conformance_root_hash72"),
        "validation": surface_map.get("validation"),
    }
    conformance_commitment = _commit("hhs_committed_conformance_snapshot_v1", conformance_snapshot)

    obj = {
        "schema": INPUT_SCHEMA,
        "version": VERSION,
        "source_roots": {
            "reachability_manifest": "RUNTIME_REACHABILITY_MANIFEST.json",
            "service_registry": "hhs_runtime/hhs_service_registry_v1.py",
            "conformance_surface_map": "hhs_runtime/hhs_kernel_conformance_surface_map_v1.py",
        },
        "committed_reachability_manifest": reachability,
        "reachability_manifest_commitment": reachability_commitment,
        "committed_conformance_snapshot": conformance_snapshot,
        "conformance_snapshot_commitment": conformance_commitment,
        "registry_status_projection": {
            "service_count": registry_status.get("service_count"),
            "derived_service_count": registry_status.get("derived_service_count"),
            "underived_service_count": registry_status.get("underived_service_count"),
        },
    }
    obj["canonical_report_input_root_hash72"] = _commit("hhs_canonical_repository_report_input_v1", obj)["digest"]
    return obj


def build_authoritative_report(root: Optional[str | Path] = None) -> Dict[str, Any]:
    inp = build_canonical_report_input(root)
    reach = inp["committed_reachability_manifest"]
    conf = inp["committed_conformance_snapshot"]
    registry = inp["registry_status_projection"]
    metrics = {
        "service_count": _metric(reach.get("service_count"), "committed_reachability_manifest.service_count"),
        "surface_count": _metric(conf.get("surface_count"), "committed_conformance_snapshot.surface_count"),
        "conformance_edge_count": _metric(conf.get("conformance_edge_count"), "committed_conformance_snapshot.conformance_edge_count"),
        "orphan_count": _metric(reach.get("orphan_count"), "committed_reachability_manifest.orphan_count"),
        "derived_service_count": _metric(registry.get("derived_service_count"), "registry_status_projection.derived_service_count"),
        "underived_service_count": _metric(registry.get("underived_service_count"), "registry_status_projection.underived_service_count"),
        "underived_surface_count": _metric(conf.get("underived_surface_count"), "committed_conformance_snapshot.underived_surface_count"),
    }
    report = {
        "schema": REPORT_SCHEMA,
        "version": VERSION,
        "ok": all(metrics[k]["availability"] == "AVAILABLE" for k in ("service_count","surface_count","conformance_edge_count","orphan_count")),
        "authority": "CANONICAL_REPORT_INPUT_OBJECT",
        "canonical_report_input_root_hash72": inp["canonical_report_input_root_hash72"],
        "metrics": metrics,
        "unknown_metric_policy": "TYPED_UNAVAILABLE_NEVER_ZERO",
        "projection_policy": "AUTHORITATIVE_JSON_THEN_DETERMINISTIC_MARKDOWN",
    }
    report["report_root_hash72"] = _commit("hhs_pass_052_1_canonical_repository_report_v1", report)["digest"]
    return {"input": inp, "report": report}


def markdown_projection(report: Mapping[str, Any]) -> str:
    def render(name: str) -> str:
        metric = report["metrics"][name]
        return str(metric["value"]) if metric["availability"] == "AVAILABLE" else "UNAVAILABLE"
    return "\n".join([
        "# Integration Report — Pass 052.1",
        "",
        "## Canonical repository metrics",
        "",
        f"- services: `{render('service_count')}`",
        f"- surfaces: `{render('surface_count')}`",
        f"- conformance edges: `{render('conformance_edge_count')}`",
        f"- orphans: `{render('orphan_count')}`",
        f"- derived services: `{render('derived_service_count')}`",
        f"- underived services: `{render('underived_service_count')}`",
        f"- underived surfaces: `{render('underived_surface_count')}`",
        "",
        "Unknown derived metrics are represented as typed `UNAVAILABLE`; they are never rendered as zero.",
        "",
        f"Canonical input root (Hash72/u^72): `{report['canonical_report_input_root_hash72']}`",
        f"Report root (Hash72/u^72): `{report['report_root_hash72']}`",
        "",
    ])


def write_canonical_report_artifacts(root: Optional[str | Path] = None) -> Dict[str, Any]:
    repo = _root(root)
    built = build_authoritative_report(repo)
    (repo / "CANONICAL_REPORT_INPUT_PASS_052_1.json").write_text(json.dumps(built["input"], indent=2, sort_keys=True), encoding="utf-8")
    (repo / "INTEGRATION_REPORT_PASS_052_1.json").write_text(json.dumps(built["report"], indent=2, sort_keys=True), encoding="utf-8")
    (repo / "INTEGRATION_REPORT_PASS_052_1.md").write_text(markdown_projection(built["report"]), encoding="utf-8")
    return built["report"]


def canonical_repository_report_self_test() -> Dict[str, Any]:
    report = write_canonical_report_artifacts()
    values = {k: v.get("value") for k, v in report["metrics"].items()}
    ok = values["service_count"] == 109 and values["surface_count"] == 132 and values["conformance_edge_count"] == 1842 and values["orphan_count"] == 0
    return {"schema":"HHS_CANONICAL_REPOSITORY_REPORT_SELF_TEST_V1", "ok":ok, "values":values, "report_root_hash72":report["report_root_hash72"]}

if __name__ == "__main__":
    print(json.dumps(canonical_repository_report_self_test(), indent=2, sort_keys=True))
