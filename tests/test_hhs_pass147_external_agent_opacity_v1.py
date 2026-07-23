from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass147.api import HHS147PublicServer
from hhs_runtime.pass147.docs import PUBLIC_DOCUMENTS
from hhs_runtime.pass147.service import HHS147Service


@pytest.fixture(scope="module")
def system(tmp_path_factory):
    root = tmp_path_factory.mktemp("pass147")
    db = root / "system.sqlite3"
    with HHS147Service(db) as service:
        owner = service.security.bootstrap_local_owner("Pass147 Test Owner")
        owner_creds = (owner["result"]["identity_id"], owner["result"]["grant_id"], owner["authentication_token"])
        service.public_registry.synchronize()
        docs = service.security.construct_path(owner_creds[0], owner_creds[1], owner_creds[2], "PUBLIC_DOC_INSTALL", {"classification": "INTERNAL"})
        service.security.execute_path(docs["result"]["contract_id"], owner_creds[0], owner_creds[2])
        agent = service.create_external_agent(*owner_creds, "Pass147 External Model")
        profile = agent["profile"]
        agent_creds = (profile["identity_id"], profile["grant_id"], agent["authentication_token"])
    return {"db": db, "owner": owner_creds, "agent": agent_creds, "profile": profile}


def test_version_and_schema(system):
    with HHS147Service(system["db"]) as service:
        assert service.version()["pass_id"] == "HHS-P147"
        # Pass 147 remains operational under the additive Pass 148 schema.
        schema_version = tuple(int(part) for part in service.db.meta("schema_version").split("."))
        assert schema_version >= (1, 3, 0)
        assert service.db.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='public_capabilities'").fetchone()
        assert service.version()["rule"]["privileged_internal_access"] == 0


def test_public_registry_is_complete_and_has_no_privileged_edges(system):
    with HHS147Service(system["db"]) as service:
        audit = service.public_registry.audit()
        assert audit["closed"] is True
        assert audit["potential_capability_complete"] is True
        assert audit["privileged_internal_access"] == 0
        assert audit["privileged_bypass_surfaces"] == []
        assert audit["total"] >= 100


def test_registry_sync_is_canonical_and_receipted(system):
    with HHS147Service(system["db"]) as service:
        result = service.public_registry.synchronize()
        assert result["result"]["status"] == "PUBLIC_CAPABILITY_CATALOG_SYNCHRONIZED"
        assert result["receipt_id"]
        count = service.db.conn.execute("SELECT COUNT(*) FROM public_capabilities WHERE active=1").fetchone()[0]
        assert count == result["result"]["count"]


def test_command_contract_is_inspectable(system):
    with HHS147Service(system["db"]) as service:
        result = service.public_registry.describe(["ingest", "file"])
        capability = result["capability"]
        assert capability["classification"] == "PUBLICLY_REQUESTABLE_THROUGH_BOUNDARY"
        assert "INGEST" in capability["capabilities"]
        assert capability["mutating"] is True
        assert result["execution_requires_boundary"] is True


def test_api_and_schema_contracts_are_inspectable(system):
    with HHS147Service(system["db"]) as service:
        api = service.public_registry.api_describe("/api/v1/query")
        assert api["count"] == 1
        assert api["operations"][0]["method"] == "POST"
        schema = service.public_registry.schema_describe("external-agent-profile")
        assert schema["definition"]["properties"]["privileged_internal_access"]["const"] == 0


def test_runtime_symbol_and_float_authority(system):
    from hhs_runtime.pass147.registry import runtime_types
    result = runtime_types()
    assert result["O_distinct_from_pi"] is True
    assert result["canonical_float_authority"] is False
    float_type = next(x for x in result["types"] if x["name"] == "IEEE_FLOAT_PROJECTION")
    assert float_type["canonical_authority"] is False


