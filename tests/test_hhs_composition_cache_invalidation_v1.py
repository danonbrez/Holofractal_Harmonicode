from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import compose_surface_pipeline
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache
from hhs_runtime.hhs_composition_cache_invalidation_v1 import evaluate_cache_invalidation


def test_cache_invalidation_rejects_changed_conformance_root(tmp_path):
    smap = build_surface_map()
    surface = smap["surfaces"][0]
    plan = compose_surface_pipeline(surface["surface_id"], operation=surface["declared_operations"][0], surface_map=smap)
    entry = SemanticCompositionCache(tmp_path / "cache.json").build_entry(plan, smap)
    assert evaluate_cache_invalidation(entry, current_surface_map=smap)["invalidated"] is False
    drifted = dict(smap)
    drifted["conformance_root_hash72"] = "changed-root"
    invalid = evaluate_cache_invalidation(entry, current_surface_map=drifted)
    assert invalid["invalidated"] is True
    assert "REJECT_COMPOSITION_CACHE_STALE" in invalid["invalidation_reasons"]
