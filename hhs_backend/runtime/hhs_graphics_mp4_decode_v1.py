"""Canonical read-only MP4 decode and timeline identity for HHS Pass 181.

FFprobe supplies declared stream metadata. FFmpeg decodes each video stream to
RGBA raw frames and each audio stream to PCM signed 32-bit little-endian frames,
then the framehash muxer emits SHA-256 identities with exact DTS, PTS, duration,
and time-base records. The reference file is never copied or modified.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

from hhs_installer.canonical import canonical_bytes, hash72, hash216, stable

CONTRACT = "HHS-P181-NCSR-GHIR-VM81-H72-H216"
AUTHORITY = "HHS_VM81_SINGLETON_GRAPHICS_HYDRATION_AUTHORITY_V1"
DECODE_MANIFEST_DOMAIN = "HHS-P181-CANONICAL-MP4-DECODE-MANIFEST-V1"
TIMELINE_IDENTITY_DOMAIN = "HHS-P181-CANONICAL-MEDIA-TIMELINE-V1"
DECODE_RECEIPT_DOMAIN = "HHS-P181-CANONICAL-MP4-DECODE-RECEIPT-V1"
CANONICAL_VIDEO_PIXEL_FORMAT = "rgba"
CANONICAL_AUDIO_CODEC = "pcm_s32le"
CANONICAL_HASH_ALGORITHM = "sha256"
DEFAULT_TIMEOUT_SECONDS = 3_600


class Mp4DecodeError(ValueError):
    """Raised when canonical media inspection or decoding fails closed."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _artifact_filename(canonical_identity: str) -> str:
    return hashlib.sha256(canonical_identity.encode("utf-8")).hexdigest() + ".json"


def _tool_environment() -> Dict[str, str]:
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
    return environment


def _run(arguments: Sequence[str], *, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    try:
        result = subprocess.run(
            list(arguments),
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_tool_environment(),
        )
    except FileNotFoundError as error:
        raise Mp4DecodeError(f"P181_MEDIA_TOOL_MISSING:{arguments[0]}") from error
    except subprocess.TimeoutExpired as error:
        raise Mp4DecodeError(f"P181_MEDIA_TOOL_TIMEOUT:{arguments[0]}") from error
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "").strip().replace("\n", " ")[-600:]
        raise Mp4DecodeError(f"P181_MEDIA_TOOL_FAILED:{arguments[0]}:{detail}") from error
    return result.stdout


def _tool_version(executable: str) -> str:
    output = _run([executable, "-version"], timeout=60)
    line = output.splitlines()[0].strip() if output.splitlines() else ""
    if not line:
        raise Mp4DecodeError(f"P181_MEDIA_TOOL_VERSION_UNAVAILABLE:{executable}")
    return line


def _exact_token(value: str) -> int | str:
    token = value.strip()
    try:
        return int(token)
    except ValueError:
        return token


def _parse_framehash(output: str) -> Dict[str, Any]:
    headers: Dict[str, str] = {}
    records = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            body = line[1:].strip()
            if body.startswith("stream#"):
                continue
            if ":" in body:
                key, value = body.split(":", 1)
                headers[key.strip()] = value.strip()
            continue
        columns = [column.strip() for column in line.split(",")]
        if len(columns) != 6:
            raise Mp4DecodeError("P181_FRAMEHASH_RECORD_INVALID")
        records.append(
            {
                "stream": _exact_token(columns[0]),
                "dts": _exact_token(columns[1]),
                "pts": _exact_token(columns[2]),
                "duration": _exact_token(columns[3]),
                "size_bytes": _exact_token(columns[4]),
                "sha256": columns[5].lower(),
            }
        )
    if headers.get("hash", "").upper() != "SHA256":
        raise Mp4DecodeError("P181_FRAMEHASH_SHA256_REQUIRED")
    return {"headers": headers, "records": records}


