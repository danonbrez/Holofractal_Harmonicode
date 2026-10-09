"""Live native C++ RNA -> Lane 5 -> Python ctypes continuity.

Requires a built exact C ABI. These are true native candidate calculations,
but the other signature witnesses in this fixture remain test-only values.
No VM81 signed commit or complete 5184-scientific-notation mapping is claimed.
"""
from __future__ import annotations

import ctypes
import dataclasses

import pytest

from hhs_backend.runtime.hhs_lane5_native_candidate_mediation_v1 import (
    NativeHash216TransitionView,
    PreparedLane5Candidate,
    SIGNATURE_FIELDS,
    Lane5NativeMediationError,
    mediate_native_rna_frame,
)
from hhs_python.runtime import hhs_uqcel_ctypes_bridge as uq
from hhs_python.runtime.hhs_exact_ctypes_bridge import HHSExactVM81Frame


def native_fixture():
    lib = uq._LIB
    native_transition = NativeHash216TransitionView()
    genesis = lib.hhs_exact_pass219_vm81_pqc_hash216_genesis_reference
    genesis.argtypes = [ctypes.POINTER(NativeHash216TransitionView)]
    genesis.restype = ctypes.c_int
    assert genesis(ctypes.byref(native_transition)) == uq.HHS_EXACT_STATUS_OK

    input_value = uq.HHSExactUQCELInputV1()
    input_value.struct_size = ctypes.sizeof(uq.HHSExactUQCELInputV1)
    input_value.uqcel_version = lib.hhs_exact_uqcel_version()
    input_value.profile = uq.HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1
    one = ctypes.c_uint8(1)
    input_value.delta.struct_size = ctypes.sizeof(uq.HHSExactBigUIntView)
    input_value.delta.byte_length = 1
    input_value.delta.bytes_be = ctypes.pointer(one)

    frame = HHSExactVM81Frame()
    for i in range(81):
        frame.words[i] = 0x9E3779B97F4A7C15 ^ (i * 0x100000001B3)

    signed_request = {field: 101 + idx for idx, field in enumerate(SIGNATURE_FIELDS)}
    signed_request["rna_prepared_signature64"] = 0
    signed_request["rna_decision_signature64"] = 0
    candidate = PreparedLane5Candidate(
        signatures=signed_request,
        hash216_references=(0x2101, 0x2102, 0x2103),
        capability_references=(0x3101, 0x3102, 0x3103, 0x3104),
        learning_stage=4,
        raw5184="0" * 5184,
        ordered_transition_word216=native_transition.transition_word216.decode("ascii"),
        native_rna_bind=True,
    )
    return candidate, input_value, frame, native_transition, one


def test_coupled_native_cell_wall_is_invoked_and_candidate_receipt_is_witnessed():
    candidate, inp, frame, transition, keepalive = native_fixture()
    assert keepalive.value == 1
    result = mediate_native_rna_frame(
        candidate, input_value=inp, vm81_frame=frame, transition=transition,
    )
    assert result["native_rna_vm5184_executed"] is True
    assert result["same_candidate_rna_tensor_and_decision_bound"] is True
    assert result["native_input_signatures"]["rna_prepared_signature64"] > 0
    assert result["native_input_signatures"]["rna_decision_signature64"] > 0
    assert result["native_binary_vm5184_bytes"] == 648
    assert result["native_binary_vm5184_bits"] == 5184
    assert result["raw5184_scientific_notation_to_frame_equivalence_proven"] is False
    assert result["canonical_mutation_admitted"] is False
    assert result["raw_state_exposed_in_result"] is False
    assert "raw5184" not in result
    assert "ordered_transition_word216" not in result

    replay = mediate_native_rna_frame(
        candidate, input_value=inp, vm81_frame=frame, transition=transition,
    )
    assert result["mediation_signature64"] == replay["mediation_signature64"]
    assert result["closure_signature64"] == replay["closure_signature64"]


def test_native_bridge_rejects_changed_transition_before_c_boundary():
    candidate, inp, frame, transition, keepalive = native_fixture()
    modified = dataclasses.replace(
        candidate,
        ordered_transition_word216=(
            ("X" if candidate.ordered_transition_word216[0] != "X" else "Y")
            + candidate.ordered_transition_word216[1:]
        ),
    )
    with pytest.raises(Lane5NativeMediationError, match="ordered Hash216 transition mismatch"):
        mediate_native_rna_frame(
            modified, input_value=inp, vm81_frame=frame, transition=transition,
        )


def test_native_bridge_rejects_wrong_frame_type_and_invalid_feedback():
    candidate, inp, frame, transition, keepalive = native_fixture()
    with pytest.raises(Lane5NativeMediationError, match="81x64 VM81 frame required"):
        mediate_native_rna_frame(
            candidate, input_value=inp, vm81_frame=b"0" * 648, transition=transition,
        )
    with pytest.raises(Lane5NativeMediationError, match="invalid native feedback trinary"):
        mediate_native_rna_frame(
            candidate, input_value=inp, vm81_frame=frame,
            transition=transition, feedback_trinary=2,
        )
