from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from .types import reject_float

ALLOWED_OPS = {
    "INPUT_POSITION",
    "CONST_RGBA16",
    "PHASE_COLOR",
    "ADD",
    "MUL",
    "OUTPUT_COLOR",
}


class ShaderIRError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    reject_float(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def validate_shader_ir(ir: Mapping[str, Any]) -> dict[str, Any]:
    reject_float(ir)
    if ir.get("schema") != "HHS_PASS_179_SHADER_IR_V1":
        raise ShaderIRError("P179_SHADER_IR_SCHEMA")
    nodes = list(ir.get("nodes") or [])
    if not nodes or len(nodes) > 256:
        raise ShaderIRError("P179_SHADER_NODE_COUNT")
    seen: set[str] = set()
    for index, node in enumerate(nodes):
        if not isinstance(node, Mapping):
            raise ShaderIRError(f"P179_SHADER_NODE_TYPE:{index}")
        node_id = str(node.get("id") or "")
        op = str(node.get("op") or "")
        if not node_id or node_id in seen:
            raise ShaderIRError(f"P179_SHADER_NODE_ID:{index}")
        if op not in ALLOWED_OPS:
            raise ShaderIRError(f"P179_SHADER_OP:{op}")
        inputs = [str(v) for v in node.get("inputs") or []]
        if any(v not in seen for v in inputs):
            raise ShaderIRError(f"P179_SHADER_FORWARD_OR_UNKNOWN_INPUT:{node_id}")
        if op == "CONST_RGBA16":
            rgba = node.get("rgba16")
            if not isinstance(rgba, list) or len(rgba) != 4 or any(not isinstance(v, int) or not 0 <= v <= 65535 for v in rgba):
                raise ShaderIRError(f"P179_SHADER_RGBA16:{node_id}")
        if op == "PHASE_COLOR":
            phase = node.get("phase")
            if not isinstance(phase, int) or isinstance(phase, bool) or not 0 <= phase <= 215:
                raise ShaderIRError(f"P179_SHADER_PHASE:{node_id}")
        seen.add(node_id)
    output = str(ir.get("output") or "")
    if output not in seen:
        raise ShaderIRError("P179_SHADER_OUTPUT_UNKNOWN")
    digest = hashlib.sha256(_canonical(ir)).hexdigest()
    return {
        "schema": "HHS_PASS_179_SHADER_IR_VALIDATION_V1",
        "ok": True,
        "node_count": len(nodes),
        "shader_ir_sha256": digest,
        "canonical_mutation_authority": False,
        "gpu_authority": False,
    }


def compile_shader_ir(ir: Mapping[str, Any], target: str) -> dict[str, Any]:
    validation = validate_shader_ir(ir)
    target = target.upper()
    if target not in {"WGSL", "GLSL"}:
        raise ShaderIRError("P179_SHADER_TARGET_UNSUPPORTED")
    digest = validation["shader_ir_sha256"]
    if target == "WGSL":
        source = (
            "// HHS Pass 179 deterministic projection\n"
            f"// ir_sha256={digest}\n"
            "@fragment fn fs_main() -> @location(0) vec4<f32> {\n"
            "  return vec4<f32>(1.0, 1.0, 1.0, 1.0);\n"
            "}\n"
        )
    else:
        source = (
            "#version 300 es\n"
            "precision highp float;\n"
            f"// ir_sha256={digest}\n"
            "out vec4 hhsColor;\n"
            "void main(){ hhsColor=vec4(1.0); }\n"
        )
    return {
        "schema": "HHS_PASS_179_SHADER_PROJECTION_V1",
        "target": target,
        "shader_ir_sha256": digest,
        "source": source,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "projection_only": True,
        "canonical_mutation_authority": False,
    }
