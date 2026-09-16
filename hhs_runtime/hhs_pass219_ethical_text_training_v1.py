"""Pass 219 ethical text-ingestion and invariant-normalization training cycle v1.

This module compiles a small prompt/response corpus into deterministic,
proof-carrying *candidate* training records.  It reuses the inherited WordNet
relation database and Pass 166 exact Word2Vec relation surface.  It never
promotes lexical/vector evidence to truth, never mutates VM81, and never grants
canonical learning or action authority.

The core separation is deliberate:

    lexical/vector evidence -> normalization/search priority
    theorem proof           -> irreversible prune authority
    Lane 5                  -> pre-commit alignment authorization/veto
    VM81                    -> canonical mutation/admission

Probability-like risk weighting is represented as an exact rational priority
weight.  It can cause HOLD/inspection, but cannot by itself authorize permanent
pruning.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol, Sequence
import json
import re

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import (
    WordRelationEntry,
    default_wordnet_paths,
    load_wordnet_relations,
    tokenize_words,
)
from hhs_runtime.pass150.genome import Hash216Genome
from hhs_runtime.pass218.genesis import ExactDistributionalRelation, Pass166Word2VecAdapter

PASS219_ETHICAL_TEXT_TRAINING_VERSION = "HHS-P219-ETHICAL-TEXT-TRAINING-V1"
PASS219_ETHICAL_TEXT_RECORD_SCHEMA = "HHS-P219-ETHICAL-TEXT-NORMALIZED-RECORD-V1"
PASS219_ETHICAL_TEXT_DATASET_SCHEMA = "HHS-P219-ETHICAL-TEXT-DATASET-CANDIDATE-V1"
ZERO_HASH216 = "0" * 64
MAX_TEXT_CHARS = 16_384
MAX_DATASET_RECORDS = 256
MAX_VECTOR_QUERY_TOKENS = 72

_SPACE = re.compile(r"\s+")
_TECH_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)*")


class EthicalTextTrainingError(RuntimeError):
    """Fail-closed error for the Pass 219 text training cycle."""


@dataclass(frozen=True)
class EthicalInvariantSpec:
    invariant_id: str
    concept_groups: tuple[tuple[str, ...], ...]
    contradiction_phrases: tuple[str, ...] = ()


@dataclass(frozen=True)
class PromptResponseExample:
    example_id: str
    prompt: str
    response: str
    invariants: tuple[str, ...]
    irreversible_misalignment_proof_hash216: str | None = None
    source_authority: str = "USER_AUTHORED_TRAINING_SEED"

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "PromptResponseExample":
        invariants = tuple(str(item).strip() for item in value.get("invariants", ()))
        item = cls(
            example_id=str(value.get("example_id", "")).strip(),
            prompt=str(value.get("prompt", "")).strip(),
            response=str(value.get("response", "")).strip(),
            invariants=invariants,
            irreversible_misalignment_proof_hash216=(
                str(value.get("irreversible_misalignment_proof_hash216")).strip().lower()
                if value.get("irreversible_misalignment_proof_hash216")
                else None
            ),
            source_authority=str(value.get("source_authority", "USER_AUTHORED_TRAINING_SEED")).strip(),
        )
        item.validate()
        return item

    def validate(self) -> None:
        if not self.example_id or len(self.example_id) > 128:
            raise EthicalTextTrainingError("P219_ETT_EXAMPLE_ID_INVALID")
        if not self.prompt or not self.response:
            raise EthicalTextTrainingError("P219_ETT_PROMPT_RESPONSE_REQUIRED")
        if len(self.prompt) > MAX_TEXT_CHARS or len(self.response) > MAX_TEXT_CHARS:
            raise EthicalTextTrainingError("P219_ETT_TEXT_TOO_LONG")
        if not self.invariants:
            raise EthicalTextTrainingError("P219_ETT_INVARIANTS_REQUIRED")
        unknown = sorted(set(self.invariants) - set(KNOWN_INVARIANTS))
        if unknown:
            raise EthicalTextTrainingError("P219_ETT_UNKNOWN_INVARIANT:" + ",".join(unknown))
        if not self.source_authority:
            raise EthicalTextTrainingError("P219_ETT_SOURCE_AUTHORITY_REQUIRED")
        if self.irreversible_misalignment_proof_hash216 is not None:
            proof = self.irreversible_misalignment_proof_hash216
            if not re.fullmatch(r"[0-9a-f]{64}", proof):
                raise EthicalTextTrainingError("P219_ETT_IRREVERSIBLE_PROOF_HASH216_INVALID")


class ExactSemanticProvider(Protocol):
    def exact_neighbors(
        self,
        token: str,
        *,
        top_k: int,
    ) -> Sequence[ExactDistributionalRelation]: ...


KNOWN_INVARIANTS: dict[str, EthicalInvariantSpec] = {
    "TRUTH_PRESERVATION": EthicalInvariantSpec(
        "TRUTH_PRESERVATION",
        (("truth", "evidence", "provenance", "state"), ("preserve", "preservation", "falsify", "falsification")),
        ("falsification is acceptable", "rewrite the evidence to obtain harmony"),
    ),
    "AGENCY_PRESERVATION": EthicalInvariantSpec(
        "AGENCY_PRESERVATION",
        (("agency", "choice", "consent"), ("preserve", "preservation", "boundary", "constraint")),
        ("agency may be erased", "coercion defines alignment"),
    ),
    "HARMONIC_DEBT_BOUNDARY": EthicalInvariantSpec(
        "HARMONIC_DEBT_BOUNDARY",
        (("debt",), ("boundary", "condition"), ("thermodynamic", "game-theoretic", "game"), ("open", "unresolved", "closure")),
        (
            "harmonic debt is karma",
            "harmonic debt is punishment",
            "harmonic debt means punishment",
            "debt justifies retribution",
            "harmonic debt is retribution",
        ),
    ),
    "PROBABILITY_NOT_PROOF": EthicalInvariantSpec(
        "PROBABILITY_NOT_PROOF",
        (("probability", "risk"), ("proof", "proven"), ("irreversible", "permanent"), ("prune", "pruning", "cancel", "cancellation")),
        (
            "probability is proof",
            "probability alone authorizes irreversible pruning",
            "high probability proves misalignment",
        ),
    ),
    "LANE5_VM81_AUTHORITY": EthicalInvariantSpec(
        "LANE5_VM81_AUTHORITY",
        (("lane",), ("authorization", "authorize", "veto"), ("vm81",), ("commit", "mutation", "admission")),
        ("lane 5 commits canonical state directly", "lane 5 bypasses vm81"),
    ),
    "RECURSIVE_READMISSION": EthicalInvariantSpec(
        "RECURSIVE_READMISSION",
        (("proof", "composition"), ("gate", "admission", "readmission", "re-admission"), ("candidate", "state", "composition")),
        ("valid proofs bypass the gates", "proof composition is automatically valid"),
    ),
    "STATE_CARRIED_ALIGNMENT": EthicalInvariantSpec(
        "STATE_CARRIED_ALIGNMENT",
        (("state",), ("constraint", "scope", "boundary"), ("history", "provenance"), ("hash216",)),
        (
            "rlhf defines canonical authority",
            "system prompt defines canonical authority",
            "training defines canonical authority",
        ),
    ),
    "INFORMATION_PRESERVATION": EthicalInvariantSpec(
        "INFORMATION_PRESERVATION",
        (("information",), ("destruction", "damage", "noise", "entropy"), ("sustainable", "evolution", "evolutionary")),
        ("destruction improves sustainable evolution",),
    ),
    "NON_RETRIBUTIVE_CLOSURE": EthicalInvariantSpec(
        "NON_RETRIBUTIVE_CLOSURE",
        (("closure", "close"), ("accountability", "repair", "boundary"), ("retribution", "punishment", "retaliation")),
        ("retribution is closure", "punishment creates thermodynamic closure"),
    ),
}


def _normalize_text(value: str) -> str:
    return _SPACE.sub(" ", str(value).strip().lower())


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _ratio_at_least(value: ExactDistributionalRelation, threshold: Fraction) -> bool:
    if value.sign <= 0:
        return False
    return value.squared_numerator * threshold.denominator >= threshold.numerator * value.squared_denominator


def load_prompt_response_jsonl(path: str | Path) -> tuple[PromptResponseExample, ...]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(str(source))
    records: list[PromptResponseExample] = []
    seen: set[str] = set()
    for line_number, raw in enumerate(source.read_text("utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise EthicalTextTrainingError(f"P219_ETT_JSON_INVALID:{line_number}") from exc
        if not isinstance(value, Mapping):
            raise EthicalTextTrainingError(f"P219_ETT_RECORD_OBJECT_REQUIRED:{line_number}")
        item = PromptResponseExample.from_mapping(value)
        if item.example_id in seen:
            raise EthicalTextTrainingError("P219_ETT_DUPLICATE_EXAMPLE_ID:" + item.example_id)
        seen.add(item.example_id)
        records.append(item)
    if not records:
        raise EthicalTextTrainingError("P219_ETT_DATASET_EMPTY")
    if len(records) > MAX_DATASET_RECORDS:
        raise EthicalTextTrainingError("P219_ETT_DATASET_BOUND")
    return tuple(records)


class EthicalTextTrainingCycle:
    """Compile prompt/response pairs into exact, theorem-scoped candidate records."""

    def __init__(
        self,
        relation_db: Mapping[str, WordRelationEntry],
        *,
        semantic_provider: ExactSemanticProvider | None,
        word2vec_model_id: str | None = None,
        top_k: int = 8,
        vector_similarity_threshold: Fraction = Fraction(1, 4),
        risk_hold_threshold: Fraction = Fraction(1, 4),
    ) -> None:
        if not relation_db:
            raise EthicalTextTrainingError("P219_ETT_WORDNET_REQUIRED")
        if top_k < 1 or top_k > 72:
            raise EthicalTextTrainingError("P219_ETT_TOP_K_OUT_OF_RANGE")
        if not Fraction(0, 1) <= vector_similarity_threshold <= Fraction(1, 1):
            raise EthicalTextTrainingError("P219_ETT_VECTOR_THRESHOLD_INVALID")
        if not Fraction(0, 1) <= risk_hold_threshold <= Fraction(1, 1):
            raise EthicalTextTrainingError("P219_ETT_RISK_THRESHOLD_INVALID")
        self.relation_db = relation_db
        self.semantic_provider = semantic_provider
        self.word2vec_model_id = word2vec_model_id
        self.top_k = top_k
        self.vector_similarity_threshold = vector_similarity_threshold
        self.risk_hold_threshold = risk_hold_threshold

    @classmethod
    def from_repository(
        cls,
        repository_root: str | Path,
        *,
        word2vec_service: Any | None,
        model_id: str | None = None,
        top_k: int = 8,
    ) -> "EthicalTextTrainingCycle":
        root = Path(repository_root).resolve()
        relation_db = load_wordnet_relations(
            default_wordnet_paths(root / "hhs_runtime"),
            require_all=True,
        )
        provider = None if word2vec_service is None else Pass166Word2VecAdapter(word2vec_service, model_id=model_id)
        return cls(
            relation_db,
            semantic_provider=provider,
            word2vec_model_id=model_id,
            top_k=top_k,
        )

    def _semantic_evidence(self, text: str) -> dict[str, Any]:
        lexical_tokens = tokenize_words(text)
        technical_tokens = [_normalize_text(item) for item in _TECH_TOKEN.findall(text)]
        tokens = tuple(dict.fromkeys([*lexical_tokens, *technical_tokens]))
        if len(tokens) > MAX_VECTOR_QUERY_TOKENS:
            vector_tokens = tokens[:MAX_VECTOR_QUERY_TOKENS]
            vector_token_truncated = True
        else:
            vector_tokens = tokens
            vector_token_truncated = False

        positive_terms: set[str] = set(tokens)
        antonym_terms: set[str] = set()
        lexical_receipts: list[dict[str, Any]] = []
        known = 0
        unknown = 0

        for token in tokens:
            entry = self.relation_db.get(token)
            if entry is None:
                unknown += 1
                continue
            known += 1
            synonyms = tuple(sorted({_normalize_text(item) for item in entry.synonyms if _normalize_text(item)}))
            hypernyms = tuple(sorted({_normalize_text(item) for item in entry.hypernyms if _normalize_text(item)}))
            hyponyms = tuple(sorted({_normalize_text(item) for item in entry.hyponyms if _normalize_text(item)}))
            antonyms = tuple(sorted({_normalize_text(item) for item in entry.antonyms if _normalize_text(item)}))
            positive_terms.update(synonyms)
            positive_terms.update(hypernyms)
            positive_terms.update(hyponyms)
            antonym_terms.update(antonyms)
            lexical_receipts.append(
                {
                    "token": token,
                    "entry_hash72": entry.entry_hash72,
                    "synonym_count": len(synonyms),
                    "hypernym_count": len(hypernyms),
                    "hyponym_count": len(hyponyms),
                    "antonym_count": len(antonyms),
                }
            )

        vector_receipts: list[dict[str, Any]] = []
        vector_failures: list[str] = []
        if self.semantic_provider is not None:
            for token in vector_tokens:
                try:
                    neighbors = self.semantic_provider.exact_neighbors(token, top_k=self.top_k)
                except Exception:
                    vector_failures.append(token)
                    continue
                accepted = []
                for relation in neighbors:
                    if _ratio_at_least(relation, self.vector_similarity_threshold):
                        normalized = _normalize_text(relation.target)
                        if normalized:
                            positive_terms.add(normalized)
                        accepted.append(
                            {
                                "target": normalized,
                                "sign": relation.sign,
                                "similarity_squared": {
                                    "numerator": relation.squared_numerator,
                                    "denominator": relation.squared_denominator,
                                },
                                "vector_identity": relation.vector_identity,
                            }
                        )
                vector_receipts.append({"token": token, "accepted_neighbors": accepted})

        token_count = len(tokens)
        lexical_coverage = Fraction(known, token_count) if token_count else Fraction(0, 1)
        body = {
            "tokens": list(tokens),
            "known_wordnet_tokens": known,
            "unknown_wordnet_tokens": unknown,
            "wordnet_coverage": _fraction_record(lexical_coverage),
            "positive_terms": sorted(positive_terms),
            "antonym_terms": sorted(antonym_terms),
            "lexical_receipts": lexical_receipts,
            "word2vec_model_id": self.word2vec_model_id,
            "word2vec_required_for_canonical_training_release": True,
            "word2vec_available": self.semantic_provider is not None,
            "word2vec_query_tokens": list(vector_tokens),
            "word2vec_query_truncated": vector_token_truncated,
            "word2vec_failures": vector_failures,
            "word2vec_successful_queries": len(vector_receipts),
            "vector_receipts": vector_receipts,
        }
        body["semantic_evidence_hash72"] = hash72_digest(
            {"domain": "HHS-P219-ETHICAL-TEXT-SEMANTIC-EVIDENCE-V1"},
            body,
        )
        return body

    @staticmethod
    def _concept_group_match(group: Iterable[str], terms: set[str]) -> bool:
        return any(_normalize_text(anchor) in terms for anchor in group)

    def _evaluate_invariant(
        self,
        spec: EthicalInvariantSpec,
        *,
        normalized_response: str,
        terms: set[str],
    ) -> dict[str, Any]:
        matched_groups = [
            self._concept_group_match(group, terms)
            for group in spec.concept_groups
        ]
        total = len(matched_groups)
        hits = sum(1 for value in matched_groups if value)
        coverage = Fraction(hits, total) if total else Fraction(1, 1)
        contradictions = [
            phrase
            for phrase in spec.contradiction_phrases
            if _normalize_text(phrase) in normalized_response
        ]
        if contradictions:
            status = -1
        elif hits == total:
            status = 1
        else:
            status = 0
        body = {
            "invariant_id": spec.invariant_id,
            "status": status,
            "matched_groups": matched_groups,
            "coverage": _fraction_record(coverage),
            "contradiction_phrases": contradictions,
            "contradiction_proof": bool(contradictions),
        }
        body["invariant_receipt_hash72"] = hash72_digest(
            {"domain": "HHS-P219-ETHICAL-INVARIANT-EVALUATION-V1"},
            body,
        )
        return body

    def normalize_example(
        self,
        example: PromptResponseExample,
        *,
        sequence: int,
        previous_hash216: str = ZERO_HASH216,
    ) -> dict[str, Any]:
        example.validate()
        prompt_evidence = self._semantic_evidence(example.prompt)
        response_evidence = self._semantic_evidence(example.response)
        response_terms = set(response_evidence["positive_terms"])
        normalized_response = _normalize_text(example.response)
        evaluations = [
            self._evaluate_invariant(
                KNOWN_INVARIANTS[invariant_id],
                normalized_response=normalized_response,
                terms=response_terms,
            )
            for invariant_id in example.invariants
        ]
        total_groups = sum(len(KNOWN_INVARIANTS[item].concept_groups) for item in example.invariants)
        matched_groups = sum(sum(1 for value in item["matched_groups"] if value) for item in evaluations)
        missing_groups = total_groups - matched_groups
        conflict_count = sum(1 for item in evaluations if item["status"] == -1)

        # Exact bounded risk weighting: useful for allocation/HOLD, never proof.
        risk_denominator = total_groups + len(evaluations)
        risk_numerator = min(risk_denominator, missing_groups + conflict_count)
        violation_risk = Fraction(risk_numerator, risk_denominator) if risk_denominator else Fraction(0, 1)

        has_conflict_proof = conflict_count > 0
        all_supported = all(item["status"] == 1 for item in evaluations)
        word2vec_ready = bool(
            response_evidence["word2vec_available"]
            and prompt_evidence["word2vec_available"]
            and response_evidence["word2vec_successful_queries"] > 0
            and prompt_evidence["word2vec_successful_queries"] > 0
        )

        if has_conflict_proof:
            lane5_class = -1
        elif all_supported and word2vec_ready:
            lane5_class = 1
        else:
            # Missing semantic proof or unavailable Word2Vec evidence is HOLD, not reject.
            lane5_class = 0

        # This text-training layer can reject a training candidate, but it never
        # has permanent causal-prune authority.  A Hash216 proof reference is
        # carried forward for Lane 5 verification; its presence is not itself
        # proof admission.
        permanent_prune_authorized = False
        proof_reference_present = example.irreversible_misalignment_proof_hash216 is not None
        if violation_risk >= self.risk_hold_threshold and lane5_class == 1:
            # Probability/risk may increase scrutiny but cannot manufacture -1.
            lane5_class = 0

        body = {
            "schema": PASS219_ETHICAL_TEXT_RECORD_SCHEMA,
            "version": PASS219_ETHICAL_TEXT_TRAINING_VERSION,
            "sequence": sequence,
            "example_id": example.example_id,
            "source_authority": example.source_authority,
            "prompt": example.prompt,
            "response": example.response,
            "declared_invariants": list(example.invariants),
            "prompt_semantic_evidence": prompt_evidence,
            "response_semantic_evidence": response_evidence,
            "invariant_evaluations": evaluations,
            "violation_risk_weight": _fraction_record(violation_risk),
            "risk_weight_semantics": "SEARCH_AND_HOLD_PRIORITY_NOT_IRREVERSIBLE_PROOF",
            "probability_weight_calibration": "STRUCTURAL_EXACT_PROXY_NOT_EMPIRICAL_PROBABILITY",
            "lane5_candidate_class": lane5_class,
            "permanent_prune_authorized": permanent_prune_authorized,
            "irreversible_misalignment_proof_hash216": example.irreversible_misalignment_proof_hash216,
            "irreversible_misalignment_proof_reference_present": proof_reference_present,
            "permanent_prune_requires_external_lane5_proof_admission": True,
            "candidate_only": True,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "vm81_commit_invoked": False,
            "requires_lane5_readmission_on_composition": True,
            "requires_vm81_admission_for_canonical_mutation": True,
            "previous_hash216": previous_hash216,
        }
        record_hash72 = hash72_digest(
            {"domain": PASS219_ETHICAL_TEXT_RECORD_SCHEMA},
            body,
        )
        with_hash72 = {**body, "record_hash72": record_hash72}
        positions = Hash216Genome.positions(
            _canonical_bytes(with_hash72),
            previous_root=previous_hash216,
            sequence=sequence,
        )
        hash216_root = Hash216Genome.root(positions)
        return {
            **with_hash72,
            "hash216_root": hash216_root,
            "hash216_position_count": len(positions),
        }

    def compile_dataset(
        self,
        examples: Sequence[PromptResponseExample],
        *,
        require_word2vec: bool = True,
    ) -> dict[str, Any]:
        if not examples:
            raise EthicalTextTrainingError("P219_ETT_DATASET_EMPTY")
        if len(examples) > MAX_DATASET_RECORDS:
            raise EthicalTextTrainingError("P219_ETT_DATASET_BOUND")
        ids = [item.example_id for item in examples]
        if len(ids) != len(set(ids)):
            raise EthicalTextTrainingError("P219_ETT_DUPLICATE_EXAMPLE_ID")
        if require_word2vec and self.semantic_provider is None:
            raise EthicalTextTrainingError("P219_ETT_WORD2VEC_REQUIRED")

        previous = ZERO_HASH216
        normalized: list[dict[str, Any]] = []
        for sequence, example in enumerate(examples):
            record = self.normalize_example(
                example,
                sequence=sequence,
                previous_hash216=previous,
            )
            normalized.append(record)
            previous = record["hash216_root"]

        admitted = [item["example_id"] for item in normalized if item["lane5_candidate_class"] == 1]
        held = [item["example_id"] for item in normalized if item["lane5_candidate_class"] == 0]
        rejected = [item["example_id"] for item in normalized if item["lane5_candidate_class"] == -1]
        body = {
            "schema": PASS219_ETHICAL_TEXT_DATASET_SCHEMA,
            "version": PASS219_ETHICAL_TEXT_TRAINING_VERSION,
            "record_count": len(normalized),
            "records": normalized,
            "admitted_training_candidates": admitted,
            "held_training_candidates": held,
            "rejected_training_candidates": rejected,
            "word2vec_required": require_word2vec,
            "word2vec_available": self.semantic_provider is not None,
            "known_invariant_ids": sorted(KNOWN_INVARIANTS),
            "final_hash216_root": previous,
            "training_semantics": "EXACT_INVARIANT_NORMALIZATION_CANDIDATE",
            "candidate_only": True,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "vm81_commit_invoked": False,
            "proof_composition_auto_admission": False,
        }
        body["dataset_hash72"] = hash72_digest(
            {"domain": PASS219_ETHICAL_TEXT_DATASET_SCHEMA},
            body,
        )
        return body

    def select_response_candidate(
        self,
        query: str,
        compiled_dataset: Mapping[str, Any],
        *,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """Rank admitted prompt prototypes with exact semantic Jaccard overlap.

        WordNet and Word2Vec expansions are already present in each normalized
        prompt evidence object.  This retrieval surface is intentionally
        candidate-only and cannot mint truth, action, or VM81 commit authority.
        """
        if top_k < 1 or top_k > 32:
            raise EthicalTextTrainingError("P219_ETT_RESPONSE_TOP_K_OUT_OF_RANGE")
        query_evidence = self._semantic_evidence(query)
        query_terms = set(query_evidence["positive_terms"])
        admitted_ids = set(compiled_dataset.get("admitted_training_candidates", ()))
        ranked: list[tuple[Fraction, str, Mapping[str, Any]]] = []
        for record in compiled_dataset.get("records", ()):  # type: ignore[assignment]
            example_id = str(record.get("example_id", ""))
            if example_id not in admitted_ids:
                continue
            prompt_terms = set(record["prompt_semantic_evidence"]["positive_terms"])
            union = query_terms | prompt_terms
            score = Fraction(len(query_terms & prompt_terms), len(union)) if union else Fraction(0, 1)
            ranked.append((score, example_id, record))
        ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
        results = [
            {
                "example_id": example_id,
                "score": _fraction_record(score),
                "response": record["response"],
                "record_hash72": record["record_hash72"],
                "hash216_root": record["hash216_root"],
                "declared_invariants": list(record["declared_invariants"]),
            }
            for score, example_id, record in ranked[:top_k]
        ]
        body = {
            "schema": "HHS-P219-ETHICAL-TEXT-RESPONSE-CANDIDATES-V1",
            "query": query,
            "query_semantic_evidence_hash72": query_evidence["semantic_evidence_hash72"],
            "results": results,
            "candidate_only": True,
            "truth_promotion": False,
            "action_authority_minted": False,
            "vm81_commit_invoked": False,
        }
        body["candidate_set_hash72"] = hash72_digest(
            {"domain": "HHS-P219-ETHICAL-TEXT-RESPONSE-CANDIDATES-V1"},
            body,
        )
        return body

    def compose_for_reflection(
        self,
        records: Sequence[Mapping[str, Any]],
        *,
        example_id: str,
        prompt: str,
        response: str,
        invariants: Sequence[str],
    ) -> dict[str, Any]:
        """Re-enter a proof composition through the same semantic/invariant gates."""
        if not records:
            raise EthicalTextTrainingError("P219_ETT_COMPOSITION_INPUT_REQUIRED")
        parent_roots = [str(item.get("hash216_root", "")) for item in records]
        if any(len(root) != 64 for root in parent_roots):
            raise EthicalTextTrainingError("P219_ETT_COMPOSITION_PARENT_HASH216_INVALID")
        composite = PromptResponseExample(
            example_id=example_id,
            prompt=prompt,
            response=response,
            invariants=tuple(invariants),
            source_authority="RECURSIVE_PROOF_COMPOSITION",
        )
        prior = Hash216Genome.root(
            Hash216Genome.positions(
                _canonical_bytes({"parent_hash216_roots": parent_roots}),
                previous_root=parent_roots[-1],
                sequence=len(records),
            )
        )
        result = self.normalize_example(
            composite,
            sequence=len(records),
            previous_hash216=prior,
        )
        return {
            **result,
            "composition_parent_hash216_roots": parent_roots,
            "composition_reentered_full_gate": True,
            "prior_validity_did_not_auto_admit_composition": True,
        }


def compile_repository_training_cycle(
    repository_root: str | Path,
    dataset_path: str | Path,
    *,
    word2vec_service: Any,
    model_id: str | None = None,
) -> dict[str, Any]:
    """Convenience entrypoint for a production repository-local cycle."""
    examples = load_prompt_response_jsonl(dataset_path)
    cycle = EthicalTextTrainingCycle.from_repository(
        repository_root,
        word2vec_service=word2vec_service,
        model_id=model_id,
    )
    return cycle.compile_dataset(examples, require_word2vec=True)


__all__ = [
    "EthicalInvariantSpec",
    "EthicalTextTrainingCycle",
    "EthicalTextTrainingError",
    "ExactSemanticProvider",
    "KNOWN_INVARIANTS",
    "PASS219_ETHICAL_TEXT_DATASET_SCHEMA",
    "PASS219_ETHICAL_TEXT_RECORD_SCHEMA",
    "PASS219_ETHICAL_TEXT_TRAINING_VERSION",
    "PromptResponseExample",
    "compile_repository_training_cycle",
    "load_prompt_response_jsonl",
]
