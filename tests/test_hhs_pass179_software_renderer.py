import hashlib

from hhs_runtime.pass179.runtime import command_stream, scene_from_payload
from hhs_runtime.pass179.software import png_from_rgba16, render_command_stream


def test_software_renderer_is_byte_deterministic_and_png_is_stable():
    scene = scene_from_payload({
        "scene_id": "render",
        "width": 16,
        "height": 12,
        "background": [100, 200, 300, 65535],
        "nodes": [{"node_id": "r", "kind": "RECT", "x": 2, "y": 2, "w": 5, "h": 4, "rgba16": [65535, 0, 0, 32768]}],
    })
    stream = command_stream(scene)
    a = render_command_stream(stream)
    b = render_command_stream(stream)
    assert a["rgba16"] == b["rgba16"]
    assert a["frame_sha256"] == b["frame_sha256"]
    png_a = png_from_rgba16(a["width"], a["height"], a["rgba16"])
    png_b = png_from_rgba16(b["width"], b["height"], b["rgba16"])
    assert png_a.startswith(b"\x89PNG\r\n\x1a\n")
    assert hashlib.sha256(png_a).digest() == hashlib.sha256(png_b).digest()
