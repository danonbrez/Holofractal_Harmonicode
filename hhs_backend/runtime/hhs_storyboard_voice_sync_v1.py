"""Deterministic 88-second voiceover synchronization for serialized storyboard reels.

This module is intentionally pure: it parses storyboard packages, converts
ElevenLabs character alignment into word timing, maps timing onto the canonical
22 x 4-second reel timeline, and plans bounded TTS speed corrections. Network
I/O and FFmpeg transport live in the CLI so tests do not require provider
credentials or media services.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

MASTER_SECONDS = Decimal("88.000")
FRAME_SECONDS = Decimal("4.000")
FRAME_COUNT = 22
FPS = 30
MASTER_FRAME_COUNT = FRAME_COUNT * int(FRAME_SECONDS) * FPS
SPEED_MIN = Decimal("0.700")
SPEED_MAX = Decimal("1.200")
DEFAULT_TOLERANCE_SECONDS = Decimal("0.350")
DEFAULT_PAUSE_THRESHOLD_SECONDS = Decimal("0.250")


@dataclass(frozen=True)
class WordTiming:
    index: int
    text: str
    start_seconds: Decimal
    end_seconds: Decimal
    text_offset: int
    text_length: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "text": self.text,
            "start_seconds": _decimal_text(self.start_seconds),
            "end_seconds": _decimal_text(self.end_seconds),
            "text_offset": self.text_offset,
            "text_length": self.text_length,
        }


@dataclass(frozen=True)
class PauseTiming:
    start_seconds: Decimal
    end_seconds: Decimal

    @property
    def duration_seconds(self) -> Decimal:
        return self.end_seconds - self.start_seconds

    def to_dict(self) -> Dict[str, str]:
        return {
            "start_seconds": _decimal_text(self.start_seconds),
            "end_seconds": _decimal_text(self.end_seconds),
            "duration_seconds": _decimal_text(self.duration_seconds),
        }


@dataclass(frozen=True)
class FitDecision:
    status: str
    current_speed: Decimal
    next_speed: Decimal
    measured_seconds: Decimal
    target_seconds: Decimal
    delta_seconds: Decimal
    bounded: bool

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        for key in ("current_speed", "next_speed", "measured_seconds", "target_seconds", "delta_seconds"):
            result[key] = _decimal_text(result[key])
        return result


def _decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"invalid decimal value: {value!r}") from exc


def _decimal_text(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP), "f")


def _timecode(seconds: Decimal) -> str:
    milliseconds = int((seconds * 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    minutes, remainder = divmod(milliseconds, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"


def extract_narrative_caption(markdown: str) -> str:
    pattern = re.compile(
        r"(?ims)^#{1,6}\s+NARRATIVE\s+CAPTION\s*$\n"
        r"(?P<body>.*?)"
        r"(?=^#{1,6}\s+(?:STORYBOARD|REFERENCE\s+MANIFEST|VOICEOVER\s+DIRECTION)\b|\Z)"
    )
    match = pattern.search(markdown)
    if not match:
        raise ValueError("scene package does not contain a NARRATIVE CAPTION section")
    body = match.group("body").strip()
    body = re.sub(r"\n\s*---\s*$", "", body).strip()
    if not body:
        raise ValueError("NARRATIVE CAPTION is empty")
    return body


def extract_storyboard_frames(markdown: str) -> List[Dict[str, Any]]:
    heading = re.compile(r"(?im)^#{1,6}\s+FRAME\s+(\d{2})\s+[—-]\s*(.*?)\s*$")
    matches = list(heading.finditer(markdown))
    frames: List[Dict[str, Any]] = []
    for position, match in enumerate(matches):
        start = match.end()
        end = matches[position + 1].start() if position + 1 < len(matches) else len(markdown)
        body = markdown[start:end].strip()
        anchor_match = re.search(r"(?ims)^TRANSITION\s+ANCHOR:\s*(.*?)(?=\n\s*\n|\Z)", body)
        anchor = anchor_match.group(1).strip() if anchor_match else ""
        prompt = body[: anchor_match.start()].strip() if anchor_match else body
        prompt = re.sub(r"\n\s*---\s*$", "", prompt).strip()
        frames.append(
            {
                "frame": int(match.group(1)),
                "label": match.group(2).strip(),
                "prompt": prompt,
                "transition_anchor": anchor,
            }
        )
    return frames


def validate_serialized_storyboard(frames: Sequence[Mapping[str, Any]]) -> None:
    if len(frames) != FRAME_COUNT:
        raise ValueError(f"serialized storyboard must contain exactly {FRAME_COUNT} frames")
    actual = [int(frame.get("frame", -1)) for frame in frames]
    expected = list(range(1, FRAME_COUNT + 1))
    if actual != expected:
        raise ValueError(f"storyboard frame numbering must be {expected[0]:02d}-{expected[-1]:02d}")


def alignment_duration(alignment: Mapping[str, Any]) -> Decimal:
    ends = alignment.get("character_end_times_seconds")
    if not isinstance(ends, Sequence) or isinstance(ends, (str, bytes)) or not ends:
        raise ValueError("alignment is missing character_end_times_seconds")
    return max(_decimal(value) for value in ends)


def words_from_character_alignment(text: str, alignment: Mapping[str, Any]) -> List[WordTiming]:
    characters = alignment.get("characters")
    starts = alignment.get("character_start_times_seconds")
    ends = alignment.get("character_end_times_seconds")
    if not isinstance(characters, Sequence) or isinstance(characters, (str, bytes)):
        raise ValueError("alignment is missing characters")
    if not isinstance(starts, Sequence) or isinstance(starts, (str, bytes)):
        raise ValueError("alignment is missing character_start_times_seconds")
    if not isinstance(ends, Sequence) or isinstance(ends, (str, bytes)):
        raise ValueError("alignment is missing character_end_times_seconds")
    if len(characters) != len(starts) or len(characters) != len(ends):
        raise ValueError("alignment character/start/end lengths differ")
    if len(characters) != len(text):
        raise ValueError(
            "alignment character count does not match source text; use the exact spoken transcript "
            "or the provider normalized alignment that matches it"
        )

    words: List[WordTiming] = []
    for index, match in enumerate(re.finditer(r"\S+", text)):
        first = match.start()
        last = match.end() - 1
        words.append(
            WordTiming(
                index=index,
                text=match.group(0),
                start_seconds=_decimal(starts[first]),
                end_seconds=_decimal(ends[last]),
                text_offset=match.start(),
                text_length=match.end() - match.start(),
            )
        )
    return words


def pauses_from_words(
    words: Sequence[WordTiming],
    *,
    threshold_seconds: Decimal = DEFAULT_PAUSE_THRESHOLD_SECONDS,
) -> List[PauseTiming]:
    pauses: List[PauseTiming] = []
    threshold = _decimal(threshold_seconds)
    for left, right in zip(words, words[1:]):
        if right.start_seconds - left.end_seconds >= threshold:
            pauses.append(PauseTiming(left.end_seconds, right.start_seconds))
    return pauses


def frame_timeline(
    words: Sequence[WordTiming],
    *,
    master_seconds: Decimal = MASTER_SECONDS,
    frame_count: int = FRAME_COUNT,
) -> List[Dict[str, Any]]:
    master = _decimal(master_seconds)
    if frame_count <= 0:
        raise ValueError("frame_count must be positive")
    frame_duration = master / Decimal(frame_count)
    pauses = pauses_from_words(words)
    result: List[Dict[str, Any]] = []
    for frame_index in range(frame_count):
        start = Decimal(frame_index) * frame_duration
        end = start + frame_duration
        overlapping = [
            word
            for word in words
            if word.start_seconds < end and word.end_seconds > start
        ]
        contained_pauses = [
            pause
            for pause in pauses
            if pause.start_seconds < end and pause.end_seconds > start
        ]
        result.append(
            {
                "frame": frame_index + 1,
                "start_seconds": _decimal_text(start),
                "end_seconds": _decimal_text(end),
                "start_timecode": _timecode(start),
                "end_timecode": _timecode(end),
                "narration": " ".join(word.text for word in overlapping),
                "words": [word.to_dict() for word in overlapping],
                "pauses": [pause.to_dict() for pause in contained_pauses],
            }
        )
    return result


def plan_next_speed(
    current_speed: Any,
    measured_seconds: Any,
    *,
    target_seconds: Any = MASTER_SECONDS,
    tolerance_seconds: Any = DEFAULT_TOLERANCE_SECONDS,
) -> FitDecision:
    current = _decimal(current_speed)
    measured = _decimal(measured_seconds)
    target = _decimal(target_seconds)
    tolerance = _decimal(tolerance_seconds)
    if current < SPEED_MIN or current > SPEED_MAX:
        raise ValueError(f"current speed must be between {SPEED_MIN} and {SPEED_MAX}")
    if measured <= 0 or target <= 0:
        raise ValueError("measured and target durations must be positive")
    delta = target - measured
    if measured <= target and delta <= tolerance:
        return FitDecision("FIT", current, current, measured, target, delta, False)

    proposed = current * measured / target
    bounded = False
    if proposed < SPEED_MIN:
        proposed = SPEED_MIN
        bounded = True
    elif proposed > SPEED_MAX:
        proposed = SPEED_MAX
        bounded = True
    proposed = proposed.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    if bounded and proposed == current:
        status = "TOO_LONG_REQUIRES_TEXT_EDIT" if measured > target else "TOO_SHORT_PAD_OR_REPACE"
    else:
        status = "REGENERATE"
    return FitDecision(status, current, proposed, measured, target, delta, bounded)


def choose_alignment(response: Mapping[str, Any], text: str) -> Mapping[str, Any]:
    candidates = [response.get("alignment"), response.get("normalized_alignment")]
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        characters = candidate.get("characters")
        if isinstance(characters, Sequence) and not isinstance(characters, (str, bytes)):
            if len(characters) == len(text):
                return candidate
    raise ValueError("ElevenLabs response did not contain an alignment matching the exact transcript")


def production_manifest(
    *,
    text: str,
    alignment: Mapping[str, Any],
    voice_id: str,
    model_id: str,
    speed: Any,
    storyboard_frames: Optional[Sequence[Mapping[str, Any]]] = None,
    master_seconds: Any = MASTER_SECONDS,
    fit_attempts: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    master = _decimal(master_seconds)
    words = words_from_character_alignment(text, alignment)
    duration = alignment_duration(alignment)
    frame_map = frame_timeline(words, master_seconds=master, frame_count=FRAME_COUNT)
    storyboard = list(storyboard_frames or [])
    if storyboard:
        validate_serialized_storyboard(storyboard)
        by_frame = {int(item["frame"]): dict(item) for item in storyboard}
        for item in frame_map:
            visual = by_frame[item["frame"]]
            item["visual_label"] = visual.get("label", "")
            item["transition_anchor"] = visual.get("transition_anchor", "")

    payload: Dict[str, Any] = {
        "schema": "HHS_SERIALIZED_STORYBOARD_VOICE_SYNC_V1",
        "master_seconds": _decimal_text(master),
        "frame_count": FRAME_COUNT,
        "frame_seconds": _decimal_text(master / Decimal(FRAME_COUNT)),
        "fps": FPS,
        "master_frame_count": int(master * FPS),
        "voice_provider": "ElevenLabs",
        "voice_id": voice_id,
        "model_id": model_id,
        "voice_speed": _decimal_text(_decimal(speed)),
        "measured_narration_seconds": _decimal_text(duration),
        "tail_silence_seconds": _decimal_text(max(Decimal("0"), master - duration)),
        "text_characters": len(text),
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "alignment_authority": "elevenlabs_character_timestamps_unscaled",
        "frames": frame_map,
        "pauses": [pause.to_dict() for pause in pauses_from_words(words)],
        "fit_attempts": list(fit_attempts or []),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    payload["manifest_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def estimate_required_text_reduction(
    text: str,
    measured_seconds: Any,
    target_seconds: Any = MASTER_SECONDS,
) -> Dict[str, Any]:
    measured = _decimal(measured_seconds)
    target = _decimal(target_seconds)
    if measured <= target:
        return {"required": False, "characters": 0, "fraction": "0.000"}
    fraction = Decimal("1") - (target / measured)
    characters = int((Decimal(len(text)) * fraction).to_integral_value(rounding=ROUND_HALF_UP))
    return {
        "required": True,
        "characters": max(1, characters),
        "fraction": _decimal_text(fraction),
    }


__all__ = [
    "DEFAULT_PAUSE_THRESHOLD_SECONDS",
    "DEFAULT_TOLERANCE_SECONDS",
    "FPS",
    "FRAME_COUNT",
    "FRAME_SECONDS",
    "FitDecision",
    "MASTER_FRAME_COUNT",
    "MASTER_SECONDS",
    "PauseTiming",
    "SPEED_MAX",
    "SPEED_MIN",
    "WordTiming",
    "alignment_duration",
    "choose_alignment",
    "estimate_required_text_reduction",
    "extract_narrative_caption",
    "extract_storyboard_frames",
    "frame_timeline",
    "pauses_from_words",
    "plan_next_speed",
    "production_manifest",
    "validate_serialized_storyboard",
    "words_from_character_alignment",
]
