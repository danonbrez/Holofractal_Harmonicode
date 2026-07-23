from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from hhs_runtime.pass145.canonical import canonical_json
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass146.api import HHS146SecurityServer
from hhs_runtime.pass146.service import HHS146Service


def bootstrap(tmp_path: Path):
    service = HHS146Service(tmp_path / "hhs146.sqlite3")
    result = service.security.bootstrap_local_owner("Test Owner")
    return service, result["result"]["identity_id"], result["result"]["grant_id"], result["authentication_token"]


def ingest_fixture(service: HHS146Service, namespace: str = "secure") -> str:
    result = service.ingest_bytes(b"O is distinct from \xcf\x80. Hash72 preserves witnessed ancestry.\n", name="fixture.txt", namespace=namespace)
    return result["source_id"]


def construct_query(service: HHS146Service, identity: str, grant: str, token: str, *, namespace: str = "secure") -> str:
    result = service.security.construct_path(identity, grant, token, "QUERY", {"question": "What is distinct from pi?", "namespace": namespace, "classification": "INTERNAL"})
    return result["result"]["contract_id"]


def test_bootstrap_authentication_and_duplicate_bootstrap_rejected(tmp_path: Path) -> None:
    service, identity, grant, token = bootstrap(tmp_path)
    with service:
        assert service.security.authenticate(identity, token)["authenticated"] is True
        with pytest.raises(Pass145Error) as wrong:
            service.security.authenticate(identity, "wrong-token")
        assert wrong.value.code == "IDENTITY_UNRESOLVED"
        with pytest.raises(Pass145Error) as duplicate:
            service.security.bootstrap_local_owner()
        assert duplicate.value.code == "AUTHORITY_INSUFFICIENT"
        assert service.db.verify_receipt_chain()["ok"] is True


def test_minimum_query_path_executes_closes_dissolves_and_replays(tmp_path: Path) -> None:
    service, identity, grant, token = bootstrap(tmp_path)
    with service:
        ingest_fixture(service)
        contract_id = construct_query(service, identity, grant, token)
        admitted = service.security.get_contract(contract_id)
        assert admitted["capabilities"] == ["DATABASE_READ", "PATH_EXECUTION", "QUERY"]
        assert admitted["pathway"]["active_capabilities"] == []
        executed = service.security.execute_path(contract_id, identity, token)
        result = executed["result"]
        assert result["status"] == "BOUNDARY_PATH_CLOSED"
        assert result["temporary_capabilities_expired"] is True
        closed = service.security.get_contract(contract_id)
        assert closed["status"] == "BOUNDARY_CLOSED"
        assert closed["pathway"]["lifecycle_state"] == "DISSOLVED"
        assert closed["pathway"]["active_capabilities"] == []
        assert service.security.replay_path(contract_id)["status"] == "REPLAY_VALIDATED"


def test_overbroad_request_is_nonrepresentable_and_creates_no_path(tmp_path: Path) -> None:
    service, identity, grant, token = bootstrap(tmp_path)
    with service:
        before = service.security.status()["counts"]["security_boundary_contracts"]
        with pytest.raises(Pass145Error) as exc:
            service.security.construct_path(identity, grant, token, "QUERY", {"question": "x", "requested_capabilities": ["QUERY", "DATABASE_READ", "PATH_EXECUTION", "NETWORK"]})
        assert exc.value.code == "CAPABILITY_OVERBROAD"
        after = service.security.status()["counts"]["security_boundary_contracts"]
        assert before == after


def test_delegated_grant_cannot_expand_parent_authority(tmp_path: Path) -> None:
    service, root_id, root_grant, root_token = bootstrap(tmp_path)
    with service:
        child = service.security.create_identity(root_id, root_grant, root_token, "Child")
        child_id = child["result"]["identity_id"]
        narrow = service.security.create_grant(root_id, root_grant, root_token, child_id, capabilities=["QUERY", "DATABASE_READ", "PATH_EXECUTION"], operations=["QUERY"], sources=["secure"], destinations=["LOCAL_RESULT"], disclosure_policy={"classifications": ["INTERNAL"]})
        narrow_grant = narrow["result"]["grant_id"]
        with pytest.raises(Pass145Error) as exc:
            service.security.create_grant(child_id, narrow_grant, child["authentication_token"], child_id, capabilities=["QUERY", "DATABASE_READ", "PATH_EXECUTION", "NETWORK"], operations=["QUERY"], sources=["secure"], destinations=["LOCAL_RESULT"])
        assert exc.value.code in {"AUTHORITY_INSUFFICIENT", "RECURSIVE_AUTHORITY_EXPANSION"}


