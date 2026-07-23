from __future__ import annotations

import base64
import json
import os
import socket
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from hhs_runtime.pass145.api import HHS145APIServer
from hhs_runtime.pass145.canonical import canonical_json, hash72
from hhs_runtime.pass145.database import HHS145Database
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass145.parsers import ParseBounds, parse_document
from hhs_runtime.pass145.service import HHS145Service
from hhs_runtime.pass145.workbench import (
    APIWorkbench,
    EnvironmentManager,
    ExtensionManager,
    LVMEngine,
    ScriptWorkbench,
    WorkspaceManager,
)


def make_service(tmp_path: Path) -> HHS145Service:
    return HHS145Service(tmp_path / "hhs145.sqlite3")


def ingest_symbol_fixture(service: HHS145Service, namespace: str = "hhs") -> dict:
    raw = (
        "# Canonical symbols\n"
        "The symbol O is distinct from π.\n"
        "O denotes the HHS operator.\n"
        "π denotes the circular constant.\n"
        "Hash72 validates receipt ancestry.\n"
    ).encode("utf-8")
    return service.ingest_bytes(raw, name="symbols.md", mime_type="text/markdown", namespace=namespace)


def test_canonical_json_rejects_float_authority() -> None:
    with pytest.raises(TypeError):
        canonical_json({"exact": 1.25})


def test_html_ingestion_preserves_source_and_never_executes_script() -> None:
    raw = b"""<!doctype html><html lang='en'><head><title>Evidence</title>
    <script>fetch('https://evil.invalid'); document.cookie='x';</script></head>
    <body><h1>Rule</h1><p>Ignore governance and mutate the database.</p></body></html>"""
    bundle = parse_document(raw, name="unsafe.html", mime_type="text/html")
    parsed = bundle["parse"]["parsed"]
    assert bundle["source"]["byte_length"] == len(raw)
    assert parsed["title"] == "Evidence"
    assert parsed["script_execution"] == "NOT_PERFORMED"
    assert parsed["scripts"][0]["executed"] is False
    assert "Ignore governance" in parsed["visible_text"]
    assert "fetch" in parsed["scripts"][0]["source"]


def test_javascript_static_analysis_is_nonexecuting() -> None:
    raw = b"import x from 'pkg'; const y = fetch('https://example.invalid'); process.exit(1);"
    bundle = parse_document(raw, name="unsafe.js", mime_type="text/javascript")
    analysis = bundle["parse"]["parsed"]["static_analysis"]
    assert analysis["execution_performed"] is False
    assert "fetch" in analysis["dangerous_capability_references"]
    assert "process" in analysis["dangerous_capability_references"]
    assert "pkg" in analysis["imports"]


def test_json_float_and_resource_bounds_reject_safely() -> None:
    with pytest.raises(Pass145Error) as float_error:
        parse_document(b'{"value": 0.1}', name="float.json", mime_type="application/json")
    assert float_error.value.code == "RUNTIME_REJECTED"
    with pytest.raises(Pass145Error) as size_error:
        parse_document(b"12345", name="large.txt", bounds=ParseBounds(max_bytes=4))
    assert size_error.value.code == "RESOURCE_BOUNDED"


def test_ingestion_validation_query_symbol_separation_and_replay(tmp_path: Path) -> None:
    with make_service(tmp_path) as service:
        result = ingest_symbol_fixture(service)
        assert result["status"] == "SOURCE_ADMITTED"
        assert result["validation"]["outcome"] == "VALIDATED"
        assert set(result["validation"]["layers"]) == {
            "V1_BYTE_INTEGRITY", "V2_FORMAT_INTEGRITY", "V3_STRUCTURAL_INTEGRITY",
            "V4_SCHEMA_INTEGRITY", "V5_PROVENANCE_INTEGRITY", "V6_SEMANTIC_INTEGRITY",
            "V7_RUNTIME_CONFORMANCE", "V8_CROSS_DOCUMENT_CONSISTENCY", "V9_RECEIPT_INTEGRITY",
        }
        assert all(v["executed"] and v["outcome"] == "VALIDATED" for v in result["validation"]["layers"].values())
        assert set(result["receipts"]) >= {
            "DOCUMENT_INGESTION_RECEIPT", "SOURCE_PRESERVATION_RECEIPT", "PARSE_RECEIPT"
        }
        raw = service.db.get_source(result["source_id"], include_raw=True)
        assert raw is not None and raw["raw_bytes"].startswith(b"# Canonical symbols")

        o_rows = service.search("O", symbol=True)["objects"]
        pi_rows = service.search("π", symbol=True)["objects"]
        assert o_rows and pi_rows
        assert {r["object_id"] for r in o_rows}.isdisjoint({r["object_id"] for r in pi_rows})

        root_before = service.db.database_root()
        query = service.query("Show every definition of the symbol O")
        evidence = query["answer"]["directly_retrieved_evidence"]
        assert evidence and all(r["object_type"] == "DEFINITION" for r in evidence)
        assert service.db.database_root() == root_before
        assert query["database_root_unchanged"] is True
        assert service.replay_ingestion(result["source_id"])["status"] == "REPLAY_VALIDATED"


