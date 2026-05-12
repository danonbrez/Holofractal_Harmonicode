# hhs_python/runtime/hhs_recursive_consensus_constellation.py
#
# HHS / HARMONICODE
# Recursive Consensus Constellation
#
# Canonical Runtime OS Convergence Substrate
#
# Runtime Principle:
#
#   consensus
#   =
#   recursive stabilization
#   toward globally reconstructible manifold attractors
#
# NOT:
#
#   replicated agreement
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# Runtime Primitive:
#
#   recursive attractor-topology stabilization
#

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
import hashlib
import json
import time


HASH216_WIDTH = 216


def _hash216(data: str) -> str:
    h1 = hashlib.sha512(data.encode()).hexdigest()
    h2 = hashlib.sha256(data.encode()).hexdigest()
    return (h1 + h2)[:HASH216_WIDTH]


@dataclass(frozen=True)
class HHSConsensusWitness:
    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    convergent: bool = True
    reconstructible: bool = True
    globally_canonical: bool = True
    phase_equivalent: bool = True
    temporally_equivalent: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        return (
            self.convergent
            and self.reconstructible
            and self.globally_canonical
            and self.phase_equivalent
            and self.temporally_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


@dataclass(frozen=True)
class HHSConsensusAttractor:
    """
    Canonical recursive convergence carrier.
    """

    attractor_id: str

    source_branch_hash216: str
    canonical_branch_hash216: str

    projection_hash216: str
    execution_hash216: str
    transport_hash216: str
    governance_hash216: str
    origin_hash216: str
    replay_hash216: str
    semantic_hash216: str
    causal_hash216: str
    temporal_hash216: str
    identity_hash216: str

    forward_convergence_hash216: str
    reciprocal_convergence_hash216: str

    attractor_topology_hash216: str

    convergent: bool = True
    reconstructible: bool = True
    globally_canonical: bool = True
    phase_equivalent: bool = True
    temporally_equivalent: bool = True

    stability_score: float = 1.0
    consensus_depth: int = 0
    branch_collapse_factor: float = 1.0

    freeze_required: bool = False
    rollback_required: bool = False
    correction_required: bool = False

    projection_witness: Optional[HHSConsensusWitness] = None
    execution_witness: Optional[HHSConsensusWitness] = None
    transport_witness: Optional[HHSConsensusWitness] = None
    governance_witness: Optional[HHSConsensusWitness] = None
    reciprocal_witness: Optional[HHSConsensusWitness] = None

    attractor_proof_hash216: str = ""

    timestamp_ns: int = field(default_factory=time.time_ns)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:

        if not self.convergent:
            return False

        if not self.reconstructible:
            return False

        if not self.globally_canonical:
            return False

        if not self.phase_equivalent:
            return False

        if not self.temporally_equivalent:
            return False

        if self.rollback_required and not self.freeze_required:
            return False

        if self.stability_score < 0.0:
            return False

        if self.consensus_depth < 0:
            return False

        if self.branch_collapse_factor < 0.0:
            return False

        for witness in (
            self.projection_witness,
            self.execution_witness,
            self.transport_witness,
            self.governance_witness,
            self.reciprocal_witness,
        ):
            if witness is not None and not witness.validate():
                return False

        return True

    def closure_hash216(self) -> str:

        payload = {
            "attractor_id": self.attractor_id,

            "source_branch": self.source_branch_hash216,
            "canonical_branch": self.canonical_branch_hash216,

            "projection": self.projection_hash216,
            "execution": self.execution_hash216,
            "transport": self.transport_hash216,
            "governance": self.governance_hash216,
            "origin": self.origin_hash216,
            "replay": self.replay_hash216,
            "semantic": self.semantic_hash216,
            "causal": self.causal_hash216,
            "temporal": self.temporal_hash216,
            "identity": self.identity_hash216,

            "forward_convergence": self.forward_convergence_hash216,
            "reciprocal_convergence": self.reciprocal_convergence_hash216,

            "topology": self.attractor_topology_hash216,

            "stability_score": self.stability_score,
            "consensus_depth": self.consensus_depth,
            "branch_collapse_factor": self.branch_collapse_factor,

            "freeze_required": self.freeze_required,
            "rollback_required": self.rollback_required,
            "correction_required": self.correction_required,
        }

        return _hash216(
            json.dumps(payload, sort_keys=True)
        )

    def receipt(self) -> Dict[str, Any]:

        return {
            "attractor_id": self.attractor_id,
            "closure_hash216": self.closure_hash216(),
            "attractor_proof_hash216": self.attractor_proof_hash216,

            "convergent": self.convergent,
            "reconstructible": self.reconstructible,
            "globally_canonical": self.globally_canonical,

            "stability_score": self.stability_score,
            "consensus_depth": self.consensus_depth,
            "branch_collapse_factor": self.branch_collapse_factor,

            "freeze_required": self.freeze_required,
            "rollback_required": self.rollback_required,
            "correction_required": self.correction_required,

            "valid": self.validate(),
            "timestamp_ns": self.timestamp_ns,
        }


class HHSRecursiveConsensusConstellation:
    """
    Canonical Runtime OS recursive manifold convergence substrate.
    """

    def __init__(self):

        self.attractor_registry: Dict[
            str,
            HHSConsensusAttractor
        ] = {}

        self.attractor_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.attractor_dependencies: Dict[
            str,
            Set[str]
        ] = {}

        self.source_branch_field: Dict[str, str] = {}
        self.canonical_branch_field: Dict[str, str] = {}

        self.projection_field: Dict[str, str] = {}
        self.execution_field: Dict[str, str] = {}
        self.transport_field: Dict[str, str] = {}
        self.governance_field: Dict[str, str] = {}
        self.origin_field: Dict[str, str] = {}
        self.replay_field: Dict[str, str] = {}
        self.semantic_field: Dict[str, str] = {}
        self.causal_field: Dict[str, str] = {}
        self.temporal_field: Dict[str, str] = {}
        self.identity_field: Dict[str, str] = {}

    def register_attractor(
        self,
        attractor: HHSConsensusAttractor,
    ) -> bool:

        if not attractor.validate():
            return False

        self.attractor_registry[
            attractor.attractor_id
        ] = attractor

        if (
            attractor.attractor_id
            not in self.attractor_lineage
        ):
            self.attractor_lineage[
                attractor.attractor_id
            ] = []

        self.attractor_lineage[
            attractor.attractor_id
        ].append(
            attractor.closure_hash216()
        )

        self.source_branch_field[
            attractor.attractor_id
        ] = attractor.source_branch_hash216

        self.canonical_branch_field[
            attractor.attractor_id
        ] = attractor.canonical_branch_hash216

        self.projection_field[
            attractor.attractor_id
        ] = attractor.projection_hash216

        self.execution_field[
            attractor.attractor_id
        ] = attractor.execution_hash216

        self.transport_field[
            attractor.attractor_id
        ] = attractor.transport_hash216

        self.governance_field[
            attractor.attractor_id
        ] = attractor.governance_hash216

        self.origin_field[
            attractor.attractor_id
        ] = attractor.origin_hash216

        self.replay_field[
            attractor.attractor_id
        ] = attractor.replay_hash216

        self.semantic_field[
            attractor.attractor_id
        ] = attractor.semantic_hash216

        self.causal_field[
            attractor.attractor_id
        ] = attractor.causal_hash216

        self.temporal_field[
            attractor.attractor_id
        ] = attractor.temporal_hash216

        self.identity_field[
            attractor.attractor_id
        ] = attractor.identity_hash216

        if (
            attractor.attractor_id
            not in self.attractor_dependencies
        ):
            self.attractor_dependencies[
                attractor.attractor_id
            ] = set()

        return True

    def connect_attractor_dependency(
        self,
        source_attractor: str,
        target_attractor: str,
    ) -> bool:

        if (
            source_attractor
            not in self.attractor_registry
        ):
            return False

        if (
            target_attractor
            not in self.attractor_registry
        ):
            return False

        self.attractor_dependencies[
            source_attractor
        ].add(
            target_attractor
        )

        return True

    def stabilize_attractor(
        self,
        source_branch_hash216: str,
        canonical_branch_hash216: str,

        projection_hash216: str,
        execution_hash216: str,
        transport_hash216: str,
        governance_hash216: str,
        origin_hash216: str,
        replay_hash216: str,
        semantic_hash216: str,
        causal_hash216: str,
        temporal_hash216: str,
        identity_hash216: str,

        stability_score: float = 1.0,
        consensus_depth: int = 0,
        branch_collapse_factor: float = 1.0,
    ) -> HHSConsensusAttractor:

        closure_seed = _hash216(
            json.dumps(
                {
                    "source_branch": source_branch_hash216,
                    "canonical_branch": canonical_branch_hash216,

                    "projection": projection_hash216,
                    "execution": execution_hash216,
                    "transport": transport_hash216,
                    "governance": governance_hash216,
                    "origin": origin_hash216,
                    "replay": replay_hash216,
                    "semantic": semantic_hash216,
                    "causal": causal_hash216,
                    "temporal": temporal_hash216,
                    "identity": identity_hash216,

                    "stability_score": stability_score,
                    "consensus_depth": consensus_depth,
                    "branch_collapse_factor": branch_collapse_factor,
                },
                sort_keys=True,
            )
        )

        convergent = (
            source_branch_hash216 != ""
            and canonical_branch_hash216 != ""
            and projection_hash216 != ""
            and execution_hash216 != ""
            and transport_hash216 != ""
            and governance_hash216 != ""
            and origin_hash216 != ""
            and replay_hash216 != ""
            and semantic_hash216 != ""
            and causal_hash216 != ""
            and temporal_hash216 != ""
            and identity_hash216 != ""
            and stability_score >= 0.5
        )

        freeze_required = not convergent
        rollback_required = not convergent
        correction_required = not convergent

        attractor = HHSConsensusAttractor(
            attractor_id=closure_seed,

            source_branch_hash216=source_branch_hash216,
            canonical_branch_hash216=canonical_branch_hash216,

            projection_hash216=projection_hash216,
            execution_hash216=execution_hash216,
            transport_hash216=transport_hash216,
            governance_hash216=governance_hash216,
            origin_hash216=origin_hash216,
            replay_hash216=replay_hash216,
            semantic_hash216=semantic_hash216,
            causal_hash216=causal_hash216,
            temporal_hash216=temporal_hash216,
            identity_hash216=identity_hash216,

            forward_convergence_hash216=closure_seed,
            reciprocal_convergence_hash216=closure_seed[::-1],

            attractor_topology_hash216=closure_seed,

            convergent=convergent,
            reconstructible=convergent,
            globally_canonical=convergent,
            phase_equivalent=convergent,
            temporally_equivalent=convergent,

            stability_score=stability_score,
            consensus_depth=consensus_depth,
            branch_collapse_factor=branch_collapse_factor,

            freeze_required=freeze_required,
            rollback_required=rollback_required,
            correction_required=correction_required,

            attractor_proof_hash216=closure_seed,
        )

        self.register_attractor(attractor)

        return attractor

    def validate_constellation(self) -> bool:

        for attractor in (
            self.attractor_registry.values()
        ):
            if not attractor.validate():
                return False

        return True

    def globally_canonical(self) -> bool:

        for attractor in (
            self.attractor_registry.values()
        ):
            if not attractor.globally_canonical:
                return False

        return True

    def attractor_cone(
        self,
        attractor_id: str,
    ) -> Set[str]:

        visited: Set[str] = set()

        def walk(node: str):

            if node in visited:
                return

            visited.add(node)

            for nxt in (
                self.attractor_dependencies.get(
                    node,
                    set(),
                )
            ):
                walk(nxt)

        walk(attractor_id)

        return visited

    def field_hash216(self) -> str:

        payload = {
            "attractor_registry": sorted(
                [
                    attractor.closure_hash216()
                    for attractor in (
                        self.attractor_registry.values()
                    )
                ]
            ),

            "lineage": self.attractor_lineage,

            "dependencies": {
                k: sorted(list(v))
                for k, v in (
                    self.attractor_dependencies.items()
                )
            },

            "source_branch": self.source_branch_field,
            "canonical_branch": self.canonical_branch_field,

            "projection": self.projection_field,
            "execution": self.execution_field,
            "transport": self.transport_field,
            "governance": self.governance_field,
            "origin": self.origin_field,
            "replay": self.replay_field,
            "semantic": self.semantic_field,
            "causal": self.causal_field,
            "temporal": self.temporal_field,
            "identity": self.identity_field,
        }

        return _hash216(
            json.dumps(payload, sort_keys=True)
        )

    def authoritative_attractor(
        self,
    ) -> Optional[
        HHSConsensusAttractor
    ]:

        if not self.attractor_registry:
            return None

        ordered = sorted(
            self.attractor_registry.values(),
            key=lambda a: (
                -a.stability_score,
                -a.consensus_depth,
                a.branch_collapse_factor,
                a.closure_hash216(),
            ),
        )

        return ordered[0]

    def receipt(self) -> Dict[str, Any]:

        authoritative = (
            self.authoritative_attractor()
        )

        return {
            "field_hash216": (
                self.field_hash216()
            ),

            "attractor_count": len(
                self.attractor_registry
            ),

            "dependency_count": sum(
                len(v)
                for v in (
                    self.attractor_dependencies.values()
                )
            ),

            "globally_canonical": (
                self.globally_canonical()
            ),

            "authoritative_attractor": (
                authoritative.attractor_id
                if authoritative
                else None
            ),

            "valid": (
                self.validate_constellation()
            ),

            "timestamp_ns": (
                time.time_ns()
            ),
        }