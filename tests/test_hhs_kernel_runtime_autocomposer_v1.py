from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import (
    compose_surface_pipeline,
    derive_runtime_pipeline,
    execute_composed_preflight,
    kernel_runtime_autocomposer_self_test,
)
from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map


def test_autocomposer_self_test_passes():
    result = kernel_runtime_autocomposer_self_test()
    assert result["ok"] is True


def test_surface_pipeline_is_kernel_derived():
    surface_map = build_surface_map()
    surface = next(s for s in surface_map["surfaces"] if s["surface_id"] == "service:kernel_conformance_surface_map.self_test")
    op = surface["declared_operations"][0]
    plan = compose_surface_pipeline(surface["surface_id"], operation=op, surface_map=surface_map)
    assert plan["composition_allowed"] is True
    assert plan["pipeline"]["handwired"] is False
    assert plan["decision"]["ok"] is True


def test_underived_pipeline_rejected():
    pipeline = derive_runtime_pipeline({"surface_id": "service:underived", "surface_type": "SERVICE"}, operation="run")
    assert pipeline["composition_allowed"] is False
    assert pipeline["status"] == "REJECT_COMPOSITION_PLAN_NOT_KERNEL_DERIVED"


def test_preflight_persists_compact_residue_only():
    surface_map = build_surface_map()
    surface = next(s for s in surface_map["surfaces"] if s["surface_type"] == "SERVICE")
    op = surface["declared_operations"][0]
    out = execute_composed_preflight(surface["surface_id"], operation=op, surface_map=surface_map, cache={})
    assert out["ok"] is True
    assert out["expanded_metadata_persisted"] is False
    assert out["compact_residue"]["expanded_payload_retained"] is False
