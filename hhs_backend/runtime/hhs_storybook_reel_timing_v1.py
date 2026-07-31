"""Deterministic timing and contextual defaults for the HHS storybook reel.

Canonical caption scheduling uses integer frame indices and ``Fraction``
values. Floating-point timestamps from external narration metadata are parsed
as decimal strings before conversion and are never used as VM81 authority.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

FPS = 30
DURATION_SECONDS = 90
FRAME_COUNT = FPS * DURATION_SECONDS
MAX_TIMING_SPANS = 256

COLOR_WHEEL: Tuple[Tuple[int, int, int], ...] = (
    (230, 65, 80),
    (235, 94, 55),
    (236, 132, 48),
    (229, 179, 45),
    (181, 196, 47),
    (75, 174, 92),
    (44, 160, 151),
    (54, 128, 203),
    (82, 92, 190),
    (137, 82, 186),
    (190, 71, 159),
    (218, 66, 117),
)

# x is the tonic and z is always the reciprocal tritone. y and w draw from
# consonant thirds, fourths, fifths, sixths, sevenths, and controlled chromatic
# neighbor tones so each palette has compatibility plus deliberate tension.
HARMONY_INTERVALS: Tuple[Tuple[int, int, int, int], ...] = (
    (0, 4, 6, 7),
    (0, 3, 6, 7),
    (0, 5, 6, 7),
    (0, 3, 6, 9),
    (0, 4, 6, 10),
    (0, 3, 6, 10),
    (0, 1, 6, 11),
    (0, 2, 6, 9),
    (0, 4, 6, 11),
    (0, 5, 6, 10),
    (0, 2, 6, 8),
    (0, 1, 6, 7),
)

STYLE_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "reciprocal_storybook": {
        "label": "Reciprocal Storybook",
        "description": "Warm illustrated pages, extruded captions, and automatic x/y/z/w reciprocal harmony.",
        "font_face": 4,
        "font_effect": 1,
        "font_scale": 1,
        "letter_spacing": 1,
        "effect_depth": 3,
        "effect_speed": 1,
        "effect_amplitude": 3,
        "palette_mode": 0,
        "phase_origin": 4294967295,
        "phase_scene_stride": 6,
        "title_x": 12,
        "title_y": 12,
        "caption_x": 12,
        "caption_y": 106,
        "title_max_chars": 20,
        "caption_chars_per_line": 22,
        "caption_lines": 2,
        "panel_opacity": 214,
    },
    "chromatic_orbit": {
        "label": "Chromatic Orbit",
        "description": "Orbital caption motion with complementary tritone color planes and chromatic neighbor accents.",
        "font_face": 1,
        "font_effect": 3,
        "font_scale": 1,
        "letter_spacing": 1,
        "effect_depth": 4,
        "effect_speed": 2,
        "effect_amplitude": 6,
        "palette_mode": 0,
        "phase_origin": 4294967295,
        "phase_scene_stride": 12,
        "title_x": 11,
        "title_y": 13,
        "caption_x": 11,
        "caption_y": 104,
        "title_max_chars": 20,
        "caption_chars_per_line": 22,
        "caption_lines": 2,
        "panel_opacity": 205,
    },
    "cinematic_parallax": {
        "label": "Cinematic Parallax",
        "description": "Deep caption extrusion and slow parallax over the native platformer texture field.",
        "font_face": 4,
        "font_effect": 2,
        "font_scale": 1,
        "letter_spacing": 1,
        "effect_depth": 7,
        "effect_speed": 1,
        "effect_amplitude": 8,
        "palette_mode": 0,
        "phase_origin": 4294967295,
        "phase_scene_stride": 6,
        "title_x": 10,
        "title_y": 11,
        "caption_x": 10,
        "caption_y": 102,
        "title_max_chars": 21,
        "caption_chars_per_line": 23,
        "caption_lines": 2,
        "panel_opacity": 222,
    },
    "phase_wave": {
        "label": "Phase Wave",
        "description": "Kinetic wave typography driven by the 72-position phase clock and twelve chromatic tone classes.",
        "font_face": 1,
        "font_effect": 4,
        "font_scale": 1,
        "letter_spacing": 1,
        "effect_depth": 4,
        "effect_speed": 2,
        "effect_amplitude": 7,
        "palette_mode": 0,
        "phase_origin": 4294967295,
        "phase_scene_stride": 18,
        "title_x": 10,
        "title_y": 12,
        "caption_x": 10,
        "caption_y": 103,
        "title_max_chars": 21,
        "caption_chars_per_line": 23,
        "caption_lines": 2,
        "panel_opacity": 216,
    },
    "serif_fable": {
        "label": "Serif Fable",
        "description": "Book-like serif captions with restrained reciprocal palettes and gentle dimensional depth.",
        "font_face": 2,
        "font_effect": 1,
        "font_scale": 1,
        "letter_spacing": 1,
        "effect_depth": 2,
        "effect_speed": 1,
        "effect_amplitude": 2,
        "palette_mode": 0,
        "phase_origin": 4294967295,
        "phase_scene_stride": 6,
        "title_x": 13,
        "title_y": 13,
        "caption_x": 13,
        "caption_y": 106,
        "title_max_chars": 20,
        "caption_chars_per_line": 22,
        "caption_lines": 2,
        "panel_opacity": 224,
    },
    "bold_caption": {
        "label": "Bold Caption Reel",
        "description": "High-contrast bold captions designed for mobile readability and rapid narration.",
        "font_face": 1,
        "font_effect": 1,
        "font_scale": 1,
        "letter_spacing": 1,
        "effect_depth": 5,
        "effect_speed": 1,
        "effect_amplitude": 3,
        "palette_mode": 0,
        "phase_origin": 4294967295,
        "phase_scene_stride": 12,
        "title_x": 9,
        "title_y": 10,
        "caption_x": 9,
        "caption_y": 101,
        "title_max_chars": 22,
        "caption_chars_per_line": 24,
        "caption_lines": 2,
        "panel_opacity": 235,
    },
    "minimal_ink": {
        "label": "Minimal Ink",
        "description": "Quiet flat typography with low motion and clean reciprocal color accents.",
        "font_face": 0,
        "font_effect": 0,
        "font_scale": 1,
        "letter_spacing": 1,
        "effect_depth": 0,
        "effect_speed": 1,
        "effect_amplitude": 0,
        "palette_mode": 0,
        "phase_origin": 4294967295,
        "phase_scene_stride": 6,
        "title_x": 14,
        "title_y": 14,
        "caption_x": 14,
        "caption_y": 107,
        "title_max_chars": 19,
        "caption_chars_per_line": 21,
        "caption_lines": 2,
        "panel_opacity": 196,
    },
    "platformer_quest": {
        "label": "Platformer Quest",
        "description": "Energetic native sprite-map styling with phase-wave captions and game-world motion.",
        "font_face": 3,
        "font_effect": 4,
        "font_scale": 1,
        "letter_spacing": 1,
        "effect_depth": 5,
        "effect_speed": 3,
        "effect_amplitude": 8,
        "palette_mode": 0,
        "phase_origin": 4294967295,
        "phase_scene_stride": 12,
        "title_x": 8,
        "title_y": 10,
        "caption_x": 8,
        "caption_y": 101,
        "title_max_chars": 23,
        "caption_chars_per_line": 24,
        "caption_lines": 2,
        "panel_opacity": 218,
    },
}


@dataclass(frozen=True)
class TextSegment:
    offset: int
    length: int
    text: str


@dataclass(frozen=True)
class TimingSpan:
    index: int
    first_frame: int
    frame_count: int
    text_offset: int
    text_length: int
    source: str

    @property
    def end_frame(self) -> int:
        return self.first_frame + self.frame_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "first_frame": self.first_frame,
            "frame_count": self.frame_count,
            "end_frame": self.end_frame,
            "start_seconds": f"{Fraction(self.first_frame, FPS)}",
            "end_seconds": f"{Fraction(self.end_frame, FPS)}",
            "text_offset": self.text_offset,
            "text_length": self.text_length,
            "source": self.source,
        }


def _fraction(value: Any) -> Fraction:
    try:
        return Fraction(Decimal(str(value)))
    except (InvalidOperation, ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"invalid timestamp: {value!r}") from exc


def _mix(a: Tuple[int, int, int], b: Tuple[int, int, int], b_weight: int) -> Tuple[int, int, int]:
    b_weight = max(0, min(100, int(b_weight)))
    a_weight = 100 - b_weight
    return tuple((a[index] * a_weight + b[index] * b_weight) // 100 for index in range(3))


def _seed(text: str, scene_index: int = 0) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big") ^ (scene_index * 0x9E3779B97F4A7C15)
    return value & ((1 << 64) - 1)


def reciprocal_palette(text: str, scene_index: int = 0) -> Dict[str, Any]:
    seed = _seed(text, scene_index)
    tonic = (seed + scene_index * 5) % 12
    harmony_index = ((seed >> 11) + scene_index * 7) % len(HARMONY_INTERVALS)
    intervals = HARMONY_INTERVALS[harmony_index]
    x_tone = tonic
    y_tone = (tonic + intervals[1]) % 12
    z_tone = (tonic + 6) % 12
    w_tone = (tonic + intervals[3]) % 12
    x = COLOR_WHEEL[x_tone]
    y = COLOR_WHEEL[y_tone]
    z = COLOR_WHEEL[z_tone]
    w = COLOR_WHEEL[w_tone]
    if (seed >> 29) & 1:
        y = _mix(y, z, 24 + scene_index % 25)
        w = _mix(w, x, 18 + scene_index % 31)
    return {
        "chromatic_tonic": int(tonic),
        "harmony_class": int(harmony_index),
        "tone_intervals": list(intervals),
        "phase_planes": {
            "x": int(x_tone * 6),
            "y": int(y_tone * 6),
            "z": int((x_tone * 6 + 36) % 72),
            "w": int(w_tone * 6),
        },
        "colors": {
            "x": "#%02x%02x%02x" % x,
            "y": "#%02x%02x%02x" % y,
            "z": "#%02x%02x%02x" % z,
            "w": "#%02x%02x%02x" % w,
        },
        "reciprocal_offset": 36,
        "chromatic_tones": 12,
    }


def contextual_defaults(text: str) -> Dict[str, Any]:
    source = text.lower()
    candidates: List[Tuple[int, str]] = []
    keyword_groups = {
        "chromatic_orbit": ("space", "star", "planet", "orbit", "cosmic", "galaxy", "future"),
        "cinematic_parallax": ("journey", "epic", "mountain", "ocean", "kingdom", "adventure", "cinematic"),
        "phase_wave": ("music", "song", "rhythm", "dance", "voice", "pulse", "dream"),
        "serif_fable": ("once", "forest", "animal", "fable", "village", "fairy", "child"),
        "bold_caption": ("lesson", "truth", "warning", "secret", "important", "remember", "because"),
        "minimal_ink": ("poem", "quiet", "still", "meditation", "simple", "silence", "minimal"),
        "platformer_quest": ("game", "hero", "quest", "level", "jump", "gate", "checkpoint"),
    }
    for template_id, words in keyword_groups.items():
        score = sum(source.count(word) for word in words)
        candidates.append((score, template_id))
    candidates.sort(key=lambda item: (-item[0], item[1]))
    template_id = candidates[0][1] if candidates and candidates[0][0] > 0 else "reciprocal_storybook"
    style = dict(STYLE_TEMPLATES[template_id])
    palette = reciprocal_palette(text or "HHS STORYBOOK", 0)
    return {
        "schema": "HHS_STORYBOOK_REEL_CONTEXTUAL_DEFAULTS_V1",
        "template_id": template_id,
        "template": style,
        "palette": palette,
        "reason": "keyword_context" if candidates and candidates[0][0] > 0 else "stable_story_hash",
        "available_templates": [
            {"id": template_key, **template}
            for template_key, template in STYLE_TEMPLATES.items()
        ],
    }


def segment_text(text: str, *, target_chars: int = 52, maximum: int = MAX_TIMING_SPANS) -> List[TextSegment]:
    if not text:
        return []
    segments: List[TextSegment] = []
    start = 0
    cursor = 0
    length = len(text)
    sentence_end = re.compile(r"[.!?]+(?:[\"'”’)]*)\s+|\n+")
    while cursor < length and len(segments) < maximum:
        desired = min(length, start + target_chars)
        match = sentence_end.search(text, desired)
        if match and match.end() - start <= target_chars * 2:
            end = match.end()
        else:
            end = desired
            while end < length and end > start + target_chars // 2 and not text[end - 1].isspace():
                end -= 1
            if end <= start:
                end = min(length, start + target_chars)
        while end < length and text[end].isspace() and text[end] != "\n":
            end += 1
        chunk = text[start:end]
        if chunk:
            segments.append(TextSegment(start, end - start, chunk))
        start = end
        cursor = end
    if start < length:
        tail = text[start:]
        if segments:
            prior = segments[-1]
            segments[-1] = TextSegment(prior.offset, prior.length + len(tail), prior.text + tail)
        else:
            segments.append(TextSegment(start, len(tail), tail))
    return segments


def _weights(segments: Sequence[TextSegment]) -> List[int]:
    weights: List[int] = []
    for segment in segments:
        source = segment.text
        weight = max(1, len(source.strip()))
        weight += source.count(",") * 4
        weight += source.count(";") * 6
        weight += source.count(":") * 5
        weight += sum(source.count(mark) for mark in ".!?") * 10
        weight += source.count("\n") * 8
        weights.append(weight)
    return weights


def _allocate_frames(weights: Sequence[int], total_frames: int = FRAME_COUNT) -> List[int]:
    if not weights:
        return []
    total_weight = sum(max(1, int(weight)) for weight in weights)
    raw = [Fraction(max(1, int(weight)) * total_frames, total_weight) for weight in weights]
    allocations = [max(1, int(value)) for value in raw]
    difference = total_frames - sum(allocations)
    remainders = sorted(
        range(len(raw)),
        key=lambda index: (raw[index] - int(raw[index]), -index),
        reverse=True,
    )
    cursor = 0
    while difference > 0:
        allocations[remainders[cursor % len(remainders)]] += 1
        difference -= 1
        cursor += 1
    cursor = 0
    while difference < 0:
        index = remainders[::-1][cursor % len(remainders)]
        if allocations[index] > 1:
            allocations[index] -= 1
            difference += 1
        cursor += 1
    return allocations


def punctuation_weighted_timings(text: str) -> List[TimingSpan]:
    segments = segment_text(text)
    frames = _allocate_frames(_weights(segments), FRAME_COUNT)
    result: List[TimingSpan] = []
    cursor = 0
    for index, (segment, frame_count) in enumerate(zip(segments, frames)):
        result.append(
            TimingSpan(index, cursor, frame_count, segment.offset, segment.length, "punctuation_weighted")
        )
        cursor += frame_count
    if result and cursor != FRAME_COUNT:
        last = result[-1]
        result[-1] = TimingSpan(
            last.index,
            last.first_frame,
            last.frame_count + (FRAME_COUNT - cursor),
            last.text_offset,
            last.text_length,
            last.source,
        )
    return result


def _normalize_spans(spans: Sequence[TimingSpan]) -> List[TimingSpan]:
    if not spans:
        return []
    normalized: List[TimingSpan] = []
    cursor = 0
    for index, span in enumerate(spans[:MAX_TIMING_SPANS]):
        end = max(cursor + 1, min(FRAME_COUNT, span.end_frame))
        normalized.append(
            TimingSpan(index, cursor, end - cursor, span.text_offset, span.text_length, span.source)
        )
        cursor = end
        if cursor >= FRAME_COUNT:
            break
    if normalized and cursor < FRAME_COUNT:
        last = normalized[-1]
        normalized[-1] = TimingSpan(
            last.index,
            last.first_frame,
            last.frame_count + FRAME_COUNT - cursor,
            last.text_offset,
            last.text_length,
            last.source,
        )
    return normalized


def _scaled_frame(seconds: Fraction, source_duration: Fraction) -> int:
    if source_duration <= 0:
        return 0
    scaled = seconds * Fraction(DURATION_SECONDS, 1) / source_duration
    return max(0, min(FRAME_COUNT, int(scaled * FPS)))


def character_alignment_timings(
    text: str,
    alignment: Mapping[str, Any],
    source_duration: Fraction,
) -> List[TimingSpan]:
    characters = alignment.get("characters")
    starts = alignment.get("character_start_times_seconds")
    ends = alignment.get("character_end_times_seconds")
    if not isinstance(characters, Sequence) or isinstance(characters, (str, bytes)):
        return []
    if not isinstance(starts, Sequence) or not isinstance(ends, Sequence):
        return []
    count = min(len(characters), len(starts), len(ends), len(text))
    if count <= 0:
        return []
    segments = segment_text(text)
    spans: List[TimingSpan] = []
    for index, segment in enumerate(segments):
        start_index = min(segment.offset, count - 1)
        end_index = min(segment.offset + segment.length - 1, count - 1)
        try:
            first = _scaled_frame(_fraction(starts[start_index]), source_duration)
            end = _scaled_frame(_fraction(ends[end_index]), source_duration)
        except (ValueError, TypeError):
            return []
        spans.append(
            TimingSpan(index, first, max(1, end - first), segment.offset, segment.length, "elevenlabs_character_alignment")
        )
    return _normalize_spans(spans)


def word_alignment_timings(
    text: str,
    entries: Sequence[Mapping[str, Any]],
    source_duration: Fraction,
) -> List[TimingSpan]:
    spans: List[TimingSpan] = []
    search_cursor = 0
    for index, entry in enumerate(entries[:MAX_TIMING_SPANS]):
        token = str(entry.get("text") or entry.get("word") or "").strip()
        if not token:
            continue
        offset = text.find(token, search_cursor)
        if offset < 0:
            offset = text.lower().find(token.lower(), search_cursor)
        if offset < 0:
            continue
        start_value = entry.get("start", entry.get("start_time", entry.get("start_seconds")))
        end_value = entry.get("end", entry.get("end_time", entry.get("end_seconds")))
        if start_value is None or end_value is None:
            continue
        try:
            first = _scaled_frame(_fraction(start_value), source_duration)
            end = _scaled_frame(_fraction(end_value), source_duration)
        except ValueError:
            continue
        spans.append(
            TimingSpan(index, first, max(1, end - first), offset, len(token), "word_or_segment_alignment")
        )
        search_cursor = offset + len(token)
    return _normalize_spans(spans)


def timings_from_alignment(
    text: str,
    alignment: Optional[Mapping[str, Any]],
    source_duration: Fraction,
) -> Tuple[List[TimingSpan], str]:
    if alignment:
        character = character_alignment_timings(text, alignment, source_duration)
        if character:
            return character, "elevenlabs_character_alignment"
        for key in ("words", "segments", "alignment"):
            entries = alignment.get(key)
            if isinstance(entries, Sequence) and not isinstance(entries, (str, bytes)):
                mapped = word_alignment_timings(
                    text,
                    [entry for entry in entries if isinstance(entry, Mapping)],
                    source_duration,
                )
                if mapped:
                    return mapped, "word_or_segment_alignment"
    return punctuation_weighted_timings(text), "punctuation_weighted_duration_fit"


def timing_file_text(spans: Iterable[TimingSpan]) -> str:
    lines = [
        f"{span.index} {span.first_frame} {span.frame_count} {span.text_offset} {span.text_length}"
        for span in spans
    ]
    return "\n".join(lines) + "\n"


def timing_manifest(spans: Sequence[TimingSpan], source: str) -> Dict[str, Any]:
    payload = {
        "schema": "HHS_STORYBOOK_REEL_TIMING_MANIFEST_V1",
        "fps": FPS,
        "duration_seconds": DURATION_SECONDS,
        "frame_count": FRAME_COUNT,
        "source": source,
        "spans": [span.to_dict() for span in spans],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    payload["sha256_transport_hint"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload
