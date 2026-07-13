from hhs_backend.runtime.hhs_three_lane_81_cell_qudit_kernel_v1 import run_three_lane_81_cell_kernel, three_lane_81_cell_kernel_self_test

def test_self_test():
    assert three_lane_81_cell_kernel_self_test()["ok"]

def test_81_cells_and_243_lane_projections():
    r=run_three_lane_81_cell_kernel()
    assert r["cell_count"]==81
    assert r["lane_projection_count"]==243
    assert r["subgrid_count"]==9

def test_every_cell_executes_three_lanes_in_order():
    r=run_three_lane_81_cell_kernel()
    assert all(c["transition"]["execution_order"]==["POSITIVE","PLASTIC","ZERO_SUM"] for c in r["cells"])

def test_plastic_and_zero_sum_gates_dynamically_close_displaced_proposals():
    r=run_three_lane_81_cell_kernel()
    assert all(c["transition"]["plastic_lane"]["continuation_admitted"] for c in r["cells"])
    assert all(c["transition"]["zero_sum_lane"]["continuation_admitted"] for c in r["cells"])
    assert any(c["transition"]["plastic_lane"]["nonzero_gradient_exercised"] for c in r["cells"])
    assert any(c["transition"]["nontrivial_dynamic_closure"] for c in r["cells"])
    assert all(c["transition"]["zero_sum_lane"]["zero_sum_residue"] == {"numerator":0,"denominator":1} for c in r["cells"])

def test_displaced_proposals_preserve_lo_shu_geometry_before_correction():
    r=run_three_lane_81_cell_kernel()
    for d in range(9):
        cells=r["cells"][d*9:(d+1)*9]
        e=[c["proposed_energy_credit"] for c in cells]
        assert [sum(e[i:i+3]) for i in (0,3,6)] == [75,75,75]
        assert [sum(e[i::3]) for i in range(3)] == [75,75,75]
        assert [e[0]+e[4]+e[8],e[2]+e[4]+e[6]] == [75,75]
        assert sum(e)==225

def test_nine_lo_shu_subgrids_conserve_energy():
    r=run_three_lane_81_cell_kernel()
    assert all(s["rows"]==[75,75,75] and s["columns"]==[75,75,75] and s["diagonals"]==[75,75] and s["cluster_energy"]==225 for s in r["subgrids"])

def test_full_72_step_state_cycle_proves_u72_equals_u0():
    r=run_three_lane_81_cell_kernel()
    u=r["u72_router"]
    assert u["executed_transition_count"] == 72
    assert len(u["transition_roots_hash72"]) == 72
    assert u["u72_state_root_hash72"] == u["u0_state_root_hash72"]
    assert u["u72_equals_u0"]
    assert u["all_routes_closed"]

def test_hash72_block_binds_actual_pass067_1_ancestry():
    r=run_three_lane_81_cell_kernel()
    b=r["hash72_lattice_block"]
    assert b["previous_root_hash72"] == r["pass067_1_root_hash72"]
    assert b["previous_root_hash72"] != "PASS_067_1_CANONICAL_ROOT"
    assert not b["sha256_labeled_hash72"]

def test_executable_hierarchical_reconstruction_matches_admitted_root():
    r=run_three_lane_81_cell_kernel()
    h=r["hierarchical_reconstruction"]
    assert h["subgrids_match"]
    assert h["router_matches"]
    assert h["lattice_block_matches"]
    assert h["hierarchical_reconstruction_verified"]
    assert h["reconstructed_lattice_block_root_hash72"] == h["admitted_lattice_block_root_hash72"]

def test_trinary_values_do_not_rank_authority():
    r=run_three_lane_81_cell_kernel()
    assert all(c["transition"]["trinary_is_functional_not_authority_rank"] for c in r["cells"])
    assert not r["global_rejection_propagated"]
