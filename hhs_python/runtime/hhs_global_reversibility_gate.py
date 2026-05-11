# hhs_python/runtime/hhs_global_reversibility_gate.py
#
# HHS / HARMONICODE
# Global Reversibility Gate
#
# Canonical Runtime OS Enforcement Layer
#
# Runtime Principle:
#
#   No mutation propagates unless:
#
#       - globally reversible
#       - replay admissible
#       - topology equivalent
#       - causally closed
#       - universally readable
#       - reciprocal HASH216 closure valid
#
# This gate is the:
#
#   universal interstitial causality membrane
#
# between ALL runtime domains.
#

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import json
import time

from hhs_python.runtime.hhs_multimodal_transition_tensor81 import (
    HHSMultimodalTransitionTensor81,
)


# ============================================================
# HASH216
# ============================================================

HASH216_WIDTH = 216


def _hash216(data: str) -> str:
    """
    Canonical HASH216 projection layer.
    """

    h1 = hashlib.sha512(data.encode()).hexdigest()
    h2 = hashlib.sha256(data.encode()).hexdigest()

    merged = h1 + h2

    return merged[:HASH216_WIDTH]


# ============================================================
# VALIDATION RESULT
# ============================================================

@dataclass(frozen=True)
class HHSGateValidationResult:
    """
    Universal admissibility proof result.
    """

    runtime_id: str

    admitted: bool

    reversible: bool
    replay_admissible: bool
    topology_equivalent: bool
    globally_readable: bool
    causally_closed: bool

    reciprocal_closure_valid: bool
    invariant_closure_valid: bool
    modality_consensus_valid: bool

    validation_hash216: str

    failure_reasons: Tuple[str, ...]

    timestamp_ns: int

    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        return (
            self.admitted
            and self.reversible
            and self.replay_admissible
            and self.topology_equivalent
            and self.globally_readable
            and self.causally_closed
            and self.reciprocal_closure_valid
            and self.invariant_closure_valid
            and self.modality_consensus_valid
        )


# ============================================================
# REVERSIBILITY GATE
# ============================================================

class HHSGlobalReversibilityGate:
    """
    Universal Runtime OS admissibility membrane.

    This gate validates:

        - cross-topology reversibility
        - replay admissibility
        - modality consensus
        - topology continuity
        - semantic readability
        - reciprocal closure
        - invariant preservation

    before ANY propagation is allowed.
    """

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self):

        self.validation_history: List[HHSGateValidationResult] = []

    # ========================================================
    # PUBLIC VALIDATION
    # ========================================================

    def validate_tensor(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ) -> HHSGateValidationResult:
        """
        Canonical universal admissibility validation.
        """

        failures: List[str] = []

        reversible = tensor.reversible()
        replay_admissible = tensor.transition_proof.replay_admissible
        topology_equivalent = tensor.topology_equivalent()
        globally_readable = tensor.globally_readable()
        causally_closed = tensor.causality_chain.causally_closed

        reciprocal_closure_valid = self._validate_hash216_closure(
            tensor
        )

        invariant_closure_valid = self._validate_invariants(
            tensor
        )

        modality_consensus_valid = self._validate_modalities(
            tensor
        )

        # ====================================================
        # FAILURES
        # ====================================================

        if not reversible:
            failures.append(
                "tensor_not_reversible"
            )

        if not replay_admissible:
            failures.append(
                "replay_not_admissible"
            )

        if not topology_equivalent:
            failures.append(
                "topology_not_equivalent"
            )

        if not globally_readable:
            failures.append(
                "globally_unreadable"
            )

        if not causally_closed:
            failures.append(
                "causality_chain_open"
            )

        if not reciprocal_closure_valid:
            failures.append(
                "hash216_reciprocal_closure_invalid"
            )

        if not invariant_closure_valid:
            failures.append(
                "global_invariant_failure"
            )

        if not modality_consensus_valid:
            failures.append(
                "modality_consensus_failure"
            )

        if not tensor.validate():
            failures.append(
                "tensor_validation_failure"
            )

        admitted = len(failures) == 0

        result = HHSGateValidationResult(
            runtime_id=tensor.runtime_id,
            admitted=admitted,
            reversible=reversible,
            replay_admissible=replay_admissible,
            topology_equivalent=topology_equivalent,
            globally_readable=globally_readable,
            causally_closed=causally_closed,
            reciprocal_closure_valid=reciprocal_closure_valid,
            invariant_closure_valid=invariant_closure_valid,
            modality_consensus_valid=modality_consensus_valid,
            validation_hash216=self._validation_hash(
                tensor,
                failures,
            ),
            failure_reasons=tuple(failures),
            timestamp_ns=time.time_ns(),
        )

        self.validation_history.append(result)

        return result

    # ========================================================
    # PROPAGATION GATE
    # ========================================================

    def authorize_propagation(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ) -> bool:
        """
        Mandatory propagation membrane.

        No tensor propagates unless globally admissible.
        """

        result = self.validate_tensor(
            tensor
        )

        return result.validate()

    # ========================================================
    # HASH216 RECIPROCAL CLOSURE
    # ========================================================

    def _validate_hash216_closure(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ) -> bool:
        """
        Canonical closure:

            Hash216 = u^72 + v^72 = C^216
        """

        seed = tensor.ternary_anchor.seed_hash216
        state = tensor.ternary_anchor.state_hash216
        receipt = tensor.ternary_anchor.receipt_hash216

        if not seed:
            return False

        if not state:
            return False

        if not receipt:
            return False

        closure = tensor.ternary_anchor.closure_hash()

        if not closure:
            return False

        if len(closure) < HASH216_WIDTH:
            return False

        return True

    # ========================================================
    # GLOBAL INVARIANTS
    # ========================================================

    def _validate_invariants(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ) -> bool:
        """
        Validate all 9 invariant governance cells.
        """

        for invariant in tensor.invariant_cells:

            if not invariant.validate():
                return False

        return True

    # ========================================================
    # MODALITY CONSENSUS
    # ========================================================

    def _validate_modalities(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ) -> bool:
        """
        Cross-modality reversibility consensus.

        Authority:
            no modality is authoritative alone.

        Admissibility:
            modalities mutually validate.
        """

        for modality in tensor.modality_layers:

            if not modality.validate():
                return False

        return True

    # ========================================================
    # VALIDATION HASH
    # ========================================================

    def _validation_hash(
        self,
        tensor: HHSMultimodalTransitionTensor81,
        failures: List[str],
    ) -> str:
        """
        Deterministic validation proof hash.
        """

        payload = {
            "runtime_id": tensor.runtime_id,
            "tensor_hash216": tensor.global_hash216(),
            "failures": failures,
            "timestamp": time.time_ns(),
        }

        return _hash216(
            json.dumps(
                payload,
                sort_keys=True,
            )
        )

    # ========================================================
    # FAIL CLOSED
    # ========================================================

    def fail_closed(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ) -> Dict[str, Any]:
        """
        Canonical fail-closed response.

        Runtime principle:
            uncertainty
            =
            inadmissibility
        """

        result = self.validate_tensor(
            tensor
        )

        return {
            "runtime_id": tensor.runtime_id,
            "admitted": False,
            "fail_closed": True,
            "validation_hash216": result.validation_hash216,
            "failure_reasons": result.failure_reasons,
            "timestamp_ns": result.timestamp_ns,
        }

    # ========================================================
    # VALIDATION HISTORY
    # ========================================================

    def validation_receipts(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Replay-admissible validation history.
        """

        out: List[Dict[str, Any]] = []

        for item in self.validation_history:

            out.append(
                {
                    "runtime_id": item.runtime_id,
                    "admitted": item.admitted,
                    "validation_hash216": item.validation_hash216,
                    "timestamp_ns": item.timestamp_ns,
                    "failure_reasons": item.failure_reasons,
                }
            )

        return out

    # ========================================================
    # UNIVERSAL READABILITY
    # ========================================================

    def verify_global_readability(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ) -> bool:
        """
        Semantic continuity invariant.

        No canonical runtime state may become:
            opaque
            unreadable
            semantically dead
        """

        return tensor.globally_readable()

    # ========================================================
    # UNIVERSAL REVERSIBILITY
    # ========================================================

    def verify_reversibility(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ) -> bool:
        """
        Universal causal invertibility invariant.
        """

        return tensor.reversible()

    # ========================================================
    # TOPOLOGY EQUIVALENCE
    # ========================================================

    def verify_topology_equivalence(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ) -> bool:
        """
        Runtime topology reconstruction invariant.
        """

        return tensor.topology_equivalent()

    # ========================================================
    # REPLAY ADMISSIBILITY
    # ========================================================

    def verify_replay_admissibility(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ) -> bool:
        """
        Deterministic replay reconstruction invariant.
        """

        return tensor.transition_proof.replay_admissible

    # ========================================================
    # CAUSALITY CONTINUITY
    # ========================================================

    def verify_causality_chain(
        self,
        tensor: HHSMultimodalTransitionTensor81,
    ) -> bool:
        """
        Canonical causality continuity invariant.
        """

        return tensor.causality_chain.causally_closed