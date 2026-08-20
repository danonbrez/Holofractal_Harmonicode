from __future__ import annotations

import copy
import hashlib
from fractions import Fraction
from pathlib import Path

import pytest

from hhs_runtime.hhs_pass219b_global_zero_sum_closure_proof_v1 import (
    CLOSURE_EXTENSION_SHA256,
    GlobalZeroSumClosureError,
    prove_global_zero_sum_closure,
    verify_global_zero_sum_closure,
)

ROOT = Path(__file__).resolve().parents[2]
EXTENSION = ROOT / "contracts" / "pass219" / "PASS_219_GLOBAL_RECURSIVE_ZERO_SUM_CLOSURE_1_16_0.harmonicode"
UQCEL_HEADER = ROOT / "hhs_runtime" / "include" / "hhs_runtime_uqcel_1_8.h"
UQCEL_VALIDATOR = ROOT / "hhs_runtime" / "c" / "hhs_runtime_uqcel_1_8_validate.inc"


def _f(fd: dict[str, int]) -> Fraction:
    return Fraction(fd["numerator"], fd["denominator"])


def test_closure_extension_is_byte_frozen() -> None:
    raw = EXTENSION.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CLOSURE_EXTENSION_SHA256
    text = raw.decode("utf-8")
    assert "N/D⁴=D⁴" in text
    assert "1=u⁷²" in text
    assert "x+y+z+w=0" in text
    assert "I+I^2+I^3+I^4=0" in text
    assert "may be algebraically simplified" in text


@pytest.mark.parametrize("P", [4, 5, 6, 8, 10, 100, 1024, Fraction(9, 2), Fraction(-7, 3)])
def test_exact_zero_sum_closure_family(P) -> None:
    proof = prove_global_zero_sum_closure(center_P=P)
    verify = verify_global_zero_sum_closure(proof)
    assert verify["status"] == "GLOBAL_ZERO_SUM_CLOSURE_VALIDATED"
    family = proof["closure_family"]
    assert _f(family["delta"]) == 1
    assert _f(family["p"]) == Fraction(P) - 1
    assert _f(family["q"]) == Fraction(P) + 1
    assert _f(family["P_squared_minus_pq"]) == 1
    assert _f(family["xy_projection"]) == 1
    assert _f(family["zw_projection"]) == 1
    assert _f(family["x_plus_y_plus_z_plus_w"]) == 0
    assert family["phase_carrier_sum_basis_1_I"] == [0, 0]
    assert _f(family["membrane_residue"]) == 1
    assert proof["denominator_projection_binding"]["unit_perimeter_cells"] == 8
    assert proof["denominator_projection_binding"]["recursive_relation_evaluated"] is False
    assert proof["global_enforcement"]["full_monolithic_evaluated"] is False


def test_zero_center_is_excluded_by_inherited_four_phase_normalization_domain() -> None:
    with pytest.raises(Exception):
        prove_global_zero_sum_closure(center_P=0)


def test_tampered_center_sum_proof_rejected() -> None:
    proof = prove_global_zero_sum_closure(center_P=4)
    bad = copy.deepcopy(proof)
    bad["closure_family"]["x_plus_y_plus_z_plus_w"] = {"numerator": 1, "denominator": 1}
    with pytest.raises(GlobalZeroSumClosureError):
        verify_global_zero_sum_closure(bad)


def test_tampered_phase_sum_proof_rejected() -> None:
    proof = prove_global_zero_sum_closure(center_P=4)
    bad = copy.deepcopy(proof)
    bad["closure_family"]["phase_carrier_sum_basis_1_I"] = [1, 0]
    with pytest.raises(GlobalZeroSumClosureError):
        verify_global_zero_sum_closure(bad)


def test_recursive_fixed_point_cannot_be_promoted_by_zero_sum_proof() -> None:
    proof = prove_global_zero_sum_closure(center_P=4)
    bad = copy.deepcopy(proof)
    bad["denominator_projection_binding"]["recursive_relation_evaluated"] = True
    with pytest.raises(GlobalZeroSumClosureError):
        verify_global_zero_sum_closure(bad)


def test_full_monolithic_chain_cannot_be_promoted_by_zero_sum_proof() -> None:
    proof = prove_global_zero_sum_closure(center_P=4)
    bad = copy.deepcopy(proof)
    bad["global_enforcement"]["full_monolithic_evaluated"] = True
    with pytest.raises(GlobalZeroSumClosureError):
        verify_global_zero_sum_closure(bad)


def test_full_symbolic_uqcel_declares_global_zero_sum_constraint() -> None:
    header = UQCEL_HEADER.read_text(encoding="utf-8")
    validator = UQCEL_VALIDATOR.read_text(encoding="utf-8")
    assert "HHS_UQCEL_CONSTRAINT_GLOBAL_ZERO_SUM_CLOSURE" in header
    assert "hhs_exact_pass219b_global_zero_sum_prove" in validator
    assert "HHS_UQCEL_CONSTRAINT_GLOBAL_ZERO_SUM_CLOSURE" in validator
    symbolic = validator.index("HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1")
    unsupported = validator.index("HHS_EXACT_UQCEL_DECISION_UNSUPPORTED_DOMAIN")
    assert symbolic < unsupported
