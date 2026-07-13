"""
HHS Conformance Decision Cache v1
=================================

Pass 043 deterministic cache for kernel-conformance decisions. A stable surface
and graph root produce a stable cache key, so repeated validation can reuse the
compact decision residue rather than re-persist expanded graph fragments.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_kernel_conformance_decision_v1 import evaluate_surface

VERSION = "PASS_043_KERNEL_DERIVED_RUNTIME_AUTOCOMPOSITION_V1"
CACHE_SCHEMA = "HHS_VALIDATION_CACHE_ENTRY_V1"
REJECT_VALIDATION_CACHE_DRIFT = "REJECT_VALIDATION_CACHE_DRIFT"


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def build_cache_key(surface: Mapping[str, Any], *, conformance_root_hash72: str) -> str:
    return _hash72("HHS_CONFORMANCE_DECISION_CACHE_KEY_V1", {
        "surface_id": surface.get("surface_id"),
        "surface_type": surface.get("surface_type"),
        "invariant_ids": sorted(surface.get("invariant_ids", []) or []),
        "contract_schemas": sorted(surface.get("contract_schemas", []) or []),
        "conformance_root_hash72": conformance_root_hash72,
    })


def make_cache_entry(surface: Mapping[str, Any], decision: Mapping[str, Any], *, conformance_root_hash72: str) -> Dict[str, Any]:
    key = build_cache_key(surface, conformance_root_hash72=conformance_root_hash72)
    entry = {
        "schema": CACHE_SCHEMA,
        "version": VERSION,
        "cache_key_hash72": key,
        "surface_id": surface.get("surface_id"),
        "surface_type": surface.get("surface_type"),
        "conformance_root_hash72": conformance_root_hash72,
        "decision_status": decision.get("status"),
        "derivation_complete": bool(decision.get("derivation_complete")),
        "decision_root_hash72": _hash72("HHS_SURFACE_CONFORMANCE_DECISION_CACHE_ROOT_V1", decision),
        "cached_fields": ["status", "derivation_complete", "surface_id", "invariant_ids", "decision_root_hash72"],
    }
    entry["cache_entry_hash72"] = _hash72(CACHE_SCHEMA, entry)
    return entry


def validate_cache_entry(entry: Mapping[str, Any], surface: Mapping[str, Any], *, conformance_root_hash72: str) -> Dict[str, Any]:
    expected_key = build_cache_key(surface, conformance_root_hash72=conformance_root_hash72)
    reasons = []
    if expected_key != entry.get("cache_key_hash72"):
        reasons.append(REJECT_VALIDATION_CACHE_DRIFT)
    if conformance_root_hash72 != entry.get("conformance_root_hash72"):
        reasons.append(REJECT_VALIDATION_CACHE_DRIFT)
    return {
        "schema": "HHS_VALIDATION_CACHE_DECISION_V1",
        "version": VERSION,
        "ok": not reasons,
        "status": "ADMIT_VALIDATION_CACHE_ENTRY" if not reasons else "REJECT_VALIDATION_CACHE_ENTRY",
        "reasons": reasons,
        "cache_key_hash72": entry.get("cache_key_hash72"),
    }


def get_or_build_decision(surface: Mapping[str, Any], *, conformance_root_hash72: str, cache: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    key = build_cache_key(surface, conformance_root_hash72=conformance_root_hash72)
    if key in cache:
        return {"schema": "HHS_VALIDATION_CACHE_LOOKUP_V1", "cache_hit": True, "entry": cache[key]}
    decision = evaluate_surface(surface)
    entry = make_cache_entry(surface, decision, conformance_root_hash72=conformance_root_hash72)
    cache[key] = entry
    return {"schema": "HHS_VALIDATION_CACHE_LOOKUP_V1", "cache_hit": False, "entry": entry, "decision": decision}


def conformance_decision_cache_self_test() -> Dict[str, Any]:
    surface = {
        "surface_id": "service:kernel_runtime_autocomposer.self_test",
        "surface_type": "SERVICE",
        "invariant_ids": ["HHS-I005", "HHS-I011", "HHS-I014", "HHS-I015"],
        "contract_schemas": ["HHS_KERNEL_RUNTIME_COMPOSITION_PLAN_V1"],
        "witness_schemas": ["HHS_KERNEL_DERIVATION_WITNESS_V1"],
        "validators": ["validate_kernel_runtime_composition_plan"],
        "rejection_codes": ["REJECT_COMPOSITION_PLAN_NOT_KERNEL_DERIVED"],
        "mutation_policy": "NO_EXTERNAL_STATE_MUTATION",
    }
    cache: Dict[str, Dict[str, Any]] = {}
    first = get_or_build_decision(surface, conformance_root_hash72="root:test", cache=cache)
    second = get_or_build_decision(surface, conformance_root_hash72="root:test", cache=cache)
    validation = validate_cache_entry(second["entry"], surface, conformance_root_hash72="root:test")
    return {
        "schema": "HHS_CONFORMANCE_DECISION_CACHE_SELF_TEST_V1",
        "version": VERSION,
        "ok": not first.get("cache_hit") and second.get("cache_hit") and validation.get("ok"),
        "first_lookup": first,
        "second_lookup": second,
        "validation": validation,
    }


if __name__ == "__main__":
    print(conformance_decision_cache_self_test())
