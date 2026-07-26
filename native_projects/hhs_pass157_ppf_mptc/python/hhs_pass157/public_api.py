from __future__ import annotations

from dataclasses import asdict
import json
from typing import Any

from .model import (
    CENTERLINE_LABELS,
    DENOMINATIONS,
    construct_exact,
    construct_exact_radius,
    construct_factorial_ratio_matrix as _construct_factorial_ratio_matrix,
    construct_loshu,
    construct_phase_nucleus as _construct_phase_nucleus,
    fibonacci_square_value,
    validate_loshu,
    validate_sudoku_x,
)
from .parser import compile_membrane, hash216

DEFAULT_CENTERLINE = tuple(range(1, len(CENTERLINE_LABELS) + 1))


def _default_state(rotation: int = 72):
    return construct_exact(
        P=5,
        p=2,
        q=3,
        euclid_m=3,
        euclid_n=2,
        full_rotation=rotation,
        local_modulus=72,
        centerline=DEFAULT_CENTERLINE,
    )


def construct_phase_nucleus(rotation: int = 72) -> dict[str, Any]:
    return asdict(_construct_phase_nucleus(rotation))


def parse_phase_tensor(source: str) -> dict[str, Any]:
    return compile_membrane(source, "CHECK_MEMBRANE")


def validate_centerline(state: list[str] | tuple[str, ...] | None = None) -> dict[str, Any]:
    path = tuple(state or CENTERLINE_LABELS)
    expected = CENTERLINE_LABELS
    return {
        "operator": "CENTER_LINE_PHASE_PRECEDES",
        "path": path,
        "expected": expected,
        "valid": path == expected,
    }


def expand_fibonacci_square(index: int) -> dict[str, Any]:
    value = fibonacci_square_value(index)
    return {
        "index": index,
        "square_state": value,
        "recurrence": "F[n+2]^2=F[n+1]^2+F[n]^2",
        "exact_radical": asdict(construct_exact_radius(value)),
    }


def construct_radical_carrier(index: int) -> dict[str, Any]:
    return asdict(construct_exact_radius(fibonacci_square_value(index)))


def construct_factorial_ratio_matrix(
    index: int,
    dimensions: tuple[int, int] = (3, 3),
) -> list[list[dict[str, Any]]]:
    return [
        [asdict(cell) for cell in row]
        for row in _construct_factorial_ratio_matrix(index, dimensions)
    ]


def project_loshu(state: Any | None = None) -> dict[str, Any]:
    cells = construct_loshu()
    return {
        "matrix": [[cells[3 * row + column].value for column in range(3)] for row in range(3)],
        "witnesses": [asdict(cell) for cell in cells],
        "closure": validate_loshu(cells),
        "source_state_bound": state is not None,
    }


def expand_sudoku_denomination(state: Any | None = None) -> dict[str, Any]:
    exact = _default_state()
    return {
        "valid": validate_sudoku_x(),
        "cell_count": len(exact.vm81_phase_tensor),
        "denominations": DENOMINATIONS,
        "cells": [asdict(cell) for cell in exact.vm81_phase_tensor],
        "source_state_bound": state is not None,
    }


def bind_vm81(state: Any | None = None) -> dict[str, Any]:
    result = expand_sudoku_denomination(state)
    return {
        "vm81_cell_count": result["cell_count"],
        "cells": result["cells"],
        "complete": result["cell_count"] == 81,
    }


def bind_local_hamiltonians(state: Any | None = None) -> dict[str, Any]:
    vm81 = bind_vm81(state)
    bindings = [
        {
            "vm81_address": cell["vm81_address"],
            "phase_index": cell["phase_index"],
            "fold_index": cell["fold_index"],
            "hamiltonian_ref": cell["local_hamiltonian_ref"],
        }
        for cell in vm81["cells"]
    ]
    return {
        "binding_count": len(bindings),
        "bindings": bindings,
        "complete": len(bindings) == 81,
        "inheritance_parent": "HHS-P156.1-LSHPVS",
    }


def normalize_u72(state: Any) -> dict[str, Any]:
    if isinstance(state, int):
        quotient, residue = divmod(state, 72)
    elif isinstance(state, dict) and "phase_index" in state:
        quotient, residue = divmod(int(state["phase_index"]), 72)
    else:
        raise TypeError("state must be an integer rotation or contain phase_index")
    return {
        "quotient": quotient,
        "phase_index": residue,
        "renewed_unit": residue == 0,
        "pivot_class": "0_fold .= 1_renewed" if residue == 0 else "PHASE_HELD",
    }


def commit_hash216(state: Any | None = None) -> dict[str, Any]:
    exact = _default_state()
    if state is not None:
        state_commitment = hash216(
            json.dumps(state, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        )
    else:
        state_commitment = exact.hash216_commitment
    return {
        "lanes": {
            "MAGNITUDE_DENOMINATION_HASH72": exact.hash72_lanes[0],
            "PHASE_ORDER_HASH72": exact.hash72_lanes[1],
            "NESTING_PROVENANCE_HASH72": exact.hash72_lanes[2],
        },
        "hash216": exact.hash216_commitment,
        "input_projection_hash216": state_commitment,
        "lane_order_valid": len(exact.hash216_commitment) == 216,
    }


def replay_pass157(receipt: dict[str, Any]) -> dict[str, Any]:
    current = verify_pass157()
    expected = receipt.get("hash216")
    return {
        "classification": "PASS157_REPLAY_MATCH" if expected == current["hash216"] else "REPLAY_MISMATCH",
        "expected_hash216": expected,
        "actual_hash216": current["hash216"],
        "match": expected == current["hash216"],
    }


def verify_pass157(state: Any | None = None) -> dict[str, Any]:
    exact = _default_state()
    checks = {
        "phase_pivot_typed": exact.phase_nucleus.fold_zero != exact.phase_nucleus.scalar_zero,
        "rotation_closed": exact.phase_nucleus.rotation_closed,
        "gear_words_distinct": len({cell.ordered_gear_word for cell in exact.vm81_phase_tensor}) == 4,
        "fibonacci_square_sequence": exact.fibonacci_squares[:7] == (1, 2, 3, 5, 8, 13, 21),
        "exact_radicals": all(carrier.authoritative for carrier in exact.radical_carriers),
        "factorial_ratios": all(cell.denominator > 0 for row in exact.factorial_ratio_matrix for cell in row),
        "loshu": validate_loshu(exact.lo_shu_construction),
        "sudoku": validate_sudoku_x(),
        "vm81": len(exact.vm81_phase_tensor) == 81,
        "hamiltonians": all(cell.local_hamiltonian_ref for cell in exact.vm81_phase_tensor),
        "hash72_lanes": all(len(lane) == 72 for lane in exact.hash72_lanes),
        "hash216": len(exact.hash216_commitment) == 216,
    }
    return {
        "contract_id": "HHS-P157-PPF-MPTC",
        "inheritance_parent": "HHS-P156.1-LSHPVS",
        "checks": checks,
        "verified": all(checks.values()),
        "hash216": exact.hash216_commitment,
        "classification": (
            "HHS_PASS_157_PYTHAGOREAN_PLASTIC_FIBONACCI_MODULAR_PHASE_TENSOR_CONSTRUCTOR_VERIFIED"
            if all(checks.values())
            else "PASS157_INCOMPLETE"
        ),
        "input_state_bound": state is not None,
    }