def _probe(path: Path) -> Dict[str, Any]:
    entries = (
        "format=format_name,format_long_name,start_time,duration,size,bit_rate,probe_score:"
        "stream=index,codec_type,codec_name,codec_long_name,profile,codec_tag_string,"
        "width,height,pix_fmt,r_frame_rate,avg_frame_rate,time_base,start_pts,start_time,"
        "duration_ts,duration,nb_frames,nb_read_frames,sample_fmt,sample_rate,channels,"
        "channel_layout,bit_rate"
    )
    output = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-count_frames",
            "-show_format",
            "-show_streams",
            "-show_entries",
            entries,
            "-of",
            "json",
            str(path),
        ]
    )
    try:
        payload = json.loads(output, parse_float=str)
    except json.JSONDecodeError as error:
        raise Mp4DecodeError("P181_FFPROBE_JSON_INVALID") from error
    streams = payload.get("streams")
    if not isinstance(streams, list) or not streams:
        raise Mp4DecodeError("P181_MP4_STREAMS_REQUIRED")
    payload["streams"] = sorted(
        [stable(stream) for stream in streams],
        key=lambda stream: int(stream.get("index", 0)),
    )
    payload["format"] = stable(payload.get("format") or {})
    return payload


def _stream_framehash(path: Path, stream: Mapping[str, Any]) -> Dict[str, Any]:
    source_index = int(stream.get("index", -1))
    codec_type = str(stream.get("codec_type") or "")
    if source_index < 0 or codec_type not in {"video", "audio"}:
        raise Mp4DecodeError("P181_DECODE_STREAM_INVALID")

    command = [
        "ffmpeg",
        "-v",
        "error",
        "-nostdin",
        "-threads",
        "1",
        "-filter_threads",
        "1",
        "-filter_complex_threads",
        "1",
        "-i",
        str(path),
        "-map",
        f"0:{source_index}",
    ]
    if codec_type == "video":
        command.extend(
            [
                "-an",
                "-sn",
                "-dn",
                "-c:v",
                "rawvideo",
                "-pix_fmt",
                CANONICAL_VIDEO_PIXEL_FORMAT,
            ]
        )
        canonical_projection = {
            "media_type": "video",
            "codec": "rawvideo",
            "pixel_format": CANONICAL_VIDEO_PIXEL_FORMAT,
        }
    else:
        command.extend(
            [
                "-vn",
                "-sn",
                "-dn",
                "-c:a",
                CANONICAL_AUDIO_CODEC,
            ]
        )
        canonical_projection = {
            "media_type": "audio",
            "codec": CANONICAL_AUDIO_CODEC,
            "sample_rate": str(stream.get("sample_rate") or "source"),
            "channels": stream.get("channels"),
        }
    command.extend(["-f", "framehash", "-hash", CANONICAL_HASH_ALGORITHM, "-"])
    parsed = _parse_framehash(_run(command))
    identity_payload = {
        "source_stream_index": source_index,
        "source_stream": stable(stream),
        "canonical_projection": canonical_projection,
        "headers": parsed["headers"],
        "records": parsed["records"],
    }
    return {
        **identity_payload,
        "record_count": len(parsed["records"]),
        "timeline_hash216": hash216(identity_payload, domain=TIMELINE_IDENTITY_DOMAIN),
    }