def test_recursive_child_boundary_preserves_or_reduces_parent_surface(tmp_path: Path) -> None:
    service, identity, grant, token = bootstrap(tmp_path)
    with service:
        parent = service.security.construct_path(identity, grant, token, "PROPAGATE", {"data": {"root": True}, "source_peer": "a", "destination_peer": "b", "classification": "INTERNAL", "disclosure_fields": ["result", "trace"]}, destination={"kind": "PEER", "id": "b"})
        parent_id = parent["result"]["contract_id"]
        child = service.security.construct_path(identity, grant, token, "PROPAGATE", {"data": {"child": True}, "source_peer": "a", "destination_peer": "b", "classification": "INTERNAL", "disclosure_fields": ["result"]}, destination={"kind": "PEER", "id": "b"}, parent_contract_id=parent_id)
        assert child["result"]["recursive_depth"] == 1
        with pytest.raises(Pass145Error) as expanded:
            service.security.construct_path(identity, grant, token, "QUERY", {"question": "x", "classification": "INTERNAL"}, parent_contract_id=parent_id)
        assert expanded.value.code == "RECURSIVE_AUTHORITY_EXPANSION"


def test_contract_carried_message_is_revalidated_by_receiver(tmp_path: Path) -> None:
    service, root_id, root_grant, root_token = bootstrap(tmp_path)
    with service:
        receiver = service.security.create_identity(root_id, root_grant, root_token, "Receiver")
        receiver_id = receiver["result"]["identity_id"]
        receiver_token = receiver["authentication_token"]
        delegated = service.security.create_grant(root_id, root_grant, root_token, receiver_id, capabilities=["NETWORK", "NETWORK_RECEIVE", "PATH_EXECUTION"], operations=["PROPAGATE"], sources=["*"], destinations=["peer-b"], disclosure_policy={"classifications": ["INTERNAL"]})
        receiver_grant = delegated["result"]["grant_id"]
        contract = service.security.construct_path(root_id, root_grant, root_token, "PROPAGATE", {"data": {"claim": "evidence"}, "source_peer": "peer-a", "destination_peer": "peer-b", "classification": "INTERNAL", "provenance": {"source_id": "SRC-1"}}, destination={"kind": "PEER", "id": "peer-b"})
        execution = service.security.execute_path(contract["result"]["contract_id"], root_id, root_token)
        message_id = execution["result"]["result"]["message_id"]
        message = service.security.inspect_message(message_id)
        assert message["integrity_valid"] is True
        received = service.security.receive_message(message_id, receiver_id, receiver_grant, receiver_token)
        assert received["result"]["prior_admission_reused_without_validation"] is False
        assert received["result"]["data"] == {"claim": "evidence"}


def test_receiver_without_network_receive_is_rejected(tmp_path: Path) -> None:
    service, root_id, root_grant, root_token = bootstrap(tmp_path)
    with service:
        receiver = service.security.create_identity(root_id, root_grant, root_token, "Receiver")
        receiver_id = receiver["result"]["identity_id"]
        receiver_token = receiver["authentication_token"]
        delegated = service.security.create_grant(root_id, root_grant, root_token, receiver_id, capabilities=["QUERY", "DATABASE_READ", "PATH_EXECUTION"], operations=["QUERY"], sources=["*"], destinations=["peer-b"], disclosure_policy={"classifications": ["INTERNAL"]})
        contract = service.security.construct_path(root_id, root_grant, root_token, "PROPAGATE", {"data": "x", "source_peer": "a", "destination_peer": "peer-b", "classification": "INTERNAL"}, destination={"kind": "PEER", "id": "peer-b"})
        execution = service.security.execute_path(contract["result"]["contract_id"], root_id, root_token)
        message_id = execution["result"]["result"]["message_id"]
        with pytest.raises(Pass145Error) as exc:
            service.security.receive_message(message_id, receiver_id, delegated["result"]["grant_id"], receiver_token)
        assert exc.value.code == "AUTHORITY_INSUFFICIENT"


