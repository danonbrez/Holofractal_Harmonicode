"""Pass220 Q3 read-only integration probes using inherited phase operations.

Unlike the earlier permutation fixture, these checks call real Pass219 QGU
phase transport and RML4 quarter-turn functions. They are NOT a proof of
native cross-Q3 octic product closure; no alternate phase, hash, or VM authority.
"""
from __future__ import annotations

from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    HASH72_ALPHABET,
    hash72_vertex_geometry,
    compress_hash72_vertex_geometry,
)
from hhs_runtime.pass219.hnan_4x4_recursive_gate_v1 import (
    PHASE_RING,
    HNAN_LO_SHU_TENSOR,
    HNAN_TERMINAL_XY_EPSILON,
    XY,
    YX,
    qgu_phase_delta,
    qgu_transport_phase,
    qgu_inverse_transport_phase,
    invariant_receipt,
)
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    expected_product_phase,
)


def test_native_hnan_preserves_ordered_tensor_and_typed_epsilon():
    assert invariant_receipt()["status"] == "PASS"
    assert HNAN_LO_SHU_TENSOR[0][0] == XY
    assert HNAN_LO_SHU_TENSOR[0][2] == YX
    assert XY != YX
    assert HNAN_TERMINAL_XY_EPSILON != XY


def test_native_qgu_transport_roundtrip_every_phase_and_orientation():
    # Exercise existing transport/inverse against all 72 native phases.
    # q, c, d are exact integer *phase transport* parameters, not arbitrary
    # re-interpretations of Hash72 character/reciprocal offset expressions.
    for phase in range(PHASE_RING):
        for q, c, d in ((1, 1, 1), (5, 3, 7), (9, -1, 1)):
            transported = qgu_transport_phase(phase, q, c, d)
            recovered = qgu_inverse_transport_phase(transported, q, c, d)
            assert recovered == phase
            assert (transported - phase) % PHASE_RING == qgu_phase_delta(q, c, d)


def test_native_rml4_opposing_quarter_turns_are_not_collapsed():
    for phase in range(PHASE_RING):
        forward = expected_product_phase(phase, 1)
        reverse = expected_product_phase(phase, -1)
        assert forward == (phase + 18) % PHASE_RING
        assert reverse == (phase - 18) % PHASE_RING
        assert forward != reverse
        assert (forward - reverse) % PHASE_RING == 36


def test_address_hydration_and_native_phase_checks_stay_independent():
    word = "".join(HASH72_ALPHABET)
    vertices = hash72_vertex_geometry(word)
    assert compress_hash72_vertex_geometry(vertices) == word
    assert len(vertices) == 72 * 72
    for position in range(72):
        vertex = vertices[position * 72 + position]
        assert vertex["source_position72"] == position
        assert vertex["coupled_position72"] == position
        # One native phase transport witness bound to an existing exact address;
        # DOES NOT manufacture missing native Hash72 offset admission semantics.
        phase = vertex["source_position72"]
        shifted = qgu_transport_phase(phase, 5, 3, 7)
        assert qgu_inverse_transport_phase(shifted, 5, 3, 7) == phase
