from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .core import ExactRational, digest256, generate_shader_source, shader_projection, write_json


def generate_all(workload: Mapping[str, Any], root: Path) -> dict[str, Any]:
    root = root.resolve()
    ratio = ExactRational(
        int(workload["stage_ratio"]["numerator"]),
        int(workload["stage_ratio"]["denominator"]),
    )
    shader_dir = root / "generated" / "shaders"
    shader_dir.mkdir(parents=True, exist_ok=True)
    fragment = shader_dir / "hhs_gfcc_fragment.glsl"
    fragment.write_text(generate_shader_source(ratio), encoding="utf-8", newline="\n")
    common = shader_dir / "hhs_gfcc_common.glsl"
    projection = shader_projection(ratio)
    common.write_text(
        "#ifndef HHS_GFCC_COMMON_GLSL\n"
        "#define HHS_GFCC_COMMON_GLSL\n"
        f"const uint HHS_GFCC_FIB_NUM = {ratio.numerator}u;\n"
        f"const uint HHS_GFCC_FIB_DEN = {ratio.denominator}u;\n"
        "// Canonical authority remains the exact integer pair above.\n"
        "#endif\n",
        encoding="utf-8",
        newline="\n",
    )
    collision = shader_dir / "hhs_gfcc_collision_field.glsl"
    collision.write_text(
        "#version 450\n"
        "// Visualization-only collision field; native C owns admissibility.\n"
        "layout(local_size_x = 8, local_size_y = 8) in;\n"
        "void main() { uint visualIndex = gl_GlobalInvocationID.x + 9u * gl_GlobalInvocationID.y; if (visualIndex == 0xffffffffu) { return; } }\n",
        encoding="utf-8",
        newline="\n",
    )
    records = []
    for path in (common, fragment, collision):
        records.append({
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": digest256({"bytes_hex": path.read_bytes().hex()}),
        })
    manifest = {
        "schema": "HHS_GFCC_SHADER_CODEGEN_MANIFEST_V1",
        "target": "GLSL_450",
        "canonical_authority": False,
        "source_spec_digest": digest256(workload["spec"]),
        "projection": projection,
        "records": records,
    }
    manifest["manifest_digest"] = digest256(manifest)
    write_json(root / "manifest" / "shader_codegen_manifest.json", manifest)
    return manifest


__all__ = ["generate_all"]
