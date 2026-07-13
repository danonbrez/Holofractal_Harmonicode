from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import (
    build_surface_map,
    find_underived_surfaces,
    find_orphaned_invariants,
    build_surface_map_witness,
)


def test_surface_map_has_no_active_underived_surfaces():
    surface_map = build_surface_map()
    assert surface_map["validation"]["ok"] is True
    assert surface_map["invariant_count"] >= 16
    assert surface_map["surface_count"] >= 52
    assert find_underived_surfaces(surface_map) == []


def test_surface_graph_root_is_deterministic_under_stable_inputs():
    a = build_surface_map()["conformance_root_hash72"]
    b = build_surface_map()["conformance_root_hash72"]
    assert a == b


def test_every_invariant_is_used_by_at_least_one_surface():
    surface_map = build_surface_map()
    assert find_orphaned_invariants(surface_map) == []


def test_surface_map_witness_has_hash72_authority():
    surface_map = build_surface_map()
    witness = build_surface_map_witness(surface_map)
    assert witness["conformance_root_hash72"]
    assert witness["hash72_kernel_witness"]["zero_sum"] is True
