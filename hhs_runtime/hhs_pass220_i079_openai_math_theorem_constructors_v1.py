"""Pass 220 I079 source-bound formal theorem constructors.

Each constructor is a deterministic HHS callable wrapper around a pinned
external Lean proof surface.  The wrapper preserves source/proof identity and
produces candidate-only Hash72 receipts; it does not claim to re-prove the
external theorem or to mint canonical VM81/Hash72/Hash216 state.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

SCHEMA = "HHS_PASS_220_I079_OPENAI_MATH_THEOREM_CONSTRUCTORS_V1"
EXPECTED_SOURCE_REVISION = "adc7f1241b42e322a6451854ab7e4b4c146bf78a"
EXPECTED_BASE_MAIN = "5823c2676452d0594fe1144f568d318e6b5da9a3"
EXPECTED_CONSTRUCTOR_COUNT = 54
EXPECTED_PROOF_SURFACE_COUNT = 57
ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/pass220/openai_math_formalized_novelty_constructors_v1.json"


class I079ConstructorError(RuntimeError):
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
        raise I079ConstructorError("I079_SCHEMA_MISMATCH")
    if data.get("source_revision") != EXPECTED_SOURCE_REVISION:
        raise I079ConstructorError("I079_SOURCE_REVISION_MISMATCH")
    if data.get("base_main") != EXPECTED_BASE_MAIN:
        raise I079ConstructorError("I079_BASE_MAIN_MISMATCH")

    rows = data.get("constructors")
    if not isinstance(rows, list) or len(rows) != EXPECTED_CONSTRUCTOR_COUNT:
        raise I079ConstructorError("I079_CONSTRUCTOR_COUNT_MISMATCH")
    ids = [row.get("constructor_id") for row in rows]
    if len(set(ids)) != len(ids):
        raise I079ConstructorError("I079_DUPLICATE_CONSTRUCTOR_ID")
    if ids != sorted(ids):
        raise I079ConstructorError("I079_CONSTRUCTOR_ORDER_NOT_CANONICAL")

    proof_count = 0
    for row in rows:
        if row.get("constructor_kind") != "HHS_SOURCE_BOUND_FORMAL_THEOREM_CONSTRUCTOR_V1":
            raise I079ConstructorError("I079_CONSTRUCTOR_KIND_MISMATCH")
        if row.get("status") != "NEW_IMPLEMENTED_I079":
            raise I079ConstructorError("I079_CONSTRUCTOR_STATUS_MISMATCH")
        if row.get("source_revision") != EXPECTED_SOURCE_REVISION:
            raise I079ConstructorError("I079_CONSTRUCTOR_SOURCE_MISMATCH")
        if row.get("pre_i078_dedicated_constructor_found") is not False:
            raise I079ConstructorError("I079_PREEXISTING_CONSTRUCTOR_AUDIT_DRIFT")
        proof_surfaces = row.get("proof_surfaces")
        if not isinstance(proof_surfaces, list) or not proof_surfaces:
            raise I079ConstructorError("I079_PROOF_SURFACE_MISSING")
        proof_count += len(proof_surfaces)
        if row.get("proof_surface_count") != len(proof_surfaces):
            raise I079ConstructorError("I079_PROOF_SURFACE_COUNT_DRIFT")
        for proof in proof_surfaces:
            if not proof.get("declaration") or not proof.get("file"):
                raise I079ConstructorError("I079_PROOF_SURFACE_INVALID")
        ingress = row.get("ingress_contract", {})
        egress = row.get("egress_contract", {})
        if ingress.get("preserve_external_types") is not True:
            raise I079ConstructorError("I079_INGRESS_TYPE_FIDELITY_DRIFT")
        if egress.get("truth_promotion") is not False:
            raise I079ConstructorError("I079_EGRESS_TRUTH_AUTHORITY_DRIFT")
        authority = row.get("authority", {})
        if authority.get("candidate_only") is not True:
            raise I079ConstructorError("I079_CONSTRUCTOR_NOT_CANDIDATE_ONLY")
        for key, value in authority.items():
            if key != "candidate_only" and value is not False:
                raise I079ConstructorError(f"I079_AUTHORITY_DRIFT:{key}")

    if proof_count != EXPECTED_PROOF_SURFACE_COUNT:
        raise I079ConstructorError("I079_TOTAL_PROOF_SURFACE_COUNT_MISMATCH")
    authority = data.get("authority", {})
    if authority.get("candidate_only") is not True:
        raise I079ConstructorError("I079_REGISTRY_NOT_CANDIDATE_ONLY")
    for key, value in authority.items():
        if key != "candidate_only" and value is not False:
            raise I079ConstructorError(f"I079_REGISTRY_AUTHORITY_DRIFT:{key}")
    return data


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
    raise I079ConstructorError("I079_UNKNOWN_CONSTRUCTOR")


def build_registry_receipt(
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    payload = {
        "source_revision": registry["source_revision"],
        "base_main": registry["base_main"],
        "constructors": registry["constructors"],
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "FORMAL_THEOREM_CONSTRUCTOR_REGISTRY",
        "candidate_only": True,
    }
    first = hash72_digest(dictionary, payload)
    replay = hash72_digest(dictionary, payload)
    if first != replay:
        raise I079ConstructorError("I079_REGISTRY_REPLAY_MISMATCH")
    return {
        "registry_sha256": _sha256(payload),
        "candidate_hash72": first,
        "replay_hash72": replay,
        "constructor_count": len(registry["constructors"]),
        "proof_surface_count": sum(
            row["proof_surface_count"] for row in registry["constructors"]
        ),
        "candidate_only": True,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
    }


def invoke_constructor(
    constructor_id: str,
    assumption_binding: Mapping[str, Any] | None = None,
    proof_declaration: str | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    row = get_constructor(constructor_id, registry)
    surfaces = row["proof_surfaces"]
    declarations = [surface["declaration"] for surface in surfaces]
    selected = proof_declaration or declarations[0]
    if selected not in declarations:
        raise I079ConstructorError("I079_PROOF_DECLARATION_NOT_ADMITTED")
    proof = next(surface for surface in surfaces if surface["declaration"] == selected)

    binding = dict(assumption_binding or {})
    binding_sha256 = _sha256(binding)
    constructor_sha256 = _sha256(row)
    frame = {
        "constructor_id": constructor_id,
        "source_revision": EXPECTED_SOURCE_REVISION,
        "source_tree_sha": row["source_tree_sha"],
        "family_id": row["family_id"],
        "proof_declaration": selected,
        "proof_file": proof["file"],
        "constructor_sha256": constructor_sha256,
        "assumption_binding_sha256": binding_sha256,
        "ingress_type": row["ingress_contract"]["type"],
        "egress_type": row["egress_contract"]["type"],
    }
    dictionary = {
        "domain": SCHEMA,
        "role": "SOURCE_BOUND_THEOREM_INVOCATION",
        "candidate_only": True,
    }
    receipt = hash72_digest(dictionary, frame)
    replay = hash72_digest(dictionary, frame)
    if receipt != replay:
        raise I079ConstructorError("I079_INVOCATION_REPLAY_MISMATCH")
    return {
        "schema": SCHEMA,
        "constructor_id": constructor_id,
        "family_id": row["family_id"],
        "source_title": row["source_title"],
        "source_revision": EXPECTED_SOURCE_REVISION,
        "proof_declaration": selected,
        "proof_file": proof["file"],
        "assumption_binding_sha256": binding_sha256,
        "constructor_sha256": constructor_sha256,
        "candidate_hash72": receipt,
        "replay_hash72": replay,
        "proof_surface_bound": True,
        "external_proof_rechecked_at_runtime": False,
        "truth_promotion": False,
        "candidate_only": True,
        "vm81_mutation_invoked": False,
        "canonical_hash72_minted": False,
        "canonical_hash216_minted": False,
        "canonical_persistence_invoked": False,
    }


__all__ = [
    "EXPECTED_CONSTRUCTOR_COUNT",
    "EXPECTED_PROOF_SURFACE_COUNT",
    "EXPECTED_SOURCE_REVISION",
    "I079ConstructorError",
    "REGISTRY_PATH",
    "SCHEMA",
    "build_registry_receipt",
    "get_constructor",
    "invoke_constructor",
    "list_constructors",
    "load_registry",
]
