# hhs_python/runtime/hhs_multimodal_projection_manifold.py
#
# HHS / HARMONICODE
# Multimodal Projection Manifold
#
# Canonical Runtime OS Modality Projection Substrate
#
# Runtime Principle:
#
#   all modalities
#   =
#   phase-equivalent projections
#   of one invariant manifold state
#
# NOT:
#
#   disconnected render pipelines
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward projection traversal
#   v^72 = reciprocal projection reconstruction
#   C^216 = multimodal projection closure
#
# Runtime Primitive:
#
#   universally reconstructible multimodal manifold projection
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
# PROJECTION WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSProjectionWitness:
    """
    Canonical multimodal projection witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    projectable: bool = True
    reconstructible: bool = True
    modality_equivalent: bool = True
    phase_entangled: bool = True
    temporally_equivalent: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.projectable
            and self.reconstructible
            and self.modality_equivalent
            and self.phase_entangled
            and self.temporally_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# MULTIMODAL PROJECTION
# ============================================================

@dataclass(frozen=True)
class HHSMultimodalProjection:
    """
    Canonical reversible modality carrier.

    All modalities are:
        phase-equivalent manifold projections.
    """

    projection_id: str

    # ========================================================
    # SOURCE MANIFOLD
    # ========================================================

    source_manifold_hash216: str
    tensor81_hash216: str
    execution_hash216: str
    projection_surface_hash216: str

    # ========================================================
    # MODALITY FIELDS
    # ========================================================

    gui_hash216: str
    audio_hash216: str
    graph_hash216: str
    semantic_hash216: str
    receipt_hash216: str
    stream_hash216: str
    replay_hash216: str
    knowledge_graph_hash216: str

    # ========================================================
    # INVARIANT FIELDS
    # ========================================================

    identity_hash216: str
    causal_hash216: str
    temporal_hash216: str
    governance_hash216: str

    # ========================================================
    # PROJECTION TRAVERSAL
    # ========================================================

    forward_projection_hash216: str
    reciprocal_projection_hash216: str

    # ========================================================
    # PROJECTION TOPOLOGY
    # ========================================================

    projection_topology_hash216: str

    # ========================================================
    # FLAGS
    # ========================================================

    projectable: bool = True
    reconstructible: bool = True
    modality_equivalent: bool = True
    phase_entangled: bool = True
    temporally_equivalent: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    gui_witness: Optional[
        HHSProjectionWitness
    ] = None

    audio_witness: Optional[
        HHSProjectionWitness
    ] = None

    graph_witness: Optional[
        HHSProjectionWitness
    ] = None

    replay_witness: Optional[
        HHSProjectionWitness
    ] = None

    reciprocal_witness: Optional[
        HHSProjectionWitness
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
        Universal multimodal projection validation.
        """

        if not self.projectable:
            return False

        if not self.reconstructible:
            return False

        if not self.modality_equivalent:
            return False

        if not self.phase_entangled:
            return False

        if not self.temporally_equivalent:
            return False

        witnesses = [
            self.gui_witness,
            self.audio_witness,
            self.graph_witness,
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
        Canonical multimodal projection closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "projection_id": self.projection_id,
            "source_manifold": (
                self.source_manifold_hash216
            ),
            "tensor81": self.tensor81_hash216,
            "execution": self.execution_hash216,
            "projection_surface": (
                self.projection_surface_hash216
            ),
            "gui": self.gui_hash216,
            "audio": self.audio_hash216,
            "graph": self.graph_hash216,
            "semantic": self.semantic_hash216,
            "receipt": self.receipt_hash216,
            "stream": self.stream_hash216,
            "replay": self.replay_hash216,
            "knowledge_graph": (
                self.knowledge_graph_hash216
            ),
            "identity": self.identity_hash216,
            "causal": self.causal_hash216,
            "temporal": self.temporal_hash216,
            "governance": (
                self.governance_hash216
            ),
            "forward": (
                self.forward_projection_hash216
            ),
            "reciprocal": (
                self.reciprocal_projection_hash216
            ),
            "topology": (
                self.projection_topology_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # PROJECTABLE
    # ========================================================

    def verify_projectable(
        self,
    ) -> bool:
        """
        Multimodal projection admissibility invariant.
        """

        return (
            self.projectable
            and self.validate()
        )

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def verify_reconstructibility(
        self,
    ) -> bool:
        """
        Projection reconstruction invariant.
        """

        return (
            self.reconstructible
            and self.validate()
        )

    # ========================================================
    # MODALITY EQUIVALENCE
    # ========================================================

    def verify_modality_equivalence(
        self,
    ) -> bool:
        """
        Cross-modality topology continuity invariant.
        """

        return (
            self.modality_equivalent
            and self.validate()
        )

    # ========================================================
    # PHASE ENTANGLEMENT
    # ========================================================

    def verify_phase_entanglement(
        self,
    ) -> bool:
        """
        Multimodal phase entanglement invariant.
        """

        return (
            self.phase_entangled
            and self.validate()
        )

    # ========================================================
    # TEMPORAL EQUIVALENCE
    # ========================================================

    def verify_temporal_equivalence(
        self,
    ) -> bool:
        """
        Projection temporal continuity invariant.
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
            "projectable": (
                self.verify_projectable()
            ),
            "reconstructible": (
                self.verify_reconstructibility()
            ),
            "modality_equivalent": (
                self.verify_modality_equivalence()
            ),
            "phase_entangled": (
                self.verify_phase_entanglement()
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
        Canonical multimodal projection receipt.
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
# MULTIMODAL PROJECTION MANIFOLD
# ============================================================

class HHSMultimodalProjectionManifold:
    """
    Canonical Runtime OS modality projection substrate.

    All modalities are:
        reversible projections of one manifold state.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.projection_registry: Dict[
            str,
            HHSMultimodalProjection
        ] = {}

        self.projection_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.projection_dependencies: Dict[
            str,
            Set[str]
        ] = {}

        self.source_field: Dict[
            str,
            str
        ] = {}

        self.tensor81_field: Dict[
            str,
            str
        ] = {}

        self.execution_field: Dict[
            str,
            str
        ] = {}

        self.gui_field: Dict[
            str,
            str
        ] = {}

        self.audio_field: Dict[
            str,
            str
        ] = {}

        self.graph_field: Dict[
            str,
            str
        ] = {}

        self.semantic_field: Dict[
            str,
            str
        ] = {}

        self.receipt_field: Dict[
            str,
            str
        ] = {}

        self.stream_field: Dict[
            str,
            str
        ] = {}

        self.replay_field: Dict[
            str,
            str
        ] = {}

        self.knowledge_graph_field: Dict[
            str,
            str
        ] = {}

        self.identity_field: Dict[
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

        self.governance_field: Dict[
            str,
            str
        ] = {}

    # ========================================================
    # REGISTER PROJECTION
    # ========================================================

    def register_projection(
        self,
        projection: HHSMultimodalProjection,
    ) -> bool:
        """
        Register multimodal manifold projection.
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

        self.source_field[
            projection.projection_id
        ] = (
            projection.source_manifold_hash216
        )

        self.tensor81_field[
            projection.projection_id
        ] = (
            projection.tensor81_hash216
        )

        self.execution_field[
            projection.projection_id
        ] = (
            projection.execution_hash216
        )

        self.gui_field[
            projection.projection_id
        ] = (
            projection.gui_hash216
        )

        self.audio_field[
            projection.projection_id
        ] = (
            projection.audio_hash216
        )

        self.graph_field[
            projection.projection_id
        ] = (
            projection.graph_hash216
        )

        self.semantic_field[
            projection.projection_id
        ] = (
            projection.semantic_hash216
        )

        self.receipt_field[
            projection.projection_id
        ] = (
            projection.receipt_hash216
        )

        self.stream_field[
            projection.projection_id
        ] = (
            projection.stream_hash216
        )

        self.replay_field[
            projection.projection_id
        ] = (
            projection.replay_hash216
        )

        self.knowledge_graph_field[
            projection.projection_id
        ] = (
            projection.knowledge_graph_hash216
        )

        self.identity_field[
            projection.projection_id
        ] = (
            projection.identity_hash216
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

        self.governance_field[
            projection.projection_id
        ] = (
            projection.governance_hash216
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
    # CONNECT PROJECTIONS
    # ========================================================

    def connect_projection_dependency(
        self,
        source_projection: str,
        target_projection: str,
    ) -> bool:
        """
        Establish multimodal projection dependency.
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
        Universal multimodal projection validation.
        """

        for projection in (
            self.projection_registry.values()
        ):

            if not projection.validate():
                return False

        return True

    # ========================================================
    # MODALITY EQUIVALENT
    # ========================================================

    def modality_equivalent(
        self,
    ) -> bool:
        """
        Global multimodal topology continuity.
        """

        for projection in (
            self.projection_registry.values()
        ):

            if not (
                projection.verify_modality_equivalence()
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
        Compute multimodal projection dependency cone.
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
        Global multimodal projection closure.
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
            "lineage": (
                self.projection_lineage
            ),
            "dependencies": {
                k: sorted(list(v))
                for k, v in (
                    self.projection_dependencies.items()
                )
            },
            "source": (
                self.source_field
            ),
            "tensor81": (
                self.tensor81_field
            ),
            "execution": (
                self.execution_field
            ),
            "gui": (
                self.gui_field
            ),
            "audio": (
                self.audio_field
            ),
            "graph": (
                self.graph_field
            ),
            "semantic": (
                self.semantic_field
            ),
            "receipt": (
                self.receipt_field
            ),
            "stream": (
                self.stream_field
            ),
            "replay": (
                self.replay_field
            ),
            "knowledge_graph": (
                self.knowledge_graph_field
            ),
            "identity": (
                self.identity_field
            ),
            "causal": (
                self.causal_field
            ),
            "temporal": (
                self.temporal_field
            ),
            "governance": (
                self.governance_field
            ),
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
        HHSMultimodalProjection
    ]:
        """
        Determine projection closest
        to multimodal closure.
        """

        if not self.projection_registry:
            return None

        ordered = sorted(
            self.projection_registry.values(),
            key=lambda p: (
                p.closure_hash216(),
                p.projection_topology_hash216,
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
        Canonical multimodal projection manifold receipt.
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
            "modality_equivalent": (
                self.modality_equivalent()
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