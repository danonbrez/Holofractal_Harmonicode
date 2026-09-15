"""Persistent Lane 5 Hash216 composition memory, Pass 219 1.39.

1.38 proves and seals reusable composition jumps in-process. 1.39 binds those
validated records to the inherited Pass 174/194 durable encrypted vector-store
substrate so a candidate route survives process restart and remains searchable
through the 1.37 GPU/vector fabric.

Persistence is not canonical transition authority. The durable record is a
candidate-memory object only; canonical VM81/Hash72/Hash216 mutation still
requires the inherited signed environmental VM81 admission path.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import operator
from pathlib import Path
import sqlite3
import struct
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass194_multimodal_storage_training_v1 import (
    GENESIS_IDENTITY,
    LEGACY_FOUNDATION_ROOT,
)
from hhs_backend.runtime.hhs_pass219_lane5_hash216_composition_jump_store_1_38 import (
    Pass219Lane5Hash216CompositionJumpStore,
    TraceRoots,
    ValidatedHash216CompositionJump,
)
from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import (
    Hash216CompositionCandidate,
    split_hash216,
)
from hhs_python.runtime.hhs_pass205_continuation_bridge import (
    CELL_COUNT,
    Pass205NativeBridge,
)
from hhs_python.runtime.hhs_pass219_lane5_composition_jump_bridge import (
    signature64_from_hash216,
)
from hhs_python.runtime.hhs_pass219_lane5_persistent_composition_memory_bridge import (
    CYCLE,
    SNAPSHOT_BYTES,
    Pass219Lane5PersistentCompositionMemoryBridge,
    signature64_from_text,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass174.runtime import Hash216Array
from hhs_runtime.pass174.storage import PersistentEncryptedVectorStore

SCHEMA = "HHS_PASS_219_LANE5_PERSISTENT_HASH216_COMPOSITION_MEMORY_1_39"
UINT64_MAX = (1 << 64) - 1
_MASK64 = UINT64_MAX
_STATE_STRUCT = struct.Struct("<81Q")


@dataclass(frozen=True)
class PersistentHash216CompositionRecord:
    jump_id: str
    parent_hash216: str
    child_hash216: str
    composition_hash216: str
    metadata_hash216: str
    vector_object_id: str
    operation_key: str
    operation_identity_sha256: str
    hash216_index_root_sha256: str
    jump_span: int
    phase_slot: int
    cycle_index: int
    layer_index: int
    trace_roots: TraceRoots
    registration_receipt_signature64: int
    persistence_signature64: int
    changed_bits: int
    quarantined: bool = False


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ValueError(f"floating-point persistent metadata forbidden at {path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_float(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_float(item, f"{path}[{index}]")


def _canonical(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _exact_uint64_words(words: Sequence[int], *, name: str) -> tuple[int, ...]:
    if len(words) != CELL_COUNT:
        raise ValueError(f"{name} requires exactly {CELL_COUNT} uint64 words")
    canonical: list[int] = []
    for index, value in enumerate(words):
        try:
            integer = operator.index(value)
        except TypeError as exc:
            raise ValueError(f"{name} word {index} must be an exact integer") from exc
        if integer < 0 or integer > UINT64_MAX:
            raise ValueError(f"{name} word {index} outside uint64")
        canonical.append(int(integer))
    return tuple(canonical)


def _pack_state(words: Sequence[int]) -> bytes:
    canonical = _exact_uint64_words(words, name="VM5184 state")
    frame = _STATE_STRUCT.pack(*canonical)
    if len(frame) != SNAPSHOT_BYTES:
        raise RuntimeError("VM5184 persistent frame length mismatch")
    return frame


def _unpack_state(frame: bytes) -> tuple[int, ...]:
    raw = bytes(frame)
    if len(raw) != SNAPSHOT_BYTES:
        raise ValueError("persistent VM5184 frame must contain exactly 648 bytes")
    return tuple(int(value) for value in _STATE_STRUCT.unpack(raw))


def _state_hash72(domain: str, hash216: str) -> str:
    split_hash216(hash216)
    return hash72_digest(
        {"domain": domain, "schema": SCHEMA},
        hash216,
    )


def _composition_seal_payload(
    *,
    parent_hash216: str,
    child_hash216: str,
    jump_span: int,
    cycle_index: int,
    layer_index: int,
    phase_slot: int,
    trace_roots: TraceRoots,
) -> bytes:
    pieces = [
        "HHS-P219-LANE5-COMPOSITION-JUMP-1.38",
        parent_hash216,
        child_hash216,
        str(int(jump_span)),
        str(int(cycle_index)),
        str(int(layer_index)),
        str(int(phase_slot)),
    ]
    for ordinal, roots in enumerate(trace_roots):
        pieces.append(str(ordinal))
        pieces.extend(roots)
    return "\n".join(pieces).encode("ascii")


def _trace_roots_json(trace_roots: TraceRoots) -> str:
    return _canonical([list(item) for item in trace_roots]).decode("utf-8")


def _trace_roots_from_json(raw: str) -> TraceRoots:
    value = json.loads(raw)
    if not isinstance(value, list):
        raise ValueError("persistent trace roots must be a list")
    roots: list[tuple[str, str, str, str]] = []
    for ordinal, item in enumerate(value):
        if not isinstance(item, list) or len(item) != 4:
            raise ValueError(f"persistent trace root {ordinal} malformed")
        canonical = tuple(str(part) for part in item)
        for part in canonical:
            split_hash216(part)
        roots.append(canonical)  # type: ignore[arg-type]
    return tuple(roots)


def _legacy_mix64(value: int) -> int:
    value &= _MASK64
    value ^= value >> 30
    value = (value * 0xBF58476D1CE4E5B9) & _MASK64
    value ^= value >> 27
    value = (value * 0x94D049BB133111EB) & _MASK64
    value ^= value >> 31
    return value & _MASK64


def _legacy_persistence_signature64(record: PersistentHash216CompositionRecord) -> int:
    descriptor = 0x4C35504552533139
    descriptor ^= _legacy_mix64(record.jump_span)
    descriptor ^= _legacy_mix64(record.phase_slot << 32)
    descriptor ^= _legacy_mix64(record.cycle_index)
    descriptor ^= _legacy_mix64(record.layer_index)
    descriptor ^= _legacy_mix64(SNAPSHOT_BYTES)
    descriptor ^= _legacy_mix64(signature64_from_hash216(record.parent_hash216))
    descriptor ^= _legacy_mix64(signature64_from_hash216(record.child_hash216))
    descriptor ^= _legacy_mix64(signature64_from_hash216(record.composition_hash216))
    metadata_signature = signature64_from_hash216(record.metadata_hash216)
    vector_signature = signature64_from_text(record.vector_object_id)
    descriptor ^= _legacy_mix64(metadata_signature)
    descriptor ^= _legacy_mix64(vector_signature)
    descriptor = _legacy_mix64(descriptor)
    return _legacy_mix64(
        descriptor ^ metadata_signature ^ vector_signature ^ 0x2002005005130139
    )


class Pass219Lane5PersistentHash216CompositionMemory:
    """Durable, restart-rehydratable, candidate-only composition memory."""

    def __init__(
        self,
        state_root: str | Path,
        *,
        vector_key: bytes | None = None,
        backend: str = "CPU_REFERENCE",
        require_physical_gpu: bool = False,
    ) -> None:
        self.state_root = Path(state_root).resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.state_root / "lane5_composition_memory.sqlite3"
        self.vector_database_path = self.state_root / "lane5_composition_vectors.sqlite3"
        self.native = Pass205NativeBridge()
        self.jump_store = Pass219Lane5Hash216CompositionJumpStore(
            backend=backend,
            require_physical_gpu=require_physical_gpu,
        )
        self.abi = Pass219Lane5PersistentCompositionMemoryBridge()
        self.vector_store = PersistentEncryptedVectorStore(
            self.vector_database_path,
            key=vector_key,
            key_path=self.state_root / "lane5_composition_vectors.key",
        )
        self._connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._init_schema()
        self._records: dict[str, PersistentHash216CompositionRecord] = {}
        self._by_parent: dict[str, list[str]] = {}
        self._load_index()

    def __enter__(self) -> "Pass219Lane5PersistentHash216CompositionMemory":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self.jump_store.close()
        self.vector_store.close()
        self._connection.close()

    def _init_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS lane5_composition_memory (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                jump_id TEXT NOT NULL UNIQUE,
                parent_hash216 TEXT NOT NULL,
                child_hash216 TEXT NOT NULL,
                composition_hash216 TEXT NOT NULL UNIQUE,
                metadata_hash216 TEXT NOT NULL,
                vector_object_id TEXT NOT NULL UNIQUE,
                operation_key TEXT NOT NULL UNIQUE,
                operation_identity_sha256 TEXT NOT NULL,
                hash216_index_root_sha256 TEXT NOT NULL,
                jump_span INTEGER NOT NULL,
                phase_slot INTEGER NOT NULL,
                cycle_index TEXT NOT NULL,
                layer_index INTEGER NOT NULL,
                trace_roots_json TEXT NOT NULL,
                registration_receipt_signature64 TEXT NOT NULL,
                persistence_signature64 TEXT NOT NULL,
                changed_bits INTEGER NOT NULL,
                quarantined INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS lane5_composition_parent_layer
                ON lane5_composition_memory(parent_hash216, layer_index, sequence);
            CREATE INDEX IF NOT EXISTS lane5_composition_child
                ON lane5_composition_memory(child_hash216, sequence);
            """
        )
        self._connection.commit()

    def _metadata_core(
        self,
        *,
        jump_id: str,
        parent_hash216: str,
        child_hash216: str,
        composition_hash216: str,
        jump_span: int,
        phase_slot: int,
        cycle_index: int,
        layer_index: int,
        trace_roots: TraceRoots,
        registration_receipt_signature64: int,
        changed_bits: int,
        quarantined: bool = False,
    ) -> dict[str, Any]:
        core: dict[str, Any] = {
            "schema": "HHS_PASS_219_LANE5_PERSISTENT_COMPOSITION_METADATA_1_39",
            "jump_id": jump_id,
            "parent_hash216": parent_hash216,
            "child_hash216": child_hash216,
            "composition_hash216": composition_hash216,
            "jump_span": int(jump_span),
            "phase_slot": int(phase_slot),
            "cycle_index": int(cycle_index),
            "layer_index": int(layer_index),
            "trace_roots": [list(item) for item in trace_roots],
            "registration_receipt_signature64": int(registration_receipt_signature64),
            "changed_bits": int(changed_bits),
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }
        if quarantined:
            core["quarantined"] = True
        return core

    def _metadata_hash216(self, core: Mapping[str, Any]) -> str:
        return self.native.hash216_bytes(_canonical(dict(core)))

    def _record_core(self, record: PersistentHash216CompositionRecord) -> dict[str, Any]:
        return self._metadata_core(
            jump_id=record.jump_id,
            parent_hash216=record.parent_hash216,
            child_hash216=record.child_hash216,
            composition_hash216=record.composition_hash216,
            jump_span=record.jump_span,
            phase_slot=record.phase_slot,
            cycle_index=record.cycle_index,
            layer_index=record.layer_index,
            trace_roots=record.trace_roots,
            registration_receipt_signature64=record.registration_receipt_signature64,
            changed_bits=record.changed_bits,
            quarantined=record.quarantined,
        )

    def _record_from_row(self, row: sqlite3.Row) -> PersistentHash216CompositionRecord:
        return PersistentHash216CompositionRecord(
            jump_id=str(row["jump_id"]),
            parent_hash216=str(row["parent_hash216"]),
            child_hash216=str(row["child_hash216"]),
            composition_hash216=str(row["composition_hash216"]),
            metadata_hash216=str(row["metadata_hash216"]),
            vector_object_id=str(row["vector_object_id"]),
            operation_key=str(row["operation_key"]),
            operation_identity_sha256=str(row["operation_identity_sha256"]),
            hash216_index_root_sha256=str(row["hash216_index_root_sha256"]),
            jump_span=int(row["jump_span"]),
            phase_slot=int(row["phase_slot"]),
            cycle_index=int(row["cycle_index"]),
            layer_index=int(row["layer_index"]),
            trace_roots=_trace_roots_from_json(str(row["trace_roots_json"])),
            registration_receipt_signature64=int(row["registration_receipt_signature64"]),
            persistence_signature64=int(row["persistence_signature64"]),
            changed_bits=int(row["changed_bits"]),
            quarantined=bool(row["quarantined"]),
        )

    def _composition_seal_valid(self, record: PersistentHash216CompositionRecord) -> bool:
        expected = self.native.hash216_bytes(
            _composition_seal_payload(
                parent_hash216=record.parent_hash216,
                child_hash216=record.child_hash216,
                jump_span=record.jump_span,
                cycle_index=record.cycle_index,
                layer_index=record.layer_index,
                phase_slot=record.phase_slot,
                trace_roots=record.trace_roots,
            )
        )
        return expected == record.composition_hash216

    def _metadata_valid(self, record: PersistentHash216CompositionRecord) -> bool:
        return self._metadata_hash216(self._record_core(record)) == record.metadata_hash216

    def _native_record_receipt(self, record: PersistentHash216CompositionRecord) -> dict[str, Any]:
        receipt = self.abi.validate_descriptor(
            parent_hash216=record.parent_hash216,
            child_hash216=record.child_hash216,
            composition_hash216=record.composition_hash216,
            metadata_hash216=record.metadata_hash216,
            vector_object_id=record.vector_object_id,
            jump_span=record.jump_span,
            phase_slot=record.phase_slot,
            cycle_index=record.cycle_index,
            layer_index=record.layer_index,
        )
        if not receipt["accepted"] or not receipt["restart_rehydratable"]:
            raise RuntimeError("native persistent composition membrane rejected record")
        if receipt["canonical_mutation_authority"] or receipt["canonical_persistence_authority"]:
            raise RuntimeError("persistent composition membrane exposed canonical authority")
        expected_signature = int(receipt["persistence_signature64"])
        if expected_signature != record.persistence_signature64:
            if record.persistence_signature64 != _legacy_persistence_signature64(record):
                raise ValueError("persistent composition native receipt signature mismatch")
            self._connection.execute(
                "UPDATE lane5_composition_memory SET persistence_signature64=? WHERE jump_id=?",
                (str(expected_signature), record.jump_id),
            )
            self._connection.commit()
            replacement = PersistentHash216CompositionRecord(
                **{**record.__dict__, "persistence_signature64": expected_signature}
            )
            self._records[record.jump_id] = replacement
            receipt["legacy_receipt_migrated"] = True
        else:
            receipt["legacy_receipt_migrated"] = False
        return receipt

    def _quarantine_record(
        self,
        record: PersistentHash216CompositionRecord,
    ) -> PersistentHash216CompositionRecord:
        replacement = PersistentHash216CompositionRecord(
            **{**record.__dict__, "quarantined": True}
        )
        try:
            metadata_hash216 = self._metadata_hash216(self._record_core(replacement))
            provisional = PersistentHash216CompositionRecord(
                **{
                    **replacement.__dict__,
                    "metadata_hash216": metadata_hash216,
                    "persistence_signature64": 0,
                }
            )
            receipt = self.abi.validate_descriptor(
                parent_hash216=provisional.parent_hash216,
                child_hash216=provisional.child_hash216,
                composition_hash216=provisional.composition_hash216,
                metadata_hash216=provisional.metadata_hash216,
                vector_object_id=provisional.vector_object_id,
                jump_span=provisional.jump_span,
                phase_slot=provisional.phase_slot,
                cycle_index=provisional.cycle_index,
                layer_index=provisional.layer_index,
            )
            if not receipt["accepted"]:
                raise RuntimeError("native quarantine receipt rejected")
            replacement = PersistentHash216CompositionRecord(
                **{
                    **provisional.__dict__,
                    "persistence_signature64": int(receipt["persistence_signature64"]),
                }
            )
            self._connection.execute(
                """
                UPDATE lane5_composition_memory
                   SET metadata_hash216=?, persistence_signature64=?, quarantined=1
                 WHERE jump_id=?
                """,
                (
                    replacement.metadata_hash216,
                    str(replacement.persistence_signature64),
                    replacement.jump_id,
                ),
            )
        except Exception:
            self._connection.execute(
                "UPDATE lane5_composition_memory SET quarantined=1 WHERE jump_id=?",
                (record.jump_id,),
            )
        self._connection.commit()
        self._records[record.jump_id] = replacement
        try:
            self.vector_store.quarantine(record.vector_object_id)
        except Exception:
            pass
        return replacement

    def _quarantine_malformed_row(self, row: sqlite3.Row) -> None:
        self._connection.execute(
            "UPDATE lane5_composition_memory SET quarantined=1 WHERE sequence=?",
            (row["sequence"],),
        )
        self._connection.commit()
        try:
            vector_object_id = str(row["vector_object_id"])
            if vector_object_id:
                self.vector_store.quarantine(vector_object_id)
        except Exception:
            pass

    def _load_index(self) -> None:
        rows = self._connection.execute(
            "SELECT * FROM lane5_composition_memory ORDER BY sequence"
        ).fetchall()
        for row in rows:
            try:
                record = self._record_from_row(row)
            except Exception:
                self._quarantine_malformed_row(row)
                continue
            valid = self._metadata_valid(record) and self._composition_seal_valid(record)
            if not valid:
                record = self._quarantine_record(record)
            self._records[record.jump_id] = record
            self._by_parent.setdefault(record.parent_hash216, []).append(record.jump_id)

    def status(self) -> dict[str, Any]:
        vector = self.vector_store.storage_status()
        persistent_records = int(
            self._connection.execute("SELECT COUNT(*) FROM lane5_composition_memory").fetchone()[0]
        )
        quarantined = int(
            self._connection.execute(
                "SELECT COUNT(*) FROM lane5_composition_memory WHERE quarantined != 0"
            ).fetchone()[0]
        )
        synchronous = int(self._connection.execute("PRAGMA synchronous").fetchone()[0])
        return {
            "schema": SCHEMA,
            "authority": self.abi.authority(),
            "persistent_records": persistent_records,
            "quarantined_records": quarantined,
            "database_path": str(self.database_path),
            "vector_store": vector,
            "journal_mode": str(self._connection.execute("PRAGMA journal_mode").fetchone()[0]),
            "synchronous": synchronous,
            "synchronous_full": synchronous == 2,
            "snapshot_bytes": SNAPSHOT_BYTES,
            "restart_rehydration_supported": True,
            "pass174_persistent_encrypted_vector_store_bound": True,
            "pass194_hash216_positional_index_bound": True,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "gpu_may_commit_hash72": False,
            "gpu_may_commit_hash216": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def persist_validated_jump(
        self,
        *,
        parent_state: Sequence[int],
        jump: ValidatedHash216CompositionJump,
    ) -> dict[str, Any]:
        parent_words = _exact_uint64_words(parent_state, name="persistent composition parent state")
        child_words = _exact_uint64_words(jump.child_state, name="persistent composition child state")
        if self.native.state_root(parent_words) != jump.parent_hash216:
            raise ValueError("persistent composition parent state/root mismatch")
        if not self.jump_store.verify_jump_replay(parent_state=parent_words, jump=jump):
            raise ValueError("persistent composition exact replay provenance mismatch")
        registration_receipt = self.jump_store._validate_record(jump)
        if not registration_receipt["accepted"]:
            raise ValueError("1.38 composition jump not admitted for persistence")

        existing = self._connection.execute(
            "SELECT * FROM lane5_composition_memory WHERE jump_id=?",
            (jump.jump_id,),
        ).fetchone()
        if existing is not None:
            record = self._record_from_row(existing)
            if record.composition_hash216 != jump.composition_hash216:
                raise ValueError("persistent composition jump ID collision")
            return {
                "schema": "HHS_PASS_219_LANE5_PERSISTENT_COMPOSITION_STORE_1_39",
                "jump_id": record.jump_id,
                "vector_object_id": record.vector_object_id,
                "operation_key": record.operation_key,
                "metadata_hash216": record.metadata_hash216,
                "idempotent": True,
                "candidate_only": True,
            }

        parent_frame = _pack_state(parent_words)
        child_frame = _pack_state(child_words)
        changed_bits = sum(
            (left ^ right).bit_count()
            for left, right in zip(parent_words, child_words)
        )
        if len(parent_frame) != SNAPSHOT_BYTES or len(child_frame) != SNAPSHOT_BYTES:
            raise RuntimeError("persistent composition VM5184 frame contract failed")

        registration_signature = int(registration_receipt["reuse_signature64"])
        core = self._metadata_core(
            jump_id=jump.jump_id,
            parent_hash216=jump.parent_hash216,
            child_hash216=jump.child_hash216,
            composition_hash216=jump.composition_hash216,
            jump_span=jump.jump_span,
            phase_slot=jump.phase_slot,
            cycle_index=jump.cycle_index,
            layer_index=jump.layer_index,
            trace_roots=jump.trace_roots,
            registration_receipt_signature64=registration_signature,
            changed_bits=changed_bits,
        )
        metadata_hash216 = self._metadata_hash216(core)
        operation_identity = sha256(
            b"HHS-P219-LANE5-PERSISTENT-COMPOSITION-OP-1.39\0"
            + _canonical(core)
            + metadata_hash216.encode("ascii")
        ).hexdigest()
        segments = split_hash216(jump.composition_hash216)
        logical_step = int(jump.cycle_index) * CYCLE + int(jump.phase_slot)
        indexed_hash216 = Hash216Array.build(
            segments[0],
            segments[1],
            segments[2],
            genesis_identity=GENESIS_IDENTITY,
            logical_step=logical_step,
            operation_identity=operation_identity,
            legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
        )
        if indexed_hash216.combined != jump.composition_hash216:
            raise RuntimeError("Pass194 Hash216 positional index changed composition identity")
        operation_key = sha256(
            b"HHS-P219-LANE5-PERSISTENT-COMPOSITION-KEY-1.39\0"
            + bytes.fromhex(operation_identity)
            + bytes.fromhex(indexed_hash216.index_root_sha256)
            + metadata_hash216.encode("ascii")
        ).hexdigest()
        parent_hash72 = _state_hash72(
            "HHS-P219-LANE5-PERSISTENT-PARENT-HASH72-1.39",
            jump.parent_hash216,
        )
        child_hash72 = _state_hash72(
            "HHS-P219-LANE5-PERSISTENT-CHILD-HASH72-1.39",
            jump.child_hash216,
        )
        vector_object = self.vector_store.admit(
            operation_key=operation_key,
            logical_step=logical_step,
            input_hash72=parent_hash72,
            output_hash72=child_hash72,
            operation_identity_sha256=operation_identity,
            hash216=indexed_hash216,
            output_snapshot=child_frame,
            legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
            genesis_identity=GENESIS_IDENTITY,
            direct_cost_units=jump.jump_span,
            changed_bits=changed_bits,
            parent_object_id=None,
        )
        provisional = PersistentHash216CompositionRecord(
            jump_id=jump.jump_id,
            parent_hash216=jump.parent_hash216,
            child_hash216=jump.child_hash216,
            composition_hash216=jump.composition_hash216,
            metadata_hash216=metadata_hash216,
            vector_object_id=vector_object.object_id,
            operation_key=operation_key,
            operation_identity_sha256=operation_identity,
            hash216_index_root_sha256=indexed_hash216.index_root_sha256,
            jump_span=jump.jump_span,
            phase_slot=jump.phase_slot,
            cycle_index=jump.cycle_index,
            layer_index=jump.layer_index,
            trace_roots=jump.trace_roots,
            registration_receipt_signature64=registration_signature,
            persistence_signature64=0,
            changed_bits=changed_bits,
            quarantined=False,
        )
        native_receipt = self.abi.validate_descriptor(
            parent_hash216=provisional.parent_hash216,
            child_hash216=provisional.child_hash216,
            composition_hash216=provisional.composition_hash216,
            metadata_hash216=provisional.metadata_hash216,
            vector_object_id=provisional.vector_object_id,
            jump_span=provisional.jump_span,
            phase_slot=provisional.phase_slot,
            cycle_index=provisional.cycle_index,
            layer_index=provisional.layer_index,
        )
        if not native_receipt["accepted"] or native_receipt["canonical_persistence_authority"]:
            self.vector_store.quarantine(vector_object.object_id)
            raise RuntimeError("native persistent composition membrane rejected stored vector")
        persistence_signature = int(native_receipt["persistence_signature64"])
        record = PersistentHash216CompositionRecord(
            **{**provisional.__dict__, "persistence_signature64": persistence_signature}
        )
        if not self._metadata_valid(record) or not self._composition_seal_valid(record):
            self.vector_store.quarantine(vector_object.object_id)
            raise RuntimeError("persistent composition record failed post-store seal validation")

        self._connection.execute(
            """
            INSERT INTO lane5_composition_memory(
                jump_id, parent_hash216, child_hash216, composition_hash216,
                metadata_hash216, vector_object_id, operation_key,
                operation_identity_sha256, hash216_index_root_sha256,
                jump_span, phase_slot, cycle_index, layer_index,
                trace_roots_json, registration_receipt_signature64,
                persistence_signature64, changed_bits, quarantined
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)
            """,
            (
                record.jump_id,
                record.parent_hash216,
                record.child_hash216,
                record.composition_hash216,
                record.metadata_hash216,
                record.vector_object_id,
                record.operation_key,
                record.operation_identity_sha256,
                record.hash216_index_root_sha256,
                record.jump_span,
                record.phase_slot,
                str(record.cycle_index),
                record.layer_index,
                _trace_roots_json(record.trace_roots),
                str(record.registration_receipt_signature64),
                str(record.persistence_signature64),
                record.changed_bits,
            ),
        )
        self._connection.commit()
        self._records[record.jump_id] = record
        self._by_parent.setdefault(record.parent_hash216, []).append(record.jump_id)
        return {
            "schema": "HHS_PASS_219_LANE5_PERSISTENT_COMPOSITION_STORE_1_39",
            "jump_id": record.jump_id,
            "parent_hash216": record.parent_hash216,
            "child_hash216": record.child_hash216,
            "composition_hash216": record.composition_hash216,
            "metadata_hash216": record.metadata_hash216,
            "vector_object_id": record.vector_object_id,
            "operation_key": record.operation_key,
            "hash216_index_root_sha256": record.hash216_index_root_sha256,
            "changed_bits": record.changed_bits,
            "native_receipt": native_receipt,
            "idempotent": False,
            "encrypted_snapshot": True,
            "restart_rehydratable": True,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    @staticmethod
    def _dedupe_destinations(
        records: Sequence[PersistentHash216CompositionRecord],
    ) -> list[PersistentHash216CompositionRecord]:
        selected: dict[str, PersistentHash216CompositionRecord] = {}
        for record in records:
            prior = selected.get(record.child_hash216)
            if prior is None or (-record.jump_span, record.jump_id) < (-prior.jump_span, prior.jump_id):
                selected[record.child_hash216] = record
        return sorted(selected.values(), key=lambda item: (item.child_hash216, item.jump_id))

    def search(
        self,
        *,
        current_state: Sequence[int],
        goal_hash216: str,
        tick: int,
        cycle_index: int,
        layer_index: int | None = None,
        top_k: int = 32,
    ) -> dict[str, Any]:
        current_words = _exact_uint64_words(current_state, name="persistent composition search state")
        parent_hash216 = self.native.state_root(current_words)
        records = [
            self._records[jump_id]
            for jump_id in self._by_parent.get(parent_hash216, [])
            if not self._records[jump_id].quarantined
        ]
        if layer_index is not None:
            records = [record for record in records if record.layer_index == int(layer_index)]
        route_count = len(records)
        records = self._dedupe_destinations(records)
        candidates = [
            Hash216CompositionCandidate(
                candidate_id=record.jump_id,
                hash216=record.child_hash216,
                validated=True,
                jump_span=record.jump_span,
                lineage_signature=record.composition_hash216,
            )
            for record in records
        ]
        result = self.jump_store.optimizer.search_hash216(
            query_hash216=goal_hash216,
            candidates=candidates,
            tick=tick,
            cycle_index=cycle_index,
            top_k=top_k,
        )
        result["persistent_composition_memory"] = True
        result["restart_rehydrated_candidates"] = len(records)
        result["persistent_routes_considered"] = route_count
        result["parent_hash216"] = parent_hash216
        result["candidate_only"] = True
        return result

    def reuse(
        self,
        *,
        current_state: Sequence[int],
        jump_id: str,
    ) -> dict[str, Any]:
        try:
            record = self._records[jump_id]
        except KeyError as exc:
            raise KeyError(f"unknown persistent composition jump: {jump_id}") from exc
        if record.quarantined:
            raise ValueError("persistent composition jump is quarantined")
        current_words = _exact_uint64_words(current_state, name="persistent composition reuse state")
        current_root = self.native.state_root(current_words)
        if current_root != record.parent_hash216:
            raise ValueError("persistent composition parent does not match current canonical state identity")
        if not self._metadata_valid(record):
            self._quarantine_record(record)
            raise ValueError("persistent composition metadata Hash216 mismatch")
        if not self._composition_seal_valid(record):
            self._quarantine_record(record)
            raise ValueError("persistent composition 1.38 seal mismatch")
        try:
            vector_object, frame = self.vector_store.retrieve(
                record.operation_key,
                legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
                genesis_identity=GENESIS_IDENTITY,
            )
            if vector_object.object_id != record.vector_object_id:
                raise ValueError("persistent vector object identity mismatch")
            if vector_object.operation_identity_sha256 != record.operation_identity_sha256:
                raise ValueError("persistent vector operation identity mismatch")
            if vector_object.hash216.combined != record.composition_hash216:
                raise ValueError("persistent vector Hash216 composition mismatch")
            if vector_object.hash216.index_root_sha256 != record.hash216_index_root_sha256:
                raise ValueError("persistent vector Hash216 index root mismatch")
            expected_parent_hash72 = _state_hash72(
                "HHS-P219-LANE5-PERSISTENT-PARENT-HASH72-1.39",
                record.parent_hash216,
            )
            expected_child_hash72 = _state_hash72(
                "HHS-P219-LANE5-PERSISTENT-CHILD-HASH72-1.39",
                record.child_hash216,
            )
            if vector_object.input_hash72 != expected_parent_hash72:
                raise ValueError("persistent vector parent Hash72 binding mismatch")
            if vector_object.output_hash72 != expected_child_hash72:
                raise ValueError("persistent vector child Hash72 binding mismatch")
            child_state = _unpack_state(frame)
            if self.native.state_root(child_state) != record.child_hash216:
                raise ValueError("persistent vector child state/Hash216 mismatch")
            native_receipt = self._native_record_receipt(record)
        except Exception:
            self._quarantine_record(record)
            raise
        return {
            "schema": "HHS_PASS_219_LANE5_PERSISTENT_COMPOSITION_REUSE_1_39",
            "jump_id": record.jump_id,
            "parent_hash216": record.parent_hash216,
            "child_hash216": record.child_hash216,
            "composition_hash216": record.composition_hash216,
            "metadata_hash216": record.metadata_hash216,
            "vector_object_id": record.vector_object_id,
            "child_state": list(child_state),
            "jump_span": record.jump_span,
            "represented_transitions": record.jump_span,
            "intermediate_transitions_executed_on_reuse": 0,
            "phase_slot": record.phase_slot,
            "cycle_index": record.cycle_index,
            "layer_index": record.layer_index,
            "native_receipt": native_receipt,
            "encrypted_snapshot": True,
            "restart_rehydrated": True,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "gpu_may_commit_hash72": False,
            "gpu_may_commit_hash216": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def quarantine(self, jump_id: str) -> None:
        try:
            record = self._records[jump_id]
        except KeyError as exc:
            raise KeyError(f"unknown persistent composition jump: {jump_id}") from exc
        self._quarantine_record(record)

    def records(self) -> tuple[PersistentHash216CompositionRecord, ...]:
        rows = self._connection.execute(
            "SELECT jump_id FROM lane5_composition_memory ORDER BY sequence"
        ).fetchall()
        return tuple(
            self._records[str(row["jump_id"])]
            for row in rows
            if str(row["jump_id"]) in self._records
        )


__all__ = [
    "PersistentHash216CompositionRecord",
    "Pass219Lane5PersistentHash216CompositionMemory",
]
