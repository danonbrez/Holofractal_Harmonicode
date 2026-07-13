from hhs_runtime.hhs_contract_schema_registry_v1 import (
    SCHEMA,
    VERSION,
    build_contract_schema_registry_manifest,
    classify_schema_object,
    contract_schema_registry_self_test,
    schema_family_specs,
    validate_schema_object,
)
from hhs_runtime.hhs_runtime_contract_v1 import make_execution_request, make_runtime_packet


def test_schema_registry_contains_required_families():
    families = {item["family"] for item in schema_family_specs()}
    assert {
        "RUNTIME_PACKET",
        "EXECUTION_REQUEST",
        "INVOCATION_RECORD",
        "SEMANTIC_ADAPTER_RECORD",
        "DRYRUN_TRACE",
        "KERNEL_WITNESS",
        "FOUNDATIONAL_AUDIT",
        "LEDGER_ENTRY",
        "API_ENVELOPE",
        "FAILURE_RECORD",
    }.issubset(families)


def test_schema_classifier_recognizes_runtime_contracts():
    request = make_execution_request("test", "op", {"ok": True})
    packet = make_runtime_packet("INTERNAL", "test", {"ok": True})
    assert classify_schema_object(request)["family"] == "EXECUTION_REQUEST"
    assert validate_schema_object(request)["ok"]
    assert classify_schema_object(packet)["family"] == "RUNTIME_PACKET"
    assert validate_schema_object(packet)["ok"]


def test_schema_registry_manifest_validates_samples():
    manifest = build_contract_schema_registry_manifest()
    assert manifest["schema"] == SCHEMA
    assert manifest["version"] == VERSION
    assert manifest["ok"]
    assert manifest["family_count"] >= 10
    assert all(item["ok"] for item in manifest["sample_validations"].values())
    assert len(manifest["hash72_kernel_witness"]["digest72"]) == 72


def test_schema_registry_self_test_writes_artifacts(tmp_path):
    result = contract_schema_registry_self_test({"root": str(tmp_path)})
    assert result["ok"]
    for artifact in result["artifacts"]:
        assert (tmp_path / artifact).exists()
