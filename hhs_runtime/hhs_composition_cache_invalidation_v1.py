"""Pass 044 cache invalidation: cached composition may accelerate, never authorize."""
from __future__ import annotations
from typing import Any, Dict, List, Mapping
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_semantic_composition_cache_v1 import validate_cache_entry, REJECT_COMPOSITION_CACHE_STALE

VERSION = "PASS_044_SEMANTIC_COMPOSITION_CACHE_V1"
INVALIDATION_SCHEMA = "HHS_COMPOSITION_INVALIDATION_RECORD_V1"

REJECT_INCREMENTAL_REBUILD_MISSES_DEPENDENCY = "REJECT_INCREMENTAL_REBUILD_MISSES_DEPENDENCY"
REJECT_SEMANTIC_INDEX_DRIFT = "REJECT_SEMANTIC_INDEX_DRIFT"


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def evaluate_cache_invalidation(entry: Mapping[str, Any], *, current_surface_map: Mapping[str, Any], current_tick: int = 0) -> Dict[str, Any]:
    decision = validate_cache_entry(entry, current_surface_map=current_surface_map, current_tick=current_tick)
    invalidated = not decision.get("ok")
    record = {
        "schema": INVALIDATION_SCHEMA,
        "version": VERSION,
        "cache_key_hash72": entry.get("cache_key_hash72"),
        "surface_id": entry.get("surface_id"),
        "invalidated": invalidated,
        "invalidation_reasons": decision.get("reasons", []),
        "decision": decision,
        "cache_authority_rule": "CACHE_HIT_REQUIRES_CURRENT_KERNEL_DEPENDENCY_ROOTS",
    }
    record["invalidation_hash72"] = _hash72(INVALIDATION_SCHEMA, record)
    return record


def invalidate_cache_set(entries: List[Mapping[str, Any]], *, current_surface_map: Mapping[str, Any], current_tick: int = 0) -> Dict[str, Any]:
    records = [evaluate_cache_invalidation(e, current_surface_map=current_surface_map, current_tick=current_tick) for e in entries]
    return {
        "schema": "HHS_COMPOSITION_CACHE_INVALIDATION_SET_V1",
        "version": VERSION,
        "entry_count": len(entries),
        "invalidated_count": len([r for r in records if r.get("invalidated")]),
        "records": records,
        "root_hash72": _hash72("HHS_COMPOSITION_CACHE_INVALIDATION_SET_V1", records),
    }


def composition_cache_invalidation_self_test() -> Dict[str, Any]:
    from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
    from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import compose_surface_pipeline
    from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache
    smap = build_surface_map()
    surf = smap["surfaces"][0]
    plan = compose_surface_pipeline(surf["surface_id"], operation=(surf.get("declared_operations") or [surf.get("symbol")])[0], surface_map=smap)
    cache = SemanticCompositionCache("demo_reports/hhs_composition_cache_invalidation_self_test.json")
    entry = cache.build_entry(plan, smap)
    valid = evaluate_cache_invalidation(entry, current_surface_map=smap, current_tick=1)
    drifted = dict(smap)
    drifted["conformance_root_hash72"] = "drifted-root"
    invalid = evaluate_cache_invalidation(entry, current_surface_map=drifted, current_tick=1)
    return {"schema": "HHS_COMPOSITION_CACHE_INVALIDATION_SELF_TEST_V1", "version": VERSION, "ok": not valid["invalidated"] and invalid["invalidated"] and REJECT_COMPOSITION_CACHE_STALE in invalid["invalidation_reasons"], "valid": valid, "invalid": invalid}

if __name__ == "__main__":
    print(composition_cache_invalidation_self_test())