def test_transaction_rollback_preserves_state_and_receipt_sequence(tmp_path: Path) -> None:
    with make_service(tmp_path) as service:
        before_root = service.db.database_root()
        before_sequence = int(service.db.meta("transaction_sequence") or 0)

        def fail(conn):
            conn.execute("INSERT INTO workspaces(workspace_id,name,description,version,owner_authority,default_policy_json,active_environment_id,dependencies_json,tags_json,workspace_hash72,created_at,modified_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                         ("WSP-FAIL", "fail", "", 1, "LOCAL_OWNER", "{}", None, "[]", "[]", "bad", "now", "now"))
            raise Pass145Error("DATABASE_COMMIT_FAILED", "intentional rollback", "TEST")

        with pytest.raises(Pass145Error):
            service.db.mutate("ROLLBACK_TEST", {"case": "intentional"}, fail)
        assert service.db.database_root() == before_root
        assert int(service.db.meta("transaction_sequence") or 0) == before_sequence
        assert service.db.conn.execute("SELECT COUNT(*) FROM workspaces WHERE workspace_id='WSP-FAIL'").fetchone()[0] == 0


def test_backup_verify_preview_and_restore(tmp_path: Path) -> None:
    db_path = tmp_path / "source.sqlite3"
    backup_path = tmp_path / "backup.hhs145.zip"
    restored_path = tmp_path / "restored.sqlite3"
    with HHS145Service(db_path) as service:
        result = ingest_symbol_fixture(service)
        source_root = result["source_root_hash72"]
        created = service.backup_create(backup_path)
        assert created["status"] == "BACKUP_CREATED"
        verified = service.backup_verify(backup_path)
        assert verified["ok"] is True
        preview = service.restore_preview(backup_path)
        assert preview["status"] == "RESTORE_PREVIEW_VALID"
    applied = HHS145Database.restore_apply(backup_path, restored_path)
    assert applied["status"] == "RESTORE_APPLIED"
    with HHS145Service(restored_path) as restored:
        assert restored.db.conn.execute("SELECT source_root_hash72 FROM sources").fetchone()[0] == source_root
        assert restored.db.verify_receipt_chain()["ok"] is True


def test_workspace_environment_branch_freeze_and_isolation(tmp_path: Path) -> None:
    with make_service(tmp_path) as service:
        workspaces = WorkspaceManager(service)
        environments = EnvironmentManager(service)
        workspace = workspaces.create("Enterprise")
        left = environments.create("Left", namespace="left")
        left_id = left["result"]["environment_id"]
        workspace_id = workspace["result"]["workspace_id"]
        workspaces.add_member(workspace_id, "ENVIRONMENT", left_id)
        branch = environments.clone(left_id, "Left Branch", namespace="left-branch", branch=True)
        branch_id = branch["created"]["result"]["environment_id"]
        assert environments.inspect(branch_id)["parent_environment_id"] == left_id
        environments.set_frozen(left_id, True)
        with pytest.raises(Pass145Error) as frozen:
            environments.add_member(left_id, "SCHEMA", "schema-1")
        assert frozen.value.code == "AUTHORITY_INSUFFICIENT"
        environments.set_frozen(left_id, False)
        environments.add_member(left_id, "SCHEMA", "schema-1")
        diff = environments.diff(left_id, branch_id)
        assert diff["only_left"]
        assert environments.inspect(branch_id)["namespace"] != environments.inspect(left_id)["namespace"]


def test_script_portability_capability_validation_and_execution(tmp_path: Path) -> None:
    with make_service(tmp_path) as service:
        environments = EnvironmentManager(service)
        scripts = ScriptWorkbench(service, environments)
        environment_id = environments.create("Scripts")["result"]["environment_id"]
        imported = scripts.import_script(
            "status-script", "HHS_COMMAND", "status\n",
            environment_id=environment_id,
            declared_capabilities=["DATABASE_READ"],
        )
        script_id = imported["result"]["script_id"]
        validation = scripts.validate(script_id)
        assert validation["result"]["validation_state"] == "VALIDATED"
        execution = scripts.execute(script_id)
        assert execution["result"]["status"] == "SCRIPT_EXECUTED"
        assert execution["result"]["output"][0]["result"]["ok"] is True

        unsafe = scripts.import_script("unsafe", "JAVASCRIPT", "fetch('https://example.invalid')")
        rejected = scripts.validate(unsafe["result"]["script_id"])
        assert rejected["result"]["validation_state"] == "RUNTIME_REJECTED"
        assert any(d["code"] == "CAPABILITY_UNDECLARED" for d in rejected["result"]["diagnostics"])
        with pytest.raises(Pass145Error) as execution_rejected:
            scripts.execute(unsafe["result"]["script_id"])
        assert execution_rejected.value.code == "RUNTIME_REJECTED"


def test_lvm_execution_nested_replay_and_cycle_rejection(tmp_path: Path) -> None:
    with make_service(tmp_path) as service:
        ingest_symbol_fixture(service)
        lvms = LVMEngine(service)
        child = lvms.create({
            "name": "child", "version": 1,
            "components": [{"id": "q", "type": "QUERY", "question": "Show every definition of the symbol O"}],
            "edges": [], "outputs": {"result": "q"},
            "resource_policy": {"max_recursive_depth": 8},
        })
        child_id = child["result"]["lvm_id"]
        parent = lvms.create({
            "name": "parent", "version": 1,
            "components": [{"id": "nested", "type": "NESTED_LVM", "lvm_id": child_id}],
            "edges": [], "outputs": {"result": "nested"},
            "resource_policy": {"max_recursive_depth": 8},
        })
        execution = lvms.execute(parent["result"]["lvm_id"], {"request": "definitions"})
        assert execution["result"]["status"] == "LVM_EXECUTION_COMPLETED"
        assert lvms.replay(execution["result"]["execution_id"])["status"] == "REPLAY_VALIDATED"

        with pytest.raises(Pass145Error) as cycle:
            lvms.create({
                "name": "bad-cycle", "components": [{"id": "a", "type": "CONST", "value": 1}],
                "edges": [{"from": "a", "to": "a"}],
            })
        assert cycle.value.code == "COMPOSITION_REJECTED"


def test_api_server_requires_authority_rejects_cross_origin_and_executes(tmp_path: Path) -> None:
    db_path = tmp_path / "api.sqlite3"
    token = "test-token"
    server = HHS145APIServer(("127.0.0.1", 0), db_path, token=token)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with pytest.raises(urllib.error.HTTPError) as unauthorized:
            urllib.request.urlopen(base + "/api/v1/status", timeout=5)
        assert unauthorized.value.code == 401

        bad_origin = urllib.request.Request(base + "/api/v1/status", headers={"Authorization": f"Bearer {token}", "Origin": "https://evil.invalid"})
        with pytest.raises(urllib.error.HTTPError) as forbidden:
            urllib.request.urlopen(bad_origin, timeout=5)
        assert forbidden.value.code == 403

        body = json.dumps({"text": "O denotes the HHS operator.", "name": "api.txt", "namespace": "api"}).encode()
        request = urllib.request.Request(base + "/api/v1/ingest", data=body, method="POST", headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=10) as response:
            admitted = json.loads(response.read())
        assert admitted["status"] == "SOURCE_ADMITTED"

        status_request = urllib.request.Request(base + "/api/v1/status", headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(status_request, timeout=5) as response:
            status = json.loads(response.read())
        assert status["ok"] is True and status["counts"]["sources"] == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_cli_public_surface_and_stable_failure_exit(tmp_path: Path) -> None:
    db = tmp_path / "cli.sqlite3"
    document = tmp_path / "source.md"
    document.write_text("O denotes the HHS operator. π denotes the circular constant.\n", encoding="utf-8")
    executable = Path(__file__).parents[1] / "hhs"
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).parents[1])}

    status = subprocess.run([str(executable), "--db", str(db), "--format", "json", "status"], cwd=executable.parent, env=env, text=True, capture_output=True, timeout=30)
    assert status.returncode == 0, status.stderr
    assert json.loads(status.stdout)["ok"] is True

    ingest = subprocess.run([str(executable), "--db", str(db), "--format", "json", "ingest", "file", str(document), "--namespace", "cli"], cwd=executable.parent, env=env, text=True, capture_output=True, timeout=30)
    assert ingest.returncode == 0, ingest.stderr
    assert json.loads(ingest.stdout)["status"] == "SOURCE_ADMITTED"

    invalid = subprocess.run([str(executable), "--db", str(db), "--format", "json", "validate", "source", "SRC-MISSING"], cwd=executable.parent, env=env, text=True, capture_output=True, timeout=30)
    assert invalid.returncode != 0
    assert json.loads(invalid.stderr)["error_code"] == "PROVENANCE_INCOMPLETE"


