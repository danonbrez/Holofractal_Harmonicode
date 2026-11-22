#include "hhs_pass220_i028_lane5_rna_g3_bridge_v1.h"
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstring>

/* Real inherited C++ RNA cell-wall ABI execution, not an FFI flag fixture.
 * This tests a candidate transport envelope; 64-phase Lo Shu matrix lowering
 * remains a separate native operator integration obligation. */
namespace {
void hash72(char out[HHS_EXACT_HASH72_STRLEN], std::uint8_t offset) {
    for (std::size_t i=0; i<HHS_EXACT_HASH72_LEN; ++i)
        out[i]=HHS_EXACT_HASH72_ALPHABET[(i+offset)%HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN]='\0';
}
HHSExactPass220I028Lane5ConstructorWitnessV1 witness() {
    HHSExactPass220I028Lane5ConstructorWitnessV1 w{};
    w.struct_size=static_cast<std::uint32_t>(sizeof(w));
    w.version=HHS_EXACT_PASS220_I028_LANE5_G3_VERSION;
    hash72(w.pipeline_root_hash72,13);
    hash72(w.constructor_graph_root_hash72,17);
    w.green_merged_pr_implementation=1;
    w.green_exact_head_workflow=1;
    w.canonical_contract=1;
    w.canonical_whitepaper_proof=1;
    w.formal_proof_receipt=1;
    w.successful_benchmark_receipt=1;
    w.restart_checkpoint=1;
    w.commit_merge_lineage=1;
    w.registered_repository_service=1;
    w.hash216_validated_composition=1;
    return w;
}
}

int main() {
    constexpr std::uint8_t loshu[9]={4,9,2,3,5,7,8,1,6};
    HHSExactVM81Frame frame{};
    for (std::size_t c=0;c<81;++c)
        frame.words[c]=UINT64_C(0x9E3779B97F4A7C15) ^
                       (static_cast<std::uint64_t>(c)*UINT64_C(0x100000001B3));
    frame.words[0]=UINT64_C(0x3ff0000000000000); /* inherited I028 IEEE ingress */
    frame.words[1]=9; frame.words[2]=9; /* inherited G3 P4/C4 equality */
    /* Preserve nine exact independent raw words in separate cells without
       disturbing the three inherited G3 selector/identity registers. */
    const std::uint64_t payloads[9]={
        UINT64_C(0x8000000000000000),
        UINT64_C(0x0000000000000001),
        UINT64_C(0x0123456789ABCDEF),
        UINT64_C(0xFEDCBA9876543210),
        UINT64_C(0xFFFFFFFFFFFFFFFF),
        UINT64_C(0x5555555555555555),
        UINT64_C(0xAAAAAAAAAAAAAAAA),
        UINT64_C(0x0000000000000000),
        UINT64_C(0x7FF8000000000001)
    };
    for (std::size_t i=0;i<9;++i) {
        frame.words[9+i]=payloads[i];
        const auto quotient=payloads[i]/loshu[i];
        const auto residue=payloads[i]%loshu[i];
        assert(quotient*loshu[i]+residue==payloads[i]);
        assert(residue<loshu[i]);
        const std::size_t begin=i*576, end=begin+575;
        assert(begin==i*9*64 && begin==i*8*72);
        assert(end<5184);
    }
    HHSExactVM81Frame saved=frame;
    std::uint8_t one=1;
    HHSExactUQCELInputV1 input{};
    input.struct_size=static_cast<std::uint32_t>(sizeof(input));
    input.uqcel_version=hhs_exact_uqcel_version();
    input.profile=HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.delta.struct_size=static_cast<std::uint32_t>(sizeof(input.delta));
    input.delta.byte_length=1;
    input.delta.bytes_be=&one;
    HHSExactPass219Hash216TransitionViewV1 predecessor{};
    assert(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&predecessor)==
           HHS_EXACT_STATUS_OK);
    auto w=witness();
    HHSExactPass220I028Lane5RNAG3BridgeCandidateV1 candidate{};
    assert(hhs_exact_pass220_i028_lane5_rna_g3_route(
        &input,&frame,&predecessor,&w,0,1,2,&candidate)==HHS_EXACT_STATUS_OK);
    assert(std::memcmp(&frame,&saved,sizeof(frame))==0);
    assert(candidate.struct_size==sizeof(candidate));
    assert(candidate.surface_linux_api_abi_ingress==1);
    assert(candidate.lane5_zero_bypass_interposer==1);
    assert(candidate.cpp_rna_cell_wall_routed==1);
    assert(candidate.holo4_evidence_equivalent==1);
    assert(candidate.pqc_firewall_required_for_canonical_admission==1);
    assert(candidate.signed_environmental_vm81_required==1);
    assert(candidate.direct_vm81_bypass_authority==0);
    assert(candidate.canonical_admission_invoked==0);
    assert(candidate.external_egress_authority==0);
    assert(candidate.g3_candidate.candidate_only==1);
    assert(candidate.g3_candidate.candidate_frame_unchanged==1);
    assert(std::memcmp(&candidate.g3_candidate.candidate_frame,
                       &frame,sizeof(frame))==0);
    /* The inherited membrane must refuse a forged predecessor and missing
       constructor witness instead of producing a successful candidate. */
    auto forged=predecessor;
    forged.transition_identity216[0]=
        forged.transition_identity216[0]=='0'?'1':'0';
    assert(hhs_exact_pass220_i028_lane5_rna_g3_route(
        &input,&frame,&forged,&w,0,1,2,&candidate)==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w.successful_benchmark_receipt=0;
    assert(hhs_exact_pass220_i028_lane5_rna_g3_route(
        &input,&frame,&predecessor,&w,0,1,2,&candidate)==
        HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    return 0;
}
