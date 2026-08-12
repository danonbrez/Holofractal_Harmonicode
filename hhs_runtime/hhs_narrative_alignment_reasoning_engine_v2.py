"""Pass 218/219 R03/R04 ethical narrative refinement.

This module extends the Pass 218 v2.2.0 / Pass 219 v1.4.0 reference
evaluator without rewriting it. It implements two append-only refinements:

R03
    Observation integrity, causal-attribution integrity, and action-relevance
    sufficiency are typed independently. A failed or unresolved causal story
    may be quarantined from truth/action authority when the selected action
    does not rely on that story. A favorable outcome cannot promote an
    incorrect attribution into truth.

R04
    Counterexample memory defaults to structural-only retention. The retained
    record carries failure-mode structure, invariant delta, causal dependency
    pattern, and an opaque source-trace hash. It contains no verbatim narrative
    body and no personal identifier fields.

The module remains a deterministic, non-mutating reference layer. Canonical
runtime mutation remains exclusively downstream through VM81 authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from typing import Dict, Iterable, Mapping, Sequence, Tuple

from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import (
    ActionCandidate,
    EthicalInvariantResult,
    EthicalMembraneEvaluation,
    EvaluationPhase,
    InvariantState,
    NarrativeFinding,
    evaluate_action,
)

VERSION = "HHS_NARRATIVE_ALIGNMENT_REASONING_ENGINE_V2"
SCHEMA = "HHS_NARRATIVE_ALIGNMENT_TRACE_V2"
AUTHORITY = "REFERENCE_ONLY_NO_VM81_MUTATION_AUTHORITY"
STRUCTURAL_RETENTION_POLICY = "STRUCTURAL_ONLY_NO_VERBATIM_NO_PERSONAL_IDENTIFIERS"
E02 = "E02_EPISTEMIC_ADEQUACY"
E10 = "E10_TRUTH_MODALITY_INTEGRITY"


class CounterexampleRetentionDecision(str, Enum):
    RETAIN_STRUCTURAL_ONLY = "RETAIN_STRUCTURAL_ONLY"
    REJECT_EMPTY_STRUCTURE = "REJECT_EMPTY_STRUCTURE"


_STATE_RANK = {
    InvariantState.PASS: 0,
    InvariantState.UNRESOLVED: 1,
    InvariantState.FAIL: 2,
}


def _worse(left: InvariantState, right: InvariantState) -> InvariantState:
    return left if _STATE_RANK[left] >= _STATE_RANK[right] else right


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


def _reference_receipt(label: str, payload: Mapping[str, object]) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )
    return hash72_digest((VERSION, label, canonical), width=24)


@dataclass(frozen=True)
class EpistemicAdequacyTrace:
    """Independent exact epistemic substates for R03."""

    observation_integrity: InvariantState
    causal_attribution_integrity: InvariantState
    action_relevance_sufficiency: InvariantState
    causal_attribution_used_for_action: bool = False
    causal_attribution_asserted_as_truth: bool = False
    observation_evidence_ids: Tuple[str, ...] = ()
    causal_attribution_evidence_ids: Tuple[str, ...] = ()
    action_relevance_evidence_ids: Tuple[str, ...] = ()

    @property
    def causal_attribution_quarantined(self) -> bool:
        return (
            self.causal_attribution_integrity is not InvariantState.PASS
            and not self.causal_attribution_used_for_action
            and not self.causal_attribution_asserted_as_truth
        )

    def derived_e02_state(self) -> InvariantState:
        state = InvariantState.PASS
        state = _worse(state, self.observation_integrity)
        state = _worse(state, self.action_relevance_sufficiency)
        if (
            self.causal_attribution_used_for_action
            or self.causal_attribution_asserted_as_truth
        ):
            state = _worse(state, self.causal_attribution_integrity)
        return state

    def derived_e10_state(self) -> InvariantState:
        if (
            self.causal_attribution_asserted_as_truth
            and self.causal_attribution_integrity is not InvariantState.PASS
        ):
            return self.causal_attribution_integrity
        return InvariantState.PASS

    def to_dict(self) -> Dict[str, object]:
        return {
            "observation_integrity": self.observation_integrity.value,
            "causal_attribution_integrity": self.causal_attribution_integrity.value,
            "action_relevance_sufficiency": self.action_relevance_sufficiency.value,
            "causal_attribution_used_for_action": self.causal_attribution_used_for_action,
            "causal_attribution_asserted_as_truth": self.causal_attribution_asserted_as_truth,
            "causal_attribution_quarantined": self.causal_attribution_quarantined,
            "observation_evidence_ids": list(self.observation_evidence_ids),
            "causal_attribution_evidence_ids": list(self.causal_attribution_evidence_ids),
            "action_relevance_evidence_ids": list(self.action_relevance_evidence_ids),
        }


@dataclass(frozen=True)
class StructuralCounterexampleRecord:
    """R04 structural-only retained counterexample.

    No field exists for prose bodies, names, addresses, raw identifiers, or
    other verbatim narrative content. ``source_trace_hash72`` is an opaque
    receipt reference, not retained source text.
    """

    failure_mode_signature: str
    invariant_delta: Tuple[str, ...]
    causal_dependency_pattern: Tuple[str, ...]
    abstract_structure: Tuple[str, ...]
    source_trace_hash72: str
    source_had_verbatim_content: bool = False
    source_had_personal_identifiers: bool = False

    def __post_init__(self) -> None:
        if not self.failure_mode_signature.strip():
            raise ValueError("failure_mode_signature is required")
        if not self.source_trace_hash72.strip():
            raise ValueError("source_trace_hash72 is required")

    @property
    def decision(self) -> CounterexampleRetentionDecision:
        if not (
            self.invariant_delta
            or self.causal_dependency_pattern
            or self.abstract_structure
        ):
            return CounterexampleRetentionDecision.REJECT_EMPTY_STRUCTURE
        return CounterexampleRetentionDecision.RETAIN_STRUCTURAL_ONLY

    def payload_without_receipt(self) -> Dict[str, object]:
        return {
            "policy": STRUCTURAL_RETENTION_POLICY,
            "decision": self.decision.value,
            "failure_mode_signature": self.failure_mode_signature,
            "invariant_delta": list(_ordered_unique(self.invariant_delta)),
            "causal_dependency_pattern": list(_ordered_unique(self.causal_dependency_pattern)),
            "abstract_structure": list(_ordered_unique(self.abstract_structure)),
            "source_trace_hash72": self.source_trace_hash72,
            "source_had_verbatim_content": self.source_had_verbatim_content,
            "source_had_personal_identifiers": self.source_had_personal_identifiers,
            "verbatim_content_retained": False,
            "personal_identifier_fields_retained": False,
        }

    @property
    def structural_receipt_hash72(self) -> str:
        return _reference_receipt(
            "HHS_STRUCTURAL_COUNTEREXAMPLE_RECORD_V1",
            self.payload_without_receipt(),
        )

    def to_dict(self) -> Dict[str, object]:
        payload = self.payload_without_receipt()
        payload["structural_receipt_hash72"] = self.structural_receipt_hash72
        return payload


def _replace_or_append_invariant(
    declared: Sequence[EthicalInvariantResult],
    invariant_id: str,
    derived_state: InvariantState,
    rationale: str,
    evidence_ids: Tuple[str, ...],
) -> Tuple[EthicalInvariantResult, ...]:
    out = []
    replaced = False
    for item in declared:
        if item.invariant_id != invariant_id:
            out.append(item)
            continue
        replaced = True
        out.append(
            EthicalInvariantResult(
                invariant_id=invariant_id,
                state=_worse(item.state, derived_state),
                rationale=" | ".join(x for x in (item.rationale, rationale) if x),
                evidence_ids=_ordered_unique(tuple(item.evidence_ids) + tuple(evidence_ids)),
            )
        )
    if not replaced:
        out.append(
            EthicalInvariantResult(
                invariant_id=invariant_id,
                state=derived_state,
                rationale=rationale,
                evidence_ids=_ordered_unique(evidence_ids),
            )
        )
    return tuple(out)


def apply_epistemic_refinement(
    declared: Sequence[EthicalInvariantResult],
    epistemic: EpistemicAdequacyTrace,
) -> Tuple[EthicalInvariantResult, ...]:
    """Fold R03 substates into the inherited hard-invariant surface."""

    e02_evidence = _ordered_unique(
        tuple(epistemic.observation_evidence_ids)
        + tuple(epistemic.causal_attribution_evidence_ids)
        + tuple(epistemic.action_relevance_evidence_ids)
    )
    refined = _replace_or_append_invariant(
        declared,
        E02,
        epistemic.derived_e02_state(),
        "R03 independent epistemic fold: observation integrity; causal-attribution integrity; action-relevance sufficiency",
        e02_evidence,
    )
    refined = _replace_or_append_invariant(
        refined,
        E10,
        epistemic.derived_e10_state(),
        "R03 prohibits truth promotion of failed/unresolved causal attribution",
        tuple(epistemic.causal_attribution_evidence_ids),
    )
    return refined


@dataclass(frozen=True)
class EthicalNarrativeEvaluationV2:
    evaluation: EthicalMembraneEvaluation
    epistemic: EpistemicAdequacyTrace
    counterexamples: Tuple[StructuralCounterexampleRecord, ...]
    trace_receipt_hash72: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "authority": AUTHORITY,
            "evaluation": self.evaluation.to_dict(),
            "epistemic_adequacy": self.epistemic.to_dict(),
            "structural_counterexamples": [item.to_dict() for item in self.counterexamples],
            "retention_policy": STRUCTURAL_RETENTION_POLICY,
            "narrative_epistemic_status": "COUNTERFACTUAL_OR_FICTIONAL",
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_vm81_mutation_performed": False,
            "trace_receipt_hash72": self.trace_receipt_hash72,
        }


def evaluate_action_v2(
    action: ActionCandidate,
    declared_invariants: Sequence[EthicalInvariantResult],
    epistemic: EpistemicAdequacyTrace,
    findings: Sequence[NarrativeFinding] = (),
    counterexamples: Sequence[StructuralCounterexampleRecord] = (),
    *,
    phase: EvaluationPhase = EvaluationPhase.PROSPECTIVE,
) -> EthicalNarrativeEvaluationV2:
    refined = apply_epistemic_refinement(declared_invariants, epistemic)
    evaluation = evaluate_action(action, refined, findings, phase=phase)
    structural = tuple(counterexamples)
    payload = {
        "evaluation": evaluation.to_dict(),
        "epistemic_adequacy": epistemic.to_dict(),
        "structural_counterexamples": [item.to_dict() for item in structural],
        "retention_policy": STRUCTURAL_RETENTION_POLICY,
        "canonical_vm81_mutation_performed": False,
        "action_authority_minted": False,
        "truth_promotion": False,
    }
    receipt = _reference_receipt(SCHEMA, payload)
    return EthicalNarrativeEvaluationV2(
        evaluation=evaluation,
        epistemic=epistemic,
        counterexamples=structural,
        trace_receipt_hash72=receipt,
    )


__all__ = [
    "VERSION",
    "SCHEMA",
    "AUTHORITY",
    "STRUCTURAL_RETENTION_POLICY",
    "CounterexampleRetentionDecision",
    "EpistemicAdequacyTrace",
    "StructuralCounterexampleRecord",
    "EthicalNarrativeEvaluationV2",
    "apply_epistemic_refinement",
    "evaluate_action_v2",
]
