from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
from hhs_runtime.hhs_incremental_pipeline_rebuilder_v1 import build_incremental_rebuild_plan, rebuild_affected_pipelines
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache


def test_incremental_rebuilder_rebuilds_only_affected_surfaces(tmp_path):
    smap = build_surface_map()
    surface = smap["surfaces"][0]
    plan = build_incremental_rebuild_plan(smap, dependency_family="contract_to_surfaces", dependency_id=surface["contract_schemas"][0])
    assert plan["affected_surface_count"] >= 1
    assert plan["full_recomposition_required"] is False
    result = rebuild_affected_pipelines(smap, plan, cache=SemanticCompositionCache(tmp_path / "cache.json"))
    assert result["ok"]
    assert result["rebuilt_count"] == plan["affected_surface_count"]
