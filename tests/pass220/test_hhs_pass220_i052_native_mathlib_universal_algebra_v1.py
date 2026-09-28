from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
LEAN = ROOT / "formal" / "lean" / "HHS" / "Mathlib" / "Algebra" / "Universal.lean"
RUNTIME_LEAN = ROOT / "formal" / "lean" / "HHS" / "Mathlib" / "Algebra" / "Native.lean"
ROOT_LEAN = ROOT / "formal" / "lean" / "HHS.lean"
CONTRACT = ROOT / "contracts" / "pass220" / "PASS_220_I052_NATIVE_MATHLIB_UNIVERSAL_ALGEBRA_V1.json"


def test_i052_contract_scope_and_authority() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["schema"] == "HHS_PASS_220_I052_NATIVE_MATHLIB_UNIVERSAL_ALGEBRA_V1"
    assert contract["universal_carriers"] == ["Nat", "Int"]
    assert contract["exact_rat_universal_closure_claimed"] is False
    assert contract["complete_mathlib_rebuild_claimed"] is False
    assert contract["implicit_commutation_authorized"] is False
    assert contract["vm81_mutation_authority"] is False
    assert contract["hash72_commit_authority"] is False
    assert contract["hash216_persistence_authority"] is False


def test_i052_lean_source_has_no_upstream_mathlib_or_placeholders() -> None:
    source = LEAN.read_text(encoding="utf-8")
    lowered = source.lower()
    assert re.search(r"\bimport\s+mathlib\b", lowered) is None
    assert re.search(r"\bsorry\b", source, flags=re.IGNORECASE) is None
    assert re.search(r"\badmit\b", source, flags=re.IGNORECASE) is None


def test_i052_promotes_exact_i050_laws_for_nat_and_int() -> None:
    source = LEAN.read_text(encoding="utf-8")
    required = (
        "Nat.add_assoc",
        "Nat.zero_add",
        "Nat.add_zero",
        "Nat.mul_assoc",
        "Nat.one_mul",
        "Nat.mul_one",
        "Nat.mul_add",
        "Nat.add_mul",
        "Int.add_assoc",
        "Int.zero_add",
        "Int.add_zero",
        "Int.mul_assoc",
        "Int.one_mul",
        "Int.mul_one",
        "Int.mul_add",
        "Int.add_mul",
        "Int.add_right_neg",
    )
    for theorem_name in required:
        assert theorem_name in source


def test_i052_does_not_export_commutativity_as_promoted_law() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "Nat.add_comm" not in source
    assert "Nat.mul_comm" not in source
    assert "Int.add_comm" not in source
    assert "Int.mul_comm" not in source
    assert "implicitCommutationAuthorized : Bool := false" in source


def test_i052_preserves_i050_runtime_evidence_boundary() -> None:
    source = RUNTIME_LEAN.read_text(encoding="utf-8")
    assert "universalProofClosed := false" in source
    promotion = LEAN.read_text(encoding="utf-8")
    assert "runtimeEvidenceReclassifiedAsUniversal : Bool := false" in promotion


def test_i052_root_imports_universal_proof_module() -> None:
    root = ROOT_LEAN.read_text(encoding="utf-8")
    assert "import HHS.Mathlib.Algebra.Universal" in root
