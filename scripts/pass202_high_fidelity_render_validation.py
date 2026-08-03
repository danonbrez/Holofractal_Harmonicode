#!/usr/bin/env python3
"""Restartable native and API production validation for Pass 202."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Sequence

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api.storybook_reel_routes import router
from hhs_backend.runtime.hhs_storybook_reel_v2 import (
    CLASSIFICATION,
    CONTRACT,
    QUALITY_PRESETS,
    HighFidelityStorybookReelRuntime,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
NATIVE_ROOT = REPO_ROOT / "native_projects" / "hhs_storybook_reel"


def run(arguments: Sequence[str], *, cwd: Path | None = None, timeout: int = 1800) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(arguments),
        cwd=str(cwd or REPO_ROOT),
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate() -> Dict[str, Any]:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe are required for Pass 202 production validation")

    run(["make", "-C", str(NATIVE_ROOT), "print-source-layout"])
    run(["make", "-C", str(NATIVE_ROOT), "test"], timeout=2400)

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        runtime = HighFidelityStorybookReelRuntime(root / "artifacts")
        catalog = runtime.parameter_catalog()
        presets = runtime.presets()
        resolved = runtime.resolve_parameters(
            {
                "text": "The high-fidelity native shader carries a reciprocal light through the city.",
                "quality_profile": "production_vertical_1080",
                "native_layers": {
                    "texture": {
                        "field": True,
                        "midground": False,
                        "materials": True,
                        "semantic": False,
                        "player": True,
                    },
                    "sprite": {
                        "atmosphere": False,
                        "phase": True,
                        "glows": False,
                        "vignette": True,
                        "hud": False,
                    },
                },
                "render": {
                    "foreground_width": 1000,
                    "foreground_height": 900,
                    "background_blur": 24,
                    "sharpen_luma": "0.62",
                    "saturation": "1.22",
                },
            }
        )
        filter_graph = runtime.video_filter_graph(resolved["render"])
        assert "flags=lanczos" in filter_graph
        assert "gblur=sigma=24" in filter_graph
        assert "overlay=(W-w)/2:(H-h)/2" in filter_graph
        assert "scale=1080:972:flags=neighbor,pad=1080:1920:0:474" not in filter_graph
        assert resolved["native_layers"]["texture_flags"] == 21
        assert resolved["native_layers"]["sprite_overlay_flags"] == 10

        story = root / "story.txt"
        base_rgba = root / "base.rgba"
        styled_rgba = root / "styled.rgba"
        pcm = root / "score.pcm"
        manifest_path = root / "native-manifest.json"
        video_path = root / "pass202-diagnostic.mp4"
        story.write_text(
            "A lantern crosses the native texture field while reciprocal colors turn through the phase clock.",
            encoding="utf-8",
        )
        cli = NATIVE_ROOT / "dist" / "hhs-storybook-reel"
        native = run(
            [
                str(cli),
                "--text-file",
                str(story),
                "--base-rgba",
                str(base_rgba),
                "--styled-rgba",
                str(styled_rgba),
                "--pcm-output",
                str(pcm),
                "--manifest",
                str(manifest_path),
                "--diagnostic-seconds",
                "2",
                "--title",
                "PASS 202",
                "--texture-flags",
                str(resolved["native_layers"]["texture_flags"]),
                "--sprite-overlay-flags",
                str(resolved["native_layers"]["sprite_overlay_flags"]),
                "--font-effect",
                "2",
                "--effect-depth",
                "7",
                "--effect-amplitude",
                "8",
            ],
            timeout=1200,
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["status"] == "HHS_STORYBOOK_REEL_OK"
        assert manifest["frame_count"] == 60
        assert manifest["parallel_computation_used"] is False
        assert manifest["replay_verified"] is True
        assert manifest["program_roundtrip_verified"] is True
        assert manifest["opcode_coverage"] == "19/19"

        render = resolved["render"]
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-f",
                "rawvideo",
                "-pixel_format",
                "rgba",
                "-video_size",
                "160x144",
                "-framerate",
                "30",
                "-i",
                str(styled_rgba),
                "-f",
                "s16le",
                "-ar",
                "48000",
                "-ac",
                "1",
                "-i",
                str(pcm),
                "-filter_complex",
                filter_graph,
                "-map",
                "[v]",
                "-map",
                "1:a:0",
                "-frames:v",
                "60",
                "-c:v",
                str(render["video_codec"]),
                "-preset",
                str(render["video_preset"]),
                "-crf",
                str(render["crf"]),
                "-pix_fmt",
                str(render["pixel_format"]),
                "-r",
                "30",
                "-c:a",
                "aac",
                "-b:a",
                str(render["audio_bitrate"]),
                "-movflags",
                str(render["movflags"]),
                "-threads",
                "1",
                "-filter_threads",
                "1",
                "-filter_complex_threads",
                "1",
                str(video_path),
            ],
            timeout=1200,
        )
        probe = json.loads(
            run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
                    "-of",
                    "json",
                    str(video_path),
                ]
            ).stdout
        )
        video = next(stream for stream in probe["streams"] if stream.get("codec_type") == "video")
        audio = next(stream for stream in probe["streams"] if stream.get("codec_type") == "audio")
        assert video["codec_name"] == "h264"
        assert video["width"] == 1080 and video["height"] == 1920
        assert video["r_frame_rate"] == "30/1"
        assert audio["codec_name"] == "aac"
        assert video_path.stat().st_size > 1000

        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        checked_endpoints = (
            "/api/runtime/storybook-reel/status",
            "/api/runtime/storybook-reel/parameters",
            "/api/runtime/storybook-reel/presets",
        )
        for endpoint in checked_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, (endpoint, response.text)
        resolve_response = client.post(
            "/api/runtime/storybook-reel/parameters/resolve",
            json={"text": "Production", "quality_profile": "production_vertical_1440"},
        )
        assert resolve_response.status_code == 200, resolve_response.text
        candidates_response = client.post(
            "/api/runtime/storybook-reel/defaults/candidates",
            json={"text": "A candle waits inside an old clock tower fable."},
        )
        assert candidates_response.status_code == 200, candidates_response.text
        assert candidates_response.json()["candidate_count"] == 3

        receipt = {
            "schema": "HHS_PASS_202_VALIDATION_RECEIPT_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "closed": True,
            "summary": {
                "quality_presets": len(QUALITY_PRESETS),
                "public_parameter_count": catalog["parameter_count"],
                "style_fields": len(catalog["style_fields"]),
                "native_layer_fields": len(catalog["native_layer_fields"]),
                "render_fields": len(catalog["render_fields"]),
                "authority_locked_fields": len(catalog["authority_locked_fields"]),
                "compiled_native_constant_records": len(catalog["compiled_native_constants"]),
                "native_diagnostic_frames": manifest["frame_count"],
                "native_opcode_coverage": manifest["opcode_coverage"],
                "native_receipts_emitted": manifest["receipts_emitted"],
                "native_replay_verified": manifest["replay_verified"],
                "native_program_roundtrip_verified": manifest["program_roundtrip_verified"],
                "diagnostic_texture_flags": resolved["native_layers"]["texture_flags"],
                "diagnostic_sprite_overlay_flags": resolved["native_layers"]["sprite_overlay_flags"],
                "diagnostic_output_width": video["width"],
                "diagnostic_output_height": video["height"],
                "diagnostic_video_codec": video["codec_name"],
                "diagnostic_audio_codec": audio["codec_name"],
                "validated_api_endpoints": len(checked_endpoints) + 2,
            },
            "catalog_hash72": catalog["catalog_hash72"],
            "resolution_hash72": resolved["resolution_hash72"],
            "native_manifest_sha256": sha256(manifest_path),
            "diagnostic_mp4_sha256": sha256(video_path),
            "native_cli_stdout": native.stdout.strip(),
            "claim_boundary": {
                "logical_vm81_frame_preserved": True,
                "logical_frame_is_output_quality_ceiling": False,
                "fixed_neighbor_black_pad_default": False,
                "all_native_layers_publicly_selectable": True,
                "compiled_constants_publicly_enumerated_read_only": True,
                "parallel_computation_used": False,
            },
            "presets": [preset["id"] for preset in presets["presets"]],
        }
        return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", default="evidence/pass202-ci/PASS202_VALIDATION_RECEIPT.json")
    args = parser.parse_args()
    evidence = Path(args.evidence)
    evidence.parent.mkdir(parents=True, exist_ok=True)
    receipt = validate()
    evidence.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
