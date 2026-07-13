"""Pass 044 semantic runtime query facade over conformance, cache, and dependency memory."""
from __future__ import annotations
from typing import Any, Dict, Mapping
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_composition_dependency_index_v1 import build_dependency_index, dependency_query
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache

VERSION = "PASS_044_SEMANTIC_COMPOSITION_CACHE_V1"
QUERY_SCHEMA = "HHS_SEMANTIC_RUNTIME_QUERY_V1"

REJECT_SEMANTIC_DB_AS_AUTHORITY_SOURCE = "REJECT_SEMANTIC_DB_AS_AUTHORITY_SOURCE"


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def query_runtime_semantics(query: str, *, surface_map: Mapping[str, Any] | None = None, cache: SemanticCompositionCache | None = None) -> Dict[str, Any]:
    if surface_map is None:
        from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
        surface_map = build_surface_map()
    cache = cache or SemanticCompositionCache("demo_reports/hhs_semantic_runtime_query_pass044.json")
    dep_index = build_dependency_index(surface_map)
    dep_hits = dependency_query(dep_index, query)
    cache_hits = cache.search(query)
    result = {
        "schema": QUERY_SCHEMA,
        "version": VERSION,
        "query": query,
        "dependency_hits": dep_hits,
        "cache_hits": cache_hits,
        "authority_boundary": "SEMANTIC_QUERY_CAN_FIND_AND_ACCELERATE_BUT_KERNEL_CONFORMANCE_DECISION_AUTHORIZES",
        "may_authorize_runtime": False,
    }
    result["query_root_hash72"] = _hash72(QUERY_SCHEMA, result)
    return result


def semantic_runtime_query_self_test() -> Dict[str, Any]:
    from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
    from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import compose_surface_pipeline
    smap = build_surface_map()
    surf = smap["surfaces"][0]
    cache = SemanticCompositionCache("demo_reports/hhs_semantic_runtime_query_self_test.json")
    plan = compose_surface_pipeline(surf["surface_id"], operation=(surf.get("declared_operations") or [surf.get("symbol")])[0], surface_map=smap)
    entry = cache.store_entry(cache.build_entry(plan, smap))
    q_surface = query_runtime_semantics(str(surf["surface_id"]), surface_map=smap, cache=cache)
    q_inv = query_runtime_semantics(str(surf["invariant_ids"][0]), surface_map=smap, cache=cache)
    return {"schema": "HHS_SEMANTIC_RUNTIME_QUERY_SELF_TEST_V1", "version": VERSION, "ok": q_surface["cache_hits"]["hit_count"] >= 1 and bool(q_inv["dependency_hits"]["hit_families"]) and q_surface["may_authorize_runtime"] is False, "surface_query": q_surface, "invariant_query": q_inv, "entry": entry}

if __name__ == "__main__":
    print(semantic_runtime_query_self_test())
