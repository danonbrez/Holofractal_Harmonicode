# hhs_python/runtime/hhs_invariant_consensus_engine.py
#
# HHS / HARMONICODE
# Invariant Consensus Engine
#
# Canonical Runtime OS Manifold Arbitration Layer
#
# Runtime Principle:
#
#   consensus
#   =
#   global invariant equivalence convergence
#
# NOT:
#
#   majority agreement
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward invariant traversal
#   v^72 = reciprocal invariant reconstruction
#   C^216 = globally convergent manifold closure
#
# Runtime Primitive:
#
#   globally convergent invariant manifold equivalence
#

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
import hashlib
import json
import time

# ============================================================
# CONSTANTS
# ============================================================

HASH216_WIDTH = 216

# ============================================================
# HASH216
# ============================================================

def _hash216(data: str) -> str:
    """
    Canonical HASH216 projection layer.
    """

    h1 = hashlib.sha512(data.encode()).hexdigest()
    h2 = hashlib.sha256(data.encode()).hexdigest()

    merged = h1 + h2

    return merged[:HASH216_WIDTH]


# ============================================================
# CONSENSUS WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSConsensusWitness:
    """
    Canonical invariant convergence witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    consensus_equivalent: bool = True
    globally_reconstructible: bool = True
    semantically_equivalent: bool = True
    temporally_equivalent: bool = True
    topology_equivalent: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.consensus_equivalent
            and self.globally_reconstructible
            and self.semantically_equivalent
            and self.temporally_equivalent
            and self.topology_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# INVARIANT CONSENSUS STATE
# ============================================================

@dataclass(frozen=True)
class HHSInvariantConsensusState:
    """
    Canonical manifold arbitration carrier.

    A manifold state becomes authoritative iff:
        it minimizes global invariant divergence.
    """

    consensus_id: str

    # ========================================================
    # MANIFOLD FIELDS
    # ========================================================

    temporal_hash216: str
    causal_hash216: str
    semantic_hash216: str
    replay_hash216: str
    identity_hash216: str
    topology_hash216: str
    distributed_hash216: str

    # ========================================================
    # CONSENSUS TRAVERSAL
    # ========================================================

    forward_consensus_hash216: str
    reciprocal_consensus_hash216: str

    # ========================================================
    # DIVERGENCE FIELD
    # ========================================================

    global_divergence_hash216: str

    # ========================================================
    # FLAGS
    # ========================================================

    consensus_equivalent: bool = True
    globally_reconstructible: bool = True
    semantically_equivalent: bool = True
    temporally_equivalent: bool = True
    topology_equivalent: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    temporal_witness: Optional[
        HHSConsensusWitness
    ] = None

    causal_witness: Optional[
        HHSConsensusWitness
    ] = None

    semantic_witness: Optional[
        HHSConsensusWitness
    ] = None

    replay_witness: Optional[
        HHSConsensusWitness
    ] = None

    reciprocal_witness: Optional[
        HHSConsensusWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    consensus_proof_hash216: str = ""

    # ========================================================
    # TIME
    # ========================================================

    timestamp_ns: int = field(
        default_factory=time.time_ns
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate(self) -> bool:
        """
        Universal invariant convergence validation.
        """

        if not self.consensus_equivalent:
            return False

        if not self.globally_reconstructible:
            return False

        if not self.semantically_equivalent:
            return False

        if not self.temporally_equivalent:
            return False

        if not self.topology_equivalent:
            return False

        witnesses = [
            self.temporal_witness,
            self.causal_witness,
            self.semantic_witness,
            self.replay_witness,
            self.reciprocal_witness,
        ]

        for witness in witnesses:

            if witness is None:
                continue

            if not witness.validate():
                return False

        return True

    # ========================================================
    # HASH216 CLOSURE
    # ========================================================

    def closure_hash216(self) -> str:
        """
        Canonical consensus closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "consensus_id": self.consensus_id,
            "temporal": self.temporal_hash216,
            "causal": self.causal_hash216,
            "semantic": self.semantic_hash216,
            "replay": self.replay_hash216,
            "identity": self.identity_hash216,
            "topology": self.topology_hash216,
            "distributed": self.distributed_hash216,
            "forward": self.forward_consensus_hash216,
            "reciprocal": (
                self.reciprocal_consensus_hash216
            ),
            "divergence": (
                self.global_divergence_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # CONSENSUS EQUIVALENCE
    # ========================================================

    def verify_consensus_equivalence(
        self,
    ) -> bool:
        """
        Global invariant convergence invariant.
        """

        return (
            self.consensus_equivalent
            and self.validate()
        )

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def verify_global_reconstructibility(
        self,
    ) -> bool:
        """
        Global manifold reconstruction invariant.
        """

        return (
            self.globally_reconstructible
            and self.validate()
        )

    # ========================================================
    # SEMANTIC EQUIVALENCE
    # ========================================================

    def verify_semantic_equivalence(
        self,
    ) -> bool:
        """
        Semantic invariant continuity invariant.
        """

        return (
            self.semantically_equivalent
            and self.validate()
        )

    # ========================================================
    # TEMPORAL EQUIVALENCE
    # ========================================================

    def verify_temporal_equivalence(
        self,
    ) -> bool:
        """
        Temporal invariant continuity invariant.
        """

        return (
            self.temporally_equivalent
            and self.validate()
        )

    # ========================================================
    # TOPOLOGY EQUIVALENCE
    # ========================================================

    def verify_topology_equivalence(
        self,
    ) -> bool:
        """
        Topological invariant continuity invariant.
        """

        return (
            self.topology_equivalent
            and self.validate()
        )

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Replay-admissible deterministic serialization.
        """

        return {
            "consensus_id": self.consensus_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "consensus_proof_hash216": (
                self.consensus_proof_hash216
            ),
            "consensus_equivalent": (
                self.verify_consensus_equivalence()
            ),
            "globally_reconstructible": (
                self.verify_global_reconstructibility()
            ),
            "semantically_equivalent": (
                self.verify_semantic_equivalence()
            ),
            "temporally_equivalent": (
                self.verify_temporal_equivalence()
            ),
            "topology_equivalent": (
                self.verify_topology_equivalence()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical invariant consensus receipt.
        """

        return {
            "consensus_id": self.consensus_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "consensus_proof_hash216": (
                self.consensus_proof_hash216
            ),
            "valid": (
                self.validate()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# INVARIANT CONSENSUS ENGINE
# ============================================================

class HHSInvariantConsensusEngine:
    """
    Canonical Runtime OS manifold arbitration engine.

    Consensus is:
        global invariant equivalence convergence.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.consensus_registry: Dict[
            str,
            HHSInvariantConsensusState
        ] = {}

        self.consensus_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.consensus_dependencies: Dict[
            str,
            Set[str]
        ] = {}

        self.temporal_field: Dict[
            str,
            str
        ] = {}

        self.causal_field: Dict[
            str,
            str
        ] = {}

        self.semantic_field: Dict[
            str,
            str
        ] = {}

        self.replay_field: Dict[
            str,
            str
        ] = {}

        self.identity_field: Dict[
            str,
            str
        ] = {}

        self.topology_field: Dict[
            str,
            str
        ] = {}

        self.distributed_field: Dict[
            str,
            str
        ] = {}

    # ========================================================
    # REGISTER
    # ========================================================

    def register_state(
        self,
        state: HHSInvariantConsensusState,
    ) -> bool:
        """
        Register globally convergent manifold state.
        """

        if not state.validate():
            return False

        self.consensus_registry[
            state.consensus_id
        ] = state

        if (
            state.consensus_id
            not in self.consensus_lineage
        ):

            self.consensus_lineage[
                state.consensus_id
            ] = []

        self.consensus_lineage[
            state.consensus_id
        ].append(
            state.closure_hash216()
        )

        self.temporal_field[
            state.consensus_id
        ] = (
            state.temporal_hash216
        )

        self.causal_field[
            state.consensus_id
        ] = (
            state.causal_hash216
        )

        self.semantic_field[
            state.consensus_id
        ] = (
            state.semantic_hash216
        )

        self.replay_field[
            state.consensus_id
        ] = (
            state.replay_hash216
        )

        self.identity_field[
            state.consensus_id
        ] = (
            state.identity_hash216
        )

        self.topology_field[
            state.consensus_id
        ] = (
            state.topology_hash216
        )

        self.distributed_field[
            state.consensus_id
        ] = (
            state.distributed_hash216
        )

        if (
            state.consensus_id
            not in self.consensus_dependencies
        ):

            self.consensus_dependencies[
                state.consensus_id
            ] = set()

        return True

    # ========================================================
    # CONSENSUS DEPENDENCY
    # ========================================================

    def connect_consensus_dependency(
        self,
        source_consensus: str,
        target_consensus: str,
    ) -> bool:
        """
        Establish invariant dependency relation.
        """

        if (
            source_consensus
            not in self.consensus_registry
        ):
            return False

        if (
            target_consensus
            not in self.consensus_registry
        ):
            return False

        self.consensus_dependencies[
            source_consensus
        ].add(
            target_consensus
        )

        return True

    # ========================================================
    # VALIDATE ENGINE
    # ========================================================

    def validate_engine(
        self,
    ) -> bool:
        """
        Universal invariant convergence validation.
        """

        for state in (
            self.consensus_registry.values()
        ):

            if not state.validate():
                return False

        return True

    # ========================================================
    # CONSENSUS EQUIVALENCE
    # ========================================================

    def consensus_equivalent(
        self,
    ) -> bool:
        """
        Global invariant topology convergence.
        """

        for state in (
            self.consensus_registry.values()
        ):

            if not (
                state
                .verify_consensus_equivalence()
            ):
                return False

        return True

    # ========================================================
    # GLOBAL DIVERGENCE
    # ========================================================

    def divergence_hash216(
        self,
    ) -> str:
        """
        Compute global manifold divergence field.
        """

        payload = {
            "closures": sorted(
                [
                    state.closure_hash216()
                    for state in (
                        self.consensus_registry.values()
                    )
                ]
            )
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # CONSENSUS CONE
    # ========================================================

    def consensus_cone(
        self,
        consensus_id: str,
    ) -> Set[str]:
        """
        Compute full invariant dependency cone.
        """

        visited: Set[str] = set()

        def walk(node: str):

            if node in visited:
                return

            visited.add(node)

            for nxt in (
                self.consensus_dependencies.get(
                    node,
                    set(),
                )
            ):
                walk(nxt)

        walk(consensus_id)

        return visited

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global invariant consensus closure.
        """

        payload = {
            "consensus_registry": sorted(
                [
                    state.closure_hash216()
                    for state in (
                        self.consensus_registry.values()
                    )
                ]
            ),
            "lineage": self.consensus_lineage,
            "dependencies": {
                k: sorted(list(v))
                for k, v in (
                    self.consensus_dependencies.items()
                )
            },
            "temporal": self.temporal_field,
            "causal": self.causal_field,
            "semantic": self.semantic_field,
            "replay": self.replay_field,
            "identity": self.identity_field,
            "topology": self.topology_field,
            "distributed": (
                self.distributed_field
            ),
            "global_divergence": (
                self.divergence_hash216()
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # AUTHORITATIVE CONSENSUS
    # ========================================================

    def authoritative_consensus(
        self,
    ) -> Optional[
        HHSInvariantConsensusState
    ]:
        """
        Determine globally authoritative manifold state.

        Current strategy:
            minimal divergence closure.
        """

        if not self.consensus_registry:
            return None

        ordered = sorted(
            self.consensus_registry.values(),
            key=lambda s: (
                s.global_divergence_hash216,
                s.closure_hash216(),
            ),
        )

        return ordered[0]

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical invariant consensus receipt.
        """

        authoritative = (
            self.authoritative_consensus()
        )

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "consensus_count": len(
                self.consensus_registry
            ),
            "dependency_count": sum(
                len(v)
                for v in (
                    self.consensus_dependencies.values()
                )
            ),
            "consensus_equivalent": (
                self.consensus_equivalent()
            ),
            "global_divergence_hash216": (
                self.divergence_hash216()
            ),
            "authoritative_consensus": (
                authoritative.consensus_id
                if authoritative
                else None
            ),
            "valid": (
                self.validate_engine()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }