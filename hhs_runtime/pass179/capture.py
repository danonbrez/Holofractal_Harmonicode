from __future__ import annotations

import hashlib
from pathlib import Path

from .runtime import GraphicsAuthority
from .software import png_from_rgba16


def capture_scene_png(
    authority: GraphicsAuthority,
    scene_id: str,
    destination: Path,
) -> dict:
    result = authority.render_scene(scene_id)
    frame = result["frame"]
    png = png_from_rgba16(frame["width"], frame["height"], frame["rgba16"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(png)
    return {
        "schema": "HHS_PASS_179_CAPTURE_V1",
        "scene_id": scene_id,
        "frame_sha256": frame["frame_sha256"],
        "png_sha256": hashlib.sha256(png).hexdigest(),
        "bytes": len(png),
        "path": str(destination),
        "projection_only": True,
        "capture_mutation_authority": False,
    }
