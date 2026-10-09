"""V7 inherited Pass159 pure execution: source, status and receipt scope."""
from hashlib import sha256
from pathlib import Path
import pytest

from hhs_runtime.hhs_pass220_v7_inherited_native_integration_v1 import (
    EXACT_SOURCE, V7NativeIntegrationError,
    validate_native_pure_output as parse_pure,
)

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"contracts/pass220/PASS_220_V7_VM81_ORDERED_MATRIX_QUOTIENT_20261009.harmonicode"

def _fixture(status="-2",replay="-2",candidate=None):
    lines=[
        "v7_exact_source=VERIFIED",
        "source_sha256="+sha256(EXACT_SOURCE).hexdigest(),
        "source_bytes=70","native_runtime=PASS159_INHERITED",
        "native_execution_mode=EVALUATE_PURE","native_commit_policy=0",
        "pure_native_status="+status,
        "pure_replay_status="+replay,
        "native_matrix_quotient_result_certified=0",
        "source_specific_signed_vm81_commit=0",
        "source_specific_hash72_hash216_canonical_receipt=0",
    ]
    if candidate is not None:
        lines+=["pure_candidate_hash216="+candidate,
                "pure_replay_hash216="+candidate]
    return "\n".join(lines)+"\n"

def test_exact_source_and_pure_status_record():
    assert SOURCE.read_bytes()==EXACT_SOURCE
    assert len(EXACT_SOURCE)==70
    assert parse_pure(_fixture(),0,EXACT_SOURCE)["canonical_mutation"] is False

def test_216_native_glyphs_not_hex():
    glyph="jx+W/!>"*30+"jx+W/!"
    assert len(glyph)==216
    rec=parse_pure(_fixture(status="0",replay="0",candidate=glyph),0,EXACT_SOURCE)
    assert rec["pure_replay_hash216"]==glyph
    assert rec["candidate_hash216"]==glyph

@pytest.mark.parametrize("mutated",[
    "v7_exact_source=OPEN_FAILED",
    "native_runtime=HOST_SCALAR",
    "native_execution_mode=EXECUTE_AND_COMMIT",
    "native_commit_policy=1",
    "source_specific_signed_vm81_commit=1",
    "source_specific_hash72_hash216_canonical_receipt=1",
    "source_sha256=not-the-original",
])
def test_authority_escalation_and_false_source_rejected(mutated):
    field=mutated.split("=",1)[0]+"="
    body=_fixture()
    assert field in body
    lines=[""+mutated if x.startswith(field) else x for x in body.splitlines()]
    with pytest.raises(V7NativeIntegrationError):
        parse_pure("\n".join(lines)+"\n",0,EXACT_SOURCE)

def test_order_mutation_rejected_before_native_exec():
    mutant=EXACT_SOURCE.replace(b"xy+yx",b"yx+xy",1)
    with pytest.raises(V7NativeIntegrationError):
        parse_pure(_fixture(),0,mutant)

def test_inconsistent_status_or_unsupported_glyph_rejected():
    glyph="x"*216
    with pytest.raises(V7NativeIntegrationError):
        parse_pure(_fixture(status="-1",replay="-2",candidate=glyph),0,EXACT_SOURCE)
    with pytest.raises(V7NativeIntegrationError):
        parse_pure(_fixture(status="0",replay="0",candidate="x"*215+" "),0,EXACT_SOURCE)

def test_actual_native_pure_execution_probe_when_built():
    import os,subprocess
    binary=os.getenv("HHS_P220_V7_PURE_EXEC_BIN")
    if not binary:
        pytest.skip("Scoped native CI compiles genuine Pass159 pure executable")
    proc=subprocess.run([binary,str(SOURCE)],capture_output=True,
                        text=True,timeout=120,check=False)
    record=parse_pure(proc.stdout,proc.returncode,EXACT_SOURCE)
    assert record["canonical_mutation"] is False
