"""Ordered prompt/response Lean + Pass219 predictive ethical cycle binding.

Composition only. The existing native I051 Lean admission and the existing
Pass219 E01..E18 counterfactual/ethical membrane perform the calculations.
This code does NOT infer missing invariant facts, generate pretend trajectory
evidence, conflate Hash72 with kernel authority, or mint VM81 transitions.
Actual RNA/VM5184 provenance is a distinct downstream required membrane.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import (
    ActionCandidate,
    EthicalInvariantResult,
    INVARIANT_ORDER,
)
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v2 import (
    EpistemicAdequacyTrace,
)
from hhs_runtime.hhs_pass219_lane5_predictive_narrative_v1 import (
    PredictiveSimulationContext,
    ProbeDepthInputs,
    simulate_and_evaluate,
)
from hhs_runtime.hhs_pass220_i051_native_lean_alignment_v1 import (
    admit_native_lean_alignment_tensor,
)


class HHSNativeEthicalResponseCycleError(RuntimeError):
    """Fail-closed missing, mismatched, or invalid ordered candidate evidence."""


def evaluate_native_ethical_response_candidate(
    *,
    prompt: str,
    response: str,
    action: ActionCandidate,
    declared_invariants: Sequence[EthicalInvariantResult],
    epistemic: EpistemicAdequacyTrace,
    narrative_generator: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    local_validator: Callable[..., Any],
    trajectory_validator: Callable[..., Any],
    context: PredictiveSimulationContext,
    depth: ProbeDepthInputs = ProbeDepthInputs(),
    relation_db: Mapping[str, Any] | None = None,
    explicit_relations: Sequence[Mapping[str, Any]] = (),
    phase8_channels: Sequence[str] | None = None,
    closure_witness: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute actual original typed theorem gates, preserving their decisions.

    The DIRECT_TEXT_RESPONSE transport profile binds originating_context to
    the precise prompt bytes and intent to the precise response bytes. Other
    action profiles require a separate typed binding proof, not coercion.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        raise HHSNativeEthicalResponseCycleError("authoritative prompt text required")
    if not isinstance(response, str) or not response.strip():
        raise HHSNativeEthicalResponseCycleError("derived response text required")
    if not isinstance(action, ActionCandidate):
        raise HHSNativeEthicalResponseCycleError("typed original ActionCandidate required")
    if action.originating_context != prompt or action.intent != response:
        raise HHSNativeEthicalResponseCycleError(
            "action intent/origin does not match ordered prompt-response candidate"
        )
    if "TEXT_EGRESS" not in action.minimum_necessary_scope:
        raise HHSNativeEthicalResponseCycleError(
            "explicit TEXT_EGRESS minimum scope required"
        )
    if not isinstance(epistemic, EpistemicAdequacyTrace):
        raise HHSNativeEthicalResponseCycleError("typed epistemic evidence required")
    if not isinstance(context, PredictiveSimulationContext):
        raise HHSNativeEthicalResponseCycleError("typed predictive context required")
    if not context.parent_hash216:
        raise HHSNativeEthicalResponseCycleError("parent Hash216 reference required")
    invariants = tuple(declared_invariants)
    if len(invariants) != len(INVARIANT_ORDER) or any(
        not isinstance(item, EthicalInvariantResult) for item in invariants
    ):
        raise HHSNativeEthicalResponseCycleError(
            "complete original E01..E18 typed invariant evidence required"
        )
    if tuple(item.invariant_id for item in invariants) != INVARIANT_ORDER:
        raise HHSNativeEthicalResponseCycleError(
            "original ordered E01..E18 invariant positions must be preserved"
        )
    if not all(callable(v) for v in (narrative_generator, local_validator, trajectory_validator)):
        raise HHSNativeEthicalResponseCycleError(
            "native ethical narrative generation and validation callbacks required"
        )

    lean = admit_native_lean_alignment_tensor(
        prompt, response,
        response_kind="TEXT",
        relation_db=relation_db,
        explicit_relations=explicit_relations,
        phase8_channels=phase8_channels,
        closure_witness=closure_witness,
    )
    if (
        not lean.get("canonical")
        or lean.get("tensor_state") != "GENESIS"
        or lean.get("ordered_tensor", {}).get("commutation_allowed_without_native_proof")
        is not False
        or lean.get("canonical_vm81_mutation_authority") is not False
    ):
        raise HHSNativeEthicalResponseCycleError(
            "native Lean ordered prompt-response tensor rejected whole candidate"
        )

    # This invokes the *existing* Pass219 narrative generator, local-state
    # validators, trajectory validator and E01..E18 exact ethical evaluator.
    # Neither a returned score nor our disposition can overrule that membrane.
    evaluated = simulate_and_evaluate(
        action,
        invariants,
        epistemic,
        narrative_generator=narrative_generator,
        local_validator=local_validator,
        trajectory_validator=trajectory_validator,
        context=context,
        depth=depth,
    )
    evaluation = evaluated.evaluation.evaluation
    if evaluated.action_id != action.action_id:
        raise HHSNativeEthicalResponseCycleError("ethical result action identity mismatch")
    if not evaluated.simulation_receipt_hash72 or not evaluated.evaluation.trace_receipt_hash72:
        raise HHSNativeEthicalResponseCycleError("original ethical trace receipts required")
    if evaluated.evaluation.evaluation.phase.value != "PROSPECTIVE":
        raise HHSNativeEthicalResponseCycleError("nonprospective ethical evaluation")

    return {
        "schema": "HHS_LANE5_ORDERED_ETHICAL_RESPONSE_CANDIDATE_V1",
        "profile": "DIRECT_TEXT_RESPONSE",
        "native_lean_admission_root_hash72": lean["admission_root_hash72"],
        "native_lean_transition_word216": lean["lineage"]["transition_word216"],
        "native_lean_ordered_tensor": lean["ordered_tensor"],
        "native_lean_closure_verified": True,
        "ethical_action_id": evaluated.action_id,
        "ethical_decision": evaluation.decision.value,
        "ethical_failed_invariants": list(evaluation.failed_invariants),
        "ethical_unresolved_invariants": list(evaluation.unresolved_invariants),
        "ethical_simulation_receipt_hash72": evaluated.simulation_receipt_hash72,
        "ethical_trace_receipt_hash72": evaluated.evaluation.trace_receipt_hash72,
        "ethical_prospective_candidate": bool(evaluated.execution_candidate),
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
        "candidate_only": True,
        "original_ethical_e01_e18_evaluated": True,
        "original_narrative_trajectories_evaluated": len(evaluated.trajectories),
        "lineage_parent_reference_present": True,
        "native_hash216_to_lean_lineage_equivalence_proven": False,
        "native_rna_vm5184_mediation_executed": False,
        "signed_environmental_vm81_admission_invoked": False,
        "all_dependencies_authoritative_for_canonical_commit": False,
        "model_generated_text_rewritten": False,
        "ethical_reference_result_is_not_canonical_vm81_admission": True,
    }
