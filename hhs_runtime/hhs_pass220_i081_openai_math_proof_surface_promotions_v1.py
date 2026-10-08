"""Pass 220 I081 proof-surface promotions for OpenAI math HOLD constructors.

I081 discovers proof surfaces that were not represented in the I079
formalization.yaml source list but are explicitly linked from the pinned
lean/docs family documentation to ComparatorChallenge configs with theorem
declarations.  Promotions are an overlay over immutable I079/I080 history.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

SCHEMA = "HHS_PASS_220_I081_OPENAI_MATH_PROOF_SURFACE_PROMOTIONS_V1"
EXPECTED_SOURCE_REVISION = "adc7f1241b42e322a6451854ab7e4b4c146bf78a"
EXPECTED_BASE_MAIN = "e2e4fcfa539e2c80997eb796abe5dbce1227d559"
EXPECTED_PROMOTION_COUNT = 17
EXPECTED_INHERITED_THEOREM_COUNT = 54
EXPECTED_INHERITED_HOLD_COUNT = 268
EXPECTED_ACTIVE_THEOREM_COUNT = 71
EXPECTED_ACTIVE_HOLD_COUNT = 251
EXPECTED_NOVELTY_COUNT = 322

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/pass220/openai_math_proof_surface_promotions_v1.json"
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

    rows = data.get("promotions")
    if not isinstance(rows, list) or len(rows) != EXPECTED_PROMOTION_COUNT:
        raise I081PromotionError("I081_PROMOTION_COUNT_MISMATCH")
    source_slugs = [row.get("source_slug") for row in rows]
    constructor_ids = [row.get("promoted_constructor_id") for row in rows]
    if len(set(source_slugs)) != len(source_slugs):
        raise I081PromotionError("I081_DUPLICATE_SOURCE_PROMOTION")
    if len(set(constructor_ids)) != len(constructor_ids):
        raise I081PromotionError("I081_DUPLICATE_CONSTRUCTOR_ID")
    if constructor_ids != sorted(constructor_ids):
        raise I081PromotionError("I081_PROMOTION_ORDER_NOT_CANONICAL")

    for row in rows:
        if row.get("source_revision") != EXPECTED_SOURCE_REVISION:
            raise I081PromotionError("I081_PROMOTION_SOURCE_REVISION_MISMATCH")
        if row.get("previous_status") != "HOLD_NO_CATALOGUED_MAIN_RESULT_PROOF":
            raise I081PromotionError("I081_PREVIOUS_STATUS_MISMATCH")
        if row.get("promoted_status") != "FORMAL_PROOF_SURFACE_BOUND":
            raise I081PromotionError("I081_PROMOTED_STATUS_MISMATCH")
        if not _is_hex40(row.get("source_tree_sha")):
            raise I081PromotionError("I081_SOURCE_TREE_SHA_INVALID")
        expected = (
            "HHS-OAI-THEOREM-F"
            + row["family_id"]
            + "-"
            + row["source_tree_sha"][:12].upper()
        )
        if row.get("promoted_constructor_id") != expected:
            raise I081PromotionError("I081_CONSTRUCTOR_ID_SOURCE_MISMATCH")
        doc = row.get("documentation", {})
        if doc.get("source_listed") is not True or not _is_hex40(doc.get("blob_sha")):
            raise I081PromotionError("I081_DOCUMENTATION_EVIDENCE_INVALID")
        comparator = row.get("comparator", {})
        if not _is_hex40(comparator.get("blob_sha")):
            raise I081PromotionError("I081_COMPARATOR_IDENTITY_INVALID")
        theorem_names = comparator.get("admitted_theorem_names")
        if not isinstance(theorem_names, list) or not theorem_names:
            raise I081PromotionError("I081_THEOREM_DECLARATION_MISSING")
        if row.get("proof_relation") not in {
            "EXACT_DOC_SOURCE_AND_COMPARATOR",
            "DOC_EXPLICIT_STRONGER_FORMAL_RESULT_IMPLIES_SOURCE",
        }:
            raise I081PromotionError("I081_PROOF_RELATION_INVALID")
        if (
            row.get("proof_relation")
            == "DOC_EXPLICIT_STRONGER_FORMAL_RESULT_IMPLIES_SOURCE"
            and not row.get("relation_note")
        ):
            raise I081PromotionError("I081_STRONGER_RELATION_NOTE_MISSING")
        authority = row.get("authority", {})
        if authority.get("candidate_only") is not True:
            raise I081PromotionError("I081_NOT_CANDIDATE_ONLY")
        if authority.get("external_formal_proof_bound") is not True:
            raise I081PromotionError("I081_FORMAL_PROOF_NOT_BOUND")
        if authority.get("source_claim_formal_support") is not True:
            raise I081PromotionError("I081_SOURCE_SUPPORT_NOT_BOUND")
        for key in (
            "canonical_truth_promotion",
            "execution_authority",
            "canonical_learning_commit_invoked",
            "model_weight_mutation_invoked",
            "vm81_mutation_invoked",
            "canonical_hash72_minted",
            "canonical_hash216_minted",
            "canonical_persistence_invoked",
            "floating_point_authority",
        ):
            if authority.get(key) is not False:
                raise I081PromotionError(f"I081_AUTHORITY_DRIFT:{key}")
    return data


def validate_active_partition(
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    i079 = json.loads(I079_PATH.read_text(encoding="utf-8"))
    i080 = json.loads(I080_PATH.read_text(encoding="utf-8"))

    inherited_theorem = {row["source_slug"] for row in i079["constructors"]}
    inherited_hold = {row["source_slug"] for row in i080["constructors"]}
    promoted = {row["source_slug"] for row in registry["promotions"]}

    if len(inherited_theorem) != EXPECTED_INHERITED_THEOREM_COUNT:
        raise I081PromotionError("I081_PARENT_THEOREM_COUNT_DRIFT")
    if len(inherited_hold) != EXPECTED_INHERITED_HOLD_COUNT:
        raise I081PromotionError("I081_PARENT_HOLD_COUNT_DRIFT")
    if inherited_theorem & inherited_hold:
        raise I081PromotionError("I081_PARENT_PARTITION_OVERLAP")
    if not promoted <= inherited_hold:
        raise I081PromotionError("I081_PROMOTION_NOT_FROM_HOLD")
    if promoted & inherited_theorem:
        raise I081PromotionError("I081_PROMOTION_ALREADY_THEOREM")

    active_theorem = inherited_theorem | promoted
    active_hold = inherited_hold - promoted
    if len(active_theorem) != EXPECTED_ACTIVE_THEOREM_COUNT:
        raise I081PromotionError("I081_ACTIVE_THEOREM_COUNT_DRIFT")
    if len(active_hold) != EXPECTED_ACTIVE_HOLD_COUNT:
        raise I081PromotionError("I081_ACTIVE_HOLD_COUNT_DRIFT")
    if active_theorem & active_hold:
        raise I081PromotionError("I081_ACTIVE_PARTITION_OVERLAP")
    if len(active_theorem | active_hold) != EXPECTED_NOVELTY_COUNT:
        raise I081PromotionError("I081_ACTIVE_COVERAGE_MISMATCH")

    return {
        "inherited_theorem_count": len(inherited_theorem),
        "inherited_hold_count": len(inherited_hold),
        "promoted_count": len(promoted),
        "active_theorem_count": len(active_theorem),
        "active_hold_count": len(active_hold),
        "coverage_gap": 0,
        "duplicate_assignment_count": 0,
        "complete": True,
    }


def list_promotions(registry: dict[str, Any] | None = None) -> tuple[str, ...]:
    registry = load_registry() if registry is None else registry
    return tuple(row["promoted_constructor_id"] for row in registry["promotions"])


def get_promotion(
    promoted_constructor_id: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    for row in registry["promotions"]:
        if row["promoted_constructor_id"] == promoted_constructor_id:
            return row
    raise I081PromotionError("I081_UNKNOWN_PROMOTED_CONSTRUCTOR")


def build_overlay_receipt(
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    partition = validate_active_partition(registry)
    payload = {
        "source_revision": registry["source_revision"],
        "base_main": registry["base_main"],
        "promotions": registry["promotions"],
        "partition": partition,
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "PROOF_SURFACE_PROMOTION_OVERLAY",
        "candidate_only": True,
    }
    first = hash72_digest(dictionary, payload)
    replay = hash72_digest(dictionary, payload)
    if first != replay:
        raise I081PromotionError("I081_OVERLAY_REPLAY_MISMATCH")
    return {
        "overlay_sha256": _sha256(payload),
        "candidate_hash72": first,
        "replay_hash72": replay,
        "partition": partition,
        "candidate_only": True,
        "external_formal_proof_bound": True,
        "canonical_truth_promotion": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
    }


def invoke_promoted_constructor(
    promoted_constructor_id: str,
    assumption_binding: Mapping[str, Any] | None = None,
    proof_declaration: str | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    row = get_promotion(promoted_constructor_id, registry)
    declarations = row["comparator"]["admitted_theorem_names"]
    selected = proof_declaration or declarations[0]
    if selected not in declarations:
        raise I081PromotionError("I081_PROOF_DECLARATION_NOT_ADMITTED")

    binding = dict(assumption_binding or {})
    frame = {
        "promoted_constructor_id": promoted_constructor_id,
        "hold_constructor_id": row["hold_constructor_id"],
        "source_revision": row["source_revision"],
        "source_tree_sha": row["source_tree_sha"],
        "family_id": row["family_id"],
        "documentation_blob_sha": row["documentation"]["blob_sha"],
        "comparator_blob_sha": row["comparator"]["blob_sha"],
        "solution_module": row["comparator"]["solution_module"],
        "proof_declaration": selected,
        "proof_relation": row["proof_relation"],
        "assumption_binding_sha256": _sha256(binding),
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "PROMOTED_FORMAL_THEOREM_INVOCATION",
        "candidate_only": True,
    }
    receipt = hash72_digest(dictionary, frame)
    replay = hash72_digest(dictionary, frame)
    if receipt != replay:
        raise I081PromotionError("I081_INVOCATION_REPLAY_MISMATCH")
    return {
        "schema": SCHEMA,
        "promoted_constructor_id": promoted_constructor_id,
        "hold_constructor_id": row["hold_constructor_id"],
        "source_title": row["source_title"],
        "source_revision": row["source_revision"],
        "source_tree_sha": row["source_tree_sha"],
        "proof_declaration": selected,
        "solution_module": row["comparator"]["solution_module"],
        "proof_relation": row["proof_relation"],
        "assumption_binding_sha256": frame["assumption_binding_sha256"],
        "candidate_hash72": receipt,
        "replay_hash72": replay,
        "external_formal_proof_bound": True,
        "source_claim_formal_support": True,
        "candidate_only": True,
        "canonical_truth_promotion": False,
        "execution_authority": False,
        "vm81_mutation_invoked": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
        "canonical_persistence_invoked": False,
    }


__all__ = [
    "EXPECTED_PROMOTION_COUNT",
    "I081PromotionError",
    "REGISTRY_PATH",
    "SCHEMA",
    "build_overlay_receipt",
    "get_promotion",
    "invoke_promoted_constructor",
    "list_promotions",
    "load_registry",
    "validate_active_partition",
]
