from __future__ import annotations

from copy import deepcopy

from hhs_runtime.hhs_kernel_runtime_autocomposer_v1 import execute_surface_preflight
from hhs_runtime.core_sandbox.hhs_pass219_combined_equation_optimizer_1_21_8 import (
    COMBINED_SHA256,
    DENOMINATOR_SOURCE,
    PERIMETER_CLOCKWISE,
    PROJECTION_SOURCE,
    SURFACE_SYMBOL,
    XY_RING,
    ZW_RING,
    combined_optimizer_surface_declaration,
    verify_combined_equation_optimizer,
)


def _expect_value_error(fn, expected: str) -> None:
    try:
        fn()
    except ValueError as exc:
        assert expected in str(exc)
    else:
        raise AssertionError(f"expected ValueError containing {expected!r}")


def test_combined_equation_identity_and_repeated_denominator() -> None:
    result = verify_combined_equation_optimizer()
    assert result["ok"] is True
    assert result["combined_source_sha256"] == COMBINED_SHA256
    assert result["denominator_occurrences"] == 2
    assert result["common_subexpression_identity_verified"] is True
    assert result["baseline_denominator_evaluations"] == 2
    assert result["planned_denominator_evaluations"] == 1
    assert result["duplicate_denominator_evaluations_eliminated"] == 1
    assert result["compute_denominator_once_candidate"] is True
    assert result["reuse_same_denominator_identity_on_lhs_and_rhs"] is True


def test_ordered_perimeter_matches_two_interleaving_four_cycles() -> None:
    result = verify_combined_equation_optimizer()
    assert result["perimeter_clockwise"] == list(PERIMETER_CLOCKWISE)
    assert result["xy_ring"] == list(XY_RING)
    assert result["zw_ring"] == list(ZW_RING)
    assert tuple(PERIMETER_CLOCKWISE[0::2]) == XY_RING
    assert tuple(PERIMETER_CLOCKWISE[1::2]) == ZW_RING
    assert "(y*x)" in DENOMINATOR_SOURCE
    assert "(x*y)" in DENOMINATOR_SOURCE
    assert "(w*z)" in DENOMINATOR_SOURCE
    assert "(z*w)" in DENOMINATOR_SOURCE


def test_denominator_magnitude_projection_is_bound_not_substituted() -> None:
    result = verify_combined_equation_optimizer()
    assert result["denominator_magnitude_projection_source"] == PROJECTION_SOURCE
    assert result["projection_outer_unit_cells"] == 8
    assert result["projection_center_cells"] == 1
    assert result["projection_unit_definition"] == "1=u⁷²"
    assert result["center_relation"] == "x+y+z+w=0/u⁷²"
    assert result["baseline_projection_cell_checks"] == 9
    assert result["candidate_projection_orbit_representatives"] == 3
    assert result["candidate_projection_checks_eliminated"] == 6
    assert result["projection_fast_path_candidate_only"] is True
    assert result["projection_derivation_authority"] is False
    assert result["projection_substitution_authorized"] is False


def test_no_algebraic_or_authority_promotion() -> None:
    result = verify_combined_equation_optimizer()
    assert result["algebraic_cancellation_authorized"] is False
    assert result["ordinary_scalar_squaring_authorized"] is False
    assert result["ncalc_matrix_power_reimplemented"] is False
    assert result["floating_point_authority"] is False
    assert result["vm81_mutation_authority"] is False
    assert result["hash72_commit_authority"] is False
    assert result["persistence_mutation_authority"] is False
    assert result["canonical_monolithic_proof"] is False
    assert result["pass169_whole_expression_admission_required"] is True


def test_mutating_ordered_product_rejects_combined_identity() -> None:
    valid = verify_combined_equation_optimizer()
    source = valid["preflight"]  # exercise first so rejection cannot bypass preflight
    assert source["ok"] is True
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    combined = (root / "contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode").read_text(encoding="utf-8")
    mutated = combined.replace("(y*x)", "(x*y)", 1)
    _expect_value_error(
        lambda: verify_combined_equation_optimizer(combined_override=mutated),
        "REJECT_I1218_SOURCE_IDENTITY_DRIFT",
    )


def test_mutating_only_second_denominator_rejects_common_subexpression_reuse() -> None:
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    combined = (root / "contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode").read_text(encoding="utf-8")
    split = combined.rsplit(DENOMINATOR_SOURCE, 1)
    assert len(split) == 2
    mutated = split[0] + DENOMINATOR_SOURCE.replace("I^4", "I^3", 1) + split[1]
    _expect_value_error(
        lambda: verify_combined_equation_optimizer(combined_override=mutated),
        "REJECT_I1218_SOURCE_IDENTITY_DRIFT",
    )


def test_projection_center_or_unit_definition_drift_rejects() -> None:
    _expect_value_error(
        lambda: verify_combined_equation_optimizer(
            projection_override=PROJECTION_SOURCE.replace("0/u⁷²", "1/u⁷²", 1)
        ),
        "REJECT_I1218_PROJECTION_DRIFT",
    )
    _expect_value_error(
        lambda: verify_combined_equation_optimizer(
            projection_override=PROJECTION_SOURCE.replace("1=u⁷²", "1=u^72", 1)
        ),
        "REJECT_I1218_PROJECTION_DRIFT",
    )


def test_membrane_rejects_incomplete_optimizer_surface() -> None:
    malformed = deepcopy(combined_optimizer_surface_declaration())
    malformed["witness_schemas"] = []
    decision = execute_surface_preflight(malformed, operation=SURFACE_SYMBOL, cache={})
    assert decision["ok"] is False
    assert decision["status"] == "REJECT_KERNEL_DERIVED_RUNTIME_PREFLIGHT"


def test_deterministic_replay_of_structural_plan() -> None:
    first = verify_combined_equation_optimizer()
    second = verify_combined_equation_optimizer()
    assert first == second


def main() -> int:
    tests = [
        value for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
    print(f"PASS219 I121.8 combined equation tests: {len(tests)} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
