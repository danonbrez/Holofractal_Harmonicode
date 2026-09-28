from __future__ import annotations

from pathlib import Path
import re

from hhs_runtime.hhs_pass220_i052_native_mathlib_universal_v1 import (
    THEOREMS,
    universal_promotion_contract,
)

ROOT = Path(__file__).resolve().parents[2]
LEAN = ROOT / "formal" / "lean" / "HHS" / "Mathlib" / "Algebra" / "Universal.lean"


def test_i052_contract_promotes_only_nat_and_int() -> None:
    contract = universal_promotion_contract()
    assert contract["nat_semiring_universal"] is True
    assert contract["int_ring_universal"] is True
    assert contract["exact_rat_ring_universal"] is False
    assert contract["runtime_arithmetic_changed"] is False
    assert contract["ordered_operands_required"] is True
    assert contract["generic_commutation_authorized"] is False
    assert contract["commutativity_theorems_exported"] is False
    assert contract["vm81_mutation_authority"] == "VM81_ONLY"


def test_i052_theorem_manifest_is_complete_and_unique() -> None:
    names = tuple(item.theorem for item in THEOREMS)
    assert len(names) == 18
    assert len(set(names)) == len(names)
    assert {item.carrier for item in THEOREMS} == {"Nat", "Int"}
    assert all("comm" not in item.law for item in THEOREMS)


def test_i052_lean_source_has_no_upstream_mathlib_or_placeholders() -> None:
    source = LEAN.read_text(encoding="utf-8")
    lowered = source.lower()
    assert re.search(r"\bimport\s+mathlib\b", lowered) is None
    assert re.search(r"\bsorry\b", source, flags=re.IGNORECASE) is None
    assert re.search(r"\badmit\b", source, flags=re.IGNORECASE) is None


def test_i052_does_not_export_commutativity_surface() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "add_comm" not in source
    assert "mul_comm" not in source
    assert "implicitHHSCommutationAuthorized := false" in source


def test_i052_preserves_i050_certificate_boundary() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "i050_nat_descriptor_remains_runtime_certificate" in source
    assert "i050_int_descriptor_remains_runtime_certificate" in source
    assert "universalProofClosed = false" in source
