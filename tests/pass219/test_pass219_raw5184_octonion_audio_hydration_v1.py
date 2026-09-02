from __future__ import annotations

from hhs_runtime.hhs_pass219_raw5184_octonion_audio_hydration_registration_v1 import (
    MANDATORY_GUARD,
    manifest,
    surface_declaration,
)
from hhs_runtime.hhs_pass219_raw5184_octonion_audio_hydration_v1 import (
    CELLS,
    PCM64_NOISE_FLOOR,
    PCM64_SATURATION_CEILING,
    PCM64_ZERO_CROSSING,
    SINE_Q62,
    SINE_Q62_SCALE,
    bitstring_to_words,
    exact_serialization_work_model,
    hydrate_words,
    le_bytes_to_words,
    pipeline,
    words_to_bitstring,
    words_to_le_bytes,
)


def fixture_bits() -> str:
    return "".join(
        "1" if ((i * 13 + 7) % 17) < 8 else "0"
        for i in range(5184)
    )


def test_raw5184_bit_byte_and_pcm_views_are_reversible() -> None:
    bits = fixture_bits()
    words = bitstring_to_words(bits)
    assert len(words) == CELLS
    assert words_to_bitstring(words) == bits
    payload = words_to_le_bytes(words)
    assert len(payload) == 648
    assert le_bytes_to_words(payload) == words

    hydration = pipeline(bits)
    assert hydration.pcm64_bits == words
    assert hydration.pilot_pcm64_bits == words[80]
    assert len(hydration.quads) == 20
    assert len(hydration.sine_pcm64) == 160
    assert hydration.canonical_mutation_authority is False
    assert hydration.canonical_hash72_authority is False
    assert hydration.canonical_hash216_authority is False
    assert hydration.scalar_projection_runtime_authority is False
    assert hydration.floating_point_authority is False


def test_mono_lanes_and_stereo_ternary_semantics_are_explicit() -> None:
    hydration = pipeline(fixture_bits())
    for quad in hydration.quads:
        t = quad.stereo_ternary
        by_basis = {channel.basis: channel.phase72 for channel in quad.channels}
        assert t.numerator_roles == (-1, 0, 1)
        assert t.denominator_roles == (-1, 0, 1)
        assert t.quotient_identity == (1, 1, 1)
        assert t.quotient_phase72 == (0, 0, 0)
        assert t.role_pcm64 == (
            PCM64_NOISE_FLOOR,
            PCM64_ZERO_CROSSING,
            PCM64_SATURATION_CEILING,
        )
        assert t.left_mono_phase72 == (
            by_basis["yx"],
            (by_basis["x"] + by_basis["y"]) % 72,
            by_basis["xy"],
        )
        assert t.right_mono_phase72 == (
            by_basis["wz"],
            (by_basis["z"] + by_basis["w"]) % 72,
            by_basis["zw"],
        )
        assert t.left_mono_yx_sum_xy is True
        assert t.right_mono_wz_sum_zw is True
        assert t.center_mono_xy_sum_colon_zw_sum is True
        assert t.center_zero_over_zero_u0_mod_u72 is True
        assert t.center_xy_sum_over_zw_sum_u0 is True
        assert t.typed_quotient_only is True
        assert t.scalar_division_attempted is False
        assert t.scalar_projection_runtime_authority is False


def test_integer_q62_sine_has_exact_72_phase_symmetries() -> None:
    assert len(SINE_Q62) == 72
    assert SINE_Q62[0] == 0
    assert SINE_Q62[18] == SINE_Q62_SCALE
    assert SINE_Q62[36] == 0
    assert SINE_Q62[54] == -SINE_Q62_SCALE
    for k in range(36):
        assert SINE_Q62[k + 36] == -SINE_Q62[k]


def test_serialization_rejects_bad_length_and_alphabet() -> None:
    bits = fixture_bits()
    try:
        bitstring_to_words(bits[:-1])
    except ValueError as exc:
        assert str(exc) == "RAW5184_LENGTH"
    else:
        raise AssertionError("short raw5184 accepted")

    bad = bits[:17] + "x" + bits[18:]
    try:
        bitstring_to_words(bad)
    except ValueError as exc:
        assert str(exc) == "RAW5184_CHARACTER"
    else:
        raise AssertionError("non-binary raw5184 accepted")


def test_registration_declares_native_authority_boundary() -> None:
    m = manifest()
    s = surface_declaration()
    assert m["mandatory_guard"] == MANDATORY_GUARD
    assert m["raw"] == {
        "bits": 5184,
        "bytes": 648,
        "bit_order": "LSB0_PER_UINT64_CELL",
        "cell_order": "ASCENDING_0_TO_80",
        "byte_order": "LITTLE_ENDIAN",
    }
    assert m["stereo_ternary"]["left_mono"] == ["yx", "x+y", "xy"]
    assert m["stereo_ternary"]["right_mono"] == ["wz", "z+w", "zw"]
    assert m["stereo_ternary"]["center_mono_relation"] == "x+y:z+w"
    assert m["stereo_ternary"]["quotient"] == [1, 1, 1]
    assert m["stereo_ternary"]["center_closure"] == "0/0=u^0 mod(u^72)=1"
    assert m["stereo_ternary"]["scalar_projection_runtime_authority"] is False
    assert m["h36"]["sine_runtime_uses_float"] is False
    assert m["h36"]["sine_projection_runtime_authority"] is False
    assert m["canonical_mutation_authority"] is False
    assert m["canonical_hash72_authority"] is False
    assert m["canonical_hash216_authority"] is False
    assert "scalar_projection_has_no_runtime_authority" in s["guards"]
    assert "integer_only_q62_pcm64_sine_projection" in s["guards"]


def test_exact_fused_serialization_work_model() -> None:
    work = exact_serialization_work_model(1)
    assert work["baseline_per_frame"] == 10529
    assert work["fused_per_frame"] == 5184
    assert work["exact_work_saved"] == 5345
    assert work["reduction_permille_floor"] == 507
    assert work["timing_is_canonical"] is False
    assert work["canonical_authority_changed"] is False
