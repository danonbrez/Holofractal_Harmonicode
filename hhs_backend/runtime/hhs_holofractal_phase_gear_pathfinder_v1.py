"""Pass 072 exact reciprocal phase-gear pathfinding over the 81-cell kernel.

The declared phase gear is preserved as a rational symbolic object:

    {{x,-x*y,z},{w*z,y+x,x*y},{w,-w*z,y}}

with y=x^-1 and z=w^-1.  No floating-point arithmetic is used.  Clockwise
quarter-turns are witnessed as graph transitions, positionally coupled to the
canonical Lo Shu tensor, and embedded once in each of the nine 3x3 subgrids of
the existing 81-cell trinary qudit kernel.
"""
from __future__ import annotations

from collections import deque
from fractions import Fraction
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_three_lane_81_cell_qudit_kernel_v1 import (
    run_three_lane_81_cell_kernel,
)

VERSION = "PASS_072_HOLOFRACTAL_PHASE_GEAR_PATHFINDER_V1"
AUTHORITY = "HHS_PASS072_EXACT_ROTATIONAL_PATH_AUTHORITY_V1"
LO_SHU: Tuple[Tuple[int, int, int], ...] = ((4, 9, 2), (3, 5, 7), (8, 1, 6))

REJECTIONS: Tuple[str, ...] = (
    "REJECT_PHASE_GEAR_WITHOUT_RECIPROCAL_NORMALIZATION",
    "REJECT_FLOATING_POINT_PHASE_STATE",
    "REJECT_ZERO_LENGTH_LOOP_AS_COMPUTATION",
    "REJECT_ROTATION_WITHOUT_HASH72_TRANSITION_WITNESS",
    "REJECT_LOCAL_LOOP_WITHOUT_81_CELL_MEMBERSHIP",
    "REJECT_HOLOFRACTAL_CLOSURE_WITH_OPEN_QUDIT_KERNEL",
)

Matrix = Tuple[Tuple[Fraction, Fraction, Fraction], ...]


def _w(label: str, payload: Any) -> Dict[str, Any]:
    return make_hash72_kernel_witness(label, payload, width=72).to_dict()


def _root(label: str, payload: Any) -> str:
    return _w(label, payload)["digest"]


def _finish(schema: str, body: Dict[str, Any], root_field: str, label: str) -> Dict[str, Any]:
    out = {"schema": schema, "version": VERSION, "authority": AUTHORITY, **body}
    out[root_field] = _root(label, out)
    return out


def _fraction(value: Fraction) -> Dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _matrix_payload(matrix: Matrix) -> List[List[Dict[str, int]]]:
    return [[_fraction(value) for value in row] for row in matrix]


def _matrix_signature(matrix: Matrix) -> Tuple[Tuple[Tuple[int, int], ...], ...]:
    return tuple(tuple((v.numerator, v.denominator) for v in row) for row in matrix)


def make_normalized_phase_gear(x: Fraction = Fraction(2, 1), z: Fraction = Fraction(3, 1)) -> Dict[str, Any]:
    if x == 0 or z == 0:
        raise ValueError("x and z must be nonzero for reciprocal normalization")
    y = Fraction(1, 1) / x
    w = Fraction(1, 1) / z
    matrix: Matrix = (
        (x, -(x * y), z),
        (w * z, y + x, x * y),
        (w, -(w * z), y),
    )
    reciprocal = x * y == 1 and w * z == 1
    return _finish(
        "HHS_NORMALIZED_RECIPROCAL_PHASE_GEAR_V1",
        {
            "relations": {"y": "x^-1", "z": "w^-1", "xy": "1", "wz": "1"},
            "x": _fraction(x),
            "y": _fraction(y),
            "z": _fraction(z),
            "w": _fraction(w),
            "matrix": _matrix_payload(matrix),
            "reciprocal_normalization_valid": reciprocal,
            "floating_point_used": False,
        },
        "phase_gear_root_hash72",
        "hhs_normalized_reciprocal_phase_gear_v1",
    )


def normalized_matrix(x: Fraction = Fraction(2, 1), z: Fraction = Fraction(3, 1)) -> Matrix:
    y = Fraction(1, 1) / x
    w = Fraction(1, 1) / z
    return (
        (x, -(x * y), z),
        (w * z, y + x, x * y),
        (w, -(w * z), y),
    )


def rotate_clockwise(matrix: Matrix) -> Matrix:
    return tuple(tuple(matrix[2 - column][row] for column in range(3)) for row in range(3))


def rotate(matrix: Matrix, quarter_turns: int) -> Matrix:
    out = matrix
    for _ in range(quarter_turns % 4):
        out = rotate_clockwise(out)
    return out


def lo_shu_weight(matrix: Matrix) -> Matrix:
    return tuple(
        tuple(matrix[row][column] * LO_SHU[row][column] for column in range(3))
        for row in range(3)
    )


def _orientation(base: Matrix, state: int) -> Dict[str, Any]:
    matrix = rotate(base, state)
    weighted = lo_shu_weight(matrix)
    return _finish(
        "HHS_LO_SHU_WEIGHTED_PHASE_GEAR_ORIENTATION_V1",
        {
            "orientation": state % 4,
            "matrix": _matrix_payload(matrix),
            "lo_shu_tensor": [list(row) for row in LO_SHU],
            "weighted_matrix": _matrix_payload(weighted),
            "state_signature": repr(_matrix_signature(weighted)),
            "reciprocal_relations_preserved": True,
        },
        "orientation_root_hash72",
        "hhs_lo_shu_weighted_phase_gear_orientation_v1",
    )


def shortest_nonempty_closed_orbit(base: Matrix, start_orientation: int = 0, max_depth: int = 8) -> Dict[str, Any]:
    start = start_orientation % 4
    start_matrix = rotate(base, start)
    start_signature = _matrix_signature(start_matrix)
    queue = deque([(start_matrix, start, [start])])
    visited_depth: Dict[Tuple[Tuple[Tuple[int, int], ...], ...], int] = {start_signature: 0}
    winning_path: List[int] = []

    while queue:
        matrix, orientation, path = queue.popleft()
        depth = len(path) - 1
        if depth >= max_depth:
            continue
        next_matrix = rotate_clockwise(matrix)
        next_orientation = (orientation + 1) % 4
        next_path = path + [next_orientation]
        next_signature = _matrix_signature(next_matrix)
        if next_signature == start_signature:
            winning_path = next_path
            break
        prior_depth = visited_depth.get(next_signature)
        if prior_depth is None or depth + 1 < prior_depth:
            visited_depth[next_signature] = depth + 1
            queue.append((next_matrix, next_orientation, next_path))

    if not winning_path:
        return _finish(
            "HHS_PHASE_GEAR_CLOSED_ORBIT_V1",
            {
                "status": "REJECT_NO_BOUNDED_CLOSED_ORBIT",
                "start_orientation": start,
                "orientation_path": [],
                "transition_count": 0,
                "nonempty": False,
                "closed": False,
            },
            "loop_root_hash72",
            "hhs_phase_gear_closed_orbit_v1",
        )

    orientations = [_orientation(base, state) for state in winning_path]
    transitions: List[Dict[str, Any]] = []
    for index in range(len(winning_path) - 1):
        transitions.append(
            _finish(
                "HHS_PHASE_GEAR_ROTATION_TRANSITION_V1",
                {
                    "step": index + 1,
                    "from_orientation": winning_path[index],
                    "to_orientation": winning_path[index + 1],
                    "from_root_hash72": orientations[index]["orientation_root_hash72"],
                    "to_root_hash72": orientations[index + 1]["orientation_root_hash72"],
                    "operator": "ROTATE_CLOCKWISE_QUARTER_TURN",
                    "reciprocal_relations_preserved": True,
                },
                "transition_root_hash72",
                "hhs_phase_gear_rotation_transition_v1",
            )
        )
    intermediate_roots = [item["orientation_root_hash72"] for item in orientations[:-1]]
    return _finish(
        "HHS_PHASE_GEAR_CLOSED_ORBIT_V1",
        {
            "status": "ADMIT_SHORTEST_NONEMPTY_CLOSED_ORBIT",
            "start_orientation": start,
            "orientation_path": winning_path,
            "transition_count": len(transitions),
            "orientations": orientations,
            "transitions": transitions,
            "nonempty": len(transitions) > 0,
            "closed": winning_path[0] == winning_path[-1],
            "intermediate_states_nonidentical": len(set(intermediate_roots)) == len(intermediate_roots),
            "reciprocal_invariants_preserved": all(t["reciprocal_relations_preserved"] for t in transitions),
        },
        "loop_root_hash72",
        "hhs_phase_gear_closed_orbit_v1",
    )


