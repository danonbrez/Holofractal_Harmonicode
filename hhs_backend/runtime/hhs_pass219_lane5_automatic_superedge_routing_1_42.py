"""Automatic exact cross-level Lane 5 routing and superedge promotion, Pass 219 1.42.

The controller searches one exact Hash216 graph containing persistent level-0
composition jumps and persistent level-1..n superedges. Selection is integer and
lexicographic, with persistent snapshot retrieval count as the primary cost.
Repeated authenticated routes may be promoted through the inherited 1.41
constructors. All returned states remain candidate-only until signed
environmental VM81 admission.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import split_hash216
from hhs_backend.runtime.hhs_pass219_lane5_superedge_hierarchy_1_41 import (
    Pass219Lane5SuperedgeHierarchy,
    _canonical,
    _exact_state,
)
from hhs_python.runtime.hhs_pass219_lane5_automatic_superedge_routing_bridge import (
    CYCLE,
    DEFAULT_PROMOTION_THRESHOLD,
    Pass219Lane5AutomaticSuperedgeRoutingBridge,
)

SCHEMA = "HHS_PASS_219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_1_42"


def _route_key(
    *,
    route_kind: str,
    start_hash216: str,
    goal_hash216: str,
    layer_index: int,
    component_ids: Sequence[str],
) -> str:
    payload = {
        "schema": "HHS_PASS_219_LANE5_AUTOMATIC_ROUTE_IDENTITY_1_42",
        "route_kind": str(route_kind),
        "start_hash216": str(start_hash216),
        "goal_hash216": str(goal_hash216),
        "layer_index": int(layer_index),
        "component_ids": [str(value) for value in component_ids],
    }
    return sha256(_canonical(payload)).hexdigest()


class Pass219Lane5AutomaticSuperedgeRouter:
    """Exact multi-level candidate router with restart-persistent promotion observations."""

    def __init__(
        self,
        state_root: str | Path,
        *,
        vector_key: bytes | None = None,
        backend: str = "CPU_REFERENCE",
        require_physical_gpu: bool = False,
        promotion_threshold: int = DEFAULT_PROMOTION_THRESHOLD,
    ) -> None:
        threshold = int(promotion_threshold)
        if threshold < 2:
            raise ValueError("automatic promotion threshold must be at least two exact observations")
        self.state_root = Path(state_root).resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.database_path = self.state_root / "lane5_automatic_superedge_routing.sqlite3"
        self.hierarchy = Pass219Lane5SuperedgeHierarchy(
            self.state_root,
            vector_key=vector_key,
            backend=backend,
            require_physical_gpu=require_physical_gpu,
        )
        self.graph = self.hierarchy.graph
        self.memory = self.hierarchy.memory
        self.native = self.hierarchy.native
        self.abi = Pass219Lane5AutomaticSuperedgeRoutingBridge()
        self.promotion_threshold = threshold
        self._connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._init_schema()

    def __enter__(self) -> "Pass219Lane5AutomaticSuperedgeRouter":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()
        self.hierarchy.close()

    def _init_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS lane5_route_observations (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                route_key TEXT NOT NULL UNIQUE,
                route_kind TEXT NOT NULL,
                start_hash216 TEXT NOT NULL,
                goal_hash216 TEXT NOT NULL,
                layer_index INTEGER NOT NULL,
                component_ids_json TEXT NOT NULL,
                observed_count INTEGER NOT NULL,
                promoted_superedge_id TEXT,
                quarantined INTEGER NOT NULL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS lane5_route_observation_endpoints
                ON lane5_route_observations(start_hash216, goal_hash216, layer_index, sequence);
            """
        )
        self._connection.commit()

    def status(self) -> dict[str, Any]:
        rows = self._connection.execute(
            "SELECT observed_count,promoted_superedge_id,quarantined FROM lane5_route_observations"
        ).fetchall()
        return {
            "schema": SCHEMA,
            "authority": self.abi.authority(),
            "promotion_threshold": self.promotion_threshold,
            "observed_routes": len(rows),
            "exact_observations": sum(int(row["observed_count"]) for row in rows),
            "promoted_routes": sum(1 for row in rows if row["promoted_superedge_id"]),
            "quarantined_observations": sum(int(row["quarantined"]) for row in rows),
            "cross_level_exact_routing": True,
            "automatic_repeated_route_promotion": True,
            "integer_only_routing_cost": True,
            "mixed_level_candidate_routing": True,
            "mixed_level_recursive_promotion": False,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def _edge_catalog(self, *, layer_index: int | None) -> dict[str, list[dict[str, Any]]]:
        result: dict[str, list[dict[str, Any]]] = {}
        for record in self.memory.records():
            if record.quarantined:
                continue
            if layer_index is not None and record.layer_index != int(layer_index):
                continue
            edge = {
                "candidate_id": record.jump_id,
                "candidate_kind": "LEVEL0",
                "hierarchy_level": 0,
                "parent_hash216": record.parent_hash216,
                "child_hash216": record.child_hash216,
                "represented_span": int(record.jump_span),
                "base_hops": 1,
                "layer_index": int(record.layer_index),
                "lineage_seal": record.composition_hash216,
            }
            result.setdefault(record.parent_hash216, []).append(edge)
        for record in self.hierarchy.records():
            if record.quarantined or not self.hierarchy._leaf_dependencies_live(record):
                continue
            if layer_index is not None and record.layer_index != int(layer_index):
                continue
            edge = {
                "candidate_id": record.superedge_id,
                "candidate_kind": "SUPEREDGE",
                "hierarchy_level": int(record.hierarchy_level),
                "parent_hash216": record.parent_hash216,
                "child_hash216": record.child_hash216,
                "represented_span": int(record.total_span),
                "base_hops": int(record.base_hops),
                "layer_index": int(record.layer_index),
                "lineage_seal": record.hierarchy_hash216,
            }
            result.setdefault(record.parent_hash216, []).append(edge)
        for edges in result.values():
            edges.sort(
                key=lambda edge: (
                    int(edge["hierarchy_level"]),
                    str(edge["candidate_kind"]),
                    str(edge["candidate_id"]),
                )
            )
        return result

    @staticmethod
    def _plan_cost(edges: Sequence[Mapping[str, Any]]) -> tuple[Any, ...]:
        levels = [int(edge["hierarchy_level"]) for edge in edges]
        return (
            len(edges),
            max(levels, default=0),
            sum(levels),
            sum(int(edge["represented_span"]) for edge in edges),
            tuple(str(edge["candidate_id"]) for edge in edges),
        )

    def plan_route(
        self,
        *,
        current_state: Sequence[int],
        goal_hash216: str,
        tick: int,
        cycle_index: int,
        max_retrievals: int = 8,
        layer_index: int | None = None,
    ) -> dict[str, Any]:
        parent = _exact_state(current_state)
        split_hash216(goal_hash216)
        if int(tick) < 0 or int(cycle_index) < 0:
            raise ValueError("tick and cycle_index must be nonnegative")
        if int(max_retrievals) < 1:
            raise ValueError("max_retrievals must be positive")
        start_hash216 = self.native.state_root(parent)
        if start_hash216 == goal_hash216:
            raise ValueError("automatic route requires a distinct exact goal")
        by_parent = self._edge_catalog(layer_index=layer_index)
        frontier: list[tuple[str, list[dict[str, Any]], frozenset[str], int | None]] = [
            (start_hash216, [], frozenset((start_hash216,)), None)
        ]
        selected: list[dict[str, Any]] | None = None

        for _depth in range(1, int(max_retrievals) + 1):
            next_by_node: dict[tuple[str, int], tuple[str, list[dict[str, Any]], frozenset[str], int]] = {}
            solutions: list[list[dict[str, Any]]] = []
            for node_hash216, route, visited, route_layer in frontier:
                for edge in by_parent.get(node_hash216, ()): 
                    edge_layer = int(edge["layer_index"])
                    if route_layer is not None and edge_layer != route_layer:
                        continue
                    child = str(edge["child_hash216"])
                    if child in visited:
                        continue
                    new_route = route + [dict(edge)]
                    if child == goal_hash216:
                        solutions.append(new_route)
                        continue
                    key = (child, edge_layer)
                    candidate = (child, new_route, visited | frozenset((child,)), edge_layer)
                    prior = next_by_node.get(key)
                    if prior is None or self._plan_cost(new_route) < self._plan_cost(prior[1]):
                        next_by_node[key] = candidate
            if solutions:
                selected = min(solutions, key=self._plan_cost)
                break
            frontier = sorted(
                next_by_node.values(),
                key=lambda item: (self._plan_cost(item[1]), item[0], item[3]),
            )
            if not frontier:
                break

        if selected is None:
            return {
                "schema": SCHEMA,
                "found": False,
                "exact_target": False,
                "start_hash216": start_hash216,
                "goal_hash216": goal_hash216,
                "max_retrievals": int(max_retrievals),
                "candidate_only": True,
            }

        chosen_layer = int(selected[0]["layer_index"])
        retrieval_count = len(selected)
        base_hops = sum(int(edge["base_hops"]) for edge in selected)
        represented_span = sum(int(edge["represented_span"]) for edge in selected)
        max_level = max(int(edge["hierarchy_level"]) for edge in selected)
        phase_slot = int(tick) % CYCLE
        effective_cycle = int(cycle_index) + int(tick) // CYCLE
        ordered_candidate_identity = sha256(
            b"HHS-P219-LANE5-AUTOMATIC-ORDERED-CANDIDATES-1.42\0"
            + _canonical([
                [
                    edge["candidate_kind"],
                    edge["candidate_id"],
                    edge["hierarchy_level"],
                    edge["lineage_seal"],
                ]
                for edge in selected
            ])
        ).hexdigest()
        route_payload = {
            "schema": "HHS_PASS_219_LANE5_AUTOMATIC_ROUTE_SEAL_1_42",
            "start_hash216": start_hash216,
            "goal_hash216": goal_hash216,
            "phase_slot": phase_slot,
            "cycle_index": effective_cycle,
            "layer_index": chosen_layer,
            "edges": selected,
        }
        route_hash216 = self.native.hash216_bytes(_canonical(route_payload))
        native_receipt = self.abi.validate_plan(
            retrieval_count=retrieval_count,
            base_hops=base_hops,
            represented_span=represented_span,
            max_hierarchy_level=max_level,
            phase_slot=phase_slot,
            layer_index=chosen_layer,
            cycle_index=effective_cycle,
            parent_hash216=start_hash216,
            goal_hash216=goal_hash216,
            route_hash216=route_hash216,
            ordered_candidate_identity=ordered_candidate_identity,
        )
        if not native_receipt["accepted"] or native_receipt["canonical_mutation_authority"]:
            raise RuntimeError("native automatic routing membrane rejected exact candidate plan")
        return {
            "schema": "HHS_PASS_219_LANE5_AUTOMATIC_ROUTE_PLAN_1_42",
            "found": True,
            "exact_target": True,
            "start_hash216": start_hash216,
            "goal_hash216": goal_hash216,
            "route_hash216": route_hash216,
            "ordered_candidate_identity": ordered_candidate_identity,
            "edges": selected,
            "retrieval_count": retrieval_count,
            "base_hops": base_hops,
            "represented_span": represented_span,
            "max_hierarchy_level": max_level,
            "phase_slot": phase_slot,
            "cycle_index": effective_cycle,
            "layer_index": chosen_layer,
            "integer_cost": list(self._plan_cost(selected)[:-1]),
            "native_receipt": native_receipt,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def execute_plan(
        self,
        *,
        current_state: Sequence[int],
        plan: Mapping[str, Any],
    ) -> dict[str, Any]:
        if not bool(plan.get("found")) or not bool(plan.get("exact_target")):
            raise ValueError("cannot execute non-exact automatic routing plan")
        current = _exact_state(current_state)
        if self.native.state_root(current) != str(plan["start_hash216"]):
            raise ValueError("automatic routing plan parent does not match current state")
        receipts: list[dict[str, Any]] = []
        for edge in plan["edges"]:
            if self.native.state_root(current) != str(edge["parent_hash216"]):
                raise ValueError("automatic route exact Hash216 adjacency failure")
            if str(edge["candidate_kind"]) == "LEVEL0":
                reused = self.memory.reuse(
                    current_state=current,
                    jump_id=str(edge["candidate_id"]),
                )
                child = _exact_state(reused["child_state"])
            elif str(edge["candidate_kind"]) == "SUPEREDGE":
                reused = self.hierarchy.reuse(
                    current_state=current,
                    superedge_id=str(edge["candidate_id"]),
                )
                child = _exact_state(reused["child_state"])
            else:
                raise ValueError("unknown automatic routing candidate kind")
            if self.native.state_root(child) != str(edge["child_hash216"]):
                raise RuntimeError("automatic route candidate child Hash216 mismatch")
            receipts.append(reused)
            current = child
        if self.native.state_root(current) != str(plan["goal_hash216"]):
            raise RuntimeError("automatic route terminal does not equal exact goal")
        return {
            "schema": "HHS_PASS_219_LANE5_AUTOMATIC_ROUTE_REUSE_1_42",
            "route_hash216": str(plan["route_hash216"]),
            "terminal_state": list(current),
            "terminal_hash216": self.native.state_root(current),
            "retrieval_count": int(plan["retrieval_count"]),
            "represented_transitions": int(plan["represented_span"]),
            "base_hops": int(plan["base_hops"]),
            "intermediate_vm81_transitions_executed": 0,
            "candidate_receipts": receipts,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_persistence_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def _observe_exact(
        self,
        *,
        route_kind: str,
        start_hash216: str,
        goal_hash216: str,
        layer_index: int,
        component_ids: Sequence[str],
    ) -> tuple[str, int, str | None]:
        split_hash216(start_hash216)
        split_hash216(goal_hash216)
        ids = tuple(str(value) for value in component_ids)
        if len(ids) < 2:
            raise ValueError("promotion observation requires at least two exact components")
        key = _route_key(
            route_kind=route_kind,
            start_hash216=start_hash216,
            goal_hash216=goal_hash216,
            layer_index=layer_index,
            component_ids=ids,
        )
        row = self._connection.execute(
            "SELECT * FROM lane5_route_observations WHERE route_key=?", (key,)
        ).fetchone()
        if row is None:
            count = 1
            promoted = None
            self._connection.execute(
                """INSERT INTO lane5_route_observations(
                    route_key,route_kind,start_hash216,goal_hash216,layer_index,
                    component_ids_json,observed_count,promoted_superedge_id,quarantined
                ) VALUES(?,?,?,?,?,?,1,NULL,0)""",
                (
                    key,
                    route_kind,
                    start_hash216,
                    goal_hash216,
                    int(layer_index),
                    json.dumps(list(ids), separators=(",", ":")),
                ),
            )
        else:
            if bool(row["quarantined"]):
                raise ValueError("route observation is quarantined")
            persisted_ids = tuple(str(value) for value in json.loads(str(row["component_ids_json"])))
            identity = (
                str(row["route_kind"]),
                str(row["start_hash216"]),
                str(row["goal_hash216"]),
                int(row["layer_index"]),
                persisted_ids,
            )
            requested = (route_kind, start_hash216, goal_hash216, int(layer_index), ids)
            if identity != requested:
                raise ValueError("route observation identity collision")
            count = int(row["observed_count"]) + 1
            promoted = str(row["promoted_superedge_id"]) if row["promoted_superedge_id"] else None
            self._connection.execute(
                "UPDATE lane5_route_observations SET observed_count=? WHERE route_key=?",
                (count, key),
            )
        self._connection.commit()
        return key, count, promoted

    def _promotion_id(self, route_key: str) -> str:
        return "auto-se-" + str(route_key)[:32]

    def observe_level0_route(
        self,
        *,
        current_state: Sequence[int],
        jump_ids: Sequence[str],
        goal_hash216: str,
        tick: int,
        cycle_index: int,
        auto_promote: bool = True,
    ) -> dict[str, Any]:
        parent = _exact_state(current_state)
        reused = self.graph.reuse_path(
            current_state=parent,
            jump_ids=jump_ids,
            goal_hash216=goal_hash216,
            tick=tick,
            cycle_index=cycle_index,
        )
        path = reused["path"]
        if not bool(path["exact_target"]):
            raise ValueError("only exact level-0 routes may be observed for promotion")
        records = {record.jump_id: record for record in self.memory.records()}
        ordered = [records[str(value)] for value in jump_ids]
        if any(record.quarantined for record in ordered):
            raise ValueError("quarantined level-0 route cannot increment promotion observation")
        layers = {int(record.layer_index) for record in ordered}
        if len(layers) != 1:
            raise ValueError("automatic promotion route must remain in one layer")
        start_hash216 = self.native.state_root(parent)
        layer = next(iter(layers))
        key, count, promoted = self._observe_exact(
            route_kind="LEVEL0_PATH",
            start_hash216=start_hash216,
            goal_hash216=goal_hash216,
            layer_index=layer,
            component_ids=jump_ids,
        )
        promotion = None
        promotion_gain = len(jump_ids) - 1
        if auto_promote and promoted is None and count >= self.promotion_threshold and promotion_gain >= 1:
            promoted = self._promotion_id(key)
            promotion = self.hierarchy.promote_path(
                superedge_id=promoted,
                current_state=parent,
                jump_ids=jump_ids,
                goal_hash216=goal_hash216,
                tick=tick,
                cycle_index=cycle_index,
            )
            self._connection.execute(
                "UPDATE lane5_route_observations SET promoted_superedge_id=? WHERE route_key=?",
                (promoted, key),
            )
            self._connection.commit()
        return {
            "schema": "HHS_PASS_219_LANE5_LEVEL0_PROMOTION_OBSERVATION_1_42",
            "route_key": key,
            "observation_count": count,
            "promotion_threshold": self.promotion_threshold,
            "promotion_gain_retrievals": promotion_gain,
            "promoted_superedge_id": promoted,
            "promotion": promotion,
            "exact_route": True,
            "candidate_only": True,
        }

    def observe_superedge_chain(
        self,
        *,
        current_state: Sequence[int],
        component_superedge_ids: Sequence[str],
        goal_hash216: str,
        tick: int,
        cycle_index: int,
        auto_promote: bool = True,
    ) -> dict[str, Any]:
        parent = _exact_state(current_state)
        split_hash216(goal_hash216)
        if len(component_superedge_ids) < 2:
            raise ValueError("superedge-chain observation requires at least two components")
        current = parent
        records = []
        for component_id in component_superedge_ids:
            by_id = {record.superedge_id: record for record in self.hierarchy.records()}
            try:
                record = by_id[str(component_id)]
            except KeyError as exc:
                raise KeyError(f"unknown observed superedge: {component_id}") from exc
            if record.quarantined or not self.hierarchy._leaf_dependencies_live(record):
                raise ValueError("quarantined superedge chain cannot increment promotion observation")
            reused = self.hierarchy.reuse(current_state=current, superedge_id=record.superedge_id)
            current = _exact_state(reused["child_state"])
            records.append(record)
        if self.native.state_root(current) != goal_hash216:
            raise ValueError("observed superedge chain does not terminate at exact goal")
        layers = {int(record.layer_index) for record in records}
        if len(layers) != 1:
            raise ValueError("automatic superedge-chain promotion must remain in one layer")
        start_hash216 = self.native.state_root(parent)
        layer = next(iter(layers))
        key, count, promoted = self._observe_exact(
            route_kind="SUPEREDGE_CHAIN",
            start_hash216=start_hash216,
            goal_hash216=goal_hash216,
            layer_index=layer,
            component_ids=component_superedge_ids,
        )
        promotion = None
        promotion_gain = len(component_superedge_ids) - 1
        if auto_promote and promoted is None and count >= self.promotion_threshold and promotion_gain >= 1:
            promoted = self._promotion_id(key)
            promotion = self.hierarchy.promote_superedges(
                superedge_id=promoted,
                current_state=parent,
                component_superedge_ids=component_superedge_ids,
                goal_hash216=goal_hash216,
                tick=tick,
                cycle_index=cycle_index,
            )
            self._connection.execute(
                "UPDATE lane5_route_observations SET promoted_superedge_id=? WHERE route_key=?",
                (promoted, key),
            )
            self._connection.commit()
        return {
            "schema": "HHS_PASS_219_LANE5_SUPEREDGE_PROMOTION_OBSERVATION_1_42",
            "route_key": key,
            "observation_count": count,
            "promotion_threshold": self.promotion_threshold,
            "promotion_gain_retrievals": promotion_gain,
            "promoted_superedge_id": promoted,
            "promotion": promotion,
            "exact_route": True,
            "candidate_only": True,
        }

    def route_and_reuse(
        self,
        *,
        current_state: Sequence[int],
        goal_hash216: str,
        tick: int,
        cycle_index: int,
        max_retrievals: int = 8,
        layer_index: int | None = None,
        learn: bool = True,
    ) -> dict[str, Any]:
        parent = _exact_state(current_state)
        plan = self.plan_route(
            current_state=parent,
            goal_hash216=goal_hash216,
            tick=tick,
            cycle_index=cycle_index,
            max_retrievals=max_retrievals,
            layer_index=layer_index,
        )
        if not plan["found"]:
            return {"schema": SCHEMA, "plan": plan, "executed": False, "candidate_only": True}
        reuse = self.execute_plan(current_state=parent, plan=plan)
        observation = None
        if learn and len(plan["edges"]) >= 2:
            kinds = {str(edge["candidate_kind"]) for edge in plan["edges"]}
            ids = [str(edge["candidate_id"]) for edge in plan["edges"]]
            if kinds == {"LEVEL0"}:
                observation = self.observe_level0_route(
                    current_state=parent,
                    jump_ids=ids,
                    goal_hash216=goal_hash216,
                    tick=tick,
                    cycle_index=cycle_index,
                    auto_promote=True,
                )
            elif kinds == {"SUPEREDGE"}:
                observation = self.observe_superedge_chain(
                    current_state=parent,
                    component_superedge_ids=ids,
                    goal_hash216=goal_hash216,
                    tick=tick,
                    cycle_index=cycle_index,
                    auto_promote=True,
                )
        return {
            "schema": "HHS_PASS_219_LANE5_AUTOMATIC_ROUTE_AND_REUSE_1_42",
            "plan": plan,
            "reuse": reuse,
            "observation": observation,
            "executed": True,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }

    def observations(self) -> tuple[dict[str, Any], ...]:
        rows = self._connection.execute(
            "SELECT * FROM lane5_route_observations ORDER BY sequence"
        ).fetchall()
        return tuple(
            {
                "route_key": str(row["route_key"]),
                "route_kind": str(row["route_kind"]),
                "start_hash216": str(row["start_hash216"]),
                "goal_hash216": str(row["goal_hash216"]),
                "layer_index": int(row["layer_index"]),
                "component_ids": list(json.loads(str(row["component_ids_json"]))),
                "observed_count": int(row["observed_count"]),
                "promoted_superedge_id": (
                    str(row["promoted_superedge_id"]) if row["promoted_superedge_id"] else None
                ),
                "quarantined": bool(row["quarantined"]),
            }
            for row in rows
        )


__all__ = ["Pass219Lane5AutomaticSuperedgeRouter"]
