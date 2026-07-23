from __future__ import annotations
import copy, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional

from .common import canonical_json, sha256_json
from .graph import TypedDependencyGraph
from .model import (
    AuthorityViolation, CandidateState, ClosureIncomplete, EdgeType,
    EquivalenceWitness, InvalidWitness, OperationNode, Pass152Error,
    ReplayMismatch, ResourceBounded, RootEquivalenceWitness, SkipWitness,
)
from .receipts import ReceiptWriter
from .recursive_control import ControlVector, RecursiveControlInvariant


class ElasticClosureEngine:
    """Deterministic logical scheduler with opportunistic physical concurrency.

    Candidate values are maintained independently from the immutable authoritative
    snapshot. Only `commit()` can replace authoritative state, and only after a
    VM81 admission callback returns an admitted transition receipt.
    """

    def __init__(
        self,
        authoritative_state: dict[str, Any],
        authority_root: str,
        receipt_root: str | Path,
        *,
        semantic_version: str = "1.0.0",
        policy_version: str = "P152-SCHEDULER-V1",
        workers: int = 4,
        max_nodes: int = 4096,
        max_horizon: int = 8,
        max_scheduler_iterations: int = 10000,
        scheduler_latency_bound_ns: int = 50_000_000,
    ) -> None:
        if workers < 1 or max_nodes < 1 or max_horizon < 1:
            raise ValueError("invalid resource policy")
        self.authoritative_state = copy.deepcopy(authoritative_state)
        self._authoritative_digest = sha256_json(self.authoritative_state)
        self.authority_root = authority_root
        self.semantic_version = semantic_version
        self.policy_version = policy_version
        self.workers = workers
        self.max_nodes = max_nodes
        self.max_horizon = max_horizon
        self.max_scheduler_iterations = max_scheduler_iterations
        self.scheduler_latency_bound_ns = scheduler_latency_bound_ns
        self.graph = TypedDependencyGraph()
        self.receipts = ReceiptWriter(receipt_root)
        self.recursive_control = RecursiveControlInvariant(
            authority_root=authority_root,
            semantic_version=semantic_version,
            committed_state_digest=self._authoritative_digest,
            policy_version=policy_version,
            workers=workers,
            max_horizon=max_horizon,
            receipt_writer=self.receipts,
        )
        self._active_control_vector: Optional[ControlVector] = None
        self.equivalence_witnesses: dict[str, EquivalenceWitness] = {}
        self.skip_witnesses: dict[str, SkipWitness] = {}
        self.root_equivalence_witnesses: dict[tuple[str, str], RootEquivalenceWitness] = {}
        self.resolved: set[str] = set()
        self.logical_order: list[str] = []
        self.commit_receipt: Optional[dict[str, Any]] = None
        self.cycle_open_ns = time.perf_counter_ns()
        self.cycle_closed_ns: Optional[int] = None
        self._state_lock = threading.RLock()
        self._active_workers = 0
        self._max_active_workers = 0
        self._productive_ns_accumulator = 0
        self._scheduler_ns = 0
        self._critical_ns = 0
        self._recompute_ns = 0
        self._saved_reuse_ns = 0
        self._saved_skip_ns = 0
        self._candidate_outputs_computed = 0
        self._candidate_outputs_used = 0
        self._invalidated_before = set()
        self.closure_flags = {
            "value": False,
            "constraint": True,
            "phase": True,
            "provenance": True,
            "authority": True,
            "receipt": True,
            "resource": True,
        }
        self.counters = {k: 0 for k in (
            "propagated", "partial", "verified", "reused", "skipped",
            "invalidated", "recomputed", "blocked", "critical", "committed"
        )}
        self.receipts.write_json("P152_CYCLE_OPEN.json", "HHS_PASS152_CYCLE_OPEN_V1", {
            "authority_root": authority_root,
            "authoritative_state_digest": self._authoritative_digest,
            "semantic_version": semantic_version,
            "policy_version": policy_version,
            "workers": workers,
            "max_nodes": max_nodes,
            "max_horizon": max_horizon,
            "invariant": "DELAY_AUTHORITY_NOT_COMPUTATION",
            "recursive_control_invariant": "PRESERVE_CAUSAL_AUTHORITY_AT_INVARIANT_CORE_WHILE_USING_EMERGENT_FREEDOM_TO_OPTIMIZE_SUBORDINATE_EXECUTION",
        })
        self.receipts.append("P152_RESOURCE_ALLOCATION.jsonl", "HHS_PASS152_RESOURCE_ALLOCATION_V1", {
            "workers": workers, "max_nodes": max_nodes, "max_horizon": max_horizon,
            "max_scheduler_iterations": max_scheduler_iterations,
        })

    def assert_authoritative_immutable(self) -> None:
        if sha256_json(self.authoritative_state) != self._authoritative_digest:
            raise AuthorityViolation("authoritative state mutated during predictive propagation")

    def add_node(self, node: OperationNode) -> None:
        self.assert_authoritative_immutable()
        if len(self.graph.nodes) >= self.max_nodes:
            self.closure_flags["resource"] = False
            raise ResourceBounded("node resource bound reached")
        if node.horizon > self.max_horizon:
            raise ResourceBounded("candidate horizon exceeds bound")
        if not node.candidate_root:
            node.candidate_root = self.authority_root
        if node.candidate_root != self.authority_root:
            raise AuthorityViolation("new candidate uses a foreign authority root")
        self.graph.add_node(node)
        if not node.dependencies:
            node.lifecycle = CandidateState.READY
        else:
            node.lifecycle = CandidateState.BLOCKED
            self.counters["blocked"] += 1
        self._state_event(node, "NODE_ADDED")

    def add_edge(self, source: str, target: str, edge_type: EdgeType) -> None:
        self.graph.add_edge(source, target, edge_type)
        target_node = self.graph.nodes[target]
        target_node.lifecycle = CandidateState.BLOCKED
        self._state_event(target_node, "DEPENDENCY_ADDED")

    def seed(self, node_id: str, value: Any, *, provenance: Optional[dict[str, Any]] = None) -> None:
        node = self.graph.nodes[node_id]
        if node.dependencies:
            raise Pass152Error("only source nodes may be seeded")
        node.value = copy.deepcopy(value)
        node.lifecycle = CandidateState.VERIFIED
        node.verification_digest = sha256_json({"node_id": node_id, "value": value, "root": node.candidate_root})
        node.provenance.append(provenance or {"kind": "SEED", "source": node_id, "authority_root": self.authority_root})
        self.resolved.add(node_id)
        self.counters["verified"] += 1
        self.logical_order.append(node_id)
        self._candidate_outputs_computed += 1
        self._state_event(node, "SEEDED_VERIFIED")
        self._reconsider_dependents(node_id)

    def register_equivalence_witness(self, witness: EquivalenceWitness) -> None:
        if witness.authority_root != self.authority_root or witness.semantic_version != self.semantic_version:
            raise InvalidWitness("equivalence witness root or semantic version mismatch")
        if witness.source_node == witness.target_node:
            raise InvalidWitness("equivalence witness must preserve distinct expression identities")
        self.equivalence_witnesses[witness.target_node] = witness

    def register_skip_witness(self, witness: SkipWitness) -> None:
        if witness.authority_root != self.authority_root or witness.semantic_version != self.semantic_version:
            raise InvalidWitness("skip witness root or semantic version mismatch")
        self.skip_witnesses[witness.node_id] = witness

    def register_root_equivalence(self, witness: RootEquivalenceWitness) -> None:
        if witness.semantic_version != self.semantic_version:
            raise InvalidWitness("root equivalence semantic version mismatch")
        self.root_equivalence_witnesses[(witness.old_root, witness.new_root)] = witness

    def _state_event(self, node: OperationNode, event: str) -> None:
        self.receipts.append("P152_CANDIDATE_FIELD_STATE.jsonl", "HHS_PASS152_CANDIDATE_FIELD_STATE_V1", {
            "event": event,
            "node_id": node.node_id,
            "operation_id": node.operation_id,
            "lifecycle": node.lifecycle.value,
            "candidate_root": node.candidate_root,
            "semantic_version": node.semantic_version,
            "phase_id": node.phase_id,
            "lane_id": node.lane_id,
            "dependencies": sorted(node.dependencies),
            "resolved_dependencies": sorted(node.dependencies & self.resolved),
            "verification_digest": node.verification_digest,
        })

    def _reconsider_dependents(self, node_id: str) -> None:
        resolved_at = time.perf_counter_ns()
        for dependent_id in self.graph.dependents(node_id):
            node = self.graph.nodes[dependent_id]
            if node.lifecycle in {CandidateState.INVALIDATED, CandidateState.CONFLICT, CandidateState.COMMITTED}:
                continue
            node.partial_inputs[node_id] = copy.deepcopy(self.graph.nodes[node_id].value)
            if node.ready_final(self.resolved):
                node.lifecycle = CandidateState.READY
                event = "READY_FINAL"
            elif node.ready_partial(self.resolved):
                node.lifecycle = CandidateState.PARTIAL
                self.counters["partial"] += 1
                event = "READY_PARTIAL"
            else:
                event = "BLOCKED"
            queued_at = time.perf_counter_ns()
            latency = queued_at - resolved_at
            if latency > self.scheduler_latency_bound_ns:
                self.closure_flags["resource"] = False
                raise ResourceBounded("early propagation scheduler latency bound exceeded")
            self.counters["propagated"] += 1
            self.receipts.append("P152_PROPAGATION_TRACE.jsonl", "HHS_PASS152_PROPAGATION_TRACE_V1", {
                "source": node_id,
                "target": dependent_id,
                "event": event,
                "scheduler_latency_ns": latency,
                "partial_ready": node.ready_partial(self.resolved),
                "final_ready": node.ready_final(self.resolved),
            })
            self._state_event(node, event)

    def _validate_equivalence(self, witness: EquivalenceWitness, target: OperationNode) -> OperationNode:
        source = self.graph.nodes.get(witness.source_node)
        if source is None or source.lifecycle != CandidateState.VERIFIED:
            raise InvalidWitness("equivalence source is not verified")
        if witness.target_node != target.node_id:
            raise InvalidWitness("equivalence target mismatch")
        if source.candidate_root != target.candidate_root or witness.authority_root != target.candidate_root:
            raise InvalidWitness("cross-root equivalence reuse rejected")
        if witness.semantic_version != target.semantic_version:
            raise InvalidWitness("semantic-version mismatch")
        operand_digest = sha256_json({d: self.graph.nodes[d].value for d in sorted(target.dependencies)})
        if operand_digest != witness.operand_digest:
            raise InvalidWitness("operand digest mismatch")
        return source

    def _apply_reuse(self, target: OperationNode, witness: EquivalenceWitness) -> None:
        source = self._validate_equivalence(witness, target)
        target.value = copy.deepcopy(source.value)
        target.lifecycle = CandidateState.VERIFIED
        target.verification_digest = sha256_json({
            "target": target.node_id, "value": target.value, "witness": asdict(witness),
            "ordered_provenance": [source.node_id, target.node_id],
        })
        target.provenance = copy.deepcopy(source.provenance) + [{
            "kind": "EQUIVALENCE_REUSE", "source_node": source.node_id,
            "target_node": target.node_id, "witness_id": witness.witness_id,
            "source_lane": witness.source_lane, "target_lane": witness.target_lane,
            "value_equal": True, "provenance_collapsed": False,
        }]
        self.resolved.add(target.node_id)
        self.logical_order.append(target.node_id)
        self.counters["reused"] += 1; self.counters["verified"] += 1
        self._candidate_outputs_computed += 1
        self._saved_reuse_ns += int(float(target.estimated_cost) * 1_000_000)
        self.receipts.append("P152_EQUIVALENCE_REUSE.jsonl", "HHS_PASS152_EQUIVALENCE_REUSE_V1", {
            "witness": asdict(witness), "result_digest": target.verification_digest,
            "ordered_provenance_preserved": True,
        })
        self._state_event(target, "VERIFIED_BY_EQUIVALENCE_REUSE")
        self._reconsider_dependents(target.node_id)

    def _apply_skip(self, target: OperationNode, witness: SkipWitness) -> None:
        if witness.node_id != target.node_id or witness.authority_root != target.candidate_root:
            raise InvalidWitness("skip witness target/root mismatch")
        if witness.input_node not in target.dependencies:
            raise InvalidWitness("skip witness input not a dependency")
        source = self.graph.nodes[witness.input_node]
        expected_hash = sha256_json({
            "operation_id": witness.operation_id,
            "input_value": source.value,
            "constraint_root": witness.constraint_root,
            "proof_id": witness.proof_id,
        })
        if expected_hash != witness.canonical_hash:
            raise InvalidWitness("skip witness canonical hash mismatch")
        target.value = copy.deepcopy(source.value)
        target.lifecycle = CandidateState.VERIFIED
        target.verification_digest = sha256_json({"target": target.node_id, "value": target.value, "witness": asdict(witness)})
        target.provenance = copy.deepcopy(source.provenance) + [{"kind": "INVARIANT_SKIP", "witness_id": witness.witness_id}]
        self.resolved.add(target.node_id); self.logical_order.append(target.node_id)
        self.counters["skipped"] += 1; self.counters["verified"] += 1
        self._candidate_outputs_computed += 1
        self._saved_skip_ns += int(float(target.estimated_cost) * 1_000_000)
        self.receipts.append("P152_INVARIANT_SKIP.jsonl", "HHS_PASS152_INVARIANT_SKIP_V1", {
            "witness": asdict(witness), "result_digest": target.verification_digest,
        })
        self._state_event(target, "VERIFIED_BY_INVARIANT_SKIP")
        self._reconsider_dependents(target.node_id)

    def _evaluate_one(self, node: OperationNode) -> tuple[str, Any, int]:
        if node.compute is None:
            raise Pass152Error(f"node {node.node_id} has no compute function")
        with self._state_lock:
            self._active_workers += 1
            self._max_active_workers = max(self._max_active_workers, self._active_workers)
        start = time.perf_counter_ns()
        try:
            values = {d: copy.deepcopy(self.graph.nodes[d].value) for d in sorted(node.dependencies)}
            result = node.compute(values)
            return node.node_id, result, time.perf_counter_ns() - start
        finally:
            with self._state_lock:
                self._active_workers -= 1

    def _ready_nodes(self) -> list[OperationNode]:
        ready: list[OperationNode] = []
        for node in self.graph.nodes.values():
            if node.lifecycle != CandidateState.READY:
                continue
            if not node.ready_final(self.resolved):
                continue
            ready.append(node)
        if not ready:
            self._active_control_vector = None
            return []

        observations = [
            {
                "node_id": node.node_id,
                "critical_cost": str(Fraction(str(self.graph.critical_cost(node.node_id)))),
                "predicted_risk": str(node.predicted_risk),
                "redundancy_cost": str(node.redundancy_cost),
                "mandatory": node.mandatory,
                "layer_id": node.layer_id,
            }
            for node in ready
        ]
        vector = self.recursive_control.optimize(
            source_layer="L2",
            target_layer="L1",
            ready_nodes=observations,
            context={
                "authority_root": self.authority_root,
                "semantic_version": self.semantic_version,
                "authoritative_state_digest": self._authoritative_digest,
            },
        )
        self._active_control_vector = vector
        critical = self.recursive_control.ordered_nodes(ready, vector, self.graph.critical_cost)
        max_cost = max(self.graph.critical_cost(node.node_id) for node in critical)
        current = [
            node.node_id for node in critical
            if abs(self.graph.critical_cost(node.node_id) - max_cost) < 1e-12
        ]
        self.counters["critical"] += len(current)
        self.receipts.append("P152_CRITICAL_PATH_FORECAST.jsonl", "HHS_PASS152_CRITICAL_PATH_FORECAST_V1", {
            "predicted_closure_cost": max_cost,
            "critical_set": current,
            "prediction_authority": "ADVISORY_PRIORITY_ONLY",
            "control_vector_id": vector.vector_id,
            "higher_layer_optimizes_policy_not_truth": True,
        })
        return critical

    def run_until_closed(self) -> dict[str, Any]:
        self.assert_authoritative_immutable()
        iterations = 0
        while True:
            iterations += 1
            if iterations > self.max_scheduler_iterations:
                self.closure_flags["resource"] = False
                raise ResourceBounded("scheduler iteration bound exceeded")
            sched_start = time.perf_counter_ns()
            ready = self._ready_nodes()
            self._scheduler_ns += time.perf_counter_ns() - sched_start
            if not ready:
                mandatory_unresolved = [
                    n for n in self.graph.nodes.values()
                    if n.mandatory and n.lifecycle not in {CandidateState.VERIFIED, CandidateState.COMMITTED}
                ]
                if mandatory_unresolved:
                    self.closure_flags["value"] = False
                    raise ClosureIncomplete("mandatory nodes remain unresolved: " + ",".join(sorted(n.node_id for n in mandatory_unresolved)))
                break

            vector = self._active_control_vector
            batch_limit = vector.max_batch if vector is not None else self.workers
            selected_ready = ready[:batch_limit]
            executable: list[OperationNode] = []
            for node in selected_ready:
                if vector is not None and node.horizon > vector.speculative_depth:
                    continue
                if vector is not None and vector.reuse_enabled and node.node_id in self.equivalence_witnesses:
                    witness = self.equivalence_witnesses[node.node_id]
                    source = self.graph.nodes.get(witness.source_node)
                    if source is None or source.lifecycle != CandidateState.VERIFIED:
                        # The target remains lawful and ready, but reuse cannot occur
                        # until its witnessed source has been verified.
                        continue
                    self._apply_reuse(node, witness); continue
                if vector is not None and vector.skip_enabled and node.node_id in self.skip_witnesses:
                    self._apply_skip(node, self.skip_witnesses[node.node_id]); continue
                node.lifecycle = CandidateState.EVALUATING
                node.evaluation_count += 1
                self._state_event(node, "EVALUATING")
                executable.append(node)

            if executable:
                work_order = [n.node_id for n in executable]
                self.receipts.append("P152_SCHEDULER_DECISIONS.jsonl", "HHS_PASS152_SCHEDULER_DECISION_V1", {
                    "logical_work_order": work_order,
                    "tie_breaker": "RECURSIVE_CONTROL_PRIORITY_THEN_CRITICAL_COST_THEN_MANDATORY_THEN_NODE_ID",
                    "worker_count": self.workers,
                    "control_vector": vector.to_dict() if vector is not None else None,
                    "semantic_authority_changed": False,
                })
                self.recursive_control.record_transition("SUBORDINATE_BATCH_SCHEDULED", {
                    "logical_work_order": work_order,
                    "control_vector_id": vector.vector_id if vector is not None else None,
                    "authority_root": self.authority_root,
                })
                results: dict[str, tuple[Any, int]] = {}
                batch_start = time.perf_counter_ns()
                with ThreadPoolExecutor(max_workers=self.workers, thread_name_prefix="hhs152") as pool:
                    futures = {pool.submit(self._evaluate_one, n): n.node_id for n in executable}
                    for fut in as_completed(futures):
                        node_id, value, duration = fut.result()
                        results[node_id] = (value, duration)
                batch_duration = time.perf_counter_ns() - batch_start
                self._productive_ns_accumulator += sum(duration for _, duration in results.values())
                self._critical_ns += batch_duration
                # Commit logical results in deterministic work order, not completion order.
                for node in executable:
                    value, duration = results[node.node_id]
                    node.value = value
                    node.lifecycle = CandidateState.PROVISIONAL
                    self._state_event(node, "PROVISIONAL")
                    node.verification_digest = sha256_json({
                        "node_id": node.node_id,
                        "operation_id": node.operation_id,
                        "value": value,
                        "candidate_root": node.candidate_root,
                        "semantic_version": node.semantic_version,
                        "phase_id": node.phase_id,
                        "lane_id": node.lane_id,
                        "dependency_values": {d: self.graph.nodes[d].value for d in sorted(node.dependencies)},
                    })
                    node.provenance.append({
                        "kind": "COMPUTED", "operation_id": node.operation_id,
                        "dependencies": sorted(node.dependencies),
                        "candidate_root": node.candidate_root,
                    })
                    node.lifecycle = CandidateState.VERIFIED
                    self.resolved.add(node.node_id); self.logical_order.append(node.node_id)
                    self.counters["verified"] += 1
                    self._candidate_outputs_computed += 1
                    self._state_event(node, "VERIFIED")
                    self._reconsider_dependents(node.node_id)

            self.assert_authoritative_immutable()
            if all(
                (not n.mandatory) or n.lifecycle == CandidateState.VERIFIED
                for n in self.graph.nodes.values()
            ):
                break

        self.closure_flags["value"] = all(
            (not n.mandatory) or n.lifecycle == CandidateState.VERIFIED
            for n in self.graph.nodes.values()
        )
        proof = self.closure_proof()
        return proof

    def invalidate_for_root_change(self, new_root: str) -> list[str]:
        if new_root == self.authority_root:
            return []
        equivalent = (self.authority_root, new_root) in self.root_equivalence_witnesses
        if equivalent:
            witness = self.root_equivalence_witnesses[(self.authority_root, new_root)]
            self.recursive_control.rebase_authority_root(
                new_root,
                equivalence_witness_id=witness.witness_id,
            )
            self.authority_root = new_root
            for n in self.graph.nodes.values():
                n.candidate_root = new_root
            return []
        invalidated = []
        for node in sorted(self.graph.nodes.values(), key=lambda x: x.node_id):
            if node.lifecycle in {
                CandidateState.PARTIAL, CandidateState.READY, CandidateState.EVALUATING,
                CandidateState.PROVISIONAL, CandidateState.VERIFIED,
            }:
                node.lifecycle = CandidateState.INVALIDATED
                invalidated.append(node.node_id)
                self.resolved.discard(node.node_id)
                self.counters["invalidated"] += 1
                self.receipts.append("P152_INVALIDATION_TRACE.jsonl", "HHS_PASS152_INVALIDATION_TRACE_V1", {
                    "node_id": node.node_id, "old_root": self.authority_root,
                    "new_root": new_root, "equivalence_witness": None,
                })
                self._state_event(node, "INVALIDATED_STALE_ROOT")
        self.recursive_control.rebase_authority_root(
            new_root,
            invalidated_nodes=invalidated,
        )
        self.authority_root = new_root
        self._invalidated_before.update(invalidated)
        self.closure_flags["value"] = False
        return invalidated

    def closure_proof(self) -> dict[str, Any]:
        mandatory = [n for n in self.graph.nodes.values() if n.mandatory]
        self.closure_flags["value"] = all(n.lifecycle == CandidateState.VERIFIED for n in mandatory)
        self.closure_flags["provenance"] = all(bool(n.provenance) for n in mandatory)
        recursive_control_state = self.recursive_control.snapshot()
        self.closure_flags["authority"] = (
            sha256_json(self.authoritative_state) == self._authoritative_digest
            and all(n.candidate_root == self.authority_root for n in mandatory)
            and recursive_control_state["history_valid"]
            and recursive_control_state["authority_root"] == self.authority_root
            and recursive_control_state["semantic_version"] == self.semantic_version
            and recursive_control_state["committed_state_digest"] == self._authoritative_digest
        )
        self.closure_flags["receipt"] = (
            all(bool(n.verification_digest) for n in mandatory)
            and all(tip != "0" * 64 for tip in recursive_control_state["history_tips"].values())
        )
        omega = all(self.closure_flags.values())
        proof = {
            "schema": "HHS_PASS152_GLOBAL_CLOSURE_PROOF_V1",
            "omega_closure": omega,
            "flags": dict(self.closure_flags),
            "authority_root": self.authority_root,
            "authoritative_state_digest": self._authoritative_digest,
            "candidate_state_digest": self.candidate_digest(),
            "mandatory_nodes": sorted(n.node_id for n in mandatory),
            "verified_nodes": sorted(n.node_id for n in mandatory if n.lifecycle == CandidateState.VERIFIED),
            "logical_work_order": list(self.logical_order),
            "predictive_receipt_chain_tip": self.receipts.chain_tip,
            "recursive_control": recursive_control_state,
            "causal_continuity": recursive_control_state["history_valid"],
            "higher_layers_optimize_policy_not_truth": True,
        }
        self.receipts.write_json("P152_GLOBAL_CLOSURE_PROOF.json", proof["schema"], proof)
        return proof

    def candidate_state(self) -> dict[str, Any]:
        return {
            "authority_root": self.authority_root,
            "semantic_version": self.semantic_version,
            "values": {n: copy.deepcopy(self.graph.nodes[n].value) for n in sorted(self.graph.nodes) if self.graph.nodes[n].lifecycle in {CandidateState.VERIFIED, CandidateState.COMMITTED}},
            "provenance": {n: copy.deepcopy(self.graph.nodes[n].provenance) for n in sorted(self.graph.nodes) if self.graph.nodes[n].lifecycle in {CandidateState.VERIFIED, CandidateState.COMMITTED}},
            "logical_work_order": list(self.logical_order),
            "control_plan_digest": self.recursive_control.active_plan_digest,
        }

    def candidate_digest(self) -> str:
        return sha256_json(self.candidate_state())

    def commit(self, vm81_admit: Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
        proof = self.closure_proof()
        if not proof["omega_closure"]:
            raise ClosureIncomplete("global closure predicate is false")
        if self.commit_receipt is not None:
            raise AuthorityViolation("cycle already committed")
        before = copy.deepcopy(self.authoritative_state)
        candidate = self.candidate_state()
        admission = vm81_admit(copy.deepcopy(candidate), copy.deepcopy(proof))
        if not admission.get("admitted"):
            raise AuthorityViolation("VM81 admission rejected")
        if not admission.get("hash72_receipt"):
            raise AuthorityViolation("VM81 admission omitted Hash72 receipt")
        committed_state = admission.get("authoritative_state")
        if not isinstance(committed_state, dict):
            raise AuthorityViolation("VM81 admission omitted authoritative state")
        self.authoritative_state = copy.deepcopy(committed_state)
        after_digest = sha256_json(self.authoritative_state)
        self.recursive_control.record_commit_extension(
            sha256_json(before),
            self.recursive_control.active_plan_digest,
            after_digest,
        )
        self._authoritative_digest = after_digest
        for node in self.graph.nodes.values():
            if node.mandatory and node.lifecycle == CandidateState.VERIFIED:
                node.lifecycle = CandidateState.COMMITTED
                node.result_used = True
                self._candidate_outputs_used += 1
        self.counters["committed"] += 1
        self.cycle_closed_ns = time.perf_counter_ns()
        self.commit_receipt = {
            "schema": "HHS_PASS152_COMMIT_RECEIPT_V1",
            "before_authoritative_digest": sha256_json(before),
            "candidate_digest": sha256_json(candidate),
            "after_authoritative_digest": self._authoritative_digest,
            "closure_proof_digest": sha256_json(proof),
            "vm81_admitted": True,
            "hash72_receipt": admission["hash72_receipt"],
            "authority_audit": admission.get("authority_audit"),
            "predictive_receipt_chain_tip": self.receipts.chain_tip,
            "recursive_control_plan_digest": self.recursive_control.active_plan_digest,
            "causal_history_prefix_digest": self.recursive_control.committed_prefix_digest,
            "history_extended_not_rewritten": True,
        }
        self.receipts.write_json("P152_COMMIT_RECEIPT.json", self.commit_receipt["schema"], self.commit_receipt, authoritative=True)
        return copy.deepcopy(self.commit_receipt)

    def metrics(self) -> dict[str, Any]:
        now = self.cycle_closed_ns or time.perf_counter_ns()
        closure_ns = max(1, now - self.cycle_open_ns)
        productive_wall_equivalent = min(closure_ns * self.workers, self._productive_ns_accumulator)
        idle_ns = max(0, closure_ns * self.workers - productive_wall_equivalent)
        return {
            "schema": "HHS_PASS152_RUNTIME_METRICS_V1",
            **{f"N_{k}": v for k, v in self.counters.items()},
            "T_closure_ns": closure_ns,
            "T_idle_ns": idle_ns,
            "T_productive_ns": productive_wall_equivalent,
            "T_critical_ns": self._critical_ns,
            "T_recomputation_ns": self._recompute_ns,
            "T_saved_reuse_ns": self._saved_reuse_ns,
            "T_saved_skip_ns": self._saved_skip_ns,
            "T_scheduler_ns": self._scheduler_ns,
            "workers": self.workers,
            "max_concurrent_workers_observed": self._max_active_workers,
            "eta_closure": productive_wall_equivalent / (closure_ns * self.workers),
            "eta_candidate": (self._candidate_outputs_used / self._candidate_outputs_computed) if self._candidate_outputs_computed else 0.0,
            "candidate_outputs_computed": self._candidate_outputs_computed,
            "candidate_outputs_eventually_used": self._candidate_outputs_used,
        }

    def replay_receipt(self) -> dict[str, Any]:
        if not self.commit_receipt:
            raise ClosureIncomplete("cannot replay before commit")
        candidate = self.candidate_state()
        observed = sha256_json(candidate)
        expected = self.commit_receipt["candidate_digest"]
        # Committed nodes retain values/provenance; lifecycle is excluded from candidate_state.
        status = "MATCH" if observed == expected else "MISMATCH"
        receipt = {
            "schema": "HHS_PASS152_REPLAY_RECEIPT_V1",
            "expected_candidate_digest": expected,
            "observed_candidate_digest": observed,
            "logical_work_order": list(self.logical_order),
            "replay_status": status,
            "hash72_receipt": self.commit_receipt["hash72_receipt"],
            "recursive_control_plan_digest": self.recursive_control.active_plan_digest,
            "causal_history_valid": self.recursive_control.verify(),
            "history_extended_not_rewritten": True,
        }
        self.receipts.write_json("P152_REPLAY_RECEIPT.json", receipt["schema"], receipt)
        if status != "MATCH":
            raise ReplayMismatch("candidate replay digest mismatch")
        return receipt
