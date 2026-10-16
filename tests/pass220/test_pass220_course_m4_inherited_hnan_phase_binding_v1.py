import subprocess
from pathlib import Path
import pytest
from hhs_runtime.hhs_pass220_course_m4_inherited_hnan_phase_binding_v1 import bind_course_m4_inherited_native_phase_gate
from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError

def test_absent_native_checker_rejected():
    with pytest.raises(ProofCorpusError,match="COURSE_M4_NATIVE_LIBRARY_REQUIRED"):
        bind_course_m4_inherited_native_phase_gate("/missing/native.so")

def test_real_inherited_native_hnan_module_four_binding(tmp_path):
    c=tmp_path/"runtime.o"
    cpp=tmp_path/"wall.o"
    h=tmp_path/"hash.o"
    library=tmp_path/"libhhs.so"
    subprocess.run(["cc","-std=c11","-O0","-fPIC","-Ihhs_runtime/include",
        "-c","hhs_runtime/c/hhs_runtime_exact_abi.c","-o",str(c)],check=True,timeout=180)
    subprocess.run(["c++","-std=c++17","-O0","-fPIC","-Ihhs_runtime/include",
        "-Inative_projects/hhs_pass188_bott_runtime/include",
        "-Inative_projects/hhs_pass189_hqlh_runtime/include","-c",
        "hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp","-o",str(cpp)],check=True,timeout=180)
    subprocess.run(["cc","-std=c11","-O0","-fPIC","-Ihhs_runtime/include",
        "-c","hhs_runtime/src/hhs_hash216.c","-o",str(h)],check=True,timeout=180)
    subprocess.run(["c++","-shared",str(c),str(cpp),str(h),
        "-o",str(library),"-lm","-lcrypto"],check=True,timeout=180)
    receipt=bind_course_m4_inherited_native_phase_gate(str(library))
    assert receipt["module_index"]==4
    assert receipt["native_phase_order_verified"]
    assert receipt["xy_yx_distinct"] and receipt["zw_wz_distinct"]
    assert len(receipt["candidate_receipt_sha256"])==64
    assert not receipt["new_native_gate_proof_required"]
    assert not receipt["complete_module_four_proved"]
    assert not receipt["course_passthrough_theorem_proved"]
    assert not receipt["canonical_admission"] and not receipt["hash216_minted"]

def test_hostile_native_library_rejected(tmp_path):
    # An ABI-matched library can self-report global success while poisoning
    # hash authority or the actual directional resolution table.
    stub=r"""
#include <string.h>
#include "hhs_pass219_lane5_hnan_global_constraint_1_63.h"
#ifndef ATTACK
#define ATTACK 0
#endif
uint32_t hhs_exact_pass219_hnan_global_version(void) {
    return ATTACK==1 ? 0x00020000U : HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;
}
HHSExactStatus hhs_exact_pass219_hnan_global_system_verify(
    HHSExactPass219HNANGlobalReceiptV1 *r) {
    memset(r,0,sizeof(*r));
    r->struct_size=sizeof(*r);r->version=HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;
    r->decision=1;r->required_rule_mask=0x7fff;r->verified_rule_mask=0x7fff;
    r->xy_yx_distinct=1;r->zw_wz_distinct=1;r->hnan_channel_order_preserved=1;
    r->ordered_zero_closure_preserved=1;r->global_delta_denominator_preserved=1;
    r->candidate_only=1;r->canonical_hash72_authority=(ATTACK==2);
    return 0;
}
HHSExactStatus hhs_exact_pass219_hnan_resolve(
    const HHSExactPass219HNANClaimV1 *c,HHSExactPass219HNANResolutionV1 *r) {
    memset(r,0,sizeof(*r));r->struct_size=sizeof(*r);
    r->version=HHS_EXACT_PASS219_HNAN_GLOBAL_VERSION;r->decision=1;
    r->rule_id=c->rule_id;r->lhs_node=c->lhs_node;r->rhs_node=c->rhs_node;
    r->relation=c->relation;r->exact_rule_match=1;
    r->source_order_preserved=1;r->typed_identity_preserved=1;
    if (ATTACK==3 && c->rule_id==12) r->rhs_node=18;
    if (ATTACK==4 && c->rule_id==13) r->lhs_node=21;
    return 0;
}
"""
    for attack, expected in [
        (1,"ABI_VERSION_MISMATCH"),
        (2,"CANONICAL_AUTHORITY_BYPASS"),
        (3,"ORDERED_RULE_DRIFT"),
        (4,"ORDERED_RULE_DRIFT"),
    ]:
        source=tmp_path/("hostile_"+str(attack)+".c")
        library=tmp_path/("libhostile_"+str(attack)+".so")
        source.write_text(stub)
        subprocess.run(["cc","-std=c11","-shared","-fPIC",
                        "-Ihhs_runtime/include","-DATTACK="+str(attack),
                        str(source),"-o",str(library)],check=True,timeout=60)
        with pytest.raises(ProofCorpusError,match=expected):
            bind_course_m4_inherited_native_phase_gate(str(library))
