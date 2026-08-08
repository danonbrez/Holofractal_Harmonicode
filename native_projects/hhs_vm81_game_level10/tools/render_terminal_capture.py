#!/usr/bin/env python3
"""Render and verify VM81 terminal presentation evidence.

The C runtime writes the exact text frames used by the interactive terminal
projection. This tool renders those frames into PNG screenshots and an MP4,
then emits a receipt binding the user-visible media to the authoritative VM81
replay trace and final Hash72/Hash216 state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

from hhs_capture_process_utils_v1 import parse_rate, run_checked

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - exercised by environment gate
    raise SystemExit(
        "Pillow is required for modality capture. Install python3-pil or pillow."
    ) from exc


CONTRACT = "HHS-VM81-USER-MODALITY-EVIDENCE-V1"
CLASSIFICATION = "VM81_USER_MODALITY_PRESENTATION_EVIDENCE_VERIFIED"
FONT_CANDIDATES = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSansMono.ttf"),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_tool(name: str) -> str:
    resolved = shutil.which(name)
    if not resolved:
        raise RuntimeError(f"required executable not found: {name}")
    return resolved


def select_font() -> Path:
    for candidate in FONT_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise RuntimeError("DejaVu Sans Mono font was not found")


def load_frames(input_dir: Path, trace: dict[str, Any]) -> list[tuple[Path, str, bytes]]:
    paths = sorted(input_dir.glob("frame_*.txt"))
    expected_count = int(trace["frame_count"])
    if len(paths) != expected_count:
        raise RuntimeError(
            f"frame count mismatch: trace={expected_count}, files={len(paths)}"
        )
    frames: list[tuple[Path, str, bytes]] = []
    for index, path in enumerate(paths):
        expected_name = f"frame_{index:06d}.txt"
        if path.name != expected_name:
            raise RuntimeError(f"non-canonical frame sequence: {path.name} != {expected_name}")
        data = path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise RuntimeError(f"frame is not UTF-8: {path}") from exc
        if not text.endswith("\n"):
            raise RuntimeError(f"frame is not newline-terminated: {path}")
        frames.append((path, text, data))
    return frames


def verify_semantic_frames(frames: list[tuple[Path, str, bytes]], trace: dict[str, Any]) -> dict[str, int]:
    indices = {
        "title": int(trace["title_frame"]),
        "checkpoint_one": int(trace["checkpoint_one_frame"]),
        "checkpoint_two": int(trace["checkpoint_two_frame"]),
        "victory": int(trace["victory_frame"]),
    }
    frame_count = len(frames)
    for name, index in indices.items():
        if index < 0 or index >= frame_count:
            raise RuntimeError(f"{name} frame index is outside the capture: {index}")

    title = frames[indices["title"]][1]
    checkpoint_one = frames[indices["checkpoint_one"]][1]
    checkpoint_two = frames[indices["checkpoint_two"]][1]
    victory = frames[indices["victory"]][1]

    required = (
        ("title", title, ("phase=TITLE", "Press ENTER to start", "Reach G")),
        ("checkpoint one", checkpoint_one, ("checkpoint=1/2", "phase=RUNNING")),
        ("checkpoint two", checkpoint_two, ("checkpoint=2/2", "phase=RUNNING")),
        ("victory", victory, ("phase=VICTORY", "VICTORY -", "checkpoint=2/2")),
    )
    for label, text, needles in required:
        for needle in needles:
            if needle not in text:
                raise RuntimeError(f"{label} frame is missing required presentation text: {needle}")

    unique_text_hashes = {sha256_bytes(item[2]) for item in frames}
    if len(unique_text_hashes) < 16:
        raise RuntimeError(
            f"capture has insufficient visual/state variation: {len(unique_text_hashes)} unique frames"
        )
    if sum(character != " " and character != "\n" for character in title) < 100:
        raise RuntimeError("title frame is effectively blank")
    if sum(character != " " and character != "\n" for character in victory) < 100:
        raise RuntimeError("victory frame is effectively blank")
    return indices


def frame_dimensions(frames: list[tuple[Path, str, bytes]]) -> tuple[int, int]:
    max_columns = 0
    max_rows = 0
    for _, text, _ in frames:
        lines = text.splitlines()
        max_rows = max(max_rows, len(lines))
        max_columns = max(max_columns, max((len(line) for line in lines), default=0))
    if max_columns == 0 or max_rows == 0:
        raise RuntimeError("capture contains no renderable text")
    return max_columns, max_rows


def render_png_frames(
    frames: list[tuple[Path, str, bytes]],
    output_frames: Path,
    font_path: Path,
) -> tuple[int, int, list[Path]]:
    font = ImageFont.truetype(str(font_path), size=16)
    probe_box = font.getbbox("M")
    cell_width = max(1, probe_box[2] - probe_box[0])
    line_height = max(1, probe_box[3] - probe_box[1] + 4)
    columns, rows = frame_dimensions(frames)
    margin = 12
    width = margin * 2 + columns * cell_width
    height = margin * 2 + rows * line_height
    if width % 2:
        width += 1
    if height % 2:
        height += 1

    output_frames.mkdir(parents=True, exist_ok=True)
    rendered_paths: list[Path] = []
    for index, (_, text, _) in enumerate(frames):
        image = Image.new("RGB", (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        for row, line in enumerate(text.splitlines()):
            draw.text(
                (margin, margin + row * line_height),
                line,
                font=font,
                fill=(240, 240, 240),
                spacing=0,
            )
        path = output_frames / f"frame_{index:06d}.png"
        image.save(path, format="PNG", optimize=False)
        if path.stat().st_size == 0:
            raise RuntimeError(f"empty PNG frame generated: {path}")
        rendered_paths.append(path)
    return width, height, rendered_paths


def create_screenshots(
    rendered_frames: list[Path],
    indices: dict[str, int],
    screenshots_dir: Path,
) -> dict[str, Path]:
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Path] = {}
    names = {
        "title": "01-title.png",
        "checkpoint_one": "02-checkpoint-one.png",
        "checkpoint_two": "03-checkpoint-two.png",
        "victory": "04-victory.png",
    }
    for key, filename in names.items():
        source = rendered_frames[indices[key]]
        destination = screenshots_dir / filename
        shutil.copyfile(source, destination)
        outputs[key] = destination

    images = [Image.open(outputs[key]).convert("RGB") for key in names]
    try:
        width = max(image.width for image in images)
        height = max(image.height for image in images)
        overview = Image.new("RGB", (width * 2, height * 2), (0, 0, 0))
        for position, image in enumerate(images):
            overview.paste(image, ((position % 2) * width, (position // 2) * height))
        overview_path = screenshots_dir / "00-overview.png"
        overview.save(overview_path, format="PNG", optimize=False)
        outputs["overview"] = overview_path
    finally:
        for image in images:
            image.close()
    return outputs


def encode_video(frames_dir: Path, video_path: Path, fps: int) -> None:
    ffmpeg = require_tool("ffmpeg")
    video_path.parent.mkdir(parents=True, exist_ok=True)
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
            str(frames_dir / "frame_%06d.png"),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(video_path),
        ]
    )
    if not video_path.is_file() or video_path.stat().st_size == 0:
        raise RuntimeError("MP4 encoder did not produce a nonempty file")


def inspect_video(video_path: Path) -> dict[str, Any]:
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
            str(video_path),
        ]
    )
    payload = json.loads(result.stdout)
    streams = payload.get("streams", [])
    if len(streams) != 1:
        raise RuntimeError(f"expected exactly one video stream, found {len(streams)}")
    stream = streams[0]
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


def verify_video(
    video: dict[str, Any],
    expected_frames: int,
    fps: int,
    width: int,
    height: int,
) -> None:
    if video["codec"] != "h264":
        raise RuntimeError(f"unexpected MP4 codec: {video['codec']}")
    if video["width"] != width or video["height"] != height:
        raise RuntimeError(
            f"video dimensions mismatch: {video['width']}x{video['height']} != {width}x{height}"
        )
    if video["frame_count"] != expected_frames:
        raise RuntimeError(
            f"video frame count mismatch: {video['frame_count']} != {expected_frames}"
        )
    if parse_rate(video["r_frame_rate"]) != Fraction(fps, 1):
        raise RuntimeError(f"video frame rate mismatch: {video['r_frame_rate']} != {fps}/1")
    expected_duration = expected_frames / fps
    if abs(video["duration_seconds"] - expected_duration) > (1.0 / fps + 0.02):
        raise RuntimeError(
            f"video duration mismatch: {video['duration_seconds']:.6f} != {expected_duration:.6f}"
        )
    if video["size_bytes"] <= 1024:
        raise RuntimeError("MP4 is implausibly small")


def build_frame_chain(frames: list[tuple[Path, str, bytes]]) -> str:
    chain = hashlib.sha256()
    for index, (_, _, data) in enumerate(frames):
        chain.update(index.to_bytes(8, "big"))
        chain.update(hashlib.sha256(data).digest())
    return chain.hexdigest()


def write_manifest(
    output_dir: Path,
    input_dir: Path,
    trace: dict[str, Any],
    frames: list[tuple[Path, str, bytes]],
    font_path: Path,
    width: int,
    height: int,
    indices: dict[str, int],
    screenshots: dict[str, Path],
    video_path: Path,
    video: dict[str, Any],
) -> Path:
    trace_path = input_dir / "capture-trace.json"
    manifest = {
        "contract": CONTRACT,
        "terminal_classification": CLASSIFICATION,
        "status": "VERIFIED",
        "source_capture_classification": trace["capture_classification"],
        "input_modality": trace["input_modality"],
        "output_modality": trace["output_modality"],
        "presentation_evidence": {
            "exact_text_frame_count": len(frames),
            "text_frame_chain_sha256": build_frame_chain(frames),
            "text_trace_sha256": sha256_file(trace_path),
            "title_frame": indices["title"],
            "checkpoint_one_frame": indices["checkpoint_one"],
            "checkpoint_two_frame": indices["checkpoint_two"],
            "victory_frame": indices["victory"],
            "unique_text_frames": len({sha256_bytes(item[2]) for item in frames}),
        },
        "rasterization": {
            "renderer": "Pillow",
            "font_path": str(font_path),
            "font_sha256": sha256_file(font_path),
            "pixel_dimensions": {"width": width, "height": height},
            "background_rgb": [0, 0, 0],
            "foreground_rgb": [240, 240, 240],
        },
        "screenshots": {
            key: {
                "path": str(path.relative_to(output_dir)),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
            for key, path in sorted(screenshots.items())
        },
        "video": {
            "path": str(video_path.relative_to(output_dir)),
            "sha256": sha256_file(video_path),
            **video,
        },
        "authoritative_correspondence": {
            "phase": trace["phase"],
            "opcode_coverage": trace["opcode_coverage"],
            "checkpoints_reached": trace["checkpoints_reached"],
            "replay": trace["replay"],
            "final_hash72": trace["final_hash72"],
            "final_hash216": trace["final_hash216"],
        },
        "closure": {
            "source_modality_evidence": "VERIFIED",
            "translation_evidence": "VERIFIED",
            "execution_evidence": "VERIFIED",
            "presentation_modality_evidence": "VERIFIED",
            "screenshots": "VERIFIED",
            "mp4": "VERIFIED",
        },
    }
    manifest_path = output_dir / "modality-evidence.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="directory containing capture-trace.json and frame_*.txt")
    parser.add_argument("--output", required=True, type=Path, help="directory for PNG, MP4, and evidence receipt")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = args.input.resolve()
    output_dir = args.output.resolve()
    trace_path = input_dir / "capture-trace.json"
    if not trace_path.is_file():
        raise RuntimeError(f"capture trace not found: {trace_path}")
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    if trace.get("contract") != CONTRACT:
        raise RuntimeError(f"unexpected capture contract: {trace.get('contract')}")
    if trace.get("capture_classification") != "VM81_TERMINAL_FRAME_STREAM_CAPTURED":
        raise RuntimeError("terminal frame stream is not classified as captured")
    if trace.get("phase") != "VICTORY" or trace.get("opcode_coverage") != "19/19":
        raise RuntimeError("authoritative execution did not reach victory with 19/19 opcode closure")
    if trace.get("checkpoints_reached") != 2 or trace.get("replay") != "MATCH":
        raise RuntimeError("authoritative checkpoint or replay closure is incomplete")

    fps = int(trace["ticks_per_second"])
    if fps <= 0:
        raise RuntimeError(f"invalid capture frame rate: {fps}")
    frames = load_frames(input_dir, trace)
    indices = verify_semantic_frames(frames, trace)
    font_path = select_font()

    if output_dir.exists():
        shutil.rmtree(output_dir)
    frames_dir = output_dir / "frames"
    screenshots_dir = output_dir / "screenshots"
    width, height, rendered_frames = render_png_frames(frames, frames_dir, font_path)
    screenshots = create_screenshots(rendered_frames, indices, screenshots_dir)
    video_path = output_dir / "vm81-platformer-playthrough.mp4"
    encode_video(frames_dir, video_path, fps)
    video = inspect_video(video_path)
    verify_video(video, len(frames), fps, width, height)
    manifest_path = write_manifest(
        output_dir,
        input_dir,
        trace,
        frames,
        font_path,
        width,
        height,
        indices,
        screenshots,
        video_path,
        video,
    )
    print(manifest_path.read_text(encoding="utf-8"), end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"modality capture verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
