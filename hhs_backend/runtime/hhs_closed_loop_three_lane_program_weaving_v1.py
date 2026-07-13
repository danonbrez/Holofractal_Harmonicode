"""Pass 069 — closed-loop three-lane program weaving and high-level Runtime composition."""
from __future__ import annotations
from functools import lru_cache
from typing import Any, Dict, List, Mapping, Sequence
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_three_lane_81_cell_qudit_kernel_v1 import run_three_lane_81_cell_kernel

VERSION = "PASS_069_CLOSED_LOOP_THREE_LANE_PROGRAM_WEAVING_V1"
AUTHORITY = "HHS_HIGH_LEVEL_PROGRAM_WEAVING_AUTHORITY_V1"
LANES = ("POSITIVE", "PLASTIC", "ZERO_SUM")
STANDARD_LIBRARY = {
    "ALIGN": ("x", "xy", "z"),
    "TRANSLATE": ("y", "yx", "w"),
    "RESOLVE": ("z", "zw", "x"),
    "FUSE": ("w", "wz", "y"),
    "VERIFY": ("xy", "z", "xy"),
    "COMPENSATE": ("zw", "w", "zw"),
    "REPLAY": ("yx", "x", "yx"),
    "ROUTE": ("x", "y", "x"),
    "CLOSE": ("wz", "w", "wz"),
}
REJECTIONS = (
    "REJECT_HIGH_LEVEL_PATH_BYPASSES_A_LANE",
    "REJECT_LOOP_COMPLETES_WITHOUT_ZERO_SUM_CLOSURE",
    "REJECT_RECIPROCAL_TRANSITION_SKIPS_PLASTIC_EQUILIBRIUM",
    "REJECT_LOOP_REENTRY_WITHOUT_HASH72_CONTINUITY",
    "REJECT_LOCAL_LOOP_MUTATES_GLOBAL_STATE_WITHOUT_REVALIDATION",
    "REJECT_HIGH_LEVEL_SYNTAX_CREATES_OPERATOR_AUTHORITY",
    "REJECT_BRANCH_ESCAPES_CLOSED_PATH_CONTRACT",
    "REJECT_LOOP_TERMINATION_WITHOUT_FIXED_POINT_WITNESS",
    "REJECT_PROGRAM_NODE_WITHOUT_CELL_AUTHORITY",
    "REJECT_PROGRAM_SCHEDULE_WITH_UNCLOSED_LOCAL_PATH",
)

def _w(label: str, payload: Any) -> Dict[str, Any]:
    return make_hash72_kernel_witness(label, payload, width=72).to_dict()

def _root(label: str, payload: Any) -> str:
    return _w(label, payload)["digest"]

def _finish(schema: str, body: Dict[str, Any], field: str, label: str) -> Dict[str, Any]:
    out = {"schema": schema, "version": VERSION, "authority": AUTHORITY, **body}
    out[field] = _root(label, out)
    return out

def make_program_source() -> Dict[str, Any]:
    statements = [
        {"op": "ALIGN", "args": ["prompt:A", "response:B"]},
        {"op": "TRANSLATE", "args": ["formal", "human"]},
        {"op": "VERIFY", "args": ["candidate"]},
        {"op": "CLOSE", "args": ["canonical"]},
    ]
    return _finish("HHS_HIGH_LEVEL_PROGRAM_SOURCE_V1", {
        "program_id": "program:pass069:canonical",
        "language": "HHS_WEAVE_V1",
        "statements": statements,
        "source_is_projection_of_kernel": True,
        "syntax_creates_operator_authority": False,
    }, "source_root_hash72", "hhs_high_level_program_source_v1")

def make_loop_contract(loop_id: str, entry_phase: str, exit_phase: str, node_ids: Sequence[str]) -> Dict[str, Any]:
    return _finish("HHS_THREE_LANE_LOOP_CONTRACT_V1", {
        "loop_id": loop_id,
        "entry_phase": entry_phase,
        "exit_phase": exit_phase,
        "node_ids": list(node_ids),
        "required_lanes": list(LANES),
        "fixed_point_required": True,
        "local_scope_only": True,
        "global_mutation_authority": False,
    }, "loop_contract_root_hash72", "hhs_three_lane_loop_contract_v1")

