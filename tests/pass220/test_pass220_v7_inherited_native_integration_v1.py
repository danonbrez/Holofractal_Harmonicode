"""V7 proof inheritance is real runtime transport, not re-proving HHS."""
from pathlib import Path
from hashlib import sha256
import pytest

from hhs_runtime.hhs_pass220_v7_inherited_native_integration_v1 import (
    EXACT_SOURCE, SCHEMA, V7NativeIntegrationError,
    validate_frontend_output, validate_hnan_mode_output, integrate,
)
from hhs_runtime.hhs_pass220_v7_ordered_matrix_geometry_v1 import (
    parse_quotient, verify_bijection,
)

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"contracts/pass220/PASS_220_V7_VM81_ORDERED_MATRIX_QUOTIENT_20261009.harmonicode"
HEX216="a"*216

def _frontend(status="0",receipt=True):
    body=(
        f"source_bytes={len(EXACT_SOURCE)}\n"
        f"source_hash216={HEX216}\n"
        f"graph_hash216={HEX216}\n"
        f"vmir_hash216={HEX216}\n"
        f"native_validate_only_status={status}\n"
    )
    if receipt:
        body+=f"native_validate_only_receipt_hash216={HEX216}\n"
    return body + (
        "vm81_source_specific_commit_verified=false\n"
        "hash72_source_specific_execution_receipt_verified=false\n"
        "source_ingress_authority=PASS159_FRONTEND_AND_NATIVE_VALIDATE_ONLY\n"
    )

def _gate():
    return (
        "v7_source_exact=1\n"
        "v7_mode=UNDECLARED\n"
        "hnan_15_rule_mask=0x7FFF\n"
        "v7_hnan_order_verified=1\n"
        "v7_decision=INHERIT_NATIVE_DISPATCH\n"
        "v7_reason=9\n"
        "v7_native_type_dispatch_required=1\n"
        "native_v7_matrix_inverse_proved=0\n"
        "native_v7_global_environment_verified=0\n"
        "canonical_vm81_admission=0\n"
        "canonical_hash72_hash216_commit=0\n"
    )

def test_original_source_inherited_graph_and_address_space():
    source=SOURCE.read_bytes()
    assert source==EXACT_SOURCE
    assert len(source)==70
    geo=parse_quotient(source)
    assert len(geo["source_bound_macro_sites"])==9
    assert geo["source_sha256"]==sha256(source).hexdigest()
    assert verify_bijection()["bijective_positions"]==5184

def test_native_hash216_uses_harmonicode_glyphs_not_hex():
    glyph=("j/VhU!54" * 27)
    assert len(glyph)==216
    raw=_frontend().replace(HEX216,glyph)
    out=validate_frontend_output(raw,0,EXACT_SOURCE)
    assert out["native_source_hash216"]==glyph
    assert out["native_constraint_graph_hash216"]==glyph
    assert out["native_vmir_hash216"]==glyph
    assert out["native_validate_only_receipt_hash216"]==glyph
    with pytest.raises(V7NativeIntegrationError,match="INVALID_NATIVE_HASH216"):
        validate_frontend_output(raw.replace(glyph,"A" * 215 + chr(9),1),0,EXACT_SOURCE)

def test_frontend_output_requires_real_hash216_and_execution_scope():
    out=validate_frontend_output(_frontend(),0,EXACT_SOURCE)
    assert out["pass159_frontend_chain"]=="VERIFIED"
    assert out["native_validate_only_completed"] is True
    assert out["canonical_vm81_commit_from_frontend"] is False
    assert out["canonical_hash72_receipt_from_frontend"] is False
    q=validate_frontend_output(_frontend(status="-1",receipt=False),0,EXACT_SOURCE)
    assert q["native_validate_only_completed"] is False

@pytest.mark.parametrize("stdout,code",[
    (_frontend(),1),
    (_frontend().replace("source_bytes=70","source_bytes=69"),0),
    (_frontend().replace("source_hash216="+HEX216,"source_hash216=bad"),0),
    (_frontend().replace("native_validate_only_status=0","native_validate_only_status=?"),0),
    (_frontend().replace("vm81_source_specific_commit_verified=false",
                          "vm81_source_specific_commit_verified=true"),0),
    (_frontend()+"source_bytes=70\n",0),
    (_frontend(status="-1",receipt=True),0),
])
def test_frontend_fake_or_incomplete_provenance_rejected(stdout,code):
    with pytest.raises(V7NativeIntegrationError):
        validate_frontend_output(stdout,code,EXACT_SOURCE)

def test_inherited_hnan_decision_does_not_invent_new_operator():
    o=validate_hnan_mode_output(_gate(),0)
    assert o["pass219_hnan_inherited_rule_mask"]=="0x7FFF"
    assert o["xy_yx_and_zw_wz_order_inherited"] is True
    assert o["pass169_quotient_mode"]=="NATIVE_TYPE_INFERENCE_REQUIRED"
    assert o["canonical_vm81_mutation_from_mode_gate"] is False

@pytest.mark.parametrize("stdout,status",[
    (_gate(),3),
    (_gate().replace("0x7FFF","0x0000"),0),
    (_gate().replace("v7_mode=UNDECLARED","v7_mode=RIGHT_MATRIX_SOLVE"),0),
    (_gate().replace("v7_decision=INHERIT_NATIVE_DISPATCH","v7_decision=ADMITTED"),0),
    (_gate().replace("canonical_vm81_admission=0","canonical_vm81_admission=1"),0),
])
def test_no_source_mode_or_authority_fabrication(stdout,status):
    with pytest.raises(V7NativeIntegrationError):
        validate_hnan_mode_output(stdout,status)

def test_exact_source_mutation_blocks_inheritance_before_any_external_process(tmp_path):
    mutation=tmp_path/"mutated.harmonicode"
    mutation.write_bytes(EXACT_SOURCE.replace(b"xy+yx",b"yx+xy",1))
    with pytest.raises(V7NativeIntegrationError,match="V7_EXACT_SOURCE_MISMATCH"):
        integrate(mutation,"/this/binary/does/not/exist","/another/missing/binary")

def test_native_full_integration_when_binaries_are_provided():
    import os
    frontend=os.environ.get("HHS_P220_V7_PASS159_FRONTEND_BIN")
    quotient=os.environ.get("HHS_P220_V7_QUOTIENT_GATE_BIN")
    if not frontend or not quotient:
        pytest.skip("Real native ABI requires binaries built by focused CI")
    pure=os.environ.get('HHS_P220_V7_PURE_EXEC_BIN')
    record=integrate(SOURCE,frontend,quotient,pure)
    assert record["schema"]==SCHEMA
    assert record["source_sha256"]==sha256(EXACT_SOURCE).hexdigest()
    assert record["inherited_native_pass159"]["pass159_frontend_chain"]=="VERIFIED"
    assert record["inherited_native_hnan_and_pass169_intent"]["pass219_hnan_inherited_rule_mask"]=="0x7FFF"
    assert record["pass169_source_registry"]["canonical_authority"] is False
    assert record["inherited_lane5_candidate"]["candidate_only"] is True
    assert record["vm81_hash72_address_bijection"]["bijective_positions"]==5184
    assert record["source_specific_quotient_operator_binding_present"] is False
    assert record["vm81_signed_environmental_commit_performed"] is False
    if pure:
        evidence=record["inherited_native_pass159_pure_execution"]
        assert evidence is not None
        assert evidence["canonical_mutation"] is False
        assert evidence["source_sha256"]==record["source_sha256"]
