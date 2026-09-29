from __future__ import annotations

from pathlib import Path
import re

from hhs_runtime.hhs_pass220_i060_native_lean_exactrat_value_algebra_v1 import (
    LEAN_DEPENDENCIES,
    LEAN_THEOREMS,
    REPOSITORY_LINEAGE,
    lean_identity_receipt,
)

ROOT = Path(__file__).resolve().parents[2]
LEAN = ROOT / "formal" / "lean" / "HHS" / "Mathlib" / "Rat" / "ValueAlgebra.lean"
ROOT_LEAN = ROOT / "formal" / "lean" / "HHS.lean"


def test_i060_closes_remaining_ordered_value_algebra_laws() -> None:
    source = LEAN.read_text(encoding="utf-8")
    for theorem in (
        "pair_add_assoc_eqv",
        "pair_mul_assoc_eqv",
        "pair_left_distrib_eqv",
        "pair_right_distrib_eqv",
        "value_add_assoc",
        "value_mul_assoc",
        "value_left_distrib",
        "value_right_distrib",
    ):
        assert f"theorem {theorem}" in source
    assert "addAssocUniversal := true" in source
    assert "mulAssocUniversal := true" in source
    assert "leftDistribUniversal := true" in source
    assert "rightDistribUniversal := true" in source


def test_i060_does_not_promote_commutation_or_rewrite_provenance() -> None:
    source = LEAN.read_text(encoding="utf-8")
    assert "addCommutationPromoted := false" in source
    assert "mulCommutationPromoted := false" in source
    assert "genericHHSCommutationAuthorized := false" in source
    assert "provenanceObjectsRewritten := false" in source


def test_i060_identity_receipt_is_hash72_valid_and_deterministic() -> None:
    receipt_a = lean_identity_receipt()
    receipt_b = lean_identity_receipt()
    assert receipt_a == receipt_b
    assert receipt_a["theorem_identity_valid"] is True
    assert receipt_a["dependency_identity_valid"] is True
    assert len(receipt_a["theorem_identity_hash72"]) == 72
    assert len(receipt_a["dependency_identity_hash72"]) == 72
    assert receipt_a["theorems"] == list(LEAN_THEOREMS)
    assert receipt_a["dependencies"] == list(LEAN_DEPENDENCIES)
    assert receipt_a["repository_lineage"] == list(REPOSITORY_LINEAGE)


def test_i060_receipt_is_intrinsic_i061_input_not_post_hoc_attachment() -> None:
    receipt = lean_identity_receipt()
    assert receipt["intrinsic_successor_binding_required"] is True
    assert receipt["intended_successor"] == (
        "PASS_220_I061_UNIFIED_SCIENTIFIC_PHYSICS_SYNTHESIS"
    )
    assert receipt["post_hoc_proof_attachment_satisfies_successor"] is False
    assert receipt["runtime_claims_live_kernel_execution"] is False


def test_i060_preserves_authority_boundary() -> None:
    receipt = lean_identity_receipt()
    assert receipt["runtime_arithmetic_changed"] is False
    assert receipt["generic_hhs_commutation_authorized"] is False
    assert receipt["vm81_mutation_authority"] == "VM81_ONLY"
    assert receipt["hash72_commit_authority"] is False
    assert receipt["hash216_persistence_authority"] is False


def test_i060_lean_source_has_no_upstream_mathlib_or_placeholders() -> None:
    source = LEAN.read_text(encoding="utf-8")
    lowered = source.lower()
    assert re.search(r"\bimport\s+mathlib\b", lowered) is None
    assert re.search(r"\bsorry\b", source, flags=re.IGNORECASE) is None
    assert re.search(r"\badmit\b", source, flags=re.IGNORECASE) is None


def test_i060_root_imports_value_algebra_module() -> None:
    root = ROOT_LEAN.read_text(encoding="utf-8")
    assert "import HHS.Mathlib.Rat.ValueAlgebra" in root
