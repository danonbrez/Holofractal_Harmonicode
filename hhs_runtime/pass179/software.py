from __future__ import annotations

import hashlib
import struct
import zlib
from typing import Any, Iterable, Mapping

from .types import MAX_DIMENSION, pixel_floor, reject_float


class SoftwareRenderError(ValueError):
    pass


def _blend(dst: tuple[int, int, int, int], src: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    sa = src[3]
    inv = 65535 - sa
    out_a = sa + (dst[3] * inv + 32767) // 65535
    if out_a == 0:
        return (0, 0, 0, 0)
    out = []
    for i in range(3):
        premul = src[i] * sa + (dst[i] * dst[3] * inv + 32767) // 65535
        out.append(min(65535, (premul + out_a // 2) // out_a))
    return (out[0], out[1], out[2], min(65535, out_a))


def render_command_stream(stream: Mapping[str, Any]) -> dict[str, Any]:
    reject_float(stream)
    if stream.get("schema") != "HHS_PASS_179_COMMAND_STREAM_V1":
        raise SoftwareRenderError("P179_COMMAND_STREAM_SCHEMA")
    width = int(stream.get("width", 0))
    height = int(stream.get("height", 0))
    if not (1 <= width <= MAX_DIMENSION and 1 <= height <= MAX_DIMENSION):
        raise SoftwareRenderError("P179_FRAME_DIMENSION_RANGE")
    commands = list(stream.get("commands") or [])
    if len(commands) > 8193:
        raise SoftwareRenderError("P179_COMMAND_COUNT_RANGE")
    pixels = [(0, 0, 0, 65535)] * (width * height)

    def fill_rect(x: int, y: int, w: int, h: int, color: tuple[int, int, int, int]) -> None:
        if w <= 0 or h <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(width, x + w)
        y1 = min(height, y + h)
        for py in range(y0, y1):
            base = py * width
            for px in range(x0, x1):
                idx = base + px
                pixels[idx] = _blend(pixels[idx], color)

    for command in commands:
        op = command.get("op")
        rgba = command.get("rgba16", [0, 0, 0, 65535])
        if not isinstance(rgba, list) or len(rgba) != 4 or any(not isinstance(v, int) or not 0 <= v <= 65535 for v in rgba):
            raise SoftwareRenderError("P179_COMMAND_COLOR")
        color = tuple(rgba)
        if op == "CLEAR":
            pixels = [color] * (width * height)
        elif op in {"RECT", "POINT"}:
            x = pixel_floor(int(command.get("x_q16", 0)))
            y = pixel_floor(int(command.get("y_q16", 0)))
            if op == "POINT":
                w = h = 1
            else:
                w = pixel_floor(int(command.get("w_q16", 0)))
                h = pixel_floor(int(command.get("h_q16", 0)))
            fill_rect(x, y, w, h, color)
        else:
            raise SoftwareRenderError(f"P179_COMMAND_OP:{op}")
    rgba16 = b"".join(struct.pack("<HHHH", *pixel) for pixel in pixels)
    return {
        "schema": "HHS_PASS_179_SOFTWARE_FRAME_V1",
        "width": width,
        "height": height,
        "rgba16": rgba16,
        "frame_sha256": hashlib.sha256(rgba16).hexdigest(),
        "canonical_mutation_authority": False,
        "floating_point_authority": False,
    }


def png_from_rgba16(width: int, height: int, rgba16: bytes) -> bytes:
    if len(rgba16) != width * height * 8:
        raise SoftwareRenderError("P179_RGBA16_LENGTH")
    rows = bytearray()
    off = 0
    for _ in range(height):
        rows.append(0)
        for _ in range(width):
            r, g, b, a = struct.unpack_from("<HHHH", rgba16, off)
            off += 8
            rows.extend((r >> 8, g >> 8, b >> 8, a >> 8))

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + chunk(b"IEND", b"")
    )