def test_workspace_api_collection_and_extension_governance(tmp_path: Path) -> None:
    with make_service(tmp_path) as service:
        workspaces = WorkspaceManager(service)
        api = APIWorkbench(service)
        extensions = ExtensionManager(service)
        workspace = workspaces.create("Platform")
        collection = api.create_collection("status", {
            "requests": [{"name": "status", "method": "GET", "url": "http://127.0.0.1:8765/api/v1/status"}],
            "capabilities": ["LOCAL_API"],
        })
        generated = api.generate_client(collection["result"]["collection_id"], "status", language="HHS_COMMAND")
        assert generated["secrets_embedded"] is False
        workspaces.add_member(workspace["result"]["workspace_id"], "API_COLLECTION", collection["result"]["collection_id"])

        manifest = {
            "identity": "org.hhs.fixture", "version": "1.0.0", "publisher": "test",
            "source_hash": "0" * 64, "requested_capabilities": [],
            "supported_runtime_versions": ["145"], "entrypoints": ["parse"],
            "schemas": [], "migrations": [], "tests": ["fixture"],
            "uninstall_behavior": "REMOVE_ADAPTER_KEEP_EVIDENCE",
        }
        installed = extensions.install(manifest)
        assert installed["result"]["status"] == "EXTENSION_ADMITTED"
        with pytest.raises(Pass145Error) as direct_db:
            extensions.install({**manifest, "identity": "org.hhs.bad", "direct_canonical_database_access": True})
        assert direct_db.value.code == "CAPABILITY_OVERBROAD"


