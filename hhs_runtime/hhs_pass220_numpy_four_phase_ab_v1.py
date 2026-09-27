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
from hashlib import sha256
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

SUPPLIED_U9_CIRCUIT_TENSOR = """(x*y*List(x*((z*179971179971)/(w*1000000)),y*((w*179971179971)/(z*179971)),z*((z*179971179971)/(w*1000001)),w*((w*179971179971)/(z*179971.179971)))^(z^4==x^2*z^2))*(z*w*List(x*((x*179971179971)/(y*1000000)),y*((y*179971179971)/(x*179971)),z*((x*179971179971)/(y*1000001)),w*((y*179971179971)/(x*179971.179971)))^(x^2==x*z))==(MatrixTimes(MatrixTimes(-x,MatrixPower(List(List(e==(-3)^(1/(Pi*x)))),-Pi)),MatrixPower(List(List(e==(-3)^(1/(Pi*x)))),Pi))==MatrixTimes(x^2,MatrixPower(List(List(e==(-3)^(1/(Pi*x)))),Pi*x))==x*y)/(List((179971179971^((z^4==x^2*z^2)+(x^2==x*z))*w*x*(x^2/y)^(x^2==x*z)*y*z*((x*z)/w)^(z^4==x^2*z^2))/10^(6*((z^4==x^2*z^2)+(x^2==x*z))),(1000001^((z^4==x^2*z^2)+(x^2==x*z))*w*x*y*(y^2/x)^(x^2==x*z))*(((w*y)/z)^(z^4==x^2*z^2)*z),(179971^((z^4==x^2*z^2)+(x^2==x*z))*w*x*y*z*((x*z)/y)^(x^2==x*z))*(z^2/w)^(z^4==x^2*z^2),(10^(6*((z^4==x^2*z^2)+(x^2==x*z)))*w*x*y*((w*y)/x)^(x^2==x*z))*((w^2/z)^(z^4==x^2*z^2)*z))==1)"""
SUPPLIED_U9_CIRCUIT_TENSOR_SHA256 = sha256(
    SUPPLIED_U9_CIRCUIT_TENSOR.encode("utf-8")
).hexdigest()



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




def _u9_tagged_circuit_slots() -> tuple[tuple[int, str], ...]:
    """Nine positional/provenance slots carrying the exact circuit tensor."""
    return tuple(
        (slot_index, SUPPLIED_U9_CIRCUIT_TENSOR)
        for slot_index in range(MACROCYCLE_ORDER)
    )


def _dense_object_apply(
    values: Sequence[Any],
    permutation: Sequence[int],
) -> tuple[Any, ...]:
    """Dense U9 control arm without evaluating or rewriting payload objects."""
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
                "HHS_NUMPY1_U9_CIRCUIT_DENSE_SELECTION_INVALID"
            )
        output.append(selected[0])
    return tuple(output)


