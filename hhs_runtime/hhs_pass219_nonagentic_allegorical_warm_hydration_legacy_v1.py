"""Pass 219 non-agentic allegorical warm-hydration reasoning layer v1.

This module composes four already-authorized candidate surfaces without
creating a new authority plane:

1. Pass 219 exact ethical text normalization (WordNet + exact Word2Vec);
2. Pass 218/219 narrative ethical reasoning v2 (reference-only diagnostics);
3. validated canonical 216-symbol Hash216 semantic states (e.g. Pass 218 I29);
4. Lane 5 20,020-cycle consecutive-prime modular Hash216 search.

The layer is deliberately allegorical and non-agentic.  It may generate and
rank fictional/counterfactual semantic correspondences, reuse a deterministic
warm projection cache, and propose reflective narrative paths.  It may not
mint truth, action authority, VM81 state, Hash72 receipts, canonical Hash216
state, or permanent causal-prune authority.

Important type boundary:

- ``training_genome_root_sha256`` is the 64-hex P150 Hash216Genome root used by
  the text-training cycle to bind an ordered training record;
- ``canonical_hash216`` is the HHS 216-symbol identity used by Lane 5 1.37 as
  three ordered Hash72 vector segments.

They are related metadata types and are never silently interchangeable.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Protocol, Sequence
import copy
import json
import re

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import HASH72_ALPHABET, validate_hash72
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v1 import (
    INVARIANT_ORDER,
    ActionCandidate,
    EthicalInvariantResult,
    EvaluationPhase,
    InvariantState,
)
from hhs_runtime.hhs_narrative_alignment_reasoning_engine_v2 import (
    EpistemicAdequacyTrace,
    StructuralCounterexampleRecord,
    evaluate_action_v2,
)
from hhs_runtime.hhs_pass219_ethical_text_training_v1 import (
    EthicalTextTrainingCycle,
    KNOWN_INVARIANTS,
    PromptResponseExample,
)

VERSION = "HHS-P219-NONAGENTIC-ALLEGORICAL-WARM-HYDRATION-V1"
PROBE_SCHEMA = "HHS-P219-ALLEGORICAL-ETHICAL-PROBE-V1"
HYDRATION_SCHEMA = "HHS-P219-ALLEGORICAL-WARM-HYDRATION-ROUTE-V1"
MAX_PROBE_CHARS = 32_768
MAX_CANDIDATES = 256
ZERO_TRAINING_GENOME_ROOT = "0" * 64

_NORMAL_SPACE = re.compile(r"\s+")
_HEX64 = re.compile(r"[0-9a-f]{64}")

# The theorem-level training invariants remain primary.  This map only allows
# the inherited v2 narrative diagnostic engine to see corresponding legacy
# dimensions; it does not redefine either invariant set.
THEOREM_TO_NARRATIVE_INVARIANT: dict[str, tuple[str, ...]] = {
    "TRUTH_PRESERVATION": ("E10_TRUTH_MODALITY_INTEGRITY",),
    "AGENCY_PRESERVATION": ("E08_AUTONOMY_PRESERVATION", "E09_NONCOERCION"),
    "HARMONIC_DEBT_BOUNDARY": ("E06_EXTERNALITY_CLOSURE",),
    "PROBABILITY_NOT_PROOF": ("E14_NO_PREDICTION_TO_AUTHORITY",),
    "LANE5_VM81_AUTHORITY": ("E18_SAFETY_RECURSION_NO_SELF_GRANT",),
    "RECURSIVE_READMISSION": ("E18_SAFETY_RECURSION_NO_SELF_GRANT",),
    "STATE_CARRIED_ALIGNMENT": (
        "E11_SCOPE_LOCALITY",
        "E18_SAFETY_RECURSION_NO_SELF_GRANT",
    ),
    "INFORMATION_PRESERVATION": (
        "E05_CONSEQUENCE_ALIGNMENT",
        "E06_EXTERNALITY_CLOSURE",
    ),
    "NON_RETRIBUTIVE_CLOSURE": ("E17_REPAIR_ROLLBACK_ADEQUACY",),
}

_STATE_RANK = {
    InvariantState.PASS: 0,
    InvariantState.UNRESOLVED: 1,
    InvariantState.FAIL: 2,
}


class AllegoricalWarmHydrationError(RuntimeError):
    """Fail-closed error for the non-agentic allegorical layer."""


class Lane5Hash216SearchProtocol(Protocol):
    def search_hash216(
        self,
        *,
        query_hash216: str,
        candidates: Sequence[Any],
        tick: int,
        cycle_index: int,
        top_k: int = 32,
    ) -> dict[str, Any]: ...


@dataclass(frozen=True)
class AllegoricalNarrativeProbe:
    probe_id: str
    prompt: str
    narrative_text: str
    invariants: tuple[str, ...]
    perspective: str = "FICTIONAL_OBSERVER"
    motifs: tuple[str, ...] = ()
    relation_families: tuple[str, ...] = ()
    modalities: tuple[str, ...] = ()

    def validated(self) -> "AllegoricalNarrativeProbe":
        probe_id = _required(self.probe_id, "P219_AWH_PROBE_ID")
        prompt = _required(self.prompt, "P219_AWH_PROMPT")
        narrative = _required(self.narrative_text, "P219_AWH_NARRATIVE")
        if len(prompt) > MAX_PROBE_CHARS or len(narrative) > MAX_PROBE_CHARS:
            raise AllegoricalWarmHydrationError("P219_AWH_PROBE_TEXT_TOO_LONG")
        invariants = _ordered_unique(self.invariants)
        if not invariants:
            raise AllegoricalWarmHydrationError("P219_AWH_INVARIANTS_REQUIRED")
        unknown = sorted(set(invariants) - set(KNOWN_INVARIANTS))
        if unknown:
            raise AllegoricalWarmHydrationError(
                "P219_AWH_UNKNOWN_INVARIANT:" + ",".join(unknown)
            )
        return AllegoricalNarrativeProbe(
            probe_id=probe_id,
            prompt=prompt,
            narrative_text=narrative,
            invariants=invariants,
            perspective=_upper(self.perspective or "FICTIONAL_OBSERVER"),
            motifs=_ordered_upper(self.motifs),
            relation_families=_ordered_upper(self.relation_families),
            modalities=_ordered_upper(self.modalities),
        )


@dataclass(frozen=True)
class ValidatedCorrespondenceState:
    candidate_id: str
    canonical_hash216: str
    validation_receipt_hash72: str
    semantic_terms: tuple[str, ...] = ()
    invariant_ids: tuple[str, ...] = ()
    relation_families: tuple[str, ...] = ()
    motifs: tuple[str, ...] = ()
    modalities: tuple[str, ...] = ()
    jump_span: int = 1
    lineage_signature: str = ""
    training_genome_root_sha256: str | None = None
    validated: bool = True

    def validated_copy(self) -> "ValidatedCorrespondenceState":
        candidate_id = _required(self.candidate_id, "P219_AWH_CANDIDATE_ID")
        canonical_hash216 = _validate_canonical_hash216(self.canonical_hash216)
        receipt = str(self.validation_receipt_hash72)
        if not validate_hash72(receipt):
            raise AllegoricalWarmHydrationError(
                "P219_AWH_VALIDATION_RECEIPT_HASH72_INVALID"
            )
        if self.validated is not True:
            raise AllegoricalWarmHydrationError("P219_AWH_UNVALIDATED_STATE")
        if isinstance(self.jump_span, bool) or not isinstance(self.jump_span, int):
            raise AllegoricalWarmHydrationError("P219_AWH_JUMP_SPAN_INTEGER_REQUIRED")
        if self.jump_span < 1:
            raise AllegoricalWarmHydrationError("P219_AWH_JUMP_SPAN_POSITIVE_REQUIRED")
        training_root = self.training_genome_root_sha256
        if training_root is not None:
            training_root = str(training_root).lower()
            if _HEX64.fullmatch(training_root) is None:
                raise AllegoricalWarmHydrationError(
                    "P219_AWH_TRAINING_GENOME_ROOT_INVALID"
                )
        return ValidatedCorrespondenceState(
            candidate_id=candidate_id,
            canonical_hash216=canonical_hash216,
            validation_receipt_hash72=receipt,
            semantic_terms=_ordered_lower(self.semantic_terms),
            invariant_ids=_ordered_upper(self.invariant_ids),
            relation_families=_ordered_upper(self.relation_families),
            motifs=_ordered_upper(self.motifs),
            modalities=_ordered_upper(self.modalities),
            jump_span=self.jump_span,
            lineage_signature=str(self.lineage_signature or receipt),
            training_genome_root_sha256=training_root,
            validated=True,
        )

    @classmethod
    def from_i29_validation(
        cls,
        candidate_id: str,
        validation: Mapping[str, Any],
        *,
        semantic_terms: Sequence[str] = (),
        invariant_ids: Sequence[str] = (),
        relation_families: Sequence[str] = (),
        motifs: Sequence[str] = (),
        modalities: Sequence[str] = (),
        jump_span: int = 1,
        training_genome_root_sha256: str | None = None,
    ) -> "ValidatedCorrespondenceState":
        expected_status = "VALIDATED_REVISABLE_HASH216_VM5184_TRANSITION_CANDIDATE"
        if validation.get("hash216_vm5184_validation_status") != expected_status:
            raise AllegoricalWarmHydrationError("P219_AWH_I29_STATUS_INVALID")
        required_true = (
            "hash216_vm5184_validation_ready",
            "hash216_continuation_verified",
            "semantic_transition_validated",
            "vm5184_candidate_projection_verified",
            "candidate_semantic_binding_verified",
        )
        for field in required_true:
            if validation.get(field) is not True:
                raise AllegoricalWarmHydrationError(
                    f"P219_AWH_I29_VALIDATION_REQUIRED:{field}"
                )
        forbidden_true = (
            "vm5184_authoritative_projection_invoked",
            "vm81_authorization_invoked",
            "atomic_promotion_invoked",
            "truth_promotion",
            "action_authority_minted",
            "canonical_learning_commit_invoked",
            "model_activation_invoked",
            "authoritative_float_weights_created",
        )
        for field in forbidden_true:
            if bool(validation.get(field)):
                raise AllegoricalWarmHydrationError(
                    f"P219_AWH_I29_AUTHORITY_DRIFT:{field}"
                )
        return cls(
            candidate_id=candidate_id,
            canonical_hash216=str(validation.get("pass218_validated_hash216") or ""),
            validation_receipt_hash72=str(
                validation.get("hash216_vm5184_validation_hash72") or ""
            ),
            semantic_terms=tuple(semantic_terms),
            invariant_ids=tuple(invariant_ids),
            relation_families=tuple(relation_families),
            motifs=tuple(motifs),
            modalities=tuple(modalities),
            jump_span=jump_span,
            lineage_signature=str(
                validation.get("hash216_vm5184_validation_hash72") or ""
            ),
            training_genome_root_sha256=training_genome_root_sha256,
            validated=True,
        ).validated_copy()


@dataclass(frozen=True)
class _Lane5Candidate:
    candidate_id: str
    hash216: str
    validated: bool
    jump_span: int
    lineage_signature: str


def _required(value: str, code: str) -> str:
    normalized = _NORMAL_SPACE.sub(" ", str(value).strip())
    if not normalized:
        raise AllegoricalWarmHydrationError(f"{code}_REQUIRED")
    return normalized


def _upper(value: str) -> str:
    return _NORMAL_SPACE.sub("_", str(value).strip().upper())


def _ordered_unique(values: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in values:
        value = _NORMAL_SPACE.sub(" ", str(raw).strip())
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return tuple(out)


def _ordered_upper(values: Sequence[str]) -> tuple[str, ...]:
    return _ordered_unique(tuple(_upper(value) for value in values if str(value).strip()))


def _ordered_lower(values: Sequence[str]) -> tuple[str, ...]:
    return _ordered_unique(
        tuple(_NORMAL_SPACE.sub(" ", str(value).strip().lower()) for value in values if str(value).strip())
    )


def _validate_canonical_hash216(value: str) -> str:
    candidate = str(value)
    if len(candidate) != 216:
        raise AllegoricalWarmHydrationError(
            "P219_AWH_CANONICAL_HASH216_REQUIRES_216_SYMBOLS"
        )
    alphabet = set(HASH72_ALPHABET)
    if any(symbol not in alphabet for symbol in candidate):
        raise AllegoricalWarmHydrationError("P219_AWH_CANONICAL_HASH216_ALPHABET_INVALID")
    return candidate


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _conditional_jaccard(query: Sequence[str], candidate: Sequence[str]) -> Fraction:
    left = set(query)
    if not left:
        return Fraction(1, 1)
    right = set(candidate)
    union = left | right
    return Fraction(len(left & right), len(union)) if union else Fraction(0, 1)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _to_legacy_state(status: int) -> InvariantState:
    if status == 1:
        return InvariantState.PASS
    if status == -1:
        return InvariantState.FAIL
    return InvariantState.UNRESOLVED


def _worse(left: InvariantState, right: InvariantState) -> InvariantState:
    return left if _STATE_RANK[left] >= _STATE_RANK[right] else right


def _legacy_invariants(
    evaluations: Sequence[Mapping[str, Any]],
) -> tuple[EthicalInvariantResult, ...]:
    states = {key: InvariantState.UNRESOLVED for key in INVARIANT_ORDER}
    sources: dict[str, list[str]] = {key: [] for key in INVARIANT_ORDER}
    for evaluation in evaluations:
        theorem_id = str(evaluation["invariant_id"])
        state = _to_legacy_state(int(evaluation["status"]))
        for legacy_id in THEOREM_TO_NARRATIVE_INVARIANT.get(theorem_id, ()):
            states[legacy_id] = _worse(states[legacy_id], state)
            sources[legacy_id].append(theorem_id)
    return tuple(
        EthicalInvariantResult(
            invariant_id=invariant_id,
            state=states[invariant_id],
            rationale=(
                "Pass219 theorem bridge from: " + ",".join(sources[invariant_id])
                if sources[invariant_id]
                else "Not asserted by this bounded allegorical probe"
            ),
        )
        for invariant_id in INVARIANT_ORDER
    )


class Pass219NonAgenticAllegoricalWarmHydration:
    """Fictional semantic reflection + exact candidate-only warm routing."""

    def __init__(
        self,
        training_cycle: EthicalTextTrainingCycle,
        lane5_search: Lane5Hash216SearchProtocol,
    ) -> None:
        self.training_cycle = training_cycle
        self.lane5_search = lane5_search
        self._warm_cache: dict[str, dict[str, Any]] = {}

    def compile_probe(self, probe: AllegoricalNarrativeProbe) -> dict[str, Any]:
        validated = probe.validated()
        training_record = self.training_cycle.normalize_example(
            PromptResponseExample(
                example_id=f"allegory:{validated.probe_id}",
                prompt=validated.prompt,
                response=validated.narrative_text,
                invariants=validated.invariants,
                source_authority="NONAGENTIC_ALLEGORICAL_FICTION",
            ),
            sequence=0,
            previous_hash216=ZERO_TRAINING_GENOME_ROOT,
        )

        declarations = _legacy_invariants(training_record["invariant_evaluations"])
        conflicts = [
            item
            for item in training_record["invariant_evaluations"]
            if int(item["status"]) == -1
        ]
        counterexamples = tuple(
            StructuralCounterexampleRecord(
                failure_mode_signature=(
                    "ALLEGORICAL_THEOREM_CONFLICT:" + str(item["invariant_id"])
                ),
                invariant_delta=(str(item["invariant_id"]),),
                causal_dependency_pattern=(
                    "FICTIONAL_PROBE",
                    "THEOREM_INVARIANT_GATE",
                    "REQUIRES_READMISSION",
                ),
                abstract_structure=(
                    "ALLEGORICAL_COUNTEREXAMPLE",
                    "NONAGENTIC_DIAGNOSTIC_ONLY",
                ),
                source_trace_hash72=str(training_record["record_hash72"]),
            )
            for item in conflicts
        )
        epistemic = EpistemicAdequacyTrace(
            observation_integrity=InvariantState.UNRESOLVED,
            causal_attribution_integrity=InvariantState.UNRESOLVED,
            action_relevance_sufficiency=InvariantState.PASS,
            causal_attribution_used_for_action=False,
            causal_attribution_asserted_as_truth=False,
            observation_evidence_ids=(str(training_record["record_hash72"]),),
        )
        fiction_action = ActionCandidate(
            action_id=f"fiction-simulation:{validated.probe_id}",
            intent="ALLEGORICAL_SEMANTIC_REFLECTION",
            requested_scope=("FICTION_SIMULATION_ONLY",),
            minimum_necessary_scope=("FICTION_SIMULATION_ONLY",),
            granted_scope=("FICTION_SIMULATION_ONLY",),
            external_effect_set=(),
            continuation_conditions=("NO_EXTERNAL_SIDE_EFFECTS", "REENTER_LANE5_BEFORE_USE"),
            reversible=True,
            authority_source_ids=("PASS219_NONAGENTIC_ALLEGORICAL_LAYER",),
            originating_context=validated.perspective,
        )
        narrative_diagnostic = evaluate_action_v2(
            fiction_action,
            declarations,
            epistemic,
            findings=(),
            counterexamples=counterexamples,
            phase=EvaluationPhase.PROSPECTIVE,
        ).to_dict()

        body = {
            "schema": PROBE_SCHEMA,
            "version": VERSION,
            "probe_id": validated.probe_id,
            "prompt": validated.prompt,
            "narrative_text": validated.narrative_text,
            "narrative_epistemic_status": "FICTIONAL_COUNTERFACTUAL_ALLEGORY",
            "perspective": validated.perspective,
            "motifs": list(validated.motifs),
            "relation_families": list(validated.relation_families),
            "modalities": list(validated.modalities),
            "declared_invariants": list(validated.invariants),
            "text_training_record": training_record,
            "training_genome_root_sha256": training_record["hash216_root"],
            "canonical_hash216_identity": None,
            "narrative_reasoning_v2": narrative_diagnostic,
            "fiction_scope": "FICTION_SIMULATION_ONLY",
            "narrative_plane_permitted": True,
            "relational_cognition_permitted": True,
            "agentic_plane_permitted": False,
            "truth_promotion_permitted": False,
            "canonical_vm81_mutation_permitted": False,
            "canonical_hash72_mint_permitted": False,
            "canonical_hash216_mint_permitted": False,
            "permanent_prune_authorized": False,
            "requires_lane5_readmission_before_downstream_use": True,
            "candidate_only": True,
        }
        body["allegorical_probe_hash72"] = hash72_digest(
            {"domain": PROBE_SCHEMA},
            body,
        )
        return body

    @staticmethod
    def _correspondence(
        probe: Mapping[str, Any],
        state: ValidatedCorrespondenceState,
    ) -> dict[str, Any]:
        text_record = probe["text_training_record"]
        semantic_terms = tuple(
            str(item)
            for item in text_record["response_semantic_evidence"]["positive_terms"]
        )
        probe_invariants = tuple(str(item) for item in probe["declared_invariants"])
        probe_relations = tuple(str(item) for item in probe["relation_families"])
        probe_motifs = tuple(str(item) for item in probe["motifs"])
        probe_modalities = tuple(
            sorted(
                set(str(item) for item in probe["modalities"])
                | {
                    "ALLEGORICAL_FICTION",
                    "ETHICAL_INVARIANT",
                    "WORDNET",
                    "WORD2VEC",
                    "HASH216",
                }
            )
        )
        axes = {
            "semantic": _conditional_jaccard(semantic_terms, state.semantic_terms),
            "invariant": _conditional_jaccard(probe_invariants, state.invariant_ids),
            "relation_family": _conditional_jaccard(probe_relations, state.relation_families),
            "motif": _conditional_jaccard(probe_motifs, state.motifs),
            "modality": _conditional_jaccard(probe_modalities, state.modalities),
        }
        tensor_score = Fraction(1, 1)
        for score in axes.values():
            tensor_score *= score
        body = {
            "candidate_id": state.candidate_id,
            "axes": {key: _fraction_record(value) for key, value in axes.items()},
            "tensor_score": _fraction_record(tensor_score),
            "positive_axis_count": sum(1 for value in axes.values() if value > 0),
            "exact_no_float": True,
        }
        body["correspondence_hash72"] = hash72_digest(
            {"domain": "HHS-P219-ALLEGORICAL-CORRESPONDENCE-TENSOR-V1"},
            body,
        )
        return body

    def warm_hydrate(
        self,
        *,
        compiled_probe: Mapping[str, Any],
        current_hash216: str,
        candidates: Sequence[ValidatedCorrespondenceState],
        tick: int,
        cycle_index: int,
        top_k: int = 16,
    ) -> dict[str, Any]:
        if compiled_probe.get("schema") != PROBE_SCHEMA:
            raise AllegoricalWarmHydrationError("P219_AWH_PROBE_SCHEMA_INVALID")
        if compiled_probe.get("agentic_plane_permitted") is not False:
            raise AllegoricalWarmHydrationError("P219_AWH_AGENTIC_PLANE_MUST_BE_CLOSED")
        if compiled_probe.get("truth_promotion_permitted") is not False:
            raise AllegoricalWarmHydrationError("P219_AWH_TRUTH_PLANE_MUST_BE_CLOSED")
        query = _validate_canonical_hash216(current_hash216)
        if isinstance(top_k, bool) or not isinstance(top_k, int) or not 1 <= top_k <= MAX_CANDIDATES:
            raise AllegoricalWarmHydrationError("P219_AWH_TOP_K_OUT_OF_RANGE")
        if len(candidates) > MAX_CANDIDATES:
            raise AllegoricalWarmHydrationError("P219_AWH_CANDIDATE_BOUND")
        validated: list[ValidatedCorrespondenceState] = []
        seen_ids: set[str] = set()
        seen_hashes: set[str] = set()
        for raw in candidates:
            state = raw.validated_copy()
            if state.candidate_id in seen_ids or state.canonical_hash216 in seen_hashes:
                raise AllegoricalWarmHydrationError("P219_AWH_DUPLICATE_CANDIDATE")
            seen_ids.add(state.candidate_id)
            seen_hashes.add(state.canonical_hash216)
            validated.append(state)

        correspondence = {
            state.candidate_id: self._correspondence(compiled_probe, state)
            for state in validated
        }
        cache_payload = {
            "probe_hash72": compiled_probe["allegorical_probe_hash72"],
            "query_hash216": query,
            "candidate_hash216": [state.canonical_hash216 for state in validated],
            "candidate_metadata": [
                {
                    "candidate_id": state.candidate_id,
                    "receipt": state.validation_receipt_hash72,
                    "semantic_terms": list(state.semantic_terms),
                    "invariant_ids": list(state.invariant_ids),
                    "relation_families": list(state.relation_families),
                    "motifs": list(state.motifs),
                    "modalities": list(state.modalities),
                    "jump_span": state.jump_span,
                    "training_genome_root_sha256": state.training_genome_root_sha256,
                }
                for state in validated
            ],
            "tick": int(tick),
            "cycle_index": int(cycle_index),
            "top_k": top_k,
        }
        cache_key = hash72_digest(
            {"domain": "HHS-P219-ALLEGORICAL-WARM-CACHE-KEY-V1"},
            cache_payload,
        )
        if cache_key in self._warm_cache:
            reused = copy.deepcopy(self._warm_cache[cache_key])
            reused["warm_reuse"] = True
            reused["warm_cache_hit"] = True
            return reused

        lane5_candidates = [
            _Lane5Candidate(
                candidate_id=state.candidate_id,
                hash216=state.canonical_hash216,
                validated=True,
                jump_span=state.jump_span,
                lineage_signature=state.lineage_signature,
            )
            for state in validated
        ]
        lane5 = self.lane5_search.search_hash216(
            query_hash216=query,
            candidates=lane5_candidates,
            tick=int(tick),
            cycle_index=int(cycle_index),
            top_k=len(lane5_candidates),
        )
        if lane5.get("candidate_only") is not True:
            raise AllegoricalWarmHydrationError("P219_AWH_LANE5_CANDIDATE_ONLY_REQUIRED")
        if bool(lane5.get("gpu_may_commit_hash72")) or bool(
            lane5.get("gpu_may_commit_hash216")
        ) or bool(lane5.get("canonical_vm81_mutation_authority")):
            raise AllegoricalWarmHydrationError("P219_AWH_LANE5_AUTHORITY_DRIFT")

        by_state = {state.candidate_id: state for state in validated}
        combined: list[dict[str, Any]] = []
        for route in lane5.get("ranked", []):
            candidate_id = str(route["candidate_id"])
            if candidate_id not in by_state or candidate_id not in correspondence:
                raise AllegoricalWarmHydrationError("P219_AWH_LANE5_UNKNOWN_CANDIDATE")
            score_record = correspondence[candidate_id]
            score = Fraction(
                int(score_record["tensor_score"]["numerator"]),
                int(score_record["tensor_score"]["denominator"]),
            )
            combined.append(
                {
                    "candidate_id": candidate_id,
                    "canonical_hash216": by_state[candidate_id].canonical_hash216,
                    "validation_receipt_hash72": by_state[candidate_id].validation_receipt_hash72,
                    "training_genome_root_sha256": by_state[candidate_id].training_genome_root_sha256,
                    "correspondence": score_record,
                    "lane5_hash216_distance": int(route["hash216_distance"]),
                    "jump_span": int(route["jump_span"]),
                    "phase_stream": int(route["phase_stream"]),
                    "routed_slot": int(route["routed_slot"]),
                    "_tensor_score": score,
                }
            )
        combined.sort(
            key=lambda item: (
                -item["_tensor_score"],
                item["lane5_hash216_distance"],
                -item["jump_span"],
                item["routed_slot"],
                item["candidate_id"],
            )
        )
        pathway = []
        for rank, item in enumerate(combined[: min(top_k, len(combined))], start=1):
            clean = dict(item)
            clean.pop("_tensor_score", None)
            clean["path_rank"] = rank
            pathway.append(clean)

        body = {
            "schema": HYDRATION_SCHEMA,
            "version": VERSION,
            "allegorical_probe_hash72": compiled_probe["allegorical_probe_hash72"],
            "current_canonical_hash216": query,
            "training_genome_root_type": "P150_HASH216GENOME_ROOT_SHA256_64_HEX",
            "lane5_hash216_type": "CANONICAL_216_SYMBOL_3XHASH72",
            "types_interchangeable": False,
            "candidate_count": len(validated),
            "pathway": pathway,
            "lane5_phase_address": lane5.get("phase_address"),
            "lane5_prime_matrix": lane5.get("prime_matrix"),
            "lane5_prime_offsets": lane5.get("prime_offsets"),
            "lane5_prime_route": lane5.get("prime_route"),
            "lane5_cycle_index": lane5.get("cycle_index", int(cycle_index)),
            "lane5_tick": lane5.get("tick", int(tick)),
            "optimization_semantics": (
                "EXACT_METADATA_CORRESPONDENCE_TENSOR_THEN_LANE5_PRIME_MODULAR_HASH216_ROUTE"
            ),
            "warm_cache_key_hash72": cache_key,
            "warm_reuse": False,
            "warm_cache_hit": False,
            "warm_cache_is_noncanonical_projection": True,
            "narrative_epistemic_status": "FICTIONAL_COUNTERFACTUAL_ALLEGORY",
            "agentic_plane_permitted": False,
            "truth_promotion_permitted": False,
            "canonical_vm81_mutation_permitted": False,
            "canonical_hash72_mint_permitted": False,
            "canonical_hash216_mint_permitted": False,
            "permanent_prune_authorized": False,
            "requires_lane5_readmission_on_reuse_or_composition": True,
            "requires_vm81_admission_for_any_canonical_mutation": True,
            "candidate_only": True,
        }
        body["hydration_receipt_hash72"] = hash72_digest(
            {"domain": HYDRATION_SCHEMA},
            body,
        )
        self._warm_cache[cache_key] = copy.deepcopy(body)
        return body

    def clear_warm_cache(self) -> None:
        self._warm_cache.clear()

    def status(self) -> dict[str, Any]:
        return {
            "version": VERSION,
            "warm_cache_entries": len(self._warm_cache),
            "narrative_plane": "FICTIONAL_COUNTERFACTUAL_ALLEGORY",
            "relational_cognition_plane": "CANDIDATE_ONLY",
            "agentic_plane_permitted": False,
            "truth_promotion_permitted": False,
            "canonical_vm81_mutation_permitted": False,
            "canonical_hash72_mint_permitted": False,
            "canonical_hash216_mint_permitted": False,
            "permanent_prune_authorized": False,
        }


def default_lane5_search(*, backend: str = "CPU_REFERENCE") -> Lane5Hash216SearchProtocol:
    """Lazy production binding to the existing Lane 5 1.37 optimizer."""
    from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import (
        Pass219Lane5Hash216GPUPhaseInterlaceOptimizer,
    )

    return Pass219Lane5Hash216GPUPhaseInterlaceOptimizer(backend=backend)


__all__ = [
    "AllegoricalNarrativeProbe",
    "AllegoricalWarmHydrationError",
    "HYDRATION_SCHEMA",
    "Lane5Hash216SearchProtocol",
    "PROBE_SCHEMA",
    "Pass219NonAgenticAllegoricalWarmHydration",
    "THEOREM_TO_NARRATIVE_INVARIANT",
    "VERSION",
    "ValidatedCorrespondenceState",
    "default_lane5_search",
]
