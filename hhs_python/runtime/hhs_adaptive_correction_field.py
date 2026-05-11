# hhs_python/runtime/hhs_adaptive_correction_field.py
#
# HHS / HARMONICODE
# Adaptive Correction Field
#
# Canonical Runtime OS Self-Stabilization Geometry Layer
#
# Runtime Principle:
#
#   correction
#   =
#   reversible manifold attractor convergence
#
# NOT:
#
#   overwrite / rollback / forced synchronization
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward correction traversal
#   v^72 = reciprocal correction reconstruction
#   C^216 = adaptive manifold stabilization closure
#
# Runtime Primitive:
#
#   self-stabilizing invariant manifold attractor correction
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
# CORRECTION WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSCorrectionWitness:
    """
    Canonical adaptive stabilization witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    correctable: bool = True
    reconstructible: bool = True
    stabilized: bool = True
    causally_equivalent: bool = True
    temporally_equivalent: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.correctable
            and self.reconstructible
            and self.stabilized
            and self.causally_equivalent
            and self.temporally_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# ADAPTIVE CORRECTION
# ============================================================

@dataclass(frozen=True)
class HHSAdaptiveCorrection:
    """
    Canonical manifold stabilization carrier.

    Correction is:
        reversible attractor convergence.
    """

    correction_id: str

    # ========================================================
    # MANIFOLD FIELDS
    # ========================================================

    drift_hash216: str
    target_hash216: str
    replay_hash216: str
    semantic_hash216: str
    causal_hash216: str
    temporal_hash216: str
    consensus_hash216: str
    multimodal_hash216: str

    # ========================================================
    # CORRECTION TRAVERSAL
    # ========================================================

    forward_correction_hash216: str
    reciprocal_correction_hash216: str

    # ========================================================
    # STABILIZATION TOPOLOGY
    # ========================================================

    correction_topology_hash216: str

    # ========================================================
    # FLAGS
    # ========================================================

    correctable: bool = True
    reconstructible: bool = True
    stabilized: bool = True
    causally_equivalent: bool = True
    temporally_equivalent: bool = True

    # ========================================================
    # WITNESSES
    # ========================================================

    drift_witness: Optional[
        HHSCorrectionWitness
    ] = None

    replay_witness: Optional[
        HHSCorrectionWitness
    ] = None

    semantic_witness: Optional[
        HHSCorrectionWitness
    ] = None

    causal_witness: Optional[
        HHSCorrectionWitness
    ] = None

    reciprocal_witness: Optional[
        HHSCorrectionWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    correction_proof_hash216: str = ""

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
        Universal adaptive correction validation.
        """

        if not self.correctable:
            return False

        if not self.reconstructible:
            return False

        if not self.stabilized:
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
        Canonical correction closure operator.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "correction_id": self.correction_id,
            "drift": self.drift_hash216,
            "target": self.target_hash216,
            "replay": self.replay_hash216,
            "semantic": self.semantic_hash216,
            "causal": self.causal_hash216,
            "temporal": self.temporal_hash216,
            "consensus": self.consensus_hash216,
            "multimodal": self.multimodal_hash216,
            "forward": (
                self.forward_correction_hash216
            ),
            "reciprocal": (
                self.reciprocal_correction_hash216
            ),
            "topology": (
                self.correction_topology_hash216
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # CORRECTABLE
    # ========================================================

    def verify_correctable(
        self,
    ) -> bool:
        """
        Adaptive correction admissibility invariant.
        """

        return (
            self.correctable
            and self.validate()
        )

    # ========================================================
    # RECONSTRUCTIBILITY
    # ========================================================

    def verify_reconstructibility(
        self,
    ) -> bool:
        """
        Correction reconstruction invariant.
        """

        return (
            self.reconstructible
            and self.validate()
        )

    # ========================================================
    # STABILIZATION
    # ========================================================

    def verify_stabilization(
        self,
    ) -> bool:
        """
        Manifold attractor stabilization invariant.
        """

        return (
            self.stabilized
            and self.validate()
        )

    # ========================================================
    # CAUSAL EQUIVALENCE
    # ========================================================

    def verify_causal_equivalence(
        self,
    ) -> bool:
        """
        Causal correction continuity invariant.
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
        Temporal correction continuity invariant.
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
            "correction_id": self.correction_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "correction_proof_hash216": (
                self.correction_proof_hash216
            ),
            "correctable": (
                self.verify_correctable()
            ),
            "reconstructible": (
                self.verify_reconstructibility()
            ),
            "stabilized": (
                self.verify_stabilization()
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
        Canonical adaptive correction receipt.
        """

        return {
            "correction_id": self.correction_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "correction_proof_hash216": (
                self.correction_proof_hash216
            ),
            "valid": (
                self.validate()
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# ADAPTIVE CORRECTION FIELD
# ============================================================

class HHSAdaptiveCorrectionField:
    """
    Canonical Runtime OS self-stabilization geometry field.

    Correction is:
        invariant manifold attractor convergence.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.correction_registry: Dict[
            str,
            HHSAdaptiveCorrection
        ] = {}

        self.correction_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.correction_dependencies: Dict[
            str,
            Set[str]
        ] = {}

        self.drift_field: Dict[
            str,
            str
        ] = {}

        self.target_field: Dict[
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
    # REGISTER CORRECTION
    # ========================================================

    def register_correction(
        self,
        correction: HHSAdaptiveCorrection,
    ) -> bool:
        """
        Register adaptive manifold stabilization.
        """

        if not correction.validate():
            return False

        self.correction_registry[
            correction.correction_id
        ] = correction

        if (
            correction.correction_id
            not in self.correction_lineage
        ):

            self.correction_lineage[
                correction.correction_id
            ] = []

        self.correction_lineage[
            correction.correction_id
        ].append(
            correction.closure_hash216()
        )

        self.drift_field[
            correction.correction_id
        ] = (
            correction.drift_hash216
        )

        self.target_field[
            correction.correction_id
        ] = (
            correction.target_hash216
        )

        self.replay_field[
            correction.correction_id
        ] = (
            correction.replay_hash216
        )

        self.semantic_field[
            correction.correction_id
        ] = (
            correction.semantic_hash216
        )

        self.causal_field[
            correction.correction_id
        ] = (
            correction.causal_hash216
        )

        self.temporal_field[
            correction.correction_id
        ] = (
            correction.temporal_hash216
        )

        self.consensus_field[
            correction.correction_id
        ] = (
            correction.consensus_hash216
        )

        self.multimodal_field[
            correction.correction_id
        ] = (
            correction.multimodal_hash216
        )

        if (
            correction.correction_id
            not in self.correction_dependencies
        ):

            self.correction_dependencies[
                correction.correction_id
            ] = set()

        return True

    # ========================================================
    # CORRECTION DEPENDENCY
    # ========================================================

    def connect_correction_dependency(
        self,
        source_correction: str,
        target_correction: str,
    ) -> bool:
        """
        Establish stabilization dependency relation.
        """

        if (
            source_correction
            not in self.correction_registry
        ):
            return False

        if (
            target_correction
            not in self.correction_registry
        ):
            return False

        self.correction_dependencies[
            source_correction
        ].add(
            target_correction
        )

        return True

    # ========================================================
    # VALIDATE FIELD
    # ========================================================

    def validate_field(
        self,
    ) -> bool:
        """
        Universal adaptive stabilization validation.
        """

        for correction in (
            self.correction_registry.values()
        ):

            if not correction.validate():
                return False

        return True

    # ========================================================
    # STABILIZED
    # ========================================================

    def stabilized(
        self,
    ) -> bool:
        """
        Global manifold stabilization continuity.
        """

        for correction in (
            self.correction_registry.values()
        ):

            if not (
                correction.verify_stabilization()
            ):
                return False

        return True

    # ========================================================
    # CORRECTION CONE
    # ========================================================

    def correction_cone(
        self,
        correction_id: str,
    ) -> Set[str]:
        """
        Compute full stabilization dependency cone.
        """

        visited: Set[str] = set()

        def walk(node: str):

            if node in visited:
                return

            visited.add(node)

            for nxt in (
                self.correction_dependencies.get(
                    node,
                    set(),
                )
            ):
                walk(nxt)

        walk(correction_id)

        return visited

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global adaptive correction closure.
        """

        payload = {
            "correction_registry": sorted(
                [
                    correction.closure_hash216()
                    for correction in (
                        self.correction_registry.values()
                    )
                ]
            ),
            "lineage": self.correction_lineage,
            "dependencies": {
                k: sorted(list(v))
                for k, v in (
                    self.correction_dependencies.items()
                )
            },
            "drift": self.drift_field,
            "target": self.target_field,
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
    # AUTHORITATIVE CORRECTION
    # ========================================================

    def authoritative_correction(
        self,
    ) -> Optional[
        HHSAdaptiveCorrection
    ]:
        """
        Determine correction closest
        to manifold stabilization equivalence.
        """

        if not self.correction_registry:
            return None

        ordered = sorted(
            self.correction_registry.values(),
            key=lambda c: (
                c.closure_hash216(),
                c.correction_topology_hash216,
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
        Canonical adaptive correction field receipt.
        """

        authoritative = (
            self.authoritative_correction()
        )

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "correction_count": len(
                self.correction_registry
            ),
            "dependency_count": sum(
                len(v)
                for v in (
                    self.correction_dependencies.values()
                )
            ),
            "stabilized": (
                self.stabilized()
            ),
            "authoritative_correction": (
                authoritative.correction_id
                if authoritative
                else None
            ),
            "valid": (
                self.validate_field()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }