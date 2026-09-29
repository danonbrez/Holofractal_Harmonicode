from __future__ import annotations

from pathlib import Path
import re

from hhs_runtime.hhs_pass220_i055_native_mathlib_exactrat_value_v1 import (
    exactrat_value_contract,
)

ROOT = Path(__file__).resolve().parents[2]
LEAN = ROOT / "formal" / "lean" / "HHS" / "Mathlib" / "Rat" / "Value.lean"
ROOT_LEAN = ROOT / "formal" / "lean" / "HHS.lean"


def test_i055_contract_constructs_value_and_provenance_layers() -> None:
    contract = exactrat_value_contract()
    assert contract["quotient_constructed"] is True
    assert contract["operations_lifted"] == ("neg", "add", "mul")
    assert contract["pair_identity_is_value_identity"] is False
    assert contract["representative_recoverable_from_quotient"] is False
    assert contract["unreduced_pair_provenance_preserved_separately"] is True
    assert contract["runtime_arithmetic_changed"] is False
    assert contract["generic_hhs_commutation_authorized"] is False
    assert contract["vm81_mutation_authority"] == "VM81_ONLY"


def test_i055_lean_uses_real_setoid_and_quotient() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "def exactRatSetoid : Setoid ExactRat" in source
    assert "abbrev ExactRatValue := Quotient exactRatSetoid" in source
    assert "Quotient.liftOn" in source
    assert "Quotient.liftOn₂" in source
    assert "Quotient.sound" in source
    assert "Quotient.exact" in source


def test_i055_lifts_only_proven_congruent_operations() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "eqv_neg_congr" in source
    assert "eqv_add_congr" in source
    assert "eqv_mul_congr" in source


def test_i055_preserves_pair_provenance_separately() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "structure ExactRatProvenance" in source
    assert "half_pair_objects_distinct" in source
    assert "half_values_equal" in source
    assert "half_provenance_objects_distinct" in source
    assert "provenancePreservedSeparately := true" in source
    assert "quotientRepresentativeRecoverable := false" in source


def test_i055_has_no_upstream_mathlib_or_placeholders() -> None:
    source = LEAN.read_text(encoding="utf-8")
    lowered = source.lower()
    assert re.search(r"\bimport\s+mathlib\b", lowered) is None
    assert re.search(r"\bsorry\b", source, flags=re.IGNORECASE) is None
    assert re.search(r"\badmit\b", source, flags=re.IGNORECASE) is None


def test_i055_root_imports_value_module() -> None:
    root = ROOT_LEAN.read_text(encoding="utf-8")
    assert "import HHS.Mathlib.Rat.Value" in root
