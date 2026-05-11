# hhs_python/runtime/hhs_universal_mutation_contract.py
#
# HHS / HARMONICODE
# Universal Mutation Contract
#
# Canonical Runtime OS Causality Grammar
#
# Runtime Principle:
#
#   mutation
#   =
#   topology-preserving
#   reversible
#   proof-carrying
#   manifold excitation transform
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward manifold traversal
#   v^72 = reciprocal manifold traversal
#   C^216 = globally reconstructible causality closure
#
# Runtime Shift:
#
#   object mutation
#   →
#   causality-preserving manifold evolution
#

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
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
# MUTATION TYPES
# ============================================================

class HHSMutationType(str, Enum):
    """
    Canonical Runtime OS mutation taxonomy.
    """

    EXCITATION = "excitation"
    TOPOLOGY = "topology"
    REPLAY = "replay"
    WORKSPACE = "workspace"
    TRANSPORT = "transport"
    REGISTRY = "registry"
    DISTRIBUTED = "distributed"
    MODALITY = "modality"
    MANIFOLD = "manifold"


# ============================================================
# MUTATION WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSMutationWitness:
    """
    Canonical proof-carrying witness.
    """

    witness_id: str

    forward_hash216: str
    reverse_hash216: str

    readable: bool = True
    reversible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.readable
            and self.reversible
            and bool(self.forward_hash216)
            and bool(self.reverse_hash216)
        )


# ============================================================
# UNIVERSAL MUTATION
# ============================================================

