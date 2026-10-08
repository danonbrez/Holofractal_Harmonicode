"""Pass 220 I081 deep audit and source-safe constructor promotion.

I081 promotes only HOLD sources with an exact documented preprint identity and
a pinned comparator/solution proof surface. Partial formalization creates a
subconstructor but leaves the manuscript-level HOLD in place.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

SCHEMA = "HHS_PASS_220_I081_OPENAI_MATH_CONSTRUCTOR_PROMOTION_AUDIT_V1"
EXPECTED_SOURCE_REVISION = "adc7f1241b42e322a6451854ab7e4b4c146bf78a"
EXPECTED_BASE_MAIN = "e2e4fcfa539e2c80997eb796abe5dbce1227d559"
EXPECTED_FULL_PROMOTIONS = 4
EXPECTED_PARTIAL = 1
EXPECTED_DENIED = 9
ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/pass220/openai_math_constructor_promotion_audit_i081_v1.json"
I078_PATH = ROOT / "data/pass220/openai_math_corpus_hydration_20261006_v1.json"
I079_PATH = ROOT / "data/pass220/openai_math_formalized_novelty_constructors_v1.json"
I080_PATH = ROOT / "data/pass220/openai_math_hold_claim_constructors_v1.json"


class I081PromotionError(RuntimeError):
    pass


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _is_hex40(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(ch in "0123456789abcdef" for ch in value)
    )


def load_registry(path: str | Path = REGISTRY_PATH) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise I081PromotionError("I081_SCHEMA_MISMATCH")
    if data.get("source_revision") != EXPECTED_SOURCE_REVISION:
        raise I081PromotionError("I081_SOURCE_REVISION_MISMATCH")
    if data.get("base_main") != EXPECTED_BASE_MAIN:
        raise I081PromotionError("I081_BASE_MAIN_MISMATCH")

    full = data.get("full_promotions")
    partial = data.get("partial_subconstructors")
    denied = data.get("denied_full_promotions")
    if not isinstance(full, list) or len(full) != EXPECTED_FULL_PROMOTIONS:
        raise I081PromotionError("I081_FULL_PROMOTION_COUNT_MISMATCH")
    if not isinstance(partial, list) or len(partial) != EXPECTED_PARTIAL:
        raise I081PromotionError("I081_PARTIAL_COUNT_MISMATCH")
    if not isinstance(denied, list) or len(denied) != EXPECTED_DENIED:
        raise I081PromotionError("I081_DENIED_COUNT_MISMATCH")

    audited_ids = [
        row["hold_constructor_id"]
        for row in [*full, *partial, *denied]
    ]
    if len(set(audited_ids)) != 14:
        raise I081PromotionError("I081_AUDIT_SOURCE_DUPLICATION")

    for row in full:
        if row.get("decision") != "PROMOTE_FULL_THEOREM_CONSTRUCTOR":
            raise I081PromotionError("I081_FULL_DECISION_DRIFT")
        if row.get("source_slug") != row.get("doc_preprint_slug"):
            raise I081PromotionError("I081_FULL_SOURCE_DOC_IDENTITY_MISMATCH")
        if not row.get("theorem_names"):
            raise I081PromotionError("I081_FULL_THEOREM_LIST_EMPTY")
        for obj in (row.get("comparator", {}), row.get("solution", {})):
            if not _is_hex40(obj.get("sha")):
                raise I081PromotionError("I081_FULL_PROOF_IDENTITY_INVALID")
        if not _is_hex40(row.get("source_tree_sha")):
            raise I081PromotionError("I081_FULL_SOURCE_TREE_INVALID")

    for row in partial:
        if row.get("decision") != "KEEP_HOLD_ADD_FORMAL_SUBCONSTRUCTOR":
            raise I081PromotionError("I081_PARTIAL_DECISION_DRIFT")
        if row.get("source_slug") != row.get("doc_preprint_slug"):
            raise I081PromotionError("I081_PARTIAL_SOURCE_DOC_IDENTITY_MISMATCH")
        if row.get("full_source_promotion") is not False:
            raise I081PromotionError("I081_PARTIAL_PROMOTION_DRIFT")
        if not row.get("excluded_scope"):
            raise I081PromotionError("I081_PARTIAL_EXCLUDED_SCOPE_MISSING")
        if not row.get("theorem_names"):
            raise I081PromotionError("I081_PARTIAL_THEOREM_LIST_EMPTY")

    for row in denied:
        if row.get("decision") != "KEEP_HOLD":
            raise I081PromotionError("I081_DENIED_DECISION_DRIFT")
        if not row.get("reason"):
            raise I081PromotionError("I081_DENIED_REASON_MISSING")

    authority = data.get("authority", {})
    if authority.get("candidate_only") is not True:
        raise I081PromotionError("I081_NOT_CANDIDATE_ONLY")
    for key, value in authority.items():
        if key in ("candidate_only", "external_formal_proof_is_provenance_authority"):
            if value is not True:
                raise I081PromotionError(f"I081_AUTHORITY_FLAG_DRIFT:{key}")
        elif value is not False:
            raise I081PromotionError(f"I081_AUTHORITY_DRIFT:{key}")
    return data


def effective_frontier(
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    i078 = json.loads(I078_PATH.read_text(encoding="utf-8"))
    i079 = json.loads(I079_PATH.read_text(encoding="utf-8"))
    i080 = json.loads(I080_PATH.read_text(encoding="utf-8"))

    novelty = {
        row["slug"]
        for row in i078["manuscripts"]
        if row.get("classification") == "NOVELTY_CANDIDATE"
    }
    theorem = {row["source_slug"] for row in i079["constructors"]}
    base_hold = {row["source_slug"] for row in i080["constructors"]}
    promoted = {row["source_slug"] for row in registry["full_promotions"]}
    partial_sources = {
        row["source_slug"] for row in registry["partial_subconstructors"]
    }

    if promoted - base_hold:
        raise I081PromotionError("I081_PROMOTED_SOURCE_NOT_IN_HOLD_PARENT")
    if partial_sources - base_hold:
        raise I081PromotionError("I081_PARTIAL_SOURCE_NOT_IN_HOLD_PARENT")
    if theorem & base_hold:
        raise I081PromotionError("I081_PARENT_PARTITION_OVERLAP")

    effective_theorem = theorem | promoted
    effective_hold = base_hold - promoted
    if effective_theorem & effective_hold:
        raise I081PromotionError("I081_EFFECTIVE_PARTITION_OVERLAP")
    if effective_theorem | effective_hold != novelty:
        raise I081PromotionError("I081_EFFECTIVE_PARTITION_COVERAGE_MISMATCH")
    if not partial_sources <= effective_hold:
        raise I081PromotionError("I081_PARTIAL_SOURCE_LEFT_HOLD")

    return {
        "novelty_sources": len(novelty),
        "effective_theorem_sources": len(effective_theorem),
        "effective_hold_sources": len(effective_hold),
        "full_promotions": len(promoted),
        "partial_subconstructors": len(partial_sources),
        "coverage_gap": 0,
        "duplicate_assignment": 0,
        "complete": True,
    }


def _find(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    for row in rows:
        if row.get(key) == value:
            return row
    raise I081PromotionError("I081_UNKNOWN_CONSTRUCTOR")


def invoke_promoted_constructor(
    promotion_id: str,
    assumption_binding: Mapping[str, Any] | None = None,
    *,
    proof_declaration: str | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    row = _find(registry["full_promotions"], "promotion_id", promotion_id)
    declarations = row["theorem_names"]
    selected = proof_declaration or declarations[0]
    if selected not in declarations:
        raise I081PromotionError("I081_PROOF_DECLARATION_NOT_ADMITTED")
    binding = dict(assumption_binding or {})
    frame = {
        "promotion_id": promotion_id,
        "source_slug": row["source_slug"],
        "source_tree_sha": row["source_tree_sha"],
        "source_revision": row["source_revision"],
        "family_doc_sha": row["family_doc"]["sha"],
        "comparator_sha": row["comparator"]["sha"],
        "solution_sha": row["solution"]["sha"],
        "proof_declaration": selected,
        "assumption_binding_sha256": _sha256(binding),
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "PROMOTED_SOURCE_BOUND_THEOREM_INVOCATION",
        "candidate_only": True,
    }
    receipt = hash72_digest(dictionary, frame)
    replay = hash72_digest(dictionary, frame)
    if receipt != replay:
        raise I081PromotionError("I081_PROMOTION_REPLAY_MISMATCH")
    return {
        "promotion_id": promotion_id,
        "source_slug": row["source_slug"],
        "proof_declaration": selected,
        "candidate_hash72": receipt,
        "replay_hash72": replay,
        "proof_surface_bound": True,
        "manuscript_status": "FORMAL_THEOREM_CONSTRUCTOR",
        "truth_promotion": False,
        "candidate_only": True,
        "vm81_mutation_invoked": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
        "canonical_persistence_invoked": False,
    }


def invoke_partial_subconstructor(
    subconstructor_id: str,
    assumption_binding: Mapping[str, Any] | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    row = _find(
        registry["partial_subconstructors"],
        "subconstructor_id",
        subconstructor_id,
    )
    frame = {
        "subconstructor_id": subconstructor_id,
        "source_slug": row["source_slug"],
        "source_tree_sha": row["source_tree_sha"],
        "source_revision": row["source_revision"],
        "family_doc_sha": row["family_doc"]["sha"],
        "comparator_sha": row["comparator"]["sha"],
        "solution_sha": row["solution"]["sha"],
        "theorem_names": row["theorem_names"],
        "assumption_binding_sha256": _sha256(dict(assumption_binding or {})),
        "excluded_scope": row["excluded_scope"],
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "PARTIAL_FORMAL_SUBCONSTRUCTOR_INVOCATION",
        "candidate_only": True,
    }
    receipt = hash72_digest(dictionary, frame)
    replay = hash72_digest(dictionary, frame)
    return {
        "subconstructor_id": subconstructor_id,
        "source_slug": row["source_slug"],
        "candidate_hash72": receipt,
        "replay_hash72": replay,
        "proof_surface_bound": True,
        "formal_subtheorem_available": True,
        "manuscript_status": "HOLD",
        "full_source_promotion": False,
        "excluded_scope": row["excluded_scope"],
        "truth_promotion": False,
        "candidate_only": True,
    }


def require_full_promotion_for_hold(
    hold_constructor_id: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    for row in registry["full_promotions"]:
        if row["hold_constructor_id"] == hold_constructor_id:
            return row
    for row in registry["partial_subconstructors"]:
        if row["hold_constructor_id"] == hold_constructor_id:
            raise I081PromotionError("I081_PARTIAL_SCOPE_NOT_FULL_PROMOTION")
    for row in registry["denied_full_promotions"]:
        if row["hold_constructor_id"] == hold_constructor_id:
            raise I081PromotionError("I081_FULL_PROMOTION_NOT_SUPPORTED")
    raise I081PromotionError("I081_HOLD_NOT_IN_AUDIT_BATCH")


__all__ = [
    "I081PromotionError",
    "REGISTRY_PATH",
    "SCHEMA",
    "effective_frontier",
    "invoke_partial_subconstructor",
    "invoke_promoted_constructor",
    "load_registry",
    "require_full_promotion_for_hold",
]