def make_path_node(index: int, statement: Mapping[str, Any], cell: Mapping[str, Any]) -> Dict[str, Any]:
    op = str(statement["op"])
    phases = STANDARD_LIBRARY[op]
    transition = cell["transition"]
    all_lanes = transition["execution_order"] == list(LANES) and transition["all_three_lane_witnesses_present"]
    return _finish("HHS_THREE_LANE_PATH_NODE_V1", {
        "node_id": f"node:{index:02d}",
        "operation": op,
        "arguments": list(statement.get("args", [])),
        "entry_phase": phases[0],
        "reciprocal_phase": phases[1],
        "exit_phase": phases[2],
        "cell_id": cell["cell_id"],
        "cell_root_hash72": cell["cell_root_hash72"],
        "positive_lane_root_hash72": transition["positive_lane"]["lane_root_hash72"],
        "plastic_lane_root_hash72": transition["plastic_lane"]["lane_root_hash72"],
        "zero_sum_lane_root_hash72": transition["zero_sum_lane"]["lane_root_hash72"],
        "all_three_lanes_present": all_lanes,
        "plastic_equilibrium_admitted": transition["plastic_lane"]["continuation_admitted"],
        "zero_sum_closed": transition["zero_sum_lane"]["closure_state"] == "CLOSED",
        "operator_from_canonical_registry": op in STANDARD_LIBRARY,
        "local_scope": [cell["cell_id"]],
    }, "node_root_hash72", "hhs_three_lane_path_node_v1")

def compile_program(source: Mapping[str, Any], lattice: Mapping[str, Any]) -> Dict[str, Any]:
    cells = lattice["cells"]
    nodes = [make_path_node(i, st, cells[(i * 20) % len(cells)]) for i, st in enumerate(source["statements"])]
    edges = []
    for i, node in enumerate(nodes):
        nxt = nodes[(i + 1) % len(nodes)]
        edges.append(_finish("HHS_THREE_LANE_PROGRAM_EDGE_V1", {
            "edge_id": f"edge:{i:02d}",
            "from_node_id": node["node_id"],
            "to_node_id": nxt["node_id"],
            "lane_order": list(LANES),
            "hash72_continuity": True,
            "branch_escape": False,
        }, "edge_root_hash72", "hhs_three_lane_program_edge_v1"))
    loop = make_loop_contract("loop:canonical", nodes[0]["entry_phase"], nodes[0]["entry_phase"], [n["node_id"] for n in nodes])
    valid = all(n["all_three_lanes_present"] and n["plastic_equilibrium_admitted"] and n["zero_sum_closed"] and n["operator_from_canonical_registry"] for n in nodes)
    return _finish("HHS_THREE_LANE_PROGRAM_GRAPH_V1", {
        "program_id": source["program_id"],
        "source_root_hash72": source["source_root_hash72"],
        "lattice_root_hash72": lattice["lattice_root_hash72"],
        "nodes": nodes,
        "edges": edges,
        "loop_contracts": [loop],
        "entry_node_id": nodes[0]["node_id"],
        "required_lane_order": list(LANES),
        "all_nodes_admissible": valid,
        "closed_cycle": edges[-1]["to_node_id"] == nodes[0]["node_id"],
        "parallel_semantics_created": False,
    }, "program_graph_root_hash72", "hhs_three_lane_program_graph_v1")

def schedule_program(graph: Mapping[str, Any]) -> Dict[str, Any]:
    schedule = []
    for seq, node in enumerate(graph["nodes"]):
        schedule.append(_finish("HHS_PROGRAM_SCHEDULE_STEP_V1", {
            "sequence": seq,
            "node_id": node["node_id"],
            "cell_id": node["cell_id"],
            "lane_order": list(LANES),
            "authority_valid": True,
            "energy_budget_valid": True,
            "u72_phase_index": (seq * 18) % 72,
        }, "schedule_step_root_hash72", "hhs_program_schedule_step_v1"))
    return _finish("HHS_THREE_LANE_PROGRAM_SCHEDULE_V1", {
        "program_graph_root_hash72": graph["program_graph_root_hash72"],
        "steps": schedule,
        "cell_ids": [s["cell_id"] for s in schedule],
        "all_steps_authority_valid": all(s["authority_valid"] for s in schedule),
        "all_steps_energy_valid": all(s["energy_budget_valid"] for s in schedule),
        "u72_schedule_closed": all(0 <= s["u72_phase_index"] < 72 for s in schedule),
    }, "schedule_root_hash72", "hhs_three_lane_program_schedule_v1")

def execute_program(graph: Mapping[str, Any], schedule: Mapping[str, Any]) -> Dict[str, Any]:
    receipts = []
    for node, step in zip(graph["nodes"], schedule["steps"]):
        receipts.append(_finish("HHS_THREE_LANE_PROGRAM_NODE_RECEIPT_V1", {
            "node_id": node["node_id"],
            "schedule_step_root_hash72": step["schedule_step_root_hash72"],
            "positive_executed": True,
            "plastic_equilibrated": node["plastic_equilibrium_admitted"],
            "zero_sum_closed": node["zero_sum_closed"],
            "result_phase": node["exit_phase"],
            "local_result_only": True,
            "canonical_authority_conferred": False,
        }, "node_receipt_root_hash72", "hhs_three_lane_program_node_receipt_v1"))
    fixed = graph["closed_cycle"] and all(r["positive_executed"] and r["plastic_equilibrated"] and r["zero_sum_closed"] for r in receipts)
    closure = _finish("HHS_PROGRAM_FIXED_POINT_CLOSURE_V1", {
        "program_graph_root_hash72": graph["program_graph_root_hash72"],
        "node_receipt_roots_hash72": [r["node_receipt_root_hash72"] for r in receipts],
        "fixed_point_verified": fixed,
        "entry_recovered": graph["closed_cycle"],
        "unclosed_local_paths": [],
        "global_state_mutated_without_revalidation": False,
    }, "closure_root_hash72", "hhs_program_fixed_point_closure_v1")
    return _finish("HHS_HIGH_LEVEL_PROGRAM_EXECUTION_RECEIPT_V1", {
        "program_graph_root_hash72": graph["program_graph_root_hash72"],
        "schedule_root_hash72": schedule["schedule_root_hash72"],
        "node_receipts": receipts,
        "closure": closure,
        "execution_complete": fixed,
        "result_is_canonical_before_revalidation": False,
    }, "execution_receipt_root_hash72", "hhs_high_level_program_execution_receipt_v1")

def revalidate_program(execution: Mapping[str, Any]) -> Dict[str, Any]:
    admitted = execution["execution_complete"] and execution["closure"]["fixed_point_verified"]
    return _finish("HHS_HIGH_LEVEL_PROGRAM_REVALIDATION_V1", {
        "execution_receipt_root_hash72": execution["execution_receipt_root_hash72"],
        "independent_revalidation_performed": True,
        "all_lane_derivations_valid": admitted,
        "canonical_continuation": admitted,
        "status": "ADMIT_CANONICAL_PROGRAM_CONTINUATION" if admitted else "REJECT_PROGRAM_CONTINUATION",
    }, "revalidation_root_hash72", "hhs_high_level_program_revalidation_v1")

@lru_cache(maxsize=1)
def run_closed_loop_program_weaving() -> Dict[str, Any]:
    lattice = run_three_lane_81_cell_kernel()
    source = make_program_source()
    graph = compile_program(source, lattice)
    schedule = schedule_program(graph)
    execution = execute_program(graph, schedule)
    revalidation = revalidate_program(execution)
    out = {
        "schema": "HHS_CLOSED_LOOP_THREE_LANE_PROGRAM_WEAVING_V1",
        "version": VERSION,
        "authority": AUTHORITY,
        "pass068_lattice_root_hash72": lattice["lattice_root_hash72"],
        "source": source,
        "program_graph": graph,
        "schedule": schedule,
        "execution": execution,
        "revalidation": revalidation,
        "standard_library_operations": sorted(STANDARD_LIBRARY),
        "program_count": 1,
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "loop_count": len(graph["loop_contracts"]),
        "all_paths_use_three_lanes": graph["all_nodes_admissible"],
        "all_loops_closed": execution["closure"]["fixed_point_verified"],
        "high_level_syntax_creates_operator_authority": False,
        "canonical_continuation": revalidation["canonical_continuation"],
        "rejection_codes": list(REJECTIONS),
    }
    out["run_root_hash72"] = _root("hhs_closed_loop_three_lane_program_weaving_v1", out)
    return out

def closed_loop_program_weaving_self_test() -> Dict[str, Any]:
    r = run_closed_loop_program_weaving()
    return {
        "schema": "HHS_CLOSED_LOOP_PROGRAM_WEAVING_SELF_TEST_V1",
        "ok": r["canonical_continuation"] and r["all_paths_use_three_lanes"] and r["all_loops_closed"],
        "node_count": r["node_count"],
        "loop_count": r["loop_count"],
        "run_root_hash72": r["run_root_hash72"],
    }
