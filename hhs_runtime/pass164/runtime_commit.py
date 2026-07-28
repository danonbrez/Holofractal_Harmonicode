from __future__ import annotations

from hashlib import sha256
import json
from time import perf_counter_ns
from typing import Any

from .common import JOURNAL_DOMAIN, ZERO216, GCMSError, canonical_bytes
from .geometry import ScaleGeometry, coordinate_bijection_proof


class RuntimeCommitMixin:
    def commit(self, batch_id: str) -> dict[str, Any]:
        try:
            reduction = self._batches.pop(batch_id)
        except KeyError as exc:
            raise GCMSError("GCMSL_REDUCTION_NOT_FOUND") from exc
        if reduction.incoming_hash72 != self.vmrc.state_hash72 or not reduction.invariant.closed:
            raise GCMSError("GCMSL_STALE_OR_OPEN_REDUCTION")
        grouped: dict[int, dict[int, int]] = {}
        for item in reduction.operations:
            grouped.setdefault(item.thread, {})[item.vm81_position] = item.trit
        pass163_receipts = []
        for thread in sorted(grouped):
            candidate = self.vmrc.submit_candidate(
                thread=thread,
                writes=grouped[thread],
                operation="VMRC_CANDIDATE_SUBMIT",
                expected_input_hash72=self.vmrc.state_hash72,
                dependency_root=reduction.reduction_hash216,
                capability_scope="GCMSL_SINGLETON_COMMIT",
                source_architecture="GCMSL_REDUCER",
                target_architecture="VM81",
            )
            pass163_receipts.append(self.vmrc.execute(candidate)["commit"]["receipt"])
        outgoing = self.vmrc.state_hash72
        self._last_reduction_root = reduction.reduction_hash216
        for item in reduction.operations:
            self._operations.pop(item.operation_id, None)
        journal = self._record(
            "COMMIT",
            {
                "batch_id": batch_id,
                "incoming_hash72": reduction.incoming_hash72,
                "outgoing_hash72": outgoing,
                "reduction_hash216": reduction.reduction_hash216,
                "stable_order": reduction.stable_order,
                "pass163_receipt_hash72": [item["receipt_hash72"] for item in pass163_receipts],
            },
        )
        return {
            "classification": "HHS_PASS_164_CLUSTER_COMMIT_ADMITTED",
            "receipt": self._receipt(
                "P164_COMMIT_RECEIPT",
                {
                    "batch_id": batch_id,
                    "incoming_hash72": reduction.incoming_hash72,
                    "outgoing_hash72": outgoing,
                    "reduction_hash216": reduction.reduction_hash216,
                    "stable_order": list(reduction.stable_order),
                    "pass163_receipt_hash72": [item["receipt_hash72"] for item in pass163_receipts],
                    "journal_hash": journal["journal_hash"],
                    "kernel_authorities": 1,
                    "permanent_indexes": 1,
                },
            ),
            "pass163_receipts": pass163_receipts,
        }

    def transport_envelope(self, payload: Any, *, cluster_id: str) -> str:
        try:
            cluster = self._clusters[cluster_id]
        except KeyError as exc:
            raise GCMSError("GCMSL_CLUSTER_NOT_REGISTERED") from exc
        if cluster.capability_zero:
            raise GCMSError("GCMSL_CAPABILITY_ZERO")
        status = self.vmrc.status()
        return self.vmrc.base64_envelope(
            payload,
            operation_class="VMRC_BASE64_ENCODE",
            source_architecture=cluster.backend.architecture,
            target_architecture="VM81",
            runtime_epoch=self.vmrc.epoch,
            incoming_hash72=self.vmrc.state_hash72,
            thread_mask="*",
            port_mask="*",
            read_set_root=ZERO216,
            write_set_root=ZERO216,
            dependency_root=ZERO216,
            parameter_root=status["parameter_root"],
            phase_gear_graph_root=status["phase_gear_root"],
            expected_expanded_state_root=self.vmrc.state_hash72,
            receipt_nonce=sha256(f"{cluster_id}:{self.vmrc.epoch}".encode()).hexdigest(),
        )

    def replay(self) -> dict[str, Any]:
        previous = ZERO216
        commits = 0
        for sequence, raw in enumerate(self._journal):
            record = dict(raw)
            supplied = record.pop("journal_hash")
            if record.get("sequence") != sequence or record.get("previous_hash") != previous:
                raise GCMSError("GCMSL_INCOMPLETE_DURABLE_JOURNAL")
            if supplied != sha256(JOURNAL_DOMAIN + canonical_bytes(record)).hexdigest():
                raise GCMSError("GCMSL_REPLAY_MISMATCH")
            commits += int(record["event"] == "COMMIT")
            previous = supplied
        pass163 = self.vmrc.replay()
        return {
            "classification": "P164_REPLAY_RECEIPT",
            "records": len(self._journal),
            "commits": commits,
            "journal_head": previous,
            "state_hash72": self.vmrc.state_hash72,
            "pass163_replay": pass163,
            "deterministic_replay": bool(pass163.get("deterministic_replay")),
        }

    def benchmark(self, *, scale: int = 1, active_edges: int | None = None) -> dict[str, Any]:
        geometry = ScaleGeometry(scale=scale, recursive_level=2)
        start = perf_counter_ns()
        proof = coordinate_bijection_proof()
        mapping_ns = perf_counter_ns() - start
        edge_count = len(self._edges) if active_edges is None else int(active_edges)
        if edge_count < 0:
            raise GCMSError("GCMSL_EDGE_COUNT_INVALID")
        start = perf_counter_ns()
        encoded = self.vmrc.snapshot().base64()
        base64_ns = perf_counter_ns() - start
        start = perf_counter_ns()
        replay = self.replay()
        replay_ns = perf_counter_ns() - start
        report = {
            "schema": "P164_BENCHMARK_RECEIPT",
            "scale": scale,
            "homogeneous_geometry": geometry.homogeneous,
            "recursive_geometry": geometry.recursive,
            "coordinate_mapping_ns": mapping_ns,
            "base64_compilation_ns": base64_ns,
            "replay_ns": replay_ns,
            "snapshot_base64_symbols": len(encoded),
            "dense_address_capacity": geometry.homogeneous["dense_capacity"],
            "active_edge_count": edge_count,
            "resident_edge_records": len(self._edges),
            "sparse_address_compression_factor": geometry.homogeneous["dense_capacity"] / max(1, edge_count),
            "theoretical_capacity_distinct_from_residency": True,
            "coordinate_proof_sha256": proof["proof_sha256"],
            "state_hash72": self.vmrc.state_hash72,
            "deterministic_replay": replay["deterministic_replay"],
            "physical_single_cycle_claimed": False,
        }
        report["benchmark_sha256"] = sha256(canonical_bytes(report)).hexdigest()
        return report

    def journal(self) -> tuple[dict[str, Any], ...]:
        return tuple(json.loads(canonical_bytes(item)) for item in self._journal)
