from __future__ import annotations

from pathlib import Path
import re

from hhs_runtime.hhs_pass220_i054_native_mathlib_exactrat_congruence_v1 import (
    THEOREMS,
    exactrat_congruence_contract,
)

ROOT = Path(__file__).resolve().parents[2]
LEAN = ROOT / "formal" / "lean" / "HHS" / "Mathlib" / "Rat" / "Congruence.lean"
ROOT_LEAN = ROOT / "formal" / "lean" / "HHS.lean"


def test_i054_contract_closes_binary_congruence_only() -> None:
    contract = exactrat_congruence_contract()
    assert contract["neg_congruence_universal"] is True
    assert contract["add_congruence_universal"] is True
    assert contract["mul_congruence_universal"] is True
    assert contract["quotient_constructed"] is False
    assert contract["pair_identity_collapsed_into_equivalence"] is False
    assert contract["generic_hhs_commutation_authorized"] is False
    assert contract["runtime_arithmetic_changed"] is False
    assert contract["vm81_mutation_authority"] == "VM81_ONLY"


def test_i054_formulas_match_i049_unreduced_runtime() -> None:
    contract = exactrat_congruence_contract()
    assert contract["addition_formula"] == (
        "(a.num*b.den+b.num*a.den)/(a.den*b.den)"
    )
    assert contract["multiplication_formula"] == (
        "(a.num*b.num)/(a.den*b.den)"
    )


def test_i054_theorem_manifest_is_exact_and_unique() -> None:
    names = tuple(item.theorem for item in THEOREMS)
    assert names == ("eqv_add_congr", "eqv_mul_congr")
    assert all(item.universal for item in THEOREMS)


def test_i054_lean_source_has_no_upstream_mathlib_or_placeholders() -> None:
    source = LEAN.read_text(encoding="utf-8")
    lowered = source.lower()
    assert re.search(r"\bimport\s+mathlib\b", lowered) is None
    assert re.search(r"\bsorry\b", source, flags=re.IGNORECASE) is None
    assert re.search(r"\badmit\b", source, flags=re.IGNORECASE) is None


def test_i054_commutation_is_private_local_only() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "private theorem mul_pair_swap_middle" in source
    assert "Int.mul_comm" in source
    assert "genericHHSCommutationAuthorized := false" in source


def test_i054_quotient_and_pair_identity_remain_deferred() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "quotientConstructed := false" in source
    assert "pairIdentityCollapsedIntoEqv := false" in source


def test_i054_root_imports_congruence_module() -> None:
    root = ROOT_LEAN.read_text(encoding="utf-8")
    assert "import HHS.Mathlib.Rat.Congruence" in root
