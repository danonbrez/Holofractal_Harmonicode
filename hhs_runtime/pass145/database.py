from __future__ import annotations

import contextlib
import json
import os
import shutil
import sqlite3
import threading
import zipfile
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Mapping

from .canonical import canonical_json, hash72, sha256_bytes, stable_id, utc_now
from .errors import Pass145Error

SCHEMA_ID = "HHS_PASS145_KNOWLEDGE_DATABASE"
SCHEMA_VERSION = "1.4.0"


SCHEMA_SQL = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    source_root_hash72 TEXT NOT NULL UNIQUE,
    namespace TEXT NOT NULL,
    logical_key TEXT NOT NULL,
    parent_source_id TEXT,
    source_kind TEXT NOT NULL,
    source_name TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    encoding TEXT NOT NULL,
    byte_length INTEGER NOT NULL,
    raw_sha256 TEXT NOT NULL,
    raw_bytes BLOB NOT NULL,
    source_json TEXT NOT NULL,
    admitted_at TEXT NOT NULL,
    immutable INTEGER NOT NULL DEFAULT 1,
    quarantined INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(parent_source_id) REFERENCES sources(source_id)
);
CREATE INDEX IF NOT EXISTS idx_sources_namespace_name ON sources(namespace, source_name);
CREATE INDEX IF NOT EXISTS idx_sources_logical_key ON sources(logical_key);
CREATE TABLE IF NOT EXISTS parses (
    parse_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    parse_root_hash72 TEXT NOT NULL UNIQUE,
    parser_id TEXT NOT NULL,
    parser_version TEXT NOT NULL,
    parse_json TEXT NOT NULL,
    FOREIGN KEY(source_id) REFERENCES sources(source_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS segments (
    segment_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    segment_index INTEGER NOT NULL,
    start_offset INTEGER NOT NULL,
    end_offset INTEGER NOT NULL,
    segment_hash72 TEXT NOT NULL UNIQUE,
    text TEXT NOT NULL,
    segment_json TEXT NOT NULL,
    FOREIGN KEY(source_id) REFERENCES sources(source_id) ON DELETE RESTRICT,
    UNIQUE(source_id, segment_index)
);
CREATE INDEX IF NOT EXISTS idx_segments_source ON segments(source_id, segment_index);
CREATE TABLE IF NOT EXISTS objects (
    object_id TEXT PRIMARY KEY,
    object_type TEXT NOT NULL,
    source_id TEXT,
    segment_id TEXT,
    namespace TEXT NOT NULL,
    exact_text TEXT,
    normalized_text TEXT,
    object_hash72 TEXT NOT NULL UNIQUE,
    interpretation_version TEXT,
    authority_level TEXT NOT NULL DEFAULT 'A1',
    validation_state TEXT NOT NULL DEFAULT 'UNVALIDATED',
    object_json TEXT NOT NULL,
    quarantined INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(source_id) REFERENCES sources(source_id) ON DELETE RESTRICT,
    FOREIGN KEY(segment_id) REFERENCES segments(segment_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_objects_type ON objects(object_type);
CREATE INDEX IF NOT EXISTS idx_objects_source ON objects(source_id);
CREATE INDEX IF NOT EXISTS idx_objects_normalized ON objects(normalized_text);
CREATE TABLE IF NOT EXISTS relations (
    relation_id TEXT PRIMARY KEY,
    relation_type TEXT NOT NULL,
    left_object_id TEXT NOT NULL,
    right_object_id TEXT NOT NULL,
    source_id TEXT,
    relation_hash72 TEXT NOT NULL UNIQUE,
    provenance_json TEXT NOT NULL,
    relation_json TEXT NOT NULL,
    FOREIGN KEY(left_object_id) REFERENCES objects(object_id) ON DELETE RESTRICT,
    FOREIGN KEY(right_object_id) REFERENCES objects(object_id) ON DELETE RESTRICT,
    FOREIGN KEY(source_id) REFERENCES sources(source_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_relations_left ON relations(left_object_id);
CREATE INDEX IF NOT EXISTS idx_relations_right ON relations(right_object_id);
CREATE TABLE IF NOT EXISTS validations (
    validation_id TEXT PRIMARY KEY,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    layer TEXT NOT NULL,
    outcome TEXT NOT NULL,
    validation_hash72 TEXT NOT NULL UNIQUE,
    details_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS environments (
    environment_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    namespace TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    version INTEGER NOT NULL,
    parent_environment_id TEXT,
    parent_state_root_hash72 TEXT,
    mode TEXT NOT NULL,
    policy_json TEXT NOT NULL,
    frozen INTEGER NOT NULL DEFAULT 0,
    archived INTEGER NOT NULL DEFAULT 0,
    destroyed INTEGER NOT NULL DEFAULT 0,
    environment_hash72 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL,
    FOREIGN KEY(parent_environment_id) REFERENCES environments(environment_id)
);
CREATE TABLE IF NOT EXISTS environment_members (
    environment_id TEXT NOT NULL,
    member_type TEXT NOT NULL,
    member_id TEXT NOT NULL,
    access_mode TEXT NOT NULL,
    member_hash72 TEXT NOT NULL,
    PRIMARY KEY(environment_id, member_type, member_id),
    FOREIGN KEY(environment_id) REFERENCES environments(environment_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS scripts (
    script_id TEXT PRIMARY KEY,
    environment_id TEXT,
    name TEXT NOT NULL,
    language TEXT NOT NULL,
    source_text TEXT NOT NULL,
    source_hash72 TEXT NOT NULL,
    normalized_hash72 TEXT NOT NULL,
    entrypoints_json TEXT NOT NULL,
    declared_capabilities_json TEXT NOT NULL,
    resolved_dependencies_json TEXT NOT NULL,
    validation_state TEXT NOT NULL,
    test_state TEXT NOT NULL,
    execution_policy TEXT NOT NULL,
    version INTEGER NOT NULL,
    parent_script_id TEXT,
    receipt_root TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(environment_id) REFERENCES environments(environment_id),
    FOREIGN KEY(parent_script_id) REFERENCES scripts(script_id)
);
CREATE TABLE IF NOT EXISTS lvms (
    lvm_id TEXT PRIMARY KEY,
    environment_id TEXT,
    name TEXT NOT NULL,
    version INTEGER NOT NULL,
    manifest_json TEXT NOT NULL,
    manifest_hash72 TEXT NOT NULL,
    receipt_root TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(environment_id) REFERENCES environments(environment_id)
);
CREATE TABLE IF NOT EXISTS executions (
    execution_id TEXT PRIMARY KEY,
    execution_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    input_json TEXT NOT NULL,
    output_json TEXT NOT NULL,
    status TEXT NOT NULL,
    pre_state_root_hash72 TEXT NOT NULL,
    post_state_root_hash72 TEXT NOT NULL,
    execution_hash72 TEXT NOT NULL,
    receipt_id TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS security_identities (
    identity_id TEXT PRIMARY KEY,
    identity_type TEXT NOT NULL,
    display_name TEXT NOT NULL,
    attributes_json TEXT NOT NULL,
    identity_hash72 TEXT NOT NULL UNIQUE,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS security_authority_grants (
    grant_id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL,
    capabilities_json TEXT NOT NULL,
    operations_json TEXT NOT NULL,
    sources_json TEXT NOT NULL,
    destinations_json TEXT NOT NULL,
    resource_policy_json TEXT NOT NULL,
    disclosure_policy_json TEXT NOT NULL,
    parent_grant_id TEXT,
    grant_hash72 TEXT NOT NULL UNIQUE,
    revoked INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(identity_id) REFERENCES security_identities(identity_id) ON DELETE RESTRICT,
    FOREIGN KEY(parent_grant_id) REFERENCES security_authority_grants(grant_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS security_boundary_contracts (
    contract_id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL,
    grant_id TEXT NOT NULL,
    parent_contract_id TEXT,
    operation TEXT NOT NULL,
    source_scope_json TEXT NOT NULL,
    destination_json TEXT NOT NULL,
    request_json TEXT NOT NULL,
    temporal_context_json TEXT NOT NULL,
    capabilities_json TEXT NOT NULL,
    resource_budget_json TEXT NOT NULL,
    disclosure_scope_json TEXT NOT NULL,
    reversibility_class TEXT NOT NULL,
    path_blueprint_json TEXT NOT NULL,
    relevant_state_root_hash72 TEXT NOT NULL,
    contract_hash72 TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    recursive_depth INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    closed_at TEXT,
    FOREIGN KEY(identity_id) REFERENCES security_identities(identity_id) ON DELETE RESTRICT,
    FOREIGN KEY(grant_id) REFERENCES security_authority_grants(grant_id) ON DELETE RESTRICT,
    FOREIGN KEY(parent_contract_id) REFERENCES security_boundary_contracts(contract_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS security_pathways (
    path_id TEXT PRIMARY KEY,
    contract_id TEXT NOT NULL UNIQUE,
    operation TEXT NOT NULL,
    lifecycle_state TEXT NOT NULL,
    active_capabilities_json TEXT NOT NULL,
    resource_budget_json TEXT NOT NULL,
    disclosure_scope_json TEXT NOT NULL,
    path_hash72 TEXT NOT NULL UNIQUE,
    result_hash72 TEXT,
    closure_status TEXT,
    recovery_state TEXT,
    created_at TEXT NOT NULL,
    closed_at TEXT,
    FOREIGN KEY(contract_id) REFERENCES security_boundary_contracts(contract_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS security_pathway_steps (
    step_id TEXT PRIMARY KEY,
    path_id TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    component TEXT NOT NULL,
    action TEXT NOT NULL,
    input_hash72 TEXT NOT NULL,
    output_hash72 TEXT NOT NULL,
    pre_state_root_hash72 TEXT NOT NULL,
    post_state_root_hash72 TEXT NOT NULL,
    status TEXT NOT NULL,
    step_hash72 TEXT NOT NULL UNIQUE,
    details_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(path_id) REFERENCES security_pathways(path_id) ON DELETE RESTRICT,
    UNIQUE(path_id, ordinal)
);
CREATE TABLE IF NOT EXISTS security_messages (
    message_id TEXT PRIMARY KEY,
    path_id TEXT NOT NULL,
    contract_id TEXT NOT NULL,
    source_peer TEXT NOT NULL,
    destination_peer TEXT NOT NULL,
    data_json TEXT NOT NULL,
    provenance_json TEXT NOT NULL,
    scope_json TEXT NOT NULL,
    expected_state_json TEXT NOT NULL,
    reversal_json TEXT NOT NULL,
    envelope_json TEXT NOT NULL,
    message_hash72 TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(path_id) REFERENCES security_pathways(path_id) ON DELETE RESTRICT,
    FOREIGN KEY(contract_id) REFERENCES security_boundary_contracts(contract_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS security_peer_trust (
    peer_id TEXT PRIMARY KEY,
    public_key_b64 TEXT NOT NULL,
    public_key_fingerprint TEXT NOT NULL UNIQUE,
    classifications_json TEXT NOT NULL,
    destinations_json TEXT NOT NULL,
    admitted_by_identity_id TEXT NOT NULL,
    trust_hash72 TEXT NOT NULL UNIQUE,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY(admitted_by_identity_id) REFERENCES security_identities(identity_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS security_negotiations (
    negotiation_id TEXT PRIMARY KEY,
    path_id TEXT NOT NULL,
    left_state_json TEXT NOT NULL,
    right_state_json TEXT NOT NULL,
    policy_json TEXT NOT NULL,
    resolution_json TEXT NOT NULL,
    negotiation_hash72 TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(path_id) REFERENCES security_pathways(path_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    sequence INTEGER NOT NULL UNIQUE,
    operation TEXT NOT NULL,
    request_json TEXT NOT NULL,
    result_json TEXT NOT NULL,
    pre_state_root_hash72 TEXT NOT NULL,
    post_state_root_hash72 TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS receipts (
    receipt_id TEXT PRIMARY KEY,
    receipt_type TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    parent_receipt_id TEXT,
    transaction_id TEXT,
    receipt_hash72 TEXT NOT NULL UNIQUE,
    receipt_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(parent_receipt_id) REFERENCES receipts(receipt_id),
    FOREIGN KEY(transaction_id) REFERENCES transactions(transaction_id)
);
CREATE TABLE IF NOT EXISTS workspaces (
    workspace_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    version INTEGER NOT NULL,
    owner_authority TEXT NOT NULL,
    default_policy_json TEXT NOT NULL,
    active_environment_id TEXT,
    dependencies_json TEXT NOT NULL,
    tags_json TEXT NOT NULL,
    workspace_hash72 TEXT NOT NULL,
    root_receipt TEXT,
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL,
    FOREIGN KEY(active_environment_id) REFERENCES environments(environment_id)
);
CREATE TABLE IF NOT EXISTS workspace_members (
    workspace_id TEXT NOT NULL,
    member_type TEXT NOT NULL,
    member_id TEXT NOT NULL,
    member_hash72 TEXT NOT NULL,
    PRIMARY KEY(workspace_id, member_type, member_id),
    FOREIGN KEY(workspace_id) REFERENCES workspaces(workspace_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS api_collections (
    collection_id TEXT PRIMARY KEY,
    environment_id TEXT,
    name TEXT NOT NULL,
    collection_json TEXT NOT NULL,
    collection_hash72 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(environment_id) REFERENCES environments(environment_id)
);
CREATE TABLE IF NOT EXISTS extensions (
    extension_id TEXT PRIMARY KEY,
    manifest_json TEXT NOT NULL,
    manifest_hash72 TEXT NOT NULL,
    admitted INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS public_capabilities (
    capability_id TEXT PRIMARY KEY,
    surface_type TEXT NOT NULL,
    classification TEXT NOT NULL,
    contract_json TEXT NOT NULL,
    capability_hash72 TEXT NOT NULL UNIQUE,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_public_capabilities_surface ON public_capabilities(surface_type,classification,active);
CREATE TABLE IF NOT EXISTS external_agent_profiles (
    profile_id TEXT PRIMARY KEY,
    identity_id TEXT NOT NULL,
    grant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    profile_json TEXT NOT NULL,
    profile_hash72 TEXT NOT NULL UNIQUE,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY(identity_id) REFERENCES security_identities(identity_id) ON DELETE RESTRICT,
    FOREIGN KEY(grant_id) REFERENCES security_authority_grants(grant_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS semantic_rules (
    rule_id TEXT PRIMARY KEY,
    rule_kind TEXT NOT NULL,
    registry_version TEXT NOT NULL,
    rule_json TEXT NOT NULL,
    rule_hash72 TEXT NOT NULL UNIQUE,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS semantic_asts (
    ast_id TEXT PRIMARY KEY,
    source_expression TEXT NOT NULL,
    source_hash72 TEXT NOT NULL,
    canonical_ast_hash TEXT NOT NULL,
    registry_version TEXT NOT NULL,
    ast_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(source_hash72,canonical_ast_hash,registry_version)
);
CREATE TABLE IF NOT EXISTS semantic_propositions (
    proposition_id TEXT PRIMARY KEY,
    ast_id TEXT NOT NULL,
    source_expression TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    primary_class TEXT NOT NULL,
    consequence_class TEXT NOT NULL,
    authority_level TEXT NOT NULL,
    operator_profile TEXT NOT NULL,
    lane_scope_json TEXT NOT NULL,
    gate_scope_json TEXT NOT NULL,
    branch_conditions_json TEXT NOT NULL,
    dependencies_json TEXT NOT NULL,
    assumptions_json TEXT NOT NULL,
    prohibited_promotions_json TEXT NOT NULL,
    interpretation_version TEXT NOT NULL,
    interpretation_hash TEXT NOT NULL,
    proposition_hash72 TEXT NOT NULL,
    proposition_json TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY(ast_id) REFERENCES semantic_asts(ast_id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_semantic_propositions_class ON semantic_propositions(primary_class,consequence_class,authority_level);
CREATE TABLE IF NOT EXISTS semantic_derivations (
    derivation_id TEXT PRIMARY KEY,
    output_proposition_id TEXT NOT NULL,
    derivation_json TEXT NOT NULL,
    derivation_hash72 TEXT NOT NULL UNIQUE,
    registry_version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(output_proposition_id) REFERENCES semantic_propositions(proposition_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS semantic_projections (
    projection_id TEXT PRIMARY KEY,
    source_ast_id TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    projection_json TEXT NOT NULL,
    projection_hash72 TEXT NOT NULL UNIQUE,
    native_state_mutation INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(source_ast_id) REFERENCES semantic_asts(ast_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS semantic_contaminations (
    finding_id TEXT PRIMARY KEY,
    proposition_id TEXT,
    diagnostic_code TEXT NOT NULL,
    severity TEXT NOT NULL,
    finding_json TEXT NOT NULL,
    finding_hash72 TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    FOREIGN KEY(proposition_id) REFERENCES semantic_propositions(proposition_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS semantic_promotion_requests (
    promotion_request_id TEXT PRIMARY KEY,
    source_proposition_id TEXT NOT NULL,
    source_class TEXT NOT NULL,
    target_class TEXT NOT NULL,
    governing_rule TEXT NOT NULL,
    dependency_set_json TEXT NOT NULL,
    scope_json TEXT NOT NULL,
    requested_by_identity TEXT NOT NULL,
    status TEXT NOT NULL,
    request_json TEXT NOT NULL,
    request_hash72 TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    FOREIGN KEY(source_proposition_id) REFERENCES semantic_propositions(proposition_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS semantic_promotion_decisions (
    promotion_decision_id TEXT PRIMARY KEY,
    promotion_request_id TEXT NOT NULL UNIQUE,
    verifier_identity TEXT NOT NULL,
    authority_level TEXT NOT NULL,
    decision TEXT NOT NULL,
    decision_json TEXT NOT NULL,
    decision_hash72 TEXT NOT NULL UNIQUE,
    receipt_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(promotion_request_id) REFERENCES semantic_promotion_requests(promotion_request_id) ON DELETE RESTRICT,
    FOREIGN KEY(receipt_id) REFERENCES receipts(receipt_id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS semantic_replays (
    replay_id TEXT PRIMARY KEY,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    original_hash72 TEXT NOT NULL,
    replay_hash72 TEXT NOT NULL,
    status TEXT NOT NULL,
    replay_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

_CANONICAL_ROOT_TABLES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("sources", ("source_id", "source_root_hash72", "namespace", "logical_key", "parent_source_id", "source_kind", "source_name", "mime_type", "encoding", "byte_length", "raw_sha256", "source_json", "immutable", "quarantined")),
    ("parses", ("parse_id", "source_id", "parse_root_hash72", "parser_id", "parser_version", "parse_json")),
    ("segments", ("segment_id", "source_id", "segment_index", "start_offset", "end_offset", "segment_hash72", "text", "segment_json")),
    ("objects", ("object_id", "object_type", "source_id", "segment_id", "namespace", "exact_text", "normalized_text", "object_hash72", "interpretation_version", "authority_level", "validation_state", "object_json", "quarantined")),
    ("relations", ("relation_id", "relation_type", "left_object_id", "right_object_id", "source_id", "relation_hash72", "provenance_json", "relation_json")),
    ("validations", ("validation_id", "target_type", "target_id", "layer", "outcome", "validation_hash72", "details_json")),
    ("environments", ("environment_id", "name", "namespace", "description", "version", "parent_environment_id", "parent_state_root_hash72", "mode", "policy_json", "frozen", "archived", "destroyed", "environment_hash72")),
    ("environment_members", ("environment_id", "member_type", "member_id", "access_mode", "member_hash72")),
    ("scripts", ("script_id", "environment_id", "name", "language", "source_text", "source_hash72", "normalized_hash72", "entrypoints_json", "declared_capabilities_json", "resolved_dependencies_json", "validation_state", "test_state", "execution_policy", "version", "parent_script_id", "receipt_root")),
    ("lvms", ("lvm_id", "environment_id", "name", "version", "manifest_json", "manifest_hash72", "receipt_root")),
    ("workspaces", ("workspace_id", "name", "description", "version", "owner_authority", "default_policy_json", "active_environment_id", "dependencies_json", "tags_json", "workspace_hash72", "root_receipt")),
    ("workspace_members", ("workspace_id", "member_type", "member_id", "member_hash72")),
    ("api_collections", ("collection_id", "environment_id", "name", "collection_json", "collection_hash72")),
    ("extensions", ("extension_id", "manifest_json", "manifest_hash72", "admitted")),
    ("public_capabilities", ("capability_id", "surface_type", "classification", "contract_json", "capability_hash72", "active")),
    ("external_agent_profiles", ("profile_id", "identity_id", "grant_id", "name", "profile_json", "profile_hash72", "active")),
    ("semantic_rules", ("rule_id", "rule_kind", "registry_version", "rule_json", "rule_hash72", "active")),
    ("semantic_asts", ("ast_id", "source_expression", "source_hash72", "canonical_ast_hash", "registry_version", "ast_json")),
    ("semantic_propositions", ("proposition_id", "ast_id", "source_expression", "source_type", "source_reference", "primary_class", "consequence_class", "authority_level", "operator_profile", "lane_scope_json", "gate_scope_json", "branch_conditions_json", "dependencies_json", "assumptions_json", "prohibited_promotions_json", "interpretation_version", "interpretation_hash", "proposition_hash72", "proposition_json", "active")),
    ("semantic_derivations", ("derivation_id", "output_proposition_id", "derivation_json", "derivation_hash72", "registry_version")),
    ("semantic_projections", ("projection_id", "source_ast_id", "profile_id", "projection_json", "projection_hash72", "native_state_mutation")),
    ("semantic_contaminations", ("finding_id", "proposition_id", "diagnostic_code", "severity", "finding_json", "finding_hash72")),
    ("semantic_promotion_requests", ("promotion_request_id", "source_proposition_id", "source_class", "target_class", "governing_rule", "dependency_set_json", "scope_json", "requested_by_identity", "status", "request_json", "request_hash72")),
    ("semantic_promotion_decisions", ("promotion_decision_id", "promotion_request_id", "verifier_identity", "authority_level", "decision", "decision_json", "decision_hash72", "receipt_id")),
    ("semantic_replays", ("replay_id", "target_type", "target_id", "original_hash72", "replay_hash72", "status", "replay_json")),
    ("security_identities", ("identity_id", "identity_type", "display_name", "attributes_json", "identity_hash72", "active")),
    ("security_authority_grants", ("grant_id", "identity_id", "capabilities_json", "operations_json", "sources_json", "destinations_json", "resource_policy_json", "disclosure_policy_json", "parent_grant_id", "grant_hash72", "revoked")),
    ("security_boundary_contracts", ("contract_id", "identity_id", "grant_id", "parent_contract_id", "operation", "source_scope_json", "destination_json", "request_json", "temporal_context_json", "capabilities_json", "resource_budget_json", "disclosure_scope_json", "reversibility_class", "path_blueprint_json", "relevant_state_root_hash72", "contract_hash72", "status", "recursive_depth")),
    ("security_pathways", ("path_id", "contract_id", "operation", "lifecycle_state", "active_capabilities_json", "resource_budget_json", "disclosure_scope_json", "path_hash72", "result_hash72", "closure_status", "recovery_state")),
    ("security_pathway_steps", ("step_id", "path_id", "ordinal", "component", "action", "input_hash72", "output_hash72", "pre_state_root_hash72", "post_state_root_hash72", "status", "step_hash72", "details_json")),
    ("security_messages", ("message_id", "path_id", "contract_id", "source_peer", "destination_peer", "data_json", "provenance_json", "scope_json", "expected_state_json", "reversal_json", "envelope_json", "message_hash72", "status")),
    ("security_peer_trust", ("peer_id", "public_key_b64", "public_key_fingerprint", "classifications_json", "destinations_json", "admitted_by_identity_id", "trust_hash72", "active")),
    ("security_negotiations", ("negotiation_id", "path_id", "left_state_json", "right_state_json", "policy_json", "resolution_json", "negotiation_hash72", "status")),
)


class HHS145Database:
    """Transactional, append-audited local knowledge authority.

    Canonical records are SQLite rows protected by IMMEDIATE transactions.
    Source bytes are immutable.  Every mutation receives an ordered receipt.
    Wall-clock timestamps are operational metadata and never participate in
    object identity or deterministic replay roots.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(str(self.path), isolation_level=None, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=FULL")
        self.conn.execute("PRAGMA trusted_schema=OFF")
        self.conn.executescript(SCHEMA_SQL)
        # Additive Pass 146 schema migration for databases created by the
        # initial 1.1.0 boundary runtime before signed peer envelopes existed.
        message_columns = {str(row[1]) for row in self.conn.execute("PRAGMA table_info(security_messages)")}
        if "envelope_json" not in message_columns:
            self.conn.execute("ALTER TABLE security_messages ADD COLUMN envelope_json TEXT NOT NULL DEFAULT '{}'")
        with self._lock:
            self.conn.execute("BEGIN IMMEDIATE")
            self._meta_default("schema_id", SCHEMA_ID)
            self._meta_default("schema_version", SCHEMA_VERSION)
            self._set_meta("schema_version", SCHEMA_VERSION)
            self._meta_default("transaction_sequence", "0")
            self._meta_default("receipt_tip", "H72N-GENESIS")
            self.conn.execute("COMMIT")

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "HHS145Database":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def _meta_default(self, key: str, value: str) -> None:
        self.conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES(?,?)", (key, value))

    def meta(self, key: str) -> str | None:
        row = self.conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return None if row is None else str(row[0])

    def _set_meta(self, key: str, value: str) -> None:
        self.conn.execute("INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))

    def database_root(self) -> str:
        payload: dict[str, Any] = {"schema_id": SCHEMA_ID, "schema_version": SCHEMA_VERSION, "tables": {}}
        for table, columns in _CANONICAL_ROOT_TABLES:
            order = ",".join(columns)
            rows = self.conn.execute(f"SELECT {order} FROM {table} ORDER BY {order}").fetchall()
            payload["tables"][table] = [[row[col] for col in columns] for row in rows]
        return hash72("hhs_pass145_database_root_v1", payload)

    def integrity_check(self) -> dict[str, Any]:
        quick = self.conn.execute("PRAGMA quick_check").fetchall()
        foreign = self.conn.execute("PRAGMA foreign_key_check").fetchall()
        root = self.database_root()
        return {
            "schema": "HHS_PASS145_DATABASE_INTEGRITY_V1",
            "ok": [r[0] for r in quick] == ["ok"] and not foreign,
            "quick_check": [r[0] for r in quick],
            "foreign_key_violations": [dict(r) for r in foreign],
            "database_root_hash72": root,
            "schema_id": self.meta("schema_id"),
            "schema_version": self.meta("schema_version"),
            "transaction_sequence": int(self.meta("transaction_sequence") or 0),
            "receipt_tip": self.meta("receipt_tip"),
        }

    def mutate(self, operation: str, request: Mapping[str, Any], apply: Callable[[sqlite3.Connection], Any], *, receipt_type: str = "KNOWLEDGE_TRANSACTION_RECEIPT") -> dict[str, Any]:
        with self._lock:
            try:
                self.conn.execute("BEGIN IMMEDIATE")
                pre_root = self.database_root()
                sequence = int(self.meta("transaction_sequence") or 0) + 1
                parent_receipt = self.meta("receipt_tip") or "H72N-GENESIS"
                result = apply(self.conn)
                result_payload = result if isinstance(result, Mapping) else {"result": result}
                post_root = self.database_root()
                tx_identity = {
                    "sequence": sequence,
                    "operation": operation,
                    "request": dict(request),
                    "result": result_payload,
                    "pre_state_root_hash72": pre_root,
                    "post_state_root_hash72": post_root,
                    "status": "TRANSACTION_COMMITTED",
                }
                transaction_id = stable_id("TX", "hhs_pass145_transaction_id_v1", tx_identity)
                receipt_payload = {
                    "schema": "HHS_PASS145_RECEIPT_V1",
                    "receipt_type": receipt_type,
                    "sequence": sequence,
                    "parent_receipt_id": parent_receipt,
                    "transaction_id": transaction_id,
                    "operation": operation,
                    "request_hash72": hash72("hhs_pass145_transaction_request_v1", dict(request)),
                    "result_hash72": hash72("hhs_pass145_transaction_result_v1", result_payload),
                    "pre_state_root_hash72": pre_root,
                    "post_state_root_hash72": post_root,
                    "status": "TRANSACTION_COMMITTED",
                    "rollback_status": "NOT_REQUIRED",
                }
                receipt_hash = hash72("hhs_pass145_receipt_v1", receipt_payload)
                receipt_id = stable_id("RCP", "hhs_pass145_receipt_id_v1", receipt_payload)
                now = utc_now()
                self.conn.execute(
                    "INSERT INTO transactions(transaction_id,sequence,operation,request_json,result_json,pre_state_root_hash72,post_state_root_hash72,status,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                    (transaction_id, sequence, operation, canonical_json(dict(request)), canonical_json(result_payload), pre_root, post_root, "TRANSACTION_COMMITTED", now),
                )
                self.conn.execute(
                    "INSERT INTO receipts(receipt_id,receipt_type,sequence,parent_receipt_id,transaction_id,receipt_hash72,receipt_json,created_at) VALUES(?,?,?,?,?,?,?,?)",
                    (receipt_id, receipt_type, sequence, None if parent_receipt == "H72N-GENESIS" else parent_receipt, transaction_id, receipt_hash, canonical_json({**receipt_payload, "receipt_id": receipt_id, "receipt_hash72": receipt_hash}), now),
                )
                self._set_meta("transaction_sequence", str(sequence))
                self._set_meta("receipt_tip", receipt_id)
                self.conn.execute("COMMIT")
                return {
                    "ok": True,
                    "status": "TRANSACTION_COMMITTED",
                    "transaction_id": transaction_id,
                    "receipt_id": receipt_id,
                    "receipt_hash72": receipt_hash,
                    "sequence": sequence,
                    "pre_state_root_hash72": pre_root,
                    "post_state_root_hash72": post_root,
                    "result": result_payload,
                }
            except Pass145Error as exc:
                with contextlib.suppress(Exception):
                    self.conn.execute("ROLLBACK")
                exc.rollback_status = "TRANSACTION_ROLLED_BACK"
                exc.mutated = False
                raise
            except Exception as exc:
                with contextlib.suppress(Exception):
                    self.conn.execute("ROLLBACK")
                raise Pass145Error("DATABASE_COMMIT_FAILED", str(exc), "TRANSACTION", mutated=False, rollback_status="TRANSACTION_ROLLED_BACK") from exc

    def insert_source_bundle(self, bundle: Mapping[str, Any], *, namespace: str, logical_key: str | None = None, parent_source_id: str | None = None) -> dict[str, Any]:
        source = dict(bundle["source"])
        parse = dict(bundle["parse"])
        raw = bytes(bundle["raw_bytes"])
        segments = [dict(x) for x in bundle.get("segments", [])]
        entities = [dict(x) for x in bundle.get("entities", [])]
        logical_key = logical_key or f"{namespace}:{source['source_name']}"

        def apply(conn: sqlite3.Connection) -> dict[str, Any]:
            existing = conn.execute("SELECT source_id,source_root_hash72 FROM sources WHERE source_root_hash72=?", (source["source_root_hash72"],)).fetchone()
            if existing:
                return {"status": "DUPLICATE_SOURCE", "source_id": existing["source_id"], "source_root_hash72": existing["source_root_hash72"]}
            conn.execute(
                "INSERT INTO sources(source_id,source_root_hash72,namespace,logical_key,parent_source_id,source_kind,source_name,mime_type,encoding,byte_length,raw_sha256,raw_bytes,source_json,admitted_at,immutable,quarantined) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,1,0)",
                (source["source_id"], source["source_root_hash72"], namespace, logical_key, parent_source_id, source["source_kind"], source["source_name"], source["mime_type"], source["encoding"], source["byte_length"], source["raw_sha256"], raw, canonical_json(source), utc_now()),
            )
            conn.execute(
                "INSERT INTO parses(parse_id,source_id,parse_root_hash72,parser_id,parser_version,parse_json) VALUES(?,?,?,?,?,?)",
                (parse["parse_id"], source["source_id"], parse["parse_root_hash72"], parse["parser_id"], parse["parser_version"], canonical_json(parse)),
            )
            for segment in segments:
                conn.execute(
                    "INSERT INTO segments(segment_id,source_id,segment_index,start_offset,end_offset,segment_hash72,text,segment_json) VALUES(?,?,?,?,?,?,?,?)",
                    (segment["segment_id"], source["source_id"], segment["segment_index"], segment["start_offset"], segment["end_offset"], segment["segment_hash"], segment["text"], canonical_json(segment)),
                )
            for entity in entities:
                conn.execute(
                    "INSERT INTO objects(object_id,object_type,source_id,segment_id,namespace,exact_text,normalized_text,object_hash72,interpretation_version,authority_level,validation_state,object_json,quarantined) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,0)",
                    (entity["entity_id"], entity["entity_type"], source["source_id"], None, namespace, entity["verbatim"], entity["normalized"], entity["entity_hash72"], "P145-EXTRACTOR-1", "A1", "UNVALIDATED", canonical_json(entity)),
                )
            return {
                "status": "SOURCE_ADMITTED",
                "source_id": source["source_id"],
                "source_root_hash72": source["source_root_hash72"],
                "parse_id": parse["parse_id"],
                "parse_root_hash72": parse["parse_root_hash72"],
                "segment_count": len(segments),
                "entity_count": len(entities),
            }

        return self.mutate("DOCUMENT_INGEST", {"source": source, "parse_root_hash72": parse["parse_root_hash72"], "namespace": namespace, "logical_key": logical_key, "parent_source_id": parent_source_id}, apply, receipt_type="DOCUMENT_INGESTION_RECEIPT")

    def insert_objects(self, source_id: str, namespace: str, objects: Iterable[Mapping[str, Any]], relations: Iterable[Mapping[str, Any]] = ()) -> dict[str, Any]:
        object_list = [dict(x) for x in objects]
        relation_list = [dict(x) for x in relations]

        def apply(conn: sqlite3.Connection) -> dict[str, Any]:
            if not conn.execute("SELECT 1 FROM sources WHERE source_id=?", (source_id,)).fetchone():
                raise Pass145Error("PROVENANCE_INCOMPLETE", "source does not exist", "KNOWLEDGE_WRITE", source_id)
            inserted = 0
            for obj in object_list:
                object_hash = obj.get("object_hash72") or obj.get("claim_root_hash72") or hash72("hhs_pass145_object_v1", obj)
                object_id = obj.get("object_id") or stable_id("OBJ", "hhs_pass145_object_id_v1", {"source_id": source_id, "hash": object_hash})
                exact = obj.get("verbatim_text") or obj.get("exact_text") or obj.get("verbatim") or obj.get("claim_text")
                normalized = obj.get("normalized_proposition") or obj.get("normalized_text") or obj.get("normalized") or obj.get("canonical_form")
                object_type = obj.get("object_type") or obj.get("claim_type") or obj.get("entity_type") or "INTERPRETATION"
                segment_id = obj.get("segment_id")
                if segment_id is None and obj.get("segment_index") is not None:
                    row = conn.execute("SELECT segment_id FROM segments WHERE source_id=? AND segment_index=?", (source_id, int(obj["segment_index"]))).fetchone()
                    segment_id = row[0] if row else None
                payload = {**obj, "object_id": object_id, "object_hash72": object_hash, "source_id": source_id}
                conn.execute(
                    "INSERT OR IGNORE INTO objects(object_id,object_type,source_id,segment_id,namespace,exact_text,normalized_text,object_hash72,interpretation_version,authority_level,validation_state,object_json,quarantined) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,0)",
                    (object_id, object_type, source_id, segment_id, namespace, exact, normalized, object_hash, obj.get("interpretation_version", "P145-INTERPRETATION-1"), obj.get("authority_level", "A1"), obj.get("validation_state", "UNVALIDATED"), canonical_json(payload)),
                )
                inserted += conn.execute("SELECT changes()").fetchone()[0]
            relation_inserted = 0
            for rel in relation_list:
                left = rel["left_object_id"]
                right = rel["right_object_id"]
                if not conn.execute("SELECT 1 FROM objects WHERE object_id=?", (left,)).fetchone() or not conn.execute("SELECT 1 FROM objects WHERE object_id=?", (right,)).fetchone():
                    raise Pass145Error("PROVENANCE_INCOMPLETE", "relation endpoint missing", "RELATION_WRITE")
                payload = {**rel, "source_id": source_id, "provenance": rel.get("provenance", {"source_id": source_id})}
                rh = rel.get("relation_hash72") or hash72("hhs_pass145_relation_v1", payload)
                rid = rel.get("relation_id") or stable_id("REL", "hhs_pass145_relation_id_v1", rh)
                conn.execute(
                    "INSERT OR IGNORE INTO relations(relation_id,relation_type,left_object_id,right_object_id,source_id,relation_hash72,provenance_json,relation_json) VALUES(?,?,?,?,?,?,?,?)",
                    (rid, rel["relation_type"], left, right, source_id, rh, canonical_json(payload["provenance"]), canonical_json({**payload, "relation_id": rid, "relation_hash72": rh})),
                )
                relation_inserted += conn.execute("SELECT changes()").fetchone()[0]
            return {"status": "KNOWLEDGE_OBJECTS_COMMITTED", "source_id": source_id, "object_count": inserted, "relation_count": relation_inserted}

        return self.mutate("KNOWLEDGE_OBJECT_COMMIT", {"source_id": source_id, "namespace": namespace, "object_count": len(object_list), "relation_count": len(relation_list)}, apply, receipt_type="KNOWLEDGE_TRANSACTION_RECEIPT")

    def add_validation(self, target_type: str, target_id: str, layer: str, outcome: str, details: Mapping[str, Any]) -> dict[str, Any]:
        payload = {"target_type": target_type, "target_id": target_id, "layer": layer, "outcome": outcome, "details": dict(details)}
        validation_hash = hash72("hhs_pass145_validation_v1", payload)
        validation_id = stable_id("VAL", "hhs_pass145_validation_id_v1", payload)

        def apply(conn: sqlite3.Connection) -> dict[str, Any]:
            conn.execute("INSERT OR IGNORE INTO validations(validation_id,target_type,target_id,layer,outcome,validation_hash72,details_json,created_at) VALUES(?,?,?,?,?,?,?,?)", (validation_id, target_type, target_id, layer, outcome, validation_hash, canonical_json(dict(details)), utc_now()))
            if target_type == "OBJECT":
                conn.execute("UPDATE objects SET validation_state=? WHERE object_id=?", (outcome, target_id))
            return {"status": outcome, "validation_id": validation_id, "validation_hash72": validation_hash}

        return self.mutate("VALIDATION_RECORD", payload, apply, receipt_type="VALIDATION_RECEIPT")

    def get_source(self, source_id: str, *, include_raw: bool = False) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM sources WHERE source_id=?", (source_id,)).fetchone()
        if not row:
            return None
        out = dict(row)
        out["source"] = json.loads(out.pop("source_json"))
        raw = out.pop("raw_bytes")
        if include_raw:
            out["raw_bytes"] = raw
        parse = self.conn.execute("SELECT parse_json FROM parses WHERE source_id=?", (source_id,)).fetchone()
        out["parse"] = json.loads(parse[0]) if parse else None
        out["segments"] = [json.loads(r[0]) for r in self.conn.execute("SELECT segment_json FROM segments WHERE source_id=? ORDER BY segment_index", (source_id,))]
        return out

    def get_object(self, object_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM objects WHERE object_id=?", (object_id,)).fetchone()
        if not row:
            return None
        out = dict(row)
        out["object"] = json.loads(out.pop("object_json"))
        out["relations"] = [json.loads(r[0]) for r in self.conn.execute("SELECT relation_json FROM relations WHERE left_object_id=? OR right_object_id=? ORDER BY relation_id", (object_id, object_id))]
        return out

    def get_receipt(self, receipt_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT receipt_json FROM receipts WHERE receipt_id=? OR receipt_hash72=?", (receipt_id, receipt_id)).fetchone()
        return json.loads(row[0]) if row else None

    def list_receipts(self, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 10_000))
        return [json.loads(r[0]) for r in self.conn.execute("SELECT receipt_json FROM receipts ORDER BY sequence DESC LIMIT ?", (limit,))]

    def search(self, text: str, *, object_type: str | None = None, source_id: str | None = None, namespace: str | None = None, limit: int = 100, exact_symbol: bool = False) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 1000))
        clauses = ["quarantined=0"]
        params: list[Any] = []
        if object_type:
            clauses.append("object_type=?")
            params.append(object_type)
        if source_id:
            clauses.append("source_id=?")
            params.append(source_id)
        if namespace:
            clauses.append("namespace=?")
            params.append(namespace)
        if exact_symbol:
            clauses.append("(exact_text=? OR normalized_text=?)")
            params.extend([text, text])
        elif text:
            clauses.append("(exact_text LIKE ? ESCAPE '\\' OR normalized_text LIKE ? ESCAPE '\\')")
            escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            params.extend([f"%{escaped}%", f"%{escaped.casefold()}%"] )
        params.append(limit)
        sql = "SELECT object_id,object_type,source_id,segment_id,namespace,exact_text,normalized_text,object_hash72,authority_level,validation_state FROM objects WHERE " + " AND ".join(clauses) + " ORDER BY source_id,object_id LIMIT ?"
        return [dict(r) for r in self.conn.execute(sql, params)]

    def source_search(self, text: str, *, namespace: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        clauses = ["quarantined=0", "(source_name LIKE ? OR source_json LIKE ?)"]
        params: list[Any] = [f"%{text}%", f"%{text}%"]
        if namespace:
            clauses.append("namespace=?")
            params.append(namespace)
        params.append(max(1, min(limit, 1000)))
        return [dict(r) for r in self.conn.execute("SELECT source_id,source_root_hash72,namespace,logical_key,parent_source_id,source_name,mime_type,byte_length,raw_sha256 FROM sources WHERE " + " AND ".join(clauses) + " ORDER BY source_name,source_id LIMIT ?", params)]

    def quarantine(self, target_id: str, release: bool = False) -> dict[str, Any]:
        value = 0 if release else 1

        def apply(conn: sqlite3.Connection) -> dict[str, Any]:
            changed = 0
            for table, key in (("sources", "source_id"), ("objects", "object_id")):
                conn.execute(f"UPDATE {table} SET quarantined=? WHERE {key}=?", (value, target_id))
                changed += conn.execute("SELECT changes()").fetchone()[0]
            if not changed:
                raise Pass145Error("PROVENANCE_INCOMPLETE", "target not found", "PROTECTION", target_id)
            return {"status": "QUARANTINE_RELEASED" if release else "QUARANTINED", "target_id": target_id}

        return self.mutate("PROTECTION_RELEASE" if release else "PROTECTION_QUARANTINE", {"target_id": target_id}, apply, receipt_type="PROTECTION_RECEIPT")

    def verify_receipt_chain(self) -> dict[str, Any]:
        rows = self.conn.execute("SELECT sequence,receipt_id,parent_receipt_id,receipt_hash72,receipt_json FROM receipts ORDER BY sequence").fetchall()
        expected_parent = "H72N-GENESIS"
        failures = []
        for row in rows:
            payload = json.loads(row["receipt_json"])
            claimed_hash = payload.pop("receipt_hash72", None)
            payload.pop("receipt_id", None)
            actual_hash = hash72("hhs_pass145_receipt_v1", payload)
            parent = row["parent_receipt_id"] or "H72N-GENESIS"
            if parent != expected_parent:
                failures.append({"sequence": row["sequence"], "reason": "PARENT_MISMATCH", "expected": expected_parent, "actual": parent})
            if actual_hash != claimed_hash or actual_hash != row["receipt_hash72"]:
                failures.append({"sequence": row["sequence"], "reason": "HASH_MISMATCH"})
            expected_parent = row["receipt_id"]
        return {"schema": "HHS_PASS145_RECEIPT_CHAIN_VERIFICATION_V1", "ok": not failures, "count": len(rows), "tip_receipt_id": expected_parent, "failures": failures}

    def create_backup(self, destination: str | Path) -> dict[str, Any]:
        dest = Path(destination).expanduser().resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        temp_db = dest.with_suffix(dest.suffix + ".sqlite")
        with sqlite3.connect(str(temp_db)) as target:
            self.conn.backup(target)
        db_bytes = temp_db.read_bytes()
        manifest = {
            "schema": "HHS_PASS145_BACKUP_MANIFEST_V1",
            "schema_id": SCHEMA_ID,
            "schema_version": SCHEMA_VERSION,
            "database_filename": "knowledge.sqlite3",
            "database_sha256": sha256_bytes(db_bytes),
            "database_root_hash72": self.database_root(),
            "receipt_tip": self.meta("receipt_tip"),
            "transaction_sequence": int(self.meta("transaction_sequence") or 0),
        }
        manifest["manifest_hash72"] = hash72("hhs_pass145_backup_manifest_v1", manifest)
        with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.writestr("manifest.json", canonical_json(manifest))
            zf.write(temp_db, "knowledge.sqlite3")
            zf.writestr("RESTORE.md", "Verify manifest.json and knowledge.sqlite3 before applying restore.\n")
        temp_db.unlink(missing_ok=True)
        result = {"status": "BACKUP_CREATED", "path": str(dest), "archive_sha256": sha256_bytes(dest.read_bytes()), "manifest": manifest}
        return result

    @staticmethod
    def verify_backup(path: str | Path) -> dict[str, Any]:
        p = Path(path).expanduser().resolve()
        try:
            with zipfile.ZipFile(p) as zf:
                names = set(zf.namelist())
                if not {"manifest.json", "knowledge.sqlite3"}.issubset(names):
                    raise Pass145Error("BACKUP_INVALID", "required backup members absent", "BACKUP_VERIFY")
                manifest = json.loads(zf.read("manifest.json"))
                db_bytes = zf.read("knowledge.sqlite3")
        except (zipfile.BadZipFile, json.JSONDecodeError, KeyError) as exc:
            raise Pass145Error("BACKUP_INVALID", str(exc), "BACKUP_VERIFY") from exc
        claimed = manifest.get("manifest_hash72")
        base = dict(manifest)
        base.pop("manifest_hash72", None)
        checks = {
            "schema": manifest.get("schema") == "HHS_PASS145_BACKUP_MANIFEST_V1",
            "database_sha256": sha256_bytes(db_bytes) == manifest.get("database_sha256"),
            "manifest_hash72": hash72("hhs_pass145_backup_manifest_v1", base) == claimed,
        }
        return {"schema": "HHS_PASS145_BACKUP_VERIFICATION_V1", "ok": all(checks.values()), "checks": checks, "manifest": manifest, "archive_sha256": sha256_bytes(p.read_bytes())}

    @staticmethod
    def restore_preview(path: str | Path) -> dict[str, Any]:
        verification = HHS145Database.verify_backup(path)
        return {"schema": "HHS_PASS145_RESTORE_PREVIEW_V1", "status": "RESTORE_PREVIEW_VALID" if verification["ok"] else "RESTORE_REJECTED", "would_mutate": False, "verification": verification}

    @staticmethod
    def restore_apply(path: str | Path, destination_db: str | Path, *, require_empty: bool = True) -> dict[str, Any]:
        verification = HHS145Database.verify_backup(path)
        if not verification["ok"]:
            raise Pass145Error("RESTORE_REJECTED", "backup verification failed", "RESTORE")
        dest = Path(destination_db).expanduser().resolve()
        if require_empty and dest.exists() and dest.stat().st_size:
            raise Pass145Error("RESTORE_REJECTED", "destination exists; explicit replacement authorization required", "RESTORE")
        dest.parent.mkdir(parents=True, exist_ok=True)
        temp = dest.with_suffix(dest.suffix + ".restore.tmp")
        with zipfile.ZipFile(Path(path).expanduser().resolve()) as zf:
            temp.write_bytes(zf.read("knowledge.sqlite3"))
        with sqlite3.connect(str(temp)) as conn:
            check = conn.execute("PRAGMA quick_check").fetchone()[0]
            if check != "ok":
                temp.unlink(missing_ok=True)
                raise Pass145Error("RESTORE_REJECTED", f"restored DB integrity: {check}", "RESTORE")
        os.replace(temp, dest)
        return {"schema": "HHS_PASS145_RESTORE_RESULT_V1", "status": "RESTORE_APPLIED", "destination": str(dest), "backup": verification}