def test_conflict_negotiation_preserves_both_states_and_no_silent_winner(tmp_path: Path) -> None:
    service, identity, grant, token = bootstrap(tmp_path)
    with service:
        contract = service.security.construct_path(identity, grant, token, "NEGOTIATE_CONFLICT", {"left_state": {"x": 1, "same": 3}, "right_state": {"x": 2, "same": 3}, "policy": {"winner": "NONE"}, "classification": "INTERNAL"})
        result = service.security.execute_path(contract["result"]["contract_id"], identity, token)["result"]["result"]
        resolution = result["resolution"]
        assert resolution["status"] == "STABLE_UNRESOLVED"
        assert resolution["silent_winner_selected"] is False
        assert resolution["nonconflicting_result"] == {"same": 3}
        assert resolution["conflicts"][0]["key"] == "x"


def test_relevant_state_change_blocks_activation(tmp_path: Path) -> None:
    service, identity, grant, token = bootstrap(tmp_path)
    with service:
        source_id = ingest_fixture(service)
        contract = service.security.construct_path(identity, grant, token, "VALIDATE_SOURCE", {"source_id": source_id, "classification": "INTERNAL"})
        def mutate(conn):
            conn.execute("UPDATE sources SET quarantined=1 WHERE source_id=?", (source_id,))
            return {"status": "SOURCE_QUARANTINED_FOR_TEST"}
        service.db.mutate("TEST_SOURCE_STATE_CHANGE", {"source_id": source_id}, mutate)
        with pytest.raises(Pass145Error) as exc:
            service.security.execute_path(contract["result"]["contract_id"], identity, token)
        assert exc.value.code == "SOURCE_STATE_INVALID"


def test_resource_failure_enters_validated_recovery_and_expires_capabilities(tmp_path: Path) -> None:
    service, identity, grant, token = bootstrap(tmp_path)
    with service:
        ingest_fixture(service)
        contract = service.security.construct_path(identity, grant, token, "QUERY", {"question": "O", "namespace": "secure", "classification": "INTERNAL", "resource_budget": {"max_output_bytes": 1}})
        contract_id = contract["result"]["contract_id"]
        with pytest.raises(Pass145Error) as exc:
            service.security.execute_path(contract_id, identity, token)
        assert exc.value.code == "RESOURCE_BOUNDED"
        failed = service.security.get_contract(contract_id)
        assert failed["status"] == "BOUNDARY_FAILED"
        assert failed["pathway"]["lifecycle_state"] == "RECOVERY_REQUIRED"
        assert failed["pathway"]["active_capabilities"] == []
        assert failed["pathway"]["recovery_state"] == "VALIDATED_HALT"


def test_float_cannot_enter_canonical_boundary_contract(tmp_path: Path) -> None:
    service, identity, grant, token = bootstrap(tmp_path)
    with service:
        with pytest.raises((Pass145Error, TypeError)):
            service.security.construct_path(identity, grant, token, "QUERY", {"question": "x", "classification": "INTERNAL", "untrusted_float": 0.1})
        assert service.security.status()["counts"]["security_boundary_contracts"] == 0


