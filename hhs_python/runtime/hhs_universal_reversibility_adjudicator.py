# hhs_python/runtime/hhs_universal_reversibility_adjudicator.py
#
# HHS / HARMONICODE
# Universal Reversibility Adjudicator
#
# Canonical Runtime OS Manifold Arbitration Authority
#
# Runtime Principle:
#
#   all operations
#   must remain globally reconstructible
#   across every manifold surface simultaneously
#
# NOT:
#
#   isolated subsystem validation
#
# Canonical closure:
#
#   Hash216 = u^72 + v^72 = C^216
#
# where:
#
#   u^72 = forward adjudication traversal
#   v^72 = reciprocal adjudication reconstruction
#   C^216 = global manifold reversibility closure
#
# Runtime Primitive:
#
#   globally adjudicated reversible manifold evolution
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
# REVERSIBILITY WITNESS
# ============================================================

@dataclass(frozen=True)
class HHSReversibilityWitness:
    """
    Canonical manifold reversibility witness.
    """

    witness_id: str

    forward_hash216: str
    reciprocal_hash216: str

    admissible: bool = True
    reconstructible: bool = True
    globally_reversible: bool = True
    phase_equivalent: bool = True
    temporally_equivalent: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> bool:

        return (
            self.admissible
            and self.reconstructible
            and self.globally_reversible
            and self.phase_equivalent
            and self.temporally_equivalent
            and bool(self.forward_hash216)
            and bool(self.reciprocal_hash216)
        )


# ============================================================
# REVERSIBILITY VERDICT
# ============================================================

