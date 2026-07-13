from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import compose_surface_pipeline
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache
from hhs_runtime.hhs_semantic_runtime_query_v1 import query_runtime_semantics


def test_semantic_runtime_query_uses_cache_and_dependency_index_without_authority(tmp_path):
    smap = build_surface_map()
    surface = smap["surfaces"][0]
    cache = SemanticCompositionCache(tmp_path / "cache.json")
    plan = compose_surface_pipeline(surface["surface_id"], operation=surface["declared_operations"][0], surface_map=smap)
    cache.store_entry(cache.build_entry(plan, smap))
    result = query_runtime_semantics(surface["invariant_ids"][0], surface_map=smap, cache=cache)
    assert result["dependency_hits"]["hit_families"]
    assert result["cache_hits"]["hit_count"] >= 1
    assert result["may_authorize_runtime"] is False
