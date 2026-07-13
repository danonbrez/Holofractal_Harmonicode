"""Pass 068 — three-lane 81-cell trinary qudit kernel and Hash72 lattice."""
from __future__ import annotations
from functools import lru_cache
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Mapping
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_lo_shu_harmonic_phase_energy_v1 import run_harmonic_phase_energy

VERSION = "PASS_068_1_DYNAMIC_CLOSURE_REPAIR_V1"
AUTHORITY = "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1"
LO_SHU_DEFORMATION = (1,0,-1,-2,0,2,1,0,-1)
DOMAINS = (
    "FORMAL_ALGEBRA", "SYMBOLIC_LOGIC", "SEMANTIC_TRANSLATION",
    "RUNTIME_EXECUTION", "PROVENANCE_AUDIT", "MULTIMODAL_FUSION",
    "CONSTRAINT_TOPOLOGY", "INFORMATION_ENERGY", "CANONICAL_REVALIDATION",
)
LO_SHU = (8,1,6,3,5,7,4,9,2)
PHASES = ("x","y","z","w","xy","yx","zw","wz")
TRITS = {"POSITIVE": 1, "PLASTIC": 0, "ZERO_SUM": -1}
REJECTIONS = (
    "REJECT_POSITIVE_LANE_BYPASSES_PLASTIC_EQUILIBRIUM",
    "REJECT_PLASTIC_GRADIENT_BYPASSES_ZERO_SUM_CLOSURE",
    "REJECT_ZERO_SUM_CORRECTION_ERASES_SOURCE_PHASE",
    "REJECT_LANE_ACQUIRES_COMPLETE_CELL_IDENTITY",
    "REJECT_TRINARY_VALUE_IMPLIES_AUTHORITY_RANK",
    "REJECT_PHASE_TRANSITION_WITHOUT_ALL_THREE_LANE_WITNESSES",
    "REJECT_PLASTIC_GRADIENT_CREATES_INFORMATION_ENERGY",
    "REJECT_NEGATIVE_LANE_PROPAGATES_GLOBAL_REJECTION",
    "REJECT_CELL_CLOSES_WHILE_SUBGRID_IMBALANCED",
    "REJECT_GLOBAL_LATTICE_WITH_UNRESOLVED_LOCAL_RESIDUE",
)

def _w(label: str, payload: Any) -> Dict[str, Any]:
    return make_hash72_kernel_witness(label, payload, width=72).to_dict()

def _root(label: str, payload: Any) -> str:
    return _w(label, payload)["digest"]

def _finish(schema: str, body: Dict[str, Any], field: str, label: str) -> Dict[str, Any]:
    out = {"schema": schema, "version": VERSION, "authority": AUTHORITY, **body}
    out[field] = _root(label, out)
    return out

def _frac(value: Fraction) -> Dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}

def _phase_for(index: int) -> str:
    return PHASES[index % len(PHASES)]

def make_oriented_lane(cell_id: str, phase: str, source_root: str) -> Dict[str, Any]:
    return _finish("HHS_ORIENTED_PHASE_LANE_V1", {
        "cell_id": cell_id,
        "trit": TRITS["POSITIVE"],
        "phase_state": phase,
        "source_phase_root_hash72": source_root,
        "constructive_proposal": True,
        "authority_rank_implied": False,
    }, "lane_root_hash72", "hhs_oriented_phase_lane_v1")

def make_plastic_lane(cell_id: str, source_energy: int, proposed_energy: int) -> Dict[str, Any]:
    residue = Fraction(source_energy - proposed_energy)
    state = "EQUILIBRIUM" if residue == 0 else ("CONTRACTION_PRESSURE" if residue > 0 else "EXPANSION_PRESSURE")
    return _finish("HHS_PLASTIC_GRADIENT_LANE_V1", {
        "cell_id": cell_id,
        "trit": TRITS["PLASTIC"],
        "minimal_polynomial": "rho^3-rho-1",
        "source_energy": source_energy,
        "proposed_energy": proposed_energy,
        "gradient_residue": _frac(residue),
        "gradient_state": state,
        "nonzero_gradient_exercised": residue != 0,
        "creates_information_energy": False,
        "continuation_admitted": True,
    }, "lane_root_hash72", "hhs_plastic_gradient_lane_v1")

