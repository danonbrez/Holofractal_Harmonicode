"""Executable exact Lane 5 candidate hydration of the four determinant phase views.

No implicit scalar/quaternion commutation, external hash mint, or VM81 authority.
"""
from __future__ import annotations

from hhs_runtime.pass191.repository_hydration import _hash216

SOURCE = (("x", "y"), ("z", "w"))
J_CYCLE = 4
WIDTH = 5184

def _quarter(matrix):
    (a, b), (c, d) = matrix
    return ((b, (a[0], -a[1])), (d, (c[0], -c[1])))

def _source():
    return ((("x", 1), ("y", 1)), (("z", 1), ("w", 1)))

def _det(matrix):
    (a, b), (c, d) = matrix
    terms = ((a[1] * d[1], a[0] + d[0]),
             (-b[1] * c[1], b[0] + c[0]))
    # Sort additive monomials; never reorder factors inside a word.
    return tuple(sorted(terms, key=lambda item: item[1]))

def _coordinates(index):
    return {
        "linear": index,
        "hash72_row": index // 72,
        "hash72_column": index % 72,
        "vm81_cell": index // 64,
        "cell_position": index % 64,
    }

def build_lane5_quartic_phase_candidate():
    """Compute all ordered symbolic phase matrices and dual address mappings."""
    matrix = _source()
    determinant = _det(matrix)
    phases = []
    for k in range(J_CYCLE):
        if _det(matrix) != determinant:
            raise ValueError("HHS_QUARTIC_DETERMINANT_PHASE_MISMATCH")
        phases.append({
            "k": k,
            "entries": [[list(value) for value in row] for row in matrix],
            "ordered_determinant": [[sign, word] for sign, word in _det(matrix)],
        })
        matrix = _quarter(matrix)
    if matrix != _source():
        raise ValueError("HHS_QUARTIC_PHASE_CYCLE_NOT_CLOSED")
    coords = [_coordinates(i) for i in range(WIDTH)]
    if any(72*p["hash72_row"] + p["hash72_column"] != p["linear"] or
           64*p["vm81_cell"] + p["cell_position"] != p["linear"] for p in coords):
        raise ValueError("HHS_QUARTIC_COORDINATE_MISMATCH")
    body = {
        "schema": "HHS_PASS220_LANE5_QUARTIC_PHASE_CARRIER_V1",
        "phase_views": phases,
        "position_count": len(coords),
        "position_map": coords,
        "quarter_cycle_closed": True,
        "determinant_order_preserved": True,
        "candidate_only": True,
        "kernel_proof_verified": False,
        "canonical_vm81_mutation_authority": False,
    }
    body["candidate_hash216"] = _hash216("HHS-P220-LANE5-QUARTIC-PHASE-CARRIER-V1", body)
    if len(body["candidate_hash216"]) != 216:
        raise ValueError("INHERITED_HASH216_LENGTH_MISMATCH")
    return body
