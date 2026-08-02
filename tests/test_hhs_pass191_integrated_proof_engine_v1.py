from __future__ import annotations

import ctypes
from fractions import Fraction

from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_integrated_proof_engine_v1 import (
    HHS186MappingResult,
    HHS186Quantization,
    SymmetryPoint,
    exact_reflection_obstruction,
)
from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_manifold_kernel_v1 import (
    CONTEXTUAL_CARDINALITY,
    MANIFOLD_SOURCE,
    OUTER_ENVELOPE_MODULUS,
    PROJECTED_CARDINALITY,
    evaluate_manifold_candidate,
    extract_membrane_witnesses,
    lo_shu_manifold_reduction,
    ordered_operator_witnesses,
)


def test_reflection_distinguishes_fixed_points_from_two_cycles() -> None:
    t = Fraction(141347, 10000)
    critical = SymmetryPoint(Fraction(1, 2), t)
    off_axis = SymmetryPoint(Fraction(1, 3), t)

    assert critical.reflect() == critical
    assert off_axis.reflect() != off_axis
    assert off_axis.reflect().reflect() == off_axis


def test_phase_closure_insufficiency_certificate_is_exact() -> None:
    certificate = exact_reflection_obstruction()

    assert certificate["theorem"] == (
        "PHASE_CLOSURE_ALONE_IS_NOT_A_FAITHFUL_CRITICAL_LINE_DISCRIMINATOR"
    )
    assert all(certificate["checks"].values())
    assert len(certificate["certificate_hash72"]) == 72


def test_native_abi_layout_matches_pass186_header() -> None:
    assert ctypes.sizeof(HHS186Quantization) == 16
    assert ctypes.sizeof(HHS186MappingResult) == 96


def test_projected_contextual_and_outer_cardinalities_are_exact() -> None:
    assert PROJECTED_CARDINALITY == 1_259_712
    assert CONTEXTUAL_CARDINALITY == 51_648_192
    assert OUTER_ENVELOPE_MODULUS == 1_259_713


def test_manifold_reduces_exactly_to_lo_shu_matrix() -> None:
    reduction = lo_shu_manifold_reduction()

    assert reduction["derived"]["stage1"] == "3"
    assert reduction["derived"]["stage2"] == "7"
    assert reduction["derived"]["nested"] == "7"
    assert reduction["matrix"] == [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    assert reduction["row_sums"] == ["15", "15", "15"]
    assert reduction["column_sums"] == ["15", "15", "15"]
    assert reduction["diagonal_sums"] == ["15", "15"]
    assert all(reduction["checks"].values())
    assert len(reduction["reduction_hash72"]) == 72


def test_manifold_membranes_preserve_exact_source_and_depth_witnesses() -> None:
    membranes = extract_membrane_witnesses()
    operators = ordered_operator_witnesses()

    assert membranes
    assert operators
    assert all(item["exact_source"] in MANIFOLD_SOURCE for item in membranes)
    assert all(
        item["depth_modulus"] == item["depth"] % (item["depth"] + 1)
        for item in membranes
    )
    assert all(not item["destructive_reduction_applied"] for item in membranes)
    assert any(item["operator"] == "==" for item in operators)
    assert any(item["operator"] == "where" for item in operators)


def test_closed_candidate_replays_all_exact_manifold_relations() -> None:
    row = {
        "address": 0,
        "score": 0,
        "P": 1,
        "p": 1,
        "q": 1,
        "t": 0,
        "m": 0,
        "delta": 0,
        "cubic": 0,
        "idempotent": 0,
        "residual_cubic_delta": 0,
        "residual_delta_idempotent": 0,
        "outer_residue_cubic_delta": 0,
        "outer_residue_delta_idempotent": 0,
        "cell81": 0,
        "resolved_cell81": 0,
        "operation64": 0,
        "ordered_basis8": 4,
        "g243": 0,
        "local_k": 0,
        "ternary": 0,
    }

    certificate = evaluate_manifold_candidate(row)

    assert certificate["ordered_basis"] == "xy"
    assert certificate["chain_decision"]["status"] == "PROVED"
    assert certificate["exact_relations"]["AB"] == 1
    assert certificate["exact_relations"]["P_fourth"] == 1
    assert certificate["exact_relations"]["sqrt_AB"] == 1
    assert all(certificate["checks"].values())
    assert len(certificate["candidate_hash72"]) == 72
