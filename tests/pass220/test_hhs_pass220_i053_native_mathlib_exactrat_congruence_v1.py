from __future__ import annotations

from pathlib import Path
import re

from hhs_runtime.hhs_pass220_i053_native_mathlib_exactrat_congruence_v1 import (
    CONGRUENCE_THEOREMS,
    exactrat_congruence_contract,
)

ROOT = Path(__file__).resolve().parents[2]
LEAN = (
    ROOT
    / "formal"
    / "lean"
    / "HHS"
    / "Mathlib"
    / "Algebra"
    / "ExactRatCongruence.lean"
)


def test_i053_contract_closes_operations_not_quotient_ring() -> None:
    contract = exactrat_congruence_contract()
    assert contract["operations"] == ("add", "neg", "sub", "mul")
    assert contract["universal_operation_congruence"] is True
    assert contract["quotient_ring_closed"] is False
    assert contract["equivalence_transitivity_closed"] is False
    assert contract["native_runtime_formulas_changed"] is False
    assert contract["carrier_local_int_commutation_used_in_proof"] is True
    assert contract["generic_hhs_commutation_authorized"] is False
    assert contract["vm81_mutation_authority"] == "VM81_ONLY"


def test_i053_manifest_has_one_theorem_per_operation() -> None:
    assert tuple(item.theorem for item in CONGRUENCE_THEOREMS) == (
        "ratAdd_congr",
        "ratNeg_congr",
        "ratSub_congr",
        "ratMul_congr",
    )


def test_i053_lean_source_has_no_upstream_mathlib_or_placeholders() -> None:
    source = LEAN.read_text(encoding="utf-8")
    lowered = source.lower()
    assert re.search(r"\bimport\s+mathlib\b", lowered) is None
    assert re.search(r"\bsorry\b", source, flags=re.IGNORECASE) is None
    assert re.search(r"\badmit\b", source, flags=re.IGNORECASE) is None


def test_i053_commutation_is_private_and_not_promoted() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "private theorem int_mul4_rotate" in source
    assert "Int.mul_comm" in source
    assert "genericHHSCommutationAuthorized := false" in source
    assert "quotientRingClosed := false" in source


def test_i053_operations_match_i049_native_formulas() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "def ratAdd" in source
    assert "def ratNeg" in source
    assert "def ratSub" in source
    assert "def ratMul" in source
    assert "a.denominator * b.denominator" in source
