#!/usr/bin/env python3
"""Generate and validate one complete 90-second HHS storybook reel."""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import wave
import zipfile
from pathlib import Path

from hhs_backend.runtime.hhs_storybook_reel_v1 import StorybookReelRuntime

STORY = (
    "Beyond the copper hills, a small lantern learned that every color has a reciprocal answer. "
    "Red called to teal across the night. Gold found violet in the quiet river. "
    "The lantern followed four phase planes through the old forest, carrying each sentence at the measured pace of the voice. "
    "At the final gate, the colors turned together like twelve notes around one wheel, and the path home became visible."
)


def make_narration(path: Path, seconds: int = 90, sample_rate: int = 8000) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        block = bytearray()
        for sample_index in range(sample_rate * seconds):
            beat = (sample_index // (sample_rate // 6)) % 12
            period = max(2, sample_rate // (180 + beat * 12))
            amplitude = 2400 if (sample_index // sample_rate) % 2 == 0 else 1700
            value = amplitude if sample_index % period < period // 2 else -amplitude
            block.extend(int(value).to_bytes(2, "little", signed=True))
            if len(block) >= 128 * 1024:
                output.writeframesraw(bytes(block))
                block.clear()
        if block:
            output.writeframesraw(bytes(block))
        output.writeframes(b"")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="evidence/storybook-reel-acceptance")
    arguments = parser.parse_args()
    output = Path(arguments.output).resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    narration = output / "acceptance-narration.wav"
    make_narration(narration)

    runtime = StorybookReelRuntime(artifact_root=output / "runtime")
    audio = runtime.upload_audio(narration.read_bytes(), narration.name, "audio/wav")
    result = runtime.generate(
        {
            "audio_id": audio["audio_id"],
            "text": STORY,
            "title": "THE RECIPROCAL LANTERN",
            "template_id": "phase_wave",
            "style": {
                "font_face": 1,
                "font_effect": 4,
                "font_scale": 1,
                "letter_spacing": 1,
                "effect_depth": 5,
                "effect_speed": 2,
                "effect_amplitude": 7,
                "palette_mode": 2,
                "phase_origin": 0,
                "phase_scene_stride": 12,
                "title_x": 10,
                "title_y": 12,
                "caption_x": 10,
                "caption_y": 103,
                "title_max_chars": 21,
                "caption_chars_per_line": 23,
                "caption_lines": 2,
                "panel_opacity": 216,
                "manual_x": "#e64150",
                "manual_y": "#e5b32d",
                "manual_z": "#2ca097",
                "manual_w": "#8952ba",
            },
        }
    )
    assert result["ok"] is True
    assert result["duration_seconds"] == 90
    assert result["fps"] == 30
    assert result["frame_count"] == 2700
    assert result["width"] == 1080
    assert result["height"] == 1920
    assert result["single_threaded"] is True
    assert result["parallel_computation_logic"] is False
    assert len(result["receipt_hash72"]) == 72
    zip_path = runtime.artifact_path(result["artifact_id"], "zip")
    video_path = runtime.artifact_path(result["artifact_id"], "video")
    assert zip_path.stat().st_size > 0
    assert video_path.stat().st_size > 0
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        required = {
            "storybook-reel.mp4",
            "source/story.txt",
            "source/style.json",
            "source/timing.json",
            "evidence/request.json",
            "evidence/native-manifest.json",
            "evidence/receipt.json",
            "README.md",
        }
        assert required <= names
        native = json.loads(archive.read("evidence/native-manifest.json"))
        receipt = json.loads(archive.read("evidence/receipt.json"))
    assert native["duration_seconds"] == 90
    assert native["frame_count"] == 2700
    assert native["parallel_computation_used"] is False
    assert native["chromatic_tones"] == 12
    assert native["reciprocal_phase_offset"] == 36
    assert native["opcode_coverage"] == "19/19"
    assert native["replay_verified"] is True
    assert receipt["video_probe"]["video_codec"] == "h264"
    assert receipt["video_probe"]["audio_codec"] == "aac"
    assert receipt["video_probe"]["frame_rate"] == "30/1"
    summary = {
        "schema": "HHS_STORYBOOK_REEL_ACCEPTANCE_V1",
        "classification": "HHS_90_SECOND_STORYBOOK_REEL_NO_CODE_APPLICATION_VERIFIED",
        "result": result,
        "native_manifest": native,
        "video_probe": receipt["video_probe"],
        "zip_path": str(zip_path),
        "video_path": str(video_path),
    }
    (output / "acceptance.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
