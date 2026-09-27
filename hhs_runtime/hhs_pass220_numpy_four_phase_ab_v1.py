"""Pass 220 NumPy1 four-way palindromic phase serialization A/B experiment.

The experiment compares two candidate-only representations of the same ordered
nine-position U9 action over the existing 81-cell NumPy1/VM81 offset carrier:

A. dense substitution tensor control;
B. scalar-symbol multiplication as permutation control + offset vectorization.

Neither arm owns canonical VM81, Hash72, or Hash216 authority.  The experiment
reuses the existing NumPy1 IEEE/5184 ingress membrane, Pass 219 Genesis U9
address-permutation convention, and Pass 220 I033 palindromic constructor.
"""
from __future__ import annotations

from fractions import Fraction
from math import gcd
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    VM81_CELLS,
    deserialize_offsets_5184,
    serialize_offsets_5184,
)
from hhs_runtime.hhs_pass220_numpy_harmonicode_array_v1 import HHSNumPyScalar
from hhs_runtime.hhs_pass220_schrodinger_firing_order_v1 import (
    macrocycle_permutation,
    permutation_power,
)
from hhs_runtime.pass219.lane5_genesis_orientation_u9_qe_bridge import (
    CENTERED_LO_SHU,
    apply_permutation,
)

SCHEMA = "HHS_PASS220_NUMPY1_FOUR_PHASE_AB_V1"
BLOCK_WIDTH = 9
BLOCK_COUNT = VM81_CELLS // BLOCK_WIDTH
CHANNELS = ("xy", "yx", "zw", "wz")
CHANNEL_FACTORS = {"xy": 1, "yx": -1, "zw": 2, "wz": -2}
CHANNEL_LABELS = {"xy": "Aa", "yx": "Ba", "zw": "Ab", "wz": "Bb"}
SCALAR_SYMBOLS = tuple(value for row in CENTERED_LO_SHU for value in row)


class HHSNumPyFourPhaseExperimentError(ValueError):
    pass


def _offsets(values: Sequence[int]) -> tuple[int, ...]:
    result = tuple(values)
    if len(result) != VM81_CELLS:
        raise HHSNumPyFourPhaseExperimentError("HHS_NUMPY1_FOUR_PHASE_VM81_WIDTH_REQUIRED")
    if any(isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 8 for v in result):
        raise HHSNumPyFourPhaseExperimentError("HHS_NUMPY1_FOUR_PHASE_OFFSET_DIGIT_INVALID")
    return result