@dataclass(frozen=True)
class HHSReversibilityVerdict:
    """
    Canonical manifold admissibility carrier.

    All operations must remain:
        globally reconstructible.
    """

    verdict_id: str

    # ========================================================
    # STATE TRANSITION
    # ========================================================

    source_state_hash216: str
    target_state_hash216: str

    # ========================================================
    # MANIFOLD FIELDS
    # ========================================================

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

    # ========================================================
    # VERDICT TRAVERSAL
    # ========================================================

    forward_verdict_hash216: str
    reciprocal_verdict_hash216: str

    # ========================================================
    # VERDICT TOPOLOGY
    # ========================================================

    verdict_topology_hash216: str

    # ========================================================
    # FLAGS
    # ========================================================

    admissible: bool = True
    reconstructible: bool = True
    globally_reversible: bool = True
    phase_equivalent: bool = True
    temporally_equivalent: bool = True

    freeze_required: bool = False
    rollback_required: bool = False
    correction_required: bool = False

    # ========================================================
    # WITNESSES
    # ========================================================

    projection_witness: Optional[
        HHSReversibilityWitness
    ] = None

    execution_witness: Optional[
        HHSReversibilityWitness
    ] = None

    transport_witness: Optional[
        HHSReversibilityWitness
    ] = None

    governance_witness: Optional[
        HHSReversibilityWitness
    ] = None

    reciprocal_witness: Optional[
        HHSReversibilityWitness
    ] = None

    # ========================================================
    # PROOF
    # ========================================================

    verdict_proof_hash216: str = ""

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
        Universal manifold reversibility validation.
        """

        if not self.admissible:
            return False

        if not self.reconstructible:
            return False

        if not self.globally_reversible:
            return False

        if not self.phase_equivalent:
            return False

        if not self.temporally_equivalent:
            return False

        if self.rollback_required:

            if not self.freeze_required:
                return False

        witnesses = [
            self.projection_witness,
            self.execution_witness,
            self.transport_witness,
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
        Canonical reversibility adjudication closure.

            Hash216 = u^72 + v^72 = C^216
        """

        payload = {
            "verdict_id": self.verdict_id,
            "source_state": (
                self.source_state_hash216
            ),
            "target_state": (
                self.target_state_hash216
            ),
            "projection": (
                self.projection_hash216
            ),
            "execution": (
                self.execution_hash216
            ),
            "transport": (
                self.transport_hash216
            ),
            "governance": (
                self.governance_hash216
            ),
            "origin": (
                self.origin_hash216
            ),
            "replay": (
                self.replay_hash216
            ),
            "semantic": (
                self.semantic_hash216
            ),
            "causal": (
                self.causal_hash216
            ),
            "temporal": (
                self.temporal_hash216
            ),
            "identity": (
                self.identity_hash216
            ),
            "forward": (
                self.forward_verdict_hash216
            ),
            "reciprocal": (
                self.reciprocal_verdict_hash216
            ),
            "topology": (
                self.verdict_topology_hash216
            ),
            "freeze_required": (
                self.freeze_required
            ),
            "rollback_required": (
                self.rollback_required
            ),
            "correction_required": (
                self.correction_required
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # GLOBAL REVERSIBILITY
    # ========================================================

    def verify_global_reversibility(
        self,
    ) -> bool:
        """
        Global manifold reconstructibility invariant.
        """

        return (
            self.globally_reversible
            and self.validate()
        )

    # ========================================================
    # ADMISSIBILITY
    # ========================================================

    def verify_admissibility(
        self,
    ) -> bool:
        """
        Universal operation admissibility invariant.
        """

        return (
            self.admissible
            and self.validate()
        )

    # ========================================================
    # PHASE EQUIVALENCE
    # ========================================================

    def verify_phase_equivalence(
        self,
    ) -> bool:
        """
        Cross-manifold phase equivalence invariant.
        """

        return (
            self.phase_equivalent
            and self.validate()
        )

    # ========================================================
    # TEMPORAL EQUIVALENCE
    # ========================================================

    def verify_temporal_equivalence(
        self,
    ) -> bool:
        """
        Global temporal continuity invariant.
        """

        return (
            self.temporally_equivalent
            and self.validate()
        )

    # ========================================================
    # RECEIPT
    # ========================================================

    def receipt(
        self,
    ) -> Dict[str, Any]:
        """
        Canonical reversibility verdict receipt.
        """

        return {
            "verdict_id": self.verdict_id,
            "closure_hash216": (
                self.closure_hash216()
            ),
            "verdict_proof_hash216": (
                self.verdict_proof_hash216
            ),
            "admissible": (
                self.verify_admissibility()
            ),
            "globally_reversible": (
                self.verify_global_reversibility()
            ),
            "freeze_required": (
                self.freeze_required
            ),
            "rollback_required": (
                self.rollback_required
            ),
            "correction_required": (
                self.correction_required
            ),
            "timestamp_ns": (
                self.timestamp_ns
            ),
        }


# ============================================================
# UNIVERSAL REVERSIBILITY ADJUDICATOR
# ============================================================

class HHSUniversalReversibilityAdjudicator:
    """
    Canonical Runtime OS manifold arbitration authority.

    All operations must remain:
        globally reconstructible.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.verdict_registry: Dict[
            str,
            HHSReversibilityVerdict
        ] = {}

        self.verdict_lineage: Dict[
            str,
            List[str]
        ] = {}

        self.verdict_dependencies: Dict[
            str,
            Set[str]
        ] = {}

        self.source_state_field: Dict[
            str,
            str
        ] = {}

        self.target_state_field: Dict[
            str,
            str
        ] = {}

        self.projection_field: Dict[
            str,
            str
        ] = {}

        self.execution_field: Dict[
            str,
            str
        ] = {}

        self.transport_field: Dict[
            str,
            str
        ] = {}

        self.governance_field: Dict[
            str,
            str
        ] = {}

        self.origin_field: Dict[
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

        self.identity_field: Dict[
            str,
            str
        ] = {}

    # ========================================================
    # REGISTER VERDICT
    # ========================================================

    def register_verdict(
        self,
        verdict: HHSReversibilityVerdict,
    ) -> bool:
        """
        Register manifold reversibility verdict.
        """

        if not verdict.validate():
            return False

        self.verdict_registry[
            verdict.verdict_id
        ] = verdict

        if (
            verdict.verdict_id
            not in self.verdict_lineage
        ):

            self.verdict_lineage[
                verdict.verdict_id
            ] = []

        self.verdict_lineage[
            verdict.verdict_id
        ].append(
            verdict.closure_hash216()
        )

        self.source_state_field[
            verdict.verdict_id
        ] = (
            verdict.source_state_hash216
        )

        self.target_state_field[
            verdict.verdict_id
        ] = (
            verdict.target_state_hash216
        )

        self.projection_field[
            verdict.verdict_id
        ] = (
            verdict.projection_hash216
        )

        self.execution_field[
            verdict.verdict_id
        ] = (
            verdict.execution_hash216
        )

        self.transport_field[
            verdict.verdict_id
        ] = (
            verdict.transport_hash216
        )

        self.governance_field[
            verdict.verdict_id
        ] = (
            verdict.governance_hash216
        )

        self.origin_field[
            verdict.verdict_id
        ] = (
            verdict.origin_hash216
        )

        self.replay_field[
            verdict.verdict_id
        ] = (
            verdict.replay_hash216
        )

        self.semantic_field[
            verdict.verdict_id
        ] = (
            verdict.semantic_hash216
        )

        self.causal_field[
            verdict.verdict_id
        ] = (
            verdict.causal_hash216
        )

        self.temporal_field[
            verdict.verdict_id
        ] = (
            verdict.temporal_hash216
        )

        self.identity_field[
            verdict.verdict_id
        ] = (
            verdict.identity_hash216
        )

        if (
            verdict.verdict_id
            not in self.verdict_dependencies
        ):

            self.verdict_dependencies[
                verdict.verdict_id
            ] = set()

        return True

    # ========================================================
    # CONNECT VERDICTS
    # ========================================================

    def connect_verdict_dependency(
        self,
        source_verdict: str,
        target_verdict: str,
    ) -> bool:
        """
        Establish manifold adjudication dependency.
        """

        if (
            source_verdict
            not in self.verdict_registry
        ):
            return False

        if (
            target_verdict
            not in self.verdict_registry
        ):
            return False

        self.verdict_dependencies[
            source_verdict
        ].add(
            target_verdict
        )

        return True

    # ========================================================
    # ADJUDICATE
    # ========================================================

    def adjudicate_transition(
        self,
        source_state_hash216: str,
        target_state_hash216: str,
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
    ) -> HHSReversibilityVerdict:
        """
        Canonical manifold reversibility adjudication.
        """

        closure_seed = _hash216(
            json.dumps(
                {
                    "source": (
                        source_state_hash216
                    ),
                    "target": (
                        target_state_hash216
                    ),
                    "projection": (
                        projection_hash216
                    ),
                    "execution": (
                        execution_hash216
                    ),
                    "transport": (
                        transport_hash216
                    ),
                    "governance": (
                        governance_hash216
                    ),
                    "origin": (
                        origin_hash216
                    ),
                    "replay": (
                        replay_hash216
                    ),
                    "semantic": (
                        semantic_hash216
                    ),
                    "causal": (
                        causal_hash216
                    ),
                    "temporal": (
                        temporal_hash216
                    ),
                    "identity": (
                        identity_hash216
                    ),
                },
                sort_keys=True,
            )
        )

        globally_reversible = (
            source_state_hash216
            != ""
            and target_state_hash216
            != ""
            and projection_hash216
            != ""
            and execution_hash216
            != ""
            and transport_hash216
            != ""
            and governance_hash216
            != ""
            and origin_hash216
            != ""
            and replay_hash216
            != ""
            and semantic_hash216
            != ""
            and causal_hash216
            != ""
            and temporal_hash216
            != ""
            and identity_hash216
            != ""
        )

        freeze_required = (
            not globally_reversible
        )

        rollback_required = (
            not globally_reversible
        )

        correction_required = (
            not globally_reversible
        )

        verdict = HHSReversibilityVerdict(
            verdict_id=closure_seed,

            source_state_hash216=(
                source_state_hash216
            ),

            target_state_hash216=(
                target_state_hash216
            ),

            projection_hash216=(
                projection_hash216
            ),

            execution_hash216=(
                execution_hash216
            ),

            transport_hash216=(
                transport_hash216
            ),

            governance_hash216=(
                governance_hash216
            ),

            origin_hash216=(
                origin_hash216
            ),

            replay_hash216=(
                replay_hash216
            ),

            semantic_hash216=(
                semantic_hash216
            ),

            causal_hash216=(
                causal_hash216
            ),

            temporal_hash216=(
                temporal_hash216
            ),

            identity_hash216=(
                identity_hash216
            ),

            forward_verdict_hash216=(
                closure_seed
            ),

            reciprocal_verdict_hash216=(
                closure_seed[::-1]
            ),

            verdict_topology_hash216=(
                closure_seed
            ),

            admissible=(
                globally_reversible
            ),

            reconstructible=(
                globally_reversible
            ),

            globally_reversible=(
                globally_reversible
            ),

            phase_equivalent=(
                globally_reversible
            ),

            temporally_equivalent=(
                globally_reversible
            ),

            freeze_required=(
                freeze_required
            ),

            rollback_required=(
                rollback_required
            ),

            correction_required=(
                correction_required
            ),

            verdict_proof_hash216=(
                closure_seed
            ),
        )

        self.register_verdict(
            verdict
        )

        return verdict

    # ========================================================
    # VALIDATE ADJUDICATOR
    # ========================================================

    def validate_adjudicator(
        self,
    ) -> bool:
        """
        Universal manifold reversibility validation.
        """

        for verdict in (
            self.verdict_registry.values()
        ):

            if not verdict.validate():
                return False

        return True

    # ========================================================
    # GLOBALLY REVERSIBLE
    # ========================================================

    def globally_reversible(
        self,
    ) -> bool:
        """
        Global manifold reversibility continuity.
        """

        for verdict in (
            self.verdict_registry.values()
        ):

            if not (
                verdict.verify_global_reversibility()
            ):
                return False

        return True

    # ========================================================
    # VERDICT CONE
    # ========================================================

    def verdict_cone(
        self,
        verdict_id: str,
    ) -> Set[str]:
        """
        Compute adjudication dependency cone.
        """

        visited: Set[str] = set()

        def walk(node: str):

            if node in visited:
                return

            visited.add(node)

            for nxt in (
                self.verdict_dependencies.get(
                    node,
                    set(),
                )
            ):
                walk(nxt)

        walk(verdict_id)

        return visited

    # ========================================================
    # FIELD CLOSURE
    # ========================================================

    def field_hash216(
        self,
    ) -> str:
        """
        Global reversibility adjudication closure.
        """

        payload = {
            "verdict_registry": sorted(
                [
                    verdict.closure_hash216()
                    for verdict in (
                        self.verdict_registry.values()
                    )
                ]
            ),
            "lineage": (
                self.verdict_lineage
            ),
            "dependencies": {
                k: sorted(list(v))
                for k, v in (
                    self.verdict_dependencies.items()
                )
            },
            "source_state": (
                self.source_state_field
            ),
            "target_state": (
                self.target_state_field
            ),
            "projection": (
                self.projection_field
            ),
            "execution": (
                self.execution_field
            ),
            "transport": (
                self.transport_field
            ),
            "governance": (
                self.governance_field
            ),
            "origin": (
                self.origin_field
            ),
            "replay": (
                self.replay_field
            ),
            "semantic": (
                self.semantic_field
            ),
            "causal": (
                self.causal_field
            ),
            "temporal": (
                self.temporal_field
            ),
            "identity": (
                self.identity_field
            ),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # AUTHORITATIVE VERDICT
    # ========================================================

    def authoritative_verdict(
        self,
    ) -> Optional[
        HHSReversibilityVerdict
    ]:
        """
        Determine verdict closest
        to global manifold closure.
        """

        if not self.verdict_registry:
            return None

        ordered = sorted(
            self.verdict_registry.values(),
            key=lambda v: (
                v.closure_hash216(),
                v.verdict_topology_hash216,
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
        Canonical reversibility adjudicator receipt.
        """

        authoritative = (
            self.authoritative_verdict()
        )

        return {
            "field_hash216": (
                self.field_hash216()
            ),
            "verdict_count": len(
                self.verdict_registry
            ),
            "dependency_count": sum(
                len(v)
                for v in (
                    self.verdict_dependencies.values()
                )
            ),
            "globally_reversible": (
                self.globally_reversible()
            ),
            "authoritative_verdict": (
                authoritative.verdict_id
                if authoritative
                else None
            ),
            "valid": (
                self.validate_adjudicator()
            ),
            "timestamp_ns": (
                time.time_ns()
            ),
        }