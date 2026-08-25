from __future__ import annotations

from pathlib import Path

from hhs_runtime.core_sandbox.hhs_pass219_combined_equation_optimizer_1_21_8 import (
    COMBINED_PATH,
    PROJECTION_SOURCE,
)
from hhs_runtime.core_sandbox.hhs_pass219_proof_preserving_optimizer_1_21_12 import (
    AUTHORITY_QUALIFIER,
    CLASSIFICATION,
    EXPECTED_GATE_OFFSETS,
    EXPECTED_PASS159_DISTINCTION,
    activate_proof_preserving_optimization,
)


def _expect_value_error(fn, expected: str) -> None:
    try:
        fn()
    except ValueError as exc:
        assert expected in str(exc)
    else:
        raise AssertionError(f"expected ValueError containing {expected!r}")


def test_read_only_optimization_is_activated_only_inside_proven_boundary() -> None:
    result = activate_proof_preserving_optimization()
    assert result["ok"] is True
    assert result["classification"] == CLASSIFICATION
    assert result["authority_qualifier"] == AUTHORITY_QUALIFIER
    assert result["read_only_optimization_activated"] is True
    assert result["source_binding"]["expected_gate_offsets"] == list(EXPECTED_GATE_OFFSETS)
    assert result["source_binding"]["pass159_whole_expression_distinction_required"] == EXPECTED_PASS159_DISTINCTION


def test_denominator_cse_uses_one_value_key_but_keeps_two_witnesses() -> None:
    cse = activate_proof_preserving_optimization()["denominator_cse"]
    assert cse["activation"] == "AUTHORIZED_READ_ONLY_VALUE_REUSE"
    assert cse["baseline_value_evaluations"] == 2
    assert cse["memoized_value_evaluations"] == 1
    assert cse["value_evaluations_avoided"] == 1
    assert cse["memoized_value_nodes"] == 1
    assert cse["source_occurrence_witness_count"] == 2
    assert len(cse["occurrence_witnesses"]) == 2

    first, second = cse["occurrence_witnesses"]
    assert first["source_offset"] < second["source_offset"]
    assert first["diagnostic_occurrence_sha256"] != second["diagnostic_occurrence_sha256"]
    assert first["memoized_value_key_sha256"] == second["memoized_value_key_sha256"]
    assert cse["receipt_count_reduction_authorized"] is False
    assert cse["source_occurrence_provenance_preserved"] is True
    assert cse["algebraic_cancellation_authorized"] is False
    assert cse["value_is_opaque_to_this_optimizer"] is True


def test_projection_fast_path_replaces_general_work_not_final_obligation() -> None:
    projection = activate_proof_preserving_optimization()["projection_validation_fast_path"]
    assert projection["activation"] == "AUTHORIZED_READ_ONLY_VALIDATION_FAST_PATH"
    assert projection["baseline_general_evaluations"] == 9
    assert projection["optimized_general_evaluations"] == 3
    assert projection["general_representatives"] == ["xy-ring", "zw-ring", "center"]
    assert projection["exact_phase_witness_checks"] == 6
    assert projection["final_verified_cells"] == 9
    assert projection["final_cell_obligation_reduction"] == 0
    assert projection["projection_substitution_authorized"] is False
    assert projection["projection_derivation_authority"] is False
    assert projection["center_relation_preserved"] == "x+y+z+w=0/u⁷²"
    assert projection["ordered_xy_yx_distinct"] is True
    assert projection["ordered_zw_wz_distinct"] is True


def test_structural_work_accounting_is_precise_and_non_benchmarking() -> None:
    work = activate_proof_preserving_optimization()["structural_work_accounting"]
    assert work["baseline_general_work_units"] == 11
    assert work["optimized_general_work_units"] == 4
    assert work["general_work_units_avoided"] == 7
    assert work["replacement_exact_phase_witness_checks"] == 6
    assert work["runtime_speedup_claimed"] is False
    assert work["proof_obligation_reduction_claimed"] is False


def test_authority_cannot_be_promoted_by_optimization() -> None:
    authority = activate_proof_preserving_optimization()["authority_boundary"]
    assert authority["pass169_whole_expression_admission_required"] is True
    assert authority["boolean_gate_truth_produced"] is False
    assert authority["canonical_monolithic_proof"] is False
    assert authority["floating_point_authority"] is False
    assert authority["vm81_mutation_authority"] is False
    assert authority["hash72_commit_authority"] is False
    assert authority["hash216_receipt_authority"] is False
    assert authority["persistence_mutation_authority"] is False
    assert authority["ncalc_matrix_power_reimplemented"] is False
    assert authority["ordinary_scalar_squaring_authorized"] is False
    assert authority["scalar_intermediate_required"] is False


def test_tampered_combined_source_is_rejected_by_inherited_i1218() -> None:
    root = Path(__file__).resolve().parents[2]
    combined = (root / COMBINED_PATH).read_text(encoding="utf-8")
    mutated = combined.replace("(y*x)", "(x*y)", 1)
    _expect_value_error(
        lambda: activate_proof_preserving_optimization(combined_override=mutated),
        "REJECT_I1218_SOURCE_IDENTITY_DRIFT",
    )


def test_tampered_projection_is_rejected_by_inherited_i1218() -> None:
    _expect_value_error(
        lambda: activate_proof_preserving_optimization(
            projection_override=PROJECTION_SOURCE.replace("0/u⁷²", "1/u⁷²", 1)
        ),
        "REJECT_I1218_PROJECTION_DRIFT",
    )


def test_schedule_replay_is_deterministic() -> None:
    first = activate_proof_preserving_optimization()
    second = activate_proof_preserving_optimization()
    assert first == second
    assert len(first["optimization_schedule_sha256"]) == 64
    assert first["optimization_schedule_sha256"] == second["optimization_schedule_sha256"]


def main() -> int:
    tests = [
        value for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
    print(f"PASS219 I121.12 proof-preserving optimizer: {len(tests)} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