def test_public_documentation_is_local_versioned_evidence(system):
    with HHS147Service(system["db"]) as service:
        rows = service.db.conn.execute("SELECT source_id,source_name,raw_sha256,immutable FROM sources WHERE namespace='hhs-public-docs-v147' ORDER BY source_name").fetchall()
        assert len(rows) == len(PUBLIC_DOCUMENTS)
        assert all(row["immutable"] == 1 for row in rows)
        query = service.query_public_docs("What is external-agent opacity?")
        assert query["documentation_namespace"] == "hhs-public-docs-v147"
        assert query["answer"]["directly_retrieved_evidence"]


def test_public_discovery_is_boundary_constructed(system):
    identity, grant, token = system["agent"]
    with HHS147Service(system["db"]) as service:
        constructed = service.security.construct_path(identity, grant, token, "PUBLIC_DISCOVER", {"action": "audit", "classification": "INTERNAL"})
        closed = service.security.execute_path(constructed["result"]["contract_id"], identity, token)
        assert constructed["result"]["minimum_capabilities"] == ["DATABASE_READ", "PATH_EXECUTION", "PUBLIC_DISCOVERY"]
        assert closed["result"]["status"] == "BOUNDARY_PATH_CLOSED"
        assert closed["result"]["result"]["privileged_internal_access"] == 0


def test_external_agent_default_grant_has_no_privileged_admin_or_network(system):
    profile = system["profile"]
    assert profile["privileged_internal_access"] == 0
    assert profile["procedural_external"] is True
    assert "SECURITY_ADMIN" not in profile["capabilities"]
    assert "NETWORK_SEND" not in profile["capabilities"]
    assert "NETWORK_RECEIVE" not in profile["capabilities"]


def test_external_agent_can_discover_from_public_primitives(system):
    identity, grant, token = system["agent"]
    with HHS147Service(system["db"]) as service:
        result = service.external_execute(identity, grant, token, ["surface", "audit"])
        assert result["operation"] == "PUBLIC_DISCOVER"
        assert result["privileged_internal_access"] == 0
        assert result["execution"]["result"]["closed"] is True


def test_external_agent_can_query_runtime_through_inherited_boundary(system):
    identity, grant, token = system["agent"]
    with HHS147Service(system["db"]) as service:
        result = service.external_execute(identity, grant, token, ["query", "What is external-agent opacity?", "--namespace", "hhs-public-docs-v147"])
        assert result["operation"] == "RUN_CLI_COMMAND"
        assert result["construction"]["minimum_capabilities"] == ["DATABASE_READ", "PATH_EXECUTION", "QUERY"]
        assert result["execution"]["status"] == "BOUNDARY_PATH_CLOSED"
        assert result["execution"]["result"]["answer"]["directly_retrieved_evidence"]


def test_external_agent_can_query_documentation_through_dedicated_boundary(system):
    identity, grant, token = system["agent"]
    with HHS147Service(system["db"]) as service:
        result = service.external_execute(identity, grant, token, ["docs", "query", "procedural", "externality"])
        assert result["operation"] == "PUBLIC_DOC_QUERY"
        assert result["execution"]["result"]["source_authority"] == "VERSIONED_LOCAL_CORPUS"


def test_external_agent_shell_shortcut_is_rejected_before_path_creation(system):
    identity, grant, token = system["agent"]
    with HHS147Service(system["db"]) as service:
        before = service.db.conn.execute("SELECT COUNT(*) FROM security_boundary_contracts").fetchone()[0]
        with pytest.raises(Pass145Error) as exc:
            service.external_execute(identity, grant, token, ["shell"])
        after = service.db.conn.execute("SELECT COUNT(*) FROM security_boundary_contracts").fetchone()[0]
        assert exc.value.code == "PRIVILEGED_INTERNAL_ACCESS_PROHIBITED"
        assert after == before


def test_external_agent_security_admin_request_is_rejected(system):
    with HHS147Service(system["db"]) as service:
        with pytest.raises(Pass145Error) as exc:
            service.create_external_agent(*system["owner"], "Overbroad Agent", capabilities=["SECURITY_ADMIN"])
        assert exc.value.code == "PRIVILEGED_INTERNAL_ACCESS_PROHIBITED"