def test_security_api_requires_server_authority_and_executes_boundary(tmp_path: Path) -> None:
    db = tmp_path / "api.sqlite3"
    with HHS146Service(db) as service:
        root = service.security.bootstrap_local_owner("API Owner")
        identity = root["result"]["identity_id"]
        grant = root["result"]["grant_id"]
        token = root["authentication_token"]
    server = HHS146SecurityServer(("127.0.0.1", 0), db, token="server-secret")
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with pytest.raises(urllib.error.HTTPError) as unauth:
            urllib.request.urlopen(base + "/api/v1/security/status", timeout=3)
        assert unauth.value.code == 401
        body = canonical_json({"identity_id": identity, "grant_id": grant, "identity_token": token, "operation": "QUERY", "request": {"question": "none", "classification": "INTERNAL"}}).encode()
        req = urllib.request.Request(base + "/api/v1/security/path/construct", data=body, headers={"Authorization": "Bearer server-secret", "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=3) as response:
            result = json.loads(response.read())
        assert result["result"]["status"] == "BOUNDARY_PATH_CONSTRUCTED"
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=3)


def test_cli_wraps_parent_commands_and_exposes_security(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    db = tmp_path / "cli.sqlite3"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root)
    version = subprocess.run([str(root / "hhs"), "--db", str(db), "version"], cwd=root, env=env, capture_output=True, text=True, check=True)
    version_payload = json.loads(version.stdout)
    # The inherited Pass 146 surface remains authoritative beneath the latest
    # additive launcher.  Later passes replace only the root release identity,
    # not the parent runtime contract.
    assert version_payload["pass_id"] == "HHS-P148-NSAM"
    assert version_payload["parent"]["pass_id"] == "HHS-P147"
    assert version_payload["parent"]["parent"]["pass_id"] == "HHS-P146"
    bootstrap_result = subprocess.run([str(root / "hhs"), "--db", str(db), "security", "bootstrap-local"], cwd=root, env=env, capture_output=True, text=True, check=True)
    assert json.loads(bootstrap_result.stdout)["result"]["status"] in {"LOCAL_SECURITY_OWNER_BOOTSTRAPPED", "LOCAL_SECURITY_OWNER_ALREADY_BOOTSTRAPPED"}
    parent_status = subprocess.run([str(root / "hhs"), "--db", str(db), "database", "integrity"], cwd=root, env=env, capture_output=True, text=True, check=True)
    assert json.loads(parent_status.stdout)["ok"] is True


def test_receipt_chain_and_database_root_cover_security_objects(tmp_path: Path) -> None:
    service, identity, grant, token = bootstrap(tmp_path)
    with service:
        root_before = service.db.database_root()
        contract = service.security.construct_path(identity, grant, token, "QUERY", {"question": "x", "classification": "INTERNAL"})
        root_after = service.db.database_root()
        assert root_before != root_after
        service.security.execute_path(contract["result"]["contract_id"], identity, token)
        assert service.db.integrity_check()["ok"] is True
        assert service.db.verify_receipt_chain()["ok"] is True
        assert service.security.status()["open_pathways"] == 0


def test_inherited_cli_operation_is_automatically_boundary_wrapped(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    db = tmp_path / "wrapped.sqlite3"
    document = tmp_path / "wrapped.txt"
    document.write_text("Boundary constructed CLI evidence.\n", encoding="utf-8")
    env = os.environ.copy(); env["PYTHONPATH"] = str(root)
    proc = subprocess.run([str(root / "hhs"), "--db", str(db), "ingest", "file", str(document), "--namespace", "wrapped"], cwd=root, env=env, capture_output=True, text=True, check=True)
    assert json.loads(proc.stdout)["status"] == "SOURCE_ADMITTED"
    with HHS146Service(db) as service:
        contracts = service.security.list_contracts()
        assert contracts and contracts[0]["operation"] == "RUN_CLI_COMMAND"
        full = service.security.get_contract(contracts[0]["contract_id"])
        assert full["status"] == "BOUNDARY_CLOSED"
        assert full["pathway"]["active_capabilities"] == []
        assert full["request"]["input_evidence"]["files"][0]["sha256"]


def test_combined_api_routes_knowledge_operations_through_boundaries(tmp_path: Path) -> None:
    db = tmp_path / "combined-api.sqlite3"
    with HHS146Service(db) as service:
        root = service.security.bootstrap_local_owner("Server Owner")
        identity = root["result"]["identity_id"]
        grant = root["result"]["grant_id"]
        token = root["authentication_token"]
    server = HHS146SecurityServer(("127.0.0.1", 0), db, token="api-token", identity_id=identity, grant_id=grant, identity_token=token)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    headers = {"Authorization": "Bearer api-token", "Content-Type": "application/json"}
    try:
        body = canonical_json({"text": "O is distinct from π.", "name": "api.txt", "namespace": "api"}).encode()
        req = urllib.request.Request(base + "/api/v1/ingest", data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as response:
            admitted = json.loads(response.read())
        assert admitted["status"] == "SOURCE_ADMITTED"
        qbody = canonical_json({"question": "What is distinct from π?", "namespace": "api"}).encode()
        qreq = urllib.request.Request(base + "/api/v1/query", data=qbody, headers=headers, method="POST")
        with urllib.request.urlopen(qreq, timeout=5) as response:
            query = json.loads(response.read())
        assert query["answer"]["directly_retrieved_evidence"]
        with HHS146Service(db) as service:
            operations = [x["operation"] for x in service.security.list_contracts(10)]
            assert operations.count("RUN_CLI_COMMAND") >= 2
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=3)


def _signed_cross_node_fixture(tmp_path: Path):
    sender_db = tmp_path / "sender.sqlite3"
    receiver_db = tmp_path / "receiver.sqlite3"
    with HHS146Service(sender_db) as sender:
        sroot = sender.security.bootstrap_local_owner("Sender")
        sid, sgrant, stoken = sroot["result"]["identity_id"], sroot["result"]["grant_id"], sroot["authentication_token"]
        public = sender.security.identity_public_record(sid)
    with HHS146Service(receiver_db) as receiver:
        rroot = receiver.security.bootstrap_local_owner("Receiver")
        rid, rgrant, rtoken = rroot["result"]["identity_id"], rroot["result"]["grant_id"], rroot["authentication_token"]
        receiver.security.trust_peer(rid, rgrant, rtoken, "peer-a", public["public_key_b64"], classifications=["INTERNAL"], destinations=["peer-b"])
    with HHS146Service(sender_db) as sender:
        contract = sender.security.construct_path(sid, sgrant, stoken, "PROPAGATE", {"data": {"claim": "O is distinct from π"}, "source_peer": "peer-a", "destination_peer": "peer-b", "classification": "INTERNAL", "provenance": {"source": "test"}}, destination={"kind": "PEER", "id": "peer-b"})
        execution = sender.security.execute_path(contract["result"]["contract_id"], sid, stoken)
        output = execution["result"]["result"]
        envelope = {k: v for k, v in output.items() if k not in {"status", "payload_detached_from_contract"}}
    return sender_db, receiver_db, (sid, sgrant, stoken), (rid, rgrant, rtoken), envelope


def test_signed_cross_node_envelope_reconstructs_receiver_boundary(tmp_path: Path) -> None:
    _, receiver_db, _, (rid, rgrant, rtoken), envelope = _signed_cross_node_fixture(tmp_path)
    with HHS146Service(receiver_db) as receiver:
        before = receiver.security.status()["counts"]["security_boundary_contracts"]
        contract = receiver.security.construct_path(rid, rgrant, rtoken, "RECEIVE_PROPAGATION", {"envelope": envelope, "source_peer": "peer-a", "destination_peer": "peer-b", "classification": "INTERNAL"}, destination={"kind": "PEER", "id": "peer-b"})
        result = receiver.security.execute_path(contract["result"]["contract_id"], rid, rtoken)
        assert result["result"]["result"]["status"] == "EXTERNAL_MESSAGE_RECEIVED_AND_REVALIDATED"
        assert receiver.security.status()["counts"]["security_boundary_contracts"] == before + 1
        inspected = receiver.security.inspect_message(envelope["message_id"])
        assert inspected["integrity_valid"] is True
        assert inspected["status"] == "EXTERNAL_RECEIVED_AND_REVALIDATED"
        assert receiver.security.replay_path(contract["result"]["contract_id"])["status"] == "REPLAY_VALIDATED"


def test_forged_cross_node_envelope_is_nonrepresentable(tmp_path: Path) -> None:
    _, receiver_db, _, (rid, rgrant, rtoken), envelope = _signed_cross_node_fixture(tmp_path)
    forged = json.loads(json.dumps(envelope))
    forged["data"]["claim"] = "forged"
    with HHS146Service(receiver_db) as receiver:
        before = receiver.security.status()["counts"]["security_boundary_contracts"]
        with pytest.raises(Pass145Error) as exc:
            receiver.security.construct_path(rid, rgrant, rtoken, "RECEIVE_PROPAGATION", {"envelope": forged, "source_peer": "peer-a", "destination_peer": "peer-b", "classification": "INTERNAL"}, destination={"kind": "PEER", "id": "peer-b"})
        assert exc.value.code == "PROVENANCE_INCOMPLETE"
        assert receiver.security.status()["counts"]["security_boundary_contracts"] == before


def test_two_node_loopback_http_message_transport(tmp_path: Path) -> None:
    _, receiver_db, _, (rid, rgrant, rtoken), envelope = _signed_cross_node_fixture(tmp_path)
    server = HHS146SecurityServer(("127.0.0.1", 0), receiver_db, token="transport-token", identity_id=rid, grant_id=rgrant, identity_token=rtoken)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        body = canonical_json({"receiver_identity_id": rid, "receiver_grant_id": rgrant, "receiver_token": rtoken, "envelope": envelope}).encode()
        request = urllib.request.Request(f"http://127.0.0.1:{server.server_port}/api/v1/security/message/admit", data=body, headers={"Authorization": "Bearer transport-token", "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=5) as response:
            result = json.loads(response.read())
        assert result["result"]["result"]["status"] == "EXTERNAL_MESSAGE_RECEIVED_AND_REVALIDATED"
        with HHS146Service(receiver_db) as receiver:
            assert receiver.security.inspect_message(envelope["message_id"])["signature_verification"]["signature_valid"] is True
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=3)


def test_schema_1_1_database_migrates_signed_envelope_column(tmp_path: Path) -> None:
    import sqlite3
    db = tmp_path / "legacy-1.1.sqlite3"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE security_messages(message_id TEXT PRIMARY KEY,path_id TEXT NOT NULL,contract_id TEXT NOT NULL,source_peer TEXT NOT NULL,destination_peer TEXT NOT NULL,data_json TEXT NOT NULL,provenance_json TEXT NOT NULL,scope_json TEXT NOT NULL,expected_state_json TEXT NOT NULL,reversal_json TEXT NOT NULL,message_hash72 TEXT NOT NULL UNIQUE,status TEXT NOT NULL,created_at TEXT NOT NULL)")
    conn.commit(); conn.close()
    with HHS146Service(db) as service:
        columns = {str(row[1]) for row in service.db.conn.execute("PRAGMA table_info(security_messages)")}
        assert "envelope_json" in columns
        # Schema 1.2.0 is the minimum version containing the signed-envelope
        # migration; additive descendants may advance the canonical schema.
        observed = tuple(int(part) for part in service.db.meta("schema_version").split("."))
        assert observed >= (1, 2, 0)


def test_peer_key_mismatch_rejected_before_receiver_path(tmp_path: Path) -> None:
    import base64
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    sender_db = tmp_path / "sender-key.sqlite3"
    receiver_db = tmp_path / "receiver-key.sqlite3"
    with HHS146Service(sender_db) as sender:
        root = sender.security.bootstrap_local_owner("Sender")
        sid, sgrant, stoken = root["result"]["identity_id"], root["result"]["grant_id"], root["authentication_token"]
        contract = sender.security.construct_path(sid, sgrant, stoken, "PROPAGATE", {"data": "signed", "source_peer": "peer-a", "destination_peer": "peer-b", "classification": "INTERNAL"}, destination={"kind": "PEER", "id": "peer-b"})
        output = sender.security.execute_path(contract["result"]["contract_id"], sid, stoken)["result"]["result"]
        envelope = {k: v for k, v in output.items() if k not in {"status", "payload_detached_from_contract"}}
    wrong_public = Ed25519PrivateKey.generate().public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    with HHS146Service(receiver_db) as receiver:
        root = receiver.security.bootstrap_local_owner("Receiver")
        rid, rgrant, rtoken = root["result"]["identity_id"], root["result"]["grant_id"], root["authentication_token"]
        receiver.security.trust_peer(rid, rgrant, rtoken, "peer-a", base64.b64encode(wrong_public).decode("ascii"), classifications=["INTERNAL"], destinations=["peer-b"])
        before = receiver.security.status()["counts"]["security_boundary_contracts"]
        with pytest.raises(Pass145Error) as exc:
            receiver.security.construct_path(rid, rgrant, rtoken, "RECEIVE_PROPAGATION", {"envelope": envelope, "source_peer": "peer-a", "destination_peer": "peer-b", "classification": "INTERNAL"}, destination={"kind": "PEER", "id": "peer-b"})
        assert exc.value.code == "IDENTITY_UNRESOLVED"
        assert receiver.security.status()["counts"]["security_boundary_contracts"] == before


def test_remote_non_loopback_binding_is_explicitly_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        HHS146SecurityServer(("0.0.0.0", 0), tmp_path / "remote.sqlite3", token="x")
