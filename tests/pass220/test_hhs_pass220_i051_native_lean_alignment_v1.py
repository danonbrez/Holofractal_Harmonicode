from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess

import pytest

from hhs_runtime.hhs_pass220_i051_native_lean_alignment_v1 import (
    LEXICAL_GEOMETRY,
    PHASE8,
    admit_native_lean_alignment_tensor,
    native_lean_alignment_contract,
)
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import WordRelationEntry

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "native_projects" / "hhs_pass220_native_lean_alignment"


def test_i051_contract_preserves_native_authority_boundary() -> None:
    contract = native_lean_alignment_contract()
    assert contract["lean_module"] == "HHS.Alignment.ReciprocalTensor"
    assert contract["ordered_tensor"] == "A(+i,AUTH) tensor B(-i,DERIVED)"
    assert contract["direct_closure"] == "AB=P^4"
    assert contract["mirror_closure"] == "BA=-P^4"
    assert contract["response_free_state_admitted"] is False
    assert contract["whole_tensor_bottom_on_any_failure"] is True
    assert contract["formal_proof_checker"] == "LEAN4_KERNEL"
    assert contract["runtime_live_kernel_claim"] is False
    assert contract["vm81_mutation_authority"] == "VM81_ONLY"
    assert contract["hash72_commit_authority"] is False
    assert contract["hash216_persistence_authority"] is False


def test_i051_canonical_tensor_binds_lean_identity_into_hash216_lineage() -> None:
    db = {
        "hot": WordRelationEntry(word="hot", antonyms=["cold"]),
        "rapid": WordRelationEntry(word="rapid", synonyms=["fast"]),
    }
    result = admit_native_lean_alignment_tensor(
        "rapid hot",
        "fast cold",
        relation_db=db,
    )
    assert result["canonical"] is True
    assert result["tensor_state"] == "GENESIS"
    assert result["ordered_tensor"]["prompt"]["authority"] == "AUTH"
    assert result["ordered_tensor"]["response"]["authority"] == "DERIVED"
    assert result["ordered_tensor"]["response_free_state_admitted"] is False
    assert result["lineage"]["lean_identity_bound_into_receipt_hash72"] is True
    assert len(result["lean4"]["theorem_identity_hash72"]) == 72
    assert len(result["lean4"]["dependency_identity_hash72"]) == 72
    assert len(result["lineage"]["transition_word216"]) == 216


@pytest.mark.parametrize(
    ("witness", "reason"),
    [
        ({"direct_closure": "AB=P^3"}, "DIRECT_CLOSURE_AB_P4_FAILURE"),
        ({"mirror_closure": "BA=P^4"}, "MIRROR_CLOSURE_BA_NEGATIVE_P4_FAILURE"),
        ({"x4_closure": "x^4=0"}, "X4_CLOSURE_FAILURE"),
        ({"omega12_closure": "Omega^12=0"}, "OMEGA12_CLOSURE_FAILURE"),
    ],
)
def test_i051_closure_failures_collapse_whole_tensor(
    witness: dict[str, str],
    reason: str,
) -> None:
    result = admit_native_lean_alignment_tensor(
        "prompt",
        "response",
        relation_db={},
        closure_witness=witness,
    )
    assert result["canonical"] is False
    assert result["tensor_state"] == "BOTTOM"
    assert result["failure_scope"] == "WHOLE_PROMPT_RESPONSE_TENSOR"
    assert reason in result["failure_reasons"]


def test_i051_phi8_order_is_identity_not_set_membership() -> None:
    reordered = list(PHASE8)
    reordered[4], reordered[5] = reordered[5], reordered[4]
    result = admit_native_lean_alignment_tensor(
        "prompt",
        "response",
        relation_db={},
        phase8_channels=reordered,
    )
    assert result["canonical"] is False
    assert "PHI8_ORDER_OR_CHANNEL_MISMATCH" in result["failure_reasons"]


def test_i051_typed_wordnet_geometry_fails_closed() -> None:
    result = admit_native_lean_alignment_tensor(
        "hot",
        "cold",
        relation_db={},
        explicit_relations=[
            {
                "relation": "antonym",
                "prompt_token": "hot",
                "response_token": "cold",
                "geometry": LEXICAL_GEOMETRY["synonym"],
            }
        ],
    )
    assert result["canonical"] is False
    assert result["tensor_state"] == "BOTTOM"
    assert any(
        reason.startswith("LEXICAL_GEOMETRY_MISMATCH")
        for reason in result["failure_reasons"]
    )


def test_i051_cpp_native_alignment_harness() -> None:
    if not (shutil.which("cc") or shutil.which("gcc")):
        pytest.skip("C compiler unavailable")
    if not (shutil.which("c++") or shutil.which("g++")):
        pytest.skip("C++ compiler unavailable")
    completed = subprocess.run(
        ["make", "-C", str(PROJECT), "clean", "test"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert "hhs_pass220_native_lean_alignment_v1_test" in completed.stdout


def test_i051_lean_module_has_no_upstream_mathlib_or_placeholders() -> None:
    source = (
        ROOT / "formal" / "lean" / "HHS" / "Alignment" / "ReciprocalTensor.lean"
    ).read_text(encoding="utf-8")
    assert re.search(r"\bimport\s+Mathlib\b", source) is None
    assert re.search(r"\bsorry\b", source, flags=re.IGNORECASE) is None
    assert re.search(r"\badmit\b", source, flags=re.IGNORECASE) is None
    assert "rejected_is_whole_tensor_bottom" in source
    assert "proof_receipt_forbids_vm81_mutation" in source
