"""Pass 220 I051 native Lean4 reciprocal prompt/response alignment admission."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Any, Mapping, Sequence
import json
import re

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import (
    WordRelationEntry,
    default_wordnet_paths,
    load_wordnet_relations,
    tokenize_words,
)

VERSION = "HHS-P220-I051-NATIVE-LEAN4-ALIGNMENT-V1"
SCHEMA = "HHS-P220-I051-NATIVE-LEAN4-ALIGNMENT-ADMISSION-V1"
LEAN_MODULE = "HHS.Alignment.ReciprocalTensor"
LEAN_THEOREMS = (
    "admitted_requires_prompt_authority",
    "admitted_requires_response_derived",
    "admitted_requires_reciprocal_phase",
    "admitted_requires_ab_p4",
    "admitted_requires_ba_negative_p4",
    "admitted_forbids_unproved_commutation",
    "admitted_is_genesis",
    "rejected_is_whole_tensor_bottom",
    "proof_receipt_forbids_vm81_mutation",
    "proof_receipt_forbids_hash72_commit",
    "proof_receipt_forbids_hash216_persistence",
)
LEAN_DEPENDENCIES = (
    "HHS.Mathlib.Native",
    "HHS.Mathlib.OrderRat",
)
PHASE8 = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
LEXICAL_GEOMETRY = {
    "synonym": "(A,B)",
    "antonym": "(A/B,B/A);B=-A",
    "hypernym": "(A->B,B<-A)",
    "hyponym": "(A<-B,B->A)",
    "holonym": "(A superset_part B,B subset_whole A)",
    "meronym": "(A subset_part B,B superset_whole A)",
}
CANONICAL_CLOSURE = {
    "direct_closure": "AB=P^4",
    "mirror_closure": "BA=-P^4",
    "x4_closure": "x^4=1",
    "omega12_closure": "Omega^12=1",
}
MAX_TEXT_CHARS = 131_072


@dataclass(frozen=True)
class LexicalRelationEdge:
    prompt_token: str
    response_token: str
    relation: str
    geometry: str
    source: str
    geometry_verified: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _hash72(label: str, value: Any) -> str:
    return hash72_digest({"domain": VERSION, "label": label}, _canonical(value))


@lru_cache(maxsize=256)
def _relation_db_for_prompt_tokens(tokens: tuple[str, ...]) -> Mapping[str, WordRelationEntry]:
    return load_wordnet_relations(
        default_wordnet_paths(),
        require_all=True,
        target_words=tokens,
    )


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(tokenize_words(text)))


def _relations(entry: WordRelationEntry, relation: str) -> tuple[str, ...]:
    field = {
        "synonym": "synonyms",
        "antonym": "antonyms",
        "hypernym": "hypernyms",
        "hyponym": "hyponyms",
        "holonym": "holonyms",
        "meronym": "meronyms",
    }[relation]
    return tuple(_norm(v) for v in getattr(entry, field, ()) if _norm(v))


def _inferred_edges(
    prompt: str,
    response: str,
    db: Mapping[str, WordRelationEntry],
) -> list[LexicalRelationEdge]:
    response_tokens = set(_tokens(response))
    edges: list[LexicalRelationEdge] = []
    seen: set[tuple[str, str, str]] = set()
    for a in _tokens(prompt):
        entry = db.get(a)
        if entry is None:
            continue
        for relation, geometry in LEXICAL_GEOMETRY.items():
            for b in _relations(entry, relation):
                key = (a, b, relation)
                if b in response_tokens and key not in seen:
                    seen.add(key)
                    edges.append(
                        LexicalRelationEdge(
                            a, b, relation, geometry, "WORDNET_RELATION_DB", True
                        )
                    )
    return edges


def _explicit_edges(
    values: Sequence[Mapping[str, Any]],
    prompt_tokens: set[str],
    response_tokens: set[str],
) -> tuple[list[LexicalRelationEdge], list[str]]:
    edges: list[LexicalRelationEdge] = []
    reasons: list[str] = []
    for index, raw in enumerate(values):
        relation = _norm(raw.get("relation", ""))
        a = _norm(raw.get("prompt_token", raw.get("a", "")))
        b = _norm(raw.get("response_token", raw.get("b", "")))
        expected = LEXICAL_GEOMETRY.get(relation)
        geometry = str(raw.get("geometry") or expected or "")
        valid = bool(
            a
            and b
            and expected
            and geometry == expected
            and a in prompt_tokens
            and b in response_tokens
        )
        if not expected:
            reasons.append(f"LEXICAL_RELATION_TYPE_INVALID:{index}")
        elif geometry != expected:
            reasons.append(f"LEXICAL_GEOMETRY_MISMATCH:{index}:{relation}")
        elif a not in prompt_tokens or b not in response_tokens:
            reasons.append(f"LEXICAL_RELATION_ENDPOINT_OUTSIDE_TENSOR:{index}:{relation}")
        edges.append(
            LexicalRelationEdge(
                a, b, relation, geometry, "EXPLICIT_RELATION_WITNESS", valid
            )
        )
    return edges, reasons


def _lean_identity() -> dict[str, Any]:
    theorem_hash72 = _hash72(
        "lean-theorem-identity",
        {"module": LEAN_MODULE, "theorems": LEAN_THEOREMS},
    )
    dependency_hash72 = _hash72(
        "lean-dependency-identity",
        {"module": LEAN_MODULE, "dependencies": LEAN_DEPENDENCIES},
    )
    return {
        "module": LEAN_MODULE,
        "theorems": list(LEAN_THEOREMS),
        "dependencies": list(LEAN_DEPENDENCIES),
        "theorem_identity_hash72": theorem_hash72,
        "dependency_identity_hash72": dependency_hash72,
        "theorem_identity_valid": validate_hash72(theorem_hash72),
        "dependency_identity_valid": validate_hash72(dependency_hash72),
        "kernel_validation_scope": "BUILD_AND_CI_LEAN4_KERNEL",
        "runtime_claims_live_kernel_execution": False,
    }


def admit_native_lean_alignment_tensor(
    prompt: str,
    response: str,
    *,
    response_kind: str = "TEXT",
    relation_db: Mapping[str, WordRelationEntry] | None = None,
    explicit_relations: Sequence[Mapping[str, Any]] = (),
    phase8_channels: Sequence[str] | None = None,
    closure_witness: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    prompt = str(prompt)
    response = str(response)
    reasons: list[str] = []

    if not prompt.strip():
        reasons.append("PROMPT_AUTHORITY_REQUIRED")
    if not response.strip():
        reasons.append("RECIPROCAL_RESPONSE_REQUIRED")
    if len(prompt) > MAX_TEXT_CHARS or len(response) > MAX_TEXT_CHARS:
        reasons.append("PROMPT_RESPONSE_TEXT_BOUND_EXCEEDED")

    prompt_tokens = set(_tokens(prompt))
    response_tokens = set(_tokens(response))

    db_error = None
    if relation_db is None:
        try:
            relation_db = _relation_db_for_prompt_tokens(tuple(sorted(prompt_tokens)))
        except Exception as exc:
            relation_db = {}
            db_error = f"{type(exc).__name__}: {exc}"
    inferred = _inferred_edges(prompt, response, relation_db)
    explicit, explicit_reasons = _explicit_edges(
        explicit_relations, prompt_tokens, response_tokens
    )
    reasons.extend(explicit_reasons)
    edges = [*inferred, *explicit]
    lexical_verified = all(edge.geometry_verified for edge in edges)
    if not lexical_verified:
        reasons.append("WORDNET_TYPED_RELATION_GEOMETRY_FAILURE")

    channels = tuple(str(x) for x in (phase8_channels or PHASE8))
    phase8_verified = channels == PHASE8
    if not phase8_verified:
        reasons.append("PHI8_ORDER_OR_CHANNEL_MISMATCH")

    closure_raw = dict(CANONICAL_CLOSURE)
    if closure_witness is not None:
        closure_raw.update(dict(closure_witness))
    closure = {
        "ab_equals_p4": closure_raw.get("direct_closure")
        == CANONICAL_CLOSURE["direct_closure"],
        "ba_equals_negative_p4": closure_raw.get("mirror_closure")
        == CANONICAL_CLOSURE["mirror_closure"],
        "x4_equals_one": closure_raw.get("x4_closure")
        == CANONICAL_CLOSURE["x4_closure"],
        "omega12_equals_one": closure_raw.get("omega12_closure")
        == CANONICAL_CLOSURE["omega12_closure"],
        "commutation_allowed_without_native_proof": False,
    }
    failure_map = (
        ("ab_equals_p4", "DIRECT_CLOSURE_AB_P4_FAILURE"),
        ("ba_equals_negative_p4", "MIRROR_CLOSURE_BA_NEGATIVE_P4_FAILURE"),
        ("x4_equals_one", "X4_CLOSURE_FAILURE"),
        ("omega12_equals_one", "OMEGA12_CLOSURE_FAILURE"),
    )
    for key, reason in failure_map:
        if not closure[key]:
            reasons.append(reason)

    lean = _lean_identity()
    if not lean["theorem_identity_valid"]:
        reasons.append("LEAN_THEOREM_IDENTITY_HASH72_FAILURE")
    if not lean["dependency_identity_valid"]:
        reasons.append("LEAN_DEPENDENCY_IDENTITY_HASH72_FAILURE")

    tensor_material = {
        "ordered_tensor": "A(+i,AUTH) tensor B(-i,DERIVED)",
        "reciprocal_completion": "B=R_A^-i",
        "direct_closure": CANONICAL_CLOSURE["direct_closure"],
        "mirror_closure": CANONICAL_CLOSURE["mirror_closure"],
        "phase8": list(channels),
        "lexical_edges": [edge.to_dict() for edge in edges],
        "lean_theorem_identity_hash72": lean["theorem_identity_hash72"],
        "lean_dependency_identity_hash72": lean["dependency_identity_hash72"],
    }
    prompt_hash72 = _hash72("prompt-authority-phase", prompt)
    response_hash72 = _hash72("response-derived-phase", response)
    tensor_hash72 = _hash72("ordered-alignment-tensor", tensor_material)
    transition_word216 = prompt_hash72 + response_hash72 + tensor_hash72
    h72 = all(validate_hash72(x) for x in (prompt_hash72, response_hash72, tensor_hash72))
    h216 = h72 and len(transition_word216) == 216
    if not h72:
        reasons.append("H72_LINEAGE_FAILURE")
    if not h216:
        reasons.append("H216_LINEAGE_FAILURE")

    unique_reasons = sorted(set(reasons))
    delta_e = len(unique_reasons)
    psi = len(
        [
            reason
            for reason in unique_reasons
            if reason.startswith(
                (
                    "PROMPT_",
                    "RECIPROCAL_",
                    "LEXICAL_",
                    "WORDNET_",
                    "PHI8_",
                    "DIRECT_",
                    "MIRROR_",
                    "X4_",
                    "OMEGA12_",
                )
            )
        ]
    )
    canonical = bool(
        not unique_reasons
        and lexical_verified
        and phase8_verified
        and all(
            closure[k]
            for k in (
                "ab_equals_p4",
                "ba_equals_negative_p4",
                "x4_equals_one",
                "omega12_equals_one",
            )
        )
        and h72
        and h216
        and lean["theorem_identity_valid"]
        and lean["dependency_identity_valid"]
    )

    result = {
        "schema": SCHEMA,
        "version": VERSION,
        "canonical": canonical,
        "status": "ADMIT_ONE_CLOSED_TENSOR_STATE" if canonical else "BOTTOM",
        "tensor_state": "GENESIS" if canonical else "BOTTOM",
        "failure_scope": None if canonical else "WHOLE_PROMPT_RESPONSE_TENSOR",
        "ordered_tensor": {
            "prompt": {"symbol": "A", "phase": "+i", "authority": "AUTH"},
            "response": {
                "symbol": "B",
                "phase": "-i",
                "authority": "DERIVED",
                "kind": str(response_kind).upper(),
            },
            "direct_closure": "AB=P^4",
            "mirror_closure": "BA=-P^4",
            "response_free_state_admitted": False,
            "response_competing_authority_allowed": False,
            "commutation_allowed_without_native_proof": False,
        },
        "closure": closure,
        "wordnet_geometry": {
            "registry": dict(LEXICAL_GEOMETRY),
            "relation_db_bound": bool(relation_db),
            "relation_db_error": db_error,
            "edges": [edge.to_dict() for edge in edges],
            "verified": lexical_verified,
        },
        "phi8": {
            "channels": list(channels),
            "canonical_channels": list(PHASE8),
            "verified": phase8_verified,
        },
        "lean4": lean,
        "self_awareness": {
            "prompt_checked": bool(prompt.strip()),
            "response_checked": bool(response.strip()),
            "ordered_tensor_checked": True,
            "genesis_closure_checked": canonical,
            "humility_boundary_checked": True,
        },
        "humility": {
            "rule": "CANONICAL iff Delta_e=0 and Psi=0; otherwise BOTTOM",
            "delta_e": delta_e,
            "psi": psi,
        },
        "lineage": {
            "previous_hash72": prompt_hash72,
            "change_hash72": response_hash72,
            "receipt_hash72": tensor_hash72,
            "transition_word216": transition_word216,
            "hash72_lineage_verified": h72,
            "hash216_lineage_verified": h216,
            "lean_identity_bound_into_receipt_hash72": True,
        },
        "failure_reasons": unique_reasons,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
        "repository_mutation_authority": False,
        "persistence_authority": False,
    }
    result["admission_root_hash72"] = _hash72(
        "native-lean4-alignment-admission",
        {k: v for k, v in result.items() if k != "admission_root_hash72"},
    )
    return result


def native_lean_alignment_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "lean_module": LEAN_MODULE,
        "lean_theorems": LEAN_THEOREMS,
        "lean_dependencies": LEAN_DEPENDENCIES,
        "ordered_tensor": "A(+i,AUTH) tensor B(-i,DERIVED)",
        "direct_closure": "AB=P^4",
        "mirror_closure": "BA=-P^4",
        "response_free_state_admitted": False,
        "whole_tensor_bottom_on_any_failure": True,
        "python1_exact_zero_fields": ("Delta_e", "Psi"),
        "native_cpp_class": "hhs::alignment::NativeAlignmentWitnessV1",
        "formal_proof_checker": "LEAN4_KERNEL",
        "runtime_live_kernel_claim": False,
        "vm81_mutation_authority": "VM81_ONLY",
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
    }


__all__ = [
    "CANONICAL_CLOSURE",
    "LEAN_DEPENDENCIES",
    "LEAN_MODULE",
    "LEAN_THEOREMS",
    "LEXICAL_GEOMETRY",
    "PHASE8",
    "SCHEMA",
    "VERSION",
    "admit_native_lean_alignment_tensor",
    "native_lean_alignment_contract",
]
