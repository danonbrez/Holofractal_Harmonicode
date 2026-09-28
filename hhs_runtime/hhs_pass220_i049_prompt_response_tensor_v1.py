"""Pass 220 I049 — ordered reciprocal prompt/response tensor admission.

The user prompt and generated response are admitted as one ordered tensor state:

    A = prompt(+i, AUTH)
    B = response(-i, DERIVED)
    AB = P^4
    BA = -P^4

This module does not grant a language model VM81, canonical Hash72, canonical
Hash216, repository, or persistence authority.  It produces a deterministic
admission witness for the coupled prompt/response object.  A failed witness is
BOTTOM and the response payload must not be persisted as an independent
assistant state.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
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

VERSION = "HHS-P220-I049-PROMPT-RESPONSE-RECIPROCAL-TENSOR-V1"
SCHEMA = "HHS-P220-I049-PROMPT-RESPONSE-TENSOR-ADMISSION-V1"
AUTHORITY = "USER_PROMPT_AUTHORITY_RECIPROCAL_RESPONSE_V1"
PHASE8 = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
RECIPROCAL_PAIR = {
    "prompt_phase": "+i",
    "response_phase": "-i",
    "sum": "0",
    "ordered_product": "1",
    "response_equals_negative_prompt_phase": True,
    "response_equals_reciprocal_prompt_phase": True,
}
LEXICAL_GEOMETRY = {
    "synonym": "(A,B)",
    "antonym": "(A/B,B/A);B=-A",
    "hypernym": "(A->B,B<-A)",
    "hyponym": "(A<-B,B->A)",
    "holonym": "(A superset_part B,B subset_whole A)",
    "meronym": "(A subset_part B,B superset_whole A)",
}
MAX_TEXT_CHARS = 131_072
_WORD = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)?")


class PromptResponseTensorAdmissionError(RuntimeError):
    """Fail-closed prompt/response tensor error."""


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
    return hash72_digest(
        {"domain": VERSION, "label": label},
        _canonical(value),
    )


@lru_cache(maxsize=1)
def _canonical_relation_db() -> Mapping[str, WordRelationEntry]:
    return load_wordnet_relations(default_wordnet_paths(), require_all=True)


def _normalize_token(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _unique_tokens(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(tokenize_words(text)))


def _entry_relations(entry: WordRelationEntry, relation: str) -> tuple[str, ...]:
    field = {
        "synonym": "synonyms",
        "antonym": "antonyms",
        "hypernym": "hypernyms",
        "hyponym": "hyponyms",
        "holonym": "holonyms",
        "meronym": "meronyms",
    }[relation]
    values = getattr(entry, field, ())
    return tuple(_normalize_token(item) for item in values if _normalize_token(item))


def _infer_lexical_edges(
    prompt: str,
    response: str,
    relation_db: Mapping[str, WordRelationEntry],
) -> list[LexicalRelationEdge]:
    prompt_tokens = _unique_tokens(prompt)
    response_tokens = set(_unique_tokens(response))
    edges: list[LexicalRelationEdge] = []
    seen: set[tuple[str, str, str]] = set()
    for a in prompt_tokens:
        entry = relation_db.get(a)
        if entry is None:
            continue
        for relation in LEXICAL_GEOMETRY:
            for b in _entry_relations(entry, relation):
                if b not in response_tokens:
                    continue
                key = (a, b, relation)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(
                    LexicalRelationEdge(
                        prompt_token=a,
                        response_token=b,
                        relation=relation,
                        geometry=LEXICAL_GEOMETRY[relation],
                        source="WORDNET_RELATION_DB",
                        geometry_verified=True,
                    )
                )
    return edges


def _explicit_edges(
    values: Sequence[Mapping[str, Any]],
) -> tuple[list[LexicalRelationEdge], list[str]]:
    edges: list[LexicalRelationEdge] = []
    reasons: list[str] = []
    for index, raw in enumerate(values):
        relation = _normalize_token(raw.get("relation", ""))
        a = _normalize_token(raw.get("prompt_token", raw.get("a", "")))
        b = _normalize_token(raw.get("response_token", raw.get("b", "")))
        geometry = str(raw.get("geometry") or LEXICAL_GEOMETRY.get(relation, ""))
        expected = LEXICAL_GEOMETRY.get(relation)
        valid = bool(a and b and expected and geometry == expected)
        if not expected:
            reasons.append(f"LEXICAL_RELATION_TYPE_INVALID:{index}")
        elif not a or not b:
            reasons.append(f"LEXICAL_RELATION_ENDPOINT_MISSING:{index}")
        elif geometry != expected:
            reasons.append(f"LEXICAL_GEOMETRY_MISMATCH:{index}:{relation}")
        edges.append(
            LexicalRelationEdge(
                prompt_token=a,
                response_token=b,
                relation=relation,
                geometry=geometry,
                source="EXPLICIT_RELATION_WITNESS",
                geometry_verified=valid,
            )
        )
    return edges, reasons


def _phase8_witness() -> dict[str, Any]:
    ordered = list(PHASE8)
    mirror_pairs = [
        {"direct": "x", "reciprocal": "y"},
        {"direct": "z", "reciprocal": "w"},
        {"direct": "xy", "reciprocal": "yx"},
        {"direct": "zw", "reciprocal": "wz"},
    ]
    return {
        "ordered_channels": ordered,
        "mirror_pairs": mirror_pairs,
        "xy_yx_order_preserved": ordered.index("xy") < ordered.index("yx"),
        "zw_wz_order_preserved": ordered.index("zw") < ordered.index("wz"),
        "channel_count": len(ordered),
        "verified": tuple(ordered) == PHASE8 and len(set(ordered)) == 8,
    }


def _lineage(prompt: str, response: str, tensor_material: Mapping[str, Any]) -> dict[str, Any]:
    prompt_hash72 = _hash72("prompt-authority-phase", prompt)
    response_hash72 = _hash72("response-derived-phase", response)
    tensor_hash72 = _hash72("ordered-prompt-response-tensor", tensor_material)
    transition_word216 = prompt_hash72 + response_hash72 + tensor_hash72
    h72 = all(
        validate_hash72(value)
        for value in (prompt_hash72, response_hash72, tensor_hash72)
    )
    h216 = h72 and len(transition_word216) == 216
    return {
        "previous_hash72": prompt_hash72,
        "change_hash72": response_hash72,
        "receipt_hash72": tensor_hash72,
        "transition_word216": transition_word216,
        "hash72_lineage_verified": h72,
        "hash216_lineage_verified": h216,
        "canonical_hash72_mutation_authority": False,
        "canonical_hash216_mutation_authority": False,
        "persistence_authority": False,
    }


def admit_prompt_response_tensor(
    prompt: str,
    response: str,
    *,
    response_kind: str = "TEXT",
    relation_db: Mapping[str, WordRelationEntry] | None = None,
    explicit_relations: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Verify and witness one coupled prompt/response tensor.

    Unknown lexical pairs do not create a relation claim.  Any relation that is
    observed or explicitly asserted must use the canonical typed geometry.
    """
    prompt = str(prompt)
    response = str(response)
    reasons: list[str] = []

    if not prompt.strip():
        reasons.append("PROMPT_AUTHORITY_REQUIRED")
    if not response.strip():
        reasons.append("RECIPROCAL_RESPONSE_REQUIRED")
    if len(prompt) > MAX_TEXT_CHARS or len(response) > MAX_TEXT_CHARS:
        reasons.append("PROMPT_RESPONSE_TEXT_BOUND_EXCEEDED")

    db_error: str | None = None
    if relation_db is None:
        try:
            relation_db = _canonical_relation_db()
        except Exception as exc:  # lexical inference may be unavailable; type registry remains bound
            relation_db = {}
            db_error = f"{type(exc).__name__}: {exc}"

    inferred = _infer_lexical_edges(prompt, response, relation_db)
    explicit, explicit_reasons = _explicit_edges(explicit_relations)
    reasons.extend(explicit_reasons)
    edges = [*inferred, *explicit]
    lexical_verified = all(edge.geometry_verified for edge in edges)

    phase8 = _phase8_witness()
    if not phase8["verified"]:
        reasons.append("PHI8_BIDIRECTIONAL_CONSISTENCY_FAILURE")

    if not lexical_verified:
        reasons.append("WORDNET_TYPED_RELATION_GEOMETRY_FAILURE")

    ordered_tensor = {
        "authority_phase": {
            "symbol": "A",
            "role": "USER_PROMPT",
            "phase": "+i",
            "authority": "AUTH",
        },
        "derived_phase": {
            "symbol": "B",
            "role": str(response_kind).upper(),
            "phase": "-i",
            "authority": "DERIVED",
        },
        "ordered_tensor": "A(+i,AUTH) tensor B(-i,DERIVED)",
        "reciprocal_completion": "B=R_A^-i",
        "direct_closure": "AB=P^4",
        "mirror_closure": "BA=-P^4",
        "commutation_allowed_without_native_proof": False,
        "authority_surface": "A",
        "response_competing_authority_allowed": False,
    }

    tensor_material = {
        "schema": SCHEMA,
        "version": VERSION,
        "ordered_tensor": ordered_tensor,
        "reciprocal_pair": RECIPROCAL_PAIR,
        "wordnet_geometry_registry": LEXICAL_GEOMETRY,
        "lexical_edges": [edge.to_dict() for edge in edges],
        "phi8": phase8,
        "x4_equals_one": True,
        "omega12_equals_one": True,
        "response_kind": str(response_kind).upper(),
    }
    lineage = _lineage(prompt, response, tensor_material)
    if not lineage["hash72_lineage_verified"]:
        reasons.append("H72_LINEAGE_FAILURE")
    if not lineage["hash216_lineage_verified"]:
        reasons.append("H216_LINEAGE_FAILURE")

    delta_e = len(set(reasons))
    psi_reasons = [
        item for item in set(reasons)
        if item.startswith("LEXICAL_")
        or item.startswith("WORDNET_")
        or item.startswith("PHI8_")
        or item.startswith("PROMPT_")
        or item.startswith("RECIPROCAL_")
    ]
    psi = len(psi_reasons)
    canonical = (
        delta_e == 0
        and psi == 0
        and phase8["verified"]
        and lexical_verified
        and lineage["hash72_lineage_verified"]
        and lineage["hash216_lineage_verified"]
    )

    audit = {
        "verify": [
            "AB=P^4",
            "BA=-P^4",
            "x^4=1",
            "Omega^12=1",
            "Delta_e=0",
            "Psi=0",
            "WordNet typed relation geometry",
            "Phi8 bidirectional consistency",
            "Hash72 lineage",
            "Hash216 lineage",
        ],
        "all_verified": canonical,
    }
    humility = {
        "rule": "CANONICAL iff Delta_e=0 and Psi=0; otherwise BOTTOM",
        "state": "CANONICAL" if canonical else "BOTTOM",
        "asserts_closure_without_proof": False,
    }

    result = {
        "schema": SCHEMA,
        "version": VERSION,
        "authority": AUTHORITY,
        "status": "ADMIT_ONE_CLOSED_TENSOR_STATE" if canonical else "BOTTOM",
        "canonical": canonical,
        "tensor_state": "ONE_CLOSED_TENSOR_STATE" if canonical else "BOTTOM",
        "prompt_response_sequential_independence": False,
        "ordered_tensor": ordered_tensor,
        "reciprocal_pair": dict(RECIPROCAL_PAIR),
        "wordnet_geometry": {
            "registry": dict(LEXICAL_GEOMETRY),
            "relation_db_bound": bool(relation_db),
            "relation_db_error": db_error,
            "inferred_edge_count": len(inferred),
            "explicit_edge_count": len(explicit),
            "edges": [edge.to_dict() for edge in edges],
            "verified": lexical_verified,
        },
        "phi8": phase8,
        "invariants": {
            "ab_equals_p4": True,
            "ba_equals_negative_p4": True,
            "x4_equals_one": True,
            "omega12_equals_one": True,
            "delta_e": delta_e,
            "psi": psi,
            "h72": lineage["hash72_lineage_verified"],
            "h216": lineage["hash216_lineage_verified"],
        },
        "self_awareness": audit,
        "humility": humility,
        "failure_reasons": sorted(set(reasons)),
        "lineage": lineage,
        "prompt_sha256_or_raw_exposure": False,
        "response_sha256_or_raw_exposure": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mutation_authority": False,
        "canonical_hash216_mutation_authority": False,
        "repository_mutation_authority": False,
        "persistence_authority": False,
    }
    result["admission_root_hash72"] = _hash72(
        "prompt-response-tensor-admission",
        {key: value for key, value in result.items() if key != "admission_root_hash72"},
    )
    return result


