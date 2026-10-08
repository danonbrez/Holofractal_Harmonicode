"""Pass 220 I081 doc-bound formalization promotions.

I081 audits a priority set of OpenAI family documentation at the frozen source
revision.  Exact source links with main-claim formal coverage are promoted from
I080 HOLD wrappers to source-bound theorem constructors.  Sources with only
selected/supporting formal results remain HOLD and receive partial evidence
bindings instead.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

SCHEMA = "HHS_PASS_220_I081_DOC_BOUND_FORMALIZATION_PROMOTIONS_V1"
EXPECTED_SOURCE_REVISION = "adc7f1241b42e322a6451854ab7e4b4c146bf78a"
EXPECTED_BASE_MAIN = "e2e4fcfa539e2c80997eb796abe5dbce1227d559"
EXPECTED_PROMOTIONS = 16
EXPECTED_PARTIAL_BINDINGS = 9
EXPECTED_ACTIVE_THEOREMS = 70
EXPECTED_ACTIVE_HOLDS = 252
EXPECTED_FRONTIER_TOTAL = 322

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/pass220/openai_math_doc_bound_formalization_promotions_v1.json"
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


def load_registry(path: str | Path = REGISTRY_PATH) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise I081PromotionError("I081_SCHEMA_MISMATCH")
    if data.get("source_revision") != EXPECTED_SOURCE_REVISION:
        raise I081PromotionError("I081_SOURCE_REVISION_MISMATCH")
    if data.get("base_main") != EXPECTED_BASE_MAIN:
        raise I081PromotionError("I081_BASE_MAIN_MISMATCH")

    promotions = data.get("promotions")
    partials = data.get("partial_bindings")
    if not isinstance(promotions, list) or len(promotions) != EXPECTED_PROMOTIONS:
        raise I081PromotionError("I081_PROMOTION_COUNT_MISMATCH")
    if not isinstance(partials, list) or len(partials) != EXPECTED_PARTIAL_BINDINGS:
        raise I081PromotionError("I081_PARTIAL_COUNT_MISMATCH")

    promotion_ids = [row["constructor_id"] for row in promotions]
    binding_ids = [row["binding_id"] for row in partials]
    if len(set(promotion_ids)) != len(promotion_ids):
        raise I081PromotionError("I081_DUPLICATE_PROMOTION_ID")
    if len(set(binding_ids)) != len(binding_ids):
        raise I081PromotionError("I081_DUPLICATE_PARTIAL_ID")
    if promotion_ids != sorted(promotion_ids) or binding_ids != sorted(binding_ids):
        raise I081PromotionError("I081_NONCANONICAL_ORDER")

    superseded = [row["supersedes_hold_constructor_id"] for row in promotions]
    partial_holds = [row["supersedes_hold_constructor_id"] for row in partials]
    if len(set(superseded)) != len(superseded):
        raise I081PromotionError("I081_DUPLICATE_SUPERSEDED_HOLD")
    if set(superseded) & set(partial_holds):
        raise I081PromotionError("I081_PROMOTION_PARTIAL_OVERLAP")

    for row in promotions:
        if row.get("coverage_class") != "DOC_VERIFIED_MAIN_CLAIM_COVERAGE":
            raise I081PromotionError("I081_PROMOTION_COVERAGE_CLASS_DRIFT")
        if row.get("source_revision") != EXPECTED_SOURCE_REVISION:
            raise I081PromotionError("I081_PROMOTION_SOURCE_DRIFT")
        if not row.get("formal_surfaces"):
            raise I081PromotionError("I081_PROMOTION_PROOF_SURFACE_MISSING")
        for proof in row["formal_surfaces"]:
            if not proof.get("comparator") or not proof.get("solution_module"):
                raise I081PromotionError("I081_PROMOTION_PROOF_SURFACE_INVALID")
            if not proof.get("theorem_names"):
                raise I081PromotionError("I081_PROMOTION_THEOREM_NAMES_MISSING")
        authority = row.get("authority", {})
        if authority.get("candidate_only") is not True:
            raise I081PromotionError("I081_PROMOTION_NOT_CANDIDATE_ONLY")
        if authority.get("external_formal_proof_authority") is not True:
            raise I081PromotionError("I081_EXTERNAL_PROOF_AUTHORITY_MISSING")
        for key in (
            "independent_hhs_reproof",
            "canonical_learning_commit_invoked",
            "model_weight_mutation_invoked",
            "vm81_mutation_invoked",
            "canonical_hash72_minted",
            "canonical_hash216_minted",
            "canonical_persistence_invoked",
            "floating_point_authority",
        ):
            if authority.get(key) is not False:
                raise I081PromotionError(f"I081_PROMOTION_AUTHORITY_DRIFT:{key}")

    for row in partials:
        if row.get("coverage_class") != "PARTIAL_SELECTED_RESULT_ONLY":
            raise I081PromotionError("I081_PARTIAL_COVERAGE_CLASS_DRIFT")
        if row.get("whole_claim_truth_authority") is not False:
            raise I081PromotionError("I081_PARTIAL_WHOLE_CLAIM_AUTHORITY_DRIFT")
        if not row.get("formal_surfaces"):
            raise I081PromotionError("I081_PARTIAL_PROOF_SURFACE_MISSING")
    return data


def validate_active_frontier(
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    i079 = json.loads(I079_PATH.read_text(encoding="utf-8"))
    i080 = json.loads(I080_PATH.read_text(encoding="utf-8"))

    i079_ids = {row["constructor_id"] for row in i079["constructors"]}
    holds = {row["constructor_id"]: row for row in i080["constructors"]}
    promoted_hold_ids = {
        row["supersedes_hold_constructor_id"] for row in registry["promotions"]
    }
    partial_hold_ids = {
        row["supersedes_hold_constructor_id"] for row in registry["partial_bindings"]
    }
    if not promoted_hold_ids <= holds.keys():
        raise I081PromotionError("I081_PROMOTED_HOLD_NOT_FOUND")
    if not partial_hold_ids <= holds.keys():
        raise I081PromotionError("I081_PARTIAL_HOLD_NOT_FOUND")
    for row in registry["promotions"]:
        hold = holds[row["supersedes_hold_constructor_id"]]
        if hold["source_slug"] != row["source_slug"]:
            raise I081PromotionError("I081_PROMOTION_SOURCE_BINDING_MISMATCH")
        if hold["source_tree_sha"] != row["source_tree_sha"]:
            raise I081PromotionError("I081_PROMOTION_TREE_BINDING_MISMATCH")
    for row in registry["partial_bindings"]:
        hold = holds[row["supersedes_hold_constructor_id"]]
        if hold["source_slug"] != row["source_slug"]:
            raise I081PromotionError("I081_PARTIAL_SOURCE_BINDING_MISMATCH")

    active_holds = set(holds) - promoted_hold_ids
    active_theorems = i079_ids | {
        row["constructor_id"] for row in registry["promotions"]
    }
    if len(active_theorems) != EXPECTED_ACTIVE_THEOREMS:
        raise I081PromotionError("I081_ACTIVE_THEOREM_COUNT_MISMATCH")
    if len(active_holds) != EXPECTED_ACTIVE_HOLDS:
        raise I081PromotionError("I081_ACTIVE_HOLD_COUNT_MISMATCH")
    if len(active_theorems) + len(active_holds) != EXPECTED_FRONTIER_TOTAL:
        raise I081PromotionError("I081_ACTIVE_FRONTIER_TOTAL_MISMATCH")
    return {
        "i079_theorem_constructors": len(i079_ids),
        "i081_promotions": len(registry["promotions"]),
        "active_theorem_constructors": len(active_theorems),
        "active_hold_constructors": len(active_holds),
        "partial_formalization_bindings": len(partial_hold_ids),
        "frontier_total": EXPECTED_FRONTIER_TOTAL,
        "coverage_gap": 0,
    }


def _find_promotion(
    constructor_id: str,
    registry: dict[str, Any],
) -> dict[str, Any]:
    for row in registry["promotions"]:
        if row["constructor_id"] == constructor_id:
            return row
    raise I081PromotionError("I081_UNKNOWN_PROMOTED_CONSTRUCTOR")


def _find_partial(binding_id: str, registry: dict[str, Any]) -> dict[str, Any]:
    for row in registry["partial_bindings"]:
        if row["binding_id"] == binding_id:
            return row
    raise I081PromotionError("I081_UNKNOWN_PARTIAL_BINDING")


def build_registry_receipt(
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    frontier = validate_active_frontier(registry)
    payload = {
        "source_revision": registry["source_revision"],
        "promotions": registry["promotions"],
        "partial_bindings": registry["partial_bindings"],
        "frontier": frontier,
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "DOC_BOUND_FORMALIZATION_PROMOTION_REGISTRY",
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
        "candidate_only": True,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
    }


def invoke_promoted_constructor(
    constructor_id: str,
    assumption_binding: Mapping[str, Any] | None = None,
    *,
    theorem_name: str | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    row = _find_promotion(constructor_id, registry)
    allowed = [
        name
        for surface in row["formal_surfaces"]
        for name in surface["theorem_names"]
    ]
    selected = theorem_name or allowed[0]
    if selected not in allowed:
        raise I081PromotionError("I081_THEOREM_NOT_ADMITTED")
    surface = next(
        surface for surface in row["formal_surfaces"]
        if selected in surface["theorem_names"]
    )
    binding = dict(assumption_binding or {})
    frame = {
        "constructor_id": constructor_id,
        "source_slug": row["source_slug"],
        "source_tree_sha": row["source_tree_sha"],
        "source_revision": EXPECTED_SOURCE_REVISION,
        "source_doc": row["source_doc"],
        "comparator": surface["comparator"],
        "solution_module": surface["solution_module"],
        "theorem_name": selected,
        "assumption_binding_sha256": _sha256(binding),
        "coverage_class": row["coverage_class"],
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "DOC_VERIFIED_THEOREM_INVOCATION",
        "candidate_only": True,
    }
    receipt = hash72_digest(dictionary, frame)
    replay = hash72_digest(dictionary, frame)
    return {
        **frame,
        "candidate_hash72": receipt,
        "replay_hash72": replay,
        "external_formal_proof_authority": True,
        "independent_hhs_reproof": False,
        "truth_promotion": False,
        "candidate_only": True,
        "vm81_mutation_invoked": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
        "canonical_persistence_invoked": False,
    }


def invoke_partial_binding(
    binding_id: str,
    evidence_binding: Mapping[str, Any] | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    row = _find_partial(binding_id, registry)
    frame = {
        "binding_id": binding_id,
        "source_slug": row["source_slug"],
        "source_tree_sha": row["source_tree_sha"],
        "source_revision": EXPECTED_SOURCE_REVISION,
        "source_doc": row["source_doc"],
        "formal_surfaces": row["formal_surfaces"],
        "evidence_binding_sha256": _sha256(dict(evidence_binding or {})),
        "coverage_class": row["coverage_class"],
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "PARTIAL_FORMALIZATION_EVIDENCE",
        "candidate_only": True,
    }
    receipt = hash72_digest(dictionary, frame)
    replay = hash72_digest(dictionary, frame)
    return {
        **frame,
        "candidate_hash72": receipt,
        "replay_hash72": replay,
        "whole_claim_status": "HOLD",
        "whole_claim_truth_authority": False,
        "candidate_only": True,
        "execution_authority": False,
        "vm81_mutation_invoked": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
        "canonical_persistence_invoked": False,
    }


__all__ = [
    "I081PromotionError",
    "REGISTRY_PATH",
    "SCHEMA",
    "build_registry_receipt",
    "invoke_partial_binding",
    "invoke_promoted_constructor",
    "load_registry",
    "validate_active_frontier",
]
