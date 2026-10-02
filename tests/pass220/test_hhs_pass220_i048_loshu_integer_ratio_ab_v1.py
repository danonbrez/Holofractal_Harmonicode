from __future__ import annotations
import copy, json
from pathlib import Path
import pytest
from hhs_runtime.hhs_pass220_i048_loshu_integer_ratio_ab_v1 import (
    EXPECTED_CELL_LABELS, EXPECTED_RESIDUES, GLOBAL_INVARIANT, RECIPROCAL_TENSOR,
    Pass220I048Error, geometry_payload, lo_shu_cell_label, run_ab_cycle,
    validate_contract, verify_wolfram_receipt,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts/pass220/PASS_220_I048_LOSHU_INTEGER_RATIO_AB_V1.json"
WOLFRAM = ROOT / "evidence/pass220/pass220_i048_loshu_integer_ratio_ab_wolfram_v1.output.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_exact_geometry_and_lo_shu_zero_mapping():
    payload = geometry_payload()
    assert payload["base9_residues"] == {k: list(v) for k, v in EXPECTED_RESIDUES.items()}
    assert payload["lo_shu_cell_labels"] == {k: list(v) for k, v in EXPECTED_CELL_LABELS.items()}
    assert lo_shu_cell_label(0) == 9
    assert payload["global_invariant_verbatim"] == GLOBAL_INVARIANT
    assert payload["reciprocal_tensor_verbatim"] == RECIPROCAL_TENSOR


def test_ab_hydration_is_exact_and_reduces_repeated_mod_work():
    receipt = run_ab_cycle(81)
    assert receipt["exact_payload_equal"]
    assert receipt["arm_A"]["payload_sha256"] == receipt["arm_B"]["payload_sha256"]
    assert receipt["arm_A"]["mod_operations"] == 1944
    assert receipt["arm_B"]["mod_operations"] == 24
    assert receipt["mod_operation_reduction"] == 1920
    assert receipt["wall_clock_speed_claimed"] is False


def test_wolfram_receipt_is_frozen_28_of_28():
    receipt = verify_wolfram_receipt(_load(WOLFRAM))
    assert receipt["status"] == "PASS"
    assert receipt["check_count"] == receipt["pass_count"] == 28


def test_contract_closes_candidate_only():
    receipt = validate_contract(_load(CONTRACT), _load(WOLFRAM))
    assert receipt["status"] == "PASS"
    assert receipt["candidate_only"]
    assert not receipt["ab"]["canonical_vm81_mutation_authority"]
    assert not receipt["ab"]["canonical_hash216_authority"]


def test_constructor_mutation_is_rejected():
    mutated = {
        "A": (1,2,3), "B": (2,3,5), "C": (3,5,8), "D": (4,7,12),
        "E": (5,8,13), "F": (3,6,9), "G": (2,4,6), "H": (7,11,18),
    }
    with pytest.raises(Pass220I048Error, match="integer-ratio geometry failed"):
        geometry_payload(mutated)


def test_float_ingress_is_rejected():
    mutated = {
        "A": (1,2,3.0), "B": (2,3,5), "C": (3,5,8), "D": (4,7,11),
        "E": (5,8,13), "F": (3,6,9), "G": (2,4,6), "H": (7,11,18),
    }
    with pytest.raises(Pass220I048Error, match="whole integers only"):
        geometry_payload(mutated)


def test_wolfram_hash_drift_is_rejected():
    receipt = copy.deepcopy(_load(WOLFRAM))
    receipt["material_sha256"] = "0" * 64
    with pytest.raises(Pass220I048Error, match="material identity mismatch"):
        verify_wolfram_receipt(receipt)
