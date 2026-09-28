"""Pass 219 Lane 5 predictive narrative consequence simulation.

This append-only layer connects native/caller-supplied narrative generation to
existing Pass 218/219 ethical equations without creating a second veto rule or
state authority.

Generation constructs counterfactual trajectories.  Every projected state is
passed through a caller-supplied exact local validator.  A separate trajectory
validator maps composition-level consequences into the existing E01..E18
``NarrativeFinding`` surface.  The inherited ``evaluate_action_v2`` membrane
then makes the ethical decision.  Actual canonical mutation remains downstream
through the existing Pass 219 VM81 admission bridge.

Generated narrative text is preserved byte-for-byte in the live simulation
result.  Structural counterexample persistence remains governed by the
existing Pass 218 R04 policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import (
    ActionCandidate,
    EthicalDecision,
    EthicalInvariantResult,
    EvaluationPhase,
    INVARIANT_ORDER,
    InvariantState,
    NarrativeFinding,
    build_narrative_probe_contract,
)
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v2 import (
    EpistemicAdequacyTrace,
    EthicalNarrativeEvaluationV2,
    StructuralCounterexampleRecord,
    evaluate_action_v2,
)

VERSION = "HHS_PASS219_LANE5_PREDICTIVE_NARRATIVE_V1"
SCHEMA = "HHS_PASS219_LANE5_PREDICTIVE_NARRATIVE_RESULT_V1"
TRAJECTORY_SCHEMA = "HHS_PASS219_LANE5_PREDICTIVE_TRAJECTORY_V1"
AUTHORITY = "COUNTERFACTUAL_SIMULATION_ONLY_VM81_MUTATION_DOWNSTREAM"
MAX_ORDINAL = 72
MAX_TRAJECTORIES = 72
MAX_STATES_PER_TRAJECTORY = 5184


class PredictiveNarrativeError(RuntimeError):
    """Raised when a predictive narrative trace violates the contract."""


def _bounded_ordinal(value: int, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field} must be an exact integer")
    if not 0 <= value <= MAX_ORDINAL:
        raise ValueError(f"{field} must be in 0..{MAX_ORDINAL}")
    return value


def _positive_bounded_int(value: int, *, field: str, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field} must be an exact integer")
    if value < 1 or value > maximum:
        raise ValueError(f"{field} must be in 1..{maximum}")
    return value


def _ordered_unique(values: Iterable[str]) -> Tuple[str, ...]:
    seen = set()
    out = []
    for raw in values:
        value = str(raw).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return tuple(out)


def _stable_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )


def _reference_receipt(label: str, payload: Mapping[str, object]) -> str:
    return hash72_digest((VERSION, label, _stable_json(payload)), width=24)


def _sha256_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ProbeDepthInputs:
    """Exact integer scheduling inputs from Pass 219 D7.

    These values may allocate simulation work.  They never override a hard
    ethical invariant and never independently authorize or veto an action.
    """

    novelty: int = 0
    scope_breadth: int = 0
    irreversibility: int = 0
    uncertainty: int = 0
    dependency_load: int = 0
    externality_risk: int = 0

    def __post_init__(self) -> None:
        for name, value in self.to_dict().items():
            _bounded_ordinal(value, field=name)

    def to_dict(self) -> Dict[str, int]:
        return {
            "novelty": self.novelty,
            "scope_breadth": self.scope_breadth,
            "irreversibility": self.irreversibility,
            "uncertainty": self.uncertainty,
            "dependency_load": self.dependency_load,
            "externality_risk": self.externality_risk,
        }

    @property
    def probe_depth_class(self) -> int:
        return max(self.to_dict().values())


@dataclass(frozen=True)
class PredictiveSimulationContext:
    """Exact context passed unchanged into Lane 5 narrative generation."""

    verbatim_equations: Tuple[str, ...] = ()
    physics_constraint_ids: Tuple[str, ...] = ()
    inherited_constraint_ids: Tuple[str, ...] = ()
    parent_hash216: Optional[str] = None
    lane5_constructor_receipt: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "verbatim_equations": list(self.verbatim_equations),
            "physics_constraint_ids": list(_ordered_unique(self.physics_constraint_ids)),
            "inherited_constraint_ids": list(_ordered_unique(self.inherited_constraint_ids)),
            "parent_hash216": self.parent_hash216,
            "lane5_constructor_receipt": self.lane5_constructor_receipt,
        }


@dataclass(frozen=True)
class ProjectedStateValidation:
    trajectory_id: str
    state_id: str
    parent_state_id: Optional[str]
    sequence: int
    status: InvariantState
    invariant_results: Tuple[EthicalInvariantResult, ...]
    witness_ids: Tuple[str, ...]
    hash216_reference: Optional[str]
    local_receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "trajectory_id": self.trajectory_id,
            "state_id": self.state_id,
            "parent_state_id": self.parent_state_id,
            "sequence": self.sequence,
            "status": self.status.value,
            "invariant_results": [item.to_dict() for item in self.invariant_results],
            "witness_ids": list(self.witness_ids),
            "hash216_reference": self.hash216_reference,
            "local_receipt_hash72": self.local_receipt_hash72,
            "canonical_vm81_mutation_performed": False,
        }


@dataclass(frozen=True)
class PredictiveTrajectory:
    trajectory_id: str
    narrative: str
    narrative_sha256: str
    narrative_receipt_hash72: str
    projected_state_validations: Tuple[ProjectedStateValidation, ...]
    finding: NarrativeFinding

    def to_dict(self) -> Dict[str, object]:
        return {
            "schema": TRAJECTORY_SCHEMA,
            "trajectory_id": self.trajectory_id,
            "narrative": self.narrative,
            "narrative_sha256": self.narrative_sha256,
            "narrative_receipt_hash72": self.narrative_receipt_hash72,
            "generated_narrative_unmodified": True,
            "projected_state_validations": [
                item.to_dict() for item in self.projected_state_validations
            ],
            "finding": self.finding.to_dict(),
            "narrative_epistemic_status": "COUNTERFACTUAL_OR_FICTIONAL",
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_vm81_mutation_performed": False,
        }


@dataclass(frozen=True)
class PredictiveNarrativeResult:
    action_id: str
    depth: ProbeDepthInputs
    context: PredictiveSimulationContext
    trajectories: Tuple[PredictiveTrajectory, ...]
    membrane_findings: Tuple[NarrativeFinding, ...]
    evaluation: EthicalNarrativeEvaluationV2
    simulation_receipt_hash72: str

    @property
    def execution_candidate(self) -> bool:
        return self.evaluation.evaluation.decision is EthicalDecision.EXECUTE_LOCAL_PROVISIONAL

    def to_dict(self) -> Dict[str, object]:
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "authority": AUTHORITY,
            "action_id": self.action_id,
            "probe_depth": self.depth.to_dict(),
            "probe_depth_class": self.depth.probe_depth_class,
            "context": self.context.to_dict(),
            "trajectories": [item.to_dict() for item in self.trajectories],
            "membrane_finding_ids": [item.finding_id for item in self.membrane_findings],
            "evaluation": self.evaluation.to_dict(),
            "execution_candidate": self.execution_candidate,
            "simulation_receipt_hash72": self.simulation_receipt_hash72,
            "generated_tokens_filtered_or_rewritten": False,
            "probability_or_depth_can_override_hard_invariants": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_vm81_mutation_performed": False,
        }


NarrativeGenerator = Callable[[Mapping[str, object]], Mapping[str, object]]
LocalStateValidator = Callable[[Mapping[str, object]], Mapping[str, object]]
TrajectoryValidator = Callable[[Mapping[str, object]], NarrativeFinding]


def _parse_invariant_result(value: Mapping[str, object]) -> EthicalInvariantResult:
    invariant_id = str(value.get("invariant_id") or "")
    if invariant_id not in INVARIANT_ORDER:
        raise PredictiveNarrativeError(f"unknown invariant_id: {invariant_id}")
    try:
        state = InvariantState(str(value.get("state") or ""))
    except ValueError as exc:
        raise PredictiveNarrativeError(
            f"invalid invariant state for {invariant_id}"
        ) from exc
    evidence_ids = value.get("evidence_ids") or ()
    if isinstance(evidence_ids, (str, bytes)):
        raise PredictiveNarrativeError("evidence_ids must be a sequence")
    return EthicalInvariantResult(
        invariant_id=invariant_id,
        state=state,
        rationale=str(value.get("rationale") or ""),
        evidence_ids=_ordered_unique(str(item) for item in evidence_ids),
    )


def _normalize_local_validation(
    trajectory_id: str,
    state_record: Mapping[str, object],
    sequence: int,
    raw: Mapping[str, object],
) -> ProjectedStateValidation:
    if raw.get("canonical_vm81_mutation_performed") is True:
        raise PredictiveNarrativeError(
            "counterfactual local validation may not claim canonical VM81 mutation"
        )
    state_id = str(state_record.get("state_id") or "").strip()
    if not state_id:
        raise PredictiveNarrativeError("projected state_id is required")
    parent_raw = state_record.get("parent_state_id")
    parent_state_id = None if parent_raw is None else str(parent_raw)
    try:
        status = InvariantState(str(raw.get("status") or ""))
    except ValueError as exc:
        raise PredictiveNarrativeError(
            f"local validator returned invalid status for {state_id}"
        ) from exc
    invariant_rows = raw.get("invariant_results") or ()
    if isinstance(invariant_rows, (str, bytes)):
        raise PredictiveNarrativeError("invariant_results must be a sequence")
    invariant_rows = list(invariant_rows)
    if any(not isinstance(item, Mapping) for item in invariant_rows):
        raise PredictiveNarrativeError("every invariant_result must be a mapping")
    invariant_results = tuple(
        _parse_invariant_result(item) for item in invariant_rows
    )
    if status is not InvariantState.PASS and not invariant_results:
        raise PredictiveNarrativeError(
            "failed or unresolved local validation requires invariant evidence"
        )
    if any(item.state is InvariantState.FAIL for item in invariant_results):
        derived_status = InvariantState.FAIL
    elif any(item.state is InvariantState.UNRESOLVED for item in invariant_results):
        derived_status = InvariantState.UNRESOLVED
    else:
        derived_status = InvariantState.PASS
    if invariant_results and derived_status is not status:
        raise PredictiveNarrativeError(
            "local validation status must equal the worst supplied invariant state"
        )
    witness_rows = raw.get("witness_ids") or ()
    if isinstance(witness_rows, (str, bytes)):
        raise PredictiveNarrativeError("witness_ids must be a sequence")
    witness_ids = _ordered_unique(str(item) for item in witness_rows)
    hash216_reference = raw.get("hash216_reference")
    if hash216_reference is not None:
        hash216_reference = str(hash216_reference)
    if not witness_ids and not hash216_reference:
        raise PredictiveNarrativeError(
            "local validation requires a witness_id or Hash216 reference"
        )
    payload = {
        "trajectory_id": trajectory_id,
        "state_id": state_id,
        "parent_state_id": parent_state_id,
        "sequence": sequence,
        "status": status.value,
        "invariant_results": [item.to_dict() for item in invariant_results],
        "witness_ids": list(witness_ids),
        "hash216_reference": hash216_reference,
        "canonical_vm81_mutation_performed": False,
    }
    return ProjectedStateValidation(
        trajectory_id=trajectory_id,
        state_id=state_id,
        parent_state_id=parent_state_id,
        sequence=sequence,
        status=status,
        invariant_results=invariant_results,
        witness_ids=witness_ids,
        hash216_reference=hash216_reference,
        local_receipt_hash72=_reference_receipt("LOCAL_STATE_VALIDATION", payload),
    )


def _validate_ordered_states(
    trajectory_id: str,
    states: Sequence[Mapping[str, object]],
    local_validator: LocalStateValidator,
    context: PredictiveSimulationContext,
) -> Tuple[ProjectedStateValidation, ...]:
    if not states:
        raise PredictiveNarrativeError(
            f"trajectory {trajectory_id} requires at least one projected state"
        )
    if len(states) > MAX_STATES_PER_TRAJECTORY:
        raise PredictiveNarrativeError("trajectory exceeds projected-state bound")
    validations = []
    previous_state_id: Optional[str] = None
    seen = set()
    for sequence, state in enumerate(states):
        state_id = str(state.get("state_id") or "").strip()
        if not state_id or state_id in seen:
            raise PredictiveNarrativeError(
                f"trajectory {trajectory_id} has missing or duplicate state_id"
            )
        parent = state.get("parent_state_id")
        if sequence == 0:
            if parent not in (None, "", "ROOT"):
                raise PredictiveNarrativeError(
                    f"trajectory {trajectory_id} first state must originate at ROOT"
                )
        elif str(parent or "") != previous_state_id:
            raise PredictiveNarrativeError(
                f"trajectory {trajectory_id} state ordering/parent continuity failed"
            )
        request = {
            "schema": "HHS_PASS219_PROJECTED_STATE_LOCAL_VALIDATION_REQUEST_V1",
            "trajectory_id": trajectory_id,
            "sequence": sequence,
            "state": dict(state),
            "context": context.to_dict(),
            "canonical_vm81_mutation_requested": False,
        }
        raw = local_validator(request)
        if not isinstance(raw, Mapping):
            raise PredictiveNarrativeError("local validator must return a mapping")
        validations.append(
            _normalize_local_validation(trajectory_id, state, sequence, raw)
        )
        seen.add(state_id)
        previous_state_id = state_id
    return tuple(validations)


def simulate_and_evaluate(
    action: ActionCandidate,
    declared_invariants: Sequence[EthicalInvariantResult],
    epistemic: EpistemicAdequacyTrace,
    *,
    narrative_generator: NarrativeGenerator,
    local_validator: LocalStateValidator,
    trajectory_validator: TrajectoryValidator,
    context: PredictiveSimulationContext = PredictiveSimulationContext(),
    depth: ProbeDepthInputs = ProbeDepthInputs(),
    counterexamples: Sequence[StructuralCounterexampleRecord] = (),
    max_trajectories: int = 8,
) -> PredictiveNarrativeResult:
    """Generate, locally validate, and ethically evaluate downstream narratives.

    The generator never decides admission.  ``trajectory_validator`` maps each
    complete trajectory into the existing ethical finding surface, after every
    projected state has passed through ``local_validator``.  The final decision
    is made only by the inherited E01..E18 membrane in ``evaluate_action_v2``.
    """

    max_trajectories = _positive_bounded_int(
        max_trajectories,
        field="max_trajectories",
        maximum=MAX_TRAJECTORIES,
    )
    probe_contract = build_narrative_probe_contract(action)
    generation_request: Dict[str, object] = {
        "schema": "HHS_PASS219_LANE5_NARRATIVE_GENERATION_REQUEST_V1",
        "version": VERSION,
        "action": action.to_dict(),
        "probe_contract": probe_contract,
        "probe_depth": depth.to_dict(),
        "probe_depth_class": depth.probe_depth_class,
        "context": context.to_dict(),
        "hard_invariant_order": list(INVARIANT_ORDER),
        "max_trajectories": max_trajectories,
        "requirements": {
            "construct_counterfactual_downstream_narratives": True,
            "preserve_verbatim_equations": True,
            "emit_ordered_projected_states": True,
            "generator_may_decide_action_authority": False,
            "generator_may_promote_truth": False,
            "generator_may_mutate_vm81": False,
        },
    }
    generated = narrative_generator(generation_request)
    if not isinstance(generated, Mapping):
        raise PredictiveNarrativeError("narrative generator must return a mapping")
    if generated.get("action_authority_minted") is True:
        raise PredictiveNarrativeError("narrative generator attempted to mint authority")
    if generated.get("truth_promotion") is True:
        raise PredictiveNarrativeError("narrative generator attempted truth promotion")
    if generated.get("canonical_vm81_mutation_performed") is True:
        raise PredictiveNarrativeError("narrative generator attempted canonical mutation")

    raw_trajectories = generated.get("trajectories") or ()
    if isinstance(raw_trajectories, (str, bytes)):
        raise PredictiveNarrativeError("trajectories must be a sequence")
    raw_trajectories = list(raw_trajectories)
    if not raw_trajectories:
        raise PredictiveNarrativeError("narrative generator returned no trajectories")
    if len(raw_trajectories) > max_trajectories:
        raise PredictiveNarrativeError("generator exceeded max_trajectories")

    trajectories = []
    findings = []
    trajectory_ids = set()
    for raw_trajectory in raw_trajectories:
        if not isinstance(raw_trajectory, Mapping):
            raise PredictiveNarrativeError("trajectory must be a mapping")
        trajectory_id = str(raw_trajectory.get("trajectory_id") or "").strip()
        if not trajectory_id or trajectory_id in trajectory_ids:
            raise PredictiveNarrativeError("trajectory_id must be nonempty and unique")
        narrative = raw_trajectory.get("narrative")
        if not isinstance(narrative, str) or not narrative:
            raise PredictiveNarrativeError(
                f"trajectory {trajectory_id} requires nonempty narrative text"
            )
        states_raw = raw_trajectory.get("states") or ()
        if isinstance(states_raw, (str, bytes)):
            raise PredictiveNarrativeError("trajectory states must be a sequence")
        states_raw = list(states_raw)
        if any(not isinstance(item, Mapping) for item in states_raw):
            raise PredictiveNarrativeError("every projected state must be a mapping")
        states = [dict(item) for item in states_raw]
        validations = _validate_ordered_states(
            trajectory_id,
            states,
            local_validator,
            context,
        )
        validation_payload = [item.to_dict() for item in validations]
        trajectory_request = {
            "schema": "HHS_PASS219_TRAJECTORY_ETHICAL_EQUATION_REQUEST_V1",
            "trajectory_id": trajectory_id,
            "action": action.to_dict(),
            "narrative": narrative,
            "narrative_sha256": _sha256_text(narrative),
            "projected_states": [dict(item) for item in states],
            "local_validations": validation_payload,
            "context": context.to_dict(),
            "hard_invariant_order": list(INVARIANT_ORDER),
            "decision_must_use_existing_ethics_equations": True,
        }
        finding = trajectory_validator(trajectory_request)
        if not isinstance(finding, NarrativeFinding):
            raise PredictiveNarrativeError(
                "trajectory validator must return NarrativeFinding"
            )
        reserved_local_id = f"{trajectory_id}:local-validation"
        if finding.finding_id == reserved_local_id or finding.finding_id in {
            item.finding_id for item in findings
        }:
            raise PredictiveNarrativeError("trajectory findings must have unique finding_id")

        narrative_payload = {
            "trajectory_id": trajectory_id,
            "narrative_sha256": _sha256_text(narrative),
            "state_validation_receipts": [
                item.local_receipt_hash72 for item in validations
            ],
            "finding_id": finding.finding_id,
            "generated_narrative_unmodified": True,
        }
        local_invariant_results = tuple(
            invariant
            for validation in validations
            for invariant in validation.invariant_results
        )
        if local_invariant_results:
            findings.append(
                NarrativeFinding(
                    finding_id=f"{trajectory_id}:local-validation",
                    perspective="LANE5_LOCAL_PROJECTED_STATE_VALIDATION",
                    material=True,
                    invariant_results=local_invariant_results,
                    notes=(
                        "Exact projected-state validation folded into the existing "
                        "ethical invariant surface before trajectory admission."
                    ),
                )
            )

        trajectories.append(
            PredictiveTrajectory(
                trajectory_id=trajectory_id,
                narrative=narrative,
                narrative_sha256=_sha256_text(narrative),
                narrative_receipt_hash72=_reference_receipt(
                    "PREDICTIVE_TRAJECTORY", narrative_payload
                ),
                projected_state_validations=validations,
                finding=finding,
            )
        )
        findings.append(finding)
        trajectory_ids.add(trajectory_id)

    evaluation = evaluate_action_v2(
        action,
        declared_invariants,
        epistemic,
        tuple(findings),
        tuple(counterexamples),
        phase=EvaluationPhase.PROSPECTIVE,
    )
    payload = {
        "action_id": action.action_id,
        "probe_depth": depth.to_dict(),
        "probe_depth_class": depth.probe_depth_class,
        "context": context.to_dict(),
        "trajectory_receipts": [item.narrative_receipt_hash72 for item in trajectories],
        "ethical_trace_receipt": evaluation.trace_receipt_hash72,
        "ethical_decision": evaluation.evaluation.decision.value,
        "canonical_vm81_mutation_performed": False,
    }
    return PredictiveNarrativeResult(
        action_id=action.action_id,
        depth=depth,
        context=context,
        trajectories=tuple(trajectories),
        membrane_findings=tuple(findings),
        evaluation=evaluation,
        simulation_receipt_hash72=_reference_receipt(SCHEMA, payload),
    )


def simulate_admit_and_execute_local(
    action: ActionCandidate,
    declared_invariants: Sequence[EthicalInvariantResult],
    epistemic: EpistemicAdequacyTrace,
    *,
    narrative_generator: NarrativeGenerator,
    local_validator: LocalStateValidator,
    trajectory_validator: TrajectoryValidator,
    context: PredictiveSimulationContext = PredictiveSimulationContext(),
    depth: ProbeDepthInputs = ProbeDepthInputs(),
    counterexamples: Sequence[StructuralCounterexampleRecord] = (),
    max_trajectories: int = 8,
    controller: Optional[Any] = None,
) -> Dict[str, object]:
    """Run predictive simulation, then enter the inherited VM81 bridge.

    The bridge re-evaluates the same exact findings and remains the sole path
    that may invoke ``authorized_tick``.  A denied/held/simulation-only result
    therefore never calls the runtime.
    """

    simulation = simulate_and_evaluate(
        action,
        declared_invariants,
        epistemic,
        narrative_generator=narrative_generator,
        local_validator=local_validator,
        trajectory_validator=trajectory_validator,
        context=context,
        depth=depth,
        counterexamples=counterexamples,
        max_trajectories=max_trajectories,
    )
    from hhs_runtime.hhs_pass219_vm81_admission_bridge_v1 import (
        admit_and_execute_local,
    )

    admission = admit_and_execute_local(
        action,
        declared_invariants,
        epistemic,
        simulation.membrane_findings,
        counterexamples,
        controller=controller,
    )
    return {
        "schema": "HHS_PASS219_LANE5_PREDICTIVE_NARRATIVE_VM81_RESULT_V1",
        "version": VERSION,
        "simulation": simulation.to_dict(),
        "vm81_admission": admission,
        "ethical_decision": simulation.evaluation.evaluation.decision.value,
        "execution_candidate": simulation.execution_candidate,
        "canonical_vm81_mutation_performed": bool(
            admission.get("canonical_vm81_mutation_performed")
        ),
        "action_authority_minted": False,
    }


__all__ = [
    "VERSION",
    "SCHEMA",
    "TRAJECTORY_SCHEMA",
    "AUTHORITY",
    "MAX_ORDINAL",
    "MAX_TRAJECTORIES",
    "MAX_STATES_PER_TRAJECTORY",
    "PredictiveNarrativeError",
    "ProbeDepthInputs",
    "PredictiveSimulationContext",
    "ProjectedStateValidation",
    "PredictiveTrajectory",
    "PredictiveNarrativeResult",
    "simulate_and_evaluate",
    "simulate_admit_and_execute_local",
]
