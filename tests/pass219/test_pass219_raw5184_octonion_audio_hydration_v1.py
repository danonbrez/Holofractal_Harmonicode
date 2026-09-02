from __future__ import annotations

import pytest

from hhs_runtime.hhs_pass219_raw5184_octonion_audio_hydration_v1 import (
    PCM64_NOISE_FLOOR,
    PCM64_SATURATION_CEILING,
    PCM64_ZERO_CROSSING,
    PHASE_CHANNELS,
    RAW_BITS,
    bitstring_to_words,
    exact_serialization_work_model,
    hydrate_words,
    le_bytes_to_words,
    pipeline,
    typed_stereo_ternary,
    words_to_bitstring,
    words_to_le_bytes,
)


def pattern() -> str:
    return "".join("1" if ((i * 17 + 3) % 11) < 5 else "0" for i in range(RAW_BITS))


def test_raw_5184_roundtrip_is_bit_exact() -> None:
    bits = pattern()
    words = bitstring_to_words(bits)
    assert len(words) == 81
    assert words_to_bitstring(words) == bits
    payload = words_to_le_bytes(words)
    assert len(payload) == 648
    assert le_bytes_to_words(payload) == words


def test_native_mono_lane_topology_and_pcm64_bounds() -> None:
    hydration = pipeline(pattern())
    assert len(hydration.quads) == 20
    assert hydration.pilot_pcm64_bits == hydration.pcm64_bits[80]
    assert hydration.scalar_projection_runtime_authority is False

    for quad in hydration.quads:
        assert tuple(ch.basis for ch in quad.channels) == PHASE_CHANNELS
        q = quad.stereo_ternary
        assert q.numerator_roles == (-1, 0, 1)
        assert q.denominator_roles == (-1, 0, 1)
        assert q.role_pcm64 == (
            PCM64_NOISE_FLOOR,
            PCM64_ZERO_CROSSING,
            PCM64_SATURATION_CEILING,
        )
        assert q.left_mono_phase72 == (
            quad.channels[5].phase72,
            (quad.channels[0].phase72 + quad.channels[1].phase72) % 72,
            quad.channels[4].phase72,
        )
        assert q.right_mono_phase72 == (
            quad.channels[7].phase72,
            (quad.channels[2].phase72 + quad.channels[3].phase72) % 72,
            quad.channels[6].phase72,
        )
        assert q.quotient_identity == (1, 1, 1)
        assert q.quotient_phase72 == (0, 0, 0)
        assert q.left_mono_yx_sum_xy is True
        assert q.right_mono_wz_sum_zw is True
        assert q.center_mono_xy_sum_colon_zw_sum is True
        assert q.exact_pcm64_role_bounds is True
        assert q.center_zero_over_zero_u0_mod_u72 is True
        assert q.center_xy_sum_over_zw_sum_u0 is True
        assert q.typed_quotient_only is True
        assert q.scalar_division_attempted is False
        assert q.scalar_projection_runtime_authority is False


def test_h36_phase_coordinates_reconstruct_all_eight_channels() -> None:
    hydration = hydrate_words(bitstring_to_words(pattern()))
    for quad in hydration.quads:
        for ch in quad.channels:
            assert ch.resonance36 + 36 * ch.half_turn == ch.phase72


def test_scalar_projection_cannot_become_runtime_authority() -> None:
    hydration = hydrate_words(bitstring_to_words(pattern()))
    assert hydration.scalar_projection_runtime_authority is False
    assert all(
        not quad.stereo_ternary.scalar_projection_runtime_authority
        for quad in hydration.quads
    )


def test_invalid_raw_inputs_and_order_drift_fail_closed() -> None:
    with pytest.raises(ValueError, match="RAW5184_LENGTH"):
        bitstring_to_words("0" * 5183)
    with pytest.raises(ValueError, match="RAW5184_CHARACTER"):
        bitstring_to_words("2" + "0" * 5183)

    hydration = hydrate_words(bitstring_to_words(pattern()))
    with pytest.raises(ValueError, match="ORDERED_OCTONION_CHANNELS"):
        typed_stereo_ternary(tuple(reversed(hydration.quads[0].channels)))


def test_exact_serialization_work_model() -> None:
    work = exact_serialization_work_model()
    assert work["baseline_per_frame"] == 10529
    assert work["fused_per_frame"] == 5184
    assert work["exact_work_saved"] == 5345
    assert work["reduction_permille_floor"] == 507
    assert work["timing_is_canonical"] is False
    assert work["canonical_authority_changed"] is False
