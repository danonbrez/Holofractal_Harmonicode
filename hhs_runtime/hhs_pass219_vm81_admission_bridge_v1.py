"""Pass 219 VM81 ethical admission bridge.

This bridge consumes the Pass 218/219 R03/R04 reference trace, and only when
the inherited Pass 219 membrane returns EXECUTE_LOCAL_PROVISIONAL does it
invoke the existing HHSRuntimeController.authorized_tick path.

The bridge does not create capability, consent, scope, or a second state
authority. Non-executable ethical decisions produce no VM81 mutation.

Repair-forward note
-------------------
The original #208 implementation treated any return from ``authorized_tick``
as sufficient evidence that canonical VM81 mutation had occurred.  Current
runtime authority returns an ``HHSAuthorityAudit.to_dict()`` packet whose
success field is ``ok`` and whose Hash72 state/receipt lineage is explicit.
This revision therefore fails closed unless the returned authority audit and
receipt lineage are both present, successful, and mutually consistent.
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

VERSION = "HHS_PASS219_VM81_ETHICAL_ADMISSION_BRIDGE_V1"
SCHEMA = "HHS_PASS219_VM81_ETHICAL_ADMISSION_RESULT_V1"
HASH72_LENGTH = 72


class VM81AdmissionBridgeError(RuntimeError):
    """Raised when an admitted action cannot prove canonical runtime closure."""


def _is_hash72(value: object) -> bool:
    return isinstance(value, str) and len(value) == HASH72_LENGTH


def _validated_authorized_tick(execution: object) -> Dict[str, object]:
    """Validate the current canonical controller return shape fail-closed.

    The bridge does not independently decide VM81 authority.  It only accepts
    an ``authorized_tick`` result after the inherited controller reports a
    successful authority audit and the audit is bound to the same 72-character
    state and receipt identities returned by the committed runtime receipt.
    """

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



def _lane5_hydration_ethical_veto(evidence: Mapping[str, object]) -> dict[str, object]:
    """Negative constraint on task harness proposals; never grants authority.

    The inherited native I028/cell-wall and signed VM81 checks remain solely
    responsible for positive constructor and canonical execution admission.
    """
    required_true = (
        "typed_ingress_verified", "inherited_lanes_1_4_verified",
        "constructor_provenance_verified", "ordered_tensor_gates_verified",
        "external_interface_equivalent", "scope_and_consent_verified",
        "verification_procedures_bound", "temporary_harness_release_planned",
    )
    required_false = (
        "direct_canonical_mutation_authority", "direct_hash72_mint_authority",
        "direct_hash216_mint_authority", "direct_persistence_authority",
    )
    roots = ("pipeline_root_hash72", "constructor_graph_root_hash72")
    failures = [k for k in required_true if evidence.get(k) is not True]
    failures += [k for k in required_false if evidence.get(k) is not False]
    failures += [k for k in roots if not _is_hash72(evidence.get(k))]
    # Candidate evidence must carry explicit external interface fidelity,
    # not just an asserted compatible result.
    if evidence.get("external_input_type_verified") is not True:
        failures.append("external_input_type_verified")
    if evidence.get("external_output_type_verified") is not True:
        failures.append("external_output_type_verified")
    if evidence.get("observable_behavior_verified") is not True:
        failures.append("observable_behavior_verified")
    if evidence.get("hydration_precedes_composition") is not True:
        failures.append("hydration_precedes_composition")
    if evidence.get("conway_candidate_only") is not True:
        failures.append("conway_candidate_only")
    return {
        "schema": "HHS_PASS220_LANE5_ETHICAL_HYDRATION_VETO_V1",
        "candidate_only": True, "vetoed": bool(failures),
        "unresolved_constraints": failures,
        "native_constructor_admitted": False,
        "canonical_mint_authority": False,
    }

def admit_and_execute_local(
    action: ActionCandidate,
    declared_invariants: Sequence[EthicalInvariantResult],
    epistemic: EpistemicAdequacyTrace,
    findings: Sequence[NarrativeFinding] = (),
    counterexamples: Sequence[StructuralCounterexampleRecord] = (),
    *,
    controller: Optional[Any] = None,
    lane5_hydration_evidence: Optional[Mapping[str, object]] = None,
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
    if lane5_hydration_evidence is not None:
        if not isinstance(lane5_hydration_evidence, Mapping):
            raise VM81AdmissionBridgeError("Lane5 evidence must be a typed mapping")
        veto = _lane5_hydration_ethical_veto(lane5_hydration_evidence)
        result["lane5_hydration_ethical_gate"] = veto
        if veto["vetoed"]:
            result["execution_allowed"] = False
            return result
    if not allowed:
        return result

    if controller is None:
        # Lazy import ensures denied/held/simulation-only candidates do not
        # instantiate the authoritative runtime merely to be rejected.
        from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController

        controller = HHSRuntimeController()

    source = "HHS_PASS219_ETHICAL_ADMISSION:" + refined.trace_receipt_hash72
    execution = _validated_authorized_tick(controller.authorized_tick(source=source))
    result["vm81_execution"] = execution
    result["canonical_vm81_mutation_performed"] = True
    return result


__all__ = [
    "VERSION",
    "SCHEMA",
    "HASH72_LENGTH",
    "VM81AdmissionBridgeError",
    "admit_and_execute_local",
    "_lane5_hydration_ethical_veto",
]
