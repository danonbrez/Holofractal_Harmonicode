from __future__ import annotations

import hashlib
import sqlite3
import sys
import threading
import types
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi import APIRouter

from hhs_backend.runtime.immutable_agent_sql_index_v1 import (
    HHSImmutableAgentAuditReader,
    HHSImmutableAgentSQLIndex,
)


def test_protected_append_only_narrative_and_chains(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    path = tmp_path / "agent.sqlite3"
    index = HHSImmutableAgentSQLIndex(path, agent_id="test-agent")
    assert index.initialize(boot_id="boot-1")["counts"]["constraints"] == 5
    constraint = index.append_constraint("RULE", "Repository mutation requires a registered contract.", "TEST", "rule-1", "A3")
    receipt = index.append_agent_event("GOAL_REGISTERED", {"goal_id": "g1", "target_hash72": "H72-t", "status": "ACTIVE"}, constraint_ids=[constraint["constraint_id"]])
    assert receipt["narrative_access"] == "DENIED_TO_GENERATING_API_TOOLS"
    assert index._protected_read_probe() is True
    assert index.integrity_check()["ok"] is True
    assert oct(path.stat().st_mode & 0o777) == "0o600"

    raw = sqlite3.connect(path)
    with pytest.raises(sqlite3.DatabaseError, match="IMMUTABLE_TABLE_DELETE_DENIED"):
        raw.execute("DELETE FROM narrative_log")
    with pytest.raises(sqlite3.DatabaseError, match="IMMUTABLE_TABLE_UPDATE_DENIED"):
        raw.execute("UPDATE agent_events SET event_type='tampered'")
    raw.close()

    token = "audit"
    monkeypatch.setenv("HHS_AGENT_AUDIT_TOKEN_SHA256", hashlib.sha256(token.encode()).hexdigest())
    reader = HHSImmutableAgentAuditReader.open(path, token)
    rows = reader.narratives()
    assert rows[0]["privacy_class"] == "PROTECTED_AUDIT_ONLY"
    assert reader.verify_chains()["ok"] is True
    with pytest.raises(sqlite3.OperationalError):
        reader._conn.execute("DELETE FROM narrative_log")
    reader.close()
    index.close()


def test_api_geometry_and_constraint_bindings(tmp_path: Path):
    index = HHSImmutableAgentSQLIndex(tmp_path / "api.sqlite3")
    index.initialize()
    router = APIRouter(tags=["cognition"])

    @router.post("/api/runtime/cognition/task")
    def task(payload: dict) -> dict:
        return payload

    result = index.register_api_routes(router.routes)
    assert result["surfaces_inserted"] == 1
    status = index.status()
    assert status["counts"]["api_surfaces"] == 1
    assert status["counts"]["constraint_bindings"] == 5
    assert status["authority_boundary"]["narrative_api_read_surface"] == "ABSENT"
    assert not hasattr(index, "read_narrative")
    assert not hasattr(index, "delete_narrative")
    index.close()


def test_pass145_backfill(tmp_path: Path):
    source = tmp_path / "p145.sqlite3"
    conn = sqlite3.connect(source)
    conn.executescript('''
    CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    INSERT INTO meta VALUES('schema_id','HHS_PASS145_KNOWLEDGE_DATABASE');
    INSERT INTO meta VALUES('schema_version','1.4.0');
    INSERT INTO meta VALUES('receipt_tip','RCP-test');
    CREATE TABLE semantic_rules(rule_id TEXT PRIMARY KEY,rule_kind TEXT,rule_json TEXT,rule_hash72 TEXT);
    CREATE TABLE semantic_propositions(proposition_id TEXT PRIMARY KEY,source_expression TEXT,primary_class TEXT,authority_level TEXT,proposition_hash72 TEXT);
    CREATE TABLE objects(object_id TEXT PRIMARY KEY,object_type TEXT,exact_text TEXT,normalized_text TEXT,authority_level TEXT,object_hash72 TEXT);
    CREATE TABLE security_boundary_contracts(contract_id TEXT PRIMARY KEY,operation TEXT,contract_hash72 TEXT,status TEXT);
    INSERT INTO semantic_rules VALUES('r1','INVARIANT','{"canonical_text":"O differs from pi","authority_level":"A3"}','H72-r');
    INSERT INTO semantic_propositions VALUES('p1','A=P^2=B','CONSTRAINT','A3','H72-p');
    INSERT INTO objects VALUES('o1','CONTRACT','Mutation requires validation',NULL,'A3','H72-o');
    INSERT INTO security_boundary_contracts VALUES('c1','repo.modify','H72-c','REGISTERED');
    ''')
    conn.close()
    index = HHSImmutableAgentSQLIndex(tmp_path / "index.sqlite3")
    index.initialize()
    result = index.backfill_pass145_constraints(source)
    assert result["inserted_constraints"] == 4
    assert index.status()["counts"]["database_snapshots"] == 1
    index.close()


def test_concurrent_event_appends_are_serialized(tmp_path: Path):
    index = HHSImmutableAgentSQLIndex(tmp_path / "concurrent.sqlite3")
    index.initialize()
    errors = []
    def worker(i):
        try:
            index.append_agent_event("TEST_EVENT", {"status": "OK", "ordinal": i})
        except Exception as exc:
            errors.append(exc)
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(16)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert not errors
    assert index.status()["counts"]["agent_events"] == 16
    token = "audit"
    import os
    os.environ["HHS_AGENT_AUDIT_TOKEN_SHA256"] = hashlib.sha256(token.encode()).hexdigest()
    reader = HHSImmutableAgentAuditReader.open(index.path, token)
    assert reader.verify_chains()["ok"] is True
    reader.close(); index.close()


@dataclass
class Memory:
    memory_id: str = "m1"
    memory_type: str = "symbolic"
    hash72: str = "H72-m"

class Semantic:
    def ingest_memory(self, *args, **kwargs): return Memory(memory_type=kwargs.get("memory_type", "symbolic"))
    def link_memories(self, source_memory_id, target_memory_id, relationship):
        return types.SimpleNamespace(link_id="l1", source_memory_id=source_memory_id, target_memory_id=target_memory_id, relationship=relationship)

class Cognition:
    def initialize(self): return self.status()
    def status(self): return {"layers": {}, "authority_boundary": {}}
    def process_packet(self, packet, emission=None): return {"status": "OK", "replay_id": "rp1"}
    def create_goal(self, objective, target_hash72="H72-t", **kwargs): return {"goal_id": "g1", "target_hash72": target_hash72}
    def create_task(self, objective, **kwargs): return {"task_id": "t1", "goal_id": "g1"}
    def execute_task(self, task_id): return {"task_id": task_id, "status": "COMPLETED"}
    def adapt_goal(self, goal_id, horizon=10): return {"goal_id": goal_id}
    def execute_research(self, objective, **kwargs): return {"task_id": "r1", "status": "COMPLETED"}
    def execute_toolchain(self, originating_task, graph_seed): return {"toolchain_id": "tc1", "status": "COMPLETED"}
    def generate_prediction(self, horizon=10): return {"prediction": True}
    def create_consensus_proposal(self, proposal_type, target_hash72, **kwargs): return {"proposal_id": "cp1"}
    def submit_consensus_vote(self, proposal_id, node_id, approved, **kwargs): return {"vote": True}
    def collect_consensus(self, proposal_id): return {"status": "QUORUM"}
    def register_multinode_goal(self, originating_node, objective, target_hash72, **kwargs): return {"goal_id": "mg1"}
    def synchronize_multinode_goals(self): return {"synchronized": []}


def test_hook_exposes_summary_not_narrative(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    sem_module = types.ModuleType("hhs_backend.runtime.runtime_semantic_memory_engine")
    semantic = Semantic()
    sem_module.runtime_semantic_memory_engine = semantic
    monkeypatch.setitem(sys.modules, sem_module.__name__, sem_module)
    routes_module = types.ModuleType("hhs_backend.api.runtime_routes")
    routes_module.router = APIRouter()
    monkeypatch.setitem(sys.modules, routes_module.__name__, routes_module)

    import hhs_backend.runtime.immutable_agent_index_hooks_v1 as hooks
    hooks._SEMANTIC_HOOKED = False
    index = HHSImmutableAgentSQLIndex(tmp_path / "hook.sqlite3")
    cognition = Cognition()
    hooks.install_agent_index_hooks(cognition, index=index)
    cognition.initialize()
    semantic.ingest_memory(memory_type="symbolic", semantic_text="registered contract", hash72="H72-m")
    cognition.create_goal("preserve constraints")
    cognition.create_task("register contract")
    cognition.execute_task("t1")
    status = cognition.status()["immutable_agent_sql_index"]
    assert status["counts"]["agent_events"] >= 5
    assert status["authority_boundary"]["writer_can_read_protected_narrative"] is False
    assert cognition.status()["authority_boundary"]["protected_narrative_read"] == "DENIED_TO_GENERATING_API_TOOLS"
    assert "narratives" not in status
    index.close()
