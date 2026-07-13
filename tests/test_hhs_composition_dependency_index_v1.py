from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
from hhs_runtime.hhs_composition_dependency_index_v1 import build_dependency_index, affected_surfaces, dependency_query


def test_dependency_index_maps_invariants_contracts_validators():
    smap = build_surface_map()
    index = build_dependency_index(smap)
    surface = smap["surfaces"][0]
    sid = surface["surface_id"]
    assert sid in affected_surfaces(index, dependency_family="invariant_to_surfaces", dependency_id=surface["invariant_ids"][0])
    assert sid in affected_surfaces(index, dependency_family="contract_to_surfaces", dependency_id=surface["contract_schemas"][0])
    assert dependency_query(index, surface["invariant_ids"][0])["hit_families"]
    assert index["semantic_index_authority"].startswith("DEPENDENCY_LOOKUP_ONLY")
