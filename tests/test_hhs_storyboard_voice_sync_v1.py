from __future__ import annotations

import base64
from decimal import Decimal

from hhs_backend.runtime.hhs_storyboard_elevenlabs_v1 import ElevenLabsVoiceoverClient
from hhs_backend.runtime.hhs_storyboard_voice_sync_v1 import (
    FRAME_COUNT,
    MASTER_SECONDS,
    extract_storyboard_frames,
    frame_timeline,
    plan_next_speed,
    production_manifest,
    validate_serialized_storyboard,
    words_from_character_alignment,
)


def _alignment(text: str, duration: Decimal):
    count = len(text)
    step = duration / Decimal(count)
    return {
        "characters": list(text),
        "character_start_times_seconds": [str(step * index) for index in range(count)],
        "character_end_times_seconds": [str(step * (index + 1)) for index in range(count)],
    }


def test_storyboard_voice_timeline_is_22_exact_four_second_windows():
    text = "Winter stayed. The chamber listened."
    alignment = _alignment(text, Decimal("20"))
    words = words_from_character_alignment(text, alignment)
    frames = frame_timeline(words)
    assert len(frames) == FRAME_COUNT == 22
    assert frames[0]["start_timecode"] == "00:00.000"
    assert frames[0]["end_timecode"] == "00:04.000"
    assert frames[-1]["start_timecode"] == "01:24.000"
    assert frames[-1]["end_timecode"] == "01:28.000"


def test_speed_planner_uses_provider_duration_without_rescaling():
    decision = plan_next_speed("1.000", "96.000")
    assert decision.status == "REGENERATE"
    assert decision.next_speed == Decimal("1.091")
    assert decision.target_seconds == MASTER_SECONDS


def test_storyboard_parser_requires_exactly_22_frames():
    markdown = "\n\n".join(
        f"### FRAME {index:02d} — Scene {index}\nPrompt {index}.\n\nTRANSITION ANCHOR: Continue."
        for index in range(1, 23)
    )
    frames = extract_storyboard_frames(markdown)
    validate_serialized_storyboard(frames)
    assert [frame["frame"] for frame in frames] == list(range(1, 23))


def test_manifest_keeps_unscaled_provider_alignment_and_visual_labels():
    text = "Life is not raw material."
    alignment = _alignment(text, Decimal("8"))
    storyboard = [
        {"frame": index, "label": f"Frame {index}", "transition_anchor": "bridge"}
        for index in range(1, 23)
    ]
    manifest = production_manifest(
        text=text,
        alignment=alignment,
        voice_id="voice",
        model_id="eleven_multilingual_v2",
        speed="1.0",
        storyboard_frames=storyboard,
    )
    assert manifest["master_seconds"] == "88.000"
    assert manifest["measured_narration_seconds"] == "8.000"
    assert manifest["tail_silence_seconds"] == "80.000"
    assert manifest["alignment_authority"] == "elevenlabs_character_timestamps_unscaled"
    assert manifest["frames"][0]["visual_label"] == "Frame 1"


def test_elevenlabs_fit_loop_regenerates_with_bounded_native_speed():
    text = "The intelligence continued listening."

    class FakeClient(ElevenLabsVoiceoverClient):
        def __init__(self):
            super().__init__(api_key="test")

        def _request(self, **kwargs):
            speed = Decimal(str(kwargs["speed"]))
            duration = Decimal("96") / speed
            return {
                "audio_base64": base64.b64encode(b"provider-audio").decode("ascii"),
                "alignment": _alignment(text, duration),
            }

    result = FakeClient().synthesize_fitted(
        text=text,
        voice_id="voice",
        max_attempts=3,
    )
    assert result.audio == b"provider-audio"
    assert Decimal(result.manifest["measured_narration_seconds"]) <= Decimal("88.350")
    assert len(result.manifest["fit_attempts"]) >= 2
    assert result.manifest["fit_attempts"][0]["status"] == "REGENERATE"