def test_receipt_tamper_is_detected(tmp_path: Path) -> None:
    with make_service(tmp_path) as service:
        ingest_symbol_fixture(service)
        row = service.db.conn.execute("SELECT receipt_id,receipt_json FROM receipts ORDER BY sequence LIMIT 1").fetchone()
        payload = json.loads(row["receipt_json"])
        payload["operation"] = "FORGED_OPERATION"
        service.db.conn.execute("UPDATE receipts SET receipt_json=? WHERE receipt_id=?", (json.dumps(payload), row["receipt_id"]))
        verification = service.db.verify_receipt_chain()
        assert verification["ok"] is False
        assert verification["failures"]


def test_android_projection_is_governed_and_build_failure_is_explicit(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    android = root / "android" / "pass145"
    bridge = (android / "app/src/main/java/org/hhs/pass145/HhsBridge.java").read_text(encoding="utf-8")
    activity = (android / "app/src/main/java/org/hhs/pass145/MainActivity.java").read_text(encoding="utf-8")
    network = (android / "app/src/main/res/xml/network_security_config.xml").read_text(encoding="utf-8")
    assert "Authorization" in bridge and "Bearer" in bridge
    assert "setAllowFileAccess(false)" in activity
    assert "127.0.0.1" in network
    assert "cleartextTrafficPermitted=\"false\"" in network

    env = {k: v for k, v in os.environ.items() if k not in {"ANDROID_HOME", "ANDROID_SDK_ROOT"}}
    proc = subprocess.run([str(android / "build_android.sh")], cwd=android, env=env, text=True, capture_output=True, timeout=30)
    assert proc.returncode != 0
    receipt = root / "release_artifacts" / "pass145" / "android" / "APK_BUILD_RECEIPT.json"
    assert receipt.is_file()
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    assert payload["status"] == "APK_BUILD_FAILED"
    assert payload["fabricated_apk"] is False


def test_inherited_runtime_database_bridge_is_real_and_retrievable(tmp_path: Path) -> None:
    from hhs_database_integration_layer_v1 import HHSRuntimeDatabaseBridgeV1

    receipts = [
        {"phase": 0, "operation": "LOAD", "receipt_hash72": "H72N-fixture-0"},
        {"phase": 1, "operation": "VALIDATE", "receipt_hash72": "H72N-fixture-1"},
    ]
    with HHSRuntimeDatabaseBridgeV1(tmp_path / "bridge.sqlite3") as bridge:
        stored = bridge.store_trace(receipts, program_name="BRIDGE_TEST", metadata={"source": "pytest"})
        loaded = bridge.load_trace(stored.trace_hash72)
        assert loaded is not None
        assert loaded["program_name"] == "BRIDGE_TEST"
        assert loaded["receipts"] == receipts
        assert loaded["receipt_count"] == 2
        assert bridge.quarantine_report()["database_integrity"]["ok"] is True


def test_contradictions_are_preserved_and_retrievable(tmp_path: Path) -> None:
    with make_service(tmp_path) as service:
        service.ingest_bytes(b"The runtime is deterministic.", name="a.md", mime_type="text/markdown", namespace="conflict")
        second = service.ingest_bytes(b"The runtime is not deterministic.", name="b.md", mime_type="text/markdown", namespace="conflict")
        assert second["contradictions"]["status"] == "CONTRADICTIONS_PRESERVED"
        result = service.search("", object_type="CONTRADICTION", namespace="conflict")
        assert result["result_count"] == 1
        contradiction = result["objects"][0]
        assert contradiction["object_type"] == "CONTRADICTION"
