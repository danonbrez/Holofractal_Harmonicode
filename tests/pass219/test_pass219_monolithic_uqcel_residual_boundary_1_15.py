from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "contracts" / "pass219" / "PASS_219_MONOLITHIC_UQCEL_RESIDUAL_BOUNDARY_1_15_0.tex"
HEADER = ROOT / "hhs_runtime" / "include" / "hhs_runtime_uqcel_1_8.h"
VALIDATOR = ROOT / "hhs_runtime" / "c" / "hhs_runtime_uqcel_1_8_validate.inc"
AMENDMENT = ROOT / "HHS_PASS_219_APPEND_ONLY_MONOLITHIC_UQCEL_RESIDUAL_BOUNDARY_AMENDMENT_1_15_0.md"
I6_EXTENSION = ROOT / "contracts" / "pass219" / "PASS_219_GLOBAL_RECURSIVE_ZERO_SUM_CLOSURE_1_16_0.harmonicode"
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


def test_aggregate_monolithic_residual_remains_a_diagnostic_bit() -> None:
    header = HEADER.read_text(encoding="utf-8")
    assert "HHS_UQCEL_RESIDUAL_MONOLITHIC_EQUALITY_CHAIN UINT64_C(0x0010)" in header
    assert "HHS_UQCEL_RESIDUAL_FULL_SOURCE UINT64_C(0x001F)" in header


def test_i6_repair_forward_supersedes_unsupported_runtime_behavior() -> None:
    extension = I6_EXTENSION.read_text(encoding="utf-8")
    validator = VALIDATOR.read_text(encoding="utf-8")

    # The historical 1.15 fail-closed statement remains repository history.
    # I6 supplies the exact lowering it required by interpreting the already
    # frozen N and D objects as a typed relation/projection bridge.
    assert "NUMERATOR_OBJECT=N" in extension
    assert "DENOMINATOR_OBJECT=D" in extension
    assert "N/D⁴=D⁴" in extension
    assert "SHALL NOT remain UNSUPPORTED_DOMAIN" in extension

    assert "HHS_EXACT_UQCEL_DECISION_UNSUPPORTED_DOMAIN" not in validator
    assert "out_admission->residual_mask = 0U;" in validator
    assert "HHS_UQCEL_CONSTRAINT_GLOBAL_RELATION_BRIDGE" in validator


def test_full_symbolic_path_does_not_use_compatibility_ab_identity() -> None:
    validator = VALIDATOR.read_text(encoding="utf-8")
    assert "if (full_symbolic) {" in validator
    assert "} else {\n        if (!hhs_exact_big_equal_view_buffer(&input->A, &p_squared)" in validator
    assert "A=P^2/B=P^2 compatibility substitution" in validator