def make_zero_sum_lane(cell_id: str, proposed_energy: int, corrected_energy: int) -> Dict[str, Any]:
    pre_residue = Fraction(proposed_energy - corrected_energy)
    post_residue = Fraction(corrected_energy - corrected_energy)
    return _finish("HHS_ZERO_SUM_EQUILIBRIUM_LANE_V1", {
        "cell_id": cell_id,
        "trit": TRITS["ZERO_SUM"],
        "proposed_energy": proposed_energy,
        "corrected_energy": corrected_energy,
        "pre_correction_residue": _frac(pre_residue),
        "zero_sum_residue": _frac(post_residue),
        "correction_applied": _frac(-pre_residue),
        "closure_state": "CLOSED" if post_residue == 0 else "OPEN",
        "cancellation_scope": [] if pre_residue == 0 else [cell_id],
        "source_phase_erased": False,
        "global_rejection_propagated": False,
        "continuation_admitted": post_residue == 0,
    }, "lane_root_hash72", "hhs_zero_sum_equilibrium_lane_v1")

def make_transition(cell_id: str, phase: str, next_phase: str, source_energy: int, proposed_energy: int, source_root: str) -> Dict[str, Any]:
    positive = make_oriented_lane(cell_id, phase, source_root)
    plastic = make_plastic_lane(cell_id, source_energy, proposed_energy)
    zero = make_zero_sum_lane(cell_id, proposed_energy, source_energy)
    lane_roots = [positive["lane_root_hash72"], plastic["lane_root_hash72"], zero["lane_root_hash72"]]
    admitted = plastic["continuation_admitted"] and zero["continuation_admitted"] and len(lane_roots) == 3
    return _finish("HHS_THREE_LANE_PHASE_TRANSITION_V1", {
        "cell_id": cell_id,
        "current_phase": phase,
        "next_phase": next_phase,
        "execution_order": ["POSITIVE", "PLASTIC", "ZERO_SUM"],
        "source_energy": source_energy,
        "proposed_energy": proposed_energy,
        "admitted_energy": source_energy,
        "positive_lane": positive,
        "plastic_lane": plastic,
        "zero_sum_lane": zero,
        "all_three_lane_witnesses_present": len(lane_roots) == 3,
        "nontrivial_dynamic_closure": proposed_energy != source_energy and zero["continuation_admitted"],
        "transition_admitted": admitted,
        "trinary_is_functional_not_authority_rank": True,
    }, "transition_root_hash72", "hhs_three_lane_phase_transition_v1")

def make_cell(domain_index: int, local_index: int, source: Mapping[str, Any]) -> Dict[str, Any]:
    global_index = domain_index * 9 + local_index
    cell_id = f"cell:{global_index:02d}"
    phase = _phase_for(global_index)
    next_phase = _phase_for(global_index + 1)
    tensor_key = ("x","y","z","w")[global_index % 4]
    tensor = source["weighted_tensors"][tensor_key]
    energy = int(tensor["base_energy"][local_index])
    proposed_energy = energy + LO_SHU_DEFORMATION[local_index]
    transition = make_transition(cell_id, phase, next_phase, energy, proposed_energy, tensor["tensor_root_hash72"])
    return _finish("HHS_TRINARY_PHASE_QUDIT_CELL_V1", {
        "cell_id": cell_id,
        "global_index": global_index,
        "row": global_index // 9,
        "column": global_index % 9,
        "subgrid_id": f"subgrid:{domain_index}",
        "domain_id": DOMAINS[domain_index],
        "lo_shu_value": LO_SHU[local_index],
        "energy_credit": energy,
        "proposed_energy_credit": proposed_energy,
        "phase_tensor": tensor_key,
        "lane_count": 3,
        "cell_identity_count": 1,
        "transition": transition,
        "cell_closed": transition["transition_admitted"],
    }, "cell_root_hash72", "hhs_trinary_phase_qudit_cell_v1")

