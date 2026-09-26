#!/usr/bin/env python3
"""HTML-driven Lane 5 HD MP4 and render-bottleneck acceptance benchmark.

The deterministic I041 HTML animation is the driver.  The harness compares the
same projection-state updates with rendering disabled versus synchronized
WebGL draws, then captures deterministic HD frames and reuses the existing HHS
H.264/ffprobe verification functions to emit a real MP4 artifact.

Timing is host-specific and projection-only.  It does not establish physical
Samsung/Fold7 timing and does not mutate canonical VM81/Hash72/Hash216 state.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import http.server
import json
import shutil
import sys
import threading
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
HTML_REL = Path("applications/holofractal_harmonizer/lane5_holographic_sprite_5184.html")
CAPTURE_TOOLS = ROOT / "native_projects" / "hhs_vm81_game_level10" / "tools"
sys.path.insert(0, str(CAPTURE_TOOLS))

from render_terminal_capture import (  # noqa: E402
    encode_video,
    inspect_video,
    sha256_file,
    verify_video,
)

SCHEMA = "HHS_PASS_220_I041_HTML_HD_MP4_RENDER_BOTTLENECK_V1"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *args: Any) -> None:
        return


def browser_executable() -> str | None:
    configured = None
    for name in (
        "google-chrome-stable",
        "google-chrome",
        "chromium",
        "chromium-browser",
    ):
        resolved = shutil.which(name)
        if resolved:
            return resolved
    return configured


def frame_metrics(frame_dir: Path, expected: int) -> dict[str, Any]:
    paths = sorted(frame_dir.glob("frame_*.png"))
    if len(paths) != expected:
        raise RuntimeError(f"HD frame count mismatch: {len(paths)} != {expected}")
    hashes: set[str] = set()
    minimum_stddev = float("inf")
    dimensions = None
    for path in paths:
        with Image.open(path) as image:
            image.load()
            dimensions = dimensions or image.size
            if image.size != dimensions:
                raise RuntimeError("HD frame dimensions drifted during capture")
            rgb = image.convert("RGB")
            stddev = sum(ImageStat.Stat(rgb).stddev) / 3.0
            minimum_stddev = min(minimum_stddev, stddev)
            if stddev < 3.0:
                raise RuntimeError(f"frame is effectively blank: {path.name}")
        hashes.add(sha256_file(path))
    if len(hashes) < max(3, expected * 3 // 4):
        raise RuntimeError(
            f"insufficient animation variation: {len(hashes)} unique of {expected}"
        )
    return {
        "frame_count": len(paths),
        "unique_frames": len(hashes),
        "minimum_channel_stddev": round(minimum_stddev, 6),
        "width": int(dimensions[0]),
        "height": int(dimensions[1]),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    output = args.output.resolve()
    if output.exists():
        shutil.rmtree(output)
    frames = output / "frames"
    samples = output / "samples"
    frames.mkdir(parents=True)
    samples.mkdir(parents=True)

    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = (
        f"http://127.0.0.1:{server.server_port}/"
        f"{HTML_REL.as_posix()}"
    )

    try:
        with sync_playwright() as p:
            launch: dict[str, Any] = {
                "headless": True,
                "args": [
                    "--no-sandbox",
                    "--ignore-gpu-blocklist",
                    "--enable-webgl",
                    "--use-gl=swiftshader",
                ],
            }
            executable = browser_executable()
            if executable:
                launch["executable_path"] = executable
            browser = p.chromium.launch(**launch)
            page = browser.new_page(
                viewport={"width": args.width, "height": args.height},
                device_scale_factor=1,
            )
            page.goto(url, wait_until="networkidle", timeout=120000)
            page.wait_for_function(
                "window.HHS_LANE5_TEST && window.HHS_LANE5_TEST.ready === true",
                timeout=120000,
            )
            path = page.evaluate(
                "(seed)=>window.HHS_LANE5_TEST.setSeed(seed)",
                args.seed,
            )
            page.evaluate("()=>window.HHS_LANE5_TEST.setManualMode(true)")
            benchmark = page.evaluate(
                "(opts)=>window.HHS_LANE5_TEST.benchmark(opts)",
                {
                    "stateTicks": args.state_ticks,
                    "renderTicks": args.render_ticks,
                    "warmup": args.warmup,
                    "phaseSamples": args.phase_samples,
                    "gpuSync": True,
                },
            )
            canvas = page.locator("canvas").first
            for index in range(args.frames):
                target_tick = index * args.tick_step
                state = page.evaluate(
                    """(tick)=>window.HHS_LANE5_TEST.step(tick,{
                        renderFrame:true,gpuSync:true,updateHudText:false
                    })""",
                    target_tick,
                )
                if state["address"] < 0 or state["address"] >= 5184:
                    raise RuntimeError("HTML driver emitted out-of-range address")
                canvas.screenshot(path=str(frames / f"frame_{index:06d}.png"))

            selected = sorted(frames.glob("frame_*.png"))
            for name, idx in (
                ("first", 0),
                ("middle", len(selected) // 2),
                ("last", len(selected) - 1),
            ):
                shutil.copyfile(selected[idx], samples / f"{name}.png")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    visual = frame_metrics(frames, args.frames)
    if (visual["width"], visual["height"]) != (args.width, args.height):
        raise RuntimeError(
            f"captured canvas is not requested HD size: "
            f"{visual['width']}x{visual['height']}"
        )

    video_path = output / "lane5-html-holographic-720p.mp4"
    encode_video(frames, video_path, args.fps)
    video = inspect_video(video_path)
    verify_video(video, args.frames, args.fps, args.width, args.height)

    if benchmark.get("rendererRemovedControl") is not True:
        raise RuntimeError("renderer-bypass control was not executed")
    if benchmark["stateOnly"]["ticksPerSecond"] <= 0:
        raise RuntimeError("state-only benchmark produced no throughput")
    if benchmark["statePlusRender"]["componentMs"]["render"] <= 0:
        raise RuntimeError("synchronized render timing was not measured")
    if benchmark.get("projectionOnly") is not True:
        raise RuntimeError("HTML benchmark lost projection-only authority")

    receipt = {
        "schema": SCHEMA,
        "status": "PASS",
        "seed": args.seed,
        "path": path,
        "html_driver": str(HTML_REL),
        "resolution": {"width": args.width, "height": args.height},
        "fps": args.fps,
        "tick_step": args.tick_step,
        "benchmark": benchmark,
        "visual": visual,
        "mp4": {
            "path": video_path.name,
            "sha256": sha256_file(video_path),
            **video,
        },
        "sample_frames": {
            path.name: {
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
            for path in sorted(samples.glob("*.png"))
        },
        "existing_media_service_reused": (
            "native_projects/hhs_vm81_game_level10/tools/"
            "render_terminal_capture.py::encode_video/inspect_video/verify_video"
        ),
        "latency_reference": (
            "artifacts/pass219b/PASS_219B_I4_FOLD7_HARDWARE_RESULT.json"
        ),
        "claim_boundary": {
            "html_drives_animation": True,
            "renderer_removed_control_measured": True,
            "browser_timing_host_specific": True,
            "physical_fold7_timing_claimed_by_this_run": False,
            "gpu_browser_floats_projection_only": True,
            "canonical_state_authority_changed": False,
        },
    }
    receipt_path = output / "lane5-html-render-bottleneck-receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, sort_keys=True))
    return receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", default="HHS-I041-LANE5-5184")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--frames", type=int, default=48)
    parser.add_argument("--tick-step", type=int, default=4)
    parser.add_argument("--state-ticks", type=int, default=4096)
    parser.add_argument("--render-ticks", type=int, default=256)
    parser.add_argument("--warmup", type=int, default=64)
    parser.add_argument("--phase-samples", type=int, default=24)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(0 if run(parse_args())["status"] == "PASS" else 1)
