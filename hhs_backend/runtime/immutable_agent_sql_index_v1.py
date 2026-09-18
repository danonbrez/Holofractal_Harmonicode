"""Append-only SQL evidence index for HHS agent activity.

The protected narrative is an execution-derived decision summary, not raw
private chain-of-thought. Runtime API tools receive only the writer capability;
no HTTP narrative read or delete surface is defined here.
"""
from __future__ import annotations

import contextlib
import functools
import hashlib
import hmac
import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

VERSION = "HHS_IMMUTABLE_AGENT_SQL_INDEX_V1"
SCHEMA_ID = "HHS_IMMUTABLE_AGENT_SQL_INDEX"
SCHEMA_VERSION = "1.0.0"
DEFAULT_DB_PATH = "data/runtime/hhs_agent_immutable_index.sqlite3"
IMMUTABLE_TABLES = (
    "database_layers", "database_snapshots", "api_surfaces", "constraints",
    "constraint_bindings", "agent_sessions", "agent_events", "narrative_log",
)


def _data(value: Any, depth: int = 0) -> Any:
    if depth > 4:
        return "<depth-bounded>"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value if len(value) <= 512 else {"text_hash72": h72("bounded-text", value), "length": len(value)}
    if isinstance(value, Mapping):
        items = sorted(value.items(), key=lambda item: str(item[0]))
        out = {str(k): _data(v, depth + 1) for k, v in items[:96]}
        if len(items) > 96:
            out["__remaining_keys__"] = len(items) - 96
        return out
    if isinstance(value, (list, tuple, set, frozenset)):
        values = list(value)
        out = [_data(item, depth + 1) for item in values[:96]]
        if len(values) > 96:
            out.append({"remaining_items": len(values) - 96})
        return out
    if hasattr(value, "model_dump"):
        return _data(value.model_dump(), depth + 1)
    if hasattr(value, "__dict__"):
        return _data(vars(value), depth + 1)
    return str(value)


def cjson(value: Any) -> str:
    return json.dumps(_data(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def h72(domain: str, value: Any) -> str:
    digest = hashlib.sha384(f"{domain}\n{cjson(value)}".encode()).hexdigest()[:72]
    return f"H72-{digest}"


def sid(prefix: str, domain: str, value: Any) -> str:
    return f"{prefix}-{h72(domain, value)[4:28]}"


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


SCHEMA_SQL = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS database_layers(
 layer_id TEXT PRIMARY KEY,layer_name TEXT NOT NULL,layer_kind TEXT NOT NULL,
 source_module TEXT NOT NULL,storage_class TEXT NOT NULL,authority_class TEXT NOT NULL,
 source_locator_hash72 TEXT NOT NULL,schema_id TEXT NOT NULL,schema_version TEXT NOT NULL,
 details_json TEXT NOT NULL,layer_hash72 TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL);
CREATE UNIQUE INDEX IF NOT EXISTS idx_db_layer_identity
 ON database_layers(layer_name,source_module,schema_version);
CREATE TABLE IF NOT EXISTS database_snapshots(
 snapshot_id TEXT PRIMARY KEY,layer_id TEXT NOT NULL,snapshot_sequence INTEGER NOT NULL,
 state_root_hash72 TEXT NOT NULL,record_count INTEGER NOT NULL,details_json TEXT NOT NULL,
 prev_snapshot_hash72 TEXT NOT NULL,snapshot_hash72 TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL,
 FOREIGN KEY(layer_id) REFERENCES database_layers(layer_id) ON DELETE RESTRICT,
 UNIQUE(layer_id,snapshot_sequence));
CREATE TABLE IF NOT EXISTS api_surfaces(
 surface_id TEXT PRIMARY KEY,path_template TEXT NOT NULL,method TEXT NOT NULL,route_name TEXT NOT NULL,
 endpoint_module TEXT NOT NULL,endpoint_qualname TEXT NOT NULL,tags_json TEXT NOT NULL,
 request_schema_json TEXT NOT NULL,response_schema_json TEXT NOT NULL,authority_class TEXT NOT NULL,
 geometry_hash72 TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_api_surface_path ON api_surfaces(path_template,method);
CREATE TABLE IF NOT EXISTS constraints(
 constraint_id TEXT PRIMARY KEY,constraint_kind TEXT NOT NULL,canonical_text TEXT NOT NULL,
 source_type TEXT NOT NULL,source_reference TEXT NOT NULL,authority_level TEXT NOT NULL,
 parent_constraint_id TEXT,provenance_json TEXT NOT NULL,constraint_hash72 TEXT NOT NULL UNIQUE,
 created_at TEXT NOT NULL,
 FOREIGN KEY(parent_constraint_id) REFERENCES constraints(constraint_id) ON DELETE RESTRICT);
CREATE TABLE IF NOT EXISTS constraint_bindings(
 binding_id TEXT PRIMARY KEY,constraint_id TEXT NOT NULL,surface_id TEXT,database_layer_id TEXT,
 binding_role TEXT NOT NULL,binding_json TEXT NOT NULL,binding_hash72 TEXT NOT NULL UNIQUE,
 created_at TEXT NOT NULL,
 FOREIGN KEY(constraint_id) REFERENCES constraints(constraint_id) ON DELETE RESTRICT,
 FOREIGN KEY(surface_id) REFERENCES api_surfaces(surface_id) ON DELETE RESTRICT,
 FOREIGN KEY(database_layer_id) REFERENCES database_layers(layer_id) ON DELETE RESTRICT);
CREATE TABLE IF NOT EXISTS agent_sessions(
 session_id TEXT PRIMARY KEY,agent_id TEXT NOT NULL,boot_id TEXT NOT NULL,authority_class TEXT NOT NULL,
 session_json TEXT NOT NULL,session_hash72 TEXT NOT NULL UNIQUE,started_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS agent_events(
 event_id TEXT PRIMARY KEY,session_id TEXT NOT NULL,sequence INTEGER NOT NULL UNIQUE,
 event_type TEXT NOT NULL,source_surface_id TEXT,input_hash72 TEXT NOT NULL,output_hash72 TEXT NOT NULL,
 constraint_set_hash72 TEXT NOT NULL,facts_json TEXT NOT NULL,prev_event_hash72 TEXT NOT NULL,
 event_hash72 TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL,
 FOREIGN KEY(session_id) REFERENCES agent_sessions(session_id) ON DELETE RESTRICT,
 FOREIGN KEY(source_surface_id) REFERENCES api_surfaces(surface_id) ON DELETE RESTRICT);
CREATE TABLE IF NOT EXISTS narrative_log(
 narrative_id TEXT PRIMARY KEY,event_id TEXT NOT NULL UNIQUE,sequence INTEGER NOT NULL UNIQUE,
 narrative_class TEXT NOT NULL,privacy_class TEXT NOT NULL,narrative_text TEXT NOT NULL,
 prev_narrative_hash72 TEXT NOT NULL,narrative_hash72 TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL,
 FOREIGN KEY(event_id) REFERENCES agent_events(event_id) ON DELETE RESTRICT);
"""


def _triggers() -> str:
    return "\n".join(
        f"""CREATE TRIGGER IF NOT EXISTS immut_{t}_u BEFORE UPDATE ON {t} BEGIN
        SELECT RAISE(ABORT,'IMMUTABLE_TABLE_UPDATE_DENIED:{t}'); END;
        CREATE TRIGGER IF NOT EXISTS immut_{t}_d BEFORE DELETE ON {t} BEGIN
        SELECT RAISE(ABORT,'IMMUTABLE_TABLE_DELETE_DENIED:{t}'); END;"""
        for t in IMMUTABLE_TABLES
    )


class HHSImmutableAgentSQLIndex:
    """Writer-only capability. It exposes no narrative read/update/delete method."""

    def __init__(self, path: str | Path | None = None, *, agent_id: str = "hhs-live-cognition") -> None:
        self.path = Path(path or os.getenv("HHS_AGENT_INDEX_DB", DEFAULT_DB_PATH)).expanduser().resolve()
        self.agent_id = agent_id
        self._lock = threading.RLock()
        self._conn: sqlite3.Connection | None = None
        self._session_id: str | None = None
        self._initialized = False

    def initialize(self, *, boot_id: str = "runtime-boot") -> dict[str, Any]:
        with self._lock:
            if self._initialized:
                return self.status()
            self.path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.path, isolation_level=None, check_same_thread=False, timeout=30)
            conn.row_factory = sqlite3.Row
            for pragma in ("foreign_keys=ON", "journal_mode=WAL", "synchronous=FULL", "trusted_schema=OFF", "busy_timeout=30000"):
                conn.execute(f"PRAGMA {pragma}")
            conn.executescript(SCHEMA_SQL)
            conn.executescript(_triggers())
            with contextlib.suppress(OSError):
                os.chmod(self.path, 0o600)
            self._conn = conn
            conn.execute("BEGIN IMMEDIATE")
            for key, value in {
                "schema_id": SCHEMA_ID, "schema_version": SCHEMA_VERSION,
                "event_sequence": "0", "event_tip": "H72-EVENT-GENESIS",
                "narrative_sequence": "0", "narrative_tip": "H72-NARRATIVE-GENESIS",
                "database_layer_count": "0", "database_snapshot_count": "0",
                "api_surface_count": "0", "constraint_count": "0", "constraint_binding_count": "0",
                "event_count": "0", "narrative_count": "0",
            }.items():
                conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES(?,?)", (key, value))
            conn.execute("COMMIT")
            conn.set_authorizer(self._authorizer)
            identity = {
                "agent_id": self.agent_id, "boot_id": boot_id,
                "authority_class": "OBSERVE_INDEX_NARRATE_NO_VM81_MUTATION",
                "narrative_policy": "DECISION_NARRATIVE_NOT_PRIVATE_CHAIN_OF_THOUGHT",
                "started_at": now(), "nonce": time.time_ns(),
            }
            self._session_id = sid("AGS", "agent-session-id", identity)
            conn.execute(
                "INSERT INTO agent_sessions VALUES(?,?,?,?,?,?,?)",
                (self._session_id, self.agent_id, boot_id, identity["authority_class"], cjson(identity), h72("agent-session", identity), identity["started_at"]),
            )
            self._initialized = True
            self._register_core_constraints()
            return self.status()

    @staticmethod
    def _authorizer(action: int, arg1: str | None, *_: Any) -> int:
        table = str(arg1 or "")
        if action == sqlite3.SQLITE_READ and table == "narrative_log":
            return sqlite3.SQLITE_DENY
        if action in {sqlite3.SQLITE_DELETE, sqlite3.SQLITE_UPDATE} and table in IMMUTABLE_TABLES:
            return sqlite3.SQLITE_DENY
        denied = {getattr(sqlite3, name, -1) for name in (
            "SQLITE_ATTACH", "SQLITE_DETACH", "SQLITE_ALTER_TABLE",
            "SQLITE_DROP_TABLE", "SQLITE_DROP_INDEX", "SQLITE_DROP_TRIGGER")}
        return sqlite3.SQLITE_DENY if action in denied else sqlite3.SQLITE_OK

    def close(self) -> None:
        if self._conn:
            self._conn.close()
        self._conn = None
        self._initialized = False

    def _db(self) -> sqlite3.Connection:
        if not self._conn:
            raise RuntimeError("immutable agent SQL index is not initialized")
        return self._conn

    def _meta(self, key: str, default: str = "") -> str:
        row = self._db().execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return default if row is None else str(row[0])

    def _set(self, key: str, value: str) -> None:
        self._db().execute(
            "INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )

    def _inc(self, key: str) -> int:
        value = int(self._meta(key, "0")) + 1
        self._set(key, str(value))
        return value

    def _register_core_constraints(self) -> None:
        for kind, text in (
            ("AUTHORITY", "The reasoning agent may observe committed VM81 state but may not mutate VM81 directly."),
            ("IMMUTABILITY", "Agent evidence, API geometry, constraints, and narrative rows are append-only and cannot be updated or deleted."),
            ("DISCLOSURE", "Generating API tools receive no read surface for the protected narrative log."),
            ("REASONING_EVIDENCE", "Narrative rows are execution-derived decision summaries and are not raw private chain-of-thought."),
            ("API_GEOMETRY", "API method, path, schema, endpoint provenance, and authority class are committed as immutable geometry."),
        ):
            self.append_constraint(kind, text, "RUNTIME_CONTRACT", VERSION, "A3")

    def register_database_layer(self, layer_name: str, layer_kind: str, source_module: str,
                                storage_class: str, authority_class: str, *, source_locator: str = "",
                                schema_id: str = "UNSPECIFIED", schema_version: str = "UNSPECIFIED",
                                details: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if not self._initialized:
            self.initialize()
        identity = {
            "layer_name": layer_name, "layer_kind": layer_kind, "source_module": source_module,
            "storage_class": storage_class, "authority_class": authority_class,
            "source_locator_hash72": h72("database-locator", source_locator),
            "schema_id": schema_id, "schema_version": schema_version,
        }
        layer_id, layer_hash = sid("DBL", "database-layer-id", identity), h72("database-layer", identity)
        db = self._db()
        db.execute("BEGIN IMMEDIATE")
        try:
            db.execute(
                "INSERT OR IGNORE INTO database_layers VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (layer_id, layer_name, layer_kind, source_module, storage_class, authority_class,
                 identity["source_locator_hash72"], schema_id, schema_version, cjson(details or {}), layer_hash, now()),
            )
            inserted = bool(db.execute("SELECT changes()").fetchone()[0])
            if inserted:
                self._inc("database_layer_count")
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
        return {"layer_id": layer_id, "layer_hash72": layer_hash, "inserted": inserted}

    def snapshot_database_layer(self, layer_id: str, state_root_hash72: str, record_count: int,
                                details: Mapping[str, Any] | None = None) -> dict[str, Any]:
        db = self._db()
        db.execute("BEGIN IMMEDIATE")
        try:
            row = db.execute(
                "SELECT snapshot_sequence,snapshot_hash72 FROM database_snapshots WHERE layer_id=? ORDER BY snapshot_sequence DESC LIMIT 1",
                (layer_id,),
            ).fetchone()
            if row:
                latest = db.execute(
                    "SELECT snapshot_id,state_root_hash72,snapshot_sequence,snapshot_hash72 FROM database_snapshots WHERE layer_id=? ORDER BY snapshot_sequence DESC LIMIT 1",
                    (layer_id,),
                ).fetchone()
                if latest and str(latest[1]) == state_root_hash72:
                    db.execute("COMMIT")
                    return {"snapshot_id": str(latest[0]), "snapshot_hash72": str(latest[3]),
                            "sequence": int(latest[2]), "inserted": False}
            sequence, previous = (int(row[0]) + 1, str(row[1])) if row else (1, "H72-SNAPSHOT-GENESIS")
            payload = {"layer_id": layer_id, "sequence": sequence, "state_root_hash72": state_root_hash72,
                       "record_count": max(0, int(record_count)), "details": _data(details or {}), "previous": previous}
            snapshot_id, snapshot_hash = sid("DBS", "database-snapshot-id", payload), h72("database-snapshot", payload)
            db.execute("INSERT INTO database_snapshots VALUES(?,?,?,?,?,?,?,?,?)",
                       (snapshot_id, layer_id, sequence, state_root_hash72, payload["record_count"],
                        cjson(payload["details"]), previous, snapshot_hash, now()))
            self._inc("database_snapshot_count")
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
        return {"snapshot_id": snapshot_id, "snapshot_hash72": snapshot_hash, "sequence": sequence, "inserted": True}

    def append_constraint(self, kind: str, text: str, source_type: str, source_reference: str,
                          authority_level: str = "A1", *, parent_constraint_id: str | None = None,
                          provenance: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if not self._initialized:
            self.initialize()
        text = str(text).strip()
        if not text:
            raise ValueError("constraint text is required")
        payload = {"kind": kind.upper(), "text": text, "source_type": source_type,
                   "source_reference": source_reference, "authority_level": authority_level,
                   "parent_constraint_id": parent_constraint_id, "provenance": _data(provenance or {})}
        constraint_id, constraint_hash = sid("CON", "constraint-id", payload), h72("constraint", payload)
        db = self._db()
        db.execute("BEGIN IMMEDIATE")
        try:
            db.execute("INSERT OR IGNORE INTO constraints VALUES(?,?,?,?,?,?,?,?,?,?)",
                       (constraint_id, kind.upper(), text, source_type, source_reference, authority_level,
                        parent_constraint_id, cjson(payload["provenance"]), constraint_hash, now()))
            inserted = bool(db.execute("SELECT changes()").fetchone()[0])
            if inserted:
                self._inc("constraint_count")
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
        return {"constraint_id": constraint_id, "constraint_hash72": constraint_hash, "inserted": inserted}

    def bind_constraint(self, constraint_id: str, *, surface_id: str | None = None,
                        database_layer_id: str | None = None, binding_role: str = "GOVERNS",
                        details: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if not surface_id and not database_layer_id:
            raise ValueError("constraint binding requires a surface or database layer")
        payload = {"constraint_id": constraint_id, "surface_id": surface_id,
                   "database_layer_id": database_layer_id, "binding_role": binding_role,
                   "details": _data(details or {})}
        binding_id, binding_hash = sid("CNB", "constraint-binding-id", payload), h72("constraint-binding", payload)
        db = self._db()
        db.execute("BEGIN IMMEDIATE")
        try:
            db.execute("INSERT OR IGNORE INTO constraint_bindings VALUES(?,?,?,?,?,?,?,?)",
                       (binding_id, constraint_id, surface_id, database_layer_id, binding_role,
                        cjson(payload["details"]), binding_hash, now()))
            inserted = bool(db.execute("SELECT changes()").fetchone()[0])
            if inserted:
                self._inc("constraint_binding_count")
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
        return {"binding_id": binding_id, "binding_hash72": binding_hash, "inserted": inserted}

    def register_api_routes(self, routes: Iterable[Any]) -> dict[str, Any]:
        if not self._initialized:
            self.initialize()
        db, inserted, seen = self._db(), 0, 0
        db.execute("BEGIN IMMEDIATE")
        try:
            for route in routes:
                path, endpoint = str(getattr(route, "path", "") or ""), getattr(route, "endpoint", None)
                methods = sorted(str(m) for m in (getattr(route, "methods", None) or []))
                if not path or endpoint is None or not methods:
                    continue
                seen += 1
                body = getattr(route, "body_field", None)
                request_model = getattr(body, "type_", None) if body else None
                def schema(model: Any) -> Any:
                    try:
                        return model.model_json_schema() if hasattr(model, "model_json_schema") else model.schema() if hasattr(model, "schema") else {}
                    except Exception as exc:
                        return {"schema_error": f"{type(exc).__name__}:{exc}"}
                for method in methods:
                    if method in {"HEAD", "OPTIONS"}:
                        continue
                    payload = {
                        "path_template": path, "method": method,
                        "route_name": str(getattr(route, "name", "") or getattr(endpoint, "__name__", "unnamed")),
                        "endpoint_module": str(getattr(endpoint, "__module__", "")),
                        "endpoint_qualname": str(getattr(endpoint, "__qualname__", getattr(endpoint, "__name__", ""))),
                        "tags": list(getattr(route, "tags", None) or []),
                        "request_schema": schema(request_model),
                        "response_schema": schema(getattr(route, "response_model", None)),
                        "authority_class": "GUARDED_API_PROJECTION",
                    }
                    geometry_hash, surface_id = h72("api-geometry", payload), sid("API", "api-surface-id", payload)
                    db.execute("INSERT OR IGNORE INTO api_surfaces VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                               (surface_id, path, method, payload["route_name"], payload["endpoint_module"],
                                payload["endpoint_qualname"], cjson(payload["tags"]), cjson(payload["request_schema"]),
                                cjson(payload["response_schema"]), payload["authority_class"], geometry_hash, now()))
                    if db.execute("SELECT changes()").fetchone()[0]:
                        inserted += 1
                        self._inc("api_surface_count")
                        core_constraints = db.execute(
                            "SELECT constraint_id FROM constraints WHERE source_reference=? ORDER BY constraint_id",
                            (VERSION,),
                        ).fetchall()
                        for constraint_row in core_constraints:
                            binding_payload = {"constraint_id": str(constraint_row[0]), "surface_id": surface_id,
                                               "database_layer_id": None, "binding_role": "GOVERNS_API_GEOMETRY",
                                               "details": {"geometry_hash72": geometry_hash}}
                            binding_id = sid("CNB", "constraint-binding-id", binding_payload)
                            binding_hash = h72("constraint-binding", binding_payload)
                            db.execute("INSERT OR IGNORE INTO constraint_bindings VALUES(?,?,?,?,?,?,?,?)",
                                       (binding_id, str(constraint_row[0]), surface_id, None,
                                        "GOVERNS_API_GEOMETRY", cjson(binding_payload["details"]),
                                        binding_hash, now()))
                            if db.execute("SELECT changes()").fetchone()[0]:
                                self._inc("constraint_binding_count")
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
        return {"routes_seen": seen, "surfaces_inserted": inserted}

    def _surface(self, method: str | None, path: str | None) -> str | None:
        if not method or not path:
            return None
        row = self._db().execute(
            "SELECT surface_id FROM api_surfaces WHERE method=? AND path_template=? ORDER BY rowid DESC LIMIT 1",
            (method.upper(), path),
        ).fetchone()
        return None if row is None else str(row[0])

    @staticmethod
    def _narrative(event_type: str, facts: Mapping[str, Any]) -> str:
        event, status = event_type.upper(), str(facts.get("status") or facts.get("outcome") or "recorded")
        if event == "COMMITTED_RUNTIME_TICK":
            return (f"The reasoning agent observed committed runtime step {facts.get('runtime_step','unknown')}, "
                    f"indexed state {facts.get('state_hash72','unavailable')}, and retained observer-only authority.")
        if event == "SEMANTIC_MEMORY_INGEST":
            return (f"The semantic memory layer admitted a {facts.get('memory_type','semantic')} record with commitment "
                    f"{facts.get('memory_hash72','unavailable')} and preserved its provenance.")
        if event == "GOAL_REGISTERED":
            return (f"The adaptive-goal layer registered goal {facts.get('goal_id','unknown')} against target "
                    f"{facts.get('target_hash72','unavailable')} without overriding invariants.")
        if event == "COGNITION_TASK_CREATED":
            return (f"The agent registered cognition task {facts.get('task_id','unknown')} under goal "
                    f"{facts.get('goal_id','unknown')}; the objective is represented by commitment.")
        if event == "COGNITION_TASK_EXECUTED":
            return (f"The agent executed cognition task {facts.get('task_id','unknown')} with outcome {status}; "
                    "the record is a decision summary, not raw private chain-of-thought.")
        if event == "AGENT_OPERATION_FAILED":
            return f"The requested agent operation failed with classified outcome {status}; prior evidence remained unchanged."
        return f"The reasoning runtime recorded {event_type} with outcome {status} and appended its commitments to the evidence chain."

    def append_agent_event(self, event_type: str, facts: Mapping[str, Any], *, input_payload: Any = None,
                           output_payload: Any = None, constraint_ids: Sequence[str] = (),
                           api_method: str | None = None, api_path: str | None = None) -> dict[str, Any]:
        if not self._initialized:
            self.initialize()
        db, safe = self._db(), _data(facts)
        input_hash, output_hash = h72("agent-input", input_payload), h72("agent-output", output_payload)
        constraint_hash = h72("agent-constraint-set", sorted(str(x) for x in constraint_ids))
        db.execute("BEGIN IMMEDIATE")
        try:
            sequence, previous = int(self._meta("event_sequence", "0")) + 1, self._meta("event_tip", "H72-EVENT-GENESIS")
            surface_id = self._surface(api_method, api_path)
            payload = {"session_id": self._session_id, "sequence": sequence, "event_type": event_type.upper(),
                       "source_surface_id": surface_id, "input_hash72": input_hash, "output_hash72": output_hash,
                       "constraint_set_hash72": constraint_hash, "facts": safe, "prev_event_hash72": previous}
            event_id, event_hash = sid("AGE", "agent-event-id", payload), h72("agent-event", payload)
            created = now()
            db.execute("INSERT INTO agent_events VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                       (event_id, self._session_id, sequence, event_type.upper(), surface_id, input_hash, output_hash,
                        constraint_hash, cjson(safe), previous, event_hash, created))
            nseq, nprev = int(self._meta("narrative_sequence", "0")) + 1, self._meta("narrative_tip", "H72-NARRATIVE-GENESIS")
            text = self._narrative(event_type, safe if isinstance(safe, Mapping) else {})
            npayload = {"event_id": event_id, "sequence": nseq,
                        "narrative_class": "EXECUTION_DERIVED_DECISION_NARRATIVE",
                        "privacy_class": "PROTECTED_AUDIT_ONLY", "narrative_text": text,
                        "prev_narrative_hash72": nprev, "raw_private_chain_of_thought": False}
            narrative_id, narrative_hash = sid("NAR", "narrative-id", npayload), h72("agent-narrative", npayload)
            db.execute("INSERT INTO narrative_log VALUES(?,?,?,?,?,?,?,?,?)",
                       (narrative_id, event_id, nseq, npayload["narrative_class"], npayload["privacy_class"],
                        text, nprev, narrative_hash, created))
            for key, value in (("event_sequence", sequence), ("event_tip", event_hash),
                               ("narrative_sequence", nseq), ("narrative_tip", narrative_hash)):
                self._set(key, str(value))
            self._inc("event_count"); self._inc("narrative_count")
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
        return {"event_id": event_id, "event_hash72": event_hash, "sequence": sequence,
                "narrative_commitment_hash72": narrative_hash,
                "narrative_access": "DENIED_TO_GENERATING_API_TOOLS"}

    def backfill_pass145_constraints(self, path: str | Path) -> dict[str, Any]:
        source = Path(path).expanduser().resolve()
        if not source.is_file() or source == self.path:
            return {"status": "SOURCE_DATABASE_UNAVAILABLE"}
        conn = sqlite3.connect(f"file:{source.as_posix()}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        try:
            tables = {str(r[0]) for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            meta = {str(r[0]): str(r[1]) for r in conn.execute("SELECT key,value FROM meta")} if "meta" in tables else {}
            counts = {t: int(conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]) for t in
                      ("semantic_rules", "semantic_propositions", "objects", "security_boundary_contracts") if t in tables}
            layer = self.register_database_layer(
                "pass145_knowledge_database", "TRANSACTIONAL_KNOWLEDGE_SQLITE", "hhs_runtime.pass145.database",
                "SQLITE_APPEND_AUDITED", "PASS145_KNOWLEDGE_AUTHORITY", source_locator=str(source),
                schema_id=meta.get("schema_id", "HHS_PASS145_KNOWLEDGE_DATABASE"),
                schema_version=meta.get("schema_version", "unknown"), details={"counts": counts, "receipt_tip": meta.get("receipt_tip")})
            inserted = 0
            if "semantic_rules" in tables:
                for row in conn.execute("SELECT rule_id,rule_kind,rule_json,rule_hash72 FROM semantic_rules ORDER BY rule_id"):
                    obj = json.loads(str(row[2])); text = str(obj.get("canonical_text") or obj.get("rule") or obj.get("text") or cjson(obj))
                    inserted += int(self.append_constraint(str(row[1]), text, "PASS145_SEMANTIC_RULE", str(row[0]),
                                                          str(obj.get("authority_level", "A3")),
                                                          provenance={"source_hash72": row[3], "database_layer_id": layer["layer_id"]})["inserted"])
            if "semantic_propositions" in tables:
                for row in conn.execute("SELECT proposition_id,source_expression,primary_class,authority_level,proposition_hash72 FROM semantic_propositions ORDER BY proposition_id"):
                    inserted += int(self.append_constraint(str(row[2]), str(row[1]), "PASS145_SEMANTIC_PROPOSITION",
                                                          str(row[0]), str(row[3]),
                                                          provenance={"source_hash72": row[4], "database_layer_id": layer["layer_id"]})["inserted"])
            if "objects" in tables:
                query = "SELECT object_id,object_type,exact_text,normalized_text,authority_level,object_hash72 FROM objects WHERE UPPER(object_type) IN ('CONSTRAINT','RULE','CONTRACT','PROPOSITION','INVARIANT') ORDER BY object_id"
                for row in conn.execute(query):
                    inserted += int(self.append_constraint(str(row[1]), str(row[2] or row[3]), "PASS145_OBJECT",
                                                          str(row[0]), str(row[4]),
                                                          provenance={"source_hash72": row[5], "database_layer_id": layer["layer_id"]})["inserted"])
            if "security_boundary_contracts" in tables:
                for row in conn.execute("SELECT contract_id,operation,contract_hash72,status FROM security_boundary_contracts ORDER BY contract_id"):
                    text = f"Operation {row[1]} is governed by boundary contract {row[0]} with status {row[3]}."
                    inserted += int(self.append_constraint("SECURITY_BOUNDARY_CONTRACT", text, "PASS145_SECURITY_CONTRACT",
                                                          str(row[0]), "A3",
                                                          provenance={"contract_hash72": row[2], "database_layer_id": layer["layer_id"]})["inserted"])
            root = h72("pass145-snapshot", {"meta": meta, "counts": counts})
            snapshot = self.snapshot_database_layer(layer["layer_id"], root, sum(counts.values()), {"meta": meta, "counts": counts})
            return {"status": "PASS145_CONSTRAINTS_BACKFILLED", "inserted_constraints": inserted,
                    "layer": layer, "snapshot": snapshot}
        finally:
            conn.close()

    def status(self) -> dict[str, Any]:
        if not self._conn:
            return {"schema": "HHS_IMMUTABLE_AGENT_SQL_INDEX_STATUS_V1", "version": VERSION,
                    "initialized": False, "path_hash72": h72("index-path", str(self.path)),
                    "narrative_api_read_surface": "ABSENT"}
        return {"schema": "HHS_IMMUTABLE_AGENT_SQL_INDEX_STATUS_V1", "version": VERSION,
                "schema_id": self._meta("schema_id"), "schema_version": self._meta("schema_version"),
                "initialized": self._initialized, "session_id": self._session_id,
                "path_hash72": h72("index-path", str(self.path)),
                "counts": {"database_layers": int(self._meta("database_layer_count", "0")),
                           "database_snapshots": int(self._meta("database_snapshot_count", "0")),
                           "api_surfaces": int(self._meta("api_surface_count", "0")),
                           "constraints": int(self._meta("constraint_count", "0")),
                           "constraint_bindings": int(self._meta("constraint_binding_count", "0")),
                           "agent_events": int(self._meta("event_count", "0")),
                           "protected_narratives": int(self._meta("narrative_count", "0"))},
                "chain_tips": {"event_hash72": self._meta("event_tip"), "narrative_hash72": self._meta("narrative_tip")},
                "authority_boundary": {"writer_can_append": True, "writer_can_read_protected_narrative": False,
                                       "writer_can_update_immutable_rows": False, "writer_can_delete_immutable_rows": False,
                                       "narrative_api_read_surface": "ABSENT", "narrative_api_delete_surface": "ABSENT",
                                       "local_audit_reader": "OUT_OF_BAND_TOKEN_REQUIRED",
                                       "raw_private_chain_of_thought": "NOT_RECORDED"}}

    def integrity_check(self) -> dict[str, Any]:
        quick = [str(r[0]) for r in self._db().execute("PRAGMA quick_check")]
        foreign = [tuple(r) for r in self._db().execute("PRAGMA foreign_key_check")]
        return {"ok": quick == ["ok"] and not foreign, "quick_check": quick,
                "foreign_key_violations": foreign, "status": self.status()}

    def _protected_read_probe(self) -> bool:
        try:
            self._db().execute("SELECT narrative_text FROM narrative_log LIMIT 1").fetchone()
        except sqlite3.DatabaseError:
            return True
        return False


class HHSImmutableAgentAuditReader:
    """Local read-only auditor; intentionally not connected to FastAPI."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    @classmethod
    def open(cls, path: str | Path, token: str) -> "HHSImmutableAgentAuditReader":
        expected = os.getenv("HHS_AGENT_AUDIT_TOKEN_SHA256", "").strip().lower()
        actual = hashlib.sha256(token.encode()).hexdigest()
        if not expected or not hmac.compare_digest(expected, actual):
            raise PermissionError("HHS_AGENT_AUDIT_TOKEN_REJECTED")
        resolved = Path(path).expanduser().resolve()
        conn = sqlite3.connect(f"file:{resolved.as_posix()}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        conn.execute("PRAGMA trusted_schema=OFF")
        return cls(conn)

    def close(self) -> None:
        self._conn.close()

    def narratives(self, limit: int = 100, after_sequence: int = 0) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM narrative_log WHERE sequence>? ORDER BY sequence LIMIT ?",
            (max(0, int(after_sequence)), max(1, min(int(limit), 10000))),
        ).fetchall()
        return [dict(row) for row in rows]

    def verify_chains(self) -> dict[str, Any]:
        event_previous, event_ok = "H72-EVENT-GENESIS", True
        for row in self._conn.execute("SELECT * FROM agent_events ORDER BY sequence"):
            payload = {"session_id": row["session_id"], "sequence": row["sequence"], "event_type": row["event_type"],
                       "source_surface_id": row["source_surface_id"], "input_hash72": row["input_hash72"],
                       "output_hash72": row["output_hash72"], "constraint_set_hash72": row["constraint_set_hash72"],
                       "facts": json.loads(row["facts_json"]), "prev_event_hash72": event_previous}
            if row["prev_event_hash72"] != event_previous or row["event_hash72"] != h72("agent-event", payload):
                event_ok = False; break
            event_previous = row["event_hash72"]
        narrative_previous, narrative_ok = "H72-NARRATIVE-GENESIS", True
        for row in self._conn.execute("SELECT * FROM narrative_log ORDER BY sequence"):
            payload = {"event_id": row["event_id"], "sequence": row["sequence"],
                       "narrative_class": row["narrative_class"], "privacy_class": row["privacy_class"],
                       "narrative_text": row["narrative_text"], "prev_narrative_hash72": narrative_previous,
                       "raw_private_chain_of_thought": False}
            if row["prev_narrative_hash72"] != narrative_previous or row["narrative_hash72"] != h72("agent-narrative", payload):
                narrative_ok = False; break
            narrative_previous = row["narrative_hash72"]
        return {"ok": event_ok and narrative_ok, "event_chain_ok": event_ok,
                "narrative_chain_ok": narrative_ok, "event_tip_hash72": event_previous,
                "narrative_tip_hash72": narrative_previous}


def _synchronized(method):
    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapped


for _method_name in (
    "initialize", "close", "register_database_layer", "snapshot_database_layer",
    "append_constraint", "bind_constraint", "register_api_routes", "append_agent_event",
    "backfill_pass145_constraints", "status", "integrity_check",
    "_protected_read_probe",
):
    setattr(HHSImmutableAgentSQLIndex, _method_name, _synchronized(getattr(HHSImmutableAgentSQLIndex, _method_name)))


immutable_agent_sql_index = HHSImmutableAgentSQLIndex()
