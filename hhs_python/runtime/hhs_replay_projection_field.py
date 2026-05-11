# hhs_python/runtime/hhs_replay_projection_field.py
#
# HHS / HARMONICODE
# Replay Projection Field
#
# Canonical Runtime OS Replay Geometry Layer
#
# Runtime Principle:
#
#   replay
#   =
#   reconstructible manifold re-projection
#
# NOT:
#
#   historical serialization playback
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward causality traversal
#   v^72 = reciprocal causality reconstruction
#   C^216 = replay-equivalent manifold closure
#
# Runtime Primitive:
#
#   reconstructible manifold projection continuity
#

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
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
# REPLAY WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSReplayWitness:
    """
    Canonical replay continuity witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    reconstructible: bool = True
    replay_equivalent: bool = True
    topology_equivalent: bool = True
    readable: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.reconstructible
            and self.replay_equivalent
            and self.topology_equivalent
            and self.readable
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# REPLAY PROJECTION
# ============================================================

@dataclass(frozen=True)
class HHSReplayProjection:
    """
    Canonical replay causality carrier.

    Replay is:
        reconstructible manifold re-projection.
    """

    projection_id: str

    # ========================================================
    # IDENTITY CONTINUITY
    # ========================================================

    source_identity_hash216: str
    target_identity_hash216: str

    # ========================================================
    # REPLAY TRAVERSAL
    # ========================================================

    forward_projection_hash216: str
    reciprocal_projection_hash216: str

    # ========================================================
    # TOPOLOGY PROJECTIONS
    # ========================================================

    topology_projection_hash216: str
    workspace_projection_hash216: str
    transport_projection_hash216: str

    # ========================================================
    # CONTINUITY CHAINS
    # ========================================================

    mutation_chain_hash216: str
    identity_chain_hash216: str

    # ========================================================
    # REPLAY FLAGS
    # ========================================================

    reconstructible: bool = True
    reversible: bool = True
    topology_equivalent: bool = True
    replay_equivalent: bool = True
    globally_readable: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    replay_witness: Optional[
        HHSReplayWitness
    ] = None

    topology_witness: Optional[
        HHSReplayWitness
    ] = None

    readability_witness: Optional[
        HHSReplayWitness
    ] = None

    reciprocal_witness: Optional[
        HHSReplayWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    projection_proof_hash216: str = ""

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
        Universal replay admissibility validation.
        """

        if not self.reconstructible:
            return False

        if not self.reversible:
            return False

        if not self.topology_equivalent:
            return False

        if not self.replay_equivalent:
            return False

        if not self.globally_readable:
            return False

        witnesses = [
            self.replay_witness,
            self.topology_witness,
            self.readability_witness,
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
        Canonical replay closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "projection_id": self.projection_id,
            "source_identity": (
                self.source_identity_hash216
            ),
            "target_identity": (
                self.target_identity_hash216
            ),
            "forward": (
                self.forward_projection_hash216
            ),
            "reciprocal": (
                self.reciprocal_projection_hash216
            ),
            "topology": (
                self.topology_projection_hash216
            ),
            "workspace": (
                self.workspace_projection_hash216
            ),
            "transport": (
                self.transport_projection_hash216
            ),
            "mutation_chain": (
                self.mutation_chain_hash216
            ),
            "identity_chain": (
                self.identity_chain_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # RECONSTRUCTION
    # ========================================================

    def verify_reconstructibility(
        self,
    ) -> bool:
        """
        Canonical replay reconstruction invariant.
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
        Reciprocal replay traversal invariant.
        """

        return (
            self.reversible
            and self.validate()
        )

    # ========================================================
    # TOPOLOGY
    # ========================================================

    def verify_topology_equivalence(
        self,
    ) -> bool:
        """
        Replay topology equivalence invariant.
        """

        return (
            self.topology_equivalent
            and self.validate()
        )

    # ========================================================
    # REPLAY EQUIVALENCE
    # ========================================================

    def verify_replay_equivalence(
        self,
    ) -> bool:
        """
        Canonical replay continuity invariant.
        """

        return (
            self.replay_equivalent
            and self.validate()
        )

    # ========================================================
    # READABILITY
    # ========================================================

    def verify_global_readability(
        self,
    ) -> bool:
        """
        Semantic replay continuity invariant.
        """

        return (
            self.globally_readable
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
            "projection_id": self.projection_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "projection_proof_hash216": (
                self.projection_proof_hash216
            ),
            "reconstructible": (
                self.verify_reconstructibility()
            ),
            "reversible": (
                self.verify_reversibility()
            ),
            "topology_equivalent": (
                self.verify_topology_equivalence()
            ),
            "replay_equivalent": (
                self.verify_replay_equivalence()
            ),
            "globally_readable": (
                self.verify_global_readability()
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
        Canonical replay projection receipt.
        """

        return {
            "projection_id": self.projection_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "projection_proof_hash216": (
                self.projection_proof_hash216
            ),
            "valid": (
                self.validate()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# REPLAY PROJECTION FIELD
# ============================================================

class HHSReplayProjectionField:
    """
    Canonical Runtime OS replay geometry field.

    Replay is:
        manifold reconstruction geometry.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.replay_registry: Dict[
            str,
            HHSReplayProjection
        ] = {}

        self.replay_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.workspace_projection_field: Dict[
            str,
            str
        ] = {}

        self.transport_projection_field: Dict[
            str,
            str
        ] = {}

        self.identity_projection_field: Dict[
            str,
            str
        ] = {}

        self.mutation_projection_field: Dict[
            str,
            str
        ] = {}

    # ========================================================
    # REGISTER
    # ========================================================

    def register_projection(
        self,
        projection: HHSReplayProjection,
    ) -> bool:
        """
        Register replay-native manifold projection.
        """

        if not projection.validate():
            return False

        self.replay_registry[
            projection.projection_id
        ] = projection

        if (
            projection.projection_id
            not in self.replay_lineage
        ):

            self.replay_lineage[
                projection.projection_id
            ] = []

        self.replay_lineage[
            projection.projection_id
        ].append(
            projection.closure_hash216()
        )

        self.workspace_projection_field[
            projection.projection_id
        ] = (
            projection.workspace_projection_hash216
        )

        self.transport_projection_field[
            projection.projection_id
        ] = (
            projection.transport_projection_hash216
        )

        self.identity_projection_field[
            projection.projection_id
        ] = (
            projection.identity_chain_hash216
        )

        self.mutation_projection_field[
            projection.projection_id
        ] = (
            projection.mutation_chain_hash216
        )

        return True

    # ========================================================
    # FIELD VALIDATION
    # ========================================================

    def validate_field(
        self,
    ) -> bool:
        """
        Universal replay continuity validation.
        """

        for projection in (
            self.replay_registry.values()
        ):

            if not projection.validate():
                return False

        return True

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global replay field closure.
        """

        payload = {
            "replay_registry": sorted(
                [
                    projection.closure_hash216()
                    for projection in (
                        self.replay_registry.values()
                    )
                ]
            ),
            "lineage": self.replay_lineage,
            "workspace": (
                self.workspace_projection_field
            ),
            "transport": (
                self.transport_projection_field
            ),
            "identity": (
                self.identity_projection_field
            ),
            "mutation": (
                self.mutation_projection_field
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # REPLAY EQUIVALENCE
    # ========================================================

    def replay_equivalent(
        self,
    ) -> bool:
        """
        Universal replay manifold equivalence.
        """

        for projection in (
            self.replay_registry.values()
        ):

            if not (
                projection.verify_replay_equivalence()
            ):
                return False

        return True

    # ========================================================
    # TOPOLOGY EQUIVALENCE
    # ========================================================

    def topology_equivalent(
        self,
    ) -> bool:
        """
        Recursive replay topology continuity.
        """

        for projection in (
            self.replay_registry.values()
        ):

            if not (
                projection.verify_topology_equivalence()
            ):
                return False

        return True

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def reconstructible(
        self,
    ) -> bool:
        """
        Canonical replay reconstruction invariant.
        """

        for projection in (
            self.replay_registry.values()
        ):

            if not (
                projection.verify_reconstructibility()
            ):
                return False

        return True

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical replay field receipt.
        """

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "projection_count": len(
                self.replay_registry
            ),
            "reconstructible": (
                self.reconstructible()
            ),
            "replay_equivalent": (
                self.replay_equivalent()
            ),
            "topology_equivalent": (
                self.topology_equivalent()
            ),
            "valid": (
                self.validate_field()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }