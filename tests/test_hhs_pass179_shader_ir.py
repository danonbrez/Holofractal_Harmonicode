import pytest

from hhs_runtime.pass179.shader_ir import ShaderIRError, compile_shader_ir, validate_shader_ir


IR = {
    "schema": "HHS_PASS_179_SHADER_IR_V1",
    "nodes": [
        {"id": "color", "op": "CONST_RGBA16", "rgba16": [65535, 32768, 0, 65535]},
        {"id": "out", "op": "OUTPUT_COLOR", "inputs": ["color"]},
    ],
    "output": "out",
}


def test_shader_ir_is_typed_and_projections_are_non_authoritative():
    validated = validate_shader_ir(IR)
    assert validated["ok"] is True
    assert validated["canonical_mutation_authority"] is False
    wgsl = compile_shader_ir(IR, "WGSL")
    glsl = compile_shader_ir(IR, "GLSL")
    assert wgsl["projection_only"] is True
    assert glsl["projection_only"] is True
    assert wgsl["shader_ir_sha256"] == glsl["shader_ir_sha256"]


def test_shader_ir_rejects_forward_reference_and_float():
    bad = {
        "schema": "HHS_PASS_179_SHADER_IR_V1",
        "nodes": [{"id": "out", "op": "OUTPUT_COLOR", "inputs": ["later"]}, {"id": "later", "op": "PHASE_COLOR", "phase": 4}],
        "output": "out",
    }
    with pytest.raises(ShaderIRError):
        validate_shader_ir(bad)
    with pytest.raises(Exception, match="P179_FLOAT_CANONICAL_AUTHORITY_FORBIDDEN"):
        validate_shader_ir({"schema": "HHS_PASS_179_SHADER_IR_V1", "nodes": [{"id": "x", "op": "PHASE_COLOR", "phase": 4.5}], "output": "x"})
