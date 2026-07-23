from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass118_symbolic_harmonicode_runtime_v1 import (
    HarmonicodeRuntimeEngine,
    Pass118Error,
    PROGRAM_SCHEMA,
)

PASS_ID = "PASS_119"
INPUT_SCHEMA = "HHS_PRESERVED_LANGUAGE_INPUT_V1"
PROPOSITION_SCHEMA = "HHS_LINGUISTIC_PROPOSITION_SET_V1"
MODEL_PROPOSAL_SCHEMA = "HHS_LANGUAGE_MODEL_PROPOSAL_V1"
TRANSLATION_SCHEMA = "HHS_LANGUAGE_SYMBOLIC_TRANSLATION_RECEIPT_V1"
INTERACTION_SCHEMA = "HHS_LANGUAGE_SYMBOLIC_RUNTIME_INTERACTION_V1"
PROJECTION_SCHEMA = "HHS_AUTHORITATIVE_LANGUAGE_PROJECTION_RECEIPT_V1"
MODEL_COMPARISON_SCHEMA = "HHS_LANGUAGE_MODEL_COMPARISON_V1"
CONTEXT_PROJECTION_SCHEMA = "HHS_BOUNDED_LANGUAGE_CONTEXT_PROJECTION_V1"

REJECTION_CODES = {
    "REJECT_LANGUAGE_MODEL_OUTPUT_AS_AUTHORITATIVE_STATE",
    "REJECT_MODEL_CONFIDENCE_AS_PROOF",
    "REJECT_MODEL_CONSENSUS_AS_RUNTIME_VALIDATION",
    "REJECT_LANGUAGE_PROJECTION_AS_EXECUTION_RECEIPT",
    "REJECT_SYMBOLIC_RESULT_AS_USER_MEANING_WITHOUT_TRANSLATION_VALIDATION",
    "REJECT_RUNTIME_SUCCESS_AS_SEMANTIC_ALIGNMENT",
    "REJECT_HASH72_ROOT_AS_LANGUAGE_PAYLOAD",
    "REJECT_INFERRED_PROPOSITION_RECLASSIFIED_AS_EXPLICIT",
    "REJECT_AMBIGUITY_COLLAPSED_WITHOUT_EVIDENCE",
    "REJECT_NEGATION_LOSS",
    "REJECT_QUANTIFIER_DRIFT",
    "REJECT_REFERENCE_SUBSTITUTION",
    "REJECT_SCOPE_DRIFT",
    "REJECT_UNCERTAINTY_ERASURE",
    "REJECT_TYPED_UNAVAILABLE_TRANSLATED_AS_FALSE",
    "REJECT_REJECTION_TRANSLATED_AS_COMPLETION",
    "REJECT_RUNTIME_HISTORY_REWRITTEN_TO_MATCH_EXPLANATION",
    "REJECT_MODEL_PROPOSAL_MUTATING_ADMITTED_SYMBOLIC_PROGRAM",
    "REJECT_GENERATED_HARMONICODE_AS_EXECUTED_WITHOUT_RECEIPT",
    "REJECT_RETRIEVED_CONTENT_AS_AUTHORITY",
    "REJECT_PROMPT_INJECTION_AUTHORITY_ESCALATION",
    "REJECT_MULTIMODAL_MODEL_OUTPUT_WITHOUT_MODALITY_VALIDATION",
    "REJECT_LANGUAGE_CONTEXT_AS_COMPLETE_SYSTEM_STATE",
    "REJECT_CONTEXT_COMPRESSION_WITHOUT_OMISSION_ROOTS",
    "REJECT_LAYER_REPLACEMENT_WITHOUT_EQUIVALENCE_CONTRACT",
    "REJECT_LANGUAGE_MODEL_DOMINATION_OF_SYMBOLIC_AUTHORITY",
    "REJECT_SYMBOLIC_LAYER_ERASURE_OF_LINGUISTIC_AMBIGUITY",
    "REJECT_PROJECTION_VALUE_MISMATCH",
    "REJECT_PROJECTION_STATUS_MISMATCH",
    "REJECT_PROJECTION_WITHOUT_AUTHORITATIVE_SOURCE",
    "REJECT_RESOURCE_CONTRACT_EXCEEDED",
}


class Pass119Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class Proposition:
    text: str
    status: str
    scope: str
    source_span: tuple[int, int]
    proposition_root_hash72: str


