"""Pass 220 I080 source-bound HOLD claim constructors.

I080 covers the I078 novelty manuscripts that do not have a catalogued
main-result proof surface in the pinned OpenAI formalization catalogue.

These constructors are callable provenance/interface objects.  They do not emit
theorem witnesses and do not promote manuscript claims to canonical truth.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

SCHEMA = "HHS_PASS_220_I080_OPENAI_MATH_HOLD_CLAIM_CONSTRUCTORS_V1"
EXPECTED_SOURCE_REVISION = "adc7f1241b42e322a6451854ab7e4b4c146bf78a"
EXPECTED_BASE_CHECKPOINT = "be8d847f5bb107456844d38acec3bd0d053166b6"
EXPECTED_HOLD_COUNT = 268
EXPECTED_I079_THEOREM_COUNT = 54
EXPECTED_NOVELTY_COUNT = 322

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/pass220/openai_math_hold_claim_constructors_v1.json"
I078_PATH = ROOT / "data/pass220/openai_math_corpus_hydration_20261006_v1.json"
I079_PATH = ROOT / "data/pass220/openai_math_formalized_novelty_constructors_v1.json"


class I080ConstructorError(RuntimeError):
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
        raise I080ConstructorError("I080_SCHEMA_MISMATCH")
    if data.get("source_revision") != EXPECTED_SOURCE_REVISION:
        raise I080ConstructorError("I080_SOURCE_REVISION_MISMATCH")
    if data.get("base_checkpoint") != EXPECTED_BASE_CHECKPOINT:
        raise I080ConstructorError("I080_BASE_CHECKPOINT_MISMATCH")

    rows = data.get("constructors")
    if not isinstance(rows, list) or len(rows) != EXPECTED_HOLD_COUNT:
        raise I080ConstructorError("I080_CONSTRUCTOR_COUNT_MISMATCH")
    ids = [row.get("constructor_id") for row in rows]
    slugs = [row.get("source_slug") for row in rows]
    if len(set(ids)) != len(ids):
        raise I080ConstructorError("I080_DUPLICATE_CONSTRUCTOR_ID")
    if len(set(slugs)) != len(slugs):
        raise I080ConstructorError("I080_DUPLICATE_SOURCE_SLUG")
    if ids != sorted(ids):
        raise I080ConstructorError("I080_CONSTRUCTOR_ORDER_NOT_CANONICAL")

    for row in rows:
        if row.get("constructor_kind") != "HHS_SOURCE_BOUND_UNVERIFIED_CLAIM_CONSTRUCTOR_V1":
            raise I080ConstructorError("I080_CONSTRUCTOR_KIND_MISMATCH")
        if row.get("status") != "HOLD_NO_CATALOGUED_MAIN_RESULT_PROOF":
            raise I080ConstructorError("I080_HOLD_STATUS_MISMATCH")
        if row.get("source_revision") != EXPECTED_SOURCE_REVISION:
            raise I080ConstructorError("I080_CONSTRUCTOR_SOURCE_REVISION_MISMATCH")
        if not _is_hex40(row.get("source_tree_sha")):
            raise I080ConstructorError("I080_SOURCE_TREE_SHA_INVALID")
        expected_id = (
            "HHS-OAI-HOLD-F"
            + row["family_id"]
            + "-"
            + row["source_tree_sha"][:12].upper()
        )
        if row.get("constructor_id") != expected_id:
            raise I080ConstructorError("I080_CONSTRUCTOR_ID_SOURCE_MISMATCH")
        if row.get("formalized_source_catalogued") is not False:
            raise I080ConstructorError("I080_FORMALIZATION_STATUS_DRIFT")
        if row.get("proof_surface_count") != 0:
            raise I080ConstructorError("I080_PROOF_SURFACE_UNEXPECTED")
        if row.get("proof_catalog_status") != "NO_CATALOGUED_MAIN_RESULT_PROOF_SURFACE":
            raise I080ConstructorError("I080_PROOF_CATALOG_STATUS_DRIFT")
        egress = row.get("egress_contract", {})
        if egress.get("theorem_witness") is not False:
            raise I080ConstructorError("I080_THEOREM_WITNESS_AUTHORITY_DRIFT")
        if egress.get("truth_promotion") is not False:
            raise I080ConstructorError("I080_TRUTH_PROMOTION_DRIFT")
        policy = row.get("upgrade_policy", {})
        if policy.get("current_state") != "HOLD":
            raise I080ConstructorError("I080_UPGRADE_STATE_DRIFT")
        if not policy.get("accepted_upgrade_paths"):
            raise I080ConstructorError("I080_UPGRADE_PATH_MISSING")
        authority = row.get("authority", {})
        if authority.get("candidate_only") is not True:
            raise I080ConstructorError("I080_CONSTRUCTOR_NOT_CANDIDATE_ONLY")
        for key, value in authority.items():
            if key != "candidate_only" and value is not False:
                raise I080ConstructorError(f"I080_AUTHORITY_DRIFT:{key}")

    authority = data.get("authority", {})
    if authority.get("candidate_only") is not True:
        raise I080ConstructorError("I080_REGISTRY_NOT_CANDIDATE_ONLY")
    for key, value in authority.items():
        if key != "candidate_only" and value is not False:
            raise I080ConstructorError(f"I080_REGISTRY_AUTHORITY_DRIFT:{key}")
    return data


def validate_frontier_coverage(
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    i078 = json.loads(I078_PATH.read_text(encoding="utf-8"))
    i079 = json.loads(I079_PATH.read_text(encoding="utf-8"))

    novelty = {
        row["slug"]
        for row in i078["manuscripts"]
        if row.get("classification") == "NOVELTY_CANDIDATE"
    }
    theorem = {row["source_slug"] for row in i079["constructors"]}
    hold = {row["source_slug"] for row in registry["constructors"]}

    if len(novelty) != EXPECTED_NOVELTY_COUNT:
        raise I080ConstructorError("I080_PARENT_NOVELTY_COUNT_DRIFT")
    if len(theorem) != EXPECTED_I079_THEOREM_COUNT:
        raise I080ConstructorError("I080_PARENT_THEOREM_COUNT_DRIFT")
    if len(hold) != EXPECTED_HOLD_COUNT:
        raise I080ConstructorError("I080_HOLD_COUNT_DRIFT")
    if theorem & hold:
        raise I080ConstructorError("I080_THEOREM_HOLD_OVERLAP")
    if theorem | hold != novelty:
        missing = sorted(novelty - (theorem | hold))
        extra = sorted((theorem | hold) - novelty)
        raise I080ConstructorError(
            "I080_FRONTIER_COVERAGE_MISMATCH:"
            + _sha256({"missing": missing, "extra": extra})
        )
    return {
        "novelty_count": len(novelty),
        "theorem_constructor_count": len(theorem),
        "hold_constructor_count": len(hold),
        "coverage_gap": 0,
        "duplicate_assignment_count": 0,
        "complete": True,
    }


def list_constructors(registry: dict[str, Any] | None = None) -> tuple[str, ...]:
    registry = load_registry() if registry is None else registry
    return tuple(row["constructor_id"] for row in registry["constructors"])


def get_constructor(
    constructor_id: str,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    for row in registry["constructors"]:
        if row["constructor_id"] == constructor_id:
            return row
    raise I080ConstructorError("I080_UNKNOWN_CONSTRUCTOR")


def build_registry_receipt(
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    coverage = validate_frontier_coverage(registry)
    payload = {
        "source_revision": registry["source_revision"],
        "base_checkpoint": registry["base_checkpoint"],
        "constructors": registry["constructors"],
        "coverage": coverage,
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "HOLD_CLAIM_CONSTRUCTOR_REGISTRY",
        "candidate_only": True,
    }
    first = hash72_digest(dictionary, payload)
    replay = hash72_digest(dictionary, payload)
    if first != replay:
        raise I080ConstructorError("I080_REGISTRY_REPLAY_MISMATCH")
    return {
        "registry_sha256": _sha256(payload),
        "candidate_hash72": first,
        "replay_hash72": replay,
        "hold_constructor_count": EXPECTED_HOLD_COUNT,
        "frontier_coverage": coverage,
        "candidate_only": True,
        "theorem_truth_authority": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
    }


def invoke_claim_constructor(
    constructor_id: str,
    claim_binding: Mapping[str, Any] | None = None,
    *,
    require_theorem_witness: bool = False,
    proof_declaration: str | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    row = get_constructor(constructor_id, registry)
    if require_theorem_witness:
        raise I080ConstructorError("I080_THEOREM_WITNESS_NOT_AVAILABLE")
    if proof_declaration is not None:
        raise I080ConstructorError("I080_PROOF_DECLARATION_NOT_AVAILABLE")

    binding = dict(claim_binding or {})
    frame = {
        "constructor_id": constructor_id,
        "family_id": row["family_id"],
        "source_title": row["source_title"],
        "source_slug": row["source_slug"],
        "source_tree_sha": row["source_tree_sha"],
        "source_revision": EXPECTED_SOURCE_REVISION,
        "claim_binding_sha256": _sha256(binding),
        "status": row["status"],
        "proof_catalog_status": row["proof_catalog_status"],
        "egress_type": row["egress_contract"]["type"],
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "SOURCE_BOUND_HOLD_CLAIM_INVOCATION",
        "candidate_only": True,
    }
    receipt = hash72_digest(dictionary, frame)
    replay = hash72_digest(dictionary, frame)
    if receipt != replay:
        raise I080ConstructorError("I080_INVOCATION_REPLAY_MISMATCH")
    return {
        "schema": SCHEMA,
        "constructor_id": constructor_id,
        "family_id": row["family_id"],
        "source_title": row["source_title"],
        "source_revision": EXPECTED_SOURCE_REVISION,
        "source_tree_sha": row["source_tree_sha"],
        "claim_binding_sha256": frame["claim_binding_sha256"],
        "candidate_hash72": receipt,
        "replay_hash72": replay,
        "status": "HOLD",
        "proof_surface_bound": False,
        "theorem_witness": False,
        "truth_promotion": False,
        "candidate_only": True,
        "execution_authority": False,
        "vm81_mutation_invoked": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
        "canonical_persistence_invoked": False,
    }


__all__ = [
    "EXPECTED_HOLD_COUNT",
    "EXPECTED_NOVELTY_COUNT",
    "EXPECTED_SOURCE_REVISION",
    "I080ConstructorError",
    "REGISTRY_PATH",
    "SCHEMA",
    "build_registry_receipt",
    "get_constructor",
    "invoke_claim_constructor",
    "list_constructors",
    "load_registry",
    "validate_frontier_coverage",
]
