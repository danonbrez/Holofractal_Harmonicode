"""Canonical Pass 220 I081 exact-source constructor promotion audit.

This is the reconciled I081 implementation.  It supersedes the competing
I081 PRs #742, #743, and #744 and preserves PR #741 as the single ancestry.

Promotion requires exact source identity plus a pinned proof surface whose
documented scope matches the source contract.  Supporting, partial, aggregate,
or merely stronger related results remain HOLD until an explicit source-
contract derivation exists.
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
EXPECTED_CANONICAL_PR = 741
EXPECTED_PROPOSAL_UNION = 29
EXPECTED_FULL_PROMOTIONS = 26
EXPECTED_PARTIAL = 13
EXPECTED_ADDITIONAL_DENIED = 9
EXPECTED_THEOREM_SOURCES = 80
EXPECTED_HOLD_SOURCES = 242
EXPECTED_FRONTIER = 322

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


def _validate_surface(surface: dict[str, Any]) -> None:
    comparator = surface.get("comparator", {})
    solution = surface.get("solution", {})
    if not comparator.get("path", "").startswith("lean/ComparatorChallenges/"):
        raise I081PromotionError("I081_COMPARATOR_PATH_INVALID")
    if not _is_hex40(comparator.get("sha")):
        raise I081PromotionError("I081_COMPARATOR_SHA_INVALID")
    if not solution.get("module") or not solution.get("path", "").startswith("lean/OAI/"):
        raise I081PromotionError("I081_SOLUTION_IDENTITY_INVALID")
    if not _is_hex40(solution.get("sha")):
        raise I081PromotionError("I081_SOLUTION_SHA_INVALID")
    if surface.get("source_revision") != EXPECTED_SOURCE_REVISION:
        raise I081PromotionError("I081_SURFACE_REVISION_DRIFT")
    names = surface.get("theorem_names")
    if not isinstance(names, list) or not names or not all(isinstance(x, str) and x for x in names):
        raise I081PromotionError("I081_THEOREM_LIST_EMPTY")


def load_registry(path: str | Path = REGISTRY_PATH) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise I081PromotionError("I081_SCHEMA_MISMATCH")
    if data.get("source_revision") != EXPECTED_SOURCE_REVISION:
        raise I081PromotionError("I081_SOURCE_REVISION_MISMATCH")
    if data.get("base_main") != EXPECTED_BASE_MAIN:
        raise I081PromotionError("I081_BASE_MAIN_MISMATCH")
    if data.get("canonical_i081") is not True or data.get("canonical_pr") != EXPECTED_CANONICAL_PR:
        raise I081PromotionError("I081_CANONICAL_IDENTITY_MISMATCH")
    if data.get("superseded_i081_prs") != [742, 743, 744]:
        raise I081PromotionError("I081_SUPERSEDED_PR_SET_DRIFT")

    reconciliation = data.get("proposal_reconciliation")
    full = data.get("full_promotions")
    partial = data.get("partial_subconstructors")
    denied = data.get("additional_denied_full_promotions")
    if not isinstance(reconciliation, list) or len(reconciliation) != EXPECTED_PROPOSAL_UNION:
        raise I081PromotionError("I081_RECONCILIATION_COUNT_MISMATCH")
    if not isinstance(full, list) or len(full) != EXPECTED_FULL_PROMOTIONS:
        raise I081PromotionError("I081_FULL_PROMOTION_COUNT_MISMATCH")
    if not isinstance(partial, list) or len(partial) != EXPECTED_PARTIAL:
        raise I081PromotionError("I081_PARTIAL_COUNT_MISMATCH")
    if not isinstance(denied, list) or len(denied) != EXPECTED_ADDITIONAL_DENIED:
        raise I081PromotionError("I081_DENIED_COUNT_MISMATCH")

    proposal_slugs = [row["source_slug"] for row in reconciliation]
    if len(set(proposal_slugs)) != EXPECTED_PROPOSAL_UNION:
        raise I081PromotionError("I081_RECONCILIATION_DUPLICATE_SOURCE")
    if any(not row.get("proposal_prs") for row in reconciliation):
        raise I081PromotionError("I081_RECONCILIATION_ORIGIN_MISSING")

    full_slugs = {row["source_slug"] for row in full}
    partial_slugs = {row["source_slug"] for row in partial}
    reconciled_full = {
        row["source_slug"] for row in reconciliation
        if row.get("decision") == "PROMOTE_FULL"
    }
    reconciled_partial = {
        row["source_slug"] for row in reconciliation
        if row.get("decision") == "KEEP_HOLD_PARTIAL_ONLY"
    }
    if full_slugs != reconciled_full:
        raise I081PromotionError("I081_RECONCILED_FULL_SET_MISMATCH")
    if len(reconciled_partial) != 3 or not reconciled_partial <= partial_slugs:
        raise I081PromotionError("I081_RECONCILED_PARTIAL_SET_MISMATCH")
    if full_slugs & partial_slugs:
        raise I081PromotionError("I081_FULL_PARTIAL_OVERLAP")

    full_ids = [row["promotion_id"] for row in full]
    partial_ids = [row["subconstructor_id"] for row in partial]
    if len(set(full_ids)) != len(full_ids):
        raise I081PromotionError("I081_DUPLICATE_PROMOTION_ID")
    if len(set(partial_ids)) != len(partial_ids):
        raise I081PromotionError("I081_DUPLICATE_PARTIAL_ID")

    allowed_relations = {
        "EXACT_DOC_SOURCE_AND_PROOF_SURFACE",
        "EXACT_DOC_SOURCE_MULTI_PROOF_SURFACE",
    }
    for row in full:
        if row.get("decision") != "PROMOTE_FULL_THEOREM_CONSTRUCTOR":
            raise I081PromotionError("I081_FULL_DECISION_DRIFT")
        if row.get("source_slug") != row.get("doc_preprint_slug"):
            raise I081PromotionError("I081_FULL_SOURCE_DOC_IDENTITY_MISMATCH")
        if row.get("proof_relation") not in allowed_relations:
            raise I081PromotionError("I081_FULL_PROOF_RELATION_NOT_EXACT")
        if not _is_hex40(row.get("source_tree_sha")):
            raise I081PromotionError("I081_FULL_SOURCE_TREE_INVALID")
        doc = row.get("family_doc", {})
        if doc.get("revision") != EXPECTED_SOURCE_REVISION or not _is_hex40(doc.get("sha")):
            raise I081PromotionError("I081_FULL_DOC_IDENTITY_INVALID")
        surfaces = row.get("formal_surfaces")
        if not isinstance(surfaces, list) or not surfaces:
            raise I081PromotionError("I081_FULL_PROOF_SURFACE_MISSING")
        for surface in surfaces:
            _validate_surface(surface)

    for row in partial:
        if row.get("decision") != "KEEP_HOLD_ADD_FORMAL_SUBCONSTRUCTOR":
            raise I081PromotionError("I081_PARTIAL_DECISION_DRIFT")
        if row.get("source_slug") != row.get("doc_preprint_slug"):
            raise I081PromotionError("I081_PARTIAL_SOURCE_DOC_IDENTITY_MISMATCH")
        if row.get("full_source_promotion") is not False:
            raise I081PromotionError("I081_PARTIAL_PROMOTION_DRIFT")
        if not row.get("excluded_scope"):
            raise I081PromotionError("I081_PARTIAL_EXCLUDED_SCOPE_MISSING")
        doc = row.get("family_doc", {})
        if doc.get("revision") != EXPECTED_SOURCE_REVISION or not _is_hex40(doc.get("sha")):
            raise I081PromotionError("I081_PARTIAL_DOC_IDENTITY_INVALID")
        surfaces = row.get("formal_surfaces")
        if not isinstance(surfaces, list) or not surfaces:
            raise I081PromotionError("I081_PARTIAL_PROOF_SURFACE_MISSING")
        for surface in surfaces:
            _validate_surface(surface)

    for row in denied:
        if row.get("decision") != "KEEP_HOLD" or not row.get("reason"):
            raise I081PromotionError("I081_ADDITIONAL_DENIAL_INVALID")

    authority = data.get("authority", {})
    if authority.get("candidate_only") is not True:
        raise I081PromotionError("I081_NOT_CANDIDATE_ONLY")
    if authority.get("external_formal_proof_is_provenance_authority") is not True:
        raise I081PromotionError("I081_EXTERNAL_PROOF_AUTHORITY_DRIFT")
    for key, value in authority.items():
        if key in ("candidate_only", "external_formal_proof_is_provenance_authority"):
            continue
        if value is not False:
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
        row["slug"] for row in i078["manuscripts"]
        if row.get("classification") == "NOVELTY_CANDIDATE"
    }
    inherited_theorem = {row["source_slug"] for row in i079["constructors"]}
    base_hold = {row["source_slug"] for row in i080["constructors"]}
    promoted = {row["source_slug"] for row in registry["full_promotions"]}
    partial_sources = {
        row["source_slug"] for row in registry["partial_subconstructors"]
    }

    if len(novelty) != EXPECTED_FRONTIER:
        raise I081PromotionError("I081_PARENT_FRONTIER_COUNT_DRIFT")
    if promoted - base_hold:
        raise I081PromotionError("I081_PROMOTED_SOURCE_NOT_IN_HOLD_PARENT")
    if partial_sources - base_hold:
        raise I081PromotionError("I081_PARTIAL_SOURCE_NOT_IN_HOLD_PARENT")
    if inherited_theorem & base_hold:
        raise I081PromotionError("I081_PARENT_PARTITION_OVERLAP")

    effective_theorem = inherited_theorem | promoted
    effective_hold = base_hold - promoted
    if effective_theorem & effective_hold:
        raise I081PromotionError("I081_EFFECTIVE_PARTITION_OVERLAP")
    if effective_theorem | effective_hold != novelty:
        raise I081PromotionError("I081_EFFECTIVE_PARTITION_COVERAGE_MISMATCH")
    if not partial_sources <= effective_hold:
        raise I081PromotionError("I081_PARTIAL_SOURCE_LEFT_HOLD")
    if len(effective_theorem) != EXPECTED_THEOREM_SOURCES:
        raise I081PromotionError("I081_THEOREM_COUNT_MISMATCH")
    if len(effective_hold) != EXPECTED_HOLD_SOURCES:
        raise I081PromotionError("I081_HOLD_COUNT_MISMATCH")

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


def _select_surface(
    row: dict[str, Any],
    proof_declaration: str | None,
) -> tuple[dict[str, Any], str]:
    surfaces = row["formal_surfaces"]
    allowed = [
        (surface, name)
        for surface in surfaces
        for name in surface["theorem_names"]
    ]
    if proof_declaration is None:
        return allowed[0]
    for surface, name in allowed:
        if name == proof_declaration:
            return surface, name
    raise I081PromotionError("I081_PROOF_DECLARATION_NOT_ADMITTED")


def invoke_promoted_constructor(
    promotion_id: str,
    assumption_binding: Mapping[str, Any] | None = None,
    *,
    proof_declaration: str | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    row = _find(registry["full_promotions"], "promotion_id", promotion_id)
    surface, selected = _select_surface(row, proof_declaration)
    frame = {
        "promotion_id": promotion_id,
        "source_slug": row["source_slug"],
        "source_tree_sha": row["source_tree_sha"],
        "source_revision": row["source_revision"],
        "family_doc_sha": row["family_doc"]["sha"],
        "comparator_sha": surface["comparator"]["sha"],
        "solution_sha": surface["solution"]["sha"],
        "proof_declaration": selected,
        "assumption_binding_sha256": _sha256(dict(assumption_binding or {})),
        "proof_relation": row["proof_relation"],
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "CANONICAL_I081_PROMOTED_THEOREM_INVOCATION",
        "candidate_only": True,
    }
    receipt = hash72_digest(dictionary, frame)
    replay = hash72_digest(dictionary, frame)
    if receipt != replay:
        raise I081PromotionError("I081_PROMOTION_REPLAY_MISMATCH")
    return {
        **frame,
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
    surface, selected = _select_surface(row, None)
    frame = {
        "subconstructor_id": subconstructor_id,
        "source_slug": row["source_slug"],
        "source_tree_sha": row["source_tree_sha"],
        "source_revision": row["source_revision"],
        "family_doc_sha": row["family_doc"]["sha"],
        "comparator_sha": surface["comparator"]["sha"],
        "solution_sha": surface["solution"]["sha"],
        "proof_declaration": selected,
        "assumption_binding_sha256": _sha256(dict(assumption_binding or {})),
        "excluded_scope": row["excluded_scope"],
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "CANONICAL_I081_PARTIAL_FORMAL_SUBCONSTRUCTOR",
        "candidate_only": True,
    }
    receipt = hash72_digest(dictionary, frame)
    replay = hash72_digest(dictionary, frame)
    return {
        **frame,
        "candidate_hash72": receipt,
        "replay_hash72": replay,
        "proof_surface_bound": True,
        "formal_subtheorem_available": True,
        "manuscript_status": "HOLD",
        "full_source_promotion": False,
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
    for row in registry["additional_denied_full_promotions"]:
        if row["hold_constructor_id"] == hold_constructor_id:
            raise I081PromotionError("I081_FULL_PROMOTION_NOT_SUPPORTED")
    raise I081PromotionError("I081_HOLD_NOT_IN_CANONICAL_AUDIT")


def build_registry_receipt(
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    frontier = effective_frontier(registry)
    payload = {
        "source_revision": registry["source_revision"],
        "canonical_pr": registry["canonical_pr"],
        "superseded_i081_prs": registry["superseded_i081_prs"],
        "proposal_reconciliation": registry["proposal_reconciliation"],
        "full_promotions": registry["full_promotions"],
        "partial_subconstructors": registry["partial_subconstructors"],
        "frontier": frontier,
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "CANONICAL_I081_RECONCILED_REGISTRY",
        "candidate_only": True,
    }
    receipt = hash72_digest(dictionary, payload)
    replay = hash72_digest(dictionary, payload)
    if receipt != replay:
        raise I081PromotionError("I081_REGISTRY_REPLAY_MISMATCH")
    return {
        "registry_sha256": _sha256(payload),
        "candidate_hash72": receipt,
        "replay_hash72": replay,
        "frontier": frontier,
        "canonical_pr": EXPECTED_CANONICAL_PR,
        "candidate_only": True,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
    }


__all__ = [
    "I081PromotionError",
    "REGISTRY_PATH",
    "SCHEMA",
    "build_registry_receipt",
    "effective_frontier",
    "invoke_partial_subconstructor",
    "invoke_promoted_constructor",
    "load_registry",
    "require_full_promotion_for_hold",
]
