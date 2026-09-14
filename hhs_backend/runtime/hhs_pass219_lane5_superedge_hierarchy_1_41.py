"""Persistent recursive Lane 5 superedge hierarchy, Pass 219 1.41.

A superedge promotes a previously authenticated 1.40 route, or an ordered route
of lower-level superedges, into one encrypted terminal VM5184 candidate object.
Direct reuse performs one persistent snapshot retrieval while preserving exact
flattened level-0 provenance and the inherited signed-environmental VM81
canonical-admission boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass194_multimodal_storage_training_v1 import (
    GENESIS_IDENTITY,
    LEGACY_FOUNDATION_ROOT,
)
from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import (
    Hash216CompositionCandidate,
    split_hash216,
)
from hhs_backend.runtime.hhs_pass219_lane5_persistent_hash216_composition_memory_1_39 import (
    _pack_state,
    _state_hash72,
    _unpack_state,
)
from hhs_backend.runtime.hhs_pass219_lane5_recursive_hash216_composition_graph_1_40 import (
    Pass219Lane5RecursiveHash216CompositionGraph,
)
from hhs_python.runtime.hhs_pass219_lane5_superedge_hierarchy_bridge import (
    CYCLE,
    QUARTER,
    Pass219Lane5SuperedgeHierarchyBridge,
)
from hhs_runtime.pass174.runtime import Hash216Array

SCHEMA = "HHS_PASS_219_LANE5_SUPEREDGE_HIERARCHY_1_41"


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ValueError(f"floating-point superedge metadata forbidden at {path}")
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


def _json_tuple(raw: str) -> tuple[str, ...]:
    value = json.loads(raw)
    if not isinstance(value, list):
        raise ValueError("superedge persisted list is malformed")
    return tuple(str(item) for item in value)


def _json_int_tuple(raw: str) -> tuple[int, ...]:
    value = json.loads(raw)
    if not isinstance(value, list):
        raise ValueError("superedge persisted integer list is malformed")
    result = tuple(int(item) for item in value)
    if any(item < 0 for item in result):
        raise ValueError("superedge persisted integer list contains negative value")
    return result


@dataclass(frozen=True)
class PersistentSuperedgeRecord:
    superedge_id: str
    hierarchy_level: int
    parent_hash216: str
    child_hash216: str
    route_hash216: str
    hierarchy_hash216: str
    metadata_hash216: str
    vector_object_id: str
    operation_key: str
    operation_identity_sha256: str
    hash216_index_root_sha256: str
    total_span: int
    base_hops: int
    direct_component_count: int
    phase_slot: int
    cycle_index: int
    layer_index: int
    component_ids: tuple[str, ...]
    component_levels: tuple[int, ...]
    component_seals: tuple[str, ...]
    leaf_jump_ids: tuple[str, ...]
    native_receipt_signature64: int
    changed_bits: int
    quarantined: bool = False


class Pass219Lane5SuperedgeHierarchy:
    """Restart-rehydratable hierarchy of one-snapshot candidate superedges."""

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
        self.database_path = self.state_root / "lane5_superedge_hierarchy.sqlite3"
        self.graph = Pass219Lane5RecursiveHash216CompositionGraph(
            self.state_root,
            vector_key=vector_key,
            backend=backend,
            require_physical_gpu=require_physical_gpu,
        )
        self.memory = self.graph.memory
        self.native = self.graph.native
        self.vector_store = self.memory.vector_store
        self.optimizer = self.memory.jump_store.optimizer
        self.abi = Pass219Lane5SuperedgeHierarchyBridge()
        self._connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._init_schema()
        self._records: dict[str, PersistentSuperedgeRecord] = {}
        self._by_parent: dict[str, list[str]] = {}
        self._load_index()

    def __enter__(self) -> "Pass219Lane5SuperedgeHierarchy":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()
        self.graph.close()

    def _init_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS lane5_superedges (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                superedge_id TEXT NOT NULL UNIQUE,
                hierarchy_level INTEGER NOT NULL,
                parent_hash216 TEXT NOT NULL,
                child_hash216 TEXT NOT NULL,
                route_hash216 TEXT NOT NULL,
                hierarchy_hash216 TEXT NOT NULL UNIQUE,
                metadata_hash216 TEXT NOT NULL,
                vector_object_id TEXT NOT NULL UNIQUE,
                operation_key TEXT NOT NULL UNIQUE,
                operation_identity_sha256 TEXT NOT NULL,
                hash216_index_root_sha256 TEXT NOT NULL,
                total_span INTEGER NOT NULL,
                base_hops INTEGER NOT NULL,
                direct_component_count INTEGER NOT NULL,
                phase_slot INTEGER NOT NULL,
                cycle_index TEXT NOT NULL,
                layer_index INTEGER NOT NULL,
                component_ids_json TEXT NOT NULL,
                component_levels_json TEXT NOT NULL,
                component_seals_json TEXT NOT NULL,
                leaf_jump_ids_json TEXT NOT NULL,
                native_receipt_signature64 TEXT NOT NULL,
                changed_bits INTEGER NOT NULL,
                quarantined INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS lane5_superedge_parent_layer
                ON lane5_superedges(parent_hash216, layer_index, hierarchy_level, sequence);
            CREATE INDEX IF NOT EXISTS lane5_superedge_child
                ON lane5_superedges(child_hash216, sequence);
            """
        )
        self._connection.commit()

    def _hierarchy_payload(
        self,
        *,
        superedge_id: str,
        hierarchy_level: int,
        parent_hash216: str,
        child_hash216: str,
        route_hash216: str,
        total_span: int,
        base_hops: int,
        component_ids: Sequence[str],
        component_levels: Sequence[int],
        component_seals: Sequence[str],
        leaf_jump_ids: Sequence[str],
    ) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_219_LANE5_SUPEREDGE_HIERARCHY_SEAL_1_41",
            "superedge_id": str(superedge_id),
            "hierarchy_level": int(hierarchy_level),
            "parent_hash216": parent_hash216,
            "child_hash216": child_hash216,
            "route_hash216": route_hash216,
            "total_span": int(total_span),
            "base_hops": int(base_hops),
            "components": [
                {
                    "component_id": str(component_id),
                    "component_level": int(component_level),
                    "component_seal": str(component_seal),
                }
                for component_id, component_level, component_seal in zip(
                    component_ids, component_levels, component_seals
                )
            ],
            "leaf_jump_ids": [str(value) for value in leaf_jump_ids],
        }

    def _metadata_core(
        self,
        *,
        superedge_id: str,
        hierarchy_level: int,
        parent_hash216: str,
        child_hash216: str,
        route_hash216: str,
        hierarchy_hash216: str,
        total_span: int,
        base_hops: int,
        phase_slot: int,
        cycle_index: int,
        layer_index: int,
        component_ids: Sequence[str],
        component_levels: Sequence[int],
        component_seals: Sequence[str],
        leaf_jump_ids: Sequence[str],
        changed_bits: int,
    ) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS_219_LANE5_SUPEREDGE_METADATA_1_41",
            "superedge_id": superedge_id,
            "hierarchy_level": int(hierarchy_level),
            "parent_hash216": parent_hash216,
            "child_hash216": child_hash216,
            "route_hash216": route_hash216,
            "hierarchy_hash216": hierarchy_hash216,
            "total_span": int(total_span),
            "base_hops": int(base_hops),
            "phase_slot": int(phase_slot),
            "cycle_index": int(cycle_index),
            "layer_index": int(layer_index),
            "component_ids": [str(value) for value in component_ids],
            "component_levels": [int(value) for value in component_levels],
            "component_seals": [str(value) for value in component_seals],
            "leaf_jump_ids": [str(value) for value in leaf_jump_ids],
            "changed_bits": int(changed_bits),
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def _record_from_row(self, row: sqlite3.Row) -> PersistentSuperedgeRecord:
        record = PersistentSuperedgeRecord(
            superedge_id=str(row["superedge_id"]),
            hierarchy_level=int(row["hierarchy_level"]),
            parent_hash216=str(row["parent_hash216"]),
            child_hash216=str(row["child_hash216"]),
            route_hash216=str(row["route_hash216"]),
            hierarchy_hash216=str(row["hierarchy_hash216"]),
            metadata_hash216=str(row["metadata_hash216"]),
            vector_object_id=str(row["vector_object_id"]),
            operation_key=str(row["operation_key"]),
            operation_identity_sha256=str(row["operation_identity_sha256"]),
            hash216_index_root_sha256=str(row["hash216_index_root_sha256"]),
            total_span=int(row["total_span"]),
            base_hops=int(row["base_hops"]),
            direct_component_count=int(row["direct_component_count"]),
            phase_slot=int(row["phase_slot"]),
            cycle_index=int(row["cycle_index"]),
            layer_index=int(row["layer_index"]),
            component_ids=_json_tuple(str(row["component_ids_json"])),
            component_levels=_json_int_tuple(str(row["component_levels_json"])),
            component_seals=_json_tuple(str(row["component_seals_json"])),
            leaf_jump_ids=_json_tuple(str(row["leaf_jump_ids_json"])),
            native_receipt_signature64=int(row["native_receipt_signature64"]),
            changed_bits=int(row["changed_bits"]),
            quarantined=bool(row["quarantined"]),
        )
        for value in (
            record.parent_hash216,
            record.child_hash216,
            record.route_hash216,
            record.hierarchy_hash216,
            record.metadata_hash216,
        ):
            split_hash216(value)
        for value in record.component_seals:
            split_hash216(value)
        if record.direct_component_count != len(record.component_ids):
            raise ValueError("superedge direct component count mismatch")
        if len(record.component_levels) != len(record.component_ids):
            raise ValueError("superedge component level count mismatch")
        if len(record.component_seals) != len(record.component_ids):
            raise ValueError("superedge component seal count mismatch")
        if record.base_hops != len(record.leaf_jump_ids):
            raise ValueError("superedge flattened leaf count mismatch")
        return record

    def _record_core(self, record: PersistentSuperedgeRecord) -> dict[str, Any]:
        return self._metadata_core(
            superedge_id=record.superedge_id,
            hierarchy_level=record.hierarchy_level,
            parent_hash216=record.parent_hash216,
            child_hash216=record.child_hash216,
            route_hash216=record.route_hash216,
            hierarchy_hash216=record.hierarchy_hash216,
            total_span=record.total_span,
            base_hops=record.base_hops,
            phase_slot=record.phase_slot,
            cycle_index=record.cycle_index,
            layer_index=record.layer_index,
            component_ids=record.component_ids,
            component_levels=record.component_levels,
            component_seals=record.component_seals,
            leaf_jump_ids=record.leaf_jump_ids,
            changed_bits=record.changed_bits,
        )

    def _metadata_valid(self, record: PersistentSuperedgeRecord) -> bool:
        return self.native.hash216_bytes(_canonical(self._record_core(record))) == record.metadata_hash216

    def _hierarchy_valid(self, record: PersistentSuperedgeRecord) -> bool:
        payload = self._hierarchy_payload(
            superedge_id=record.superedge_id,
            hierarchy_level=record.hierarchy_level,
            parent_hash216=record.parent_hash216,
            child_hash216=record.child_hash216,
            route_hash216=record.route_hash216,
            total_span=record.total_span,
            base_hops=record.base_hops,
            component_ids=record.component_ids,
            component_levels=record.component_levels,
            component_seals=record.component_seals,
            leaf_jump_ids=record.leaf_jump_ids,
        )
        return self.native.hash216_bytes(_canonical(payload)) == record.hierarchy_hash216

    def _leaf_dependencies_live(self, record: PersistentSuperedgeRecord) -> bool:
        base = {item.jump_id: item for item in self.memory.records()}
        for jump_id in record.leaf_jump_ids:
            item = base.get(jump_id)
            if item is None or item.quarantined:
                return False
        return True

    def _quarantine_record(self, record: PersistentSuperedgeRecord) -> None:
        self._connection.execute(
            "UPDATE lane5_superedges SET quarantined=1 WHERE superedge_id=?",
            (record.superedge_id,),
        )
        self._connection.commit()
        try:
            self.vector_store.quarantine(record.vector_object_id)
        except Exception:
            pass
        self._records[record.superedge_id] = PersistentSuperedgeRecord(
            **{**record.__dict__, "quarantined": True}
        )

    def _load_index(self) -> None:
        rows = self._connection.execute(
            "SELECT * FROM lane5_superedges ORDER BY sequence"
        ).fetchall()
        for row in rows:
            try:
                record = self._record_from_row(row)
                valid = (
                    self._metadata_valid(record)
                    and self._hierarchy_valid(record)
                    and self._leaf_dependencies_live(record)
                )
                if not valid:
                    self._quarantine_record(record)
                    record = self._records[record.superedge_id]
                else:
                    self._records[record.superedge_id] = record
                self._by_parent.setdefault(record.parent_hash216, []).append(record.superedge_id)
            except Exception:
                self._connection.execute(
                    "UPDATE lane5_superedges SET quarantined=1 WHERE sequence=?",
                    (int(row["sequence"]),),
                )
                self._connection.commit()

    def status(self) -> dict[str, Any]:
        rows = self._connection.execute(
            "SELECT hierarchy_level, quarantined FROM lane5_superedges ORDER BY sequence"
        ).fetchall()
        active = [record for record in self._records.values() if not record.quarantined]
        levels: dict[int, int] = {}
        for record in active:
            levels[record.hierarchy_level] = levels.get(record.hierarchy_level, 0) + 1
        synchronous = int(self._connection.execute("PRAGMA synchronous").fetchone()[0])
        return {
            "schema": SCHEMA,
            "authority": self.abi.authority(),
            "persistent_superedges": len(rows),
            "active_superedges": len(active),
            "quarantined_superedges": sum(int(row["quarantined"]) for row in rows),
            "levels": levels,
            "full_cycle": CYCLE,
            "quarter_cycle": QUARTER,
            "restart_rehydratable_superedges": True,
            "one_snapshot_direct_reuse": True,
            "transitive_flattened_provenance": True,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
            "journal_mode": str(self._connection.execute("PRAGMA journal_mode").fetchone()[0]),
            "synchronous_full": synchronous == 2,
        }

    def _persist_superedge(
        self,
        *,
        superedge_id: str,
        hierarchy_level: int,
        parent_state: Sequence[int],
        terminal_state: Sequence[int],
        route_hash216: str,
        total_span: int,
        base_hops: int,
        component_ids: Sequence[str],
        component_levels: Sequence[int],
        component_seals: Sequence[str],
        leaf_jump_ids: Sequence[str],
        tick: int,
        cycle_index: int,
        layer_index: int,
    ) -> dict[str, Any]:
        if not superedge_id:
            raise ValueError("superedge_id must be non-empty")
        if hierarchy_level < 1:
            raise ValueError("superedge hierarchy level must be positive")
        if len(component_ids) < 2:
            raise ValueError("superedge promotion requires at least two components")
        if not (
            len(component_ids) == len(component_levels) == len(component_seals)
        ):
            raise ValueError("superedge component metadata lengths differ")
        if base_hops != len(leaf_jump_ids) or base_hops < len(component_ids):
            raise ValueError("superedge flattened base-hop accounting mismatch")
        if len(set(leaf_jump_ids)) != len(leaf_jump_ids):
            raise ValueError("superedge flattened provenance contains repeated level-0 edge")
        if hierarchy_level != 1 + max(int(value) for value in component_levels):
            raise ValueError("superedge hierarchy level does not equal one plus component maximum")
        if int(tick) < 0 or int(cycle_index) < 0 or int(layer_index) < 0:
            raise ValueError("superedge coordinates must be nonnegative")

        parent = tuple(int(value) for value in parent_state)
        terminal = tuple(int(value) for value in terminal_state)
        parent_hash216 = self.native.state_root(parent)
        child_hash216 = self.native.state_root(terminal)
        split_hash216(route_hash216)
        for seal in component_seals:
            split_hash216(seal)

        existing = self._connection.execute(
            "SELECT * FROM lane5_superedges WHERE superedge_id=?",
            (superedge_id,),
        ).fetchone()
        if existing is not None:
            record = self._record_from_row(existing)
            return {
                "schema": "HHS_PASS_219_LANE5_SUPEREDGE_PROMOTION_1_41",
                "superedge_id": record.superedge_id,
                "hierarchy_hash216": record.hierarchy_hash216,
                "vector_object_id": record.vector_object_id,
                "idempotent": True,
                "candidate_only": True,
            }

        phase_slot = int(tick) % CYCLE
        effective_cycle = int(cycle_index) + int(tick) // CYCLE
        hierarchy_payload = self._hierarchy_payload(
            superedge_id=superedge_id,
            hierarchy_level=hierarchy_level,
            parent_hash216=parent_hash216,
            child_hash216=child_hash216,
            route_hash216=route_hash216,
            total_span=total_span,
            base_hops=base_hops,
            component_ids=component_ids,
            component_levels=component_levels,
            component_seals=component_seals,
            leaf_jump_ids=leaf_jump_ids,
        )
        hierarchy_hash216 = self.native.hash216_bytes(_canonical(hierarchy_payload))
        changed_bits = sum((left ^ right).bit_count() for left, right in zip(parent, terminal))
        metadata_core = self._metadata_core(
            superedge_id=superedge_id,
            hierarchy_level=hierarchy_level,
            parent_hash216=parent_hash216,
            child_hash216=child_hash216,
            route_hash216=route_hash216,
            hierarchy_hash216=hierarchy_hash216,
            total_span=total_span,
            base_hops=base_hops,
            phase_slot=phase_slot,
            cycle_index=effective_cycle,
            layer_index=layer_index,
            component_ids=component_ids,
            component_levels=component_levels,
            component_seals=component_seals,
            leaf_jump_ids=leaf_jump_ids,
            changed_bits=changed_bits,
        )
        metadata_hash216 = self.native.hash216_bytes(_canonical(metadata_core))
        component_lineage_identity = sha256(
            b"HHS-P219-LANE5-SUPEREDGE-COMPONENT-LINEAGE-1.41\0"
            + _canonical(
                [
                    [str(component_id), int(component_level), str(component_seal)]
                    for component_id, component_level, component_seal in zip(
                        component_ids, component_levels, component_seals
                    )
                ]
            )
        ).hexdigest()
        flattened_leaf_identity = sha256(
            b"HHS-P219-LANE5-SUPEREDGE-FLATTENED-LEAVES-1.41\0"
            + _canonical([str(value) for value in leaf_jump_ids])
        ).hexdigest()
        native_receipt = self.abi.validate(
            hierarchy_level=hierarchy_level,
            direct_component_count=len(component_ids),
            base_hops=base_hops,
            total_span=total_span,
            phase_slot=phase_slot,
            layer_index=layer_index,
            cycle_index=effective_cycle,
            parent_hash216=parent_hash216,
            child_hash216=child_hash216,
            route_hash216=route_hash216,
            hierarchy_hash216=hierarchy_hash216,
            metadata_hash216=metadata_hash216,
            component_lineage_identity=component_lineage_identity,
            flattened_leaf_identity=flattened_leaf_identity,
        )
        if not native_receipt["accepted"] or not native_receipt["one_snapshot_direct_reuse"]:
            raise RuntimeError("native superedge hierarchy membrane rejected promotion")
        if native_receipt["canonical_mutation_authority"] or native_receipt["canonical_persistence_authority"]:
            raise RuntimeError("native superedge hierarchy exposed canonical authority")

        operation_identity = sha256(
            b"HHS-P219-LANE5-SUPEREDGE-OPERATION-1.41\0"
            + _canonical(metadata_core)
            + hierarchy_hash216.encode("ascii")
        ).hexdigest()
        segments = split_hash216(hierarchy_hash216)
        logical_step = effective_cycle * CYCLE + phase_slot
        indexed_hash216 = Hash216Array.build(
            segments[0],
            segments[1],
            segments[2],
            genesis_identity=GENESIS_IDENTITY,
            logical_step=logical_step,
            operation_identity=operation_identity,
            legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
        )
        if indexed_hash216.combined != hierarchy_hash216:
            raise RuntimeError("Pass194 Hash216 positional index changed superedge identity")
        operation_key = sha256(
            b"HHS-P219-LANE5-SUPEREDGE-KEY-1.41\0"
            + bytes.fromhex(operation_identity)
            + bytes.fromhex(indexed_hash216.index_root_sha256)
            + metadata_hash216.encode("ascii")
        ).hexdigest()
        parent_hash72 = _state_hash72(
            "HHS-P219-LANE5-SUPEREDGE-PARENT-HASH72-1.41", parent_hash216
        )
        child_hash72 = _state_hash72(
            "HHS-P219-LANE5-SUPEREDGE-CHILD-HASH72-1.41", child_hash216
        )
        vector_object = self.vector_store.admit(
            operation_key=operation_key,
            logical_step=logical_step,
            input_hash72=parent_hash72,
            output_hash72=child_hash72,
            operation_identity_sha256=operation_identity,
            hash216=indexed_hash216,
            output_snapshot=_pack_state(terminal),
            legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
            genesis_identity=GENESIS_IDENTITY,
            direct_cost_units=int(total_span),
            changed_bits=changed_bits,
            parent_object_id=None,
        )
        record = PersistentSuperedgeRecord(
            superedge_id=superedge_id,
            hierarchy_level=int(hierarchy_level),
            parent_hash216=parent_hash216,
            child_hash216=child_hash216,
            route_hash216=route_hash216,
            hierarchy_hash216=hierarchy_hash216,
            metadata_hash216=metadata_hash216,
            vector_object_id=vector_object.object_id,
            operation_key=operation_key,
            operation_identity_sha256=operation_identity,
            hash216_index_root_sha256=indexed_hash216.index_root_sha256,
            total_span=int(total_span),
            base_hops=int(base_hops),
            direct_component_count=len(component_ids),
            phase_slot=phase_slot,
            cycle_index=effective_cycle,
            layer_index=int(layer_index),
            component_ids=tuple(str(value) for value in component_ids),
            component_levels=tuple(int(value) for value in component_levels),
            component_seals=tuple(str(value) for value in component_seals),
            leaf_jump_ids=tuple(str(value) for value in leaf_jump_ids),
            native_receipt_signature64=int(native_receipt["hierarchy_receipt_signature64"]),
            changed_bits=changed_bits,
            quarantined=False,
        )
        if not self._metadata_valid(record) or not self._hierarchy_valid(record):
            self.vector_store.quarantine(vector_object.object_id)
            raise RuntimeError("superedge failed post-store seal verification")
        if not self._leaf_dependencies_live(record):
            self.vector_store.quarantine(vector_object.object_id)
            raise RuntimeError("superedge contains unavailable or quarantined level-0 dependency")

        self._connection.execute(
            """
            INSERT INTO lane5_superedges(
                superedge_id, hierarchy_level, parent_hash216, child_hash216,
                route_hash216, hierarchy_hash216, metadata_hash216,
                vector_object_id, operation_key, operation_identity_sha256,
                hash216_index_root_sha256, total_span, base_hops,
                direct_component_count, phase_slot, cycle_index, layer_index,
                component_ids_json, component_levels_json, component_seals_json,
                leaf_jump_ids_json, native_receipt_signature64, changed_bits,
                quarantined
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)
            """,
            (
                record.superedge_id,
                record.hierarchy_level,
                record.parent_hash216,
                record.child_hash216,
                record.route_hash216,
                record.hierarchy_hash216,
                record.metadata_hash216,
                record.vector_object_id,
                record.operation_key,
                record.operation_identity_sha256,
                record.hash216_index_root_sha256,
                record.total_span,
                record.base_hops,
                record.direct_component_count,
                record.phase_slot,
                str(record.cycle_index),
                record.layer_index,
                json.dumps(list(record.component_ids), separators=(",", ":")),
                json.dumps(list(record.component_levels), separators=(",", ":")),
                json.dumps(list(record.component_seals), separators=(",", ":")),
                json.dumps(list(record.leaf_jump_ids), separators=(",", ":")),
                str(record.native_receipt_signature64),
                record.changed_bits,
            ),
        )
        self._connection.commit()
        self._records[record.superedge_id] = record
        self._by_parent.setdefault(record.parent_hash216, []).append(record.superedge_id)
        return {
            "schema": "HHS_PASS_219_LANE5_SUPEREDGE_PROMOTION_1_41",
            "superedge_id": record.superedge_id,
            "hierarchy_level": record.hierarchy_level,
            "parent_hash216": record.parent_hash216,
            "child_hash216": record.child_hash216,
            "route_hash216": record.route_hash216,
            "hierarchy_hash216": record.hierarchy_hash216,
            "metadata_hash216": record.metadata_hash216,
            "vector_object_id": record.vector_object_id,
            "total_span": record.total_span,
            "base_hops": record.base_hops,
            "direct_component_count": record.direct_component_count,
            "leaf_jump_ids": list(record.leaf_jump_ids),
            "native_receipt": native_receipt,
            "idempotent": False,
            "encrypted_snapshot": True,
            "restart_rehydratable": True,
            "one_snapshot_direct_reuse": True,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def promote_path(
        self,
        *,
        superedge_id: str,
        current_state: Sequence[int],
        jump_ids: Sequence[str],
        goal_hash216: str,
        tick: int,
        cycle_index: int,
    ) -> dict[str, Any]:
        if len(jump_ids) < 2:
            raise ValueError("level-1 superedge requires at least two persistent route edges")
        reused = self.graph.reuse_path(
            current_state=current_state,
            jump_ids=jump_ids,
            goal_hash216=goal_hash216,
            tick=tick,
            cycle_index=cycle_index,
        )
        path = reused["path"]
        if not path["exact_target"]:
            raise ValueError("superedge promotion requires an exact 1.40 target route")
        records = {record.jump_id: record for record in self.memory.records()}
        ordered = [records[str(jump_id)] for jump_id in jump_ids]
        if any(record.quarantined for record in ordered):
            raise ValueError("cannot promote quarantined persistent edge")
        layers = {record.layer_index for record in ordered}
        if len(layers) != 1:
            raise ValueError("level-1 superedge components must share one layer index")
        return self._persist_superedge(
            superedge_id=superedge_id,
            hierarchy_level=1,
            parent_state=current_state,
            terminal_state=reused["terminal_state"],
            route_hash216=path["path_hash216"],
            total_span=int(path["total_span"]),
            base_hops=len(ordered),
            component_ids=[record.jump_id for record in ordered],
            component_levels=[0 for _ in ordered],
            component_seals=[record.composition_hash216 for record in ordered],
            leaf_jump_ids=[record.jump_id for record in ordered],
            tick=tick,
            cycle_index=cycle_index,
            layer_index=next(iter(layers)),
        )

    def promote_superedges(
        self,
        *,
        superedge_id: str,
        current_state: Sequence[int],
        component_superedge_ids: Sequence[str],
        goal_hash216: str,
        tick: int,
        cycle_index: int,
    ) -> dict[str, Any]:
        split_hash216(goal_hash216)
        if len(component_superedge_ids) < 2:
            raise ValueError("higher-level superedge requires at least two component superedges")
        current = tuple(int(value) for value in current_state)
        start_hash216 = self.native.state_root(current)
        component_records: list[PersistentSuperedgeRecord] = []
        leaf_ids: list[str] = []
        for component_id in component_superedge_ids:
            try:
                record = self._records[str(component_id)]
            except KeyError as exc:
                raise KeyError(f"unknown component superedge: {component_id}") from exc
            if record.quarantined:
                raise ValueError("cannot compose quarantined superedge")
            reused = self.reuse(current_state=current, superedge_id=record.superedge_id)
            current = tuple(int(value) for value in reused["child_state"])
            component_records.append(record)
            leaf_ids.extend(record.leaf_jump_ids)
        terminal_hash216 = self.native.state_root(current)
        if terminal_hash216 != goal_hash216:
            raise ValueError("higher-level superedge terminal does not equal requested exact goal")
        layers = {record.layer_index for record in component_records}
        if len(layers) != 1:
            raise ValueError("higher-level superedge components must share one layer index")
        route_payload = {
            "schema": "HHS_PASS_219_LANE5_SUPEREDGE_ROUTE_1_41",
            "start_hash216": start_hash216,
            "goal_hash216": goal_hash216,
            "component_ids": [record.superedge_id for record in component_records],
            "component_hierarchy_hash216": [
                record.hierarchy_hash216 for record in component_records
            ],
            "cycle_index": int(cycle_index) + int(tick) // CYCLE,
            "phase_slot": int(tick) % CYCLE,
        }
        route_hash216 = self.native.hash216_bytes(_canonical(route_payload))
        return self._persist_superedge(
            superedge_id=superedge_id,
            hierarchy_level=1 + max(record.hierarchy_level for record in component_records),
            parent_state=current_state,
            terminal_state=current,
            route_hash216=route_hash216,
            total_span=sum(record.total_span for record in component_records),
            base_hops=sum(record.base_hops for record in component_records),
            component_ids=[record.superedge_id for record in component_records],
            component_levels=[record.hierarchy_level for record in component_records],
            component_seals=[record.hierarchy_hash216 for record in component_records],
            leaf_jump_ids=leaf_ids,
            tick=tick,
            cycle_index=cycle_index,
            layer_index=next(iter(layers)),
        )

    def _native_record_receipt(self, record: PersistentSuperedgeRecord) -> dict[str, Any]:
        component_lineage_identity = sha256(
            b"HHS-P219-LANE5-SUPEREDGE-COMPONENT-LINEAGE-1.41\0"
            + _canonical(
                [
                    [component_id, component_level, component_seal]
                    for component_id, component_level, component_seal in zip(
                        record.component_ids, record.component_levels, record.component_seals
                    )
                ]
            )
        ).hexdigest()
        flattened_leaf_identity = sha256(
            b"HHS-P219-LANE5-SUPEREDGE-FLATTENED-LEAVES-1.41\0"
            + _canonical(list(record.leaf_jump_ids))
        ).hexdigest()
        receipt = self.abi.validate(
            hierarchy_level=record.hierarchy_level,
            direct_component_count=record.direct_component_count,
            base_hops=record.base_hops,
            total_span=record.total_span,
            phase_slot=record.phase_slot,
            layer_index=record.layer_index,
            cycle_index=record.cycle_index,
            parent_hash216=record.parent_hash216,
            child_hash216=record.child_hash216,
            route_hash216=record.route_hash216,
            hierarchy_hash216=record.hierarchy_hash216,
            metadata_hash216=record.metadata_hash216,
            component_lineage_identity=component_lineage_identity,
            flattened_leaf_identity=flattened_leaf_identity,
        )
        if int(receipt["hierarchy_receipt_signature64"]) != record.native_receipt_signature64:
            raise ValueError("superedge native receipt signature mismatch")
        return receipt

    def reuse(
        self,
        *,
        current_state: Sequence[int],
        superedge_id: str,
    ) -> dict[str, Any]:
        try:
            record = self._records[superedge_id]
        except KeyError as exc:
            raise KeyError(f"unknown superedge: {superedge_id}") from exc
        if record.quarantined:
            raise ValueError("superedge is quarantined")
        current_root = self.native.state_root(current_state)
        if current_root != record.parent_hash216:
            raise ValueError("superedge parent does not match current state Hash216")
        try:
            if not self._metadata_valid(record):
                raise ValueError("superedge metadata Hash216 mismatch")
            if not self._hierarchy_valid(record):
                raise ValueError("superedge hierarchy Hash216 mismatch")
            if not self._leaf_dependencies_live(record):
                raise ValueError("superedge level-0 dependency is unavailable or quarantined")
            native_receipt = self._native_record_receipt(record)
            vector_object, frame = self.vector_store.retrieve(
                record.operation_key,
                legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
                genesis_identity=GENESIS_IDENTITY,
            )
            if vector_object.object_id != record.vector_object_id:
                raise ValueError("superedge vector object identity mismatch")
            if vector_object.operation_identity_sha256 != record.operation_identity_sha256:
                raise ValueError("superedge vector operation identity mismatch")
            if vector_object.hash216.combined != record.hierarchy_hash216:
                raise ValueError("superedge vector hierarchy Hash216 mismatch")
            if vector_object.hash216.index_root_sha256 != record.hash216_index_root_sha256:
                raise ValueError("superedge vector Hash216 index root mismatch")
            expected_parent_hash72 = _state_hash72(
                "HHS-P219-LANE5-SUPEREDGE-PARENT-HASH72-1.41", record.parent_hash216
            )
            expected_child_hash72 = _state_hash72(
                "HHS-P219-LANE5-SUPEREDGE-CHILD-HASH72-1.41", record.child_hash216
            )
            if vector_object.input_hash72 != expected_parent_hash72:
                raise ValueError("superedge parent Hash72 binding mismatch")
            if vector_object.output_hash72 != expected_child_hash72:
                raise ValueError("superedge child Hash72 binding mismatch")
            child_state = _unpack_state(frame)
            if self.native.state_root(child_state) != record.child_hash216:
                raise ValueError("superedge terminal VM5184 state/Hash216 mismatch")
        except Exception:
            self._quarantine_record(record)
            raise
        return {
            "schema": "HHS_PASS_219_LANE5_SUPEREDGE_REUSE_1_41",
            "superedge_id": record.superedge_id,
            "hierarchy_level": record.hierarchy_level,
            "parent_hash216": record.parent_hash216,
            "child_hash216": record.child_hash216,
            "route_hash216": record.route_hash216,
            "hierarchy_hash216": record.hierarchy_hash216,
            "metadata_hash216": record.metadata_hash216,
            "vector_object_id": record.vector_object_id,
            "child_state": list(child_state),
            "total_span": record.total_span,
            "base_hops": record.base_hops,
            "direct_component_count": record.direct_component_count,
            "leaf_jump_ids": list(record.leaf_jump_ids),
            "persistent_snapshot_retrievals": 1,
            "component_snapshot_retrievals": 0,
            "represented_transitions": record.total_span,
            "intermediate_vm81_transitions_executed": 0,
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

    def search(
        self,
        *,
        current_state: Sequence[int],
        goal_hash216: str,
        tick: int,
        cycle_index: int,
        layer_index: int | None = None,
        min_level: int = 1,
        top_k: int = 32,
    ) -> dict[str, Any]:
        split_hash216(goal_hash216)
        parent_hash216 = self.native.state_root(current_state)
        records = [
            self._records[superedge_id]
            for superedge_id in self._by_parent.get(parent_hash216, [])
            if not self._records[superedge_id].quarantined
            and self._records[superedge_id].hierarchy_level >= int(min_level)
        ]
        if layer_index is not None:
            records = [record for record in records if record.layer_index == int(layer_index)]
        live = [record for record in records if self._leaf_dependencies_live(record)]
        candidates = [
            Hash216CompositionCandidate(
                candidate_id=record.superedge_id,
                hash216=record.child_hash216,
                validated=True,
                jump_span=record.total_span,
                lineage_signature=record.hierarchy_hash216,
            )
            for record in live
        ]
        ranked = self.optimizer.search_hash216(
            query_hash216=goal_hash216,
            candidates=candidates,
            tick=int(tick),
            cycle_index=int(cycle_index),
            top_k=max(1, int(top_k)),
        )
        ranked["superedge_hierarchy"] = True
        ranked["parent_hash216"] = parent_hash216
        ranked["active_superedge_candidates"] = len(live)
        ranked["candidate_only"] = True
        return ranked

    def quarantine(self, superedge_id: str) -> None:
        try:
            record = self._records[superedge_id]
        except KeyError as exc:
            raise KeyError(f"unknown superedge: {superedge_id}") from exc
        self._quarantine_record(record)

    def records(self) -> tuple[PersistentSuperedgeRecord, ...]:
        rows = self._connection.execute(
            "SELECT superedge_id FROM lane5_superedges ORDER BY sequence"
        ).fetchall()
        return tuple(
            self._records[str(row["superedge_id"])]
            for row in rows
            if str(row["superedge_id"]) in self._records
        )


__all__ = ["PersistentSuperedgeRecord", "Pass219Lane5SuperedgeHierarchy"]
