from pathlib import Path

from hhs_runtime.hhs_persistence_guard_v1 import (
    write_json_artifact,
    read_json_artifact,
    export_text_artifact,
    guard_persistence_payload,
    persistence_guard_self_test,
)
from hhs_runtime.hhs_unified_hash72_ledger_v1 import verify_unified_ledger


def test_persistence_guard_wraps_json_read_write(tmp_path: Path):
    path = tmp_path / "artifact.json"
    payload_a = {"b": 2, "a": 1}
    payload_b = {"a": 1, "b": 2}

    write = write_json_artifact(path, payload_a, source="test.persistence.write")
    read = read_json_artifact(path, source="test.persistence.read")

    assert write["schema"] == "HHS_PERSISTENCE_WRITE_JSON_RESULT_V1"
    assert read["schema"] == "HHS_PERSISTENCE_READ_JSON_RESULT_V1"
    assert write["payload_hash72"] == read["payload_hash72"]
    assert write["payload_hash72"] == write_json_artifact(tmp_path / "artifact2.json", payload_b, source="test.persistence.write2")["payload_hash72"]
    assert write["io_egress_record"]["direction"] == "EGRESS"
    assert read["io_ingress_record"]["direction"] == "INGRESS"
    assert verify_unified_ledger()["ok"] is True


def test_persistence_guard_wraps_text_export_and_generic_propagation(tmp_path: Path):
    export = export_text_artifact(tmp_path / "artifact.txt", "sealed export", source="test.persistence.export")
    propagation = guard_persistence_payload("test.persistence.propagate", {"kind": "database_row", "id": 1})

    assert export["io_egress_record"]["direction"] == "EGRESS"
    assert propagation["io_propagation_record"]["direction"] == "PROPAGATION"
    assert len(propagation["payload_hash72"]) == 72
    assert verify_unified_ledger()["ok"] is True


def test_persistence_guard_self_test():
    result = persistence_guard_self_test()
    assert result["schema"] == "HHS_PERSISTENCE_GUARD_SELF_TEST_V1"
    assert result["write_ok"] is True
    assert result["read_ok"] is True
    assert result["export_ok"] is True
    assert result["payload_hash72"] == result["read_payload_hash72"]
