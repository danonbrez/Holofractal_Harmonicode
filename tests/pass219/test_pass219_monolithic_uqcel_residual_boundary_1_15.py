from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "contracts" / "pass219" / "PASS_219_MONOLITHIC_UQCEL_RESIDUAL_BOUNDARY_1_15_0.tex"
HEADER = ROOT / "hhs_runtime" / "include" / "hhs_runtime_uqcel_1_8.h"
VALIDATOR = ROOT / "hhs_runtime" / "c" / "hhs_runtime_uqcel_1_8_validate.inc"
AMENDMENT = ROOT / "HHS_PASS_219_APPEND_ONLY_MONOLITHIC_UQCEL_RESIDUAL_BOUNDARY_AMENDMENT_1_15_0.md"
EXPECTED_SHA256 = "9f2238981bf509d22ffebb46816346f389fd2d949ccd7956cde3630ab2b56944"


def test_verbatim_monolithic_equation_fixture_is_byte_frozen() -> None:
    raw = FIXTURE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256
    text = raw.decode("utf-8")
    assert "\\frac{AB}{P^2}" in text
    assert "\\sqrt{AB}" in text
    assert "\\mathcal{M}_{L_H}" in text
    assert "\\frac{\\Delta}{P} = \\sqrt{pq + u^{72}}^{\\,x^2}" in text


def test_full_symbolic_ab_semantics_are_lhs_rhs_not_p_squared() -> None:
    amendment = AMENDMENT.read_text(encoding="utf-8")
    assert "`A` is the complete left-hand side" in amendment
    assert "`B` is the complete right-hand side" in amendment
    assert "`A` and `B` are **not** definitionally equal to `P^2`" in amendment


def test_aggregate_monolithic_residual_cannot_be_dropped() -> None:
    header = HEADER.read_text(encoding="utf-8")
    assert "HHS_UQCEL_RESIDUAL_MONOLITHIC_EQUALITY_CHAIN UINT64_C(0x0010)" in header
    assert "HHS_UQCEL_RESIDUAL_FULL_SOURCE UINT64_C(0x001F)" in header


def test_full_symbolic_path_does_not_run_integer_symmetric_ab_checks() -> None:
    validator = VALIDATOR.read_text(encoding="utf-8")
    symbolic_guard = validator.index("if (input->profile == HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1)")
    compatibility_ab_check = validator.index("hhs_exact_big_equal_view_buffer(&input->A, &p_squared)")
    assert symbolic_guard < compatibility_ab_check
    assert "The aggregate monolithic residual remains set." in validator
