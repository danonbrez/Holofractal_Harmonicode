from pathlib import Path

from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import compose_surface_pipeline
from hhs_runtime.hhs_semantic_composition_cache_v1 import (
    SemanticCompositionCache,
    build_composition_cache_key,
    validate_cache_entry,
    REJECT_SEMANTIC_DB_AS_AUTHORITY_SOURCE,
)


def _plan():
    smap = build_surface_map()
    surface = next(s for s in smap["surfaces"] if s["surface_type"] == "SERVICE")
    operation = (surface.get("declared_operations") or [surface.get("symbol")])[0]
    return smap, surface, compose_surface_pipeline(surface["surface_id"], operation=operation, surface_map=smap)


def test_semantic_cache_stores_verbatim_and_searches(tmp_path: Path):
    smap, surface, plan = _plan()
    cache = SemanticCompositionCache(tmp_path / "cache.json")
    entry = cache.store_entry(cache.build_entry(plan, smap, created_at_tick=1, decay_window_ticks=5))
    assert entry["verbatim_semantic_text"]
    assert entry["expanded_payload_persisted"] is False
    assert entry["ml_projection"]["authority"] == "ADVISORY_SEARCH_GEOMETRY_NOT_RUNTIME_AUTHORITY"
    assert cache.search(surface["surface_id"])["hit_count"] == 1
    assert cache.search(surface["invariant_ids"][0])["hit_count"] == 1


def test_cache_key_stable_and_validation_rejects_authority_drift(tmp_path: Path):
    smap, _, plan = _plan()
    cache = SemanticCompositionCache(tmp_path / "cache.json")
    entry = cache.build_entry(plan, smap)
    assert entry["cache_key_hash72"] == build_composition_cache_key(plan, smap)
    assert validate_cache_entry(entry, current_surface_map=smap)["ok"]
    drifted = dict(entry)
    drifted["authority_rule"] = "SEMANTIC_DB_AUTHORIZES_RUNTIME"
    decision = validate_cache_entry(drifted, current_surface_map=smap)
    assert not decision["ok"]
    assert REJECT_SEMANTIC_DB_AS_AUTHORITY_SOURCE in decision["reasons"]


def test_receipt_vector_index_nearest_is_available(tmp_path: Path):
    smap, _, plan = _plan()
    cache = SemanticCompositionCache(tmp_path / "cache.json")
    entry = cache.store_entry(cache.build_entry(plan, smap))
    nearest = cache.nearest(entry)
    assert nearest["advisory_only"] is True
    assert nearest["vector_index_stats"]["node_count"] >= 1
