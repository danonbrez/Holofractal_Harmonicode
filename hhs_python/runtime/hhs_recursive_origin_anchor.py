# hhs_python/runtime/hhs_recursive_origin_anchor.py
#
# HHS / HARMONICODE
# Recursive Origin Anchor
#
# Canonical Runtime OS Recursive Continuity Substrate
#
# Runtime Principle:
#
#   identity
#   =
#   reconstructible recursive origin topology
#
# NOT:
#
#   persistent runtime identifiers
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward origin traversal
#   v^72 = reciprocal origin reconstruction
#   C^216 = recursive invariant-origin closure
#
# Runtime Primitive:
#
#   recursive invariant-origin continuity
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
# ORIGIN WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSOriginWitness:
    """
    Canonical recursive-origin continuity witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    anchored: bool = True
    reconstructible: bool = True
    origin_equivalent: bool = True
    future_equivalent: bool = True
    temporally_equivalent: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.anchored
            and self.reconstructible
            and self.origin_equivalent
            and self.future_equivalent
            and self.temporally_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# RECURSIVE ORIGIN
# ============================================================

@dataclass(frozen=True)
class HHSRecursiveOrigin:
    """
    Canonical invariant-origin carrier.

    Identity is:
        reconstructible recursive origin topology.
    """

    origin_id: str

    # ========================================================
    # ORIGIN FIELDS
    # ========================================================

    seed_hash216: str
    origin_hash216: str
    identity_hash216: str
    replay_hash216: str
    semantic_hash216: str
    causal_hash216: str
    temporal_hash216: str
    consensus_hash216: str
    multimodal_hash216: str
    governance_hash216: str

    # ========================================================
    # ORIGIN TRAVERSAL
    # ========================================================

    forward_origin_hash216: str
    reciprocal_origin_hash216: str

    # ========================================================
    # ORIGIN TOPOLOGY
    # ========================================================

    origin_topology_hash216: str

    # ========================================================
    # FLAGS
    # ========================================================

    anchored: bool = True
    reconstructible: bool = True
    origin_equivalent: bool = True
    future_equivalent: bool = True
    temporally_equivalent: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    seed_witness: Optional[
        HHSOriginWitness
    ] = None

    origin_witness: Optional[
        HHSOriginWitness
    ] = None

    replay_witness: Optional[
        HHSOriginWitness
    ] = None

    governance_witness: Optional[
        HHSOriginWitness
    ] = None

    reciprocal_witness: Optional[
        HHSOriginWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    origin_proof_hash216: str = ""

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
        Universal recursive-origin validation.
        """

        if not self.anchored:
            return False

        if not self.reconstructible:
            return False

        if not self.origin_equivalent:
            return False

        if not self.future_equivalent:
            return False

        if not self.temporally_equivalent:
            return False

        witnesses = [
            self.seed_witness,
            self.origin_witness,
            self.replay_witness,
            self.governance_witness,
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
        Canonical recursive-origin closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "origin_id": self.origin_id,
            "seed": self.seed_hash216,
            "origin": self.origin_hash216,
            "identity": self.identity_hash216,
            "replay": self.replay_hash216,
            "semantic": self.semantic_hash216,
            "causal": self.causal_hash216,
            "temporal": self.temporal_hash216,
            "consensus": self.consensus_hash216,
            "multimodal": self.multimodal_hash216,
            "governance": self.governance_hash216,
            "forward": (
                self.forward_origin_hash216
            ),
            "reciprocal": (
                self.reciprocal_origin_hash216
            ),
            "topology": (
                self.origin_topology_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # ANCHORED
    # ========================================================

    def verify_anchored(
        self,
    ) -> bool:
        """
        Recursive-origin anchoring invariant.
        """

        return (
            self.anchored
            and self.validate()
        )

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def verify_reconstructibility(
        self,
    ) -> bool:
        """
        Origin reconstruction invariant.
        """

        return (
            self.reconstructible
            and self.validate()
        )

    # ========================================================
    # ORIGIN EQUIVALENCE
    # ========================================================

    def verify_origin_equivalence(
        self,
    ) -> bool:
        """
        Recursive-origin continuity invariant.
        """

        return (
            self.origin_equivalent
            and self.validate()
        )

    # ========================================================
    # FUTURE EQUIVALENCE
    # ========================================================

    def verify_future_equivalence(
        self,
    ) -> bool:
        """
        Future-topology inheritance invariant.
        """

        return (
            self.future_equivalent
            and self.validate()
        )

    # ========================================================
    # TEMPORAL EQUIVALENCE
    # ========================================================

    def verify_temporal_equivalence(
        self,
    ) -> bool:
        """
        Temporal origin continuity invariant.
        """

        return (
            self.temporally_equivalent
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
            "origin_id": self.origin_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "origin_proof_hash216": (
                self.origin_proof_hash216
            ),
            "anchored": (
                self.verify_anchored()
            ),
            "reconstructible": (
                self.verify_reconstructibility()
            ),
            "origin_equivalent": (
                self.verify_origin_equivalence()
            ),
            "future_equivalent": (
                self.verify_future_equivalence()
            ),
            "temporally_equivalent": (
                self.verify_temporal_equivalence()
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
        Canonical recursive-origin receipt.
        """

        return {
            "origin_id": self.origin_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "origin_proof_hash216": (
                self.origin_proof_hash216
            ),
            "valid": (
                self.validate()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# RECURSIVE ORIGIN ANCHOR
# ============================================================

class HHSRecursiveOriginAnchor:
    """
    Canonical Runtime OS recursive continuity substrate.

    Identity is:
        reconstructible recursive origin topology.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.origin_registry: Dict[
            str,
            HHSRecursiveOrigin
        ] = {}

        self.origin_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.origin_dependencies: Dict[
            str,
            Set[str]
        ] = {}

        self.seed_field: Dict[
            str,
            str
        ] = {}

        self.origin_field: Dict[
            str,
            str
        ] = {}

        self.identity_field: Dict[
            str,
            str
        ] = {}

        self.replay_field: Dict[
            str,
            str
        ] = {}

        self.semantic_field: Dict[
            str,
            str
        ] = {}

        self.causal_field: Dict[
            str,
            str
        ] = {}

        self.temporal_field: Dict[
            str,
            str
        ] = {}

        self.consensus_field: Dict[
            str,
            str
        ] = {}

        self.multimodal_field: Dict[
            str,
            str
        ] = {}

        self.governance_field: Dict[
            str,
            str
        ] = {}

    # ========================================================
    # REGISTER ORIGIN
    # ========================================================

    def register_origin(
        self,
        origin: HHSRecursiveOrigin,
    ) -> bool:
        """
        Register recursive invariant origin.
        """

        if not origin.validate():
            return False

        self.origin_registry[
            origin.origin_id
        ] = origin

        if (
            origin.origin_id
            not in self.origin_lineage
        ):

            self.origin_lineage[
                origin.origin_id
            ] = []

        self.origin_lineage[
            origin.origin_id
        ].append(
            origin.closure_hash216()
        )

        self.seed_field[
            origin.origin_id
        ] = (
            origin.seed_hash216
        )

        self.origin_field[
            origin.origin_id
        ] = (
            origin.origin_hash216
        )

        self.identity_field[
            origin.origin_id
        ] = (
            origin.identity_hash216
        )

        self.replay_field[
            origin.origin_id
        ] = (
            origin.replay_hash216
        )

        self.semantic_field[
            origin.origin_id
        ] = (
            origin.semantic_hash216
        )

        self.causal_field[
            origin.origin_id
        ] = (
            origin.causal_hash216
        )

        self.temporal_field[
            origin.origin_id
        ] = (
            origin.temporal_hash216
        )

        self.consensus_field[
            origin.origin_id
        ] = (
            origin.consensus_hash216
        )

        self.multimodal_field[
            origin.origin_id
        ] = (
            origin.multimodal_hash216
        )

        self.governance_field[
            origin.origin_id
        ] = (
            origin.governance_hash216
        )

        if (
            origin.origin_id
            not in self.origin_dependencies
        ):

            self.origin_dependencies[
                origin.origin_id
            ] = set()

        return True

    # ========================================================
    # ORIGIN DEPENDENCY
    # ========================================================

    def connect_origin_dependency(
        self,
        source_origin: str,
        target_origin: str,
    ) -> bool:
        """
        Establish recursive-origin dependency relation.
        """

        if (
            source_origin
            not in self.origin_registry
        ):
            return False

        if (
            target_origin
            not in self.origin_registry
        ):
            return False

        self.origin_dependencies[
            source_origin
        ].add(
            target_origin
        )

        return True

    # ========================================================
    # VALIDATE ANCHOR
    # ========================================================

    def validate_anchor(
        self,
    ) -> bool:
        """
        Universal recursive-origin validation.
        """

        for origin in (
            self.origin_registry.values()
        ):

            if not origin.validate():
                return False

        return True

    # ========================================================
    # ANCHORED
    # ========================================================

    def anchored(
        self,
    ) -> bool:
        """
        Global recursive-origin continuity.
        """

        for origin in (
            self.origin_registry.values()
        ):

            if not (
                origin.verify_anchored()
            ):
                return False

        return True

    # ========================================================
    # ORIGIN CONE
    # ========================================================

    def origin_cone(
        self,
        origin_id: str,
    ) -> Set[str]:
        """
        Compute full recursive-origin dependency cone.
        """

        visited: Set[str] = set()

        def walk(node: str):

            if node in visited:
                return

            visited.add(node)

            for nxt in (
                self.origin_dependencies.get(
                    node,
                    set(),
                )
            ):
                walk(nxt)

        walk(origin_id)

        return visited

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global recursive-origin closure.
        """

        payload = {
            "origin_registry": sorted(
                [
                    origin.closure_hash216()
                    for origin in (
                        self.origin_registry.values()
                    )
                ]
            ),
            "lineage": self.origin_lineage,
            "dependencies": {
                k: sorted(list(v))
                for k, v in (
                    self.origin_dependencies.items()
                )
            },
            "seed": self.seed_field,
            "origin": self.origin_field,
            "identity": self.identity_field,
            "replay": self.replay_field,
            "semantic": self.semantic_field,
            "causal": self.causal_field,
            "temporal": self.temporal_field,
            "consensus": self.consensus_field,
            "multimodal": self.multimodal_field,
            "governance": self.governance_field,
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # AUTHORITATIVE ORIGIN
    # ========================================================

    def authoritative_origin(
        self,
    ) -> Optional[
        HHSRecursiveOrigin
    ]:
        """
        Determine origin closest
        to recursive continuity closure.
        """

        if not self.origin_registry:
            return None

        ordered = sorted(
            self.origin_registry.values(),
            key=lambda o: (
                o.closure_hash216(),
                o.origin_topology_hash216,
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
        Canonical recursive-origin anchor receipt.
        """

        authoritative = (
            self.authoritative_origin()
        )

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "origin_count": len(
                self.origin_registry
            ),
            "dependency_count": sum(
                len(v)
                for v in (
                    self.origin_dependencies.values()
                )
            ),
            "anchored": (
                self.anchored()
            ),
            "authoritative_origin": (
                authoritative.origin_id
                if authoritative
                else None
            ),
            "valid": (
                self.validate_anchor()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }