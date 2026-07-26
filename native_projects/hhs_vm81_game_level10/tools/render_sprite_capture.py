#!/usr/bin/env python3
"""Render and verify VM81 sprite-map overlay-gradient evidence.

The native C renderer exports the exact 160x144 sprite framebuffer for every
state in the deterministic VM81 playthrough. This tool validates that stream,
creates user-facing PNG evidence and an H.264 MP4, and binds every transformed
artifact to the native frame-stream and final Hash72/Hash216 receipts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont, ImageStat
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required. Install python3-pil or pillow.") from exc


CONTRACT = "HHS-VM81-SPRITE-MAP-OVERLAY-GRADIENTS-V1"
CLASSIFICATION = "VM81_SPRITE_MAP_OVERLAY_GRADIENTS_PRESENTATION_VERIFIED"
LOGICAL_SIZE = (160, 144)
VIDEO_SIZE = (640, 576)
FONT_CANDIDATES = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSansMono.ttf"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_tool(name: str) -> str:
    tool = shutil.which(name)
    if not tool:
        raise RuntimeError(f"required executable not found: {name}")
    return tool


def run_checked(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def select_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def load_trace(input_dir: Path) -> dict[str, Any]:
    path = input_dir / "sprite-capture-trace.json"
    if not path.is_file():
        raise RuntimeError(f"sprite trace missing: {path}")
    trace = json.loads(path.read_text(encoding="utf-8"))
    if trace.get("contract") != CONTRACT:
        raise RuntimeError(f"unexpected sprite contract: {trace.get('contract')}")
    if trace.get("capture_classification") != "VM81_SPRITE_MAP_OVERLAY_GRADIENTS_CAPTURED":
        raise RuntimeError("native sprite capture classification is missing")
    if trace.get("state_projection_non_mutating") != "VERIFIED":
        raise RuntimeError("native renderer did not attest projection-only behavior")
    if trace.get("replay") != "MATCH" or trace.get("opcode_coverage") != "19/19":
        raise RuntimeError("sprite capture is not bound to complete replay closure")
    return trace


def load_frame_paths(input_dir: Path, expected_count: int) -> list[Path]:
    paths = sorted(input_dir.glob("frame_*.ppm"))
    if len(paths) != expected_count:
        raise RuntimeError(f"frame count mismatch: files={len(paths)} trace={expected_count}")
    for index, path in enumerate(paths):
        expected = f"frame_{index:06d}.ppm"
        if path.name != expected:
            raise RuntimeError(f"noncanonical frame sequence: {path.name} != {expected}")
    return paths


def inspect_frames(paths: list[Path]) -> dict[str, Any]:
    hashes: set[str] = set()
    minimum_stddev = float("inf")
    minimum_colors = 1 << 30
    maximum_colors = 0
    for path in paths:
        with Image.open(path) as image:
            image.load()
            if image.size != LOGICAL_SIZE:
                raise RuntimeError(f"frame dimensions mismatch: {path} -> {image.size}")
            rgb = image.convert("RGB")
            colors = rgb.getcolors(maxcolors=LOGICAL_SIZE[0] * LOGICAL_SIZE[1])
            color_count = len(colors or [])
            if color_count < 32:
                raise RuntimeError(f"frame has insufficient sprite/gradient color content: {path}")
            minimum_colors = min(minimum_colors, color_count)
            maximum_colors = max(maximum_colors, color_count)
            stddev = sum(ImageStat.Stat(rgb).stddev) / 3.0
            minimum_stddev = min(minimum_stddev, stddev)
            if stddev < 12.0:
                raise RuntimeError(f"frame is effectively blank or flat: {path}")
        hashes.add(sha256_file(path))
    if len(hashes) < max(200, len(paths) * 3 // 4):
        raise RuntimeError(f"insufficient frame variation: {len(hashes)} unique of {len(paths)}")
    return {
        "unique_frames": len(hashes),
        "minimum_rgb_colors": minimum_colors,
        "maximum_rgb_colors": maximum_colors,
        "minimum_channel_stddev": round(minimum_stddev, 4),
    }


def verify_gradient(image: Image.Image) -> dict[str, Any]:
    rgb = image.convert("RGB")
    top = ImageStat.Stat(rgb.crop((0, 12, 160, 42))).mean
    lower = ImageStat.Stat(rgb.crop((0, 72, 160, 102))).mean
    distance = sum(abs(a - b) for a, b in zip(top, lower))
    if distance < 24.0:
        raise RuntimeError(f"atmospheric vertical gradient is not visible enough: distance={distance:.3f}")
    return {
        "top_mean_rgb": [round(value, 3) for value in top],
        "lower_mean_rgb": [round(value, 3) for value in lower],
        "absolute_rgb_distance": round(distance, 3),
    }


def labelled_scaled_image(source: Path, label: str, scale: int = 4) -> Image.Image:
    with Image.open(source) as image:
        base = image.convert("RGB").resize(
            (image.width * scale, image.height * scale),
            Image.Resampling.NEAREST,
        )
    bar_height = 34
    canvas = Image.new("RGB", (base.width, base.height + bar_height), (8, 12, 28))
    canvas.paste(base, (0, bar_height))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 8), label, font=select_font(16), fill=(238, 244, 255))
    return canvas


def create_screenshots(
    frame_paths: list[Path],
    trace: dict[str, Any],
    output_dir: Path,
) -> dict[str, Path]:
    screenshots = output_dir / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)
    selected = {
        "title": (int(trace["title_frame"]), "01-title.png", "TITLE / BASE SPRITE MAP"),
        "checkpoint_one": (
            int(trace["checkpoint_one_frame"]),
            "02-checkpoint-one.png",
            "CHECKPOINT 1 / PHASE GRADIENT",
        ),
        "checkpoint_two": (
            int(trace["checkpoint_two_frame"]),
            "03-checkpoint-two.png",
            "CHECKPOINT 2 / CAMERA OVERLAY",
        ),
        "victory": (int(trace["victory_frame"]), "04-victory.png", "VICTORY / GOAL GLOW"),
    }
    outputs: dict[str, Path] = {}
    panels: list[Image.Image] = []
    try:
        for key, (index, filename, label) in selected.items():
            if index < 0 or index >= len(frame_paths):
                raise RuntimeError(f"selected sprite frame outside sequence: {key}={index}")
            panel = labelled_scaled_image(frame_paths[index], label)
            destination = screenshots / filename
            panel.save(destination, format="PNG", optimize=False)
            outputs[key] = destination
            panels.append(panel)

        panel_width = max(panel.width for panel in panels)
        panel_height = max(panel.height for panel in panels)
        overview = Image.new("RGB", (panel_width * 2, panel_height * 2), (4, 6, 16))
        for position, panel in enumerate(panels):
            overview.paste(panel, ((position % 2) * panel_width, (position // 2) * panel_height))
        overview_path = screenshots / "00-sprite-gradient-overview.png"
        overview.save(overview_path, format="PNG", optimize=False)
        outputs["overview"] = overview_path
    finally:
        for panel in panels:
            panel.close()
    return outputs


def create_layer_comparison(input_dir: Path, output_dir: Path) -> tuple[Path, dict[str, Any]]:
    layer_dir = input_dir / "layers"
    manifest_path = layer_dir / "layer-manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("native overlay layer manifest is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("classification") != "VM81_SPRITE_OVERLAY_LAYER_COMPARISON_CAPTURED":
        raise RuntimeError("native layer comparison classification is missing")
    layer_paths = sorted(layer_dir.glob("[0-9][0-9]-*.ppm"))
    if len(layer_paths) != 5:
        raise RuntimeError(f"expected five overlay layers, found {len(layer_paths)}")
    hashes = [sha256_file(path) for path in layer_paths]
    if len(set(hashes)) != len(hashes):
        raise RuntimeError("one or more sprite overlay layers are visually identical")

    labels = [
        "BASE MAP",
        "+ ATMOSPHERE",
        "+ PHASE",
        "+ GLOWS",
        "FULL COMPOSITE",
    ]
    panels = [labelled_scaled_image(path, label, scale=3) for path, label in zip(layer_paths, labels)]
    try:
        width = max(panel.width for panel in panels)
        height = max(panel.height for panel in panels)
        sheet = Image.new("RGB", (width * len(panels), height), (4, 6, 16))
        for index, panel in enumerate(panels):
            sheet.paste(panel, (index * width, 0))
        output = output_dir / "screenshots" / "05-overlay-gradient-layers.png"
        sheet.save(output, format="PNG", optimize=False)
    finally:
        for panel in panels:
            panel.close()
    return output, {
        "source_frame": int(manifest["source_frame"]),
        "source_state_hash216": manifest["source_state_hash216"],
        "native_layer_hashes": [layer["hash216"] for layer in manifest["layers"]],
        "ppm_sha256": hashes,
    }


def encode_video(frame_dir: Path, output: Path, fps: int) -> None:
    ffmpeg = require_tool("ffmpeg")
    output.parent.mkdir(parents=True, exist_ok=True)
    run_checked(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(frame_dir / "frame_%06d.ppm"),
            "-vf",
            f"scale={VIDEO_SIZE[0]}:{VIDEO_SIZE[1]}:flags=neighbor",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "16",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    if not output.is_file() or output.stat().st_size <= 1024:
        raise RuntimeError("sprite MP4 was not produced or is implausibly small")


def parse_rate(value: str) -> Fraction:
    if not value or value == "0/0":
        return Fraction(0, 1)
    return Fraction(value)


def inspect_video(path: Path) -> dict[str, Any]:
    ffprobe = require_tool("ffprobe")
    result = run_checked(
        [
            ffprobe,
            "-v",
            "error",
            "-count_frames",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,width,height,r_frame_rate,avg_frame_rate,nb_read_frames,duration:format=duration,size",
            "-of",
            "json",
            str(path),
        ]
    )
    payload = json.loads(result.stdout)
    stream = payload.get("streams", [{}])[0]
    format_data = payload.get("format", {})
    return {
        "codec": stream.get("codec_name"),
        "width": int(stream.get("width", 0)),
        "height": int(stream.get("height", 0)),
        "r_frame_rate": stream.get("r_frame_rate", "0/0"),
        "avg_frame_rate": stream.get("avg_frame_rate", "0/0"),
        "frame_count": int(stream.get("nb_read_frames", 0)),
        "duration_seconds": float(stream.get("duration") or format_data.get("duration") or 0.0),
        "size_bytes": int(format_data.get("size", 0)),
    }


def verify_video(video: dict[str, Any], frame_count: int, fps: int) -> None:
    if video["codec"] != "h264":
        raise RuntimeError(f"unexpected sprite video codec: {video['codec']}")
    if (video["width"], video["height"]) != VIDEO_SIZE:
        raise RuntimeError(f"sprite video dimensions mismatch: {video['width']}x{video['height']}")
    if video["frame_count"] != frame_count:
        raise RuntimeError(f"sprite video frame count mismatch: {video['frame_count']} != {frame_count}")
    if parse_rate(video["r_frame_rate"]) != Fraction(fps, 1):
        raise RuntimeError(f"sprite video frame rate mismatch: {video['r_frame_rate']}")
    expected_duration = frame_count / fps
    if abs(video["duration_seconds"] - expected_duration) > (1.0 / fps + 0.02):
        raise RuntimeError(
            f"sprite video duration mismatch: {video['duration_seconds']:.6f} != {expected_duration:.6f}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    input_dir = args.input.resolve()
    output_dir = args.output.resolve()
    trace = load_trace(input_dir)
    frame_count = int(trace["frame_count"])
    fps = int(trace["ticks_per_second"])
    frame_paths = load_frame_paths(input_dir, frame_count)
    frame_metrics = inspect_frames(frame_paths)

    with Image.open(frame_paths[int(trace["title_frame"])]) as title_image:
        gradient_metrics = verify_gradient(title_image)

    output_dir.mkdir(parents=True, exist_ok=True)
    screenshots = create_screenshots(frame_paths, trace, output_dir)
    layer_sheet, layer_metrics = create_layer_comparison(input_dir, output_dir)
    video_path = output_dir / "vm81-platformer-sprite-gradients.mp4"
    encode_video(input_dir, video_path, fps)
    video = inspect_video(video_path)
    verify_video(video, frame_count, fps)

    receipt = {
        "contract": CONTRACT,
        "terminal_classification": CLASSIFICATION,
        "status": "VERIFIED",
        "source_capture_classification": trace["capture_classification"],
        "authoritative_state": trace["authoritative_state"],
        "mutation_authority": trace["mutation_authority"],
        "projection_authority": trace["projection_authority"],
        "logical_resolution": trace["logical_resolution"],
        "video_resolution": f"{VIDEO_SIZE[0]}x{VIDEO_SIZE[1]}",
        "frame_count": frame_count,
        "ticks_per_second": fps,
        "selected_frames": {
            "title": int(trace["title_frame"]),
            "checkpoint_one": int(trace["checkpoint_one_frame"]),
            "checkpoint_two": int(trace["checkpoint_two_frame"]),
            "victory": int(trace["victory_frame"]),
        },
        "sprite_map": {
            "atlas_tile_size": trace["atlas_tile_size"],
            "player_sprite_size": trace["player_sprite_size"],
            "overlay_layers": trace["overlay_layers"],
            "overlay_flags": int(trace["overlay_flags"]),
            "frame_metrics": frame_metrics,
            "gradient_metrics": gradient_metrics,
            "layer_comparison": layer_metrics,
        },
        "screenshots": {
            key: {"path": str(path.relative_to(output_dir)), "sha256": sha256_file(path)}
            for key, path in screenshots.items()
        },
        "overlay_layer_sheet": {
            "path": str(layer_sheet.relative_to(output_dir)),
            "sha256": sha256_file(layer_sheet),
        },
        "mp4": {
            "path": str(video_path.relative_to(output_dir)),
            "sha256": sha256_file(video_path),
            **video,
        },
        "state_projection_non_mutating": trace["state_projection_non_mutating"],
        "phase": trace["phase"],
        "opcode_coverage": trace["opcode_coverage"],
        "checkpoints_reached": int(trace["checkpoints_reached"]),
        "replay": trace["replay"],
        "frame_stream_hash72": trace["frame_stream_hash72"],
        "frame_stream_hash216": trace["frame_stream_hash216"],
        "final_hash72": trace["final_hash72"],
        "final_hash216": trace["final_hash216"],
    }
    receipt_path = output_dir / "sprite-modality-evidence.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
