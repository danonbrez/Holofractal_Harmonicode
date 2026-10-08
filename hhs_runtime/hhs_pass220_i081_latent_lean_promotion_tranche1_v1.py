"""Pass 220 I081 latent Lean formalization promotion overlay."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

SCHEMA = "HHS_PASS_220_I081_LATENT_LEAN_PROMOTION_TRANCHE1_V1"
EXPECTED_SOURCE_REVISION = "adc7f1241b42e322a6451854ab7e4b4c146bf78a"
EXPECTED_BASE_MAIN = "e2e4fcfa539e2c80997eb796abe5dbce1227d559"
EXPECTED_PROMOTION_COUNT = 10
EXPECTED_PARTIAL_COUNT = 3
EXPECTED_PROOF_DECLARATION_COUNT = 18
ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/pass220/openai_math_latent_lean_promotion_tranche1_v1.json"
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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry(path: str | Path = REGISTRY_PATH) -> dict[str, Any]:
    data = _load_json(Path(path))
    if data.get("schema") != SCHEMA:
        raise I081PromotionError("I081_SCHEMA_MISMATCH")
    if data.get("source_revision") != EXPECTED_SOURCE_REVISION:
        raise I081PromotionError("I081_SOURCE_REVISION_MISMATCH")
    if data.get("base_main") != EXPECTED_BASE_MAIN:
        raise I081PromotionError("I081_BASE_MAIN_MISMATCH")

    promotions = data.get("promotions")
    partials = data.get("partial_formalizations_retained_on_hold")
    if not isinstance(promotions, list) or len(promotions) != EXPECTED_PROMOTION_COUNT:
        raise I081PromotionError("I081_PROMOTION_COUNT_MISMATCH")
    if not isinstance(partials, list) or len(partials) != EXPECTED_PARTIAL_COUNT:
        raise I081PromotionError("I081_PARTIAL_COUNT_MISMATCH")

    promoted_ids = [row.get("promoted_constructor_id") for row in promotions]
    hold_ids = [row.get("supersedes_hold_constructor_id") for row in promotions]
    if len(set(promoted_ids)) != len(promoted_ids):
        raise I081PromotionError("I081_DUPLICATE_PROMOTED_ID")
    if len(set(hold_ids)) != len(hold_ids):
        raise I081PromotionError("I081_DUPLICATE_SUPERSEDED_HOLD_ID")
    if promoted_ids != sorted(promoted_ids):
        raise I081PromotionError("I081_PROMOTION_ORDER_NOT_CANONICAL")

    proof_count = 0
    for row in promotions:
        if row.get("constructor_kind") != "HHS_SOURCE_BOUND_FORMAL_THEOREM_CONSTRUCTOR_V1":
            raise I081PromotionError("I081_CONSTRUCTOR_KIND_MISMATCH")
        if row.get("status") != "PROMOTED_I081_FROM_HOLD":
            raise I081PromotionError("I081_PROMOTION_STATUS_MISMATCH")
        doc = row.get("formalization_scope_doc", {})
        if doc.get("source_link_exact") is not True or not doc.get("sha"):
            raise I081PromotionError("I081_SCOPE_DOC_BINDING_MISSING")
        surfaces = row.get("proof_surfaces")
        if not isinstance(surfaces, list) or not surfaces:
            raise I081PromotionError("I081_PROOF_SURFACE_MISSING")
        if row.get("proof_surface_count") != len(surfaces):
            raise I081PromotionError("I081_PROOF_SURFACE_COUNT_DRIFT")
        proof_count += len(surfaces)
        for surface in surfaces:
            for key in (
                "comparator_config",
                "comparator_config_sha",
                "solution_module",
                "solution_file",
                "theorem_declaration",
            ):
                if not surface.get(key):
                    raise I081PromotionError(f"I081_PROOF_SURFACE_FIELD_MISSING:{key}")
        authority = row.get("authority", {})
        if authority.get("candidate_only") is not True:
            raise I081PromotionError("I081_PROMOTION_NOT_CANDIDATE_ONLY")
        for key, value in authority.items():
            if key != "candidate_only" and value is not False:
                raise I081PromotionError(f"I081_AUTHORITY_DRIFT:{key}")

    if proof_count != EXPECTED_PROOF_DECLARATION_COUNT:
        raise I081PromotionError("I081_TOTAL_PROOF_COUNT_MISMATCH")

    for row in partials:
        if row.get("status") != "REMAIN_HOLD":
            raise I081PromotionError("I081_PARTIAL_STATUS_DRIFT")
        if row.get("theorem_truth_authority") is not False:
            raise I081PromotionError("I081_PARTIAL_TRUTH_AUTHORITY_DRIFT")

    return data


def validate_effective_frontier(
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    i079 = _load_json(I079_PATH)
    i080 = _load_json(I080_PATH)

    base_theorem = {row["source_slug"] for row in i079["constructors"]}
    base_hold = {row["source_slug"] for row in i080["constructors"]}
    promoted = {row["source_slug"] for row in registry["promotions"]}

    if promoted & base_theorem:
        raise I081PromotionError("I081_PROMOTION_ALREADY_THEOREM")
    if not promoted <= base_hold:
        raise I081PromotionError("I081_PROMOTION_NOT_IN_HOLD_FRONTIER")

    effective_theorem = base_theorem | promoted
    effective_hold = base_hold - promoted
    if effective_theorem & effective_hold:
        raise I081PromotionError("I081_EFFECTIVE_FRONTIER_OVERLAP")
    if len(effective_theorem) != 64:
        raise I081PromotionError("I081_EFFECTIVE_THEOREM_COUNT_MISMATCH")
    if len(effective_hold) != 258:
        raise I081PromotionError("I081_EFFECTIVE_HOLD_COUNT_MISMATCH")
    if len(effective_theorem | effective_hold) != 322:
        raise I081PromotionError("I081_EFFECTIVE_COVERAGE_MISMATCH")

    partial_slugs = {
        row["source_slug"]
        for row in registry["partial_formalizations_retained_on_hold"]
    }
    if not partial_slugs <= effective_hold:
        raise I081PromotionError("I081_PARTIAL_NOT_RETAINED_ON_HOLD")

    return {
        "effective_theorem_count": len(effective_theorem),
        "effective_hold_count": len(effective_hold),
        "coverage_total": len(effective_theorem | effective_hold),
        "coverage_gap": 0,
        "partial_formalization_hold_count": len(partial_slugs),
        "complete": True,
    }


def list_promoted_constructors(
    registry: dict[str, Any] | None = None,
) -> tuple[str, ...]:
    registry = load_registry() if registry is None else registry
    return tuple(row["promoted_constructor_id"] for row in registry["promotions"])


def get_promoted_constructor(
    constructor_id: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    for row in registry["promotions"]:
        if row["promoted_constructor_id"] == constructor_id:
            return row
    raise I081PromotionError("I081_UNKNOWN_PROMOTED_CONSTRUCTOR")


def invoke_promoted_constructor(
    constructor_id: str,
    assumption_binding: Mapping[str, Any] | None = None,
    theorem_declaration: str | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    row = get_promoted_constructor(constructor_id, registry)
    declarations = [surface["theorem_declaration"] for surface in row["proof_surfaces"]]
    selected = theorem_declaration or declarations[0]
    if selected not in declarations:
        raise I081PromotionError("I081_THEOREM_DECLARATION_NOT_ADMITTED")
    surface = next(
        item for item in row["proof_surfaces"]
        if item["theorem_declaration"] == selected
    )
    binding = dict(assumption_binding or {})
    frame = {
        "constructor_id": constructor_id,
        "supersedes_hold_constructor_id": row["supersedes_hold_constructor_id"],
        "source_revision": row["source_revision"],
        "source_tree_sha": row["source_tree_sha"],
        "scope_doc_sha": row["formalization_scope_doc"]["sha"],
        "comparator_config_sha": surface["comparator_config_sha"],
        "theorem_declaration": selected,
        "solution_file": surface["solution_file"],
        "assumption_binding_sha256": _sha256(binding),
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "LATENT_FORMAL_THEOREM_PROMOTION_INVOCATION",
        "candidate_only": True,
    }
    receipt = hash72_digest(dictionary, frame)
    replay = hash72_digest(dictionary, frame)
    if receipt != replay:
        raise I081PromotionError("I081_INVOCATION_REPLAY_MISMATCH")
    return {
        "schema": SCHEMA,
        "constructor_id": constructor_id,
        "source_slug": row["source_slug"],
        "theorem_declaration": selected,
        "solution_file": surface["solution_file"],
        "candidate_hash72": receipt,
        "replay_hash72": replay,
        "proof_surface_bound": True,
        "truth_promotion": False,
        "candidate_only": True,
        "vm81_mutation_invoked": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
        "canonical_persistence_invoked": False,
    }


def build_promotion_receipt(
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    frontier = validate_effective_frontier(registry)
    payload = {
        "source_revision": registry["source_revision"],
        "promotions": registry["promotions"],
        "partials": registry["partial_formalizations_retained_on_hold"],
        "frontier": frontier,
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "LATENT_LEAN_PROMOTION_OVERLAY",
        "candidate_only": True,
    }
    receipt = hash72_digest(dictionary, payload)
    replay = hash72_digest(dictionary, payload)
    if receipt != replay:
        raise I081PromotionError("I081_PROMOTION_REPLAY_MISMATCH")
    return {
        "overlay_sha256": _sha256(payload),
        "candidate_hash72": receipt,
        "replay_hash72": replay,
        "promotion_count": EXPECTED_PROMOTION_COUNT,
        "proof_declaration_count": EXPECTED_PROOF_DECLARATION_COUNT,
        "frontier": frontier,
        "candidate_only": True,
    }


__all__ = [
    "EXPECTED_PROMOTION_COUNT",
    "EXPECTED_PROOF_DECLARATION_COUNT",
    "I081PromotionError",
    "REGISTRY_PATH",
    "SCHEMA",
    "build_promotion_receipt",
    "get_promoted_constructor",
    "invoke_promoted_constructor",
    "list_promoted_constructors",
    "load_registry",
    "validate_effective_frontier",
]