def _blocks(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    source = _offsets(values)
    return tuple(
        source[start : start + BLOCK_WIDTH]
        for start in range(0, VM81_CELLS, BLOCK_WIDTH)
    )


def _inverse_permutation(permutation: Sequence[int]) -> tuple[int, ...]:
    perm = tuple(int(v) for v in permutation)
    inverse = [0] * len(perm)
    for column, row in enumerate(perm, start=1):
        inverse[row - 1] = column
    return tuple(inverse)


def phase_plan() -> tuple[dict[str, Any], ...]:
    """Return the four ordered channel controls for each nine-cell nucleus."""
    u9 = macrocycle_permutation()
    rows = []
    for block_index, scalar_symbol in enumerate(SCALAR_SYMBOLS):
        channels = {}
        for channel in CHANNELS:
            exponent = (scalar_symbol * CHANNEL_FACTORS[channel]) % BLOCK_WIDTH
            permutation = permutation_power(u9, exponent)
            channels[channel] = {
                "label": CHANNEL_LABELS[channel],
                "factor": CHANNEL_FACTORS[channel],
                "permutation_power": exponent,
                "permutation": permutation,
                "inverse_permutation": _inverse_permutation(permutation),
            }
        rows.append(
            {
                "block_index": block_index,
                "scalar_symbol": scalar_symbol,
                "channels": channels,
            }
        )
    return tuple(rows)


PHASE_PLAN = phase_plan()


def _permutation_matrix(permutation: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    perm = tuple(permutation)
    matrix = [[0] * len(perm) for _ in perm]
    for column, row in enumerate(perm, start=1):
        matrix[row - 1][column - 1] = 1
    return tuple(tuple(row) for row in matrix)


def _dense_apply(block: Sequence[int], permutation: Sequence[int]) -> tuple[int, ...]:
    matrix = _permutation_matrix(permutation)
    source = tuple(block)
    return tuple(
        sum(coefficient * value for coefficient, value in zip(row, source))
        for row in matrix
    )


def substitution_tensor_transform(
    offsets: Sequence[int],
    channel: str,
) -> tuple[int, ...]:
    """Arm A: explicit dense 9x9 substitution tensors; control candidate only."""
    if channel not in CHANNELS:
        raise HHSNumPyFourPhaseExperimentError("HHS_NUMPY1_FOUR_PHASE_CHANNEL_INVALID")
    out = []
    for block, plan in zip(_blocks(offsets), PHASE_PLAN):
        out.extend(_dense_apply(block, plan["channels"][channel]["permutation"]))
    return tuple(out)


def scalar_offset_vector_transform(
    offsets: Sequence[int],
    channel: str,
) -> tuple[int, ...]:
    """Arm B: scalar symbol selects a U9 power; offsets move by index permutation."""
    if channel not in CHANNELS:
        raise HHSNumPyFourPhaseExperimentError("HHS_NUMPY1_FOUR_PHASE_CHANNEL_INVALID")
    out = []
    for block, plan in zip(_blocks(offsets), PHASE_PLAN):
        out.extend(apply_permutation(block, plan["channels"][channel]["permutation"]))
    return tuple(out)


def scalar_offset_vector_inverse(
    offsets: Sequence[int],
    channel: str,
) -> tuple[int, ...]:
    if channel not in CHANNELS:
        raise HHSNumPyFourPhaseExperimentError("HHS_NUMPY1_FOUR_PHASE_CHANNEL_INVALID")
    out = []
    for block, plan in zip(_blocks(offsets), PHASE_PLAN):
        out.extend(apply_permutation(block, plan["channels"][channel]["inverse_permutation"]))
    return tuple(out)


def _ratio(numerator: int, denominator: int) -> str:
    common = gcd(numerator, denominator)
    return f"{numerator // common}/{denominator // common}"


def four_phase_ab_witness_from_offsets(offsets: Sequence[int]) -> dict[str, Any]:
    source = _offsets(offsets)
    source_5184 = serialize_offsets_5184(source)
    zero_positions = tuple(index for index, value in enumerate(source) if value == 0)

    channel_rows: dict[str, Any] = {}
    all_equal = True
    all_roundtrip = True
    all_zero_count = True

    for channel in CHANNELS:
        arm_a = substitution_tensor_transform(source, channel)
        arm_b = scalar_offset_vector_transform(source, channel)
        recovered = scalar_offset_vector_inverse(arm_b, channel)
        transformed_5184 = serialize_offsets_5184(arm_b)
        recovered_5184 = serialize_offsets_5184(recovered)

        equal = arm_a == arm_b
        roundtrip = recovered == source and recovered_5184 == source_5184
        zero_count_ok = sum(v == 0 for v in arm_b) == len(zero_positions)
        all_equal = all_equal and equal
        all_roundtrip = all_roundtrip and roundtrip
        all_zero_count = all_zero_count and zero_count_ok

        channel_rows[channel] = {
            "phase_label": CHANNEL_LABELS[channel],
            "transformed_offsets": arm_b,
            "transformed_5184": transformed_5184,
            "arm_a_equals_arm_b": equal,
            "inverse_roundtrip_exact": roundtrip,
            "zero_spacer_count_preserved": zero_count_ok,
            "zero_positions_after": tuple(index for index, value in enumerate(arm_b) if value == 0),
            "block_controls": tuple(
                {
                    "scalar_symbol": row["scalar_symbol"],
                    "permutation_power": row["channels"][channel]["permutation_power"],
                    "permutation": row["channels"][channel]["permutation"],
                }
                for row in PHASE_PLAN
            ),
        }

    dense_matrix_cells = BLOCK_COUNT * len(CHANNELS) * BLOCK_WIDTH * BLOCK_WIDTH
    dense_nonzero_entries = BLOCK_COUNT * len(CHANNELS) * BLOCK_WIDTH
    vector_index_refs = dense_nonzero_entries
    scalar_symbol_controls = BLOCK_COUNT * len(CHANNELS)
    vector_control_units = vector_index_refs + scalar_symbol_controls

    return {
        "schema": SCHEMA,
        "source_offsets": source,
        "source_5184": source_5184,
        "source_zero_positions": zero_positions,
        "scalar_symbols": SCALAR_SYMBOLS,
        "phase_channels": channel_rows,
        "semantic_identity_all_channels": all_equal,
        "inverse_roundtrip_all_channels": all_roundtrip,
        "zero_spacers_retained_all_channels": all_zero_count,
        "logical_cost": {
            "arm_a_dense_matrix_cells": dense_matrix_cells,
            "arm_a_dense_nonzero_entries": dense_nonzero_entries,
            "arm_b_vector_index_refs": vector_index_refs,
            "arm_b_scalar_symbol_controls": scalar_symbol_controls,
            "arm_b_total_control_units": vector_control_units,
            "dense_to_vector_control_ratio_exact": _ratio(dense_matrix_cells, vector_control_units),
            "arm_b_less_logical_storage": vector_control_units < dense_matrix_cells,
            "timing_is_canonical": False,
        },
        "semantics": {
            "scalar_symbol_role": "PERMUTATION_CONTROL_NOT_PAYLOAD_SCALARIZATION",
            "zero_role": "TYPED_POSITIONAL_SPACER_RETAINED",
            "ordered_channels": CHANNELS,
            "channel_labels": CHANNEL_LABELS,
            "reciprocal_factor_pairs": {"xy_yx": (1, -1), "zw_wz": (2, -2)},
            "substitution_tensor_is_control_candidate_only": True,
            "scalar_offset_vectorization_is_candidate_only": True,
        },
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    }


def four_phase_ab_witness_for_scalar(scalar: HHSNumPyScalar) -> dict[str, Any]:
    if not isinstance(scalar, HHSNumPyScalar) or scalar.dtype != "float64":
        raise HHSNumPyFourPhaseExperimentError("HHS_NUMPY1_FOUR_PHASE_FLOAT64_SCALAR_REQUIRED")
    if scalar.ieee_bits is None:
        raise HHSNumPyFourPhaseExperimentError("HHS_NUMPY1_FOUR_PHASE_IEEE_BITS_REQUIRED")

    offsets = deserialize_offsets_5184(scalar.bigint_5184)
    witness = four_phase_ab_witness_from_offsets(offsets)
    palindrome = scalar.palindromic_symbolic_witness()
    recovered_bits = scalar.recover_ingress_identity()

    return {
        **witness,
        "ieee_bits": f"{scalar.ieee_bits:016x}",
        "recovered_ieee_bits": f"{recovered_bits:016x}",
        "exact_ieee_roundtrip": recovered_bits == scalar.ieee_bits,
        "existing_palindromic_constructor_validation_ok": bool(
            palindrome.get("validation", {}).get("ok")
        ),
        "existing_palindromic_constructor_schema": palindrome.get("schema"),
        "palindromic_authority_delegated_to_existing_constructor": True,
        "four_way_palindromic_phase_serialization": True,
        "host_float_arithmetic_used": False,
    }


def experiment_acceptance(witness: Mapping[str, Any]) -> bool:
    return all(
        (
            witness.get("semantic_identity_all_channels") is True,
            witness.get("inverse_roundtrip_all_channels") is True,
            witness.get("zero_spacers_retained_all_channels") is True,
            witness.get("exact_ieee_roundtrip") is True,
            witness.get("existing_palindromic_constructor_validation_ok") is True,
            witness.get("logical_cost", {}).get("arm_b_less_logical_storage") is True,
            witness.get("canonical_vm81_mutation_authority") is False,
            witness.get("canonical_hash72_authority") is False,
            witness.get("canonical_hash216_authority") is False,
        )
    )


__all__ = [
    "CHANNELS",
    "CHANNEL_LABELS",
    "PHASE_PLAN",
    "SCALAR_SYMBOLS",
    "experiment_acceptance",
    "four_phase_ab_witness_for_scalar",
    "four_phase_ab_witness_from_offsets",
    "phase_plan",
    "scalar_offset_vector_inverse",
    "scalar_offset_vector_transform",
    "substitution_tensor_transform",
]
