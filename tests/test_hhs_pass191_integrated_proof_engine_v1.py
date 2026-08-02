from __future__ import annotations

import ctypes
from fractions import Fraction

from native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_integrated_proof_engine_v1 import (
    HYDRATED_CARDINALITY,
    OUTER_ENVELOPE_MODULUS,
    HHS186MappingResult,
    HHS186Quantization,
    SymmetryPoint,
    exact_reflection_obstruction,
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


def test_hydrated_cardinality_and_outer_envelope_are_exact() -> None:
    assert HYDRATED_CARDINALITY == 1_259_712
    assert OUTER_ENVELOPE_MODULUS == 1_259_713
