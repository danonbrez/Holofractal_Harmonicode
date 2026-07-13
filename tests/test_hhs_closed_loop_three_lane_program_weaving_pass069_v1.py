from hhs_backend.runtime.hhs_closed_loop_three_lane_program_weaving_v1 import run_closed_loop_program_weaving, closed_loop_program_weaving_self_test

def test_self_test(): assert closed_loop_program_weaving_self_test()["ok"]
def test_program_nodes_use_all_three_lanes():
 r=run_closed_loop_program_weaving(); assert r["all_paths_use_three_lanes"]; assert all(n["all_three_lanes_present"] for n in r["program_graph"]["nodes"])
def test_program_graph_is_closed_cycle():
 r=run_closed_loop_program_weaving(); assert r["program_graph"]["closed_cycle"]; assert r["all_loops_closed"]
def test_high_level_syntax_does_not_create_authority():
 r=run_closed_loop_program_weaving(); assert not r["high_level_syntax_creates_operator_authority"]; assert all(n["operator_from_canonical_registry"] for n in r["program_graph"]["nodes"])
def test_schedule_is_authority_energy_and_u72_valid():
 r=run_closed_loop_program_weaving(); s=r["schedule"]; assert s["all_steps_authority_valid"] and s["all_steps_energy_valid"] and s["u72_schedule_closed"]
def test_execution_result_requires_revalidation():
 r=run_closed_loop_program_weaving(); assert not r["execution"]["result_is_canonical_before_revalidation"]; assert r["revalidation"]["independent_revalidation_performed"]; assert r["canonical_continuation"]
def test_standard_library_compiles_to_kernel_paths():
 r=run_closed_loop_program_weaving(); assert set(["ALIGN","TRANSLATE","VERIFY","CLOSE"]).issubset(r["standard_library_operations"])
def test_no_unclosed_local_paths():
 r=run_closed_loop_program_weaving(); assert r["execution"]["closure"]["unclosed_local_paths"] == []
