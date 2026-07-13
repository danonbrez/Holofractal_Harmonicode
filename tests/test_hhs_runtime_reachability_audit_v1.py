from pathlib import Path

from hhs_runtime.hhs_runtime_reachability_audit_v1 import (
    SCHEMA,
    build_reachability_manifest,
    reachability_audit_self_test,
)


def test_reachability_manifest_contains_canonical_surfaces():
    root = Path(__file__).resolve().parents[1]
    manifest = build_reachability_manifest(root)
    assert manifest["schema"] == SCHEMA
    assert manifest["module_count"] > 0
    assert manifest["service_count"] >= 14
    assert manifest["api_route_count"] >= 18
    assert manifest["hash72_kernel_witness"]["schema"] == "HHS_HASH72_KERNEL_WITNESS_V1"
    assert len(manifest["hash72_kernel_witness"]["dna"]) == 72
    assert manifest["hash72_kernel_witness"]["zero_sum"] is True


def test_reachability_records_statuses_for_spine_modules():
    root = Path(__file__).resolve().parents[1]
    manifest = build_reachability_manifest(root)
    by_module = {record["module"]: record for record in manifest["records"]}
    assert by_module["hhs_runtime.hhs_service_registry_v1"]["status"] in {"BOOT_REACHABLE", "API_REACHABLE"}
    assert by_module["hhs_runtime.hhs_srcg_gate_v1"]["status"] == "SERVICE_REACHABLE"
    assert by_module["hhs_runtime.hhs_system_closure_harness_v1"]["status"] == "SERVICE_REACHABLE"
    assert by_module["hhs_backend.api.runtime_routes"]["status"] == "API_REACHABLE"


def test_reachability_self_test_writes_artifacts():
    result = reachability_audit_self_test()
    assert result["ok"] is True
    root = Path(__file__).resolve().parents[1]
    for rel in result["artifacts"]:
        assert (root / rel).exists()
