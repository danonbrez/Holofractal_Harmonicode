from pathlib import Path
import pytest

from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import ContractError
from native_projects.hhs_bifurcation_calibration.hhs_pass082_1_offset_entangled_calibration_v1 import (
    default_workload,
    run,
    verify_replay,
    run_registry,
    U72_PHASE_OFFSET,
)

R = Path(__file__).resolve().parents[1]


def test_w11_offsets_0_and_1_close_after_inverse_normalization():
    v = verify_replay(R, default_workload(R, 2, "CONSECUTIVE", workload_id="W11:test"))
    x = v["initial"]
    assert v["deterministic_replay_verified"]
    assert len({r["raw_branch_root_hash72"] for r in x["branch_receipts"]}) == 2
    assert len({r["raw_closure_coordinate_root_hash72"] for r in x["branch_receipts"]}) == 2
    assert len({r["normalized_closure_coordinate_root_hash72"] for r in x["branch_receipts"]}) == 1
    assert x["closure_receipt"]["closure_relation"] == "EQUALITY_UNDER_DECLARED_OFFSET_TRANSFORM"


def test_w12_opposite_phase_0_and_36():
    x = run(R, default_workload(R, 2, "MAXIMUM_DISTANCE", workload_id="W12:test"))
    assert [r["offset_value"]["phase"] for r in x["branch_receipts"]] == [0, 36]
    assert x["closure_receipt"]["offset_inverses_verified"]
    assert x["closure_receipt"]["raw_branch_roots_distinct"]
    assert x["closure_receipt"]["normalized_closure_roots_identical"]


def test_w14_eight_coprime_stride_offsets_unique():
    x = run(R, default_workload(R, 8, "COPRIME_STRIDE", workload_id="W14:test", stride=5))
    offsets = [r["offset_value"]["phase"] for r in x["branch_receipts"]]
    assert offsets == [0, 5, 10, 15, 20, 25, 30, 35]
    assert len(set(offsets)) == 8


def test_w17_sixty_four_dense_offsets():
    x = run(R, default_workload(R, 64, "COPRIME_STRIDE", workload_id="W17:test", stride=5))
    assert len(x["branch_receipts"]) == 64
    assert len({r["offset_value"]["phase"] for r in x["branch_receipts"]}) == 64
    assert len({r["receipt_root_hash72"] for r in x["branch_receipts"]}) == 64
    assert x["closure_receipt"]["normalized_closure_roots_identical"]


def test_w16_combined_phase_and_cell_offsets_commit_order():
    a = run(R, default_workload(R, 4, "CONSECUTIVE", workload_id="W20:a", combined=True, transform_order=["PHASE", "CELL"]))
    b = run(R, default_workload(R, 4, "CONSECUTIVE", workload_id="W20:b", combined=True, transform_order=["CELL", "PHASE"]))
    assert [r["raw_branch_root_hash72"] for r in a["branch_receipts"]] != [r["raw_branch_root_hash72"] for r in b["branch_receipts"]]
    assert a["closure_receipt"]["normalized_closure_root_hash72"] == b["closure_receipt"]["normalized_closure_root_hash72"]


def test_duplicate_offset_rejected_when_uniqueness_required():
    w = default_workload(R, 2, "CONSECUTIVE")
    w["branches"][1]["offset"] = w["branches"][0]["offset"]
    with pytest.raises(ContractError, match="REJECT_NONUNIQUE_BRANCH_OFFSET"):
        run(R, w)


def test_out_of_domain_offset_rejected():
    w = default_workload(R, 2, "CONSECUTIVE")
    w["branches"][1]["offset"] = 72
    with pytest.raises(ContractError, match="REJECT_OFFSET_OUT_OF_DOMAIN"):
        run(R, w)


def test_missing_inverse_rejected():
    w = default_workload(R, 2, "CONSECUTIVE")
    w["branches"][0]["inverse_offset_transform_root_hash72"] = ""
    with pytest.raises(ContractError, match="REJECT_OFFSET_WITHOUT_INVERSE"):
        run(R, w)


def test_unwitnessed_offset_rejected():
    w = default_workload(R, 2, "CONSECUTIVE")
    del w["branches"][0]["offset_transform_root_hash72"]
    with pytest.raises(ContractError, match="REJECT_UNWITNESSED_OFFSET"):
        run(R, w)


def test_offset_outside_lease_rejected():
    w = default_workload(R, 2, "CONSECUTIVE")
    w["branches"][0]["lease_scope"] = "NATIVE_INVOCATION_ONLY"
    with pytest.raises(ContractError, match="REJECT_OFFSET_OPERATION_OUTSIDE_LEASE"):
        run(R, w)


def test_normalized_closure_failure_rejected():
    w = default_workload(R, 2, "CONSECUTIVE")
    w["force_normalized_closure_mismatch"] = True
    with pytest.raises(ContractError, match="REJECT_OFFSET_ENTANGLEMENT_CLOSURE_FAILURE"):
        run(R, w)


def test_replay_altered_offset_rejected():
    w = default_workload(R, 2, "CONSECUTIVE")
    w["alter_offset_on_replay"] = True
    with pytest.raises(ContractError, match="REJECT_OFFSET_REPLAY_MISMATCH"):
        verify_replay(R, w)


def test_native_float_remains_opaque_and_non_authoritative():
    x = run(R, default_workload(R, 2, "CONSECUTIVE"))
    assert all(r["native_float_bytes_opaque"] for r in x["branch_receipts"])
    assert x["closure_receipt"]["native_floating_output_non_authoritative"]


def test_full_registry_w11_to_w20():
    x = run_registry(R)
    assert x["noncommutative_order_distinct"]
    assert any(r["workload_id"].startswith("W18") and r["rejection_code"] == "REJECT_NONUNIQUE_BRANCH_OFFSET" for r in x["negative_results"])
    assert any(r["workload_id"].startswith("W19") and r["rejection_code"] == "REJECT_OFFSET_ENTANGLEMENT_CLOSURE_FAILURE" for r in x["negative_results"])
