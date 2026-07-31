"""Single-threaded HHS storybook-reel application runtime.

The browser is a live projection and control surface. Final media is produced by
``native_projects/hhs_storybook_reel`` over the inherited VM81 platformer,
sprite, texture, Hash72, and Hash216 ABIs. FFmpeg/ffprobe are used only for
codec transport, narration normalization, scaling, muxing, and inspection.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import time
import uuid
import zipfile
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from hhs_backend.runtime.hhs_storybook_reel_timing_v1 import (
    DURATION_SECONDS,
    FPS,
    FRAME_COUNT,
    STYLE_TEMPLATES,
    contextual_defaults,
    timing_file_text,
    timing_manifest,
    timings_from_alignment,
)
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

getcontext().prec = 28

VERSION = "HHS_STORYBOOK_REEL_STUDIO_V1"
AUTHORITY = "HHS_VM81_SINGLETON_STORYBOOK_REEL_AUTHORITY_V1"
MAX_AUDIO_BYTES = 64 * 1024 * 1024
MAX_TEXT_BYTES = 16_384
SUPPORTED_AUDIO_SUFFIXES = {
    ".aac",
    ".flac",
    ".m4a",
    ".mp3",
    ".mp4",
    ".ogg",
    ".opus",
    ".wav",
    ".webm",
}
STYLE_INTEGER_RANGES: Dict[str, Tuple[int, int]] = {
    "font_face": (0, 4),
    "font_effect": (0, 4),
    "font_scale": (1, 4),
    "letter_spacing": (0, 8),
    "effect_depth": (0, 12),
    "effect_speed": (1, 72),
    "effect_amplitude": (0, 24),
    "palette_mode": (0, 2),
    "phase_origin": (0, 4_294_967_295),
    "phase_scene_stride": (1, 71),
    "title_x": (0, 150),
    "title_y": (0, 136),
    "caption_x": (0, 150),
    "caption_y": (0, 136),
    "title_max_chars": (1, 40),
    "caption_chars_per_line": (1, 40),
    "caption_lines": (1, 4),
    "panel_opacity": (0, 255),
}
COLOR_KEYS = ("manual_x", "manual_y", "manual_z", "manual_w")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def _decimal_fraction(value: str) -> Fraction:
    return Fraction(Decimal(str(value)))


def _fraction_decimal(value: Fraction, places: int = 6) -> str:
    quantizer = Decimal(1).scaleb(-places)
    decimal = Decimal(value.numerator) / Decimal(value.denominator)
    return format(decimal.quantize(quantizer), "f")


def _safe_filename(value: str, fallback: str = "audio") -> str:
    name = Path(value or fallback).name
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip(".-")
    return stem[:120] or fallback


def _stable_zip(output: Path, files: Sequence[Tuple[Path, str]]) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source, archive_name in sorted(files, key=lambda item: item[1]):
            info = zipfile.ZipInfo(archive_name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, source.read_bytes())


class StorybookReelRuntime:
    """Restartable, serialized application runtime for captioned story reels."""

    def __init__(self, artifact_root: Optional[Path] = None) -> None:
        self.repo_root = Path(__file__).resolve().parents[2]
        configured = os.environ.get("HHS_STORYBOOK_REEL_ARTIFACT_ROOT")
        self.artifact_root = Path(artifact_root or configured or self.repo_root / "artifacts" / "storybook_reels")
        self.upload_root = self.artifact_root / "uploads"
        self.render_root = self.artifact_root / "renders"
        self.native_root = self.repo_root / "native_projects" / "hhs_storybook_reel"
        self.native_cli = self.native_root / "dist" / "hhs-storybook-reel"
        self.native_library = self.native_root / "dist" / "libhhs_storybook_reel.so"
        self._authority_lock = threading.RLock()
        self.upload_root.mkdir(parents=True, exist_ok=True)
        self.render_root.mkdir(parents=True, exist_ok=True)

    def status(self) -> Dict[str, Any]:
        return {
            "schema": "HHS_STORYBOOK_REEL_STATUS_V1",
            "version": VERSION,
            "ok": True,
            "authority": AUTHORITY,
            "duration_seconds": DURATION_SECONDS,
            "fps": FPS,
            "frame_count": FRAME_COUNT,
            "output_width": 1080,
            "output_height": 1920,
            "single_threaded": True,
            "parallel_computation_logic": False,
            "native_game_abi": "native_projects/hhs_vm81_game_level10",
            "native_reel_abi": "native_projects/hhs_storybook_reel",
            "ffmpeg_role": "codec_transport_scaling_muxing_only",
            "ffmpeg_available": shutil.which("ffmpeg") is not None,
            "ffprobe_available": shutil.which("ffprobe") is not None,
            "make_available": shutil.which("make") is not None,
            "native_cli_ready": self.native_cli.is_file(),
            "native_library_ready": self.native_library.is_file(),
            "max_audio_bytes": MAX_AUDIO_BYTES,
            "max_text_bytes": MAX_TEXT_BYTES,
            "templates": [
                {"id": template_id, **template}
                for template_id, template in STYLE_TEMPLATES.items()
            ],
            "studio_path": "/storybook-reel/",
        }

    @staticmethod
    def contextual_defaults(text: str) -> Dict[str, Any]:
        return contextual_defaults(text)

    def _run(
        self,
        arguments: Sequence[str],
        *,
        cwd: Optional[Path] = None,
        timeout: int = 900,
    ) -> subprocess.CompletedProcess[str]:
        environment = dict(os.environ)
        environment.update(
            {
                "OMP_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
                "VECLIB_MAXIMUM_THREADS": "1",
                "NUMEXPR_NUM_THREADS": "1",
            }
        )
        return subprocess.run(
            list(arguments),
            cwd=str(cwd) if cwd else None,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def _ensure_tools(self) -> None:
        missing = [tool for tool in ("ffmpeg", "ffprobe", "make") if shutil.which(tool) is None]
        if missing:
            raise RuntimeError(f"missing required media/build tools: {', '.join(missing)}")

    def _ensure_native(self) -> None:
        if self.native_cli.is_file() and self.native_library.is_file():
            return
        self._run(["make", "-C", str(self.native_root), "all"], timeout=900)
        if not self.native_cli.is_file() or not self.native_library.is_file():
            raise RuntimeError("native storybook-reel ABI build did not produce required surfaces")

    def _probe_audio(self, path: Path) -> Dict[str, Any]:
        result = self._run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "format=duration:stream=codec_name,sample_rate,channels",
                "-of",
                "json",
                str(path),
            ],
            timeout=120,
        )
        payload = json.loads(result.stdout or "{}")
        streams = payload.get("streams") or []
        if not streams:
            raise ValueError("uploaded file has no readable audio stream")
        duration_value = str((payload.get("format") or {}).get("duration") or "0")
        duration = _decimal_fraction(duration_value)
        if duration <= 0:
            raise ValueError("uploaded audio duration is not positive")
        stream = streams[0]
        return {
            "duration_fraction": duration,
            "duration_seconds": _fraction_decimal(duration),
            "codec_name": stream.get("codec_name"),
            "sample_rate": int(stream.get("sample_rate") or 0),
            "channels": int(stream.get("channels") or 0),
        }

    def upload_audio(self, data: bytes, filename: str, content_type: str = "application/octet-stream") -> Dict[str, Any]:
        if not data:
            raise ValueError("audio upload is empty")
        if len(data) > MAX_AUDIO_BYTES:
            raise ValueError(f"audio upload exceeds {MAX_AUDIO_BYTES} bytes")
        safe_name = _safe_filename(filename, "narration.wav")
        suffix = Path(safe_name).suffix.lower()
        if suffix not in SUPPORTED_AUDIO_SUFFIXES:
            raise ValueError(f"unsupported audio extension: {suffix or 'none'}")
        self._ensure_tools()
        token = uuid.uuid4().hex
        audio_id = f"audio:{token}"
        stored = self.upload_root / f"{token}{suffix}"
        stored.write_bytes(data)
        try:
            probe = self._probe_audio(stored)
        except Exception:
            stored.unlink(missing_ok=True)
            raise
        transport_sha256 = hashlib.sha256(data).hexdigest()
        record = {
            "schema": "HHS_STORYBOOK_REEL_AUDIO_INGRESS_V1",
            "audio_id": audio_id,
            "original_filename": safe_name,
            "stored_filename": stored.name,
            "content_type": content_type,
            "size_bytes": len(data),
            "sha256_transport_hint": transport_sha256,
            "duration_seconds": probe["duration_seconds"],
            "codec_name": probe["codec_name"],
            "sample_rate": probe["sample_rate"],
            "channels": probe["channels"],
            "created_at_unix_ms": int(time.time() * 1000),
            "authority": AUTHORITY,
        }
        record["audio_root_hash72"] = hash72("HHS_STORYBOOK_REEL_AUDIO_INGRESS_V1", record)
        (self.upload_root / f"{token}.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return {
            "ok": True,
            "status": "STORYBOOK_REEL_AUDIO_READY",
            **record,
        }

    def _audio_record(self, audio_id: str) -> Tuple[Dict[str, Any], Path, Fraction]:
        match = re.fullmatch(r"audio:([0-9a-f]{32})", str(audio_id or ""))
        if not match:
            raise ValueError("invalid audio_id")
        token = match.group(1)
        metadata_path = self.upload_root / f"{token}.json"
        if not metadata_path.is_file():
            raise FileNotFoundError("audio upload does not exist")
        record = json.loads(metadata_path.read_text(encoding="utf-8"))
        source_path = self.upload_root / str(record["stored_filename"])
        if not source_path.is_file():
            raise FileNotFoundError("audio payload is missing")
        duration = _decimal_fraction(str(record["duration_seconds"]))
        return record, source_path, duration

    @staticmethod
    def _parse_color(value: Any, fallback: Mapping[str, int]) -> Dict[str, int]:
        if isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            return {
                "r": int(value[1:3], 16),
                "g": int(value[3:5], 16),
                "b": int(value[5:7], 16),
            }
        if isinstance(value, Mapping):
            return {
                component: max(0, min(255, int(value.get(component, fallback.get(component, 0)))))
                for component in ("r", "g", "b")
            }
        return {component: int(fallback.get(component, 0)) for component in ("r", "g", "b")}

    def _style(self, text: str, template_id: Optional[str], overrides: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        defaults = contextual_defaults(text)
        resolved_id = str(template_id or defaults["template_id"])
        if resolved_id not in STYLE_TEMPLATES:
            raise ValueError(f"unknown reel template: {resolved_id}")
        style = {
            key: value
            for key, value in STYLE_TEMPLATES[resolved_id].items()
            if key not in {"label", "description"}
        }
        override_values = dict(overrides or {})
        for key, bounds in STYLE_INTEGER_RANGES.items():
            if key not in override_values:
                continue
            value = int(override_values[key])
            if value < bounds[0] or value > bounds[1]:
                raise ValueError(f"style {key} must be between {bounds[0]} and {bounds[1]}")
            style[key] = value
        palette = defaults["palette"]["colors"]
        fallback_colors = {
            "manual_x": self._parse_color(palette["x"], {}),
            "manual_y": self._parse_color(palette["y"], {}),
            "manual_z": self._parse_color(palette["z"], {}),
            "manual_w": self._parse_color(palette["w"], {}),
        }
        for key in COLOR_KEYS:
            style[key] = self._parse_color(override_values.get(key), fallback_colors[key])
        return {
            "template_id": resolved_id,
            "template_label": STYLE_TEMPLATES[resolved_id]["label"],
            "values": style,
            "contextual_palette": defaults["palette"],
        }

    @staticmethod
    def _atempo_chain(source_duration: Fraction) -> str:
        factor = source_duration / Fraction(DURATION_SECONDS, 1)
        parts: List[Fraction] = []
        while factor > 2:
            parts.append(Fraction(2, 1))
            factor /= 2
        while factor < Fraction(1, 2):
            parts.append(Fraction(1, 2))
            factor *= 2
        if factor != 1:
            parts.append(factor)
        filters = [f"atempo={_fraction_decimal(part, 8)}" for part in parts]
        filters.extend(
            [
                "aresample=48000",
                f"apad=pad_dur={DURATION_SECONDS}",
                f"atrim=duration={DURATION_SECONDS}",
            ]
        )
        return ",".join(filters)

    @staticmethod
    def _style_cli_arguments(style: Mapping[str, Any]) -> List[str]:
        values = style["values"]
        arguments: List[str] = []
        for key in STYLE_INTEGER_RANGES:
            cli_key = key.replace("_", "-")
            arguments.extend([f"--{cli_key}", str(values[key])])
        for plane in ("x", "y", "z", "w"):
            color = values[f"manual_{plane}"]
            for component in ("r", "g", "b"):
                arguments.extend([f"--manual-{plane}-{component}", str(color[component])])
        return arguments

    def _normalize_audio(self, source: Path, output: Path, duration: Fraction) -> None:
        self._run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-i",
                str(source),
                "-vn",
                "-af",
                self._atempo_chain(duration),
                "-ar",
                "48000",
                "-ac",
                "1",
                "-c:a",
                "pcm_s16le",
                "-threads",
                "1",
                str(output),
            ],
            timeout=900,
        )

    def _encode_mp4(self, styled_rgba: Path, narration_wav: Path, output: Path) -> None:
        filter_graph = (
            "[0:v]scale=1080:972:flags=neighbor,"
            "pad=1080:1920:0:474:color=0x0b0910[v]"
        )
        self._run(
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
                str(FPS),
                "-i",
                str(styled_rgba),
                "-i",
                str(narration_wav),
                "-filter_complex",
                filter_graph,
                "-map",
                "[v]",
                "-map",
                "1:a:0",
                "-frames:v",
                str(FRAME_COUNT),
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                "-r",
                str(FPS),
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                "-threads",
                "1",
                "-filter_threads",
                "1",
                "-filter_complex_threads",
                "1",
                str(output),
            ],
            timeout=1800,
        )

    def _probe_video(self, path: Path) -> Dict[str, Any]:
        result = self._run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration,size:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
                "-of",
                "json",
                str(path),
            ],
            timeout=120,
        )
        payload = json.loads(result.stdout or "{}")
        streams = payload.get("streams") or []
        video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
        audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
        if not video or not audio:
            raise RuntimeError("generated MP4 is missing video or audio stream")
        duration = _decimal_fraction(str((payload.get("format") or {}).get("duration") or "0"))
        if duration < Fraction(899, 10) or duration > Fraction(901, 10):
            raise RuntimeError(f"generated MP4 duration is outside 90-second acceptance: {_fraction_decimal(duration)}")
        if video.get("codec_name") != "h264" or int(video.get("width") or 0) != 1080 or int(video.get("height") or 0) != 1920:
            raise RuntimeError("generated MP4 video stream failed codec or dimension acceptance")
        if str(video.get("r_frame_rate")) != f"{FPS}/1":
            raise RuntimeError("generated MP4 frame rate is not 30 fps")
        return {
            "duration_seconds": _fraction_decimal(duration),
            "size_bytes": int((payload.get("format") or {}).get("size") or 0),
            "video_codec": video.get("codec_name"),
            "audio_codec": audio.get("codec_name"),
            "width": int(video.get("width") or 0),
            "height": int(video.get("height") or 0),
            "frame_rate": video.get("r_frame_rate"),
            "audio_sample_rate": int(audio.get("sample_rate") or 0),
            "audio_channels": int(audio.get("channels") or 0),
        }

    def _artifact_record(self, artifact_id: str) -> Tuple[Dict[str, Any], Path]:
        match = re.fullmatch(r"reel:([0-9a-f]{32})", str(artifact_id or ""))
        if not match:
            raise ValueError("invalid artifact_id")
        directory = self.render_root / match.group(1)
        metadata_path = directory / "artifact.json"
        if not metadata_path.is_file():
            raise FileNotFoundError("storybook-reel artifact does not exist")
        return json.loads(metadata_path.read_text(encoding="utf-8")), directory

    def artifact(self, artifact_id: str) -> Dict[str, Any]:
        record, _ = self._artifact_record(artifact_id)
        return record

    def artifact_path(self, artifact_id: str, kind: str) -> Path:
        record, directory = self._artifact_record(artifact_id)
        filename_key = {"zip": "zip_filename", "video": "video_filename"}.get(kind)
        if not filename_key:
            raise ValueError("unknown artifact kind")
        path = directory / str(record[filename_key])
        if not path.is_file():
            raise FileNotFoundError("artifact payload is missing")
        return path

    def generate(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        text = str(payload.get("text") or "")
        title = str(payload.get("title") or "HHS STORYBOOK").strip() or "HHS STORYBOOK"
        if not text.strip():
            raise ValueError("matching narration text is required")
        if len(text.encode("utf-8")) > MAX_TEXT_BYTES:
            raise ValueError(f"text exceeds {MAX_TEXT_BYTES} UTF-8 bytes")
        if len(title.encode("utf-8")) > 128:
            raise ValueError("title exceeds 128 UTF-8 bytes")
        audio_record, audio_path, source_duration = self._audio_record(str(payload.get("audio_id") or ""))
        style = self._style(text, payload.get("template_id"), payload.get("style"))
        alignment = payload.get("alignment")
        if alignment is not None and not isinstance(alignment, Mapping):
            raise ValueError("alignment must be a JSON object")
        spans, timing_source = timings_from_alignment(text, alignment, source_duration)
        if not spans:
            raise ValueError("caption timing could not be derived")
        token = uuid.uuid4().hex
        artifact_id = f"reel:{token}"
        directory = self.render_root / token
        directory.mkdir(parents=True, exist_ok=False)
        story_path = directory / "story.txt"
        style_path = directory / "style.json"
        request_path = directory / "request.json"
        timing_text_path = directory / "timing.txt"
        timing_json_path = directory / "timing.json"
        base_rgba = directory / "base.rgba"
        styled_rgba = directory / "styled.rgba"
        generated_pcm = directory / "native-score.pcm"
        native_manifest_path = directory / "native-manifest.json"
        narration_wav = directory / "narration-normalized.wav"
        video_path = directory / "storybook-reel.mp4"
        receipt_path = directory / "receipt.json"
        readme_path = directory / "README.md"
        zip_path = directory / "storybook-reel-package.zip"
        story_path.write_text(text, encoding="utf-8")
        style_path.write_text(json.dumps(style, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        timing_text_path.write_text(timing_file_text(spans), encoding="utf-8")
        timing_payload = timing_manifest(spans, timing_source)
        timing_payload["audio_id"] = audio_record["audio_id"]
        timing_payload["source_audio_duration_seconds"] = audio_record["duration_seconds"]
        timing_json_path.write_text(json.dumps(timing_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        request_record = {
            "schema": "HHS_STORYBOOK_REEL_REQUEST_V1",
            "artifact_id": artifact_id,
            "audio_id": audio_record["audio_id"],
            "title": title,
            "template_id": style["template_id"],
            "style": style["values"],
            "timing_source": timing_source,
            "duration_seconds": DURATION_SECONDS,
            "fps": FPS,
            "frame_count": FRAME_COUNT,
            "single_threaded": True,
            "parallel_computation_logic": False,
            "authority": AUTHORITY,
        }
        request_record["request_root_hash72"] = hash72("HHS_STORYBOOK_REEL_REQUEST_V1", request_record)
        request_path.write_text(json.dumps(request_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        started = time.perf_counter_ns()
        with self._authority_lock:
            self._ensure_tools()
            self._ensure_native()
            native_arguments = [
                str(self.native_cli),
                "--text-file",
                str(story_path),
                "--base-rgba",
                str(base_rgba),
                "--styled-rgba",
                str(styled_rgba),
                "--pcm-output",
                str(generated_pcm),
                "--manifest",
                str(native_manifest_path),
                "--timing-file",
                str(timing_text_path),
                "--title",
                title,
                *self._style_cli_arguments(style),
            ]
            native_result = self._run(native_arguments, cwd=self.repo_root, timeout=1800)
            self._normalize_audio(audio_path, narration_wav, source_duration)
            self._encode_mp4(styled_rgba, narration_wav, video_path)
        elapsed_ns = time.perf_counter_ns() - started
        probe = self._probe_video(video_path)
        native_manifest = json.loads(native_manifest_path.read_text(encoding="utf-8"))
        mp4_sha256 = _sha256_file(video_path)
        story_sha256 = _sha256_file(story_path)
        style_sha256 = _sha256_file(style_path)
        timing_sha256 = _sha256_file(timing_json_path)
        readme_path.write_text(
            "# HHS Storybook Reel Package\n\n"
            "This package contains a 90-second vertical H.264/AAC MP4 generated from the included narration and matching text. "
            "Visual frames were produced by the native VM81 platformer, sprite-map, texture, storybook, Hash72, and Hash216 ABI surfaces. "
            "FFmpeg was used only for narration normalization, integer-scale presentation, codec encoding, and MP4 muxing.\n\n"
            f"- Template: {style['template_label']}\n"
            f"- Caption timing: {timing_source}\n"
            "- Parallel computation: disabled\n"
            "- Canonical duration: 90 seconds\n",
            encoding="utf-8",
        )
        receipt = {
            "schema": "HHS_STORYBOOK_REEL_RECEIPT_V1",
            "classification": "HHS_90_SECOND_STORYBOOK_REEL_APPLICATION_VERIFIED",
            "artifact_id": artifact_id,
            "request_root_hash72": request_record["request_root_hash72"],
            "audio_root_hash72": audio_record["audio_root_hash72"],
            "story_sha256_transport_hint": story_sha256,
            "style_sha256_transport_hint": style_sha256,
            "timing_sha256_transport_hint": timing_sha256,
            "mp4_sha256_transport_hint": mp4_sha256,
            "native_manifest": native_manifest,
            "video_probe": probe,
            "elapsed_ns": elapsed_ns,
            "single_threaded": True,
            "parallel_computation_logic": False,
            "authority": AUTHORITY,
            "native_stdout": native_result.stdout.strip(),
        }
        receipt["receipt_hash72"] = hash72("HHS_STORYBOOK_REEL_RECEIPT_V1", receipt)
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        package_files = [
            (video_path, "storybook-reel.mp4"),
            (audio_path, f"source/{audio_record['original_filename']}"),
            (story_path, "source/story.txt"),
            (style_path, "source/style.json"),
            (timing_json_path, "source/timing.json"),
            (request_path, "evidence/request.json"),
            (native_manifest_path, "evidence/native-manifest.json"),
            (receipt_path, "evidence/receipt.json"),
            (readme_path, "README.md"),
        ]
        _stable_zip(zip_path, package_files)
        zip_sha256 = _sha256_file(zip_path)
        record = {
            "schema": "HHS_STORYBOOK_REEL_ARTIFACT_V1",
            "version": VERSION,
            "ok": True,
            "status": "STORYBOOK_REEL_PACKAGE_READY",
            "classification": receipt["classification"],
            "artifact_id": artifact_id,
            "audio_id": audio_record["audio_id"],
            "title": title,
            "template_id": style["template_id"],
            "template_label": style["template_label"],
            "timing_source": timing_source,
            "timing_span_count": len(spans),
            "duration_seconds": DURATION_SECONDS,
            "fps": FPS,
            "frame_count": FRAME_COUNT,
            "width": probe["width"],
            "height": probe["height"],
            "video_filename": video_path.name,
            "zip_filename": zip_path.name,
            "video_size_bytes": video_path.stat().st_size,
            "zip_size_bytes": zip_path.stat().st_size,
            "video_sha256_transport_hint": mp4_sha256,
            "zip_sha256_transport_hint": zip_sha256,
            "receipt_hash72": receipt["receipt_hash72"],
            "request_root_hash72": request_record["request_root_hash72"],
            "native_story_hash72": native_manifest.get("story_hash72"),
            "native_frame_chain_hash72": native_manifest.get("styled_frame_chain_hash72"),
            "single_threaded": True,
            "parallel_computation_logic": False,
            "download_url": f"/api/runtime/storybook-reel/artifacts/{artifact_id}/download.zip",
            "video_url": f"/api/runtime/storybook-reel/artifacts/{artifact_id}/video.mp4",
            "created_at_unix_ms": int(time.time() * 1000),
            "authority": AUTHORITY,
        }
        (directory / "artifact.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        for intermediate in (base_rgba, styled_rgba, generated_pcm, narration_wav):
            intermediate.unlink(missing_ok=True)
        return record


STORYBOOK_REEL_RUNTIME = StorybookReelRuntime()
