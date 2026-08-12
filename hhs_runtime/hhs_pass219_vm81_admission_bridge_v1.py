"""Pass 219 VM81 ethical admission bridge.

This bridge consumes the Pass 218/219 R03/R04 reference trace, and only when
the inherited Pass 219 membrane returns EXECUTE_LOCAL_PROVISIONAL does it
invoke the existing HHSRuntimeController.authorized_tick path.

The bridge does not create capability, consent, scope, or a second state
authority. Non-executable ethical decisions produce no VM81 mutation.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import (
    ActionCandidate,
    EthicalDecision,
    EthicalInvariantResult,
    EvaluationPhase,
    NarrativeFinding,
)
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v2 import (
    EpistemicAdequacyTrace,
    StructuralCounterexampleRecord,
    evaluate_action_v2,
)

VERSION = "HHS_PASS219_VM81_ETHICAL_ADMISSION_BRIDGE_V1"
SCHEMA = "HHS_PASS219_VM81_ETHICAL_ADMISSION_RESULT_V1"


def admit_and_execute_local(
    action: ActionCandidate,
    declared_invariants: Sequence[EthicalInvariantResult],
    epistemic: EpistemicAdequacyTrace,
    findings: Sequence[NarrativeFinding] = (),
    counterexamples: Sequence[StructuralCounterexampleRecord] = (),
    *,
    controller: Optional[Any] = None,
) -> Dict[str, object]:
    """Evaluate, then enter the inherited VM81 authority path if admitted."""

    refined = evaluate_action_v2(
        action,
        declared_invariants,
        epistemic,
        findings,
        counterexamples,
        phase=EvaluationPhase.PROSPECTIVE,
    )
    ethical = refined.evaluation
    allowed = ethical.decision is EthicalDecision.EXECUTE_LOCAL_PROVISIONAL

    result: Dict[str, object] = {
        "schema": SCHEMA,
        "version": VERSION,
        "ethical_trace": refined.to_dict(),
        "ethical_decision": ethical.decision.value,
        "effective_scope": list(ethical.scope.effective_scope),
        "execution_allowed": allowed,
        "canonical_vm81_mutation_performed": False,
        "action_authority_minted": False,
        "vm81_execution": None,
    }
    if not allowed:
        return result

    if controller is None:
        # Lazy import ensures denied/held/simulation-only candidates do not
        # instantiate the authoritative runtime merely to be rejected.
        from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController

        controller = HHSRuntimeController()

    source = "HHS_PASS219_ETHICAL_ADMISSION:" + refined.trace_receipt_hash72
    execution = controller.authorized_tick(source=source)
    result["vm81_execution"] = execution
    result["canonical_vm81_mutation_performed"] = True
    return result


__all__ = [
    "VERSION",
    "SCHEMA",
    "admit_and_execute_local",
]
