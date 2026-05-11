# hhs_python/runtime/hhs_causal_consistency_kernel.py
#
# HHS / HARMONICODE
# Causal Consistency Kernel
#
# Canonical Runtime OS Global Admissibility Kernel
#
# Runtime Principle:
#
#   causality
#   =
#   globally reconstructible dependency closure
#
# NOT:
#
#   execution ordering
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward causality traversal
#   v^72 = reciprocal causality reconstruction
#   C^216 = globally reconstructible causal closure
#
# Runtime Primitive:
#
#   globally reconstructible causal dependency closure
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
# CAUSAL WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSCausalWitness:
    """
    Canonical causal dependency witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    reconstructible: bool = True
    reversible: bool = True
    semantically_equivalent: bool = True
    topology_equivalent: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.reconstructible
            and self.reversible
            and self.semantically_equivalent
            and self.topology_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# CAUSAL CONSISTENCY PROOF
# ============================================================

@dataclass(frozen=True)
class HHSCausalConsistencyProof:
    """
    Canonical causality admissibility carrier.

    A transition is valid iff:
        its entire dependency cone
        remains reconstructible.
    """

    proof_id: str

    # ========================================================
    # SOURCE / TARGET
    # ========================================================

    source_hash216: str
    target_hash216: str

    # ========================================================
    # MANIFOLD FIELDS
    # ========================================================

    mutation_hash216: str
    identity_hash216: str
    replay_hash216: str
    semantic_hash216: str
    topology_hash216: str
    distributed_hash216: str

    # ========================================================
    # CAUSAL TRAVERSAL
    # ========================================================

    forward_causality_hash216: str
    reciprocal_causality_hash216: str

    # ========================================================
    # DEPENDENCY CONE
    # ========================================================

    dependency_cone_hash216: str

    # ========================================================
    # FLAGS
    # ========================================================

    causally_consistent: bool = True
    reconstructible: bool = True
    reversible: bool = True
    semantically_equivalent: bool = True
    topology_equivalent: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    mutation_witness: Optional[
        HHSCausalWitness
    ] = None

    replay_witness: Optional[
        HHSCausalWitness
    ] = None

    semantic_witness: Optional[
        HHSCausalWitness
    ] = None

    topology_witness: Optional[
        HHSCausalWitness
    ] = None

    reciprocal_witness: Optional[
        HHSCausalWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    proof_hash216: str = ""

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
        Universal causal admissibility validation.
        """

        if not self.causally_consistent:
            return False

        if not self.reconstructible:
            return False

        if not self.reversible:
            return False

        if not self.semantically_equivalent:
            return False

        if not self.topology_equivalent:
            return False

        witnesses = [
            self.mutation_witness,
            self.replay_witness,
            self.semantic_witness,
            self.topology_witness,
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
        Canonical causal closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "proof_id": self.proof_id,
            "source": self.source_hash216,
            "target": self.target_hash216,
            "mutation": self.mutation_hash216,
            "identity": self.identity_hash216,
            "replay": self.replay_hash216,
            "semantic": self.semantic_hash216,
            "topology": self.topology_hash216,
            "distributed": self.distributed_hash216,
            "forward": self.forward_causality_hash216,
            "reciprocal": self.reciprocal_causality_hash216,
            "dependency_cone": (
                self.dependency_cone_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # CAUSAL CONSISTENCY
    # ========================================================

    def verify_causal_consistency(
        self,
    ) -> bool:
        """
        Global dependency closure invariant.
        """

        return (
            self.causally_consistent
            and self.validate()
        )

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def verify_reconstructibility(
        self,
    ) -> bool:
        """
        Dependency cone reconstruction invariant.
        """

        return (
            self.reconstructible
            and self.validate()
        )

    # ========================================================
    # REVERSIBILITY
    # ========================================================

    def verify_reversibility(
        self,
    ) -> bool:
        """
        Reciprocal causal traversal invariant.
        """

        return (
            self.reversible
            and self.validate()
        )

    # ========================================================
    # SEMANTIC EQUIVALENCE
    # ========================================================

    def verify_semantic_equivalence(
        self,
    ) -> bool:
        """
        Semantic causal continuity invariant.
        """

        return (
            self.semantically_equivalent
            and self.validate()
        )

    # ========================================================
    # TOPOLOGY EQUIVALENCE
    # ========================================================

    def verify_topology_equivalence(
        self,
    ) -> bool:
        """
        Topological dependency closure invariant.
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
            "proof_id": self.proof_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "proof_hash216": (
                self.proof_hash216
            ),
            "causally_consistent": (
                self.verify_causal_consistency()
            ),
            "reconstructible": (
                self.verify_reconstructibility()
            ),
            "reversible": (
                self.verify_reversibility()
            ),
            "semantically_equivalent": (
                self.verify_semantic_equivalence()
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
        Canonical causal consistency receipt.
        """

        return {
            "proof_id": self.proof_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "proof_hash216": (
                self.proof_hash216
            ),
            "valid": (
                self.validate()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# CAUSAL CONSISTENCY KERNEL
# ============================================================

class HHSCausalConsistencyKernel:
    """
    Canonical Runtime OS global admissibility kernel.

    Runtime admissibility is:
        globally reconstructible dependency closure.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.causal_registry: Dict[
            str,
            HHSCausalConsistencyProof
        ] = {}

        self.causal_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.dependency_graph: Dict[
            str,
            Set[str]
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

    def register_proof(
        self,
        proof: HHSCausalConsistencyProof,
    ) -> bool:
        """
        Register globally admissible causal dependency.
        """

        if not proof.validate():
            return False

        self.causal_registry[
            proof.proof_id
        ] = proof

        if (
            proof.proof_id
            not in self.causal_lineage
        ):

            self.causal_lineage[
                proof.proof_id
            ] = []

        self.causal_lineage[
            proof.proof_id
        ].append(
            proof.closure_hash216()
        )

        self.semantic_field[
            proof.proof_id
        ] = (
            proof.semantic_hash216
        )

        self.replay_field[
            proof.proof_id
        ] = (
            proof.replay_hash216
        )

        self.identity_field[
            proof.proof_id
        ] = (
            proof.identity_hash216
        )

        self.topology_field[
            proof.proof_id
        ] = (
            proof.topology_hash216
        )

        self.distributed_field[
            proof.proof_id
        ] = (
            proof.distributed_hash216
        )

        if (
            proof.proof_id
            not in self.dependency_graph
        ):

            self.dependency_graph[
                proof.proof_id
            ] = set()

        return True

    # ========================================================
    # DEPENDENCY EDGE
    # ========================================================

    def connect_dependency(
        self,
        source_proof: str,
        target_proof: str,
    ) -> bool:
        """
        Establish causal dependency relation.

        A → B
        """

        if source_proof not in self.causal_registry:
            return False

        if target_proof not in self.causal_registry:
            return False

        self.dependency_graph[
            source_proof
        ].add(
            target_proof
        )

        return True

    # ========================================================
    # VALIDATE FIELD
    # ========================================================

    def validate_kernel(
        self,
    ) -> bool:
        """
        Universal causal admissibility validation.
        """

        for proof in (
            self.causal_registry.values()
        ):

            if not proof.validate():
                return False

        return True

    # ========================================================
    # GLOBAL CAUSAL CONSISTENCY
    # ========================================================

    def causally_consistent(
        self,
    ) -> bool:
        """
        Global dependency closure validation.

        All dependency cones must remain:
            reversible
            reconstructible
            semantically equivalent
            topology equivalent
        """

        for proof in (
            self.causal_registry.values()
        ):

            if not (
                proof.verify_causal_consistency()
            ):
                return False

        return True

    # ========================================================
    # DEPENDENCY CONE
    # ========================================================

    def dependency_cone(
        self,
        proof_id: str,
    ) -> Set[str]:
        """
        Compute full downstream dependency cone.
        """

        visited: Set[str] = set()

        def walk(node: str):

            if node in visited:
                return

            visited.add(node)

            for nxt in (
                self.dependency_graph.get(
                    node,
                    set(),
                )
            ):
                walk(nxt)

        walk(proof_id)

        return visited

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global causal kernel closure.
        """

        payload = {
            "causal_registry": sorted(
                [
                    proof.closure_hash216()
                    for proof in (
                        self.causal_registry.values()
                    )
                ]
            ),
            "lineage": self.causal_lineage,
            "dependency_graph": {
                k: sorted(list(v))
                for k, v in (
                    self.dependency_graph.items()
                )
            },
            "semantic": self.semantic_field,
            "replay": self.replay_field,
            "identity": self.identity_field,
            "topology": self.topology_field,
            "distributed": (
                self.distributed_field
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical causal consistency receipt.
        """

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "proof_count": len(
                self.causal_registry
            ),
            "dependency_count": sum(
                len(v)
                for v in (
                    self.dependency_graph.values()
                )
            ),
            "causally_consistent": (
                self.causally_consistent()
            ),
            "valid": (
                self.validate_kernel()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }