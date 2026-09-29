from __future__ import annotations

from pathlib import Path
import re

from hhs_runtime.hhs_pass220_i056_native_mathlib_exactrat_value_laws_v1 import (
    exactrat_value_laws_contract,
)

ROOT = Path(__file__).resolve().parents[2]
LEAN = ROOT / "formal" / "lean" / "HHS" / "Mathlib" / "Rat" / "ValueLaws.lean"
ROOT_LEAN = ROOT / "formal" / "lean" / "HHS.lean"


def test_i056_contract_closes_bounded_value_laws() -> None:
    contract = exactrat_value_laws_contract()
    assert contract["closed_universal_laws"] == (
        "add_left_identity",
        "add_right_identity",
        "mul_left_identity",
        "mul_right_identity",
        "add_left_inverse",
        "add_right_inverse",
    )
    assert contract["deferred_universal_laws"] == (
        "add_assoc",
        "mul_assoc",
        "left_distrib",
        "right_distrib",
    )
    assert contract["provenance_objects_rewritten"] is False
    assert contract["generic_hhs_commutation_authorized"] is False
    assert contract["runtime_arithmetic_changed"] is False
    assert contract["vm81_mutation_authority"] == "VM81_ONLY"


def test_i056_defines_zero_one_without_pair_reduction() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "def zeroPair : ExactRat" in source
    assert "def onePair : ExactRat" in source
    assert "def zeroValue : ExactRatValue" in source
    assert "def oneValue : ExactRatValue" in source


def test_i056_proves_six_universal_quotient_laws() -> None:
    source = LEAN.read_text(encoding="utf-8")
    required = (
        "theorem value_add_zero",
        "theorem value_zero_add",
        "theorem value_mul_one",
        "theorem value_one_mul",
        "theorem value_add_neg",
        "theorem value_neg_add",
    )
    for theorem in required:
        assert theorem in source


def test_i056_does_not_claim_associativity_or_distributivity() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "addAssocUniversal := false" in source
    assert "mulAssocUniversal := false" in source
    assert "leftDistribUniversal := false" in source
    assert "rightDistribUniversal := false" in source


def test_i056_preserves_provenance_and_commutation_boundaries() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "provenanceObjectsRewrittenByValueLaws := false" in source
    assert "genericHHSCommutationAuthorized := false" in source


def test_i056_has_no_upstream_mathlib_or_placeholders() -> None:
    source = LEAN.read_text(encoding="utf-8")
    lowered = source.lower()
    assert re.search(r"\bimport\s+mathlib\b", lowered) is None
    assert re.search(r"\bsorry\b", source, flags=re.IGNORECASE) is None
    assert re.search(r"\badmit\b", source, flags=re.IGNORECASE) is None


def test_i056_root_imports_value_laws_module() -> None:
    root = ROOT_LEAN.read_text(encoding="utf-8")
    assert "import HHS.Mathlib.Rat.ValueLaws" in root
