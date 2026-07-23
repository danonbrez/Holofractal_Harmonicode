from pathlib import Path
from copy import deepcopy
import pytest
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_vm81_native_exposure.hhs_pass078_vm81_native_exposure_v1 import *
ROOT=Path(__file__).resolve().parents[1]

def test_kernel_freeze_round_trip():
    m=kernel_freeze_manifest(ROOT); assert verify_kernel_freeze(ROOT,m); assert len(m["files"])==4

def test_native_census_is_nonempty_and_catalogues_internal_functions():
    m=native_capability_manifest(ROOT); assert m["native_function_count"]>=20
    assert any(x["symbol"]=="hhs_manifold_step" and x["native_visibility"]=="INTERNAL_STATIC" for x in m["functions"])

def test_exposure_registry_is_complete_and_does_not_reimplement():
    m=native_capability_manifest(ROOT); r=native_exposure_registry(m)
    assert r["entry_count"]==m["native_function_count"] and r["complete_catalogue"]
    assert all(not x["native_semantics_reimplemented"] for x in r["entries"])

def test_internal_functions_are_descriptors_not_falsely_direct_callable():
    r=native_exposure_registry(native_capability_manifest(ROOT))
    x=next(x for x in r["entries"] if x["native_symbol"]=="hhs_manifold_step")
    assert x["binding_mode"]=="WITNESSED_CAPABILITY_DESCRIPTOR" and not x["callable_from_higher_level"]

def test_vm81_lane_binding_covers_all_cells_once():
    m=vm81_lane_binding_manifest(); flat=[c for b in m["bindings"] for c in b["cell_indices"]]
    assert sorted(flat)==list(range(81)); assert len(flat)==len(set(flat)); assert not m["unbound_lanes"]

def test_duplicate_lanes_rejected():
    with pytest.raises(ContractError): vm81_lane_binding_manifest(("x","x"))

def test_overlap_relations_are_complete_and_reciprocal():
    m=vm81_overlap_relation_map(); assert m["cell_count"]==81
    assert all(m["cells"][m["cells"][i]["reciprocal_cell"]]["reciprocal_cell"]==i for i in range(81))

def test_plastic_recurrence_is_exact_characteristic_sequence():
    s=plastic_recurrence(20); assert all(s[n]==s[n-2]+s[n-3] for n in range(3,len(s)))

def test_geometry_is_external_exact_and_source_bound():
    g=plastic_e6_geometry("vm-root"); assert not g["kernel_mutation"] and g["removable_without_kernel_semantic_change"]
    assert g["numeric_model"]=="EXACT_INTEGER_RATIONAL_NO_FLOATS" and len(g["nodes"])==81

def test_geometry_requires_source_provenance():
    with pytest.raises(ContractError): plastic_e6_geometry("")

def test_wave_output_is_candidate_not_authority():
    w=wave_candidate(geometry=plastic_e6_geometry("vm"),source_cell=40,amplitude=2,phase_delta=7)
    assert not w["canonical_admission"] and w["candidate_count"]>0
    assert all(x["status"]=="CANDIDATE_REQUIRES_NATIVE_VM81_ADMISSION" for x in w["candidates"])

def test_release_is_deterministic(): assert build_release(ROOT)==build_release(ROOT)
