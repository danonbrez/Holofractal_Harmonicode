"""Tests for Pass 219 exact constraint/evolution optimizer v1."""
from __future__ import annotations

import copy
import json

from hhs_spi_constraint_evolution_optimizer_v1 import (
    LIFECYCLE,
    SPIConstraintEvolutionOptimizerError,
    VM5184_ADDRESS_COUNT,
    build_learning_candidate,
    decode_vm5184_address,
    optimize_learning_candidates,
    reference_optimizer_cycle,
    verify_learning_candidate,
    vm5184_address,
)


def _candidate(candidate_id: str, *, branches: int, reuse: int, semantic: str = ""):
    return build_learning_candidate(
        candidate_id=candidate_id,
        tensor_kind="LO_SHU",
        stage_index=3,
        hydration_lane=2,
        cell_index=17,
        operation_index=23,
        branch_count=branches,
        reusable_branch_count=reuse,
        symbolic_parameter_state=f"PARAM:{candidate_id}",
        semantic_label=semantic,
    )


def test_vm5184_address_round_trip_is_exact():
    assert VM5184_ADDRESS_COUNT == 5184
    for cell, op in ((0, 0), (17, 23), (80, 63)):
        address = vm5184_address(cell, op)
        assert decode_vm5184_address(address) == (cell, op)


def test_candidate_closes_first_three_lifecycle_gates():
    candidate = _candidate("A", branches=32, reuse=20)
    report = verify_learning_candidate(candidate)
    assert report["ok"] is True
    assert candidate["lifecycle"]["FORMALIZE"] == "PASS"
    assert candidate["lifecycle"]["PROVE"] == "PASS"
    assert candidate["lifecycle"]["IMPLEMENT"] == "PASS"
    assert candidate["lifecycle"]["OPTIMIZE"] == "PENDING_SELECTION"
    assert candidate["authority"]["candidate_only"] is True
    assert candidate["authority"]["canonical_admission"] is False


def test_false_or_broken_candidate_cannot_traverse_full_cycle():
    candidate = _candidate("BROKEN", branches=10, reuse=4)
    broken = copy.deepcopy(candidate)
    broken["lifecycle"]["PROVE"] = "FAIL"
    report = verify_learning_candidate(broken)
    assert report["ok"] is False
    try:
        optimize_learning_candidates([broken])
    except SPIConstraintEvolutionOptimizerError as exc:
        assert "NO_CANDIDATE_SURVIVED" in str(exc)
    else:
        raise AssertionError("broken proof candidate unexpectedly survived optimizer gates")


def test_optimizer_minimizes_unresolved_exact_work_and_maximizes_reuse():
    a = _candidate("A", branches=30, reuse=20)  # unresolved 10
    b = _candidate("B", branches=40, reuse=31)  # unresolved 9
    c = _candidate("C", branches=50, reuse=41)  # unresolved 9, greater reuse => wins
    receipt = optimize_learning_candidates([a, b, c])
    assert receipt["selected_candidate_id"] == "C"
    assert receipt["selected_score"] == {
        "unresolved_branch_count": 9,
        "reusable_branch_count": 41,
    }


def test_semantic_label_is_downstream_and_has_no_selection_authority():
    a = _candidate("A", branches=20, reuse=10, semantic="preferred by narrative")
    b = _candidate("B", branches=20, reuse=11, semantic="ordinary")
    receipt = optimize_learning_candidates([a, b])
    assert receipt["selected_candidate_id"] == "B"
    assert receipt["semantic_label_used_for_selection"] is False


def test_float_objective_authority_fails_closed():
    try:
        build_learning_candidate(
            candidate_id="FLOAT",
            tensor_kind="LO_SHU",
            stage_index=0,
            hydration_lane=0,
            cell_index=0,
            operation_index=0,
            branch_count=10.0,
            reusable_branch_count=4,
            symbolic_parameter_state="FLOAT",
        )
    except SPIConstraintEvolutionOptimizerError as exc:
        assert "EXACT_INTEGER_REQUIRED" in str(exc)
    else:
        raise AssertionError("float work authority unexpectedly accepted")


def test_receipt_tampering_is_detected():
    candidate = _candidate("TAMPER", branches=12, reuse=2)
    tampered = copy.deepcopy(candidate)
    tampered["work"]["reusable_branch_count"] = 8
    assert verify_learning_candidate(tampered)["ok"] is False


def test_reference_cycle_reaches_projection_canonization_and_iteration_seed():
    receipt = reference_optimizer_cycle()
    assert receipt["lifecycle_order"] == list(LIFECYCLE)
    assert receipt["selected_candidate_id"] == "SUDOKU-S4-REUSE"
    assert receipt["lifecycle"]["OPTIMIZE"] == "PASS"
    assert receipt["lifecycle"]["CANONIZE"] == "PROJECTION_RECEIPT_ELIGIBLE"
    assert receipt["lifecycle"]["ITERATE"] == "NEXT_CYCLE_SEED_EMITTED"
    assert receipt["canonization"]["repository_main_canonized"] is False
    assert receipt["iteration_seed"]["next_cycle"] == "FORMALIZE"
    assert receipt["empirical_speedup_claimed"] is False


def test_reference_cycle_preserves_authority_boundary():
    receipt = reference_optimizer_cycle()
    authority = receipt["authority"]
    assert authority == {
        "candidate_only": True,
        "canonical_admission": False,
        "vm81_mutation": False,
        "canonical_hash72": False,
        "canonical_hash216": False,
        "canonical_persistence": False,
        "floating_point": False,
    }
    assert receipt["knowledge_graph"]["hash216_vector_store_reference_eligible"] is True
    assert receipt["knowledge_graph"]["canonical_hash216_minted"] is False


def test_optimizer_receipt_is_deterministic():
    assert reference_optimizer_cycle() == reference_optimizer_cycle()


def main() -> None:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    results = []
    for test in tests:
        try:
            test()
            results.append({"name": test.__name__, "passed": True})
        except Exception as exc:
            results.append({"name": test.__name__, "passed": False, "error": f"{type(exc).__name__}: {exc}"})
    report = {
        "schema": "HHS_SPI_CONSTRAINT_EVOLUTION_OPTIMIZER_TEST_REPORT_V1",
        "passed": sum(1 for result in results if result["passed"]),
        "failed": sum(1 for result in results if not result["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
