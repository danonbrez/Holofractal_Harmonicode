from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .core import ExactRational, digest256, shader_projection, write_json

_UNIFORM_MEMBERS = (
    "phi_projection",
    "inverse_sqrt2_projection",
    "scale_projection",
    "time_projection",
    "fibonacci_n",
    "nonary_phase",
    "vm81_cell",
    "hash72_index",
    "hash216_index",
    "shell_depth",
    "orientation",
    "constraint_flags",
)


def _uniform_block() -> str:
    return """layout(set = 0, binding = 0, std140) uniform HHS_GFCC_Uniforms {
    float phi_projection;
    float inverse_sqrt2_projection;
    float scale_projection;
    float time_projection;
    uint fibonacci_n;
    uint nonary_phase;
    uint vm81_cell;
    uint hash72_index;
    uint hash216_index;
    uint shell_depth;
    uint orientation;
    uint constraint_flags;
} gfcc;
"""


def generate_all(workload: Mapping[str, Any], root: Path) -> dict[str, Any]:
    root = root.resolve()
    ratio = ExactRational(
        int(workload["stage_ratio"]["numerator"]),
        int(workload["stage_ratio"]["denominator"]),
    )
    projection = shader_projection(ratio)
    shader_dir = root / "generated" / "shaders"
    shader_dir.mkdir(parents=True, exist_ok=True)

    common = shader_dir / "hhs_gfcc_common.glsl"
    common.write_text(
        "#ifndef HHS_GFCC_COMMON_GLSL\n"
        "#define HHS_GFCC_COMMON_GLSL\n"
        f"const uint HHS_GFCC_FIB_NUM = {ratio.numerator}u;\n"
        f"const uint HHS_GFCC_FIB_DEN = {ratio.denominator}u;\n"
        "// Canonical authority remains the exact integer pair and symbolic roots.\n"
        "#endif\n",
        encoding="utf-8",
        newline="\n",
    )

    fragment = shader_dir / "hhs_gfcc_fragment.glsl"
    fragment.write_text(
        "#version 450\n"
        "// Projected rendering only; native C owns canonical state and admissibility.\n"
        f"// phi exact source: {projection['phi']['exact_source']}\n"
        f"// eta exact source: {projection['inverse_sqrt2']['exact_source']}\n"
        f"// stage ratio exact source: {ratio.numerator}/{ratio.denominator}\n"
        + _uniform_block()
        + "layout(location = 0) out vec4 outColor;\n"
        "void main() {\n"
        "  vec2 p = gl_FragCoord.xy * gfcc.inverse_sqrt2_projection;\n"
        "  float phase = fract((p.x + p.y + float(gfcc.nonary_phase)) / 9.0);\n"
        "  float shell = fract(length(p) / max(gfcc.scale_projection, 0.0001));\n"
        "  float indexMix = float((gfcc.vm81_cell + gfcc.hash72_index + gfcc.hash216_index + gfcc.shell_depth + gfcc.orientation + gfcc.constraint_flags + gfcc.fibonacci_n) & 255u) / 255.0;\n"
        "  outColor = vec4(phase, shell, fract(phase * gfcc.phi_projection + gfcc.time_projection), indexMix);\n"
        "}\n",
        encoding="utf-8",
        newline="\n",
    )

    collision = shader_dir / "hhs_gfcc_collision_field.glsl"
    collision.write_text(
        "#version 450\n"
        "// Visualization-only collision field; native C owns collision acceptance.\n"
        + _uniform_block()
        + "layout(local_size_x = 8, local_size_y = 8) in;\n"
        "void main() {\n"
        "  uint visualIndex = gl_GlobalInvocationID.x + 9u * gl_GlobalInvocationID.y;\n"
        "  float projected = gfcc.phi_projection + gfcc.inverse_sqrt2_projection + gfcc.scale_projection + gfcc.time_projection;\n"
        "  uint indexed = gfcc.fibonacci_n + gfcc.nonary_phase + gfcc.vm81_cell + gfcc.hash72_index + gfcc.hash216_index + gfcc.shell_depth + gfcc.orientation + gfcc.constraint_flags;\n"
        "  if (visualIndex == 0xffffffffu && projected < 0.0 && indexed == 0xffffffffu) { return; }\n"
        "}\n",
        encoding="utf-8",
        newline="\n",
    )

    records = []
    for path in (common, fragment, collision):
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size": path.stat().st_size,
                "sha256": digest256({"bytes_hex": path.read_bytes().hex()}),
            }
        )
    manifest = {
        "schema": "HHS_GFCC_SHADER_CODEGEN_MANIFEST_V1",
        "target": "GLSL_450_VULKAN_1_1",
        "canonical_authority": False,
        "source_spec_digest": digest256(workload["spec"]),
        "projection": projection,
        "uniform_block": {
            "set": 0,
            "binding": 0,
            "layout": "std140",
            "expected_size_bytes": 48,
            "members": list(_UNIFORM_MEMBERS),
        },
        "records": records,
    }
    manifest["manifest_digest"] = digest256(manifest)
    write_json(root / "manifest" / "shader_codegen_manifest.json", manifest)
    return manifest


__all__ = ["generate_all"]
