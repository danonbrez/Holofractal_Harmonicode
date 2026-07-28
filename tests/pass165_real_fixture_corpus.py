"""Independent real-format fixture builder for Pass 165 terminal validation.

The corpus is generated from repository source bytes at test time.  No media
binary is committed, and the builder does not import the Pass 165 tokenizer or
modality detector.
"""
from __future__ import annotations

from hashlib import sha256, shake_256
import json
from pathlib import Path
import shutil
import struct
import subprocess
import wave
import zlib

SOURCE_PATHS = (
    "HHS_PASS_164_IMPLEMENTATION_STATUS.md",
    "HHS_PASS_165_IMPLEMENTATION_STATUS.md",
    "HHS_PASS_165_AUTHORITY_BINDING.json",
    "hhs_runtime/pass165/ingestion.py",
)


def repository_source(root: Path) -> bytes:
    parts = []
    for relative in SOURCE_PATHS:
        path = root / relative
        if not path.is_file():
            raise AssertionError(f"repository fixture source missing: {relative}")
        raw = path.read_bytes()
        parts.append(relative.encode("utf-8") + b"\0" + raw)
    return b"\n--HHS-P165-REPOSITORY-SOURCE--\n".join(parts)


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(seed: bytes) -> bytes:
    digest = sha256(seed).hexdigest()
    text = (
        "HHS Pass 165 repository-derived PDF fixture. "
        f"Source digest {digest}. Exact 81 x 64 = 5184 projection geometry."
    )
    lines = [text[index : index + 72] for index in range(0, len(text), 72)]
    stream = "BT /F1 10 Tf 40 760 Td 14 TL " + " ".join(
        f"({_pdf_escape(line)}) Tj T*" for line in lines
    ) + " ET"
    stream_bytes = stream.encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream_bytes)).encode("ascii") + b" >>\nstream\n" + stream_bytes + b"\nendstream",
    ]
    output = bytearray(b"%PDF-1.4\n%HHS165\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return bytes(output)


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def build_png(seed: bytes, width: int = 72, height: int = 72) -> bytes:
    pixels = shake_256(b"HHS-P165-PNG\0" + seed).digest(width * height * 3)
    rows = b"".join(b"\x00" + pixels[row * width * 3 : (row + 1) * width * 3] for row in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _png_chunk(b"IDAT", zlib.compress(rows, 9))
        + _png_chunk(b"IEND", b"")
    )


def build_wav(seed: bytes, frames: int = 8000) -> bytes:
    samples = shake_256(b"HHS-P165-WAV\0" + seed).digest(frames)
    pcm = b"".join(struct.pack("<h", (sample - 128) * 128) for sample in samples)
    from io import BytesIO

    output = BytesIO()
    with wave.open(output, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        handle.writeframes(pcm)
    return output.getvalue()


def build_mp4(seed: bytes, directory: Path) -> bytes:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise AssertionError("ffmpeg is required for the real MP4 fixture")
    frame_dir = directory / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    width = height = 72
    for frame_index in range(8):
        pixels = shake_256(b"HHS-P165-MP4\0" + seed + bytes([frame_index])).digest(width * height * 3)
        (frame_dir / f"frame_{frame_index:02d}.ppm").write_bytes(
            f"P6\n{width} {height}\n255\n".encode("ascii") + pixels
        )
    output = directory / "repository_fixture.mp4"
    subprocess.run(
        [
            ffmpeg,
            "-v",
            "error",
            "-y",
            "-framerate",
            "6",
            "-i",
            str(frame_dir / "frame_%02d.ppm"),
            "-an",
            "-c:v",
            "mpeg4",
            "-q:v",
            "4",
            "-pix_fmt",
            "yuv420p",
            "-map_metadata",
            "-1",
            "-fflags",
            "+bitexact",
            "-flags:v",
            "+bitexact",
            str(output),
        ],
        check=True,
    )
    return output.read_bytes()


def validate_pdf(raw: bytes) -> dict[str, object]:
    assert raw.startswith(b"%PDF-1.4")
    assert b"xref\n" in raw and b"trailer\n" in raw and raw.rstrip().endswith(b"%%EOF")
    return {"format": "PDF", "bytes": len(raw), "sha256": sha256(raw).hexdigest()}


def validate_png(raw: bytes) -> dict[str, object]:
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
    cursor = 8
    kinds = []
    while cursor < len(raw):
        length = struct.unpack(">I", raw[cursor : cursor + 4])[0]
        kind = raw[cursor + 4 : cursor + 8]
        payload = raw[cursor + 8 : cursor + 8 + length]
        crc = struct.unpack(">I", raw[cursor + 8 + length : cursor + 12 + length])[0]
        assert crc == zlib.crc32(kind + payload) & 0xFFFFFFFF
        kinds.append(kind)
        cursor += 12 + length
    assert kinds[0] == b"IHDR" and kinds[-1] == b"IEND"
    return {"format": "PNG", "bytes": len(raw), "sha256": sha256(raw).hexdigest()}


def validate_wav(raw: bytes) -> dict[str, object]:
    from io import BytesIO

    with wave.open(BytesIO(raw), "rb") as handle:
        assert handle.getnchannels() == 1
        assert handle.getsampwidth() == 2
        assert handle.getframerate() == 8000
        assert handle.getnframes() == 8000
    return {"format": "WAV", "bytes": len(raw), "sha256": sha256(raw).hexdigest()}


def validate_mp4(raw: bytes, directory: Path) -> dict[str, object]:
    assert len(raw) >= 12 and raw[4:8] == b"ftyp"
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise AssertionError("ffprobe is required for MP4 validation")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "validated.mp4"
    path.write_bytes(raw)
    completed = subprocess.run(
        [ffprobe, "-v", "error", "-show_streams", "-of", "json", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    metadata = json.loads(completed.stdout)
    video_streams = [stream for stream in metadata.get("streams", []) if stream.get("codec_type") == "video"]
    assert video_streams and int(video_streams[0]["width"]) == 72 and int(video_streams[0]["height"]) == 72
    return {"format": "MP4", "bytes": len(raw), "sha256": sha256(raw).hexdigest(), "codec": video_streams[0].get("codec_name")}


def build_corpus(root: Path, directory: Path) -> dict[str, bytes]:
    seed = repository_source(root)
    return {
        "PDF": build_pdf(seed),
        "IMAGE": build_png(seed),
        "AUDIO": build_wav(seed),
        "VIDEO": build_mp4(seed, directory),
    }
