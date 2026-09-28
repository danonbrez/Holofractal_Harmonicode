from __future__ import annotations

import json
from pathlib import Path

from hhs_runtime.hhs_pass220_multidimensional_constraint_manifold_v1 import (
    PHASE_CELLS,
    admit_multidimensional_constraint_state,
    dimensional_phase_ladder_witness,
    phase_index,
    phase_turn,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts/pass219/PASS_219_LOCAL_CIRCULAR_PHASE_FIBER_INVARIANT_1_0.md"
OUTPUT = ROOT / "evidence/pass219/local_circular_phase_fiber_wolfram_20260925_v1.output.json"
RECEIPT = ROOT / "evidence/pass219/local_circular_phase_fiber_wolfram_20260925_v1.receipt.json"


def test_existing_runtime_already_exposes_local_circular_phase_fibers() -> None:
    witness = dimensional_phase_ladder_witness()
    assert witness["one_dimensional_phase"]["carrier"] == "u^n"
    assert witness["two_dimensional_circular_projection"] == (
        "cos(theta_n)",
        "sin(theta_n)",
    )
    assert witness["three_dimensional_spherical_projection"] == (
        "r*sin(phi)*cos(theta_n)",
        "r*sin(phi)*sin(theta_n)",
        "r*cos(phi)",
    )
    assert witness["four_dimensional_toroidal_projection"] == (
        "Rxy*cos(theta_n)",
        "Rxy*sin(theta_n)",
        "Rzw*cos(phi_n)",
        "Rzw*sin(phi_n)",
    )
    assert witness["four_dimensional_phase_pairs"] == (("x", "y"), ("z", "w"))


def test_existing_runtime_phase_address_is_exactly_72_periodic() -> None:
    assert PHASE_CELLS == 72
    for index in range(-144, 145):
        assert phase_index(index + 72) == phase_index(index)
        assert phase_turn(index + 72) == phase_turn(index)


def test_existing_joint_admission_remains_authority_bounded() -> None:
    admitted = admit_multidimensional_constraint_state()
    assert admitted["ok"] is True
    assert all(admitted["checks"].values())
    assert admitted["floating_point_authority"] is False
    assert admitted["ordinary_scalar_flattening_authority"] is False
    assert admitted["canonical_hash72_mint_authority"] is False
    assert admitted["canonical_hash216_authority"] is False
    assert admitted["canonical_vm81_mutation_authority"] is False
    assert admitted["mutation_performed"] is False


def test_wolfram_receipt_closes_all_formalization_checks() -> None:
    output = json.loads(OUTPUT.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert output["Schema"] == "HHS_PASS219_LOCAL_CIRCULAR_PHASE_FIBER_WOLFRAM_PROOF_V1"
    assert output["TestsRun"] == 13
    assert output["TestsSucceeded"] == 13
    assert output["TestsFailed"] == 0
    assert output["AllSucceeded"] is True
    assert output["ProofSummarySHA256"] == (
        "0b6a39efe4bdf39f758a240717f79b11a21b2eacc204d2964fbce67bd35a1035"
    )
    assert receipt["proof"]["all_succeeded"] is True
    assert receipt["implementation_binding"]["existing_surface_only"] is True
    assert receipt["implementation_binding"]["new_phase_dynamics_implementation"] is False


def test_cross_scale_claim_is_circle_preserving_not_overclaimed_symplectic() -> None:
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "cross-scale circular-class preservation" in contract
    assert "conformally symplectic" in contract
    assert "fixed-scale phase transport" in contract
    assert "rho=1" in contract
    assert "arbitrary radius rescaling preserves an unrenormalized symplectic form" in contract


def test_native_order_and_projection_authority_remain_separate() -> None:
    contract = CONTRACT.read_text(encoding="utf-8")
    assert "does not commute or identify" in contract
    assert "xy" in contract and "yx" in contract
    assert "zw" in contract and "wz" in contract
    assert "Squaring is therefore a proof/readout channel" in contract
    assert "does not authorize scalar feedback" in contract

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["authority"] == {
        "floating_point_canonical_authority": False,
        "commutative_phase_reorder_authority": False,
        "vm81_mutation_authority": False,
        "hash72_mint_authority": False,
        "hash216_mint_authority": False,
        "canonical_persistence_authority": False,
    }


def test_formalization_adds_no_parallel_phase_runtime() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    binding = receipt["implementation_binding"]
    assert binding["module"] == (
        "hhs_runtime/hhs_pass220_multidimensional_constraint_manifold_v1.py"
    )
    assert binding["existing_surface_only"] is True
    assert binding["new_phase_dynamics_implementation"] is False
