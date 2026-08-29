"""Exact Pass 188 versioned NFT/content-license lineage authority.

This runtime is subordinate to inherited VM81 admission. Every mutation requires
an explicit 72-glyph inherited authority witness and appends one deterministic
Hash72 event. External-chain, wallet, browser-local, and marketplace metadata are
evidence only and never authorize mutation or egress.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import threading
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

CONTRACT_ID = "HHS-P188-VNFTCLL-LOSP-VM81-H72-H216"
COMPLETION_CLASSIFICATION = "HHS_PASS_188_VERSIONED_CONTENT_LICENSE_AND_LEGACY_STATE_VERIFIED"
SCHEMA_VERSION = 1
ZERO_HASH72 = "0" * 72

LEGACY_POLICIES = {
    "LEGACY_BOUND",
    "CURRENT_TERMS",
    "OPT_IN_UPGRADE",
    "COMPATIBILITY_FLOOR",
    "REVOCABLE_CAPABILITY",
    "FORKED_LICENSE",
    "SUNSET",
}
EXTERNAL_ANCHOR_STATUSES = {"PENDING", "CONFIRMED", "FAILED", "REORGED", "UNAVAILABLE"}
MUTATION_OPERATIONS = {
    "content create",
    "content version",
    "license create",
    "license update",
    "license branch",
    "license activate",
    "binding create",
    "binding upgrade",
    "ownership transfer",
    "delegation create",
    "revoke",
    "expire",
    "graph edge create",
}


def _reject_float(value: Any, path: str = "value") -> None:
    if isinstance(value, float):
        raise ValueError(f"floating-point canonical ingress rejected at {path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_float(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_float(item, f"{path}[{index}]")


def canonical_json(value: Any) -> str:
    _reject_float(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash72(domain: str, value: Any) -> str:
    payload = canonical_json(value).encode("utf-8")
    first = hashlib.sha256(domain.encode("utf-8") + b"\0" + payload).hexdigest()
    second = hashlib.sha256(b"HHS-HASH72\0" + first.encode("ascii") + payload).hexdigest()
    return first + second[:8]


def require_hash72(value: str, name: str) -> str:
    text = str(value)
    if len(text) != 72 or any(ch not in "0123456789abcdef" for ch in text):
        raise ValueError(f"{name} must be 72 lowercase hexadecimal glyphs")
    if text == ZERO_HASH72:
        raise ValueError(f"{name} may not be the zero Hash72")
    return text


def _sorted_unique(values: Iterable[str]) -> list[str]:
    items = list(values)
    _reject_float(items)
    return sorted({str(v) for v in items})


def _exact_royalty(value: Any) -> tuple[int, int]:
    if value is None:
        return (0, 1)
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError("royalty must be [numerator, denominator]")
    numerator = int(value[0])
    denominator = int(value[1])
    if denominator <= 0 or numerator < 0:
        raise ValueError("invalid exact royalty")
    fraction = Fraction(numerator, denominator)
    return fraction.numerator, fraction.denominator


class LicenseLineageAuthority:
    """Durable append-only Pass 188 license authority."""

    def __init__(self, path: str | os.PathLike[str]):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(self.path, timeout=5.0, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._connection.execute("PRAGMA busy_timeout=5000")
        self._init_schema()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "LicenseLineageAuthority":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _init_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS events(
                sequence INTEGER PRIMARY KEY,
                predecessor_hash72 TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                authority_hash72 TEXT NOT NULL,
                successor_hash72 TEXT NOT NULL,
                hash216 TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS content_versions(
                logical_content_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                content_version_id TEXT NOT NULL UNIQUE,
                content_hash TEXT NOT NULL,
                parents_json TEXT NOT NULL,
                embedded_license_ids_json TEXT NOT NULL,
                creation_sequence INTEGER NOT NULL,
                PRIMARY KEY(logical_content_id, version)
            );
            CREATE TABLE IF NOT EXISTS license_versions(
                logical_license_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                license_version_id TEXT NOT NULL UNIQUE,
                parents_json TEXT NOT NULL,
                controlled_content_ids_json TEXT NOT NULL,
                rights_json TEXT NOT NULL,
                obligations_json TEXT NOT NULL,
                legacy_policy TEXT NOT NULL,
                controller_at_creation TEXT NOT NULL,
                territory TEXT,
                modality TEXT,
                revocable_rights_json TEXT NOT NULL,
                compatibility_floor_json TEXT NOT NULL,
                royalty_numerator INTEGER NOT NULL,
                royalty_denominator INTEGER NOT NULL,
                delta_json TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 0,
                expired INTEGER NOT NULL DEFAULT 0,
                external_anchor_status TEXT NOT NULL DEFAULT 'UNAVAILABLE',
                creation_sequence INTEGER NOT NULL,
                PRIMARY KEY(logical_license_id, version)
            );
            CREATE TABLE IF NOT EXISTS ownership(
                logical_license_id TEXT PRIMARY KEY,
                controller TEXT NOT NULL,
                root_hash72 TEXT NOT NULL,
                event_sequence INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS delegations(
                delegation_id TEXT PRIMARY KEY,
                logical_license_id TEXT NOT NULL,
                principal TEXT NOT NULL,
                rights_json TEXT NOT NULL,
                active INTEGER NOT NULL,
                creation_sequence INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS bindings(
                binding_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                principal TEXT NOT NULL,
                logical_content_id TEXT NOT NULL,
                content_version_id TEXT NOT NULL,
                logical_license_id TEXT NOT NULL,
                license_version_id TEXT NOT NULL,
                rights_snapshot_json TEXT NOT NULL,
                obligations_snapshot_json TEXT NOT NULL,
                status TEXT NOT NULL,
                creation_sequence INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS admitted_operations(
                operation_id TEXT PRIMARY KEY,
                binding_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                target_egress TEXT NOT NULL,
                license_version_id TEXT NOT NULL,
                content_version_id TEXT NOT NULL,
                receipt_hash72 TEXT NOT NULL,
                event_sequence INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS revocations(
                revocation_id TEXT PRIMARY KEY,
                logical_license_id TEXT NOT NULL,
                license_version_id TEXT NOT NULL,
                principal TEXT NOT NULL,
                operation TEXT NOT NULL,
                creation_sequence INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS graph_edges(
                project_id TEXT NOT NULL,
                source_node TEXT NOT NULL,
                target_node TEXT NOT NULL,
                creation_sequence INTEGER NOT NULL,
                PRIMARY KEY(project_id, source_node, target_node)
            );
            """
        )
        self._connection.commit()

    def _root(self, connection: sqlite3.Connection | None = None) -> tuple[int, str]:
        conn = connection or self._connection
        row = conn.execute(
            "SELECT sequence, successor_hash72 FROM events ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        return (int(row[0]), str(row[1])) if row else (0, ZERO_HASH72)

    def _mutate(
        self,
        event_type: str,
        payload: Mapping[str, Any],
        authority_hash72: str,
        apply: Callable[[sqlite3.Connection, int, str], Any],
    ) -> dict[str, Any]:
        authority = require_hash72(authority_hash72, "vm81_authority_hash72")
        payload_dict = dict(payload)
        _reject_float(payload_dict)
        with self._lock:
            conn = self._connection
            conn.execute("BEGIN IMMEDIATE")
            try:
                previous_sequence, predecessor = self._root(conn)
                sequence = previous_sequence + 1
                event_payload = {
                    "contract": CONTRACT_ID,
                    "sequence": sequence,
                    "event_type": event_type,
                    "payload": payload_dict,
                    "authority_hash72": authority,
                }
                successor = hash72(
                    "HHS-P188-LICENSE-EVENT",
                    {"predecessor_hash72": predecessor, **event_payload},
                )
                closure = hash72(
                    "HHS-P188-LICENSE-CLOSURE",
                    {
                        "predecessor_hash72": predecessor,
                        "successor_hash72": successor,
                        "sequence": sequence,
                        "event_type": event_type,
                    },
                )
                hash216 = predecessor + successor + closure
                result = apply(conn, sequence, successor)
                conn.execute(
                    "INSERT INTO events VALUES(?,?,?,?,?,?,?)",
                    (
                        sequence,
                        predecessor,
                        event_type,
                        canonical_json(payload_dict),
                        authority,
                        successor,
                        hash216,
                    ),
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return {
            "sequence": sequence,
            "event_type": event_type,
            "predecessor_hash72": predecessor,
            "successor_hash72": successor,
            "hash216": hash216,
            "authority_hash72": authority,
            "result": result,
        }

    def _content_row(self, content_version_id: str) -> sqlite3.Row:
        row = self._connection.execute(
            "SELECT * FROM content_versions WHERE content_version_id=?", (content_version_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"unknown content version: {content_version_id}")
        return row

    def _license_row(self, license_version_id: str) -> sqlite3.Row:
        row = self._connection.execute(
            "SELECT * FROM license_versions WHERE license_version_id=?", (license_version_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"unknown license version: {license_version_id}")
        return row

    @staticmethod
    def _license_dict(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "logical_license_id": row["logical_license_id"],
            "version": int(row["version"]),
            "license_version_id": row["license_version_id"],
            "parents": json.loads(row["parents_json"]),
            "controlled_content_ids": json.loads(row["controlled_content_ids_json"]),
            "rights": json.loads(row["rights_json"]),
            "obligations": json.loads(row["obligations_json"]),
            "legacy_policy": row["legacy_policy"],
            "controller_at_creation": row["controller_at_creation"],
            "territory": row["territory"],
            "modality": row["modality"],
            "revocable_rights": json.loads(row["revocable_rights_json"]),
            "compatibility_floor_rights": json.loads(row["compatibility_floor_json"]),
            "royalty": [int(row["royalty_numerator"]), int(row["royalty_denominator"])],
            "delta": json.loads(row["delta_json"]),
            "active": bool(row["active"]),
            "expired": bool(row["expired"]),
            "external_anchor_status": row["external_anchor_status"],
        }

    def content_create(
        self,
        *,
        logical_content_id: str,
        content_hash: str,
        authority_hash72: str,
        embedded_license_ids: Sequence[str] = (),
    ) -> dict[str, Any]:
        if not logical_content_id or not content_hash:
            raise ValueError("logical_content_id and content_hash are required")
        if self._connection.execute(
            "SELECT 1 FROM content_versions WHERE logical_content_id=?", (logical_content_id,)
        ).fetchone():
            raise ValueError("logical content already exists")
        payload = {
            "logical_content_id": logical_content_id,
            "version": 1,
            "content_hash": content_hash,
            "parents": [],
            "embedded_license_ids": _sorted_unique(embedded_license_ids),
        }
        content_version_id = "cv_" + hash72("HHS-P188-CONTENT-VERSION", payload)

        def apply(conn: sqlite3.Connection, sequence: int, _: str) -> dict[str, Any]:
            conn.execute(
                "INSERT INTO content_versions VALUES(?,?,?,?,?,?,?)",
                (
                    logical_content_id,
                    1,
                    content_version_id,
                    content_hash,
                    "[]",
                    canonical_json(payload["embedded_license_ids"]),
                    sequence,
                ),
            )
            return {"content_version_id": content_version_id, **payload}

        return self._mutate("CONTENT_CREATED", payload, authority_hash72, apply)

    def content_version(
        self,
        *,
        logical_content_id: str,
        content_hash: str,
        authority_hash72: str,
        parent_content_version_ids: Sequence[str] | None = None,
        embedded_license_ids: Sequence[str] = (),
    ) -> dict[str, Any]:
        latest = self._connection.execute(
            "SELECT * FROM content_versions WHERE logical_content_id=? ORDER BY version DESC LIMIT 1",
            (logical_content_id,),
        ).fetchone()
        if latest is None:
            raise KeyError("logical content does not exist")
        version = int(latest["version"]) + 1
        parents = list(parent_content_version_ids or [latest["content_version_id"]])
        for parent in parents:
            row = self._content_row(parent)
            if row["logical_content_id"] != logical_content_id:
                raise ValueError("parent content version belongs to different logical content")
        payload = {
            "logical_content_id": logical_content_id,
            "version": version,
            "content_hash": content_hash,
            "parents": parents,
            "embedded_license_ids": _sorted_unique(embedded_license_ids),
        }
        content_version_id = "cv_" + hash72("HHS-P188-CONTENT-VERSION", payload)

        def apply(conn: sqlite3.Connection, sequence: int, _: str) -> dict[str, Any]:
            conn.execute(
                "INSERT INTO content_versions VALUES(?,?,?,?,?,?,?)",
                (
                    logical_content_id,
                    version,
                    content_version_id,
                    content_hash,
                    canonical_json(parents),
                    canonical_json(payload["embedded_license_ids"]),
                    sequence,
                ),
            )
            return {"content_version_id": content_version_id, **payload}

        return self._mutate("CONTENT_VERSION_CREATED", payload, authority_hash72, apply)

    def content_compare(self, left_content_version_id: str, right_content_version_id: str) -> dict[str, Any]:
        left = self._content_row(left_content_version_id)
        right = self._content_row(right_content_version_id)
        return {
            "same_logical_content": left["logical_content_id"] == right["logical_content_id"],
            "same_content_hash": left["content_hash"] == right["content_hash"],
            "left": dict(left),
            "right": dict(right),
        }

    def license_create(
        self,
        *,
        logical_license_id: str,
        controlled_content_ids: Sequence[str],
        rights: Sequence[str],
        obligations: Mapping[str, Any],
        legacy_policy: str,
        controller: str,
        authority_hash72: str,
        territory: str | None = None,
        modality: str | None = None,
        revocable_rights: Sequence[str] = (),
        compatibility_floor_rights: Sequence[str] = (),
        royalty: Sequence[int] | None = None,
        external_anchor_status: str = "UNAVAILABLE",
    ) -> dict[str, Any]:
        if legacy_policy not in LEGACY_POLICIES:
            raise ValueError("unknown legacy policy")
        if external_anchor_status not in EXTERNAL_ANCHOR_STATUSES:
            raise ValueError("unknown external anchor status")
        if self._connection.execute(
            "SELECT 1 FROM license_versions WHERE logical_license_id=?", (logical_license_id,)
        ).fetchone():
            raise ValueError("logical license already exists")
        for content_id in controlled_content_ids:
            if not self._connection.execute(
                "SELECT 1 FROM content_versions WHERE logical_content_id=?", (content_id,)
            ).fetchone():
                raise KeyError(f"unknown controlled content: {content_id}")
        rn, rd = _exact_royalty(royalty)
        payload = {
            "logical_license_id": logical_license_id,
            "version": 1,
            "parents": [],
            "controlled_content_ids": _sorted_unique(controlled_content_ids),
            "rights": _sorted_unique(rights),
            "obligations": dict(obligations),
            "legacy_policy": legacy_policy,
            "controller": controller,
            "territory": territory,
            "modality": modality,
            "revocable_rights": _sorted_unique(revocable_rights),
            "compatibility_floor_rights": _sorted_unique(compatibility_floor_rights),
            "royalty": [rn, rd],
            "delta": {"op": "CREATE"},
            "external_anchor_status": external_anchor_status,
        }
        license_version_id = "lv_" + hash72("HHS-P188-LICENSE-VERSION", payload)

        def apply(conn: sqlite3.Connection, sequence: int, successor: str) -> dict[str, Any]:
            conn.execute(
                """INSERT INTO license_versions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    logical_license_id,
                    1,
                    license_version_id,
                    "[]",
                    canonical_json(payload["controlled_content_ids"]),
                    canonical_json(payload["rights"]),
                    canonical_json(payload["obligations"]),
                    legacy_policy,
                    controller,
                    territory,
                    modality,
                    canonical_json(payload["revocable_rights"]),
                    canonical_json(payload["compatibility_floor_rights"]),
                    rn,
                    rd,
                    canonical_json(payload["delta"]),
                    1,
                    0,
                    external_anchor_status,
                    sequence,
                ),
            )
            root = hash72(
                "HHS-P188-OWNERSHIP-ROOT",
                {
                    "logical_license_id": logical_license_id,
                    "controller": controller,
                    "sequence": sequence,
                    "event_hash72": successor,
                },
            )
            conn.execute(
                "INSERT INTO ownership VALUES(?,?,?,?)",
                (logical_license_id, controller, root, sequence),
            )
            return {"license_version_id": license_version_id, "ownership_root_hash72": root, **payload}

        return self._mutate("LICENSE_CREATED", payload, authority_hash72, apply)

    def _next_license_version(
        self,
        *,
        parent_license_version_id: str,
        delta: Mapping[str, Any],
        authority_hash72: str,
        branch: bool,
    ) -> dict[str, Any]:
        parent_row = self._license_row(parent_license_version_id)
        parent = self._license_dict(parent_row)
        logical_license_id = parent["logical_license_id"]
        latest = self._connection.execute(
            "SELECT MAX(version) FROM license_versions WHERE logical_license_id=?",
            (logical_license_id,),
        ).fetchone()[0]
        version = int(latest) + 1
        allowed = {
            "controlled_content_ids",
            "rights",
            "obligations",
            "legacy_policy",
            "territory",
            "modality",
            "revocable_rights",
            "compatibility_floor_rights",
            "royalty",
            "external_anchor_status",
        }
        unknown = set(delta) - allowed
        if unknown:
            raise ValueError(f"unknown license delta fields: {sorted(unknown)}")
        state = dict(parent)
        for key, value in delta.items():
            state[key] = value
        if state["legacy_policy"] not in LEGACY_POLICIES:
            raise ValueError("unknown legacy policy")
        if state["external_anchor_status"] not in EXTERNAL_ANCHOR_STATUSES:
            raise ValueError("unknown external anchor status")
        state["rights"] = _sorted_unique(state["rights"])
        state["revocable_rights"] = _sorted_unique(state["revocable_rights"])
        state["compatibility_floor_rights"] = _sorted_unique(state["compatibility_floor_rights"])
        state["controlled_content_ids"] = _sorted_unique(state["controlled_content_ids"])
        floor = set(parent["compatibility_floor_rights"])
        if floor and not floor.issubset(set(state["rights"])):
            raise ValueError("compatibility floor rights cannot be removed")
        rn, rd = _exact_royalty(state["royalty"])
        payload = {
            "logical_license_id": logical_license_id,
            "version": version,
            "parents": [parent_license_version_id],
            "controlled_content_ids": state["controlled_content_ids"],
            "rights": state["rights"],
            "obligations": dict(state["obligations"]),
            "legacy_policy": state["legacy_policy"],
            "controller": self.ownership_inspect(logical_license_id)["controller"],
            "territory": state["territory"],
            "modality": state["modality"],
            "revocable_rights": state["revocable_rights"],
            "compatibility_floor_rights": state["compatibility_floor_rights"],
            "royalty": [rn, rd],
            "delta": dict(delta),
            "external_anchor_status": state["external_anchor_status"],
            "branch": bool(branch),
        }
        license_version_id = "lv_" + hash72("HHS-P188-LICENSE-VERSION", payload)

        def apply(conn: sqlite3.Connection, sequence: int, _: str) -> dict[str, Any]:
            if not branch:
                conn.execute(
                    "UPDATE license_versions SET active=0 WHERE logical_license_id=?",
                    (logical_license_id,),
                )
            conn.execute(
                """INSERT INTO license_versions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    logical_license_id,
                    version,
                    license_version_id,
                    canonical_json([parent_license_version_id]),
                    canonical_json(payload["controlled_content_ids"]),
                    canonical_json(payload["rights"]),
                    canonical_json(payload["obligations"]),
                    payload["legacy_policy"],
                    payload["controller"],
                    payload["territory"],
                    payload["modality"],
                    canonical_json(payload["revocable_rights"]),
                    canonical_json(payload["compatibility_floor_rights"]),
                    rn,
                    rd,
                    canonical_json(payload["delta"]),
                    1,
                    0,
                    payload["external_anchor_status"],
                    sequence,
                ),
            )
            return {"license_version_id": license_version_id, **payload}

        return self._mutate(
            "LICENSE_BRANCH_CREATED" if branch else "LICENSE_UPDATED",
            payload,
            authority_hash72,
            apply,
        )

    def license_update(self, *, parent_license_version_id: str, delta: Mapping[str, Any], authority_hash72: str) -> dict[str, Any]:
        return self._next_license_version(
            parent_license_version_id=parent_license_version_id,
            delta=delta,
            authority_hash72=authority_hash72,
            branch=False,
        )

    def license_branch(self, *, parent_license_version_id: str, delta: Mapping[str, Any], authority_hash72: str) -> dict[str, Any]:
        if not delta.get("territory") and not delta.get("modality"):
            raise ValueError("license branch requires territory or modality scope")
        merged = {**dict(delta), "legacy_policy": "FORKED_LICENSE"}
        return self._next_license_version(
            parent_license_version_id=parent_license_version_id,
            delta=merged,
            authority_hash72=authority_hash72,
            branch=True,
        )

    def license_activate(self, *, license_version_id: str, authority_hash72: str) -> dict[str, Any]:
        row = self._license_row(license_version_id)
        if row["expired"]:
            raise ValueError("expired license cannot be activated")
        payload = {
            "logical_license_id": row["logical_license_id"],
            "license_version_id": license_version_id,
        }

        def apply(conn: sqlite3.Connection, sequence: int, _: str) -> dict[str, Any]:
            conn.execute(
                "UPDATE license_versions SET active=0 WHERE logical_license_id=?",
                (row["logical_license_id"],),
            )
            conn.execute(
                "UPDATE license_versions SET active=1 WHERE license_version_id=?",
                (license_version_id,),
            )
            return {**payload, "active": True, "sequence": sequence}

        return self._mutate("LICENSE_ACTIVATED", payload, authority_hash72, apply)

    def license_inspect(self, *, logical_license_id: str | None = None, license_version_id: str | None = None) -> dict[str, Any]:
        if license_version_id:
            return self._license_dict(self._license_row(license_version_id))
        if not logical_license_id:
            raise ValueError("logical_license_id or license_version_id required")
        rows = self._connection.execute(
            "SELECT * FROM license_versions WHERE logical_license_id=? ORDER BY version",
            (logical_license_id,),
        ).fetchall()
        return {"logical_license_id": logical_license_id, "versions": [self._license_dict(row) for row in rows]}

    def ownership_inspect(self, logical_license_id: str) -> dict[str, Any]:
        row = self._connection.execute(
            "SELECT * FROM ownership WHERE logical_license_id=?", (logical_license_id,)
        ).fetchone()
        if row is None:
            raise KeyError("unknown license ownership")
        return {
            "logical_license_id": logical_license_id,
            "controller": row["controller"],
            "root_hash72": row["root_hash72"],
            "event_sequence": int(row["event_sequence"]),
        }

    def _active_candidates(
        self,
        logical_license_id: str,
        logical_content_id: str,
        territory: str | None,
        modality: str | None,
    ) -> list[sqlite3.Row]:
        rows = self._connection.execute(
            "SELECT * FROM license_versions WHERE logical_license_id=? AND active=1",
            (logical_license_id,),
        ).fetchall()
        candidates: list[tuple[int, sqlite3.Row]] = []
        for row in rows:
            if row["expired"]:
                continue
            if logical_content_id not in json.loads(row["controlled_content_ids_json"]):
                continue
            if row["territory"] is not None and row["territory"] != territory:
                continue
            if row["modality"] is not None and row["modality"] != modality:
                continue
            specificity = int(row["territory"] is not None) + int(row["modality"] is not None)
            candidates.append((specificity, row))
        if not candidates:
            return []
        best = max(score for score, _ in candidates)
        return [row for score, row in candidates if score == best]

    def _binding_row(self, binding_id: str) -> sqlite3.Row:
        row = self._connection.execute(
            "SELECT * FROM bindings WHERE binding_id=?", (binding_id,)
        ).fetchone()
        if row is None:
            raise KeyError(f"unknown binding: {binding_id}")
        return row

    def license_decision(
        self,
        *,
        logical_license_id: str,
        logical_content_id: str,
        principal: str,
        operation: str,
        target_egress: str,
        binding_id: str | None = None,
        territory: str | None = None,
        modality: str | None = None,
        external_context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        binding = self._binding_row(binding_id) if binding_id else None
        bound_license = self._license_dict(self._license_row(binding["license_version_id"])) if binding else None
        use_bound = bool(
            bound_license
            and bound_license["legacy_policy"] in {
                "LEGACY_BOUND",
                "OPT_IN_UPGRADE",
                "REVOCABLE_CAPABILITY",
            }
        )
        if use_bound:
            candidates = [self._license_row(binding["license_version_id"])]
        else:
            candidates = self._active_candidates(
                logical_license_id, logical_content_id, territory, modality
            )
        if not candidates:
            return self._decision_report("DENY", "NO_APPLICABLE_LICENSE", None, principal, operation, target_egress)
        if len(candidates) != 1:
            return self._decision_report("AMBIGUOUS", "MULTIPLE_APPLICABLE_LICENSES", None, principal, operation, target_egress)
        row = candidates[0]
        license_state = self._license_dict(row)
        if row["expired"] and not use_bound:
            return self._decision_report("DENY", "LICENSE_EXPIRED", license_state, principal, operation, target_egress)
        owner = self.ownership_inspect(logical_license_id)["controller"]
        delegated = False
        if principal != owner:
            drow = self._connection.execute(
                "SELECT rights_json FROM delegations WHERE logical_license_id=? AND principal=? AND active=1 ORDER BY creation_sequence DESC LIMIT 1",
                (logical_license_id, principal),
            ).fetchone()
            if drow is None or operation not in json.loads(drow["rights_json"]):
                return self._decision_report("DENY", "PRINCIPAL_NOT_AUTHORIZED", license_state, principal, operation, target_egress)
            delegated = True
        if operation not in license_state["rights"]:
            return self._decision_report("DENY", "RIGHT_NOT_GRANTED", license_state, principal, operation, target_egress)
        revoked = self._connection.execute(
            """SELECT 1 FROM revocations
               WHERE logical_license_id=? AND license_version_id=? AND operation=?
                 AND principal IN (?, '*') LIMIT 1""",
            (logical_license_id, row["license_version_id"], operation, principal),
        ).fetchone()
        if revoked is not None:
            return self._decision_report("DENY", "REVOCABLE_CAPABILITY_REVOKED", license_state, principal, operation, target_egress)
        report = self._decision_report("ALLOW", "AUTHORIZED", license_state, principal, operation, target_egress)
        report["delegated"] = delegated
        report["external_context_authority"] = False
        report["external_context_observed"] = bool(external_context)
        return report

    @staticmethod
    def _decision_report(
        decision: str,
        reason: str,
        license_state: Mapping[str, Any] | None,
        principal: str,
        operation: str,
        target_egress: str,
    ) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_188_LICENSE_DECISION_V1",
            "contract": CONTRACT_ID,
            "decision": decision,
            "reason": reason,
            "principal": principal,
            "operation": operation,
            "target_egress": target_egress,
            "license_version_id": license_state.get("license_version_id") if license_state else None,
            "legacy_policy": license_state.get("legacy_policy") if license_state else None,
            "obligations": license_state.get("obligations", {}) if license_state else {},
            "royalty": license_state.get("royalty", [0, 1]) if license_state else [0, 1],
            "human_report": f"{decision}: {reason}; operation={operation}; principal={principal}; egress={target_egress}",
        }

    def binding_create(
        self,
        *,
        binding_id: str,
        project_id: str,
        principal: str,
        content_version_id: str,
        license_version_id: str,
        operation: str,
        target_egress: str,
        authority_hash72: str,
        territory: str | None = None,
        modality: str | None = None,
    ) -> dict[str, Any]:
        content = self._content_row(content_version_id)
        license_state = self._license_dict(self._license_row(license_version_id))
        decision = self.license_decision(
            logical_license_id=license_state["logical_license_id"],
            logical_content_id=content["logical_content_id"],
            principal=principal,
            operation=operation,
            target_egress=target_egress,
            territory=territory,
            modality=modality,
        )
        if decision["decision"] != "ALLOW" or decision["license_version_id"] != license_version_id:
            raise PermissionError(f"binding admission rejected: {decision['reason']}")
        if self._connection.execute(
            "SELECT 1 FROM bindings WHERE binding_id=?", (binding_id,)
        ).fetchone():
            raise ValueError("binding already exists")
        payload = {
            "binding_id": binding_id,
            "project_id": project_id,
            "principal": principal,
            "logical_content_id": content["logical_content_id"],
            "content_version_id": content_version_id,
            "logical_license_id": license_state["logical_license_id"],
            "license_version_id": license_version_id,
            "rights_snapshot": license_state["rights"],
            "obligations_snapshot": license_state["obligations"],
            "operation": operation,
            "target_egress": target_egress,
        }

        def apply(conn: sqlite3.Connection, sequence: int, successor: str) -> dict[str, Any]:
            conn.execute(
                "INSERT INTO bindings VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    binding_id,
                    project_id,
                    principal,
                    content["logical_content_id"],
                    content_version_id,
                    license_state["logical_license_id"],
                    license_version_id,
                    canonical_json(license_state["rights"]),
                    canonical_json(license_state["obligations"]),
                    "ACTIVE",
                    sequence,
                ),
            )
            op_id = "op_" + hash72(
                "HHS-P188-ADMITTED-OPERATION",
                {"binding_id": binding_id, "operation": operation, "sequence": sequence},
            )
            conn.execute(
                "INSERT INTO admitted_operations VALUES(?,?,?,?,?,?,?,?)",
                (
                    op_id,
                    binding_id,
                    operation,
                    target_egress,
                    license_version_id,
                    content_version_id,
                    successor,
                    sequence,
                ),
            )
            return {"binding_id": binding_id, "operation_id": op_id, "decision": decision}

        return self._mutate("BINDING_CREATED", payload, authority_hash72, apply)

    def binding_inspect(self, binding_id: str) -> dict[str, Any]:
        row = self._binding_row(binding_id)
        result = dict(row)
        result["rights_snapshot"] = json.loads(result.pop("rights_snapshot_json"))
        result["obligations_snapshot"] = json.loads(result.pop("obligations_snapshot_json"))
        return result

    def graph_edge_create(
        self,
        *,
        project_id: str,
        source_node: str,
        target_node: str,
        authority_hash72: str,
    ) -> dict[str, Any]:
        payload = {
            "project_id": project_id,
            "source_node": source_node,
            "target_node": target_node,
        }

        def apply(conn: sqlite3.Connection, sequence: int, _: str) -> dict[str, Any]:
            conn.execute(
                "INSERT OR IGNORE INTO graph_edges VALUES(?,?,?,?)",
                (project_id, source_node, target_node, sequence),
            )
            return {**payload, "sequence": sequence}

        return self._mutate("GRAPH_EDGE_CREATED", payload, authority_hash72, apply)

    def impact(self, *, project_id: str, changed_nodes: Sequence[str]) -> dict[str, Any]:
        edges = self._connection.execute(
            "SELECT source_node,target_node FROM graph_edges WHERE project_id=?",
            (project_id,),
        ).fetchall()
        outgoing: dict[str, set[str]] = {}
        for row in edges:
            outgoing.setdefault(row["source_node"], set()).add(row["target_node"])
        seen = set(str(n) for n in changed_nodes)
        queue = list(seen)
        while queue:
            node = queue.pop(0)
            for target in sorted(outgoing.get(node, ())):
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        return {
            "project_id": project_id,
            "changed_nodes": list(changed_nodes),
            "affected_closure": sorted(seen),
        }

    def binding_upgrade(
        self,
        *,
        binding_id: str,
        new_content_version_id: str | None,
        new_license_version_id: str | None,
        authority_hash72: str,
        operation: str,
        target_egress: str,
        territory: str | None = None,
        modality: str | None = None,
    ) -> dict[str, Any]:
        old = self._binding_row(binding_id)
        content_version_id = new_content_version_id or old["content_version_id"]
        license_version_id = new_license_version_id or old["license_version_id"]
        content = self._content_row(content_version_id)
        license_state = self._license_dict(self._license_row(license_version_id))
        decision = self.license_decision(
            logical_license_id=license_state["logical_license_id"],
            logical_content_id=content["logical_content_id"],
            principal=old["principal"],
            operation=operation,
            target_egress=target_egress,
            territory=territory,
            modality=modality,
        )
        if decision["decision"] != "ALLOW" or decision["license_version_id"] != license_version_id:
            raise PermissionError(f"binding upgrade rejected: {decision['reason']}")
        affected = self.impact(project_id=old["project_id"], changed_nodes=[binding_id])
        payload = {
            "binding_id": binding_id,
            "from_content_version_id": old["content_version_id"],
            "to_content_version_id": content_version_id,
            "from_license_version_id": old["license_version_id"],
            "to_license_version_id": license_version_id,
            "affected_closure": affected["affected_closure"],
            "operation": operation,
            "target_egress": target_egress,
        }

        def apply(conn: sqlite3.Connection, sequence: int, successor: str) -> dict[str, Any]:
            conn.execute(
                """UPDATE bindings
                   SET content_version_id=?, license_version_id=?, rights_snapshot_json=?,
                       obligations_snapshot_json=?, creation_sequence=?
                   WHERE binding_id=?""",
                (
                    content_version_id,
                    license_version_id,
                    canonical_json(license_state["rights"]),
                    canonical_json(license_state["obligations"]),
                    sequence,
                    binding_id,
                ),
            )
            op_id = "op_" + hash72(
                "HHS-P188-UPGRADE-OPERATION",
                {"binding_id": binding_id, "sequence": sequence, "license_version_id": license_version_id},
            )
            conn.execute(
                "INSERT INTO admitted_operations VALUES(?,?,?,?,?,?,?,?)",
                (
                    op_id,
                    binding_id,
                    operation,
                    target_egress,
                    license_version_id,
                    content_version_id,
                    successor,
                    sequence,
                ),
            )
            return {**payload, "operation_id": op_id, "decision": decision}

        return self._mutate("BINDING_UPGRADED", payload, authority_hash72, apply)

    def ownership_transfer(
        self,
        *,
        logical_license_id: str,
        current_controller: str,
        new_controller: str,
        expected_root_hash72: str,
        authority_hash72: str,
    ) -> dict[str, Any]:
        current = self.ownership_inspect(logical_license_id)
        if current["controller"] != current_controller:
            raise PermissionError("current controller mismatch")
        if current["root_hash72"] != expected_root_hash72:
            raise ValueError("stale ownership root")
        payload = {
            "logical_license_id": logical_license_id,
            "from_controller": current_controller,
            "to_controller": new_controller,
            "previous_root_hash72": expected_root_hash72,
        }

        def apply(conn: sqlite3.Connection, sequence: int, successor: str) -> dict[str, Any]:
            root = hash72(
                "HHS-P188-OWNERSHIP-ROOT",
                {**payload, "sequence": sequence, "event_hash72": successor},
            )
            conn.execute(
                "UPDATE ownership SET controller=?, root_hash72=?, event_sequence=? WHERE logical_license_id=?",
                (new_controller, root, sequence, logical_license_id),
            )
            return {**payload, "ownership_root_hash72": root}

        return self._mutate("OWNERSHIP_TRANSFERRED", payload, authority_hash72, apply)

    def delegation_create(
        self,
        *,
        delegation_id: str,
        logical_license_id: str,
        controller: str,
        principal: str,
        rights: Sequence[str],
        authority_hash72: str,
    ) -> dict[str, Any]:
        current = self.ownership_inspect(logical_license_id)
        if current["controller"] != controller:
            raise PermissionError("controller does not own license")
        active_rows = self._connection.execute(
            "SELECT rights_json FROM license_versions WHERE logical_license_id=? AND active=1",
            (logical_license_id,),
        ).fetchall()
        granted = set().union(*(set(json.loads(row["rights_json"])) for row in active_rows)) if active_rows else set()
        requested = set(rights)
        if not requested.issubset(granted):
            raise PermissionError("delegation exceeds active rights")
        payload = {
            "delegation_id": delegation_id,
            "logical_license_id": logical_license_id,
            "controller": controller,
            "principal": principal,
            "rights": sorted(requested),
        }

        def apply(conn: sqlite3.Connection, sequence: int, _: str) -> dict[str, Any]:
            conn.execute(
                "INSERT INTO delegations VALUES(?,?,?,?,?,?)",
                (delegation_id, logical_license_id, principal, canonical_json(sorted(requested)), 1, sequence),
            )
            return payload

        return self._mutate("DELEGATION_CREATED", payload, authority_hash72, apply)

    def revoke(
        self,
        *,
        revocation_id: str,
        license_version_id: str,
        principal: str,
        operation: str,
        authority_hash72: str,
    ) -> dict[str, Any]:
        state = self._license_dict(self._license_row(license_version_id))
        if operation not in state["revocable_rights"]:
            raise PermissionError("capability was not declared revocable")
        payload = {
            "revocation_id": revocation_id,
            "logical_license_id": state["logical_license_id"],
            "license_version_id": license_version_id,
            "principal": principal,
            "operation": operation,
        }

        def apply(conn: sqlite3.Connection, sequence: int, _: str) -> dict[str, Any]:
            conn.execute(
                "INSERT INTO revocations VALUES(?,?,?,?,?,?)",
                (
                    revocation_id,
                    state["logical_license_id"],
                    license_version_id,
                    principal,
                    operation,
                    sequence,
                ),
            )
            return payload

        return self._mutate("CAPABILITY_REVOKED", payload, authority_hash72, apply)

    def expire(self, *, license_version_id: str, authority_hash72: str) -> dict[str, Any]:
        row = self._license_row(license_version_id)
        payload = {
            "logical_license_id": row["logical_license_id"],
            "license_version_id": license_version_id,
        }

        def apply(conn: sqlite3.Connection, sequence: int, _: str) -> dict[str, Any]:
            conn.execute(
                "UPDATE license_versions SET expired=1, active=0 WHERE license_version_id=?",
                (license_version_id,),
            )
            return {**payload, "expired": True, "sequence": sequence}

        return self._mutate("LICENSE_EXPIRED", payload, authority_hash72, apply)

    def obligations_inspect(self, binding_ids: Sequence[str]) -> dict[str, Any]:
        rows = [self.binding_inspect(binding_id) for binding_id in binding_ids]
        return {
            "bindings": list(binding_ids),
            "obligations": [
                {"binding_id": row["binding_id"], "obligations": row["obligations_snapshot"]}
                for row in rows
            ],
        }

    def royalties_inspect(self, binding_ids: Sequence[str]) -> dict[str, Any]:
        total = Fraction(0, 1)
        lines = []
        for binding_id in binding_ids:
            binding = self.binding_inspect(binding_id)
            state = self._license_dict(self._license_row(binding["license_version_id"]))
            amount = Fraction(state["royalty"][0], state["royalty"][1])
            total += amount
            lines.append(
                {
                    "binding_id": binding_id,
                    "license_version_id": state["license_version_id"],
                    "royalty": [amount.numerator, amount.denominator],
                    "attribution": state["obligations"].get("attribution"),
                }
            )
        return {
            "lines": lines,
            "aggregate_royalty": [total.numerator, total.denominator],
        }

    def compile_egress(self, binding_ids: Sequence[str]) -> dict[str, Any]:
        obligations = []
        families = set()
        incompatible: list[str] = []
        for binding_id in binding_ids:
            binding = self.binding_inspect(binding_id)
            state = self._license_dict(self._license_row(binding["license_version_id"]))
            ob = dict(state["obligations"])
            family = ob.get("license_family")
            if family:
                families.add(str(family))
            obligations.append((binding_id, ob))
        for binding_id, ob in obligations:
            conflicts = set(str(x) for x in ob.get("incompatible_with", []))
            hit = sorted(conflicts.intersection(families))
            if hit:
                incompatible.append(f"{binding_id}:{','.join(hit)}")
        return {
            "classification": "LICENSE_EGRESS_COMPATIBLE" if not incompatible else "LICENSE_EGRESS_INCOMPATIBLE",
            "compatible": not incompatible,
            "conflicts": incompatible,
            "royalties": self.royalties_inspect(binding_ids),
            "obligations": self.obligations_inspect(binding_ids),
        }

    def replay(self) -> dict[str, Any]:
        predecessor = ZERO_HASH72
        expected_sequence = 1
        for row in self._connection.execute("SELECT * FROM events ORDER BY sequence"):
            if int(row["sequence"]) != expected_sequence:
                return {"valid": False, "reason": "SEQUENCE_DRIFT", "events": expected_sequence - 1}
            if row["predecessor_hash72"] != predecessor:
                return {"valid": False, "reason": "PREDECESSOR_DRIFT", "events": expected_sequence - 1}
            payload = json.loads(row["payload_json"])
            event_payload = {
                "contract": CONTRACT_ID,
                "sequence": expected_sequence,
                "event_type": row["event_type"],
                "payload": payload,
                "authority_hash72": row["authority_hash72"],
            }
            successor = hash72(
                "HHS-P188-LICENSE-EVENT",
                {"predecessor_hash72": predecessor, **event_payload},
            )
            closure = hash72(
                "HHS-P188-LICENSE-CLOSURE",
                {
                    "predecessor_hash72": predecessor,
                    "successor_hash72": successor,
                    "sequence": expected_sequence,
                    "event_type": row["event_type"],
                },
            )
            if successor != row["successor_hash72"] or predecessor + successor + closure != row["hash216"]:
                return {"valid": False, "reason": "HASH_DRIFT", "events": expected_sequence - 1}
            predecessor = successor
            expected_sequence += 1
        return {
            "valid": True,
            "events": expected_sequence - 1,
            "root_hash72": predecessor,
            "hash216_complete": True,
        }

    def _verify_materialized_state(self) -> dict[str, Any]:
        errors: list[str] = []

        def event(sequence: int) -> sqlite3.Row | None:
            return self._connection.execute(
                "SELECT * FROM events WHERE sequence=?", (int(sequence),)
            ).fetchone()

        for row in self._connection.execute("SELECT * FROM content_versions"):
            erow = event(row["creation_sequence"])
            if erow is None or erow["event_type"] not in {"CONTENT_CREATED", "CONTENT_VERSION_CREATED"}:
                errors.append(f"content_event:{row['content_version_id']}")
                continue
            payload = json.loads(erow["payload_json"])
            expected_id = "cv_" + hash72("HHS-P188-CONTENT-VERSION", payload)
            if expected_id != row["content_version_id"]:
                errors.append(f"content_identity:{row['content_version_id']}")
            if (
                payload.get("logical_content_id") != row["logical_content_id"]
                or int(payload.get("version", -1)) != int(row["version"])
                or payload.get("content_hash") != row["content_hash"]
                or payload.get("parents") != json.loads(row["parents_json"])
                or payload.get("embedded_license_ids") != json.loads(row["embedded_license_ids_json"])
            ):
                errors.append(f"content_materialization:{row['content_version_id']}")

        for row in self._connection.execute("SELECT * FROM license_versions"):
            erow = event(row["creation_sequence"])
            if erow is None or erow["event_type"] not in {
                "LICENSE_CREATED",
                "LICENSE_UPDATED",
                "LICENSE_BRANCH_CREATED",
            }:
                errors.append(f"license_event:{row['license_version_id']}")
                continue
            payload = json.loads(erow["payload_json"])
            expected_id = "lv_" + hash72("HHS-P188-LICENSE-VERSION", payload)
            if expected_id != row["license_version_id"]:
                errors.append(f"license_identity:{row['license_version_id']}")
            checks = {
                "logical_license_id": row["logical_license_id"],
                "version": int(row["version"]),
                "parents": json.loads(row["parents_json"]),
                "controlled_content_ids": json.loads(row["controlled_content_ids_json"]),
                "rights": json.loads(row["rights_json"]),
                "obligations": json.loads(row["obligations_json"]),
                "legacy_policy": row["legacy_policy"],
                "controller": row["controller_at_creation"],
                "territory": row["territory"],
                "modality": row["modality"],
                "revocable_rights": json.loads(row["revocable_rights_json"]),
                "compatibility_floor_rights": json.loads(row["compatibility_floor_json"]),
                "royalty": [int(row["royalty_numerator"]), int(row["royalty_denominator"])],
                "delta": json.loads(row["delta_json"]),
                "external_anchor_status": row["external_anchor_status"],
            }
            for key, actual in checks.items():
                if payload.get(key) != actual:
                    errors.append(f"license_materialization:{row['license_version_id']}:{key}")

        for row in self._connection.execute("SELECT * FROM bindings"):
            erow = event(row["creation_sequence"])
            if erow is None or erow["event_type"] not in {"BINDING_CREATED", "BINDING_UPGRADED"}:
                errors.append(f"binding_event:{row['binding_id']}")
                continue
            payload = json.loads(erow["payload_json"])
            if payload.get("binding_id") != row["binding_id"]:
                errors.append(f"binding_identity:{row['binding_id']}")
            expected_content = payload.get(
                "to_content_version_id", payload.get("content_version_id")
            )
            expected_license = payload.get(
                "to_license_version_id", payload.get("license_version_id")
            )
            if expected_content != row["content_version_id"] or expected_license != row["license_version_id"]:
                errors.append(f"binding_materialization:{row['binding_id']}")

        for row in self._connection.execute("SELECT * FROM admitted_operations"):
            erow = event(row["event_sequence"])
            if (
                erow is None
                or erow["successor_hash72"] != row["receipt_hash72"]
                or self._connection.execute(
                    "SELECT 1 FROM bindings WHERE binding_id=?", (row["binding_id"],)
                ).fetchone() is None
            ):
                errors.append(f"operation_materialization:{row['operation_id']}")

        for row in self._connection.execute("SELECT * FROM revocations"):
            erow = event(row["creation_sequence"])
            payload = json.loads(erow["payload_json"]) if erow is not None else {}
            if erow is None or erow["event_type"] != "CAPABILITY_REVOKED" or payload.get("revocation_id") != row["revocation_id"]:
                errors.append(f"revocation_materialization:{row['revocation_id']}")

        for row in self._connection.execute("SELECT * FROM delegations"):
            erow = event(row["creation_sequence"])
            payload = json.loads(erow["payload_json"]) if erow is not None else {}
            if erow is None or erow["event_type"] != "DELEGATION_CREATED" or payload.get("delegation_id") != row["delegation_id"]:
                errors.append(f"delegation_materialization:{row['delegation_id']}")

        for row in self._connection.execute("SELECT * FROM graph_edges"):
            erow = event(row["creation_sequence"])
            payload = json.loads(erow["payload_json"]) if erow is not None else {}
            if (
                erow is None
                or erow["event_type"] != "GRAPH_EDGE_CREATED"
                or payload.get("project_id") != row["project_id"]
                or payload.get("source_node") != row["source_node"]
                or payload.get("target_node") != row["target_node"]
            ):
                errors.append(
                    f"graph_edge_materialization:{row['project_id']}:{row['source_node']}:{row['target_node']}"
                )

        for row in self._connection.execute("SELECT * FROM ownership"):
            erow = event(row["event_sequence"])
            if erow is None:
                errors.append(f"ownership_event:{row['logical_license_id']}")
                continue
            payload = json.loads(erow["payload_json"])
            if erow["event_type"] == "LICENSE_CREATED":
                controller = payload.get("controller")
                expected_root = hash72(
                    "HHS-P188-OWNERSHIP-ROOT",
                    {
                        "logical_license_id": row["logical_license_id"],
                        "controller": controller,
                        "sequence": int(erow["sequence"]),
                        "event_hash72": erow["successor_hash72"],
                    },
                )
            elif erow["event_type"] == "OWNERSHIP_TRANSFERRED":
                controller = payload.get("to_controller")
                expected_root = hash72(
                    "HHS-P188-OWNERSHIP-ROOT",
                    {
                        **payload,
                        "sequence": int(erow["sequence"]),
                        "event_hash72": erow["successor_hash72"],
                    },
                )
            else:
                errors.append(f"ownership_event_type:{row['logical_license_id']}")
                continue
            if controller != row["controller"] or expected_root != row["root_hash72"]:
                errors.append(f"ownership_materialization:{row['logical_license_id']}")

        return {"valid": not errors, "errors": errors}

    def verify(self) -> dict[str, Any]:
        replay = self.replay()
        materialized = self._verify_materialized_state()
        immutable_ids = (
            self._connection.execute("SELECT COUNT(*) FROM content_versions").fetchone()[0],
            self._connection.execute("SELECT COUNT(*) FROM license_versions").fetchone()[0],
        )
        return {
            "schema": "HHS_PASS_188_LICENSE_VERIFY_V1",
            "contract": CONTRACT_ID,
            "classification": COMPLETION_CLASSIFICATION if replay["valid"] and materialized["valid"] else "HHS_PASS_188_LICENSE_VERIFY_FAILED",
            "replay": replay,
            "materialized_state": materialized,
            "content_versions": int(immutable_ids[0]),
            "license_versions": int(immutable_ids[1]),
            "external_chain_required": False,
            "wallet_authority": False,
            "browser_local_authority": False,
            "marketplace_authority": False,
            "floating_point_canonical_authority": False,
            "new_vm81_authority": False,
            "new_hash72_clock": False,
        }

    def export_evidence(self, path: str | os.PathLike[str]) -> dict[str, Any]:
        verification = self.verify()
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            **verification,
            "operations": [
                row["event_type"]
                for row in self._connection.execute("SELECT event_type FROM events ORDER BY sequence")
            ],
        }
        destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return payload

    def checkpoint(self, path: str | os.PathLike[str]) -> dict[str, Any]:
        target = Path(path)
        if target.exists():
            raise FileExistsError(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            self._connection.execute("PRAGMA wal_checkpoint(FULL)")
            destination = sqlite3.connect(str(target))
            try:
                self._connection.backup(destination)
            finally:
                destination.close()
        replay = self.replay()
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        return {"path": str(target), "sha256": digest, "events": replay["events"], "root_hash72": replay["root_hash72"]}

    @classmethod
    def recover(
        cls,
        checkpoint_path: str | os.PathLike[str],
        destination_path: str | os.PathLike[str],
        expected_sha256: str,
        expected_events: int,
        expected_root_hash72: str,
    ) -> "LicenseLineageAuthority":
        source = Path(checkpoint_path)
        destination = Path(destination_path)
        if destination.exists():
            raise FileExistsError(destination)
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected_sha256:
            raise ValueError("checkpoint digest mismatch")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        authority = cls(destination)
        replay = authority.replay()
        if (
            not replay["valid"]
            or replay["events"] != int(expected_events)
            or replay["root_hash72"] != expected_root_hash72
        ):
            authority.close()
            destination.unlink(missing_ok=True)
            raise ValueError("recovered authority does not match captured replay root")
        return authority


CLI_OPERATIONS = {
    "content-create": "content_create",
    "content-version": "content_version",
    "content-compare": "content_compare",
    "license-create": "license_create",
    "license-update": "license_update",
    "license-branch": "license_branch",
    "license-activate": "license_activate",
    "license-inspect": "license_inspect",
    "license-decision": "license_decision",
    "binding-create": "binding_create",
    "binding-inspect": "binding_inspect",
    "binding-upgrade": "binding_upgrade",
    "ownership-transfer": "ownership_transfer",
    "delegation-create": "delegation_create",
    "revoke": "revoke",
    "expire": "expire",
    "obligations-inspect": "obligations_inspect",
    "royalties-inspect": "royalties_inspect",
    "impact": "impact",
    "replay": "replay",
    "verify": "verify",
    "export-evidence": "export_evidence",
    "graph-edge-create": "graph_edge_create",
    "compile-egress": "compile_egress",
}


def execute_operation(authority: LicenseLineageAuthority, operation: str, args: Mapping[str, Any]) -> Any:
    method_name = CLI_OPERATIONS.get(operation, operation.replace(" ", "_"))
    if not hasattr(authority, method_name):
        raise KeyError(f"unknown Pass 188 operation: {operation}")
    return getattr(authority, method_name)(**dict(args))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HHS Pass 188 versioned content-license runtime")
    parser.add_argument("--db", required=True)
    parser.add_argument("operation", choices=sorted(CLI_OPERATIONS))
    parser.add_argument("--json", default="{}")
    ns = parser.parse_args(argv)
    args = json.loads(ns.json)
    with LicenseLineageAuthority(ns.db) as authority:
        result = execute_operation(authority, ns.operation, args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
