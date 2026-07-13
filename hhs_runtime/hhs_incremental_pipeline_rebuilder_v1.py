"""Pass 044 incremental rebuild planner for kernel-derived runtime pipelines."""
from __future__ import annotations
from typing import Any, Dict, List, Mapping
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_composition_dependency_index_v1 import affected_surfaces, build_dependency_index
from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import compose_surface_pipeline
from hhs_runtime.hhs_semantic_composition_cache_v1 import SemanticCompositionCache

VERSION = "PASS_044_SEMANTIC_COMPOSITION_CACHE_V1"
REBUILD_SCHEMA = "HHS_INCREMENTAL_PIPELINE_REBUILD_PLAN_V1"

REJECT_INCREMENTAL_REBUILD_MISSES_DEPENDENCY = "REJECT_INCREMENTAL_REBUILD_MISSES_DEPENDENCY"


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def build_incremental_rebuild_plan(surface_map: Mapping[str, Any], *, dependency_family: str, dependency_id: str) -> Dict[str, Any]:
    index = build_dependency_index(surface_map)
    affected = affected_surfaces(index, dependency_family=dependency_family, dependency_id=dependency_id)
    plan = {
        "schema": REBUILD_SCHEMA,
        "version": VERSION,
        "dependency_family": dependency_family,
        "dependency_id": dependency_id,
        "conformance_graph_root": surface_map.get("conformance_root_hash72"),
        "affected_surface_count": len(affected),
        "affected_surfaces": affected,
        "rebuild_scope": "AFFECTED_SURFACES_ONLY" if affected else "NO_REBUILD_REQUIRED",
        "full_recomposition_required": False,
    }
    plan["rebuild_plan_hash72"] = _hash72(REBUILD_SCHEMA, plan)
    return plan


def rebuild_affected_pipelines(surface_map: Mapping[str, Any], rebuild_plan: Mapping[str, Any], *, cache: SemanticCompositionCache | None = None) -> Dict[str, Any]:
    cache = cache or SemanticCompositionCache("demo_reports/hhs_incremental_rebuild_cache_pass044.json")
    by_id = {s["surface_id"]: s for s in surface_map.get("surfaces", [])}
    rebuilt: List[Dict[str, Any]] = []
    missed: List[str] = []
    for sid in rebuild_plan.get("affected_surfaces", []) or []:
        surface = by_id.get(sid)
        if not surface:
            missed.append(str(sid))
            continue
        operation = (surface.get("declared_operations") or [surface.get("symbol") or "self_test"])[0]
        plan = compose_surface_pipeline(sid, operation=operation, surface_map=surface_map)
        entry = cache.build_entry(plan, surface_map)
        cache.store_entry(entry)
        rebuilt.append({"surface_id": sid, "operation": operation, "cache_key_hash72": entry.get("cache_key_hash72"), "composition_root_hash72": entry.get("composition_root_hash72")})
    status = "ADMIT_INCREMENTAL_REBUILD" if not missed else "REJECT_INCREMENTAL_REBUILD"
    result = {"schema": "HHS_INCREMENTAL_PIPELINE_REBUILD_RESULT_V1", "version": VERSION, "status": status, "ok": not missed, "rebuilt_count": len(rebuilt), "missed_surfaces": missed, "rebuilt": rebuilt}
    result["rebuild_result_hash72"] = _hash72("HHS_INCREMENTAL_PIPELINE_REBUILD_RESULT_V1", result)
    return result


def incremental_pipeline_rebuilder_self_test() -> Dict[str, Any]:
    from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
    smap = build_surface_map()
    surface = smap["surfaces"][0]
    contract = surface["contract_schemas"][0]
    plan = build_incremental_rebuild_plan(smap, dependency_family="contract_to_surfaces", dependency_id=contract)
    result = rebuild_affected_pipelines(smap, plan, cache=SemanticCompositionCache("demo_reports/hhs_incremental_rebuilder_self_test.json"))
    return {"schema": "HHS_INCREMENTAL_PIPELINE_REBUILDER_SELF_TEST_V1", "version": VERSION, "ok": plan["affected_surface_count"] >= 1 and result["ok"] and result["rebuilt_count"] == plan["affected_surface_count"], "plan": plan, "result": result}

if __name__ == "__main__":
    print(incremental_pipeline_rebuilder_self_test())
