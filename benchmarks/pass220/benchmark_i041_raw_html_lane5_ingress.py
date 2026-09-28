#!/usr/bin/env python3
"""Lane 5 opaque/raw HTML ingress acceptance for the canonical I041 simulation.

This harness does not rewrite or inject a replacement dynamics layer into the
HTML source. It serves the selected HTML file byte-for-byte, sets the browser
viewport externally, verifies WebGL/canvas health, captures at the inherited
quartic projection cadence, and emits an MP4 through the existing HHS media
transport.

The default RAF step is 4 because quartic closure skips 3/4 projection writes
while the simulation itself continues to update on every RAF/tick.
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
CAPTURE_TOOLS = ROOT / "native_projects" / "hhs_vm81_game_level10" / "tools"
sys.path.insert(0, str(CAPTURE_TOOLS))

from render_terminal_capture import (  # noqa: E402
    encode_video,
    inspect_video,
    sha256_file,
    verify_video,
)

SCHEMA = "HHS_PASS_220_I041_RAW_HTML_LANE5_INGRESS_V1"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *args: Any) -> None:
        return


def _sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _browser_executable() -> str | None:
    for name in (
        "google-chrome-stable",
        "google-chrome",
        "chromium",
        "chromium-browser",
    ):
        resolved = shutil.which(name)
        if resolved:
            return resolved
    return None


def _resolve_html(html_arg: Path) -> tuple[Path, Path]:
    candidate = html_arg
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    resolved = candidate.resolve()
    try:
        relative = resolved.relative_to(ROOT)
    except ValueError as exc:
        raise RuntimeError("raw HTML ingress must point to a repository file") from exc
    if resolved.suffix.lower() != ".html":
        raise RuntimeError("raw HTML ingress requires an .html source")
    if not resolved.is_file():
        raise RuntimeError(f"HTML source does not exist: {relative}")
    return resolved, relative


def _wait_raf(page: Any, count: int) -> None:
    page.evaluate(
        """(count)=>new Promise((resolve)=>{
            let seen=0;
            function step(){
                seen++;
                if(seen>=count){ resolve(seen); return; }
                requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        })""",
        count,
    )


def _frame_metrics(frame_dir: Path, expected: int) -> dict[str, Any]:
    paths = sorted(frame_dir.glob("frame_*.png"))
    if len(paths) != expected:
        raise RuntimeError(f"frame count mismatch: {len(paths)} != {expected}")
    unique: set[str] = set()
    minimum_stddev = float("inf")
    dimensions: tuple[int, int] | None = None
    for path in paths:
        with Image.open(path) as image:
            image.load()
            dimensions = dimensions or image.size
            if image.size != dimensions:
                raise RuntimeError("canvas capture dimensions drifted")
            rgb = image.convert("RGB")
            stddev = sum(ImageStat.Stat(rgb).stddev) / 3.0
            minimum_stddev = min(minimum_stddev, stddev)
            if stddev < 2.0:
                raise RuntimeError(f"captured frame is effectively blank: {path.name}")
        unique.add(sha256_file(path))
    if dimensions is None:
        raise RuntimeError("no captured frames")
    return {
        "frame_count": len(paths),
        "unique_frames": len(unique),
        "minimum_channel_stddev": round(minimum_stddev, 6),
        "width": dimensions[0],
        "height": dimensions[1],
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    html_path, html_rel = _resolve_html(args.html)
    source_sha_before = _sha256_path(html_path)

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
    url = f"http://127.0.0.1:{server.server_port}/{html_rel.as_posix()}"

    page_errors: list[str] = []
    console_errors: list[str] = []

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
            executable = _browser_executable()
            if executable:
                launch["executable_path"] = executable
            browser = p.chromium.launch(**launch)
            page = browser.new_page(
                viewport={"width": args.width, "height": args.height},
                device_scale_factor=1,
            )
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            page.on(
                "console",
                lambda msg: console_errors.append(msg.text)
                if msg.type == "error"
                else None,
            )
            page.goto(url, wait_until="networkidle", timeout=args.timeout_ms)
            page.wait_for_selector("canvas", state="visible", timeout=args.timeout_ms)
            _wait_raf(page, args.warmup_raf)

            health = page.evaluate(
                """({width,height})=>{
                    const canvas=document.querySelector("canvas");
                    if(!canvas) return {canvas:false};
                    const gl2=canvas.getContext("webgl2");
                    const gl=gl2 || canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
                    return {
                        canvas:true,
                        canvasWidth:canvas.width,
                        canvasHeight:canvas.height,
                        cssWidth:canvas.clientWidth,
                        cssHeight:canvas.clientHeight,
                        innerWidth:window.innerWidth,
                        innerHeight:window.innerHeight,
                        requestedWidth:width,
                        requestedHeight:height,
                        webgl:!!gl
                    };
                }""",
                {"width": args.width, "height": args.height},
            )
            if health.get("canvas") is not True:
                raise RuntimeError("canonical HTML did not create a canvas")
            if health.get("webgl") is not True:
                raise RuntimeError("canonical HTML canvas has no WebGL context")
            if (health["canvasWidth"], health["canvasHeight"]) != (
                args.width,
                args.height,
            ):
                raise RuntimeError(
                    "canonical canvas does not match requested drawing-buffer "
                    f"resolution: {health['canvasWidth']}x{health['canvasHeight']} "
                    f"!= {args.width}x{args.height}"
                )

            canvas = page.locator("canvas").first
            for index in range(args.frames):
                _wait_raf(page, args.raf_step)
                canvas.screenshot(path=str(frames / f"frame_{index:06d}.png"))

            selected = sorted(frames.glob("frame_*.png"))
            for label, idx in (
                ("first", 0),
                ("middle", len(selected) // 2),
                ("last", len(selected) - 1),
            ):
                shutil.copyfile(selected[idx], samples / f"{label}.png")
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    source_sha_after = _sha256_path(html_path)
    if source_sha_before != source_sha_after:
        raise RuntimeError("raw Lane 5 ingress mutated the canonical HTML source")
    if page_errors:
        raise RuntimeError(f"page runtime errors: {page_errors}")
    if console_errors:
        raise RuntimeError(f"browser console errors: {console_errors}")

    visual = _frame_metrics(frames, args.frames)
    if (visual["width"], visual["height"]) != (args.width, args.height):
        raise RuntimeError(
            f"captured canvas is not requested resolution: "
            f"{visual['width']}x{visual['height']}"
        )

    video_path = output / f"lane5-raw-html-{args.width}x{args.height}.mp4"
    encode_video(frames, video_path, args.fps)
    video = inspect_video(video_path)
    verify_video(video, args.frames, args.fps, args.width, args.height)

    receipt = {
        "schema": SCHEMA,
        "status": "PASS",
        "mode": "OPAQUE_UNALTERED_HTML",
        "html_source": str(html_rel),
        "source_sha256_before": source_sha_before,
        "source_sha256_after": source_sha_after,
        "source_unchanged": source_sha_before == source_sha_after,
        "resolution": {"width": args.width, "height": args.height},
        "quartic_projection": {
            "simulation_updates_are_not_skipped": True,
            "projection_render_period": 4,
            "raf_step": args.raf_step,
            "default_capture_aligns_to_fresh_quartic_render": args.raf_step == 4,
        },
        "browser_health": {
            **health,
            "page_runtime_errors": page_errors,
            "console_error_messages": console_errors,
        },
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
        "authority": {
            "source_rewrite": False,
            "replacement_dynamics": False,
            "canonical_state_mutation": False,
            "lane5_role": "external observation/render transport",
        },
    }
    receipt_path = output / "lane5-raw-html-ingress-receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, sort_keys=True))
    return receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--frames", type=int, default=48)
    parser.add_argument("--raf-step", type=int, default=4)
    parser.add_argument("--warmup-raf", type=int, default=16)
    parser.add_argument("--timeout-ms", type=int, default=120000)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(0 if run(parse_args())["status"] == "PASS" else 1)
