# hhs_python/runtime/hhs_runtime_identity_field.py
#
# HHS / HARMONICODE
# Runtime Identity Field
#
# Canonical Runtime OS Identity Conservation Layer
#
# Runtime Principle:
#
#   identity
#   =
#   reconstructible causality continuity
#
# NOT:
#
#   object pointer continuity
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward identity traversal
#   v^72 = reciprocal identity reconstruction
#   C^216 = globally conserved identity closure
#
# Runtime Primitive:
#
#   conserved reconstructible causality identity
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
# IDENTITY WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSIdentityWitness:
    """
    Canonical identity continuity witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    reconstructible: bool = True
    readable: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.reconstructible
            and self.readable
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# RUNTIME IDENTITY
# ============================================================

@dataclass(frozen=True)
class HHSRuntimeIdentity:
    """
    Canonical conserved identity carrier.

    Runtime identity is:
        reconstructible continuity closure
    """

    identity_id: str

    # ========================================================
    # TERNARY RECIPROCAL ANCHORS
    # ========================================================

    seed_hash216: str
    state_hash216: str
    receipt_hash216: str

    # ========================================================
    # IDENTITY PROJECTIONS
    # ========================================================

    forward_identity_hash216: str
    reciprocal_identity_hash216: str

    topology_identity_hash216: str
    replay_identity_hash216: str
    workspace_identity_hash216: str
    transport_identity_hash216: str

    # ========================================================
    # CONTINUITY FLAGS
    # ========================================================

    identity_continuous: bool = True
    reconstructible: bool = True
    globally_readable: bool = True
    replay_equivalent: bool = True
    topology_equivalent: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    topology_witness: Optional[
        HHSIdentityWitness
    ] = None

    replay_witness: Optional[
        HHSIdentityWitness
    ] = None

    readability_witness: Optional[
        HHSIdentityWitness
    ] = None

    reciprocal_witness: Optional[
        HHSIdentityWitness
    ] = None

    # ========================================================
    # IDENTITY PROOF
    # ========================================================

    identity_proof_hash216: str = ""

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
        Universal identity admissibility.
        """

        if not self.identity_continuous:
            return False

        if not self.reconstructible:
            return False

        if not self.globally_readable:
            return False

        if not self.replay_equivalent:
            return False

        if not self.topology_equivalent:
            return False

        witnesses = [
            self.topology_witness,
            self.replay_witness,
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
        Canonical identity closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "identity_id": self.identity_id,
            "seed": self.seed_hash216,
            "state": self.state_hash216,
            "receipt": self.receipt_hash216,
            "forward": self.forward_identity_hash216,
            "reciprocal": self.reciprocal_identity_hash216,
            "topology": self.topology_identity_hash216,
            "replay": self.replay_identity_hash216,
            "workspace": self.workspace_identity_hash216,
            "transport": self.transport_identity_hash216,
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # CONTINUITY
    # ========================================================

    def verify_continuity(
        self,
    ) -> bool:
        """
        Canonical identity continuity invariant.
        """

        return (
            self.identity_continuous
            and self.validate()
        )

    # ========================================================
    # RECONSTRUCTION
    # ========================================================

    def verify_reconstructibility(
        self,
    ) -> bool:
        """
        Identity reconstruction invariant.
        """

        return (
            self.reconstructible
            and self.validate()
        )

    # ========================================================
    # READABILITY
    # ========================================================

    def verify_global_readability(
        self,
    ) -> bool:
        """
        Semantic continuity invariant.
        """

        return (
            self.globally_readable
            and self.validate()
        )

    # ========================================================
    # REPLAY
    # ========================================================

    def verify_replay_equivalence(
        self,
    ) -> bool:
        """
        Replay-native identity equivalence.
        """

        return (
            self.replay_equivalent
            and self.validate()
        )

    # ========================================================
    # TOPOLOGY
    # ========================================================

    def verify_topology_equivalence(
        self,
    ) -> bool:
        """
        Recursive topology continuity invariant.
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
            "identity_id": self.identity_id,
            "closure_hash216": self.closure_hash216(),
            "identity_proof_hash216": (
                self.identity_proof_hash216
            ),
            "continuous": (
                self.verify_continuity()
            ),
            "reconstructible": (
                self.verify_reconstructibility()
            ),
            "globally_readable": (
                self.verify_global_readability()
            ),
            "replay_equivalent": (
                self.verify_replay_equivalence()
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
        Canonical identity continuity receipt.
        """

        return {
            "identity_id": self.identity_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "identity_proof_hash216": (
                self.identity_proof_hash216
            ),
            "continuous": (
                self.identity_continuous
            ),
            "reconstructible": (
                self.reconstructible
            ),
            "valid": (
                self.validate()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# IDENTITY FIELD
# ============================================================

class HHSRuntimeIdentityField:
    """
    Canonical Runtime OS conserved identity field.

    Runtime identity is:
        a persistent manifold continuity excitation.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.identity_registry: Dict[
            str,
            HHSRuntimeIdentity
        ] = {}

        self.identity_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.identity_projection_field: Dict[
            str,
            str
        ] = {}

        self.identity_transport_field: Dict[
            str,
            str
        ] = {}

        self.identity_workspace_field: Dict[
            str,
            str
        ] = {}

        self.identity_replay_field: Dict[
            str,
            str
        ] = {}

    # ========================================================
    # REGISTER
    # ========================================================

    def register_identity(
        self,
        identity: HHSRuntimeIdentity,
    ) -> bool:
        """
        Register conserved runtime identity.
        """

        if not identity.validate():
            return False

        self.identity_registry[
            identity.identity_id
        ] = identity

        if (
            identity.identity_id
            not in self.identity_lineage
        ):

            self.identity_lineage[
                identity.identity_id
            ] = []

        self.identity_lineage[
            identity.identity_id
        ].append(
            identity.closure_hash216()
        )

        self.identity_projection_field[
            identity.identity_id
        ] = (
            identity.topology_identity_hash216
        )

        self.identity_transport_field[
            identity.identity_id
        ] = (
            identity.transport_identity_hash216
        )

        self.identity_workspace_field[
            identity.identity_id
        ] = (
            identity.workspace_identity_hash216
        )

        self.identity_replay_field[
            identity.identity_id
        ] = (
            identity.replay_identity_hash216
        )

        return True

    # ========================================================
    # FIELD VALIDATION
    # ========================================================

    def validate_field(
        self,
    ) -> bool:
        """
        Universal identity conservation validation.
        """

        for identity in (
            self.identity_registry.values()
        ):

            if not identity.validate():
                return False

        return True

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global identity field closure.
        """

        payload = {
            "identities": sorted(
                [
                    identity.closure_hash216()
                    for identity in (
                        self.identity_registry.values()
                    )
                ]
            ),
            "lineage": self.identity_lineage,
            "projection": (
                self.identity_projection_field
            ),
            "transport": (
                self.identity_transport_field
            ),
            "workspace": (
                self.identity_workspace_field
            ),
            "replay": (
                self.identity_replay_field
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
        Canonical identity field receipt.
        """

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "identity_count": len(
                self.identity_registry
            ),
            "valid": (
                self.validate_field()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }