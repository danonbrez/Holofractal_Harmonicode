"""Pass 219 VM81 ethical admission bridge.

The inherited R03/R04 narrative membrane remains intact.  The expanded
constitutional/compositional membrane may now be evaluated first and, only
when it returns PASS, the candidate continues through the existing local
ethical evaluator and the same HHSRuntimeController.authorized_tick singleton
VM81 authority path.  No second mutation authority is introduced.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Sequence

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
from hhs_runtime.hhs_pass219_constitutional_ethics_membrane_v1 import (
    ConstitutionalEthicsCandidate,
    EthicsState,
    evaluate_constitutional_ethics,
)

VERSION = "HHS_PASS219_VM81_ETHICAL_ADMISSION_BRIDGE_V1"
SCHEMA = "HHS_PASS219_VM81_ETHICAL_ADMISSION_RESULT_V1"
HASH72_LENGTH = 72


class VM81AdmissionBridgeError(RuntimeError):
    """Raised when an admitted action cannot prove canonical runtime closure."""


def _is_hash72(value: object) -> bool:
    return isinstance(value, str) and len(value) == HASH72_LENGTH


def _validated_authorized_tick(execution: object) -> Dict[str, object]:
    if not isinstance(execution, Mapping):
        raise VM81AdmissionBridgeError("authorized_tick returned no mapping")
    runtime = execution.get("runtime")
    receipt = execution.get("receipt")
    audit = execution.get("authority_audit")
    if not isinstance(runtime, Mapping):
        raise VM81AdmissionBridgeError("authorized_tick runtime packet missing")
    if not isinstance(receipt, Mapping):
        raise VM81AdmissionBridgeError("authorized_tick receipt packet missing")
    if not isinstance(audit, Mapping):
        raise VM81AdmissionBridgeError("authorized_tick authority audit missing")
    if audit.get("ok") is not True:
        raise VM81AdmissionBridgeError("canonical runtime authority audit is not successful")

    state_hash72 = receipt.get("state_hash72")
    receipt_hash72 = receipt.get("receipt_hash72")
    if not _is_hash72(state_hash72):
        raise VM81AdmissionBridgeError("committed state Hash72 lineage missing or malformed")
    if not _is_hash72(receipt_hash72):
        raise VM81AdmissionBridgeError("committed receipt Hash72 lineage missing or malformed")
    if audit.get("state_hash72") != state_hash72:
        raise VM81AdmissionBridgeError("authority audit state Hash72 does not bind the committed receipt")
    if audit.get("receipt_hash72") != receipt_hash72:
        raise VM81AdmissionBridgeError("authority audit receipt Hash72 does not bind the committed receipt")
    if runtime.get("state_hash72") != state_hash72:
        raise VM81AdmissionBridgeError("runtime state Hash72 does not bind the committed receipt")
    return dict(execution)


def admit_and_execute_local(
    action: ActionCandidate,
    declared_invariants: Sequence[EthicalInvariantResult],
    epistemic: EpistemicAdequacyTrace,
    findings: Sequence[NarrativeFinding] = (),
    counterexamples: Sequence[StructuralCounterexampleRecord] = (),
    *,
    controller: Optional[Any] = None,
) -> Dict[str, object]:
    """Existing local ethical gate followed by inherited singleton authority."""
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
        from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
        controller = HHSRuntimeController()
    source = "HHS_PASS219_ETHICAL_ADMISSION:" + refined.trace_receipt_hash72
    execution = _validated_authorized_tick(controller.authorized_tick(source=source))
    result["vm81_execution"] = execution
    result["canonical_vm81_mutation_performed"] = True
    return result


def admit_and_execute_constitutional(
    constitutional_candidate: ConstitutionalEthicsCandidate,
    action: ActionCandidate,
    declared_invariants: Sequence[EthicalInvariantResult],
    epistemic: EpistemicAdequacyTrace,
    findings: Sequence[NarrativeFinding] = (),
    counterexamples: Sequence[StructuralCounterexampleRecord] = (),
    *,
    controller: Optional[Any] = None,
) -> Dict[str, object]:
    """Global/local constitutional gate before the existing admission bridge.

    FAIL and HOLD never touch the runtime controller.  PASS does not mint new
    authority; it only permits continuation into ``admit_and_execute_local``.
    """
    constitutional = evaluate_constitutional_ethics(constitutional_candidate)
    if constitutional.state is not EthicsState.PASS:
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "constitutional_trace": constitutional.to_dict(),
            "constitutional_state": constitutional.state.value,
            "execution_allowed": False,
            "canonical_vm81_mutation_performed": False,
            "action_authority_minted": False,
            "vm81_execution": None,
        }

    result = admit_and_execute_local(
        action,
        declared_invariants,
        epistemic,
        findings,
        counterexamples,
        controller=controller,
    )
    result["constitutional_trace"] = constitutional.to_dict()
    result["constitutional_state"] = constitutional.state.value
    return result


__all__ = [
    "VERSION",
    "SCHEMA",
    "HASH72_LENGTH",
    "VM81AdmissionBridgeError",
    "admit_and_execute_local",
    "admit_and_execute_constitutional",
]
