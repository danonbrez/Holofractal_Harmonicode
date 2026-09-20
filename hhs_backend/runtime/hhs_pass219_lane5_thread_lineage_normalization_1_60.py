"""Pass 219 Lane 5 1.60: normalized thread-lineage hierarchical memory.

One physical SQLite fabric is partitioned by a boundary-derived Hash216 thread
root.  The root is generated from scope, evolutionary lineage, PQC witness and
the exact 5,184-character BigInt transcription plus its ordered palindromic
read witness.  This module adds no canonical VM81/Hash72/Hash216 commit authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, Iterable, Mapping

from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import split_hash216
from hhs_python.runtime.hhs_pass205_continuation_bridge import Pass205NativeBridge
from hhs_runtime.harmonicode_lane5_bigint_transcription_v1 import transcribe_5184
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    SERIALIZED_CHARACTERS,
    VM81_CELLS,
    serialize_offsets_5184,
)

SCHEMA = "HHS_PASS_219_LANE5_THREAD_LINEAGE_NORMALIZATION_MEMORY_1_60"
THEOREM_ID = "HHS-T5184-005"
ZERO_OFFSETS = (0,) * VM81_CELLS
ZERO_SERIALIZATION_5184 = serialize_offsets_5184(ZERO_OFFSETS)
_SAFE_KIND = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")


class ThreadLineageMemoryError(ValueError):
    pass


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ThreadLineageMemoryError(f"floating-point thread metadata forbidden at {path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_float(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple, set, frozenset)):
        for index, item in enumerate(value):
            _reject_float(item, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def _validate_hash216(value: str, name: str) -> str:
    try:
        split_hash216(value)
    except Exception as exc:
        raise ThreadLineageMemoryError(f"{name} is not canonical Hash216") from exc
    return value


def _validate_serialization(value: str) -> str:
    if not isinstance(value, str) or len(value) != SERIALIZED_CHARACTERS:
        raise ThreadLineageMemoryError("BigInt serialization must be exactly 5184 characters")
    offsets = transcribe_5184(value)
    if not isinstance(offsets, tuple) or len(offsets) != VM81_CELLS:
        raise ThreadLineageMemoryError("BigInt serialization did not decode to VM81 offsets")
    if transcribe_5184(offsets) != value:
        raise ThreadLineageMemoryError("BigInt serialization is not canonical")
    return value


def _caps(values: Iterable[str]) -> tuple[str, ...]:
    result = tuple(sorted({str(value) for value in values}))
    if not result or any(not item or len(item) > 128 for item in result):
        raise ThreadLineageMemoryError("invalid empty/oversized thread scope")
    return result


@dataclass(frozen=True)
class ThreadBoundary:
    scope_hash216: str
    thread_root_hash216: str
    evolution_hash216: str
    lineage_hash216: str
    pqc_witness_hash216: str
    palindrome_hash216: str
    bigint_serialization_5184: str
    capabilities: tuple[str, ...]

    @property
    def normalized_zero(self) -> bool:
        return self.bigint_serialization_5184 == ZERO_SERIALIZATION_5184

    @property
    def virtual_root(self) -> str:
        return (
            f"/scope/{self.scope_hash216}/thread/{self.thread_root_hash216}"
            f"/lineage/{self.lineage_hash216}"
        )


@dataclass(frozen=True)
class ThreadIndexRecord:
    scope_hash216: str
    thread_root_hash216: str
    lineage_hash216: str
    object_hash216: str
    object_type: str
    object_ref: str
    metadata_hash216: str

    @property
    def virtual_path(self) -> str:
        return (
            f"/scope/{self.scope_hash216}/thread/{self.thread_root_hash216}"
            f"/lineage/{self.lineage_hash216}/{self.object_type}/{self.object_hash216}"
        )


class Pass219Lane5ThreadLineageMemory:
    """Shared physical SQL fabric with fail-closed logical thread partitions."""

    def __init__(self, state_root: str | Path) -> None:
        self.state_root = Path(state_root).resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.state_root / "lane5_thread_lineage_memory.sqlite3"
        self.native = Pass205NativeBridge()
        self.db = sqlite3.connect(self.database_path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def __enter__(self) -> "Pass219Lane5ThreadLineageMemory":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self.db.close()

    def _hash(self, domain: str, value: Any) -> str:
        raw = domain.encode("ascii") + b"\0" + _canonical(value)
        return _validate_hash216(self.native.hash216_bytes(raw), domain)

    def _scope_hash(self, capabilities: tuple[str, ...]) -> str:
        return self._hash("HHS-P219-LANE5-THREAD-SCOPE-1.60", list(capabilities))

    def derive_boundary(
        self,
        *,
        evolution_hash216: str,
        lineage_hash216: str,
        pqc_witness_hash216: str,
        bigint_serialization_5184: str,
        capabilities: Iterable[str],
    ) -> ThreadBoundary:
        evolution = _validate_hash216(evolution_hash216, "evolution_hash216")
        lineage = _validate_hash216(lineage_hash216, "lineage_hash216")
        pqc = _validate_hash216(pqc_witness_hash216, "pqc_witness_hash216")
        serialized = _validate_serialization(bigint_serialization_5184)
        caps = _caps(capabilities)
        scope = self._scope_hash(caps)
        palindrome = self._hash(
            "HHS-P219-LANE5-THREAD-PALINDROME-1.60",
            {"forward": serialized, "reverse": serialized[::-1]},
        )
        root = self._hash(
            "HHS-P219-LANE5-THREAD-ROOT-1.60",
            {
                "scope_hash216": scope,
                "evolution_hash216": evolution,
                "lineage_hash216": lineage,
                "pqc_witness_hash216": pqc,
                "palindrome_hash216": palindrome,
                "bigint_serialization_5184": serialized,
            },
        )
        return ThreadBoundary(scope, root, evolution, lineage, pqc, palindrome, serialized, caps)

    def register_thread(
        self,
        *,
        evolution_hash216: str,
        lineage_hash216: str,
        pqc_witness_hash216: str,
        capabilities: Iterable[str],
        bigint_serialization_5184: str = ZERO_SERIALIZATION_5184,
    ) -> ThreadBoundary:
        b = self.derive_boundary(
            evolution_hash216=evolution_hash216,
            lineage_hash216=lineage_hash216,
            pqc_witness_hash216=pqc_witness_hash216,
            bigint_serialization_5184=bigint_serialization_5184,
            capabilities=capabilities,
        )
        old = self.db.execute(
            "SELECT * FROM lane5_thread_roots WHERE thread_root_hash216=?", (b.thread_root_hash216,)
        ).fetchone()
        if old is not None:
            loaded = self._row_boundary(old)
            if loaded != b:
                raise ThreadLineageMemoryError("thread root collision")
            return loaded
        self.db.execute(
            """INSERT INTO lane5_thread_roots(
                 scope_hash216,thread_root_hash216,evolution_hash216,lineage_hash216,
                 pqc_witness_hash216,palindrome_hash216,bigint_serialization_5184,
                 capabilities_json
               ) VALUES(?,?,?,?,?,?,?,?)""",
            (
                b.scope_hash216, b.thread_root_hash216, b.evolution_hash216, b.lineage_hash216,
                b.pqc_witness_hash216, b.palindrome_hash216, b.bigint_serialization_5184,
                _canonical(list(b.capabilities)).decode("utf-8"),
            ),
        )
        self.db.commit()
        return b

    def _init_schema(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS lane5_thread_roots(
              sequence INTEGER PRIMARY KEY AUTOINCREMENT,
              scope_hash216 TEXT NOT NULL,
              thread_root_hash216 TEXT NOT NULL UNIQUE,
              evolution_hash216 TEXT NOT NULL,
              lineage_hash216 TEXT NOT NULL,
              pqc_witness_hash216 TEXT NOT NULL,
              palindrome_hash216 TEXT NOT NULL,
              bigint_serialization_5184 TEXT NOT NULL,
              capabilities_json TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS lane5_thread_roots_scope
              ON lane5_thread_roots(scope_hash216,lineage_hash216,sequence);
            CREATE TABLE IF NOT EXISTS lane5_thread_index(
              sequence INTEGER PRIMARY KEY AUTOINCREMENT,
              scope_hash216 TEXT NOT NULL,
              thread_root_hash216 TEXT NOT NULL,
              lineage_hash216 TEXT NOT NULL,
              object_hash216 TEXT NOT NULL,
              object_type TEXT NOT NULL,
              object_ref TEXT NOT NULL,
              metadata_hash216 TEXT NOT NULL,
              UNIQUE(scope_hash216,thread_root_hash216,lineage_hash216,object_hash216),
              FOREIGN KEY(thread_root_hash216) REFERENCES lane5_thread_roots(thread_root_hash216)
            );
            CREATE INDEX IF NOT EXISTS lane5_thread_index_partition
              ON lane5_thread_index(scope_hash216,thread_root_hash216,lineage_hash216,sequence);
            CREATE TABLE IF NOT EXISTS lane5_thread_bridges(
              sequence INTEGER PRIMARY KEY AUTOINCREMENT,
              source_thread_root_hash216 TEXT NOT NULL,
              target_thread_root_hash216 TEXT NOT NULL,
              lineage_hash216 TEXT NOT NULL,
              shared_scope_hash216 TEXT NOT NULL,
              capabilities_json TEXT NOT NULL,
              UNIQUE(source_thread_root_hash216,target_thread_root_hash216,lineage_hash216,shared_scope_hash216)
            );
            """
        )
        self.db.commit()

    def _row_boundary(self, row: sqlite3.Row) -> ThreadBoundary:
        b = ThreadBoundary(
            str(row["scope_hash216"]), str(row["thread_root_hash216"]),
            str(row["evolution_hash216"]), str(row["lineage_hash216"]),
            str(row["pqc_witness_hash216"]), str(row["palindrome_hash216"]),
            str(row["bigint_serialization_5184"]),
            tuple(json.loads(str(row["capabilities_json"]))),
        )
        rebuilt = self.derive_boundary(
            evolution_hash216=b.evolution_hash216,
            lineage_hash216=b.lineage_hash216,
            pqc_witness_hash216=b.pqc_witness_hash216,
            bigint_serialization_5184=b.bigint_serialization_5184,
            capabilities=b.capabilities,
        )
        if rebuilt != b:
            raise ThreadLineageMemoryError("stored thread boundary reconstruction failed")
        return b

    def thread(self, root: str) -> ThreadBoundary:
        root = _validate_hash216(root, "thread_root_hash216")
        row = self.db.execute(
            "SELECT * FROM lane5_thread_roots WHERE thread_root_hash216=?", (root,)
        ).fetchone()
        if row is None:
            raise ThreadLineageMemoryError("unknown thread root")
        return self._row_boundary(row)

    def create_shared_scope(
        self,
        *,
        source_thread_root_hash216: str,
        target_thread_root_hash216: str,
        capabilities: Iterable[str],
    ) -> dict[str, Any]:
        source, target = self.thread(source_thread_root_hash216), self.thread(target_thread_root_hash216)
        if source.thread_root_hash216 == target.thread_root_hash216:
            raise ThreadLineageMemoryError("shared scope requires distinct threads")
        if source.lineage_hash216 != target.lineage_hash216:
            raise ThreadLineageMemoryError("cross-thread sharing requires matching evolutionary lineage")
        shared = _caps(capabilities)
        if not set(shared).issubset(set(source.capabilities) & set(target.capabilities)):
            raise ThreadLineageMemoryError("shared scope would widen authority")
        shared_scope = self._scope_hash(shared)
        self.db.execute(
            """INSERT OR IGNORE INTO lane5_thread_bridges(
                 source_thread_root_hash216,target_thread_root_hash216,lineage_hash216,
                 shared_scope_hash216,capabilities_json
               ) VALUES(?,?,?,?,?)""",
            (
                source.thread_root_hash216, target.thread_root_hash216, source.lineage_hash216,
                shared_scope, _canonical(list(shared)).decode("utf-8"),
            ),
        )
        self.db.commit()
        return {
            "source_thread_root_hash216": source.thread_root_hash216,
            "target_thread_root_hash216": target.thread_root_hash216,
            "lineage_hash216": source.lineage_hash216,
            "shared_scope_hash216": shared_scope,
            "capabilities": shared,
            "scope_expansion": False,
        }

    def index_object(
        self,
        *,
        thread_root_hash216: str,
        object_hash216: str,
        object_type: str,
        object_ref: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> ThreadIndexRecord:
        b = self.thread(thread_root_hash216)
        obj = _validate_hash216(object_hash216, "object_hash216")
        kind, ref = str(object_type), str(object_ref)
        if not _SAFE_KIND.fullmatch(kind) or not ref:
            raise ThreadLineageMemoryError("invalid object type/ref")
        payload = {
            "scope_hash216": b.scope_hash216,
            "thread_root_hash216": b.thread_root_hash216,
            "lineage_hash216": b.lineage_hash216,
            "object_hash216": obj,
            "object_type": kind,
            "object_ref": ref,
            "metadata": dict(metadata or {}),
        }
        metadata_hash = self._hash("HHS-P219-LANE5-THREAD-INDEX-METADATA-1.60", payload)
        rec = ThreadIndexRecord(
            b.scope_hash216, b.thread_root_hash216, b.lineage_hash216,
            obj, kind, ref, metadata_hash,
        )
        self.db.execute(
            """INSERT OR REPLACE INTO lane5_thread_index(
                 scope_hash216,thread_root_hash216,lineage_hash216,object_hash216,
                 object_type,object_ref,metadata_hash216
               ) VALUES(?,?,?,?,?,?,?)""",
            (
                rec.scope_hash216, rec.thread_root_hash216, rec.lineage_hash216,
                rec.object_hash216, rec.object_type, rec.object_ref, rec.metadata_hash216,
            ),
        )
        self.db.commit()
        return rec

    def authorized_index(
        self,
        *,
        requester_thread_root_hash216: str,
        required_capabilities: Iterable[str],
        target_thread_root_hash216: str | None = None,
    ) -> tuple[ThreadIndexRecord, ...]:
        requester = self.thread(requester_thread_root_hash216)
        target = self.thread(target_thread_root_hash216 or requester.thread_root_hash216)
        required = set(_caps(required_capabilities))
        if requester.thread_root_hash216 == target.thread_root_hash216:
            available = set(requester.capabilities)
        else:
            if requester.lineage_hash216 != target.lineage_hash216:
                raise ThreadLineageMemoryError("cross-thread lineage mismatch")
            rows = self.db.execute(
                """SELECT capabilities_json FROM lane5_thread_bridges
                   WHERE source_thread_root_hash216=? AND target_thread_root_hash216=?
                     AND lineage_hash216=? ORDER BY sequence""",
                (requester.thread_root_hash216, target.thread_root_hash216, target.lineage_hash216),
            ).fetchall()
            if not rows:
                raise ThreadLineageMemoryError("cross-thread scope is not explicitly admitted")
            available = set()
            for row in rows:
                available.update(json.loads(str(row["capabilities_json"])))
        if not required.issubset(available):
            raise ThreadLineageMemoryError("requested operation exceeds admitted thread scope")

        # Security filter precedes any vector ranking: unauthorized candidates
        # never enter the searchable population.
        rows = self.db.execute(
            """SELECT scope_hash216,thread_root_hash216,lineage_hash216,object_hash216,
                      object_type,object_ref,metadata_hash216
               FROM lane5_thread_index
               WHERE scope_hash216=? AND thread_root_hash216=? AND lineage_hash216=?
               ORDER BY sequence""",
            (target.scope_hash216, target.thread_root_hash216, target.lineage_hash216),
        ).fetchall()
        return tuple(
            ThreadIndexRecord(
                str(r["scope_hash216"]), str(r["thread_root_hash216"]), str(r["lineage_hash216"]),
                str(r["object_hash216"]), str(r["object_type"]), str(r["object_ref"]),
                str(r["metadata_hash216"]),
            )
            for r in rows
        )

    def status(self) -> dict[str, Any]:
        synchronous = int(self.db.execute("PRAGMA synchronous").fetchone()[0])
        return {
            "schema": SCHEMA,
            "theorem": THEOREM_ID,
            "journal_mode": str(self.db.execute("PRAGMA journal_mode").fetchone()[0]),
            "synchronous_full": synchronous == 2,
            "thread_roots": int(self.db.execute("SELECT COUNT(*) FROM lane5_thread_roots").fetchone()[0]),
            "indexed_objects": int(self.db.execute("SELECT COUNT(*) FROM lane5_thread_index").fetchone()[0]),
            "shared_scope_bridges": int(self.db.execute("SELECT COUNT(*) FROM lane5_thread_bridges").fetchone()[0]),
            "physical_database_fabric": "shared",
            "logical_thread_indexes": True,
            "normalized_zero_offsets": len(ZERO_OFFSETS) == 81 and not any(ZERO_OFFSETS),
            "normalized_serialization_characters": len(ZERO_SERIALIZATION_5184),
            "thread_index_is_boundary_derived": True,
            "namespace_prefilter_before_vector_rank": True,
            "scope_union_escalation_allowed": False,
            "cross_thread_access_requires_explicit_scope": True,
            "cross_thread_access_requires_matching_lineage": True,
            "pqc_witness_required": True,
            "floating_point_canonical_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_commit_authority": False,
        }


def normalized_genesis_witness() -> dict[str, Any]:
    offsets = transcribe_5184(ZERO_SERIALIZATION_5184)
    return {
        "schema": "HHS_PASS_219_LANE5_NORMALIZED_GENESIS_WITNESS_1_60",
        "theorem": THEOREM_ID,
        "vm81_cells": VM81_CELLS,
        "serialized_characters": len(ZERO_SERIALIZATION_5184),
        "offsets": offsets,
        "all_qudit_offsets_zero": offsets == ZERO_OFFSETS,
        "same_transcription_operation_roundtrip": transcribe_5184(offsets) == ZERO_SERIALIZATION_5184,
        "underlying_transition_logic_modified": False,
        "floating_point_canonical_authority": False,
    }
