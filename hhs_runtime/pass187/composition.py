"""HHS Pass 187 universal multimodal composition authority.

Canonical graph mutation is subordinate to inherited VM81 admission. The caller
must supply a nonzero inherited Hash72 receipt for every mutation. This runtime
records that receipt and derives local evidence identities; it never issues a
second canonical Hash72 commit stream.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
import shutil
import sqlite3
import stat
import threading
import zipfile
from collections import deque
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

CONTRACT_ID = "HHS-P187-UMOACF-IR-HC-VM81-H72-H216"
COMPLETION_CLASSIFICATION = "HHS_PASS_187_UNIVERSAL_COMPOSITION_AND_INCREMENTAL_RECOMPOSITION_VERIFIED"
ZERO_HASH72 = "0" * 72

RELATIONSHIPS = {
    "LIVE",
    "SNAPSHOT",
    "REFERENCE",
    "FORK",
    "LAYER",
    "NEST",
    "FEEDBACK",
    "CONTROL",
    "COMPILED",
}
PROPAGATING_RELATIONSHIPS = {"LIVE", "LAYER", "NEST", "FEEDBACK", "CONTROL", "COMPILED"}
GRAPH_MUTATIONS = {
    "CREATE",
    "IMPORT",
    "RECORD",
    "CONNECT",
    "DISCONNECT",
    "INTEGRATE",
    "LAYER",
    "REORDER",
    "NEST",
    "UNNEST",
    "FREEZE",
    "SNAPSHOT",
    "REFERENCE",
    "FORK",
    "BRANCH",
    "MERGE",
    "REVERSE",
    "REPLACE",
    "INVALIDATE",
    "RECOMPOSE",
    "COMPILE",
}
ALL_OPERATIONS = GRAPH_MUTATIONS | {"REPLAY", "EXPORT", "STATUS", "OBJECTS", "PORTS", "COMPATIBILITY", "IMPACT"}

REQUIRED_DESCRIPTOR_FIELDS = (
    "logical_object_id",
    "immutable_version_id",
    "object_class",
    "modality_set",
    "content_identity",
    "source_identity",
    "provenance",
    "owner_or_mutation_authority",
    "permissions",
    "inputs",
    "outputs",
    "operations",
    "dependencies",
    "state_schema",
    "state_identity",
    "history_root",
    "replay_root",
    "compatible_egress_targets",
    "runtime_authority",
)


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


def require_hash72(value: str, name: str = "vm81_receipt_hash72") -> str:
    text = str(value)
    if len(text) != 72 or any(ch not in "0123456789abcdef" for ch in text):
        raise ValueError(f"{name} must be 72 lowercase hexadecimal glyphs")
    if text == ZERO_HASH72:
        raise ValueError(f"{name} may not be zero")
    return text


def _sorted_unique(values: Iterable[str]) -> list[str]:
    items = list(values)
    _reject_float(items)
    return sorted({str(item) for item in items})


def _port_map(descriptor: Mapping[str, Any], kind: str) -> dict[str, dict[str, Any]]:
    rows = descriptor.get(kind, [])
    return {str(row["name"]): dict(row) for row in rows}


def _graph_projection(state: Mapping[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(
        {
            "project_id": state["project_id"],
            "objects": state["objects"],
            "edges": state["edges"],
            "layers": state["layers"],
            "snapshots": state["snapshots"],
            "branches": state["branches"],
            "templates": state["templates"],
            "cache": state["cache"],
            "artifacts": state["artifacts"],
            "execution_counts": state["execution_counts"],
            "runtime_values": state["runtime_values"],
        }
    )


def harmonicode_expression(edge: Mapping[str, Any]) -> str:
    return (
        f"{edge['relationship']}("
        f"{edge['source_logical_object_id']}.{edge['source_port']} -> "
        f"{edge['target_logical_object_id']}.{edge['target_port']}"
        f", edge={edge['edge_id']})"
    )


def graph_to_harmonicode(state: Mapping[str, Any]) -> str:
    lines = [f"PROJECT {canonical_json({'project_id': state['project_id']})}"]
    for logical_id in sorted(state["objects"]):
        obj = state["objects"][logical_id]
        lines.append("OBJECT " + canonical_json(obj))
    for edge in sorted(state["edges"].values(), key=lambda row: (int(row["order"]), row["edge_id"])):
        lines.append("EDGE " + canonical_json(edge))
    for layer_id in sorted(state["layers"]):
        lines.append(
            "LAYERORDER "
            + canonical_json({"logical_object_id": layer_id, "edge_ids": state["layers"][layer_id]})
        )
    return "\n".join(lines) + "\n"


def parse_harmonicode(text: str) -> dict[str, Any]:
    project_id = None
    objects: dict[str, Any] = {}
    edges: dict[str, Any] = {}
    layers: dict[str, list[str]] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        prefix, payload = line.split(" ", 1)
        decoded = json.loads(payload)
        if prefix == "PROJECT":
            project_id = decoded["project_id"]
        elif prefix == "OBJECT":
            objects[decoded["logical_object_id"]] = decoded
        elif prefix == "EDGE":
            edges[decoded["edge_id"]] = decoded
        elif prefix == "LAYERORDER":
            layers[decoded["logical_object_id"]] = list(decoded["edge_ids"])
        else:
            raise ValueError(f"unknown Harmonicode record: {prefix}")
    if not project_id:
        raise ValueError("Harmonicode PROJECT record missing")
    return {
        "project_id": project_id,
        "objects": objects,
        "edges": edges,
        "layers": layers,
    }


class CompositionAuthority:
    def __init__(self, path: str | os.PathLike[str], project_id: str = "project.default"):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(self.path, timeout=5.0, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.execute("PRAGMA busy_timeout=5000")
        self._init_schema(project_id)

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "CompositionAuthority":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _init_schema(self, project_id: str) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS canonical_state(
                singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                state_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS events(
                sequence INTEGER PRIMARY KEY,
                operation TEXT NOT NULL,
                parameters_json TEXT NOT NULL,
                vm81_receipt_hash72 TEXT NOT NULL UNIQUE,
                predecessor_vm81_receipt_hash72 TEXT NOT NULL,
                event_evidence_hash72 TEXT NOT NULL,
                hash216 TEXT NOT NULL,
                reversible INTEGER NOT NULL,
                compensation_json TEXT NOT NULL,
                pre_state_json TEXT NOT NULL,
                post_state_json TEXT NOT NULL
            );
            """
        )
        row = self._connection.execute(
            "SELECT state_json FROM canonical_state WHERE singleton=1"
        ).fetchone()
        if row is None:
            genesis = {
                "schema": "HHS_PASS_187_COMPOSITION_STATE_V1",
                "contract": CONTRACT_ID,
                "project_id": project_id,
                "objects": {},
                "edges": {},
                "layers": {},
                "snapshots": {},
                "branches": {},
                "templates": {},
                "cache": {},
                "artifacts": [],
                "execution_counts": {},
                "runtime_values": {},
                "frozen_objects": [],
                "active_branch": "main",
            }
            self._connection.execute(
                "INSERT INTO canonical_state(singleton,state_json) VALUES(1,?)",
                (canonical_json(genesis),),
            )
            self._connection.commit()

    def state(self) -> dict[str, Any]:
        row = self._connection.execute(
            "SELECT state_json FROM canonical_state WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise RuntimeError("canonical state missing")
        return json.loads(row["state_json"])

    def _last_event(self, conn: sqlite3.Connection | None = None) -> tuple[int, str]:
        connection = conn or self._connection
        row = connection.execute(
            "SELECT sequence,vm81_receipt_hash72 FROM events ORDER BY sequence DESC LIMIT 1"
        ).fetchone()
        return (int(row[0]), str(row[1])) if row else (0, ZERO_HASH72)

    def _commit(
        self,
        operation: str,
        parameters: Mapping[str, Any],
        vm81_receipt_hash72: str,
        apply: Callable[[dict[str, Any]], tuple[dict[str, Any], Any]],
        *,
        reversible: bool = True,
        compensation: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        receipt = require_hash72(vm81_receipt_hash72)
        params = dict(parameters)
        _reject_float(params)
        with self._lock:
            conn = self._connection
            conn.execute("BEGIN IMMEDIATE")
            try:
                if conn.execute(
                    "SELECT 1 FROM events WHERE vm81_receipt_hash72=?", (receipt,)
                ).fetchone():
                    raise ValueError("duplicate inherited VM81 Hash72 receipt")
                pre = self.state()
                sequence, predecessor_receipt = self._last_event(conn)
                sequence += 1
                post, result = apply(copy.deepcopy(pre))
                post_json = canonical_json(post)
                evidence = hash72(
                    "HHS-P187-COMPOSITION-EVENT-EVIDENCE",
                    {
                        "sequence": sequence,
                        "operation": operation,
                        "parameters": params,
                        "vm81_receipt_hash72": receipt,
                        "pre_state_identity": hash72("HHS-P187-PRE-STATE", pre),
                        "post_state_identity": hash72("HHS-P187-POST-STATE", post),
                    },
                )
                hash216 = predecessor_receipt + receipt + evidence
                conn.execute(
                    """INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        sequence,
                        operation,
                        canonical_json(params),
                        receipt,
                        predecessor_receipt,
                        evidence,
                        hash216,
                        1 if reversible else 0,
                        canonical_json(dict(compensation or {})),
                        canonical_json(pre),
                        post_json,
                    ),
                )
                conn.execute(
                    "UPDATE canonical_state SET state_json=? WHERE singleton=1",
                    (post_json,),
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return {
            "sequence": sequence,
            "operation": operation,
            "vm81_receipt_hash72": receipt,
            "predecessor_vm81_receipt_hash72": predecessor_receipt,
            "event_evidence_hash72": evidence,
            "hash216": hash216,
            "result": result,
        }

    @staticmethod
    def descriptor(
        *,
        logical_object_id: str,
        object_class: str,
        modality_set: Sequence[str],
        content_identity: str,
        source_identity: str,
        provenance: Mapping[str, Any],
        owner_or_mutation_authority: str,
        permissions: Sequence[str],
        inputs: Sequence[Mapping[str, Any]],
        outputs: Sequence[Mapping[str, Any]],
        operations: Sequence[str],
        dependencies: Sequence[str],
        state_schema: Mapping[str, Any],
        state: Mapping[str, Any],
        compatible_egress_targets: Sequence[str],
        runtime_authority: str = "INHERITED_VM81",
        parent_version_id: str | None = None,
        version_number: int = 1,
        trusted: bool = True,
    ) -> dict[str, Any]:
        base = {
            "logical_object_id": logical_object_id,
            "version_number": int(version_number),
            "object_class": object_class,
            "modality_set": _sorted_unique(modality_set),
            "content_identity": content_identity,
            "source_identity": source_identity,
            "provenance": dict(provenance),
            "owner_or_mutation_authority": owner_or_mutation_authority,
            "permissions": _sorted_unique(permissions),
            "inputs": [dict(row) for row in inputs],
            "outputs": [dict(row) for row in outputs],
            "operations": [str(item) for item in operations],
            "dependencies": [str(item) for item in dependencies],
            "state_schema": dict(state_schema),
            "state": dict(state),
            "compatible_egress_targets": _sorted_unique(compatible_egress_targets),
            "runtime_authority": runtime_authority,
            "parent_version_id": parent_version_id,
            "trusted": bool(trusted),
        }
        _reject_float(base)
        immutable_version_id = "ov_" + hash72("HHS-P187-OBJECT-VERSION", base)
        state_identity = hash72("HHS-P187-OBJECT-STATE", base["state"])
        history_root = hash72(
            "HHS-P187-OBJECT-HISTORY",
            {
                "logical_object_id": logical_object_id,
                "immutable_version_id": immutable_version_id,
                "parent_version_id": parent_version_id,
            },
        )
        replay_root = hash72(
            "HHS-P187-OBJECT-REPLAY",
            {
                "source_identity": source_identity,
                "content_identity": content_identity,
                "state_identity": state_identity,
            },
        )
        result = {
            **base,
            "immutable_version_id": immutable_version_id,
            "state_identity": state_identity,
            "history_root": history_root,
            "replay_root": replay_root,
        }
        for field in REQUIRED_DESCRIPTOR_FIELDS:
            if field not in result:
                raise AssertionError(f"descriptor field missing: {field}")
        return result

    @staticmethod
    def _active_descriptor(state: Mapping[str, Any], logical_object_id: str) -> dict[str, Any]:
        obj = state["objects"].get(logical_object_id)
        if obj is None:
            raise KeyError(f"unknown object: {logical_object_id}")
        active = obj["active_version_id"]
        for version in obj["versions"]:
            if version["immutable_version_id"] == active:
                return version
        raise RuntimeError(f"active version missing: {logical_object_id}")

    def create_object(
        self,
        descriptor: Mapping[str, Any],
        vm81_receipt_hash72: str,
        *,
        imported: bool = False,
    ) -> dict[str, Any]:
        row = dict(descriptor)
        _reject_float(row)
        logical_id = str(row["logical_object_id"])
        if imported and bool(row.get("trusted", True)):
            raise ValueError("imported descriptor must be explicitly marked trusted=false before admission")
        params = {
            "logical_object_id": logical_id,
            "immutable_version_id": row["immutable_version_id"],
            "imported": bool(imported),
        }

        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            if logical_id in state["objects"]:
                raise ValueError("logical object already exists")
            state["objects"][logical_id] = {
                "logical_object_id": logical_id,
                "active_version_id": row["immutable_version_id"],
                "versions": [row],
            }
            state["execution_counts"][logical_id] = 0
            return state, {"descriptor": row}

        return self._commit("IMPORT" if imported else "CREATE", params, vm81_receipt_hash72, apply)

    def replace_object(
        self,
        logical_object_id: str,
        *,
        state_update: Mapping[str, Any] | None,
        content_identity: str | None,
        vm81_receipt_hash72: str,
    ) -> dict[str, Any]:
        params = {
            "logical_object_id": logical_object_id,
            "state_update": dict(state_update or {}),
            "content_identity": content_identity,
        }

        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            if logical_object_id in state["frozen_objects"]:
                raise PermissionError("object is frozen")
            old = self._active_descriptor(state, logical_object_id)
            next_state = dict(old["state"])
            next_state.update(dict(state_update or {}))
            new = self.descriptor(
                logical_object_id=logical_object_id,
                object_class=old["object_class"],
                modality_set=old["modality_set"],
                content_identity=content_identity or old["content_identity"],
                source_identity=old["source_identity"],
                provenance={**old["provenance"], "replaced_from": old["immutable_version_id"]},
                owner_or_mutation_authority=old["owner_or_mutation_authority"],
                permissions=old["permissions"],
                inputs=old["inputs"],
                outputs=old["outputs"],
                operations=old["operations"],
                dependencies=old["dependencies"],
                state_schema=old["state_schema"],
                state=next_state,
                compatible_egress_targets=old["compatible_egress_targets"],
                runtime_authority=old["runtime_authority"],
                parent_version_id=old["immutable_version_id"],
                version_number=int(old["version_number"]) + 1,
                trusted=bool(old.get("trusted", True)),
            )
            state["objects"][logical_object_id]["versions"].append(new)
            state["objects"][logical_object_id]["active_version_id"] = new["immutable_version_id"]
            return state, {
                "previous_version_id": old["immutable_version_id"],
                "immutable_version_id": new["immutable_version_id"],
                "descriptor": new,
            }

        return self._commit("REPLACE", params, vm81_receipt_hash72, apply)

    def objects(self) -> dict[str, Any]:
        state = self.state()
        return {
            logical_id: self._active_descriptor(state, logical_id)
            for logical_id in sorted(state["objects"])
        }

    def ports(self, logical_object_id: str) -> dict[str, Any]:
        descriptor = self._active_descriptor(self.state(), logical_object_id)
        return {"inputs": descriptor["inputs"], "outputs": descriptor["outputs"]}

    def compatibility(
        self,
        source_logical_object_id: str,
        source_port: str,
        target_logical_object_id: str,
        target_port: str,
    ) -> dict[str, Any]:
        state = self.state()
        source = self._active_descriptor(state, source_logical_object_id)
        target = self._active_descriptor(state, target_logical_object_id)
        outputs = _port_map(source, "outputs")
        inputs = _port_map(target, "inputs")
        if source_port not in outputs:
            return {"compatible": False, "reason": "SOURCE_PORT_MISSING"}
        if target_port not in inputs:
            return {"compatible": False, "reason": "TARGET_PORT_MISSING"}
        source_type = outputs[source_port].get("type")
        target_type = inputs[target_port].get("type")
        if source_type == target_type:
            return {
                "compatible": True,
                "match": "EXACT",
                "source_type": source_type,
                "target_type": target_type,
            }
        adapters = []
        for logical_id in sorted(state["objects"]):
            row = self._active_descriptor(state, logical_id)
            if row["object_class"] != "adapter":
                continue
            ins = _port_map(row, "inputs")
            outs = _port_map(row, "outputs")
            if any(p.get("type") == source_type for p in ins.values()) and any(
                p.get("type") == target_type for p in outs.values()
            ):
                adapters.append(logical_id)
        return {
            "compatible": False,
            "reason": "EXPLICIT_ADAPTER_REQUIRED" if adapters else "INCOMPATIBLE_PORT_TYPES",
            "source_type": source_type,
            "target_type": target_type,
            "adapter_candidates": adapters,
        }

    def connect(
        self,
        *,
        edge_id: str,
        source_logical_object_id: str,
        source_port: str,
        target_logical_object_id: str,
        target_port: str,
        relationship: str,
        vm81_receipt_hash72: str,
        metadata: Mapping[str, Any] | None = None,
        order: int | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        if relationship not in RELATIONSHIPS:
            raise ValueError("unknown relationship")
        if operation_name is None:
            operation_name = relationship if relationship in {"LAYER", "NEST", "REFERENCE"} else "CONNECT"
        if source_logical_object_id == target_logical_object_id and relationship != "FEEDBACK":
            raise ValueError("self-edge requires FEEDBACK")
        meta = dict(metadata or {})
        if relationship == "FEEDBACK" and int(meta.get("max_iterations", 0)) <= 0:
            raise ValueError("FEEDBACK requires positive max_iterations")
        compat = self.compatibility(
            source_logical_object_id, source_port, target_logical_object_id, target_port
        )
        if not compat["compatible"]:
            raise ValueError(compat["reason"])
        params = {
            "edge_id": edge_id,
            "source_logical_object_id": source_logical_object_id,
            "source_port": source_port,
            "target_logical_object_id": target_logical_object_id,
            "target_port": target_port,
            "relationship": relationship,
            "metadata": meta,
            "order": order,
        }

        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            if edge_id in state["edges"]:
                raise ValueError("edge already exists")
            source = self._active_descriptor(state, source_logical_object_id)
            target = self._active_descriptor(state, target_logical_object_id)
            next_order = int(order) if order is not None else len(state["edges"])
            edge = {
                "edge_id": edge_id,
                "source_logical_object_id": source_logical_object_id,
                "source_version_id": source["immutable_version_id"],
                "source_port": source_port,
                "target_logical_object_id": target_logical_object_id,
                "target_version_id": target["immutable_version_id"],
                "target_port": target_port,
                "relationship": relationship,
                "metadata": meta,
                "order": next_order,
                "expression": "",
            }
            edge["expression"] = harmonicode_expression(edge)
            state["edges"][edge_id] = edge
            if relationship == "LAYER":
                state["layers"].setdefault(target_logical_object_id, []).append(edge_id)
            return state, {"edge": edge, "compatibility": compat}

        return self._commit(operation_name, params, vm81_receipt_hash72, apply)

    def disconnect(
        self,
        edge_id: str,
        vm81_receipt_hash72: str,
        *,
        operation_name: str = "DISCONNECT",
    ) -> dict[str, Any]:
        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            edge = state["edges"].pop(edge_id, None)
            if edge is None:
                raise KeyError("unknown edge")
            for rows in state["layers"].values():
                if edge_id in rows:
                    rows.remove(edge_id)
            return state, {"edge": edge}

        return self._commit(operation_name, {"edge_id": edge_id}, vm81_receipt_hash72, apply)

    def reorder_layer(
        self,
        logical_object_id: str,
        edge_ids: Sequence[str],
        vm81_receipt_hash72: str,
    ) -> dict[str, Any]:
        ids = list(edge_ids)

        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            current = state["layers"].get(logical_object_id, [])
            if sorted(current) != sorted(ids):
                raise ValueError("reorder must contain exact current layer edge set")
            state["layers"][logical_object_id] = ids
            for index, edge_id in enumerate(ids):
                state["edges"][edge_id]["order"] = index
                state["edges"][edge_id]["expression"] = harmonicode_expression(state["edges"][edge_id])
            return state, {"logical_object_id": logical_object_id, "edge_ids": ids}

        return self._commit(
            "REORDER",
            {"logical_object_id": logical_object_id, "edge_ids": ids},
            vm81_receipt_hash72,
            apply,
        )

    def freeze(self, logical_object_id: str, vm81_receipt_hash72: str) -> dict[str, Any]:
        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            self._active_descriptor(state, logical_object_id)
            if logical_object_id not in state["frozen_objects"]:
                state["frozen_objects"].append(logical_object_id)
                state["frozen_objects"].sort()
            return state, {"logical_object_id": logical_object_id, "frozen": True}

        return self._commit("FREEZE", {"logical_object_id": logical_object_id}, vm81_receipt_hash72, apply)

    def snapshot(self, snapshot_id: str, vm81_receipt_hash72: str) -> dict[str, Any]:
        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            if snapshot_id in state["snapshots"]:
                raise ValueError("snapshot already exists")
            projection = _graph_projection(state)
            identity = hash72("HHS-P187-SNAPSHOT", projection)
            state["snapshots"][snapshot_id] = {
                "snapshot_id": snapshot_id,
                "identity": identity,
                "projection": projection,
            }
            return state, {"snapshot_id": snapshot_id, "identity": identity}

        return self._commit("SNAPSHOT", {"snapshot_id": snapshot_id}, vm81_receipt_hash72, apply)

    def fork_object(
        self,
        source_logical_object_id: str,
        new_logical_object_id: str,
        vm81_receipt_hash72: str,
    ) -> dict[str, Any]:
        state = self.state()
        old = self._active_descriptor(state, source_logical_object_id)
        forked = self.descriptor(
            logical_object_id=new_logical_object_id,
            object_class=old["object_class"],
            modality_set=old["modality_set"],
            content_identity=old["content_identity"],
            source_identity=old["source_identity"],
            provenance={**old["provenance"], "forked_from": old["immutable_version_id"]},
            owner_or_mutation_authority=old["owner_or_mutation_authority"],
            permissions=old["permissions"],
            inputs=old["inputs"],
            outputs=old["outputs"],
            operations=old["operations"],
            dependencies=old["dependencies"],
            state_schema=old["state_schema"],
            state=old["state"],
            compatible_egress_targets=old["compatible_egress_targets"],
            runtime_authority=old["runtime_authority"],
            parent_version_id=old["immutable_version_id"],
            version_number=1,
            trusted=bool(old.get("trusted", True)),
        )
        params = {
            "source_logical_object_id": source_logical_object_id,
            "new_logical_object_id": new_logical_object_id,
            "source_version_id": old["immutable_version_id"],
            "fork_version_id": forked["immutable_version_id"],
        }

        def apply(next_state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            if new_logical_object_id in next_state["objects"]:
                raise ValueError("fork target already exists")
            next_state["objects"][new_logical_object_id] = {
                "logical_object_id": new_logical_object_id,
                "active_version_id": forked["immutable_version_id"],
                "versions": [forked],
            }
            next_state["execution_counts"][new_logical_object_id] = 0
            return next_state, {"descriptor": forked}

        return self._commit("FORK", params, vm81_receipt_hash72, apply)

    def branch(self, branch_id: str, vm81_receipt_hash72: str) -> dict[str, Any]:
        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            if branch_id in state["branches"]:
                raise ValueError("branch already exists")
            state["branches"][branch_id] = {
                "branch_id": branch_id,
                "parent_branch_id": state["active_branch"],
                "base_identity": hash72("HHS-P187-BRANCH-BASE", _graph_projection(state)),
                "projection": _graph_projection(state),
            }
            return state, {"branch_id": branch_id, "base_identity": state["branches"][branch_id]["base_identity"]}

        return self._commit("BRANCH", {"branch_id": branch_id}, vm81_receipt_hash72, apply)

    def merge_branch(self, branch_id: str, vm81_receipt_hash72: str) -> dict[str, Any]:
        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            branch = state["branches"].get(branch_id)
            if branch is None:
                raise KeyError("unknown branch")
            branch_projection = branch["projection"]
            conflicts = []
            for logical_id, branch_obj in branch_projection["objects"].items():
                current_obj = state["objects"].get(logical_id)
                if current_obj is None:
                    continue
                if (
                    current_obj["active_version_id"] != branch_obj["active_version_id"]
                    and current_obj["active_version_id"] not in {
                        version["immutable_version_id"] for version in branch_obj["versions"]
                    }
                ):
                    conflicts.append(logical_id)
            if conflicts:
                raise ValueError("branch merge conflict:" + ",".join(sorted(conflicts)))
            return state, {"branch_id": branch_id, "compatible": True, "conflicts": []}

        return self._commit("MERGE", {"branch_id": branch_id}, vm81_receipt_hash72, apply)

    def record_template(
        self,
        template_id: str,
        start_sequence: int,
        end_sequence: int,
        vm81_receipt_hash72: str,
        parameterize: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        rows = self._connection.execute(
            "SELECT operation,parameters_json FROM events WHERE sequence BETWEEN ? AND ? ORDER BY sequence",
            (int(start_sequence), int(end_sequence)),
        ).fetchall()
        if not rows:
            raise ValueError("no events in record range")
        template = [
            {"operation": row["operation"], "parameters": json.loads(row["parameters_json"])}
            for row in rows
        ]
        mapping = dict(parameterize or {})

        def parameterize_value(value: Any) -> Any:
            if isinstance(value, str) and value in mapping:
                return "${" + str(mapping[value]) + "}"
            if isinstance(value, list):
                return [parameterize_value(item) for item in value]
            if isinstance(value, dict):
                return {key: parameterize_value(item) for key, item in value.items()}
            return value

        template = parameterize_value(template)

        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            if template_id in state["templates"]:
                raise ValueError("template already exists")
            state["templates"][template_id] = {
                "template_id": template_id,
                "operations": template,
                "structure_identity": hash72("HHS-P187-TEMPLATE", template),
            }
            return state, state["templates"][template_id]

        return self._commit(
            "RECORD",
            {
                "template_id": template_id,
                "start_sequence": start_sequence,
                "end_sequence": end_sequence,
                "parameterize": mapping,
            },
            vm81_receipt_hash72,
            apply,
        )

    def template_replay_structure(self, template_id: str, parameters: Mapping[str, str] | None = None) -> dict[str, Any]:
        template = self.state()["templates"].get(template_id)
        if template is None:
            raise KeyError("unknown template")
        mapping = dict(parameters or {})
        rows = copy.deepcopy(template["operations"])
        encoded = canonical_json(rows)
        for key, value in sorted(mapping.items()):
            encoded = encoded.replace(" + str(key) + ", str(value))
        decoded = json.loads(encoded)
        return {
            "template_id": template_id,
            "operations": decoded,
            "structure_identity": hash72("HHS-P187-TEMPLATE", decoded),
        }

    def reverse(self, sequence: int, vm81_receipt_hash72: str) -> dict[str, Any]:
        row = self._connection.execute(
            "SELECT * FROM events WHERE sequence=?", (int(sequence),)
        ).fetchone()
        if row is None:
            raise KeyError("unknown event")
        if not bool(row["reversible"]):
            compensation = json.loads(row["compensation_json"])
            raise PermissionError("irreversible event; compensation required:" + canonical_json(compensation))
        pre_state = json.loads(row["pre_state_json"])

        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            preserved = {
                "snapshots": state["snapshots"],
                "branches": state["branches"],
                "templates": state["templates"],
                "artifacts": state["artifacts"],
            }
            restored = copy.deepcopy(pre_state)
            restored["snapshots"].update(preserved["snapshots"])
            restored["branches"].update(preserved["branches"])
            restored["templates"].update(preserved["templates"])
            restored["artifacts"].extend(
                item for item in preserved["artifacts"] if item not in restored["artifacts"]
            )
            return restored, {"reversed_sequence": int(sequence)}

        return self._commit(
            "REVERSE",
            {"reversed_sequence": int(sequence)},
            vm81_receipt_hash72,
            apply,
        )

    def _downstream(self, state: Mapping[str, Any]) -> dict[str, set[str]]:
        outgoing: dict[str, set[str]] = {}
        for edge in state["edges"].values():
            if edge["relationship"] not in PROPAGATING_RELATIONSHIPS:
                continue
            outgoing.setdefault(edge["source_logical_object_id"], set()).add(
                edge["target_logical_object_id"]
            )
        return outgoing

    def impact(self, changed_logical_object_ids: Sequence[str]) -> dict[str, Any]:
        state = self.state()
        outgoing = self._downstream(state)
        affected = set(str(item) for item in changed_logical_object_ids)
        queue = deque(sorted(affected))
        while queue:
            node = queue.popleft()
            for target in sorted(outgoing.get(node, ())):
                if target not in affected:
                    affected.add(target)
                    queue.append(target)
        all_nodes = set(state["objects"])
        return {
            "changed": sorted(set(str(item) for item in changed_logical_object_ids)),
            "affected": sorted(affected),
            "unaffected": sorted(all_nodes - affected),
        }

    def invalidate(
        self,
        changed_logical_object_ids: Sequence[str],
        vm81_receipt_hash72: str,
    ) -> dict[str, Any]:
        impact = self.impact(changed_logical_object_ids)

        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            for key, row in state["cache"].items():
                if row["logical_object_id"] in impact["affected"]:
                    row["stale"] = True
            return state, impact

        return self._commit(
            "INVALIDATE",
            {"changed_logical_object_ids": list(changed_logical_object_ids)},
            vm81_receipt_hash72,
            apply,
        )

    def _topological_plan(self, state: Mapping[str, Any], affected: set[str]) -> list[str]:
        indegree = {node: 0 for node in affected}
        outgoing: dict[str, set[str]] = {}
        for edge in state["edges"].values():
            if edge["relationship"] == "FEEDBACK":
                continue
            source = edge["source_logical_object_id"]
            target = edge["target_logical_object_id"]
            if source in affected and target in affected and edge["relationship"] in PROPAGATING_RELATIONSHIPS:
                outgoing.setdefault(source, set()).add(target)
                indegree[target] += 1
        queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
        plan: list[str] = []
        while queue:
            node = queue.popleft()
            plan.append(node)
            for target in sorted(outgoing.get(node, ())):
                indegree[target] -= 1
                if indegree[target] == 0:
                    queue.append(target)
        remaining = sorted(set(affected) - set(plan))
        plan.extend(remaining)
        return plan

    def recompose(
        self,
        changed_logical_object_ids: Sequence[str],
        vm81_receipt_hash72: str,
        *,
        authority_scope: str,
        license_scope: str,
        target: str = "runtime",
    ) -> dict[str, Any]:
        impact = self.impact(changed_logical_object_ids)
        affected = set(impact["affected"])

        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            plan = self._topological_plan(state, affected)
            executed: list[str] = []
            cache_hits: list[str] = []
            for logical_id in plan:
                descriptor = self._active_descriptor(state, logical_id)
                deps = sorted(
                    edge["source_logical_object_id"]
                    for edge in state["edges"].values()
                    if edge["target_logical_object_id"] == logical_id
                    and edge["relationship"] in PROPAGATING_RELATIONSHIPS
                )
                dependency_fingerprint = hash72(
                    "HHS-P187-DEPENDENCY-FINGERPRINT",
                    {
                        "logical_object_id": logical_id,
                        "active_version_id": descriptor["immutable_version_id"],
                        "dependencies": [
                            {
                                "logical_object_id": dep,
                                "active_version_id": self._active_descriptor(
                                    state, dep
                                )["immutable_version_id"],
                                "runtime_value_identity": state["runtime_values"].get(
                                    dep,
                                    self._active_descriptor(
                                        state, dep
                                    )["immutable_version_id"],
                                ),
                            }
                            for dep in deps
                        ],
                    },
                )
                cache_key = hash72(
                    "HHS-P187-CACHE-KEY",
                    {
                        "project_id": state["project_id"],
                        "logical_object_id": logical_id,
                        "target": target,
                        "authority_scope": authority_scope,
                        "license_scope": license_scope,
                        "dependency_fingerprint": dependency_fingerprint,
                    },
                )
                row = state["cache"].get(cache_key)
                if row and not row["stale"]:
                    cache_hits.append(logical_id)
                    continue
                value_identity = hash72(
                    "HHS-P187-RECOMPOSED-VALUE",
                    {
                        "logical_object_id": logical_id,
                        "active_version_id": descriptor["immutable_version_id"],
                        "dependency_fingerprint": dependency_fingerprint,
                        "target": target,
                    },
                )
                state["cache"][cache_key] = {
                    "cache_key": cache_key,
                    "logical_object_id": logical_id,
                    "target": target,
                    "authority_scope": authority_scope,
                    "license_scope": license_scope,
                    "dependency_fingerprint": dependency_fingerprint,
                    "value_identity": value_identity,
                    "stale": False,
                }
                state["runtime_values"][logical_id] = value_identity
                state["execution_counts"][logical_id] = int(state["execution_counts"].get(logical_id, 0)) + 1
                executed.append(logical_id)
            return state, {
                **impact,
                "plan": plan,
                "executed": executed,
                "cache_hits": cache_hits,
                "execution_counts": {
                    logical_id: state["execution_counts"].get(logical_id, 0)
                    for logical_id in sorted(state["objects"])
                },
            }

        return self._commit(
            "RECOMPOSE",
            {
                "changed_logical_object_ids": list(changed_logical_object_ids),
                "authority_scope": authority_scope,
                "license_scope": license_scope,
                "target": target,
            },
            vm81_receipt_hash72,
            apply,
        )

    def compatibility_plan(self, target: str) -> dict[str, Any]:
        state = self.state()
        unsupported = []
        for logical_id in sorted(state["objects"]):
            descriptor = self._active_descriptor(state, logical_id)
            targets = set(descriptor["compatible_egress_targets"])
            if target not in targets and "*" not in targets:
                unsupported.append(logical_id)
        return {
            "target": target,
            "compatible": not unsupported,
            "unsupported_objects": unsupported,
            "human_report": (
                f"target={target}: compatible"
                if not unsupported
                else f"target={target}: unsupported objects: {', '.join(unsupported)}"
            ),
        }

    @staticmethod
    def _deterministic_zip(path: Path, files: Mapping[str, bytes]) -> None:
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name in sorted(files):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                archive.writestr(info, files[name])

    def compile_target(
        self,
        target: str,
        output_path: str | os.PathLike[str],
        vm81_receipt_hash72: str,
    ) -> dict[str, Any]:
        plan = self.compatibility_plan(target)
        if not plan["compatible"]:
            raise ValueError(plan["human_report"])
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        state_before = self.state()
        projection = _graph_projection(state_before)
        graph_identity = hash72("HHS-P187-COMPILED-GRAPH", projection)
        manifest = {
            "schema": "HHS_PASS_187_COMPILED_ARTIFACT_V1",
            "contract": CONTRACT_ID,
            "project_id": state_before["project_id"],
            "target": target,
            "graph_identity": graph_identity,
            "harmonicode": graph_to_harmonicode(state_before),
        }
        if target == "web-app":
            escaped = json.dumps(manifest, sort_keys=True).replace("</", "<\/")
            output.write_text(
                "<!doctype html><html><head><meta charset=\"utf-8\"><title>HHS P187 App</title></head>"
                "<body><main id=\"app\" tabindex=\"0\">Compiled HHS composition application</main>"
                f"<script type=\"application/json\" id=\"hhs-graph\">{escaped}</script></body></html>",
                encoding="utf-8",
            )
        elif target == "project-bundle":
            self._deterministic_zip(
                output,
                {
                    "manifest.json": (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
                    "graph.harmonicode": manifest["harmonicode"].encode(),
                },
            )
        elif target == "native-cli":
            output.write_text(
                "#!/usr/bin/env python3\n"
                "import json\n"
                f"print(json.dumps({json.dumps(manifest, sort_keys=True)}, sort_keys=True))\n",
                encoding="utf-8",
            )
            output.chmod(0o755)
        else:
            raise ValueError("unsupported compiler target")
        artifact_sha256 = hashlib.sha256(output.read_bytes()).hexdigest()
        artifact = {
            "artifact_id": "artifact_" + hash72(
                "HHS-P187-ARTIFACT",
                {"target": target, "graph_identity": graph_identity, "sha256": artifact_sha256},
            ),
            "target": target,
            "path": str(output),
            "sha256": artifact_sha256,
            "graph_identity": graph_identity,
        }

        def apply(state: dict[str, Any]) -> tuple[dict[str, Any], Any]:
            state["artifacts"].append(artifact)
            return state, {"plan": plan, "artifact": artifact}

        return self._commit(
            "COMPILE",
            {"target": target, "output_path": str(output), "graph_identity": graph_identity},
            vm81_receipt_hash72,
            apply,
            reversible=False,
            compensation={"action": "delete_artifact", "path": str(output)},
        )

    def export(self, output_path: str | os.PathLike[str]) -> dict[str, Any]:
        state = self.state()
        payload = {
            "schema": "HHS_PASS_187_COMPOSITION_EXPORT_V1",
            "contract": CONTRACT_ID,
            "state": state,
            "harmonicode": graph_to_harmonicode(state),
            "replay": self.replay(),
        }
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {"path": str(destination), "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()}

    def replay(self) -> dict[str, Any]:
        predecessor_receipt = ZERO_HASH72
        expected_sequence = 1
        last_post = None
        for row in self._connection.execute("SELECT * FROM events ORDER BY sequence"):
            if int(row["sequence"]) != expected_sequence:
                return {"valid": False, "reason": "SEQUENCE_DRIFT", "events": expected_sequence - 1}
            if row["predecessor_vm81_receipt_hash72"] != predecessor_receipt:
                return {"valid": False, "reason": "RECEIPT_PREDECESSOR_DRIFT", "events": expected_sequence - 1}
            params = json.loads(row["parameters_json"])
            pre = json.loads(row["pre_state_json"])
            post = json.loads(row["post_state_json"])
            evidence = hash72(
                "HHS-P187-COMPOSITION-EVENT-EVIDENCE",
                {
                    "sequence": expected_sequence,
                    "operation": row["operation"],
                    "parameters": params,
                    "vm81_receipt_hash72": row["vm81_receipt_hash72"],
                    "pre_state_identity": hash72("HHS-P187-PRE-STATE", pre),
                    "post_state_identity": hash72("HHS-P187-POST-STATE", post),
                },
            )
            expected_hash216 = predecessor_receipt + row["vm81_receipt_hash72"] + evidence
            if evidence != row["event_evidence_hash72"] or expected_hash216 != row["hash216"]:
                return {"valid": False, "reason": "EVENT_EVIDENCE_DRIFT", "events": expected_sequence - 1}
            predecessor_receipt = row["vm81_receipt_hash72"]
            last_post = post
            expected_sequence += 1
        current = self.state()
        if last_post is not None and canonical_json(last_post) != canonical_json(current):
            return {"valid": False, "reason": "MATERIALIZED_STATE_DRIFT", "events": expected_sequence - 1}
        return {
            "valid": True,
            "events": expected_sequence - 1,
            "last_vm81_receipt_hash72": predecessor_receipt,
            "state_identity": hash72("HHS-P187-CURRENT-STATE", current),
            "hash216_archive_complete": True,
            "local_event_evidence_is_mutation_authority": False,
        }

    def status(self) -> dict[str, Any]:
        state = self.state()
        replay = self.replay()
        harmonicode = graph_to_harmonicode(state)
        roundtrip = parse_harmonicode(harmonicode)
        expected = {
            "project_id": state["project_id"],
            "objects": state["objects"],
            "edges": state["edges"],
            "layers": state["layers"],
        }
        return {
            "schema": "HHS_PASS_187_COMPOSITION_STATUS_V1",
            "contract": CONTRACT_ID,
            "classification": COMPLETION_CLASSIFICATION if replay["valid"] else "HHS_PASS_187_COMPOSITION_VERIFY_FAILED",
            "replay": replay,
            "object_count": len(state["objects"]),
            "edge_count": len(state["edges"]),
            "harmonicode_roundtrip": canonical_json(roundtrip) == canonical_json(expected),
            "vm81_receipt_required_for_mutation": True,
            "independent_vm81_authority": False,
            "independent_hash72_clock": False,
            "browser_authority": False,
            "cache_authority": False,
            "compiled_artifact_authority": False,
            "floating_point_canonical_authority": False,
        }

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
        return {
            "path": str(target),
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "events": replay["events"],
            "state_identity": replay["state_identity"],
        }

    @classmethod
    def recover(
        cls,
        checkpoint_path: str | os.PathLike[str],
        destination_path: str | os.PathLike[str],
        expected_sha256: str,
        expected_events: int,
        expected_state_identity: str,
    ) -> "CompositionAuthority":
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
            or replay["state_identity"] != expected_state_identity
        ):
            authority.close()
            destination.unlink(missing_ok=True)
            raise ValueError("recovered graph does not match checkpoint witness")
        return authority

    def execute(self, operation: str, args: Mapping[str, Any]) -> Any:
        op = operation.upper()
        kwargs = dict(args)
        if op == "CREATE":
            return self.create_object(kwargs["descriptor"], kwargs["vm81_receipt_hash72"])
        if op == "IMPORT":
            return self.create_object(kwargs["descriptor"], kwargs["vm81_receipt_hash72"], imported=True)
        if op in {"CONNECT", "INTEGRATE", "LAYER", "NEST", "REFERENCE"}:
            relationship = {
                "CONNECT": kwargs.pop("relationship", "LIVE"),
                "INTEGRATE": "LIVE",
                "LAYER": "LAYER",
                "NEST": "NEST",
                "REFERENCE": "REFERENCE",
            }[op]
            return self.connect(relationship=relationship, operation_name=op, **kwargs)
        if op in {"DISCONNECT", "UNNEST"}:
            return self.disconnect(
                kwargs["edge_id"],
                kwargs["vm81_receipt_hash72"],
                operation_name=op,
            )
        if op == "REORDER":
            return self.reorder_layer(
                kwargs["logical_object_id"], kwargs["edge_ids"], kwargs["vm81_receipt_hash72"]
            )
        if op == "FREEZE":
            return self.freeze(kwargs["logical_object_id"], kwargs["vm81_receipt_hash72"])
        if op == "SNAPSHOT":
            return self.snapshot(kwargs["snapshot_id"], kwargs["vm81_receipt_hash72"])
        if op == "FORK":
            return self.fork_object(
                kwargs["source_logical_object_id"],
                kwargs["new_logical_object_id"],
                kwargs["vm81_receipt_hash72"],
            )
        if op == "BRANCH":
            return self.branch(kwargs["branch_id"], kwargs["vm81_receipt_hash72"])
        if op == "MERGE":
            return self.merge_branch(kwargs["branch_id"], kwargs["vm81_receipt_hash72"])
        if op == "RECORD":
            return self.record_template(
                kwargs["template_id"],
                kwargs["start_sequence"],
                kwargs["end_sequence"],
                kwargs["vm81_receipt_hash72"],
                kwargs.get("parameterize"),
            )
        if op == "REVERSE":
            return self.reverse(kwargs["sequence"], kwargs["vm81_receipt_hash72"])
        if op == "REPLAY":
            return self.replay()
        if op == "REPLACE":
            return self.replace_object(
                kwargs["logical_object_id"],
                state_update=kwargs.get("state_update"),
                content_identity=kwargs.get("content_identity"),
                vm81_receipt_hash72=kwargs["vm81_receipt_hash72"],
            )
        if op == "INVALIDATE":
            return self.invalidate(
                kwargs["changed_logical_object_ids"], kwargs["vm81_receipt_hash72"]
            )
        if op == "RECOMPOSE":
            return self.recompose(**kwargs)
        if op == "COMPILE":
            return self.compile_target(
                kwargs["target"], kwargs["output_path"], kwargs["vm81_receipt_hash72"]
            )
        if op == "EXPORT":
            return self.export(kwargs["output_path"])
        if op == "STATUS":
            return self.status()
        if op == "OBJECTS":
            return self.objects()
        if op == "PORTS":
            return self.ports(kwargs["logical_object_id"])
        if op == "COMPATIBILITY":
            return self.compatibility(
                kwargs["source_logical_object_id"],
                kwargs["source_port"],
                kwargs["target_logical_object_id"],
                kwargs["target_port"],
            )
        if op == "IMPACT":
            return self.impact(kwargs["changed_logical_object_ids"])
        raise KeyError(f"unknown Pass 187 operation: {operation}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="HHS Pass 187 composition authority")
    parser.add_argument("--db", required=True)
    parser.add_argument("operation")
    parser.add_argument("--json", default="{}")
    ns = parser.parse_args(argv)
    args = json.loads(ns.json)
    with CompositionAuthority(ns.db) as authority:
        result = authority.execute(ns.operation, args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
