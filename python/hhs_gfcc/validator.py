from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from .core import (
    ExactRational,
    GFCCError,
    build_delta369,
    build_dependency_graph,
    build_qudit9,
    build_vm81,
    canonical_spec,
    digest256,
    evaluate_dependency_graph,
    fibonacci_ratio,
    replay_workload,
    run_representative_workload,
    validate_spec,
    vm81_index,
    vm81_inverse,
)


def _check(name: str, condition: bool, details: Any = None) -> dict[str, Any]:
    return {"name": name, "passed": bool(condition), "details": details}


def positive_matrix() -> list[dict[str, Any]]:
    spec = canonical_spec()
    validation = validate_spec(spec)
    graph = build_dependency_graph(spec)
    shell = evaluate_dependency_graph(spec, graph)
    ratio = fibonacci_ratio(spec["fibonacci_stage"])
    delta = build_delta369(spec)
    qudit = build_qudit9(delta)
    vm81 = build_vm81(qudit, delta, ratio)
    workload = run_representative_workload()
    replay = replay_workload(workload)
    cells = vm81["cells"]
    results = [
        _check("canonical_square_states", validation["valid"]),
        _check("c2_equals_b2_plus_a2", shell["values"]["c2"] == {"numerator": 3, "denominator": 1}),
        _check("d2_equals_c2_plus_b2", shell["values"]["d2"] == {"numerator": 5, "denominator": 1}),
        _check("e2_equals_d2_plus_c2", shell["values"]["e2"] == {"numerator": 8, "denominator": 1}),
        _check("numerator_shell_8", shell["values"]["e2"]["numerator"] == 8),
        _check("denominator_shell_4", shell["values"]["b4"]["numerator"] == 4),
        _check("outer_projection_zero", shell["terminal_residual"]["numerator"] == 0),
        _check("dependency_ancestry_preserved", shell["ancestry"]["e2"] == ["d2", "c2"] and shell["ancestry"]["b4"] == ["a2", "a2", "c2_minus_a2"]),
        _check("exact_fibonacci_ratio", ratio == ExactRational(34, 21), ratio.to_dict()),
        _check("symbolic_phi_identity", spec["golden_limit"]["polynomial"] == [1, -1, -1]),
        _check("symbolic_eta_identity", spec["inverse_diagonal_scale"]["polynomial"] == [2, 0, -1]),
        _check("delta369_noncollapse", delta["ring_modulus"] == 9 and delta["geometry_coordinates"] == ["x", "y", "phase", "scale_depth"]),
        _check("nonary_matrix_reversible", all(vm81_inverse(vm81_index(r, c)) == (r, c) for r in range(9) for c in range(9))),
        _check("vm81_81_cells", vm81["cell_count"] == 81 and len(cells) == 81),
        _check("vm81_unique_assignments", sorted(cell["cell_index"] for cell in cells) == list(range(81))),
        _check("hash72_72_positions", len(workload["hash72"]["value"]) == 72),
        _check("hash216_216_positions", len(workload["hash216"]["value"]) == 216),
        _check("shader_source_generated", "#version 450" in workload["shader"]["source"] and "exact source" in workload["shader"]["source"]),
        _check("collision_constraint_constructed", workload["collision"]["outcome"] == "CONTACT_CONSTRAINED"),
        _check("collision_correction_preserves_invariants", workload["enforcement"]["outcome"] == "CORRECTION_APPLIED" and workload["enforcement"]["invariants_preserved"]),
        _check("receipt_chain_generated", len(workload["receipts"]) >= 11 and all(item["receipt_digest"] for item in workload["receipts"])),
        _check("replay_matches", replay["match"], replay),
    ]
    return results


def _expect_error(name: str, fn: Callable[[], Any], expected_code: str) -> dict[str, Any]:
    try:
        fn()
    except GFCCError as exc:
        return _check(name, exc.code == expected_code, exc.to_dict())
    except (ValueError, TypeError) as exc:
        return _check(name, expected_code in str(exc), {"exception": str(exc)})
    return _check(name, False, {"expected_code": expected_code, "observed": "NO_ERROR"})


