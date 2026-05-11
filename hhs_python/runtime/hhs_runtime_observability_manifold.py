# hhs_python/runtime/hhs_runtime_observability_manifold.py
#
# HHS / HARMONICODE
# Runtime Observability Manifold
#
# Canonical Runtime OS Introspection Geometry Layer
#
# Runtime Principle:
#
#   observability
#   =
#   reconstructible invariant topology introspection
#
# NOT:
#
#   logs / metrics / traces
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward observability traversal
#   v^72 = reciprocal observability reconstruction
#   C^216 = introspection topology closure
#
# Runtime Primitive:
#
#   reconstructible invariant topology introspection
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
# OBSERVABILITY WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSObservabilityWitness:
    """
    Canonical introspection witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    observable: bool = True
    reconstructible: bool = True
    diagnostic_equivalent: bool = True
    causally_equivalent: bool = True
    temporally_equivalent: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.observable
            and self.reconstructible
            and self.diagnostic_equivalent
            and self.causally_equivalent
            and self.temporally_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# OBSERVABILITY PROJECTION
# ============================================================

@dataclass(frozen=True)
class HHSObservabilityProjection:
    """
    Canonical introspection manifold carrier.

    Diagnostics are:
        invariant topology projections.
    """

    projection_id: str

    # ========================================================
    # MANIFOLD FIELDS
    # ========================================================

    drift_hash216: str
    replay_hash216: str
    semantic_hash216: str
    causal_hash216: str
    temporal_hash216: str
    consensus_hash216: str
    multimodal_hash216: str

    # ========================================================
    # OBSERVABILITY TRAVERSAL
    # ========================================================

    forward_observability_hash216: str
    reciprocal_observability_hash216: str

    # ========================================================
    # TOPOLOGY
    # ========================================================

    observability_topology_hash216: str

    # ========================================================
    # FLAGS
    # ========================================================

    observable: bool = True
    reconstructible: bool = True
    diagnostic_equivalent: bool = True
    causally_equivalent: bool = True
    temporally_equivalent: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    drift_witness: Optional[
        HHSObservabilityWitness
    ] = None

    replay_witness: Optional[
        HHSObservabilityWitness
    ] = None

    semantic_witness: Optional[
        HHSObservabilityWitness
    ] = None

    causal_witness: Optional[
        HHSObservabilityWitness
    ] = None

    reciprocal_witness: Optional[
        HHSObservabilityWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    projection_proof_hash216: str = ""

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
        Universal introspection admissibility validation.
        """

        if not self.observable:
            return False

        if not self.reconstructible:
            return False

        if not self.diagnostic_equivalent:
            return False

        if not self.causally_equivalent:
            return False

        if not self.temporally_equivalent:
            return False

        witnesses = [
            self.drift_witness,
            self.replay_witness,
            self.semantic_witness,
            self.causal_witness,
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
        Canonical observability closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "projection_id": self.projection_id,
            "drift": self.drift_hash216,
            "replay": self.replay_hash216,
            "semantic": self.semantic_hash216,
            "causal": self.causal_hash216,
            "temporal": self.temporal_hash216,
            "consensus": self.consensus_hash216,
            "multimodal": self.multimodal_hash216,
            "forward": (
                self.forward_observability_hash216
            ),
            "reciprocal": (
                self.reciprocal_observability_hash216
            ),
            "topology": (
                self.observability_topology_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # OBSERVABLE
    # ========================================================

    def verify_observable(
        self,
    ) -> bool:
        """
        Runtime introspection invariant.
        """

        return (
            self.observable
            and self.validate()
        )

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def verify_reconstructibility(
        self,
    ) -> bool:
        """
        Introspection reconstruction invariant.
        """

        return (
            self.reconstructible
            and self.validate()
        )

    # ========================================================
    # DIAGNOSTIC EQUIVALENCE
    # ========================================================

    def verify_diagnostic_equivalence(
        self,
    ) -> bool:
        """
        Diagnostic topology continuity invariant.
        """

        return (
            self.diagnostic_equivalent
            and self.validate()
        )

    # ========================================================
    # CAUSAL EQUIVALENCE
    # ========================================================

    def verify_causal_equivalence(
        self,
    ) -> bool:
        """
        Causal diagnostic continuity invariant.
        """

        return (
            self.causally_equivalent
            and self.validate()
        )

    # ========================================================
    # TEMPORAL EQUIVALENCE
    # ========================================================

    def verify_temporal_equivalence(
        self,
    ) -> bool:
        """
        Temporal diagnostic continuity invariant.
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
            "projection_id": self.projection_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "projection_proof_hash216": (
                self.projection_proof_hash216
            ),
            "observable": (
                self.verify_observable()
            ),
            "reconstructible": (
                self.verify_reconstructibility()
            ),
            "diagnostic_equivalent": (
                self.verify_diagnostic_equivalence()
            ),
            "causally_equivalent": (
                self.verify_causal_equivalence()
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
        Canonical observability projection receipt.
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
# RUNTIME OBSERVABILITY MANIFOLD
# ============================================================

class HHSRuntimeObservabilityManifold:
    """
    Canonical Runtime OS introspection geometry field.

    Observability is:
        reconstructible invariant topology introspection.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.projection_registry: Dict[
            str,
            HHSObservabilityProjection
        ] = {}

        self.projection_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.projection_dependencies: Dict[
            str,
            Set[str]
        ] = {}

        self.drift_field: Dict[
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

    # ========================================================
    # REGISTER PROJECTION
    # ========================================================

    def register_projection(
        self,
        projection: HHSObservabilityProjection,
    ) -> bool:
        """
        Register observable invariant topology projection.
        """

        if not projection.validate():
            return False

        self.projection_registry[
            projection.projection_id
        ] = projection

        if (
            projection.projection_id
            not in self.projection_lineage
        ):

            self.projection_lineage[
                projection.projection_id
            ] = []

        self.projection_lineage[
            projection.projection_id
        ].append(
            projection.closure_hash216()
        )

        self.drift_field[
            projection.projection_id
        ] = (
            projection.drift_hash216
        )

        self.replay_field[
            projection.projection_id
        ] = (
            projection.replay_hash216
        )

        self.semantic_field[
            projection.projection_id
        ] = (
            projection.semantic_hash216
        )

        self.causal_field[
            projection.projection_id
        ] = (
            projection.causal_hash216
        )

        self.temporal_field[
            projection.projection_id
        ] = (
            projection.temporal_hash216
        )

        self.consensus_field[
            projection.projection_id
        ] = (
            projection.consensus_hash216
        )

        self.multimodal_field[
            projection.projection_id
        ] = (
            projection.multimodal_hash216
        )

        if (
            projection.projection_id
            not in self.projection_dependencies
        ):

            self.projection_dependencies[
                projection.projection_id
            ] = set()

        return True

    # ========================================================
    # PROJECTION DEPENDENCY
    # ========================================================

    def connect_projection_dependency(
        self,
        source_projection: str,
        target_projection: str,
    ) -> bool:
        """
        Establish observability dependency relation.
        """

        if (
            source_projection
            not in self.projection_registry
        ):
            return False

        if (
            target_projection
            not in self.projection_registry
        ):
            return False

        self.projection_dependencies[
            source_projection
        ].add(
            target_projection
        )

        return True

    # ========================================================
    # VALIDATE MANIFOLD
    # ========================================================

    def validate_manifold(
        self,
    ) -> bool:
        """
        Universal observability validation.
        """

        for projection in (
            self.projection_registry.values()
        ):

            if not projection.validate():
                return False

        return True

    # ========================================================
    # OBSERVABLE
    # ========================================================

    def observable(
        self,
    ) -> bool:
        """
        Global invariant observability continuity.
        """

        for projection in (
            self.projection_registry.values()
        ):

            if not (
                projection.verify_observable()
            ):
                return False

        return True

    # ========================================================
    # PROJECTION CONE
    # ========================================================

    def projection_cone(
        self,
        projection_id: str,
    ) -> Set[str]:
        """
        Compute full introspection dependency cone.
        """

        visited: Set[str] = set()

        def walk(node: str):

            if node in visited:
                return

            visited.add(node)

            for nxt in (
                self.projection_dependencies.get(
                    node,
                    set(),
                )
            ):
                walk(nxt)

        walk(projection_id)

        return visited

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global observability manifold closure.
        """

        payload = {
            "projection_registry": sorted(
                [
                    projection.closure_hash216()
                    for projection in (
                        self.projection_registry.values()
                    )
                ]
            ),
            "lineage": self.projection_lineage,
            "dependencies": {
                k: sorted(list(v))
                for k, v in (
                    self.projection_dependencies.items()
                )
            },
            "drift": self.drift_field,
            "replay": self.replay_field,
            "semantic": self.semantic_field,
            "causal": self.causal_field,
            "temporal": self.temporal_field,
            "consensus": self.consensus_field,
            "multimodal": self.multimodal_field,
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # AUTHORITATIVE PROJECTION
    # ========================================================

    def authoritative_projection(
        self,
    ) -> Optional[
        HHSObservabilityProjection
    ]:
        """
        Determine projection closest
        to introspection closure equivalence.
        """

        if not self.projection_registry:
            return None

        ordered = sorted(
            self.projection_registry.values(),
            key=lambda p: (
                p.closure_hash216(),
                p.observability_topology_hash216,
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
        Canonical observability manifold receipt.
        """

        authoritative = (
            self.authoritative_projection()
        )

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "projection_count": len(
                self.projection_registry
            ),
            "dependency_count": sum(
                len(v)
                for v in (
                    self.projection_dependencies.values()
                )
            ),
            "observable": (
                self.observable()
            ),
            "authoritative_projection": (
                authoritative.projection_id
                if authoritative
                else None
            ),
            "valid": (
                self.validate_manifold()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }