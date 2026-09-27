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
    MACROCYCLE_ORDER,
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

ORDERED_TENSOR_LITERAL = (
    ("(x*y)", "x+y", "(y*x)"),
    (
        "(x*y)-(z*w)",
        "x+y-z-w+(x*y)+(y*x)-(z*w)-(w*z)",
        "(w*z)-(y*x)",
    ),
    ("(w*z)", "z+w", "(z*w)"),
)
_PRODUCT_TOKEN_PROJECTION = (
    ("(x*y)", "xy"),
    ("(y*x)", "yx"),
    ("(z*w)", "zw"),
    ("(w*z)", "wz"),
)



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




def _flatten_tensor(tensor: Sequence[Sequence[str]]) -> tuple[str, ...]:
    rows = tuple(tuple(str(cell) for cell in row) for row in tensor)
    if len(rows) != 3 or any(len(row) != 3 for row in rows):
        raise HHSNumPyFourPhaseExperimentError(
            "HHS_NUMPY1_ORDERED_TENSOR_3X3_REQUIRED"
        )
    return tuple(value for row in rows for value in row)


def _reshape_tensor(values: Sequence[str]) -> tuple[tuple[str, ...], ...]:
    source = tuple(values)
    if len(source) != BLOCK_WIDTH:
        raise HHSNumPyFourPhaseExperimentError(
            "HHS_NUMPY1_ORDERED_TENSOR_U9_WIDTH_REQUIRED"
        )
    return tuple(
        tuple(source[start : start + 3])
        for start in range(0, BLOCK_WIDTH, 3)
    )


def _dense_symbolic_apply(
    values: Sequence[str],
    permutation: Sequence[int],
) -> tuple[str, ...]:
    """Dense U9 control arm without evaluating or rewriting any cell."""
    matrix = _permutation_matrix(permutation)
    source = tuple(values)
    output = []
    for row in matrix:
        selected = [
            source[index]
            for index, coefficient in enumerate(row)
            if coefficient == 1
        ]
        if len(selected) != 1:
            raise HHSNumPyFourPhaseExperimentError(
                "HHS_NUMPY1_ORDERED_TENSOR_DENSE_SELECTION_INVALID"
            )
        output.append(selected[0])
    return tuple(output)


def supplied_tensor_u9_witness() -> dict[str, Any]:
    """Run the literal supplied circuit tensor through the exact U9 orbit.

    The tensor strings are opaque ordered circuit cells. U9 is allowed only to
    permute their nine addresses. No cell expression is projected, simplified,
    commuted, normalized, factored, or rewritten.
    """
    source = _flatten_tensor(ORDERED_TENSOR_LITERAL)
    u9 = macrocycle_permutation()
    identity = tuple(range(1, MACROCYCLE_ORDER + 1))

    states = [source]
    cases = []
    all_dense_vector_equal = True
    all_direct_iterative_equal = True
    all_cells_preserved = True
    all_inverse = True
    current = source

    for power in range(1, MACROCYCLE_ORDER + 1):
        current = apply_permutation(current, u9)
        direct_permutation = permutation_power(u9, power)
        direct = apply_permutation(source, direct_permutation)
        dense = _dense_symbolic_apply(source, direct_permutation)
        inverse_permutation = permutation_power(
            u9,
            (MACROCYCLE_ORDER - power) % MACROCYCLE_ORDER,
        )
        recovered = apply_permutation(direct, inverse_permutation)

        dense_vector_equal = dense == direct
        direct_iterative_equal = direct == current
        cells_preserved = sorted(direct) == sorted(source)
        inverse_exact = recovered == source

        all_dense_vector_equal = (
            all_dense_vector_equal and dense_vector_equal
        )
        all_direct_iterative_equal = (
            all_direct_iterative_equal and direct_iterative_equal
        )
        all_cells_preserved = all_cells_preserved and cells_preserved
        all_inverse = all_inverse and inverse_exact

        states.append(current)
        cases.append(
            {
                "u9_power": power,
                "permutation": direct_permutation,
                "tensor_state": _reshape_tensor(direct),
                "dense_substitution_state": _reshape_tensor(dense),
                "dense_equals_vector": dense_vector_equal,
                "direct_equals_iterative": direct_iterative_equal,
                "all_literal_cells_preserved": cells_preserved,
                "inverse_recovers_source": inverse_exact,
            }
        )

    first_nine = tuple(states[:-1])
    return {
        "schema": "HHS_PASS220_NUMPY1_SUPPLIED_CIRCUIT_TENSOR_U9_V1",
        "literal_tensor": ORDERED_TENSOR_LITERAL,
        "u9_role": "ADDRESS_ORBIT_PERMUTATION_OVER_NINE_LITERAL_CIRCUIT_CELLS",
        "u9_permutation": u9,
        "u9_order": MACROCYCLE_ORDER,
        "u9_power_9_is_identity": (
            permutation_power(u9, MACROCYCLE_ORDER) == identity
        ),
        "one_step_not_identity": states[1] != source,
        "nine_distinct_preclosure_states": (
            len(set(first_nine)) == MACROCYCLE_ORDER
        ),
        "full_orbit_returns_literal_tensor_exactly": states[-1] == source,
        "full_orbit_tensor": _reshape_tensor(states[-1]),
        "state_count_including_closure": len(states),
        "cases": tuple(cases),
        "dense_vector_u9_identity_all_powers": all_dense_vector_equal,
        "direct_iterative_u9_identity_all_powers": all_direct_iterative_equal,
        "literal_cells_preserved_all_powers": all_cells_preserved,
        "inverse_roundtrip_all_powers": all_inverse,
        "x_times_y_and_y_times_x_remain_distinct_literal_cells": (
            source[0] != source[2]
        ),
        "w_times_z_and_z_times_w_remain_distinct_literal_cells": (
            source[6] != source[8]
        ),
        "center_cell_literal_exact": (
            source[4]
            == "x+y-z-w+(x*y)+(y*x)-(z*w)-(w*z)"
        ),
        "notation_projection_used": False,
        "algebraic_simplification_used": False,
        "commutation_used": False,
        "term_reordering_inside_cell_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    }


def supplied_tensor_u9_acceptance(witness: Mapping[str, Any]) -> bool:
    return all(
        (
            witness.get("u9_order") == 9,
            witness.get("u9_power_9_is_identity") is True,
            witness.get("one_step_not_identity") is True,
            witness.get("nine_distinct_preclosure_states") is True,
            witness.get("full_orbit_returns_literal_tensor_exactly") is True,
            witness.get("state_count_including_closure") == 10,
            witness.get("dense_vector_u9_identity_all_powers") is True,
            witness.get("direct_iterative_u9_identity_all_powers") is True,
            witness.get("literal_cells_preserved_all_powers") is True,
            witness.get("inverse_roundtrip_all_powers") is True,
            witness.get(
                "x_times_y_and_y_times_x_remain_distinct_literal_cells"
            )
            is True,
            witness.get(
                "w_times_z_and_z_times_w_remain_distinct_literal_cells"
            )
            is True,
            witness.get("center_cell_literal_exact") is True,
            witness.get("notation_projection_used") is False,
            witness.get("algebraic_simplification_used") is False,
            witness.get("commutation_used") is False,
            witness.get("term_reordering_inside_cell_used") is False,
        )
    )


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
    supplied_u9 = supplied_tensor_u9_witness()
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
        "supplied_tensor_u9_witness": supplied_u9,
        "supplied_tensor_u9_acceptance": supplied_tensor_u9_acceptance(
            supplied_u9
        ),
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
            witness.get("supplied_tensor_u9_acceptance") is True,
            witness.get("logical_cost", {}).get("arm_b_less_logical_storage") is True,
            witness.get("canonical_vm81_mutation_authority") is False,
            witness.get("canonical_hash72_authority") is False,
            witness.get("canonical_hash216_authority") is False,
        )
    )


__all__ = [
    "CHANNELS",
    "CHANNEL_LABELS",
    "ORDERED_TENSOR_LITERAL",
    "PHASE_PLAN",
    "SCALAR_SYMBOLS",
    "experiment_acceptance",
    "four_phase_ab_witness_for_scalar",
    "four_phase_ab_witness_from_offsets",
    "phase_plan",
    "supplied_tensor_u9_acceptance",
    "supplied_tensor_u9_witness",
    "scalar_offset_vector_inverse",
    "scalar_offset_vector_transform",
    "substitution_tensor_transform",
]