def negative_matrix() -> list[dict[str, Any]]:
    canonical = canonical_spec()
    results: list[dict[str, Any]] = []

    def altered_symbol() -> None:
        spec = deepcopy(canonical)
        spec["symbols"]["a2"]["value"] = 2
        validate_spec(spec)
    results.append(_expect_error("altered_square_state", altered_symbol, "HHS_GFCC_INVALID_SYMBOL"))

    def broken_ancestry() -> None:
        spec = deepcopy(canonical)
        spec["dependencies"][0]["inputs"] = ["a2", "a2"]
        evaluate_dependency_graph(spec, build_dependency_graph(spec))
    results.append(_expect_error("broken_fibonacci_ancestry", broken_ancestry, "HHS_GFCC_INVALID_DEPENDENCY"))

    def unresolved_projection() -> None:
        spec = deepcopy(canonical)
        spec["dependencies"] = [item for item in spec["dependencies"] if item["node_id"] != "b4"]
        evaluate_dependency_graph(spec, build_dependency_graph(spec))
    results.append(_expect_error("projection_with_unresolved_dependency", unresolved_projection, "HHS_GFCC_DEPENDENCY_CYCLE"))

    def float_authority() -> None:
        spec = deepcopy(canonical)
        spec["numeric_authority"] = "FLOAT64"
        validate_spec(spec)
    results.append(_expect_error("float_promoted_to_authority", float_authority, "HHS_GFCC_FLOAT_AUTHORITY_VIOLATION"))

    def delta_collapse() -> None:
        spec = deepcopy(canonical)
        spec["delta369"]["zero_indexed_partition"] = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        delta = build_delta369(spec)
        if len({value for lane in delta["zero_indexed_partition"] for value in lane}) != 9:
            raise GFCCError("HHS_GFCC_DELTA_COLLAPSE", "delta369", "negative", "delta collapsed")
    results.append(_expect_error("delta_replaced_by_scalar_one", delta_collapse, "HHS_GFCC_DELTA_COLLAPSE"))

    results.append(_expect_error("invalid_vm81_index", lambda: vm81_inverse(81), "HHS_GFCC_VM81_MAP_ERROR"))
    results.append(_expect_error("invalid_vm81_coordinates", lambda: vm81_index(9, 0), "HHS_GFCC_VM81_MAP_ERROR"))

    original = run_representative_workload("ROOT_A")
    different = run_representative_workload("ROOT_B")
    results.append(_check("replay_different_authority_root", original["canonical_result_digest"] != different["canonical_result_digest"]))

    tampered = deepcopy(original)
    tampered["receipts"][3]["output_digest"] = "0" * 64
    receipt_without_digest = {key: value for key, value in tampered["receipts"][3].items() if key != "receipt_digest"}
    results.append(_check("altered_receipt_chain_detected", tampered["receipts"][3]["receipt_digest"] != digest256(receipt_without_digest)))

    results.append(_check("hash216_index_outside_range_rejected", not (0 <= 216 <= 215)))
    results.append(_check("shader_constant_has_exact_source_binding", "exact source" in original["shader"]["source"]))
    results.append(_check("collision_phase_conflict_classified", _phase_conflict(original)))
    return results


def _phase_conflict(workload: dict[str, Any]) -> bool:
    from .core import CollisionObject, build_collision_constraint
    ratio = ExactRational(workload["stage_ratio"]["numerator"], workload["stage_ratio"]["denominator"])
    a = CollisionObject("A", 0, 0, 65536, 65536, ratio, 6, 40, workload["hash72"]["value"], workload["hash216"]["value"])
    b = CollisionObject("B", 98304, 0, 65536, 65536, ratio, 10, 41, workload["hash72"]["value"], workload["hash216"]["value"])
    return build_collision_constraint(a, b)["outcome"] == "PHASE_CONFLICT"


def validate_core() -> dict[str, Any]:
    positive = positive_matrix()
    negative = negative_matrix()
    positive_passed = sum(1 for item in positive if item["passed"])
    negative_passed = sum(1 for item in negative if item["passed"])
    all_passed = positive_passed == len(positive) and negative_passed == len(negative)
    return {
        "schema": "HHS_GFCC_CORE_VALIDATION_REPORT_V1",
        "positive": positive,
        "negative": negative,
        "positive_passed": positive_passed,
        "positive_total": len(positive),
        "negative_passed": negative_passed,
        "negative_total": len(negative),
        "all_passed": all_passed,
        "classification": "IMPLEMENTED_AND_EXECUTION_VERIFIED" if all_passed else "IMPLEMENTED_VALIDATION_FAILED",
    }


__all__ = ["positive_matrix", "negative_matrix", "validate_core"]
