from __future__ import annotations

from pathlib import Path
import re

from hhs_runtime.hhs_pass220_i053_native_mathlib_exactrat_equivalence_v1 import (
    THEOREMS,
    exactrat_equivalence_contract,
)

ROOT = Path(__file__).resolve().parents[2]
LEAN = ROOT / "formal" / "lean" / "HHS" / "Mathlib" / "Rat" / "Equivalence.lean"
ROOT_LEAN = ROOT / "formal" / "lean" / "HHS.lean"


def test_i053_contract_closes_only_equivalence_nucleus() -> None:
    contract = exactrat_equivalence_contract()
    assert contract["equivalence_relation_universal"] is True
    assert contract["neg_congruence_universal"] is True
    assert contract["add_congruence_universal"] is False
    assert contract["mul_congruence_universal"] is False
    assert contract["quotient_constructed"] is False
    assert contract["pair_identity_collapsed_into_equivalence"] is False
    assert contract["generic_hhs_commutation_authorized"] is False
    assert contract["runtime_arithmetic_changed"] is False
    assert contract["vm81_mutation_authority"] == "VM81_ONLY"


def test_i053_theorem_manifest_is_unique_and_universal() -> None:
    names = tuple(item.theorem for item in THEOREMS)
    assert len(names) == 5
    assert len(set(names)) == len(names)
    assert all(item.universal for item in THEOREMS)


def test_i053_lean_source_has_no_upstream_mathlib_or_placeholders() -> None:
    source = LEAN.read_text(encoding="utf-8")
    lowered = source.lower()
    assert re.search(r"\bimport\s+mathlib\b", lowered) is None
    assert re.search(r"\bsorry\b", source, flags=re.IGNORECASE) is None
    assert re.search(r"\badmit\b", source, flags=re.IGNORECASE) is None


def test_i053_commutation_is_explicit_local_and_not_exported() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "private theorem three_factor_swap_right" in source
    assert "Int.mul_comm" in source
    assert "genericHHSCommutationAuthorized := false" in source
    assert "theorem exactrat_mul_comm" not in source.lower()
    assert "theorem exactrat_add_comm" not in source.lower()


def test_i053_unreduced_pair_identity_is_not_equivalence_identity() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "pairIdentityCollapsedIntoEqv := false" in source
    assert "quotientConstructed := false" in source


def test_i053_root_imports_equivalence_module() -> None:
    root = ROOT_LEAN.read_text(encoding="utf-8")
    assert "import HHS.Mathlib.Rat.Equivalence" in root
