from __future__ import annotations

from hhs_backend.runtime.hhs_pass215_iteration4_exact_linear_execution_v4 import (
    COMPARISON_MAPPING_ADDENDUM_GIT_BLOB_SHA1,
    REQUIRED_SUITE_OUTPUT_ROOT_HASH216,
    _comparison_projection,
    _exact_ratio,
)


def _work(total: int):
    return {"executed_work_units_total": total}


def test_dense_reference_binds_to_actual_dense_work_not_cold_mode() -> None:
    evidence = {
        "aggregate_execution": {
            "dense_reference_work": _work(3_014_112),
            "factored_reference_work": _work(2_049_888),
        },
        "frozen_workload_modes": {
            "cold": {"work": _work(2_112_096)},
            "warm": {"work": _work(2_049_888)},
            "exact_repetition": {"work": _work(7)},
            "single_region_mutation": {"work": _work(11_911)},
        },
    }
    projection = _comparison_projection(evidence)
    assert projection["dense_reference"]["source"] == "aggregate_execution.dense_reference_work"
    assert projection["dense_reference"]["executed_work_units_total"] == 3_014_112
    assert projection["dense_reference"]["executed_work_units_total"] != evidence["frozen_workload_modes"]["cold"]["work"]["executed_work_units_total"]
    assert projection["exact_integer_reference"]["source"] == "aggregate_execution.factored_reference_work"
    assert projection["exact_integer_reference"]["executed_work_units_total"] == 2_049_888


def test_compiled_cache_and_continuation_bind_to_predeclared_modes() -> None:
    evidence = {
        "aggregate_execution": {
            "dense_reference_work": _work(3_014_112),
            "factored_reference_work": _work(2_049_888),
        },
        "frozen_workload_modes": {
            "cold": {"work": _work(2_112_096)},
            "warm": {"work": _work(2_049_888)},
            "exact_repetition": {"work": _work(7)},
            "single_region_mutation": {"work": _work(11_911)},
        },
    }
    projection = _comparison_projection(evidence)
    assert projection["pass213_compiled_rom_only"]["source"] == "frozen_workload_modes.warm.work"
    assert projection["compiled_rom_plus_cache_layers"]["source"] == "frozen_workload_modes.exact_repetition.work"
    assert projection["compiled_rom_plus_continuation_delta"]["source"] == "frozen_workload_modes.single_region_mutation.work"
    assert projection["compiled_rom_plus_cache_layers"]["executed_work_units_total"] == 7
    assert projection["compiled_rom_plus_continuation_delta"]["executed_work_units_total"] == 11_911


def test_total_primitive_ratio_and_frozen_bindings() -> None:
    assert _exact_ratio(3_014_112, 2_049_888) == {"numerator": 31_397, "denominator": 21_353}
    assert COMPARISON_MAPPING_ADDENDUM_GIT_BLOB_SHA1 == "17fc5927c96f944d89a9e06cc2a684ae47e97c56"
    assert REQUIRED_SUITE_OUTPUT_ROOT_HASH216 == "14de39b3b326eb64bbac5d8be829c289c4a5e1f39b842bfdba59b46fea2c9acb"