def supplied_tensor_u9_witness() -> dict[str, Any]:
    """Run the full supplied circuit tensor as one opaque payload under U9.

    U9 acts only on nine tagged positional/provenance slots.  The tensor itself
    is never parsed, evaluated, simplified, commuted, reordered, factored, or
    projected by this experiment.
    """
    source = _u9_tagged_circuit_slots()
    u9 = macrocycle_permutation()
    identity = tuple(range(1, MACROCYCLE_ORDER + 1))

    orbit = [source]
    iterative = source
    power_cases = []
    all_dense_vector_equal = True
    all_direct_iterative_equal = True
    all_payload_verbatim = True
    all_slot_provenance = True
    all_inverse = True

    for power in range(1, MACROCYCLE_ORDER + 1):
        iterative = apply_permutation(iterative, u9)
        direct_permutation = permutation_power(u9, power)
        direct = apply_permutation(source, direct_permutation)
        dense = _dense_object_apply(source, direct_permutation)
        inverse_permutation = permutation_power(
            u9,
            (MACROCYCLE_ORDER - power) % MACROCYCLE_ORDER,
        )
        recovered = apply_permutation(direct, inverse_permutation)

        dense_vector_equal = dense == direct
        direct_iterative_equal = direct == iterative
        payload_verbatim = all(
            payload == SUPPLIED_U9_CIRCUIT_TENSOR
            for _, payload in direct
        )
        slot_provenance = sorted(
            slot_index for slot_index, _ in direct
        ) == list(range(MACROCYCLE_ORDER))
        inverse_exact = recovered == source

        all_dense_vector_equal = (
            all_dense_vector_equal and dense_vector_equal
        )
        all_direct_iterative_equal = (
            all_direct_iterative_equal and direct_iterative_equal
        )
        all_payload_verbatim = all_payload_verbatim and payload_verbatim
        all_slot_provenance = all_slot_provenance and slot_provenance
        all_inverse = all_inverse and inverse_exact

        orbit.append(iterative)
        power_cases.append(
            {
                "u9_power": power,
                "permutation": direct_permutation,
                "output_slot_order": tuple(
                    slot_index for slot_index, _ in direct
                ),
                "dense_equals_vector": dense_vector_equal,
                "direct_equals_iterative": direct_iterative_equal,
                "payload_verbatim_all_positions": payload_verbatim,
                "slot_provenance_preserved": slot_provenance,
                "inverse_recovers_source": inverse_exact,
            }
        )

    channel_cases = []
    all_channel_equal = True
    all_channel_inverse = True
    all_channel_payload = True
    all_channel_provenance = True
    powers_by_channel: dict[str, set[int]] = {
        channel: set() for channel in CHANNELS
    }

    for plan in PHASE_PLAN:
        for channel in CHANNELS:
            control = plan["channels"][channel]
            powers_by_channel[channel].add(control["permutation_power"])
            arm_a = _dense_object_apply(source, control["permutation"])
            arm_b = apply_permutation(source, control["permutation"])
            recovered = apply_permutation(
                arm_b,
                control["inverse_permutation"],
            )
            equal = arm_a == arm_b
            inverse = recovered == source
            payload_verbatim = all(
                payload == SUPPLIED_U9_CIRCUIT_TENSOR
                for _, payload in arm_b
            )
            provenance = sorted(
                slot_index for slot_index, _ in arm_b
            ) == list(range(MACROCYCLE_ORDER))

            all_channel_equal = all_channel_equal and equal
            all_channel_inverse = all_channel_inverse and inverse
            all_channel_payload = all_channel_payload and payload_verbatim
            all_channel_provenance = all_channel_provenance and provenance

            channel_cases.append(
                {
                    "block_index": plan["block_index"],
                    "scalar_symbol": plan["scalar_symbol"],
                    "channel": channel,
                    "phase_label": control["label"],
                    "permutation_power": control["permutation_power"],
                    "output_slot_order": tuple(
                        slot_index for slot_index, _ in arm_b
                    ),
                    "dense_equals_vector": equal,
                    "inverse_recovers_source": inverse,
                    "payload_verbatim_all_positions": payload_verbatim,
                    "slot_provenance_preserved": provenance,
                }
            )

    first_nine = tuple(orbit[:-1])
    all_u9_powers_covered = all(
        powers == set(range(MACROCYCLE_ORDER))
        for powers in powers_by_channel.values()
    )

    return {
        "schema": "HHS_PASS220_NUMPY1_SUPPLIED_CIRCUIT_TENSOR_U9_V2",
        "supplied_circuit_tensor": SUPPLIED_U9_CIRCUIT_TENSOR,
        "supplied_circuit_tensor_sha256": SUPPLIED_U9_CIRCUIT_TENSOR_SHA256,
        "tensor_is_indivisible_payload": True,
        "u9_role": (
            "ADDRESS_ORBIT_PERMUTATION_OVER_NINE_TAGGED_POSITIONS_"
            "CARRYING_ONE_EXACT_CIRCUIT_TENSOR"
        ),
        "u9_permutation": u9,
        "u9_order": MACROCYCLE_ORDER,
        "u9_power_9_is_identity": (
            permutation_power(u9, MACROCYCLE_ORDER) == identity
        ),
        "one_step_not_identity_by_slot_provenance": orbit[1] != source,
        "nine_distinct_preclosure_positional_states": (
            len(set(first_nine)) == MACROCYCLE_ORDER
        ),
        "full_orbit_returns_tagged_source_exactly": orbit[-1] == source,
        "state_count_including_closure": len(orbit),
        "power_cases": tuple(power_cases),
        "dense_vector_u9_identity_all_powers": all_dense_vector_equal,
        "direct_iterative_u9_identity_all_powers": (
            all_direct_iterative_equal
        ),
        "payload_verbatim_all_powers": all_payload_verbatim,
        "slot_provenance_preserved_all_powers": all_slot_provenance,
        "inverse_roundtrip_all_powers": all_inverse,
        "channel_case_count": len(channel_cases),
        "expected_channel_case_count": len(PHASE_PLAN) * len(CHANNELS),
        "all_u9_powers_covered_per_channel": all_u9_powers_covered,
        "phase_channel_powers": {
            channel: tuple(sorted(powers))
            for channel, powers in powers_by_channel.items()
        },
        "channel_cases": tuple(channel_cases),
        "dense_vector_identity_all_channel_cases": all_channel_equal,
        "inverse_roundtrip_all_channel_cases": all_channel_inverse,
        "payload_verbatim_all_channel_cases": all_channel_payload,
        "slot_provenance_preserved_all_channel_cases": (
            all_channel_provenance
        ),
        "internal_algebra_parsed": False,
        "internal_algebra_evaluated": False,
        "internal_algebra_simplified": False,
        "internal_terms_reordered": False,
        "internal_operations_commuted": False,
        "notation_projection_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
    }