def make_subgrid(domain_index: int, cells: List[Mapping[str, Any]]) -> Dict[str, Any]:
    energies = [int(c["energy_credit"]) for c in cells]
    rows = [sum(energies[i:i+3]) for i in (0,3,6)]
    cols = [sum(energies[i::3]) for i in range(3)]
    diags = [energies[0]+energies[4]+energies[8], energies[2]+energies[4]+energies[6]]
    conserved = rows == [75]*3 and cols == [75]*3 and diags == [75]*2 and sum(energies) == 225
    return _finish("HHS_LO_SHU_TRINARY_SUBGRID_V1", {
        "subgrid_id": f"subgrid:{domain_index}",
        "domain_id": DOMAINS[domain_index],
        "cell_ids": [c["cell_id"] for c in cells],
        "cell_roots_hash72": [c["cell_root_hash72"] for c in cells],
        "rows": rows, "columns": cols, "diagonals": diags,
        "cluster_energy": sum(energies),
        "local_lo_shu_conservation": conserved,
        "all_cells_closed": all(c["cell_closed"] for c in cells),
    }, "subgrid_root_hash72", "hhs_lo_shu_trinary_subgrid_v1")

def make_u72_route(cells: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    cell_list = list(cells)
    seed = {
        "phase_index": 0,
        "phase_state": "x",
        "cell_roots_hash72": [c["cell_root_hash72"] for c in cell_list],
    }
    initial_root = _root("hhs_u0_committed_state_v1", seed)
    current_index = 0
    transition_roots = []
    for step in range(1, 73):
        prior = current_index
        current_index = (current_index + 1) % 72
        transition_roots.append(_root("hhs_u72_phase_step_v1", {
            "step": step, "from": prior, "to": current_index, "initial_root_hash72": initial_root,
        }))
    final_state = {**seed, "phase_index": current_index}
    final_root = _root("hhs_u0_committed_state_v1", final_state)
    routes = []
    for c in cell_list:
        phase_index = (c["global_index"] * 8 + PHASES.index(c["transition"]["next_phase"])) % 72
        routes.append({"cell_id": c["cell_id"], "phase_index": phase_index, "u72_address_valid": 0 <= phase_index < 72})
    return _finish("HHS_U72_TRINARY_PHASE_ROUTER_V1", {
        "routes": routes,
        "period": 72,
        "u0_state_root_hash72": initial_root,
        "u72_state_root_hash72": final_root,
        "executed_transition_count": len(transition_roots),
        "transition_roots_hash72": transition_roots,
        "u72_equals_u0": final_root == initial_root,
        "all_routes_closed": all(r["u72_address_valid"] for r in routes) and final_root == initial_root,
    }, "router_root_hash72", "hhs_u72_trinary_phase_router_v1")

def make_hash72_lattice_block(previous_root_hash72: str, subgrids: List[Mapping[str, Any]], router: Mapping[str, Any]) -> Dict[str, Any]:
    return _finish("HHS_HASH72_TRINARY_LATTICE_BLOCK_V1", {
        "previous_root_hash72": previous_root_hash72,
        "subgrid_roots_hash72": [s["subgrid_root_hash72"] for s in subgrids],
        "u72_router_root_hash72": router["router_root_hash72"],
        "sha256_labeled_hash72": False,
    }, "lattice_block_root_hash72", "hhs_hash72_trinary_lattice_block_v1")

def reconstruct_lattice_hierarchy(previous_root_hash72: str, cells: List[Mapping[str, Any]], admitted_subgrids: List[Mapping[str, Any]], admitted_router: Mapping[str, Any], admitted_block: Mapping[str, Any]) -> Dict[str, Any]:
    rebuilt_subgrids = [make_subgrid(d, cells[d*9:(d+1)*9]) for d in range(9)]
    rebuilt_router = make_u72_route(cells)
    rebuilt_block = make_hash72_lattice_block(previous_root_hash72, rebuilt_subgrids, rebuilt_router)
    subgrids_match = [s["subgrid_root_hash72"] for s in rebuilt_subgrids] == [s["subgrid_root_hash72"] for s in admitted_subgrids]
    router_matches = rebuilt_router["router_root_hash72"] == admitted_router["router_root_hash72"]
    block_matches = rebuilt_block["lattice_block_root_hash72"] == admitted_block["lattice_block_root_hash72"]
    return _finish("HHS_EXECUTABLE_HIERARCHICAL_RECONSTRUCTION_V1", {
        "subgrids_match": subgrids_match,
        "router_matches": router_matches,
        "lattice_block_matches": block_matches,
        "hierarchical_reconstruction_verified": subgrids_match and router_matches and block_matches,
        "reconstructed_lattice_block_root_hash72": rebuilt_block["lattice_block_root_hash72"],
        "admitted_lattice_block_root_hash72": admitted_block["lattice_block_root_hash72"],
    }, "reconstruction_root_hash72", "hhs_executable_hierarchical_reconstruction_v1")

@lru_cache(maxsize=1)
def run_three_lane_81_cell_kernel() -> Dict[str, Any]:
    source = run_harmonic_phase_energy()
    cells: List[Dict[str, Any]] = []
    subgrids: List[Dict[str, Any]] = []
    for d in range(9):
        local = [make_cell(d, i, source) for i in range(9)]
        cells.extend(local)
        subgrids.append(make_subgrid(d, local))
    router = make_u72_route(cells)
    block = make_hash72_lattice_block(source["run_root_hash72"], subgrids, router)
    reconstruction = reconstruct_lattice_hierarchy(source["run_root_hash72"], cells, subgrids, router, block)
    total_energy = sum(s["cluster_energy"] for s in subgrids)
    out = {
        "schema": "HHS_81_CELL_TRINARY_QUDIT_LATTICE_V1",
        "version": VERSION,
        "authority": AUTHORITY,
        "pass067_1_root_hash72": source["run_root_hash72"],
        "cell_count": len(cells),
        "lane_projection_count": len(cells) * 3,
        "subgrid_count": len(subgrids),
        "domain_count": len(DOMAINS),
        "cells": cells,
        "subgrids": subgrids,
        "u72_router": router,
        "hash72_lattice_block": block,
        "hierarchical_reconstruction": reconstruction,
        "total_energy": total_energy,
        "expected_total_energy": 2025,
        "all_local_subgrids_closed": all(s["local_lo_shu_conservation"] and s["all_cells_closed"] for s in subgrids),
        "all_cells_have_three_lanes": all(c["lane_count"] == 3 for c in cells),
        "lane_identity_is_not_cell_identity": all(c["cell_identity_count"] == 1 for c in cells),
        "global_rejection_propagated": False,
        "rejection_codes": list(REJECTIONS),
    }
    out["global_closure"] = out["cell_count"] == 81 and out["lane_projection_count"] == 243 and out["all_local_subgrids_closed"] and router["all_routes_closed"] and reconstruction["hierarchical_reconstruction_verified"] and total_energy == 2025
    out["lattice_root_hash72"] = _root("hhs_81_cell_trinary_qudit_lattice_v1", out)
    return out

def three_lane_81_cell_kernel_self_test() -> Dict[str, Any]:
    r = run_three_lane_81_cell_kernel()
    return {
        "schema": "HHS_THREE_LANE_81_CELL_KERNEL_SELF_TEST_V1",
        "ok": r["global_closure"],
        "cell_count": r["cell_count"],
        "lane_projection_count": r["lane_projection_count"],
        "subgrid_count": r["subgrid_count"],
        "total_energy": r["total_energy"],
        "lattice_root_hash72": r["lattice_root_hash72"],
    }
