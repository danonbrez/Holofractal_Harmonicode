from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
from typing import Any, Mapping, Sequence

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass163.vmrc import VMRCRuntime

from .backends import CPUReferenceBackend, SimulatedGPUBackend
from .common import (
    JOURNAL_DOMAIN,
    MAX_CLUSTERS,
    OP_DOMAIN,
    P,
    ZERO216,
    GCMSError,
    canonical_bytes,
    hash216,
)
from .geometry import dimensions, rank_one_tensor
from .models import BackendDeclaration, ClusterEdge, ClusterRecord


class RuntimeBaseMixin:
    RUNTIME_VERSION = "HHS-P164-GCMSL-1.0.0"

    def __init__(self, vmrc: VMRCRuntime | None = None) -> None:
        self.vmrc = vmrc or VMRCRuntime()
        self._clusters: dict[str, ClusterRecord] = {}
        self._operations = {}
        self._edges: dict[str, ClusterEdge] = {}
        self._batches = {}
        self._journal: list[dict[str, Any]] = []
        self._last_reduction_root = ZERO216
        self._cpu = CPUReferenceBackend()
        self._gpu = SimulatedGPUBackend()
        self._record("GENESIS", {"state_hash72": self.vmrc.state_hash72})

    def _record(self, event: str, body: Mapping[str, Any]) -> dict[str, Any]:
        previous = self._journal[-1]["journal_hash"] if self._journal else ZERO216
        raw = {"sequence": len(self._journal), "event": event, "previous_hash": previous, **dict(body)}
        sealed = {**raw, "journal_hash": sha256(JOURNAL_DOMAIN + canonical_bytes(raw)).hexdigest()}
        self._journal.append(sealed)
        return sealed

    def _receipt(self, schema: str, body: Mapping[str, Any]) -> dict[str, Any]:
        payload = {"schema": schema, "version": 1, "runtime_epoch": self.vmrc.epoch, **dict(body)}
        state = self.vmrc.status()
        receipt_hash72 = hash72_digest(payload, self.vmrc.snapshot().to_bytes())
        envelope = self.vmrc.base64_envelope(
            payload,
            operation_class="VMRC_RECEIPT",
            source_architecture="GCMSL_REDUCER",
            target_architecture="VM81",
            runtime_epoch=self.vmrc.epoch,
            incoming_hash72=self.vmrc.state_hash72,
            thread_mask="*",
            port_mask="7,8",
            read_set_root=ZERO216,
            write_set_root=ZERO216,
            dependency_root=self._last_reduction_root,
            parameter_root=state["parameter_root"],
            phase_gear_graph_root=state["phase_gear_root"],
            expected_expanded_state_root=self.vmrc.state_hash72,
            receipt_nonce=sha256(f"{schema}:{self.vmrc.epoch}:{len(self._journal)}".encode()).hexdigest(),
        )
        return {
            **payload,
            "state_hash72": self.vmrc.state_hash72,
            "receipt_hash72": receipt_hash72,
            "receipt_sha256": sha256(
                b"HHS-P164-RECEIPT-V1\0" + receipt_hash72.encode() + canonical_bytes(payload)
            ).hexdigest(),
            "pass163_transport_envelope": envelope,
        }

    def status(self) -> dict[str, Any]:
        return {
            "classification": "HHS_PASS_164_UNIVERSAL_81_72_64_SCALING_LAW_IMPLEMENTED",
            "runtime_version": self.RUNTIME_VERSION,
            **dimensions(),
            "rank_one_tensor": rank_one_tensor(),
            "kernel_authorities": 1,
            "permanent_indexes": 1,
            "clusters": len(self._clusters),
            "active_edges": len(self._edges),
            "pending_operations": len(self._operations),
            "state_hash72": self.vmrc.state_hash72,
            "pass163_index_records": len(self.vmrc.index_records()),
            "worker_mutation_authority": False,
            "canonical_commit_authority": "PASS163_VM81_SINGLETON",
        }

    def register_cluster(
        self,
        cluster_id: str,
        *,
        level: int = 1,
        tile_index: int = 0,
        backend: BackendDeclaration | None = None,
        required_participant: bool = True,
    ) -> dict[str, Any]:
        if not cluster_id:
            raise GCMSError("GCMSL_CLUSTER_ID_REQUIRED")
        if cluster_id in self._clusters:
            raise GCMSError("GCMSL_DUPLICATE_CLUSTER")
        if len(self._clusters) >= MAX_CLUSTERS:
            raise GCMSError("GCMSL_CLUSTER_BOUND")
        if not 1 <= level <= 16 or tile_index < 0:
            raise GCMSError("GCMSL_TILE_OR_LEVEL_INVALID")
        record = ClusterRecord(
            cluster_id,
            level,
            tile_index,
            backend or self._cpu.declaration,
            "",
            required_participant,
        )
        self._clusters[cluster_id] = record
        journal = self._record("CLUSTER_REGISTER", {"cluster": asdict(record)})
        return {
            "cluster": asdict(record),
            "receipt": self._receipt(
                "P164_CLUSTER_REGISTER_RECEIPT",
                {
                    "cluster_id": cluster_id,
                    "capability_zero": True,
                    "journal_hash": journal["journal_hash"],
                },
            ),
        }

    def grant_capability(self, cluster_id: str, capability_scope: str) -> dict[str, Any]:
        if not capability_scope:
            raise GCMSError("GCMSL_CAPABILITY_ZERO")
        try:
            prior = self._clusters[cluster_id]
        except KeyError as exc:
            raise GCMSError("GCMSL_CLUSTER_NOT_REGISTERED") from exc
        updated = ClusterRecord(
            prior.cluster_id,
            prior.level,
            prior.tile_index,
            prior.backend,
            capability_scope,
            prior.required_participant,
        )
        self._clusters[cluster_id] = updated
        journal = self._record(
            "CAPABILITY_GRANT",
            {"cluster_id": cluster_id, "capability_scope": capability_scope},
        )
        return {
            "cluster": asdict(updated),
            "receipt": self._receipt(
                "P164_TILE_BIND_RECEIPT",
                {
                    "cluster_id": cluster_id,
                    "capability_scope": capability_scope,
                    "journal_hash": journal["journal_hash"],
                },
            ),
        }

    def register_edge(
        self,
        *,
        level: int,
        source_cluster: str,
        destination_cluster: str,
        domain: str,
        source: str,
        destination: str,
        exact_weight: str,
        polarity: int,
        u72_offset: int = 0,
        xyzw_weights: Sequence[str] = ("1", "1", "1", "1"),
        prior_edge_id: str | None = None,
    ) -> dict[str, Any]:
        if source_cluster not in self._clusters or destination_cluster not in self._clusters:
            raise GCMSError("GCMSL_CLUSTER_NOT_REGISTERED")
        allowed = {
            "AUTHORITY_VM81",
            "RECIPROCAL_PHASE",
            "LOGICAL_THREAD",
            "VM_THREAD_BRIDGE",
            "PARAMETER",
            "CONTINUATION",
            "INTERCONNECT_ROUTE",
        }
        if domain not in allowed or polarity not in (-1, 1) or not 0 <= u72_offset < P:
            raise GCMSError("GCMSL_EDGE_FIELD_INVALID")
        weights = tuple(str(item) for item in xyzw_weights)
        if len(weights) != 4:
            raise GCMSError("GCMSL_EDGE_FIELD_INVALID")
        history: tuple[str, ...] = ()
        if prior_edge_id is not None:
            try:
                prior = self._edges[prior_edge_id]
            except KeyError as exc:
                raise GCMSError("GCMSL_STALE_MEMRISTOR_EDGE") from exc
            history = prior.admitted_history + (prior.edge_id,)
        body = {
            "level": level,
            "source_cluster": source_cluster,
            "destination_cluster": destination_cluster,
            "domain": domain,
            "source": source,
            "destination": destination,
            "epoch": self.vmrc.epoch,
            "exact_weight": str(exact_weight),
            "polarity": polarity,
            "u72_offset": u72_offset,
            "xyzw_weights": weights,
            "admitted_history": history,
        }
        positions, vector = hash216(OP_DOMAIN, body, sequence=len(history))
        edge_id = sha256(OP_DOMAIN + canonical_bytes(body) + bytes.fromhex(vector)).hexdigest()
        edge = ClusterEdge(edge_id=edge_id, hash216_vector=vector, **body)
        self._edges[edge_id] = edge
        journal = self._record("EDGE_REGISTER", {"edge": asdict(edge)})
        return {
            "edge": asdict(edge),
            "positions_hash216": list(positions),
            "receipt": self._receipt(
                "P164_MEMRISTOR_EDGE_RECEIPT",
                {"edge_id": edge_id, "journal_hash": journal["journal_hash"]},
            ),
        }
