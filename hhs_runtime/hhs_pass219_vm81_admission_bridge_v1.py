"""Pass 219 VM81 ethical admission bridge.

Canonical mutation is reachable only after the expanded constitutional and
compositional membrane passes.  The public local evaluator remains available
for diagnostics, but it cannot touch the runtime controller.  This closes the
legacy path in which a caller could invoke the local ethical gate without the
mandatory local/global modality membrane.

The constitutional path appends code-owned modality traces intrinsically and
then continues through the inherited HHSRuntimeController.authorized_tick
singleton VM81 authority.  No second mutation authority is introduced.
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
from hhs_runtime.hhs_pass219_modality_constitutional_trace_v1 import (
    close_candidate_modalities,
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


def _evaluate_local(
    action: ActionCandidate,
    declared_invariants: Sequence[EthicalInvariantResult],
    epistemic: EpistemicAdequacyTrace,
    findings: Sequence[NarrativeFinding],
    counterexamples: Sequence[StructuralCounterexampleRecord],
):
    return evaluate_action_v2(
        action,
        declared_invariants,
        epistemic,
        findings,
        counterexamples,
        phase=EvaluationPhase.PROSPECTIVE,
    )


def _local_result(refined: object) -> Dict[str, object]:
    ethical = refined.evaluation
    local_pass = ethical.decision is EthicalDecision.EXECUTE_LOCAL_PROVISIONAL
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "ethical_trace": refined.to_dict(),
        "ethical_decision": ethical.decision.value,
        "effective_scope": list(ethical.scope.effective_scope),
        "local_ethical_pass": local_pass,
        "constitutional_trace_required": True,
        "execution_allowed": False,
        "canonical_vm81_mutation_performed": False,
        "action_authority_minted": False,
        "vm81_execution": None,
    }


def admit_and_execute_local(
    action: ActionCandidate,
    declared_invariants: Sequence[EthicalInvariantResult],
    epistemic: EpistemicAdequacyTrace,
    findings: Sequence[NarrativeFinding] = (),
    counterexamples: Sequence[StructuralCounterexampleRecord] = (),
    *,
    controller: Optional[Any] = None,
) -> Dict[str, object]:
    """Evaluate the inherited local membrane without mutation authority.

    ``controller`` is retained only for API compatibility and is deliberately
    ignored.  Local success is necessary but no longer sufficient for VM81
    execution.  Callers must use ``admit_and_execute_constitutional``.
    """
    del controller
    refined = _evaluate_local(action, declared_invariants, epistemic, findings, counterexamples)
    return _local_result(refined)


def _execute_after_constitutional_pass(
    refined: object,
    constitutional: object,
    *,
    controller: Optional[Any],
) -> Dict[str, object]:
    """Private continuation reachable only from the constitutional gate."""
    result = _local_result(refined)
    result["constitutional_trace"] = constitutional.to_dict()
    result["constitutional_state"] = constitutional.state.value

    ethical = refined.evaluation
    if ethical.decision is not EthicalDecision.EXECUTE_LOCAL_PROVISIONAL:
        return result

    if controller is None:
        from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
        controller = HHSRuntimeController()

    source = (
        "HHS_PASS219_CONSTITUTIONAL_ETHICAL_ADMISSION:"
        + constitutional.trace_receipt_hash72
        + ":"
        + refined.trace_receipt_hash72
    )
    execution = _validated_authorized_tick(controller.authorized_tick(source=source))
    result["execution_allowed"] = True
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
    """Mandatory local/global modality closure before singleton VM81 authority.

    The candidate's participating modalities are closed against the root
    invariant set.  Missing root invariants fail closed.  The constitutional
    membrane and VM81 bridge traces are appended intrinsically by code rather
    than caller choice.  FAIL and HOLD never touch the runtime controller.
    """
    closed_candidate = close_candidate_modalities(constitutional_candidate)
    constitutional = evaluate_constitutional_ethics(closed_candidate)
    if constitutional.state is not EthicsState.PASS:
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "constitutional_trace": constitutional.to_dict(),
            "constitutional_state": constitutional.state.value,
            "constitutional_trace_required": True,
            "execution_allowed": False,
            "canonical_vm81_mutation_performed": False,
            "action_authority_minted": False,
            "vm81_execution": None,
        }

    refined = _evaluate_local(action, declared_invariants, epistemic, findings, counterexamples)
    return _execute_after_constitutional_pass(
        refined,
        constitutional,
        controller=controller,
    )


__all__ = [
    "VERSION",
    "SCHEMA",
    "HASH72_LENGTH",
    "VM81AdmissionBridgeError",
    "admit_and_execute_local",
    "admit_and_execute_constitutional",
]
