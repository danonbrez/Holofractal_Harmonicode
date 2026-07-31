from __future__ import annotations

from fractions import Fraction

from hhs_backend.runtime.hhs_storybook_reel_timing_v1 import (
    FRAME_COUNT,
    STYLE_TEMPLATES,
    character_alignment_timings,
    contextual_defaults,
    punctuation_weighted_timings,
    reciprocal_palette,
    timing_file_text,
    timings_from_alignment,
)


def test_contextual_defaults_expose_full_template_suite():
    result = contextual_defaults("A hero crossed the final game level and opened the checkpoint gate.")
    assert result["template_id"] == "platformer_quest"
    assert len(result["available_templates"]) >= 8
    assert set(STYLE_TEMPLATES) <= {item["id"] for item in result["available_templates"]}


def test_reciprocal_palette_uses_twelve_tones_and_opposed_x_z_planes():
    first = reciprocal_palette("The reciprocal lantern", 0)
    repeat = reciprocal_palette("The reciprocal lantern", 0)
    next_scene = reciprocal_palette("The reciprocal lantern", 1)
    assert first == repeat
    assert first["chromatic_tones"] == 12
    assert first["reciprocal_offset"] == 36
    assert first["phase_planes"]["z"] == (first["phase_planes"]["x"] + 36) % 72
    assert all(value % 6 == 0 for value in first["phase_planes"].values())
    assert first != next_scene


def test_punctuation_weighted_timing_closes_exactly_at_2700_frames():
    text = (
        "First the lantern woke. Then it crossed the river, slowly and carefully. "
        "At the final gate, every color answered its reciprocal partner!"
    )
    spans = punctuation_weighted_timings(text)
    assert spans
    assert spans[0].first_frame == 0
    assert spans[-1].end_frame == FRAME_COUNT
    assert sum(span.frame_count for span in spans) == FRAME_COUNT
    assert all(span.frame_count > 0 for span in spans)
    assert timing_file_text(spans).count("\n") == len(spans)


def test_elevenlabs_character_alignment_is_scaled_to_canonical_90_seconds():
    text = "A light returned home."
    characters = list(text)
    starts = [str(index / 10) for index in range(len(characters))]
    ends = [str((index + 1) / 10) for index in range(len(characters))]
    alignment = {
        "characters": characters,
        "character_start_times_seconds": starts,
        "character_end_times_seconds": ends,
    }
    spans = character_alignment_timings(text, alignment, Fraction(len(characters), 10))
    assert spans
    assert spans[0].first_frame == 0
    assert spans[-1].end_frame == FRAME_COUNT
    resolved, source = timings_from_alignment(text, alignment, Fraction(len(characters), 10))
    assert source == "elevenlabs_character_alignment"
    assert resolved[-1].end_frame == FRAME_COUNT


def test_invalid_or_absent_alignment_uses_deterministic_duration_fit():
    spans, source = timings_from_alignment(
        "One sentence. A second sentence.",
        {"characters": []},
        Fraction(12, 1),
    )
    assert source == "punctuation_weighted_duration_fit"
    assert spans[-1].end_frame == FRAME_COUNT
