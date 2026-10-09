"""Real inherited HNAN native relation preflight, never V4 whole-equation proof."""
from pathlib import Path
import re
import pytest
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"contracts/pass220/PASS_220_ORDERED_PHASE_CHAIN_V4_20261009.harmonicode"
ARTIFACT=ROOT/"artifacts/pass220/v4-hnan-phase/hnan_preflight.txt"
NATIVE="hhs_exact_pass219_hnan_global_system_verify"


def test_source_phase_order_and_40_gate_spans() -> None:
    data=SOURCE.read_bytes()
    assert len(data)==527 and data[-1:]==b"\n"
    assert data.count(b"==")==40
    assert b"u^72==x*y" in data
    assert b"u^36==(y*x*w*z)/a^2" in data
    assert b"==x==-y*(" in data
    assert b"1==z*w" in data and b"1==x*y" in data
    assert "y*x*w*z" != "x*y*w*z"


def test_native_api_invocations_are_read_only_and_distinguish_order() -> None:
    c=(ROOT/"tools/pass220/pass220_v4_native_hnan_phase_order_preflight.c").read_text()
    assert NATIVE in c
    assert "hhs_exact_pass219_hnan_resolve(" in c
    assert "check_relation(12U,\"xy_yx\")" in c
    assert "check_relation(13U,\"zw_wz\")" in c
    for forbidden in ("hhs159_interpret(", "hhs_exact_vm81_admit_uqcel(",
                      "hhs_exact_pass219_vm81_environment_admit_signed(",
                      "HHS159_MODE_EXECUTE_AND_COMMIT"):
        assert forbidden not in c
    assert "40_boolean_truth_witnesses=UNRESOLVED" in c
    assert "vm81_signed_commit_performed=0" in c


def test_native_hnan_inherited_rules_and_negative_checks() -> None:
    if not ARTIFACT.exists():
        pytest.skip("Native CI runs inherited HNAN runtime and generates artifact")
    t=ARTIFACT.read_text()
    for claim in (
        "v4_source_identity=VERIFIED",
        "v4_gate_occurrence_count=40",
        "hnan_15_rule_mask=0x7FFF",
        "hnan_jordan_rank=3","hnan_jordan_nullity=1",
        "hnan_jordan_squared_nullity=2",
        "hnan_xy_yx_original_order=VERIFIED",
        "hnan_zw_wz_original_order=VERIFIED",
        "hnan_xy_yx_reverse=REJECTED_SOURCE_ORDER",
        "hnan_zw_wz_reverse=REJECTED_SOURCE_ORDER",
        "hnan_xy_yx_commutation=REJECTED",
        "hnan_zw_wz_commutation=REJECTED",
        "hnan_xy_yx_equality_reversal=REJECTED",
        "hnan_zw_wz_equality_reversal=REJECTED",
        "40_boolean_truth_witnesses=UNRESOLVED",
        "vm81_signed_commit_performed=0",
        "canonical_hash72_hash216_transition_performed=0",
        "v4_hnan_native_preflight=PASS",
    ):
        assert claim in t
    assert re.search(r"^v4_hnan_native_preflight=PASS$",t,re.M)
