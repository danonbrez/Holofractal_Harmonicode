"""Pass 219 SPI — composite tensor-pair translation stack v1.

Composition order:

1. same-shape equal-sum equation closure at local scale a²=1;
2. exact Fibonacci/Pythagorean scale coordinate from the square-state ladder;
3. three-set cubic normalization t³=t+a², equivalently t³-t=a²=∆=1.

Each layer remains independently typed.  The composite receipt only composes
already-validated projection witnesses and never mutates native tensor state.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence

from hhs_spi_equal_sum_tensor_translation_rule_v1 import lo_shu_translation_witness
from hhs_spi_equal_sum_tensor_translation_rule_v2 import full_sudoku_translation_witness
from hhs_spi_fibonacci_pythagorean_scaling_rule_v1 import (
    tensor_scale_coordinate,
    cross_stage_translation_witness,
)
from hhs_spi_tensor_pair_cubic_normalization_rule_v1 import tensor_pair_cubic_witness

FORMAT = "HHS_SPI_TENSOR_PAIR_TRANSLATION_STACK_V1"
VERSION = "1.0.0"
PROFILE = "EQUAL-SUM+A2-FIBONACCI+CUBIC-THREESET-v1"


class SPITensorPairTranslationStackError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _all_unit(values: Sequence[Mapping[str, Any]]) -> bool:
    return all(v == {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1} for v in values)


def compose_tensor_pair_translation(
    *,
    equal_sum_witness: Mapping[str, Any],
    stage_index: int,
) -> Dict[str, Any]:
    if equal_sum_witness.get("equation_translation_authorized") is not True:
        raise SPITensorPairTranslationStackError("equal-sum translation prerequisite is not closed")
    source_norm = tuple(equal_sum_witness.get("source_normalized_equations", ()))
    target_norm = tuple(equal_sum_witness.get("target_normalized_equations", ()))
    if not source_norm or not target_norm or not _all_unit(source_norm + target_norm):
        raise SPITensorPairTranslationStackError("equal-sum normalized equations are not all exact unit")

    invariant = equal_sum_witness["invariant_sum"]
    # Convert exact JSON rational from predecessor receipt to integer/rational pair.
    if not isinstance(invariant, Mapping) or invariant.get("type") != "EXACT_RATIONAL":
        raise SPITensorPairTranslationStackError("predecessor invariant sum is not exact rational JSON")
    numerator = int(invariant["numerator"])
    denominator = int(invariant["denominator"])
    if denominator != 1:
        invariant_value: Any = (numerator, denominator)
        from fractions import Fraction
        invariant_value = Fraction(numerator, denominator)
    else:
        invariant_value = numerator

    source_scale = tensor_scale_coordinate(
        equation_sum=invariant_value,
        invariant_sum=invariant_value,
        stage_index=stage_index,
    )
    target_scale = tensor_scale_coordinate(
        equation_sum=invariant_value,
        invariant_sum=invariant_value,
        stage_index=stage_index,
    )
    if source_scale["scale_coordinate"] != target_scale["scale_coordinate"]:
        raise SPITensorPairTranslationStackError("tensor pair did not share the same Fibonacci scale coordinate")

    cubic = tensor_pair_cubic_witness(
        pair_layer_id=f"PAIR:{equal_sum_witness['source_id']}:{equal_sum_witness['target_id']}:S{stage_index}",
        source_tensor_id=equal_sum_witness["source_id"],
        target_tensor_id=equal_sum_witness["target_id"],
        source_shape=equal_sum_witness["source_shape"],
        target_shape=equal_sum_witness["target_shape"],
        equal_sum_normalized=True,
    )

    next_stage = cross_stage_translation_witness(
        invariant_sum=invariant_value,
        source_stage=stage_index,
        target_stage=stage_index + 1,
    )

    receipt: Dict[str, Any] = {
        "schema": "HHS_SPI_TENSOR_PAIR_TRANSLATION_STACK_RECEIPT_V1",
        "format": FORMAT,
        "version": VERSION,
        "profile": PROFILE,
        "source_tensor_id": equal_sum_witness["source_id"],
        "target_tensor_id": equal_sum_witness["target_id"],
        "shape": equal_sum_witness["source_shape"],
        "invariant_sum": equal_sum_witness["invariant_sum"],
        "equal_sum_layer": {
            "receipt_sha256": equal_sum_witness["receipt_sha256"],
            "equation_count": equal_sum_witness["sum_equation_count"],
            "local_scale": "a²=1",
            "closed": True,
        },
        "fibonacci_pythagorean_scale_layer": {
            "stage_index": stage_index,
            "source_scale_coordinate": source_scale["scale_coordinate"],
            "target_scale_coordinate": target_scale["scale_coordinate"],
            "same_scale_coordinate": True,
            "pythagorean_seed": "a²+b²=c²",
            "next_stage_ratio": next_stage["finite_scale_ratio"],
            "golden_limit_symbolic": True,
            "finite_ratio_replaced_by_phi": False,
        },
        "cubic_three_set_layer": {
            "receipt_sha256": cubic["receipt_sha256"],
            "three_set": cubic["three_set"],
            "relation": cubic["source_relation"],
            "residual_relation": cubic["residual_relation"],
            "native_t_solved": False,
            "closed": True,
        },
        "composition": {
            "ordered_layers": [
                "EQUAL_SUM_A2_NORMALIZATION",
                "FIBONACCI_PYTHAGOREAN_SCALE",
                "TENSOR_PAIR_CUBIC_THREE_SET",
            ],
            "local_scale": "a²=1",
            "universal_denominator": "∆=1",
            "three_set_normalization": "t³=t+a²",
            "projection_only": True,
        },
        "native_tensor_identity_authorized": False,
        "native_t_solved": False,
        "canonical_admission_authority": False,
        "vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }
    receipt["receipt_sha256"] = sha256(_stable_json(receipt).encode("utf-8")).hexdigest()
    return receipt


def lo_shu_translation_stack(stage_index: int = 0) -> Dict[str, Any]:
    return compose_tensor_pair_translation(
        equal_sum_witness=lo_shu_translation_witness(),
        stage_index=stage_index,
    )


def sudoku_translation_stack(stage_index: int = 0) -> Dict[str, Any]:
    return compose_tensor_pair_translation(
        equal_sum_witness=full_sudoku_translation_witness(),
        stage_index=stage_index,
    )