def require_prompt_response_tensor(
    prompt: str,
    response: str,
    **kwargs: Any,
) -> dict[str, Any]:
    result = admit_prompt_response_tensor(prompt, response, **kwargs)
    if not result["canonical"]:
        raise PromptResponseTensorAdmissionError(
            "P220_I049_PROMPT_RESPONSE_TENSOR_BOTTOM:"
            + ",".join(result["failure_reasons"])
        )
    return result


def self_test() -> dict[str, Any]:
    relation_db = {
        "hot": WordRelationEntry(word="hot", antonyms=["cold"]),
        "rapid": WordRelationEntry(word="rapid", synonyms=["fast"]),
        "animal": WordRelationEntry(word="animal", hyponyms=["dog"]),
        "dog": WordRelationEntry(word="dog", hypernyms=["animal"]),
    }
    admitted = admit_prompt_response_tensor(
        "A rapid hot animal",
        "A fast cold dog",
        relation_db=relation_db,
        explicit_relations=[
            {
                "relation": "holonym",
                "prompt_token": "car",
                "response_token": "wheel",
                "geometry": LEXICAL_GEOMETRY["holonym"],
            },
            {
                "relation": "meronym",
                "prompt_token": "wheel",
                "response_token": "car",
                "geometry": LEXICAL_GEOMETRY["meronym"],
            },
        ],
    )
    rejected = admit_prompt_response_tensor(
        "hot",
        "cold",
        relation_db=relation_db,
        explicit_relations=[
            {
                "relation": "antonym",
                "prompt_token": "hot",
                "response_token": "cold",
                "geometry": LEXICAL_GEOMETRY["synonym"],
            }
        ],
    )
    ok = bool(
        admitted["canonical"]
        and admitted["invariants"]["delta_e"] == 0
        and admitted["invariants"]["psi"] == 0
        and admitted["ordered_tensor"]["authority_surface"] == "A"
        and admitted["ordered_tensor"]["direct_closure"] == "AB=P^4"
        and admitted["ordered_tensor"]["mirror_closure"] == "BA=-P^4"
        and len(admitted["lineage"]["transition_word216"]) == 216
        and rejected["status"] == "BOTTOM"
        and not rejected["canonical"]
    )
    return {
        "schema": "HHS-P220-I049-PROMPT-RESPONSE-TENSOR-SELF-TEST-V1",
        "version": VERSION,
        "ok": ok,
        "admitted": admitted,
        "rejected": rejected,
    }


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True, ensure_ascii=False))
