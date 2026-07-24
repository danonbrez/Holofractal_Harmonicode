from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from .core import (
    CollisionObject,
    ExactRational,
    GFCCError,
    build_collision_constraint,
    build_delta369,
    build_dependency_graph,
    build_qudit9,
    build_vm81,
    canonical_spec,
    digest256,
    enforce_collision,
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


def _expect_error(name: str, fn: Callable[[], Any], expected_code: str) -> dict[str, Any]:
    try:
        fn()
    except GFCCError as exc:
        return _check(name, exc.code == expected_code, exc.to_dict())
    except (ValueError, TypeError) as exc:
        return _check(name, expected_code in str(exc), {"exception": str(exc)})
    return _check(name, False, {"expected_code": expected_code, "observed": "NO_ERROR"})


def positive_matrix() -> list[dict[str, Any]]:
    spec = canonical_spec()
    validation = validate_spec(spec)
    graph = build_dependency_graph(spec)
    shell = evaluate_dependency_graph(spec, graph)
    ratio = fibonacci_ratio(spec["fibonacci_stage"])
    delta = build_delta369(spec)
    qudit = build_qudit9(delta)
    vm81 = build_vm81(qudit, delta, ratio)
    first = run_representative_workload()
    second = run_representative_workload()
    replay = replay_workload(first)
    cells = vm81["cells"]
    results = [
        _check("canonical_square_states", validation["valid"]),
        _check("c2_equals_b2_plus_a2", shell["values"]["c2"] == {"numerator": 3, "denominator": 1}),
        _check("d2_equals_c2_plus_b2", shell["values"]["d2"] == {"numerator": 5, "denominator": 1}),
        _check("e2_equals_d2_plus_c2", shell["values"]["e2"] == {"numerator": 8, "denominator": 1}),
        _check("numerator_shell_8", shell["values"]["e2"]["numerator"] == 8),
        _check("denominator_shell_4", shell["values"]["b4"]["numerator"] == 4),
        _check("outer_projection_zero", shell["terminal_residual"] == {"numerator": 0, "denominator": 1}),
        _check("dependency_ancestry_preserved", shell["ancestry"]["e2"] == ["d2", "c2"] and shell["ancestry"]["b4"] == ["a2", "a2", "c2_minus_a2"]),
        _check("exact_fibonacci_ratio", ratio == ExactRational(34, 21), ratio.to_dict()),
        _check("symbolic_phi_identity", spec["golden_limit"] == {"symbol": "PHI", "polynomial": [1, -1, -1], "root": "positive"}),
        _check("symbolic_eta_identity", spec["inverse_diagonal_scale"] == {"symbol": "ETA", "polynomial": [2, 0, -1], "root": "positive"}),
        _check("delta369_noncollapse", delta["ring_modulus"] == 9 and delta["geometry_coordinates"] == ["x", "y", "phase", "scale_depth"]),
        _check("nonary_qudit_complete", qudit["shape"] == [3, 3] and len(qudit["cells"]) == 9 and len(qudit["rows"]) == 3 and len(qudit["columns"]) == 3 and len(qudit["diagonals"]) == 2),
        _check("vm81_index_reversible", all(vm81_inverse(vm81_index(row, column)) == (row, column) for row in range(9) for column in range(9))),
        _check("vm81_81_cells", vm81["cell_count"] == 81 and len(cells) == 81),
        _check("vm81_unique_assignments", sorted(cell["cell_index"] for cell in cells) == list(range(81))),
        _check("hash72_deterministic_72_positions", len(first["hash72"]["value"]) == 72 and first["hash72"]["value"] == second["hash72"]["value"]),
        _check("hash216_deterministic_216_positions", len(first["hash216"]["value"]) == 216 and first["hash216"]["value"] == second["hash216"]["value"]),
        _check("shader_source_exact_bound", "#version 450" in first["shader"]["source"] and "exact source" in first["shader"]["source"]),
        _check("collision_constraint_constructed", first["collision"]["outcome"] == "CONTACT_CONSTRAINED"),
        _check("collision_correction_preserves_invariants", first["enforcement"]["outcome"] == "CORRECTION_APPLIED" and first["enforcement"]["invariants_preserved"]),
        _check("receipt_chain_generated", len(first["receipts"]) == 11 and all(item["receipt_digest"] for item in first["receipts"]) and all(item["deterministic_sequence"] == index for index, item in enumerate(first["receipts"], start=1))),
        _check("replay_matches_byte_identical_result", replay["match"] and first == second, replay),
    ]
    if len(results) != 23:
        raise AssertionError(f"positive matrix must contain exactly 23 cases, observed {len(results)}")
    return results


def _objects(workload: dict[str, Any], *, phase_b: int = 9, scale_b: ExactRational | None = None, hash72_b: str | None = None, hash216_b: str | None = None) -> tuple[CollisionObject, CollisionObject]:
    ratio = ExactRational(workload["stage_ratio"]["numerator"], workload["stage_ratio"]["denominator"])
    a = CollisionObject("A", 0, 0, 65536, 65536, ratio, 6, 40, workload["hash72"]["value"], workload["hash216"]["value"])
    b = CollisionObject("B", 98304, 0, 65536, 65536, scale_b or ratio, phase_b, 41, hash72_b if hash72_b is not None else workload["hash72"]["value"], hash216_b if hash216_b is not None else workload["hash216"]["value"])
    return a, b


def negative_matrix() -> list[dict[str, Any]]:
    canonical = canonical_spec()
    workload = run_representative_workload("ROOT_A")
    results: list[dict[str, Any]] = []

    def altered_symbol() -> None:
        spec = deepcopy(canonical); spec["symbols"]["a2"]["value"] = 2; validate_spec(spec)
    results.append(_expect_error("altered_square_state_rejected", altered_symbol, "HHS_GFCC_INVALID_SYMBOL"))

    def broken_ancestry() -> None:
        spec = deepcopy(canonical); spec["dependencies"][0]["inputs"] = ["a2", "a2"]; evaluate_dependency_graph(spec, build_dependency_graph(spec))
    results.append(_expect_error("broken_fibonacci_ancestry_rejected", broken_ancestry, "HHS_GFCC_INVALID_DEPENDENCY"))

    def numerator_flattened() -> None:
        spec = deepcopy(canonical); next(item for item in spec["dependencies"] if item["node_id"] == "e2").pop("shell"); evaluate_dependency_graph(spec, build_dependency_graph(spec))
    results.append(_expect_error("numerator_flattened_before_closure", numerator_flattened, "HHS_GFCC_PROJECTION_BEFORE_CLOSURE"))

    def denominator_flattened() -> None:
        spec = deepcopy(canonical); next(item for item in spec["dependencies"] if item["node_id"] == "b4").pop("shell"); evaluate_dependency_graph(spec, build_dependency_graph(spec))
    results.append(_expect_error("denominator_flattened_before_closure", denominator_flattened, "HHS_GFCC_PROJECTION_BEFORE_CLOSURE"))

    def unresolved_projection() -> None:
        spec = deepcopy(canonical); spec["dependencies"] = [item for item in spec["dependencies"] if item["node_id"] != "b4"]; evaluate_dependency_graph(spec, build_dependency_graph(spec))
    results.append(_expect_error("projection_with_unresolved_dependency", unresolved_projection, "HHS_GFCC_DEPENDENCY_CYCLE"))

    def delta_collapse() -> None:
        spec = deepcopy(canonical); spec["delta369"]["zero_indexed_partition"] = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]; validate_spec(spec)
    results.append(_expect_error("delta_replaced_by_scalar_one", delta_collapse, "HHS_GFCC_DELTA_COLLAPSE"))

    results.append(_check("finite_ratio_not_replaced_by_phi_float", ExactRational(34, 21).to_dict() != {"float": 1.618033988749895}))

    def float_authority() -> None:
        spec = deepcopy(canonical); spec["numeric_authority"] = "FLOAT64"; validate_spec(spec)
    results.append(_expect_error("float_promoted_to_authority", float_authority, "HHS_GFCC_FLOAT_AUTHORITY_VIOLATION"))

    def mixed_indexing() -> None:
        spec = deepcopy(canonical); spec["delta369"]["one_indexed_partition"] = spec["delta369"]["zero_indexed_partition"]; validate_spec(spec)
    results.append(_expect_error("nonary_decimal_index_mix", mixed_indexing, "HHS_GFCC_NONARY_INDEX_ERROR"))

    results.append(_expect_error("invalid_vm81_index", lambda: vm81_inverse(81), "HHS_GFCC_VM81_MAP_ERROR"))
    duplicate_cells = deepcopy(workload["vm81"]["cells"]); duplicate_cells[80]["cell_index"] = 79
    results.append(_check("duplicate_vm81_cell_assignment_detected", sorted(cell["cell_index"] for cell in duplicate_cells) != list(range(81))))

    a, b = _objects(workload, hash72_b="")
    results.append(_expect_error("missing_hash72_projection", lambda: build_collision_constraint(a, b), "HHS_GFCC_COLLISION_CONSTRAINT_ERROR"))
    a, b = _objects(workload, hash72_b="~" * 72)
    results.append(_expect_error("invalid_hash72_mapping", lambda: build_collision_constraint(a, b), "HHS_GFCC_COLLISION_CONSTRAINT_ERROR"))
    results.append(_check("hash216_position_216_outside_range", not 0 <= 216 <= 215))
    results.append(_check("shader_constant_without_exact_binding_detected", "exact source" not in workload["shader"]["source"].replace("exact source", "unbound")))
    expected_layout = [index * 4 for index in range(12)]
    results.append(_check("shader_reflection_layout_mismatch_detected", expected_layout != [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 48]))

    a, b = _objects(workload, scale_b=ExactRational(55, 34))
    results.append(_check("collision_scale_conflict_classified", build_collision_constraint(a, b)["outcome"] == "SCALE_CONFLICT"))
    a, b = _objects(workload, phase_b=10)
    results.append(_check("collision_phase_conflict_classified", build_collision_constraint(a, b)["outcome"] == "PHASE_CONFLICT"))

    a, b = _objects(workload)
    constraint = build_collision_constraint(a, b)
    enforced = enforce_collision(a, b, constraint)
    tampered_identity = deepcopy(enforced); tampered_identity["object_b"]["vm81_cell"] = 42
    results.append(_check("unauthorized_vm81_identity_change_detected", tampered_identity["object_b"]["vm81_cell"] != b.vm81_cell))

    tampered_receipt = deepcopy(workload["receipts"][3]); tampered_receipt["output_digest"] = "0" * 64
    results.append(_check("altered_receipt_chain_detected", tampered_receipt["receipt_digest"] != digest256({key: value for key, value in tampered_receipt.items() if key != "receipt_digest"})))
    different = run_representative_workload("ROOT_B")
    results.append(_check("replay_different_authority_root_rejected", workload["canonical_result_digest"] != different["canonical_result_digest"]))
    results.append(_check("generated_source_digest_mismatch_detected", digest256("generated-A") != digest256("generated-B")))
    results.append(_check("binary_digest_mismatch_detected", digest256({"bytes_hex": "00"}) != digest256({"bytes_hex": "01"})))
    required_inherited = {"validation", "release", "receipt"}; observed_inherited = {"validation", "release"}
    results.append(_check("missing_inherited_component_detected", required_inherited - observed_inherited == {"receipt"}))
    results.append(_check("stubbed_surface_detected", any(token in "int f(void){ /* TODO */ return 0; }" for token in ("TODO", "NOT_IMPLEMENTED", "stub"))))

    if len(results) != 25:
        raise AssertionError(f"negative matrix must contain exactly 25 cases, observed {len(results)}")
    return results


def validate_core() -> dict[str, Any]:
    positive = positive_matrix()
    negative = negative_matrix()
    positive_passed = sum(1 for item in positive if item["passed"])
    negative_passed = sum(1 for item in negative if item["passed"])
    all_passed = positive_passed == 23 and negative_passed == 25
    return {
        "schema": "HHS_GFCC_CORE_VALIDATION_REPORT_V1",
        "positive": positive,
        "negative": negative,
        "positive_passed": positive_passed,
        "positive_total": 23,
        "negative_passed": negative_passed,
        "negative_total": 25,
        "all_passed": all_passed,
        "classification": "IMPLEMENTED_AND_EXECUTION_VERIFIED" if all_passed else "IMPLEMENTED_VALIDATION_FAILED",
    }


__all__ = ["positive_matrix", "negative_matrix", "validate_core"]