def supplied_tensor_u9_acceptance(witness: Mapping[str, Any]) -> bool:
    return all(
        (
            witness.get("tensor_is_indivisible_payload") is True,
            witness.get("u9_order") == 9,
            witness.get("u9_power_9_is_identity") is True,
            witness.get("one_step_not_identity_by_slot_provenance") is True,
            witness.get(
                "nine_distinct_preclosure_positional_states"
            )
            is True,
            witness.get("full_orbit_returns_tagged_source_exactly") is True,
            witness.get("state_count_including_closure") == 10,
            witness.get("dense_vector_u9_identity_all_powers") is True,
            witness.get("direct_iterative_u9_identity_all_powers") is True,
            witness.get("payload_verbatim_all_powers") is True,
            witness.get("slot_provenance_preserved_all_powers") is True,
            witness.get("inverse_roundtrip_all_powers") is True,
            witness.get("channel_case_count")
            == witness.get("expected_channel_case_count")
            == 36,
            witness.get("all_u9_powers_covered_per_channel") is True,
            witness.get("dense_vector_identity_all_channel_cases") is True,
            witness.get("inverse_roundtrip_all_channel_cases") is True,
            witness.get("payload_verbatim_all_channel_cases") is True,
            witness.get(
                "slot_provenance_preserved_all_channel_cases"
            )
            is True,
            witness.get("internal_algebra_parsed") is False,
            witness.get("internal_algebra_evaluated") is False,
            witness.get("internal_algebra_simplified") is False,
            witness.get("internal_terms_reordered") is False,
            witness.get("internal_operations_commuted") is False,
            witness.get("notation_projection_used") is False,
            witness.get("canonical_vm81_mutation_authority") is False,
            witness.get("canonical_hash72_authority") is False,
            witness.get("canonical_hash216_authority") is False,
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
    "PHASE_PLAN",
    "SCALAR_SYMBOLS",
    "SUPPLIED_U9_CIRCUIT_TENSOR",
    "SUPPLIED_U9_CIRCUIT_TENSOR_SHA256",
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