class CanonicalMp4Decoder:
    """Build deterministic decoded-frame, PCM, and timing identity manifests."""

    def __init__(self, manifest_root: Path) -> None:
        self.manifest_root = Path(manifest_root)
        self.manifest_root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def status() -> Dict[str, Any]:
        return {
            "ffmpeg_available": shutil.which("ffmpeg") is not None,
            "ffprobe_available": shutil.which("ffprobe") is not None,
            "video_projection": f"rawvideo:{CANONICAL_VIDEO_PIXEL_FORMAT}",
            "audio_projection": CANONICAL_AUDIO_CODEC,
            "frame_hash": CANONICAL_HASH_ALGORITHM,
            "decoder_threads": 1,
        }

    def build(
        self,
        source_path: Path | str,
        *,
        reference_id: str,
        source_sha256: str,
        logical_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        path = Path(source_path).expanduser().resolve(strict=True)
        before = path.stat()
        if not path.is_file() or path.suffix.lower() != ".mp4":
            raise Mp4DecodeError("P181_CANONICAL_DECODE_REQUIRES_MP4")
        if _sha256_file(path) != source_sha256:
            raise Mp4DecodeError("P181_REFERENCE_IDENTITY_MISMATCH_BEFORE_DECODE")

        toolchain = {
            "ffmpeg": _tool_version("ffmpeg"),
            "ffprobe": _tool_version("ffprobe"),
            "decoder_threads": 1,
            "frame_hash": CANONICAL_HASH_ALGORITHM,
        }
        probe = _probe(path)
        decoded_timelines = []
        metadata_only_streams = []
        for stream in probe["streams"]:
            codec_type = str(stream.get("codec_type") or "")
            if codec_type in {"video", "audio"}:
                decoded_timelines.append(_stream_framehash(path, stream))
            else:
                metadata_only_streams.append(stable(stream))

        after = path.stat()
        after_sha256 = _sha256_file(path)
        if (
            before.st_size != after.st_size
            or before.st_mtime_ns != after.st_mtime_ns
            or source_sha256 != after_sha256
        ):
            raise Mp4DecodeError("P181_REFERENCE_CHANGED_DURING_CANONICAL_DECODE")

        timeline_payload = {
            "reference_id": reference_id,
            "source_sha256": source_sha256,
            "decoded_timelines": decoded_timelines,
            "metadata_only_streams": metadata_only_streams,
        }
        timeline_hash216 = hash216(timeline_payload, domain=TIMELINE_IDENTITY_DOMAIN)
        manifest_identity_payload = {
            "reference_id": reference_id,
            "source_sha256": source_sha256,
            "toolchain": toolchain,
            "probe": probe,
            "timeline_hash216": timeline_hash216,
        }
        decode_manifest_id = hash216(manifest_identity_payload, domain=DECODE_MANIFEST_DOMAIN)
        manifest = {
            "schema": "HHS_P181_CANONICAL_MP4_DECODE_MANIFEST_V1",
            "contract": CONTRACT,
            "authority": AUTHORITY,
            "decode_manifest_id": decode_manifest_id,
            "reference_id": reference_id,
            "logical_name": str(logical_name or path.name),
            "source_sha256": source_sha256,
            "source_path": str(path),
            "reference_read_only": True,
            "reference_copied": False,
            "toolchain": toolchain,
            "probe": probe,
            "decoded_timelines": decoded_timelines,
            "metadata_only_streams": metadata_only_streams,
            "timeline_hash216": timeline_hash216,
            "source_state": {
                "size_bytes": before.st_size,
                "mode": before.st_mode,
                "mtime_ns": before.st_mtime_ns,
            },
        }
        manifest["receipt_hash72"] = hash72(manifest, domain=DECODE_RECEIPT_DOMAIN)
        output = self.manifest_root / _artifact_filename(decode_manifest_id)
        output.write_bytes(canonical_bytes(manifest))
        return {**manifest, "manifest_path": str(output)}

    def replay(
        self,
        source_path: Path | str,
        *,
        reference_id: str,
        source_sha256: str,
        expected_timeline_hash216: str,
        logical_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        replay = self.build(
            source_path,
            reference_id=reference_id,
            source_sha256=source_sha256,
            logical_name=logical_name,
        )
        matches = replay["timeline_hash216"] == str(expected_timeline_hash216)
        return {
            "schema": "HHS_P181_CANONICAL_MP4_DECODE_REPLAY_V1",
            "ok": matches,
            "status": (
                "HHS_MP4_CANONICAL_TIMELINE_REPLAY_VERIFIED"
                if matches
                else "REJECT_MP4_CANONICAL_TIMELINE_REPLAY_MISMATCH"
            ),
            "reference_id": reference_id,
            "expected_timeline_hash216": str(expected_timeline_hash216),
            "observed_timeline_hash216": replay["timeline_hash216"],
            "decode_manifest_id": replay["decode_manifest_id"],
            "manifest_path": replay["manifest_path"],
        }
