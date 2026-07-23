from __future__ import annotations

import copy
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, Iterable, Mapping, Optional

from .common import sha256_json
from .model import AuthorityViolation, Pass152Error, ResourceBounded


_ALLOWED_CONTROL_FIELDS = frozenset({
    "scheduling",
    "resource_allocation",
    "branch_priority",
    "cache_placement",
    "equivalence_reuse",
    "speculative_depth",
    "representation_choice",
    "batching",
    "transport_order",
})

_PROHIBITED_CONTROL_FIELDS = frozenset({
    "invariant_truth",
    "committed_state",
    "authoritative_state",
    "authority_root",
    "semantic_identity",
    "semantic_version",
    "provenance",
    "receipt_history",
    "hash72_head",
    "vm81_admission",
})


def _fraction(value: Fraction | int | str) -> Fraction:
    if isinstance(value, Fraction):
        return value
    return Fraction(value)


def _json_fraction(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


@dataclass(frozen=True)
class LayerDefinition:
    layer_id: str
    index: int
    invariant_names: tuple[str, ...]
    admissible_control_fields: frozenset[str] = _ALLOWED_CONTROL_FIELDS


@dataclass(frozen=True)
class ControlVector:
    vector_id: str
    source_layer: str
    target_layer: str
    policy_version: str
    critical_weight: Fraction = Fraction(1, 1)
    risk_weight: Fraction = Fraction(1, 1)
    redundancy_weight: Fraction = Fraction(1, 1)
    branch_priority: Mapping[str, int] = field(default_factory=dict)
    max_batch: int = 1
    speculative_depth: int = 1
    reuse_enabled: bool = True
    skip_enabled: bool = True
    cache_enabled: bool = True
    representation_choice: str = "CANONICAL_EXACT"
    batching: str = "DETERMINISTIC_READY_BATCH"
    transport_order: str = "TYPED_DEPENDENCY_ORDER"

    def to_dict(self) -> dict[str, Any]:
        return {
            "vector_id": self.vector_id,
            "source_layer": self.source_layer,
            "target_layer": self.target_layer,
            "policy_version": self.policy_version,
            "critical_weight": _json_fraction(self.critical_weight),
            "risk_weight": _json_fraction(self.risk_weight),
            "redundancy_weight": _json_fraction(self.redundancy_weight),
            "branch_priority": dict(sorted(self.branch_priority.items())),
            "max_batch": self.max_batch,
            "speculative_depth": self.speculative_depth,
            "reuse_enabled": self.reuse_enabled,
            "skip_enabled": self.skip_enabled,
            "cache_enabled": self.cache_enabled,
            "representation_choice": self.representation_choice,
            "batching": self.batching,
            "transport_order": self.transport_order,
            "control_fields": sorted(_ALLOWED_CONTROL_FIELDS),
        }


class AppendOnlyLayerHistory:
    """Digest-chained causal history for one control layer.

    The chain may only be extended. Existing entries are copied on read and are
    never replaced by plan revision or optimization.
    """

    def __init__(self, layer_id: str) -> None:
        self.layer_id = layer_id
        self._entries: list[dict[str, Any]] = []
        self._tip = "0" * 64

    def append(self, event: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        body = {
            "schema": "HHS_PASS152_LAYER_HISTORY_ENTRY_V1",
            "layer_id": self.layer_id,
            "sequence": len(self._entries) + 1,
            "event": event,
            "previous_digest": self._tip,
            "payload": copy.deepcopy(dict(payload)),
        }
        digest = sha256_json(body)
        entry = {**body, "entry_digest": digest}
        self._entries.append(entry)
        self._tip = digest
        return copy.deepcopy(entry)

    def verify(self) -> bool:
        previous = "0" * 64
        for index, entry in enumerate(self._entries, start=1):
            if entry.get("sequence") != index or entry.get("previous_digest") != previous:
                return False
            body = {k: copy.deepcopy(v) for k, v in entry.items() if k != "entry_digest"}
            digest = sha256_json(body)
            if digest != entry.get("entry_digest"):
                return False
            previous = digest
        return previous == self._tip

    @property
    def tip(self) -> str:
        return self._tip

    @property
    def entries(self) -> list[dict[str, Any]]:
        return copy.deepcopy(self._entries)


class RecursiveControlInvariant:
    """Recursive supervisory optimization constrained by invariant authority.

    Higher layers may alter subordinate execution policy. They cannot alter
    lower-layer truth, committed state, provenance, receipt history, semantic
    identity, or authority boundaries.
    """

    def __init__(
        self,
        *,
        authority_root: str,
        semantic_version: str,
        committed_state_digest: str,
        policy_version: str,
        workers: int,
        max_horizon: int,
        receipt_writer: Any,
    ) -> None:
        self.authority_root = authority_root
        self.semantic_version = semantic_version
        self.committed_state_digest = committed_state_digest
        self.policy_version = policy_version
        self.workers = workers
        self.max_horizon = max_horizon
        self.receipts = receipt_writer
        self.layers: dict[str, LayerDefinition] = {
            "L0": LayerDefinition(
                "L0", 0,
                (
                    "AUTHORITATIVE_STATE_IMMUTABLE_DURING_PROPAGATION",
                    "VM81_ONLY_COMMIT_AUTHORITY",
                    "HASH72_ONLY_AFTER_VM81_CLOSURE",
                    "SEMANTIC_IDENTITY_PRESERVED",
                    "PROVENANCE_PRESERVED",
                    "CAUSAL_HISTORY_APPEND_ONLY",
                ),
            ),
            "L1": LayerDefinition(
                "L1", 1,
                (
                    "ELASTIC_CLOSURE",
                    "EARLY_PROPAGATION",
                    "DETERMINISTIC_LOGICAL_ORDER",
                    "RESOURCE_BOUNDED_EXECUTION",
                ),
            ),
            "L2": LayerDefinition(
                "L2", 2,
                (
                    "GLOBAL_STRUCTURE_MAY_OPTIMIZE_SUBORDINATE_POLICY",
                    "PREDICTION_INFLUENCES_PRIORITY_NOT_TRUTH",
                    "PLAN_REVISION_DOES_NOT_REWRITE_COMMITTED_PREFIX",
                ),
            ),
        }
        self.histories = {layer_id: AppendOnlyLayerHistory(layer_id) for layer_id in self.layers}
        self._active_plan_digest: Optional[str] = None
        self._control_sequence = 0
        self._committed_prefix_digest = sha256_json({
            "authority_root": authority_root,
            "semantic_version": semantic_version,
            "committed_state_digest": committed_state_digest,
        })
        for layer_id in sorted(self.layers, key=lambda item: self.layers[item].index):
            layer = self.layers[layer_id]
            entry = self.histories[layer_id].append("LAYER_OPEN", {
                "layer_index": layer.index,
                "invariants": list(layer.invariant_names),
                "committed_prefix_digest": self._committed_prefix_digest,
            })
            self.receipts.append(
                "P152_LAYER_HISTORY.jsonl",
                "HHS_PASS152_LAYER_HISTORY_V1",
                entry,
            )

    def _assert_core_context(self, context: Mapping[str, Any]) -> None:
        if context.get("authority_root") != self.authority_root:
            raise AuthorityViolation("recursive control attempted authority-root mutation")
        if context.get("semantic_version") != self.semantic_version:
            raise AuthorityViolation("recursive control attempted semantic-version mutation")
        if context.get("authoritative_state_digest") != self.committed_state_digest:
            raise AuthorityViolation("recursive control observed a rewritten committed state")

    def reject_prohibited_mutation(self, proposed: Mapping[str, Any]) -> None:
        prohibited = sorted(set(proposed) & _PROHIBITED_CONTROL_FIELDS)
        if prohibited:
            raise AuthorityViolation(
                "higher-layer control attempted prohibited truth mutation: " + ",".join(prohibited)
            )
        unsupported = sorted(set(proposed) - _ALLOWED_CONTROL_FIELDS)
        if unsupported:
            raise AuthorityViolation(
                "higher-layer control contains unsupported fields: " + ",".join(unsupported)
            )

    def optimize(
        self,
        *,
        source_layer: str,
        target_layer: str,
        ready_nodes: Iterable[Mapping[str, Any]],
        context: Mapping[str, Any],
        requested_controls: Optional[Mapping[str, Any]] = None,
    ) -> ControlVector:
        self._assert_core_context(context)
        source = self.layers[source_layer]
        target = self.layers[target_layer]
        if source.index <= target.index:
            raise AuthorityViolation("recursive control projection must move from higher to lower layer")
        requested = dict(requested_controls or {})
        self.reject_prohibited_mutation(requested)

        nodes = [dict(node) for node in ready_nodes]
        branch_priority: dict[str, int] = {}
        for node in nodes:
            critical = _fraction(node.get("critical_cost", 0))
            risk = _fraction(node.get("predicted_risk", 0))
            redundancy = _fraction(node.get("redundancy_cost", 0))
            explicit = int(dict(requested.get("branch_priority", {})).get(str(node["node_id"]), 0))
            score = critical * 1000 - risk * 100 - redundancy * 100 + explicit
            branch_priority[str(node["node_id"])] = int(score)

        max_batch = int(requested.get("batching", {}).get("max_batch", min(self.workers, max(1, len(nodes))))) if isinstance(requested.get("batching"), Mapping) else min(self.workers, max(1, len(nodes)))
        if max_batch < 1 or max_batch > self.workers:
            raise ResourceBounded("recursive control max_batch exceeds worker policy")
        speculative_depth = int(requested.get("speculative_depth", self.max_horizon))
        if speculative_depth < 1 or speculative_depth > self.max_horizon:
            raise ResourceBounded("recursive control speculative depth exceeds horizon")

        self._control_sequence += 1
        provisional = {
            "sequence": self._control_sequence,
            "source_layer": source_layer,
            "target_layer": target_layer,
            "policy_version": self.policy_version,
            "branch_priority": dict(sorted(branch_priority.items())),
            "max_batch": max_batch,
            "speculative_depth": speculative_depth,
            "ready_node_ids": sorted(str(node["node_id"]) for node in nodes),
            "committed_prefix_digest": self._committed_prefix_digest,
        }
        vector_id = "P152-CV-" + sha256_json(provisional)[:24]
        vector = ControlVector(
            vector_id=vector_id,
            source_layer=source_layer,
            target_layer=target_layer,
            policy_version=self.policy_version,
            critical_weight=Fraction(1, 1),
            risk_weight=Fraction(1, 1),
            redundancy_weight=Fraction(1, 1),
            branch_priority=branch_priority,
            max_batch=max_batch,
            speculative_depth=speculative_depth,
            reuse_enabled=bool(requested.get("equivalence_reuse", True)),
            skip_enabled=bool(requested.get("scheduling", {}).get("allow_invariant_skip", True)) if isinstance(requested.get("scheduling"), Mapping) else True,
            cache_enabled=bool(requested.get("cache_placement", True)),
            representation_choice=str(requested.get("representation_choice", "CANONICAL_EXACT")),
            batching="DETERMINISTIC_READY_BATCH",
            transport_order=str(requested.get("transport_order", "TYPED_DEPENDENCY_ORDER")),
        )

        new_plan_digest = sha256_json(vector.to_dict())
        if self._active_plan_digest is not None and self._active_plan_digest != new_plan_digest:
            revision = self.histories[source_layer].append("FUTURE_PLAN_REVISED", {
                "old_plan_digest": self._active_plan_digest,
                "new_plan_digest": new_plan_digest,
                "committed_prefix_digest": self._committed_prefix_digest,
                "committed_prefix_rewritten": False,
            })
            self.receipts.append(
                "P152_PLAN_REVISION.jsonl",
                "HHS_PASS152_PLAN_REVISION_V1",
                revision,
            )
        self._active_plan_digest = new_plan_digest

        projection = self.histories[source_layer].append("CONTROL_PROJECTED_DOWN", {
            "control_vector": vector.to_dict(),
            "target_invariants": list(target.invariant_names),
            "lower_layer_truth_mutated": False,
        })
        application = self.histories[target_layer].append("CONTROL_ADMITTED", {
            "control_vector_id": vector.vector_id,
            "admissible_fields": sorted(target.admissible_control_fields),
            "committed_prefix_digest": self._committed_prefix_digest,
        })
        self.receipts.append(
            "P152_RECURSIVE_CONTROL_TRACE.jsonl",
            "HHS_PASS152_RECURSIVE_CONTROL_TRACE_V1",
            {
                "projection": projection,
                "application": application,
                "canonical_invariant": "EXPLOIT_FREEDOM_RECURSIVELY_PRESERVE_INVARIANTS_ABSOLUTELY_EXTEND_HISTORY_MONOTONICALLY",
            },
        )
        return vector

    def ordered_nodes(self, nodes: Iterable[Any], vector: ControlVector, critical_cost: Any) -> list[Any]:
        return sorted(
            list(nodes),
            key=lambda node: (
                -vector.branch_priority.get(node.node_id, 0),
                -int(_fraction(critical_cost(node.node_id)) * 1000),
                not node.mandatory,
                node.node_id,
            ),
        )

    def rebase_authority_root(
        self,
        new_root: str,
        *,
        equivalence_witness_id: Optional[str] = None,
        invalidated_nodes: Iterable[str] = (),
    ) -> None:
        old_root = self.authority_root
        if new_root == old_root:
            return
        invalidated = sorted(set(invalidated_nodes))
        if equivalence_witness_id is None and not invalidated:
            raise AuthorityViolation("authority-root rebase requires equivalence or explicit invalidation")
        self.authority_root = new_root
        self._active_plan_digest = None
        event = self.histories["L0"].append("AUTHORITY_ROOT_REBASED", {
            "old_root": old_root,
            "new_root": new_root,
            "equivalence_witness_id": equivalence_witness_id,
            "invalidated_nodes": invalidated,
            "committed_state_digest": self.committed_state_digest,
            "committed_history_rewritten": False,
        })
        self.receipts.append(
            "P152_LAYER_HISTORY.jsonl",
            "HHS_PASS152_LAYER_HISTORY_V1",
            event,
        )

    def record_transition(self, event: str, payload: Mapping[str, Any], *, layer_id: str = "L1") -> None:
        entry = self.histories[layer_id].append(event, {
            **copy.deepcopy(dict(payload)),
            "committed_prefix_digest": self._committed_prefix_digest,
        })
        self.receipts.append(
            "P152_LAYER_HISTORY.jsonl",
            "HHS_PASS152_LAYER_HISTORY_V1",
            entry,
        )

    def record_commit_extension(self, before_digest: str, control_digest: str, after_digest: str) -> None:
        if before_digest != self.committed_state_digest:
            raise AuthorityViolation("commit history does not extend the active committed prefix")
        event = {
            "before_digest": before_digest,
            "control_digest": control_digest,
            "after_digest": after_digest,
            "previous_committed_prefix_digest": self._committed_prefix_digest,
        }
        new_prefix = sha256_json(event)
        for layer_id in sorted(self.layers, key=lambda item: self.layers[item].index):
            entry = self.histories[layer_id].append("WITNESSED_STATE_TRANSITION", {
                **event,
                "new_committed_prefix_digest": new_prefix,
            })
            self.receipts.append(
                "P152_LAYER_HISTORY.jsonl",
                "HHS_PASS152_LAYER_HISTORY_V1",
                entry,
            )
        self.committed_state_digest = after_digest
        self._committed_prefix_digest = new_prefix

    def verify(self) -> bool:
        return all(history.verify() for history in self.histories.values())

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": "HHS_PASS152_RECURSIVE_CONTROL_STATE_V1",
            "canonical_invariant": "PRESERVE_CAUSAL_AUTHORITY_AT_INVARIANT_CORE_WHILE_USING_EMERGENT_FREEDOM_TO_OPTIMIZE_SUBORDINATE_EXECUTION",
            "authority_root": self.authority_root,
            "semantic_version": self.semantic_version,
            "policy_version": self.policy_version,
            "committed_state_digest": self.committed_state_digest,
            "committed_prefix_digest": self._committed_prefix_digest,
            "active_plan_digest": self._active_plan_digest,
            "history_valid": self.verify(),
            "history_tips": {layer_id: history.tip for layer_id, history in sorted(self.histories.items())},
            "layers": [
                {
                    "layer_id": layer.layer_id,
                    "index": layer.index,
                    "invariants": list(layer.invariant_names),
                    "admissible_control_fields": sorted(layer.admissible_control_fields),
                }
                for layer in sorted(self.layers.values(), key=lambda value: value.index)
            ],
        }

    @property
    def active_plan_digest(self) -> str:
        return self._active_plan_digest or ("0" * 64)

    @property
    def committed_prefix_digest(self) -> str:
        return self._committed_prefix_digest
