from __future__ import annotations

from hhs_backend.runtime.hhs_pass215_iteration4_exact_linear_execution_v3 import (
    EXCLUDED_CAPACITY_OR_ATTRIBUTION_KEYS,
    PRIMITIVE_EXECUTED_WORK_UNIT_KEYS,
    primitive_executed_work_units,
    validate_primitive_work_record,
)


def test_primitive_work_formula_excludes_capacity_coverage_and_delta_aliases() -> None:
    record = {
        "source_tensor_bytes": 999999,
        "source_quantization_blocks": 1000,
        "logical_weights": 32000,
        "block_decodes": 10,
        "quant_integer_products": 20,
        "quant_integer_additions": 30,
        "exact_rational_scale_multiplications": 40,
        "exact_rational_accumulation_additions": 50,
        "compiled_descriptor_builds": 60,
        "compiled_descriptor_hits": 70,
        "exact_output_cache_hits": 80,
        "exact_output_cache_misses": 90,
        "changed_input_coordinates": 2,
        "delta_weight_products": 20,
        "delta_output_accumulations": 100,
        "full_output_rows_recomputed": 200,
        "continuation_output_rows_updated": 200,
        "semantic_compare_count": 300,
        "checkpoint_bytes": 123456,
        "recovery_work_units": 110,
    }
    expected = sum(record[key] for key in PRIMITIVE_EXECUTED_WORK_UNIT_KEYS)
    assert primitive_executed_work_units(record) == expected
    assert all(key not in PRIMITIVE_EXECUTED_WORK_UNIT_KEYS for key in EXCLUDED_CAPACITY_OR_ATTRIBUTION_KEYS)
    record["executed_work_units_total"] = expected
    validate_primitive_work_record(record)


def test_delta_weight_products_are_attribution_not_second_product() -> None:
    record = {key: 0 for key in set(PRIMITIVE_EXECUTED_WORK_UNIT_KEYS) | set(EXCLUDED_CAPACITY_OR_ATTRIBUTION_KEYS)}
    record["quant_integer_products"] = 2976
    record["delta_weight_products"] = 2976
    assert primitive_executed_work_units(record) == 2976


def test_capacity_population_does_not_change_primitive_work_total() -> None:
    base = {key: 0 for key in set(PRIMITIVE_EXECUTED_WORK_UNIT_KEYS) | set(EXCLUDED_CAPACITY_OR_ATTRIBUTION_KEYS)}
    base["block_decodes"] = 9
    expected = primitive_executed_work_units(base)
    base["source_tensor_bytes"] = 1_000_000_000
    base["source_quantization_blocks"] = 1_000_000
    base["logical_weights"] = 32_000_000
    base["full_output_rows_recomputed"] = 100_000
    assert primitive_executed_work_units(base) == expected == 9