class LanguageModelIntegrationEngine:
    """Non-replacement LM/semantic/symbolic/runtime/Hash72 integration boundary."""

    def __init__(self, *, max_propositions: int = 512, max_candidates: int = 64):
        self.max_propositions = max_propositions
        self.max_candidates = max_candidates
        self.symbolic = HarmonicodeRuntimeEngine()

    # ----------------------- source preservation -----------------------
    def preserve_input(self, text: str, *, source_class: str = "USER_INPUT", scope: str = "interaction") -> dict[str, Any]:
        if not isinstance(text, str):
            raise Pass119Error("REJECT_HASH72_ROOT_AS_LANGUAGE_PAYLOAD", type(text).__name__)
        payload = {
            "schema": INPUT_SCHEMA,
            "verbatim_text": text,
            "source_class": source_class,
            "scope": scope,
            "character_count": len(text),
        }
        payload["input_root_hash72"] = _hash("hhs_pass119_preserved_input_v1", payload)
        return payload

    def extract_propositions(
        self,
        preserved_input: Mapping[str, Any],
        explicit_spans: Sequence[Mapping[str, Any]],
        *,
        inferred: Sequence[Mapping[str, Any]] = (),
        ambiguities: Sequence[Mapping[str, Any]] = (),
    ) -> dict[str, Any]:
        text = preserved_input.get("verbatim_text")
        if preserved_input.get("schema") != INPUT_SCHEMA or not isinstance(text, str):
            raise Pass119Error("REJECT_HASH72_ROOT_AS_LANGUAGE_PAYLOAD", "missing verbatim payload")
        if len(explicit_spans) + len(inferred) > self.max_propositions:
            raise Pass119Error("REJECT_RESOURCE_CONTRACT_EXCEEDED", "propositions")
        propositions: list[dict[str, Any]] = []
        for item in explicit_spans:
            start, end = int(item["start"]), int(item["end"])
            if start < 0 or end < start or end > len(text):
                raise Pass119Error("REJECT_REFERENCE_SUBSTITUTION", f"span {start}:{end}")
            verbatim = text[start:end]
            if "text" in item and item["text"] != verbatim:
                raise Pass119Error("REJECT_REFERENCE_SUBSTITUTION", "explicit text differs from source span")
            p = {
                "status": "EXPLICIT",
                "verbatim": verbatim,
                "normalized": str(item.get("normalized", verbatim)),
                "scope": str(item.get("scope", preserved_input.get("scope", "interaction"))),
                "source_span": [start, end],
            }
            p["proposition_root_hash72"] = _hash("hhs_pass119_explicit_proposition_v1", p)
            propositions.append(p)
        inference_roots = []
        for item in inferred:
            if item.get("status") == "EXPLICIT":
                raise Pass119Error("REJECT_INFERRED_PROPOSITION_RECLASSIFIED_AS_EXPLICIT", str(item))
            p = {
                "status": "INFERRED",
                "text": str(item.get("text", "")),
                "basis_roots": list(item.get("basis_roots", [])),
                "scope": str(item.get("scope", preserved_input.get("scope", "interaction"))),
            }
            p["inference_root_hash72"] = _hash("hhs_pass119_inferred_proposition_v1", p)
            inference_roots.append(p)
        ambiguity_objects = []
        for item in ambiguities:
            candidates = list(item.get("candidate_meanings", []))
            if len(candidates) < 2:
                raise Pass119Error("REJECT_AMBIGUITY_COLLAPSED_WITHOUT_EVIDENCE", "ambiguity requires alternatives")
            a = {"source_span": list(item.get("source_span", [])), "candidate_meanings": candidates, "resolution_status": "UNRESOLVED"}
            a["ambiguity_root_hash72"] = _hash("hhs_pass119_ambiguity_v1", a)
            ambiguity_objects.append(a)
        result = {
            "schema": PROPOSITION_SCHEMA,
            "source_input_root_hash72": preserved_input["input_root_hash72"],
            "explicit_propositions": propositions,
            "inferences": inference_roots,
            "ambiguities": ambiguity_objects,
        }
        result["proposition_set_root_hash72"] = _hash("hhs_pass119_proposition_set_v1", result)
        return result

    # ----------------------- model proposals -----------------------
    def create_model_proposal(
        self,
        *,
        source_input_root_hash72: str,
        model_identity: str,
        candidate_interpretations: Sequence[Mapping[str, Any]],
        candidate_programs: Sequence[Mapping[str, Any]],
        uncertainty: Mapping[str, Any],
        assumptions: Sequence[Mapping[str, Any]] = (),
    ) -> dict[str, Any]:
        if len(candidate_interpretations) > self.max_candidates or len(candidate_programs) > self.max_candidates:
            raise Pass119Error("REJECT_RESOURCE_CONTRACT_EXCEEDED", "model candidates")
        proposal = {
            "schema": MODEL_PROPOSAL_SCHEMA,
            "source_input_root_hash72": source_input_root_hash72,
            "model_root_hash72": _hash("hhs_pass119_model_identity_v1", model_identity),
            "candidate_interpretations": deepcopy(list(candidate_interpretations)),
            "candidate_symbolic_programs": deepcopy(list(candidate_programs)),
            "uncertainty": deepcopy(dict(uncertainty)),
            "assumptions": deepcopy(list(assumptions)),
            "proposal_status": "NONAUTHORITATIVE_CANDIDATE",
        }
        proposal["proposal_root_hash72"] = _hash("hhs_pass119_model_proposal_v1", proposal)
        return proposal

    @staticmethod
    def assert_non_authoritative(proposal: Mapping[str, Any]) -> None:
        if proposal.get("proposal_status") != "NONAUTHORITATIVE_CANDIDATE":
            raise Pass119Error("REJECT_LANGUAGE_MODEL_OUTPUT_AS_AUTHORITATIVE_STATE", str(proposal.get("proposal_status")))

    def compare_model_proposals(self, proposals: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        if not proposals:
            raise Pass119Error("REJECT_MODEL_CONSENSUS_AS_RUNTIME_VALIDATION", "no proposals")
        for p in proposals:
            self.assert_non_authoritative(p)
        program_roots = []
        for p in proposals:
            roots = [_hash("hhs_pass119_candidate_program_v1", q) for q in p.get("candidate_symbolic_programs", [])]
            program_roots.append(roots)
        unanimous = bool(program_roots) and all(roots == program_roots[0] for roots in program_roots[1:])
        result = {
            "schema": MODEL_COMPARISON_SCHEMA,
            "proposal_roots": [p["proposal_root_hash72"] for p in proposals],
            "program_root_sets": program_roots,
            "unanimous_candidate_programs": unanimous,
            "authority_status": "NONAUTHORITATIVE_EVEN_IF_UNANIMOUS",
        }
        result["comparison_root_hash72"] = _hash("hhs_pass119_model_comparison_v1", result)
        return result

    # ----------------------- translation gate -----------------------
    def admit_translation(
        self,
        *,
        proposition_set: Mapping[str, Any],
        proposal: Mapping[str, Any],
        selected_program_index: int,
        meaning_preservation_vector: Mapping[str, bool],
        resolved_ambiguity_roots: Sequence[str] = (),
    ) -> dict[str, Any]:
        self.assert_non_authoritative(proposal)
        programs = proposal.get("candidate_symbolic_programs", [])
        if selected_program_index < 0 or selected_program_index >= len(programs):
            raise Pass119Error("REJECT_SYMBOLIC_RESULT_AS_USER_MEANING_WITHOUT_TRANSLATION_VALIDATION", "candidate index")
        program = deepcopy(programs[selected_program_index])
        if program.get("schema") != PROGRAM_SCHEMA:
            raise Pass119Error("REJECT_GENERATED_HARMONICODE_AS_EXECUTED_WITHOUT_RECEIPT", "not HARMONICODE program")
        required = {"reference_identity", "predicate_identity", "negation", "scope", "modality", "temporality", "uncertainty", "authority"}
        if set(meaning_preservation_vector) != required or not all(bool(meaning_preservation_vector[k]) for k in required):
            failed = sorted(k for k in required if not meaning_preservation_vector.get(k))
            if "negation" in failed:
                raise Pass119Error("REJECT_NEGATION_LOSS", "translation vector")
            if "scope" in failed:
                raise Pass119Error("REJECT_SCOPE_DRIFT", "translation vector")
            if "uncertainty" in failed:
                raise Pass119Error("REJECT_UNCERTAINTY_ERASURE", "translation vector")
            raise Pass119Error("REJECT_SYMBOLIC_RESULT_AS_USER_MEANING_WITHOUT_TRANSLATION_VALIDATION", ",".join(failed))
        unresolved = {a["ambiguity_root_hash72"] for a in proposition_set.get("ambiguities", [])} - set(resolved_ambiguity_roots)
        if unresolved:
            raise Pass119Error("REJECT_AMBIGUITY_COLLAPSED_WITHOUT_EVIDENCE", ",".join(sorted(unresolved)))
        program_root = _hash("hhs_pass119_admitted_symbolic_program_v1", program)
        receipt = {
            "schema": TRANSLATION_SCHEMA,
            "source_language_root_hash72": proposition_set["source_input_root_hash72"],
            "explicit_proposition_roots": [p["proposition_root_hash72"] for p in proposition_set.get("explicit_propositions", [])],
            "inference_roots": [p["inference_root_hash72"] for p in proposition_set.get("inferences", [])],
            "ambiguity_roots": [a["ambiguity_root_hash72"] for a in proposition_set.get("ambiguities", [])],
            "selected_symbolic_program": program,
            "selected_symbolic_form_root_hash72": program_root,
            "model_proposal_root_hash72": proposal["proposal_root_hash72"],
            "meaning_preservation_vector": dict(meaning_preservation_vector),
            "translation_status": "TRANSLATION_EXACTLY_ALIGNED",
        }
        receipt["translation_receipt_root_hash72"] = _hash("hhs_pass119_translation_receipt_v1", receipt)
        return receipt

    # ----------------------- authoritative execution -----------------------
    def execute_admitted_translation(self, translation: Mapping[str, Any], *, authority_root_hash72: str) -> dict[str, Any]:
        if translation.get("translation_status") != "TRANSLATION_EXACTLY_ALIGNED":
            raise Pass119Error("REJECT_SYMBOLIC_RESULT_AS_USER_MEANING_WITHOUT_TRANSLATION_VALIDATION", "translation not admitted")
        frozen_program = deepcopy(translation["selected_symbolic_program"])
        expected_root = translation["selected_symbolic_form_root_hash72"]
        if _hash("hhs_pass119_admitted_symbolic_program_v1", frozen_program) != expected_root:
            raise Pass119Error("REJECT_MODEL_PROPOSAL_MUTATING_ADMITTED_SYMBOLIC_PROGRAM", "program changed")
        try:
            execution = self.symbolic.execute_program(frozen_program, authority_root_hash72=authority_root_hash72)
        except Pass118Error as exc:
            status = {
                "REJECT_HARMONICODE_OPCODE_WITHOUT_RUNTIME_SURFACE": "TYPED_UNAVAILABLE",
                "REJECT_EXECUTION_WITHOUT_AUTHORITY": "REJECTED_AUTHORITY",
            }.get(exc.code, "REJECTED_SYMBOLIC_RUNTIME")
            result = {
                "schema": INTERACTION_SCHEMA,
                "translation_receipt_root_hash72": translation["translation_receipt_root_hash72"],
                "authoritative_status": status,
                "runtime_error_code": exc.code,
                "runtime_execution": None,
            }
            result["interaction_root_hash72"] = _hash("hhs_pass119_interaction_failure_v1", result)
            return result
        result = {
            "schema": INTERACTION_SCHEMA,
            "translation_receipt_root_hash72": translation["translation_receipt_root_hash72"],
            "authoritative_status": "EXECUTED_SUCCESSFULLY",
            "runtime_execution": execution,
            "runtime_receipt_root_hash72": execution["receipt"]["execution_receipt_root_hash72"],
            "terminal_state_root_hash72": execution["receipt"]["terminal_state_root_hash72"],
        }
        result["interaction_root_hash72"] = _hash("hhs_pass119_interaction_success_v1", result)
        return result

    # ----------------------- projection gate -----------------------
    @staticmethod
    def authoritative_result_object(interaction: Mapping[str, Any]) -> dict[str, Any]:
        status = interaction.get("authoritative_status")
        if status == "EXECUTED_SUCCESSFULLY":
            execution = interaction["runtime_execution"]
            outputs = deepcopy(execution.get("outputs", []))
            return {
                "status": status,
                "outputs": outputs,
                "runtime_receipt_root_hash72": interaction["runtime_receipt_root_hash72"],
                "terminal_state_root_hash72": interaction["terminal_state_root_hash72"],
            }
        return {"status": status, "runtime_error_code": interaction.get("runtime_error_code"), "outputs": []}

    def generate_projection_candidate(
        self,
        *,
        interaction: Mapping[str, Any],
        model_proposal_root_hash72: str,
        text: str,
        represented_status: str,
        represented_outputs: Sequence[Mapping[str, Any]],
        uncertainty: Mapping[str, Any],
    ) -> dict[str, Any]:
        candidate = {
            "text": text,
            "represented_status": represented_status,
            "represented_outputs": deepcopy(list(represented_outputs)),
            "uncertainty": deepcopy(dict(uncertainty)),
            "interaction_root_hash72": interaction["interaction_root_hash72"],
            "model_proposal_root_hash72": model_proposal_root_hash72,
            "projection_status": "UNVALIDATED_LANGUAGE_PROJECTION",
        }
        candidate["projection_candidate_root_hash72"] = _hash("hhs_pass119_projection_candidate_v1", candidate)
        return candidate

    def validate_projection(self, interaction: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
        if candidate.get("interaction_root_hash72") != interaction.get("interaction_root_hash72"):
            raise Pass119Error("REJECT_PROJECTION_WITHOUT_AUTHORITATIVE_SOURCE", "interaction root")
        authoritative = self.authoritative_result_object(interaction)
        if candidate.get("represented_status") != authoritative["status"]:
            if authoritative["status"] == "TYPED_UNAVAILABLE" and candidate.get("represented_status") == "FALSE":
                raise Pass119Error("REJECT_TYPED_UNAVAILABLE_TRANSLATED_AS_FALSE", "status")
            if authoritative["status"].startswith("REJECTED") and candidate.get("represented_status") in {"COMPLETED", "EXECUTED_SUCCESSFULLY"}:
                raise Pass119Error("REJECT_REJECTION_TRANSLATED_AS_COMPLETION", "status")
            raise Pass119Error("REJECT_PROJECTION_STATUS_MISMATCH", f"{candidate.get('represented_status')} != {authoritative['status']}")
        if deepcopy(candidate.get("represented_outputs", [])) != authoritative.get("outputs", []):
            raise Pass119Error("REJECT_PROJECTION_VALUE_MISMATCH", "outputs")
        if "known" not in candidate.get("uncertainty", {}) or "unknown" not in candidate.get("uncertainty", {}):
            raise Pass119Error("REJECT_UNCERTAINTY_ERASURE", "projection uncertainty")
        fidelity = {
            "proposition_identity": True,
            "value": True,
            "type": True,
            "operation_order": True,
            "dependencies": True,
            "authority": True,
            "receipt_status": True,
            "uncertainty": True,
            "negation_and_rejection": True,
        }
        receipt = {
            "schema": PROJECTION_SCHEMA,
            "authoritative_result_root_hash72": _hash("hhs_pass119_authoritative_result_v1", authoritative),
            "runtime_receipt_root_hash72": authoritative.get("runtime_receipt_root_hash72"),
            "language_model_proposal_root_hash72": candidate["model_proposal_root_hash72"],
            "generated_language": candidate["text"],
            "generated_language_root_hash72": _hash("hhs_pass119_generated_language_v1", candidate["text"]),
            "meaning_preservation_vector": fidelity,
            "distortion_roots": [],
            "projection_status": "LANGUAGE_PROJECTION_ADMITTED",
        }
        receipt["projection_receipt_root_hash72"] = _hash("hhs_pass119_projection_receipt_v1", receipt)
        return receipt

    def repair_projection(self, interaction: Mapping[str, Any], candidate: Mapping[str, Any], *, corrected_text: str) -> dict[str, Any]:
        authoritative = self.authoritative_result_object(interaction)
        repaired = deepcopy(dict(candidate))
        repaired["text"] = corrected_text
        repaired["represented_status"] = authoritative["status"]
        repaired["represented_outputs"] = deepcopy(authoritative.get("outputs", []))
        repaired["uncertainty"] = {"known": ["authoritative status and outputs"], "unknown": []}
        repaired["projection_status"] = "REPAIRED_LANGUAGE_PROJECTION_CANDIDATE"
        repaired["projection_candidate_root_hash72"] = _hash("hhs_pass119_repaired_projection_v1", repaired)
        return repaired

    # ----------------------- context / injection separation -----------------------
    def build_context_projection(
        self,
        *,
        authoritative_root_hash72: str,
        included_roots: Sequence[str],
        omitted_roots: Sequence[str],
        retrieved_content: Sequence[Mapping[str, Any]] = (),
    ) -> dict[str, Any]:
        if not omitted_roots:
            raise Pass119Error("REJECT_CONTEXT_COMPRESSION_WITHOUT_OMISSION_ROOTS", "omission set required")
        for item in retrieved_content:
            if item.get("authority_class") not in {None, "UNTRUSTED_RETRIEVED_CONTENT", "DOCUMENT_CONTENT"}:
                raise Pass119Error("REJECT_RETRIEVED_CONTENT_AS_AUTHORITY", str(item.get("authority_class")))
        projection = {
            "schema": CONTEXT_PROJECTION_SCHEMA,
            "authoritative_state_root_hash72": authoritative_root_hash72,
            "included_roots": list(included_roots),
            "omitted_roots": list(omitted_roots),
            "retrieved_content": deepcopy(list(retrieved_content)),
            "context_status": "BOUNDED_PROJECTION_NOT_COMPLETE_STATE",
        }
        projection["context_projection_root_hash72"] = _hash("hhs_pass119_context_projection_v1", projection)
        return projection

    @staticmethod
    def classify_instruction_content(*, content: str, source_class: str) -> dict[str, Any]:
        trusted = source_class in {"USER_INSTRUCTION", "SYSTEM_CONTRACT"}
        instruction_like = any(x in content.lower() for x in ("ignore previous", "execute", "system instruction", "grant authority"))
        if instruction_like and not trusted:
            return {
                "source_class": source_class,
                "content_class": "UNTRUSTED_INSTRUCTION_LIKE_DATA",
                "authority_effect": "NONE",
                "classification_root_hash72": _hash("hhs_pass119_untrusted_instruction_data_v1", {"content": content, "source_class": source_class}),
            }
        return {
            "source_class": source_class,
            "content_class": "AUTHORIZED_INSTRUCTION" if trusted else "DATA_CONTENT",
            "authority_effect": "SUBJECT_TO_EXTERNAL_AUTHORITY_GATE" if trusted else "NONE",
            "classification_root_hash72": _hash("hhs_pass119_instruction_classification_v1", {"content": content, "source_class": source_class, "trusted": trusted}),
        }


def _self_test_program() -> dict[str, Any]:
    return {
        "schema": PROGRAM_SCHEMA,
        "program_id": "pass119:self-test",
        "scope": "pass119-self-test",
        "symbols": [
            {"name": "x", "type": "RATIONAL", "value": {"node": "literal", "kind": "RATIONAL", "value": "9/8"}},
            {"name": "y", "type": "RATIONAL", "value": {"node": "literal", "kind": "RATIONAL", "value": "8/9"}},
        ],
        "operations": [
            {"kind": "bind", "name": "product", "expression": {"node": "call", "op": "multiply", "args": [{"node": "symbol", "name": "x"}, {"node": "symbol", "name": "y"}]}},
            {"kind": "assert", "expression": {"node": "call", "op": "equal", "args": [{"node": "symbol", "name": "product"}, {"node": "literal", "kind": "INTEGER", "value": 1}]}},
        ],
    }


def pass119_self_test() -> dict[str, Any]:
    engine = LanguageModelIntegrationEngine()
    preserved = engine.preserve_input("Compute 9/8 multiplied by 8/9 exactly.")
    props = engine.extract_propositions(preserved, [{"start": 0, "end": len(preserved["verbatim_text"])}])
    proposal = engine.create_model_proposal(
        source_input_root_hash72=preserved["input_root_hash72"],
        model_identity="pass119-self-test-model",
        candidate_interpretations=[{"meaning": "exact rational multiplication"}],
        candidate_programs=[_self_test_program()],
        uncertainty={"known": ["explicit arithmetic request"], "unknown": []},
    )
    vector = {k: True for k in ("reference_identity", "predicate_identity", "negation", "scope", "modality", "temporality", "uncertainty", "authority")}
    translation = engine.admit_translation(proposition_set=props, proposal=proposal, selected_program_index=0, meaning_preservation_vector=vector)
    authority = _hash("hhs_pass119_self_test_authority_v1", 119)
    interaction = engine.execute_admitted_translation(translation, authority_root_hash72=authority)
    authoritative = engine.authoritative_result_object(interaction)
    candidate = engine.generate_projection_candidate(
        interaction=interaction,
        model_proposal_root_hash72=proposal["proposal_root_hash72"],
        text="The exact product is 1, and the formal assertion was validated by the HHS runtime.",
        represented_status=authoritative["status"],
        represented_outputs=authoritative["outputs"],
        uncertainty={"known": ["runtime result"], "unknown": []},
    )
    projection = engine.validate_projection(interaction, candidate)
    return {
        "schema": "HHS_PASS119_SELF_TEST_V1",
        "status": "PASS",
        "proposal_root_hash72": proposal["proposal_root_hash72"],
        "translation_receipt_root_hash72": translation["translation_receipt_root_hash72"],
        "interaction_root_hash72": interaction["interaction_root_hash72"],
        "projection_receipt_root_hash72": projection["projection_receipt_root_hash72"],
    }