def test_unknown_public_primitive_is_explicit_not_internal_fallback(system):
    with HHS147Service(system["db"]) as service:
        with pytest.raises(Pass145Error) as exc:
            service.public_registry.describe(["internal-kernel", "execute"])
        assert exc.value.code == "PUBLIC_PRIMITIVE_MISSING"


def test_boundary_explanation_is_public_and_nonexecuting(system):
    identity, grant, token = system["agent"]
    with HHS147Service(system["db"]) as service:
        built = service.security.construct_path(identity, grant, token, "PUBLIC_DISCOVER", {"action": "boundary", "target": "RUN_CLI_COMMAND", "classification": "INTERNAL"})
        closed = service.security.execute_path(built["result"]["contract_id"], identity, token)
        result = closed["result"]["result"]
        assert result["operation"] == "RUN_CLI_COMMAND"
        assert result["path_constructed_before_execution"] is True


def test_receipt_chain_remains_valid(system):
    with HHS147Service(system["db"]) as service:
        check = service.db.verify_receipt_chain()
        assert check["ok"] is True
        assert check["count"] > 0



def test_query_script_lvm_replay_uses_semantic_projection(system):
    from hhs_runtime.pass145.workbench import EnvironmentManager, ScriptWorkbench, LVMEngine

    with HHS147Service(system["db"]) as service:
        env = EnvironmentManager(service).create("Pass147 Replay Environment", namespace="pass147-replay")
        environment_id = env["result"]["environment_id"]
        service.ingest_bytes(
            b"External-agent opacity requires public procedural construction and replayable receipts.",
            name="replay-source.md",
            mime_type="text/markdown",
            namespace="pass147-replay",
        )
        scripts = ScriptWorkbench(service)
        imported = scripts.import_script(
            "Replay Query",
            "HHS_COMMAND",
            "query external-agent opacity\n",
            environment_id=environment_id,
            declared_capabilities=["DATABASE_READ"],
        )
        script_id = imported["result"]["script_id"]
        assert scripts.validate(script_id)["result"]["validation_state"] == "VALIDATED"
        lvms = LVMEngine(service)
        created = lvms.create(
            {
                "name": "Pass147 Query Replay LVM",
                "version": 1,
                "components": [{"id": "query_script", "type": "SCRIPT", "script_id": script_id, "input": "$input"}],
                "edges": [],
                "outputs": {"result": "$query_script"},
                "resource_policy": {"max_recursive_depth": 8},
                "failure_policy": "HALT_AND_RECEIPT",
                "replay_policy": "DETERMINISTIC",
                "capabilities": ["NATIVE_RUNTIME", "DATABASE_READ", "DATABASE_WRITE"],
            },
            environment_id=environment_id,
        )
        execution = lvms.execute(created["result"]["lvm_id"], {})
        replay = lvms.replay(execution["result"]["execution_id"])
        assert replay["status"] == "REPLAY_VALIDATED"
        assert replay["execution_hash_equal"] is True

def _request(url: str, token: str | None = None, data: dict | None = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    raw = None
    method = "GET"
    if data is not None:
        raw = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
        method = "POST"
    req = urllib.request.Request(url, data=raw, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.status, json.loads(response.read())


def test_authenticated_public_api_and_agent_execution(system):
    owner_identity, owner_grant, owner_token = system["owner"]
    server = HHS147PublicServer(("127.0.0.1", 0), system["db"], token="api-test-token", identity_id=owner_identity, grant_id=owner_grant, identity_token=owner_token)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with pytest.raises(urllib.error.HTTPError) as exc:
            _request(base + "/api/v1/public/capabilities")
        assert exc.value.code == 401
        status, catalog = _request(base + "/api/v1/public/capabilities", "api-test-token")
        assert status == 200 and catalog["count"] >= 100
        aid, gid, tok = system["agent"]
        status, executed = _request(base + "/api/v1/public/agent/execute", "api-test-token", {"identity_id": aid, "grant_id": gid, "identity_token": tok, "argv": ["surface", "audit"]})
        assert status == 200
        assert executed["privileged_internal_access"] == 0
        assert executed["execution"]["status"] == "BOUNDARY_PATH_CLOSED"
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)