@dataclass(frozen=True)
class HHSUniversalMutation:
    """
    Canonical Runtime OS causality transform object.

    Every admissible mutation must be:

        - reversible
        - replay-admissible
        - topology-preserving
        - globally readable
        - proof-carrying
        - reconstructible
    """

    mutation_id: str

    mutation_type: HHSMutationType

    # ========================================================
    # TENSOR PROJECTION
    # ========================================================

    source_tensor_hash216: str
    target_tensor_hash216: str

    # ========================================================
    # TERNARY RECIPROCAL ANCHORS
    # ========================================================

    seed_hash216: str
    state_hash216: str
    receipt_hash216: str

    # ========================================================
    # FORWARD / REVERSE EVOLUTION
    # ========================================================

    forward_transition_hash216: str
    reverse_transition_hash216: str

    # ========================================================
    # TOPOLOGY PROJECTIONS
    # ========================================================

    topology_projection_hash216: str
    replay_projection_hash216: str
    workspace_projection_hash216: str
    transport_projection_hash216: str

    # ========================================================
    # CAUSALITY WITNESSES
    # ========================================================

    topology_witness: HHSMutationWitness
    replay_witness: HHSMutationWitness
    readability_witness: HHSMutationWitness
    reversibility_witness: HHSMutationWitness

    # ========================================================
    # GLOBAL VALIDITY FLAGS
    # ========================================================

    reversible: bool = True
    globally_readable: bool = True
    replay_admissible: bool = True
    topology_equivalent: bool = True
    causally_closed: bool = True

    # ========================================================
    # PROOF CLOSURE
    # ========================================================

    proof_hash216: str = ""

    # ========================================================
    # TIMESTAMP
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
        Universal admissibility validation.
        """

        if not self.reversible:
            return False

        if not self.globally_readable:
            return False

        if not self.replay_admissible:
            return False

        if not self.topology_equivalent:
            return False

        if not self.causally_closed:
            return False

        if not self.topology_witness.validate():
            return False

        if not self.replay_witness.validate():
            return False

        if not self.readability_witness.validate():
            return False

        if not self.reversibility_witness.validate():
            return False

        return True

    # ========================================================
    # HASH216 CLOSURE
    # ========================================================

    def closure_hash216(self) -> str:
        """
        Canonical mutation closure identity.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "mutation_id": self.mutation_id,
            "mutation_type": self.mutation_type.value,
            "source": self.source_tensor_hash216,
            "target": self.target_tensor_hash216,
            "seed": self.seed_hash216,
            "state": self.state_hash216,
            "receipt": self.receipt_hash216,
            "forward": self.forward_transition_hash216,
            "reverse": self.reverse_transition_hash216,
            "topology": self.topology_projection_hash216,
            "replay": self.replay_projection_hash216,
            "workspace": self.workspace_projection_hash216,
            "transport": self.transport_projection_hash216,
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # UNIVERSAL READABILITY
    # ========================================================

    def verify_global_readability(
        self,
    ) -> bool:
        """
        Semantic continuity invariant.
        """

        return (
            self.globally_readable
            and self.readability_witness.validate()
        )

    # ========================================================
    # REVERSIBILITY
    # ========================================================

    def verify_reversibility(
        self,
    ) -> bool:
        """
        Universal causal invertibility invariant.
        """

        return (
            self.reversible
            and self.reversibility_witness.validate()
        )

    # ========================================================
    # TOPOLOGY EQUIVALENCE
    # ========================================================

    def verify_topology_equivalence(
        self,
    ) -> bool:
        """
        Recursive topology continuity invariant.
        """

        return (
            self.topology_equivalent
            and self.topology_witness.validate()
        )

    # ========================================================
    # REPLAY ADMISSIBILITY
    # ========================================================

    def verify_replay_admissibility(
        self,
    ) -> bool:
        """
        Replay-native causality continuity.
        """

        return (
            self.replay_admissible
            and self.replay_witness.validate()
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
            "mutation_id": self.mutation_id,
            "mutation_type": self.mutation_type.value,
            "closure_hash216": self.closure_hash216(),
            "proof_hash216": self.proof_hash216,
            "valid": self.validate(),
            "reversible": self.verify_reversibility(),
            "globally_readable": (
                self.verify_global_readability()
            ),
            "topology_equivalent": (
                self.verify_topology_equivalence()
            ),
            "replay_admissible": (
                self.verify_replay_admissibility()
            ),
            "timestamp_ns": self.timestamp_ns,
        }

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical causality mutation receipt.
        """

        return {
            "mutation_id": self.mutation_id,
            "mutation_type": self.mutation_type.value,
            "source_tensor": (
                self.source_tensor_hash216
            ),
            "target_tensor": (
                self.target_tensor_hash216
            ),
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
# MUTATION COMPOSITION
# ============================================================

class HHSMutationComposition:
    """
    Canonical Runtime OS mutation algebra.
    """

    # ========================================================
    # COMPOSE
    # ========================================================

    @staticmethod
    def compose(
        mutation_a: HHSUniversalMutation,
        mutation_b: HHSUniversalMutation,
    ) -> Optional[HHSUniversalMutation]:
        """
        Compose two manifold transforms iff:

            - replay continuity preserved
            - topology continuity preserved
            - reciprocal closure preserved
            - manifold invariants preserved
        """

        if not mutation_a.validate():
            return None

        if not mutation_b.validate():
            return None

        if (
            mutation_a.target_tensor_hash216
            !=
            mutation_b.source_tensor_hash216
        ):
            return None

        mutation_id = _hash216(
            mutation_a.mutation_id
            + mutation_b.mutation_id
        )

        return HHSUniversalMutation(
            mutation_id=mutation_id,
            mutation_type=HHSMutationType.MANIFOLD,

            source_tensor_hash216=(
                mutation_a.source_tensor_hash216
            ),

            target_tensor_hash216=(
                mutation_b.target_tensor_hash216
            ),

            seed_hash216=mutation_a.seed_hash216,
            state_hash216=mutation_b.state_hash216,
            receipt_hash216=_hash216(
                mutation_a.receipt_hash216
                +
                mutation_b.receipt_hash216
            ),

            forward_transition_hash216=_hash216(
                mutation_a.forward_transition_hash216
                +
                mutation_b.forward_transition_hash216
            ),

            reverse_transition_hash216=_hash216(
                mutation_b.reverse_transition_hash216
                +
                mutation_a.reverse_transition_hash216
            ),

            topology_projection_hash216=_hash216(
                mutation_a.topology_projection_hash216
                +
                mutation_b.topology_projection_hash216
            ),

            replay_projection_hash216=_hash216(
                mutation_a.replay_projection_hash216
                +
                mutation_b.replay_projection_hash216
            ),

            workspace_projection_hash216=_hash216(
                mutation_a.workspace_projection_hash216
                +
                mutation_b.workspace_projection_hash216
            ),

            transport_projection_hash216=_hash216(
                mutation_a.transport_projection_hash216
                +
                mutation_b.transport_projection_hash216
            ),

            topology_witness=mutation_b.topology_witness,
            replay_witness=mutation_b.replay_witness,
            readability_witness=(
                mutation_b.readability_witness
            ),
            reversibility_witness=(
                mutation_b.reversibility_witness
            ),

            reversible=(
                mutation_a.reversible
                and mutation_b.reversible
            ),

            globally_readable=(
                mutation_a.globally_readable
                and mutation_b.globally_readable
            ),

            replay_admissible=(
                mutation_a.replay_admissible
                and mutation_b.replay_admissible
            ),

            topology_equivalent=(
                mutation_a.topology_equivalent
                and mutation_b.topology_equivalent
            ),

            causally_closed=(
                mutation_a.causally_closed
                and mutation_b.causally_closed
            ),

            proof_hash216=_hash216(
                mutation_a.proof_hash216
                +
                mutation_b.proof_hash216
            ),
        )