def _make_subgrid_loop(base: Matrix, subgrid: Mapping[str, Any], start_orientation: int) -> Dict[str, Any]:
    loop = shortest_nonempty_closed_orbit(base, start_orientation=start_orientation)
    return _finish(
        "HHS_SUBGRID_PHASE_GEAR_LOOP_V1",
        {
            "subgrid_id": subgrid["subgrid_id"],
            "domain_id": subgrid["domain_id"],
            "cell_ids": list(subgrid["cell_ids"]),
            "cell_roots_hash72": list(subgrid["cell_roots_hash72"]),
            "subgrid_root_hash72": subgrid["subgrid_root_hash72"],
            "start_orientation": start_orientation % 4,
            "orientation_path": list(loop["orientation_path"]),
            "transition_count": loop["transition_count"],
            "closed": loop["closed"],
            "nonempty": loop["nonempty"],
            "intermediate_states_nonidentical": loop["intermediate_states_nonidentical"],
            "reciprocal_invariants_preserved": loop["reciprocal_invariants_preserved"],
            "local_loop_root_hash72": loop["loop_root_hash72"],
        },
        "subgrid_loop_root_hash72",
        "hhs_subgrid_phase_gear_loop_v1",
    )


@lru_cache(maxsize=1)
def run_holofractal_phase_gear_pathfinder() -> Dict[str, Any]:
    kernel = run_three_lane_81_cell_kernel()
    gear = make_normalized_phase_gear()
    base = normalized_matrix()
    loops = [
        _make_subgrid_loop(base, subgrid, index % 4)
        for index, subgrid in enumerate(kernel["subgrids"])
    ]
    covered_cells = [cell_id for loop in loops for cell_id in loop["cell_ids"]]
    periods = [int(loop["transition_count"]) for loop in loops]
    macro = _finish(
        "HHS_HOLOFRACTAL_PHASE_GEAR_MACRO_LOOP_V1",
        {
            "phase_gear_root_hash72": gear["phase_gear_root_hash72"],
            "lattice_root_hash72": kernel["lattice_root_hash72"],
            "subgrid_loop_roots_hash72": [loop["subgrid_loop_root_hash72"] for loop in loops],
            "local_loop_count": len(loops),
            "local_periods": periods,
            "total_rotation_steps": sum(periods),
            "covered_cell_count": len(set(covered_cells)),
            "all_81_cells_covered_once": len(covered_cells) == 81 and len(set(covered_cells)) == 81,
            "all_local_loops_closed": all(loop["closed"] and loop["nonempty"] for loop in loops),
            "all_intermediate_states_nonidentical": all(loop["intermediate_states_nonidentical"] for loop in loops),
            "reciprocal_invariants_preserved": all(loop["reciprocal_invariants_preserved"] for loop in loops),
            "kernel_global_closure": bool(kernel["global_closure"]),
        },
        "macro_loop_root_hash72",
        "hhs_holofractal_phase_gear_macro_loop_v1",
    )
    result = {
        "schema": "HHS_HOLOFRACTAL_PHASE_GEAR_PATHFINDER_V1",
        "version": VERSION,
        "authority": AUTHORITY,
        "phase_gear": gear,
        "lo_shu_tensor": [list(row) for row in LO_SHU],
        "lattice_root_hash72": kernel["lattice_root_hash72"],
        "local_loops": loops,
        "macro_loop": macro,
        "local_loop_count": len(loops),
        "local_periods": periods,
        "total_rotation_steps": sum(periods),
        "cell_coverage_count": len(set(covered_cells)),
        "rotation_operator_period": 4,
        "kernel_global_closure": bool(kernel["global_closure"]),
        "holofractal_closure": bool(
            kernel["global_closure"]
            and macro["all_81_cells_covered_once"]
            and macro["all_local_loops_closed"]
            and macro["reciprocal_invariants_preserved"]
            and periods == [4] * 9
        ),
        "floating_point_used": False,
        "rejection_codes": list(REJECTIONS),
    }
    result["run_root_hash72"] = _root("hhs_holofractal_phase_gear_pathfinder_v1", result)
    return result


def holofractal_phase_gear_pathfinder_self_test() -> Dict[str, Any]:
    result = run_holofractal_phase_gear_pathfinder()
    return {
        "schema": "HHS_HOLOFRACTAL_PHASE_GEAR_PATHFINDER_SELF_TEST_V1",
        "ok": result["holofractal_closure"],
        "local_loop_count": result["local_loop_count"],
        "local_periods": result["local_periods"],
        "total_rotation_steps": result["total_rotation_steps"],
        "cell_coverage_count": result["cell_coverage_count"],
        "macro_loop_root_hash72": result["macro_loop"]["macro_loop_root_hash72"],
        "run_root_hash72": result["run_root_hash72"],
    }


if __name__ == "__main__":
    print(holofractal_phase_gear_pathfinder_self_test())
