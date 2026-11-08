#include "hhs_pass220_q81_hnan_native_phase_candidate_v1.h"
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>

#define CHECK(x) do { if (!(x)) { std::fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x); return 1; } } while(0)
static void root72(char out[HHS_EXACT_HASH72_STRLEN], std::uint8_t offset) {
    for(std::size_t i=0;i<HHS_EXACT_HASH72_LEN;++i)
        out[i]=HHS_EXACT_HASH72_ALPHABET[(i+offset)%HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN]='\0';
}
static HHSExactPass220I028Lane5ConstructorWitnessV1 witness() {
    HHSExactPass220I028Lane5ConstructorWitnessV1 w{};
    w.struct_size=static_cast<std::uint32_t>(sizeof(w));
    w.version=HHS_EXACT_PASS220_I028_LANE5_G3_VERSION;
    root72(w.pipeline_root_hash72,13U);
    root72(w.constructor_graph_root_hash72,17U);
    w.green_merged_pr_implementation=1U;
    w.green_exact_head_workflow=1U;
    w.canonical_contract=1U;
    w.canonical_whitepaper_proof=1U;
    w.formal_proof_receipt=1U;
    w.successful_benchmark_receipt=1U;
    w.restart_checkpoint=1U;
    w.commit_merge_lineage=1U;
    w.registered_repository_service=1U;
    w.hash216_validated_composition=1U;
    return w;
}
int main() {
    std::uint8_t one=1U;
    HHSExactBigUIntView a2{static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)),1U,&one};
    HHSExactUQCELInputV1 input{};
    input.struct_size=static_cast<std::uint32_t>(sizeof(input));
    input.uqcel_version=hhs_exact_uqcel_version();
    input.profile=HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.delta=a2;
    HHSExactVM81Frame frame{};
    frame.words[0]=UINT64_C(0x3ff0000000000000);
    frame.words[1]=9U;
    frame.words[2]=9U;
    frame.words[4*9+3]=frame.words[4*9+4]=frame.words[4*9+5]=1U;
    const auto original=frame;
    HHSExactPass219Hash216TransitionViewV1 predecessor{};
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&predecessor)==HHS_EXACT_STATUS_OK);
    auto root=witness();
    std::int8_t pairs[81][2]{};
    constexpr std::int8_t cases[4][2]={{0,1},{1,0},{-1,1},{1,-1}};
    for(std::size_t i=0;i<81;++i) {
        pairs[i][0]=cases[i%4][0]; pairs[i][1]=cases[i%4][1];
    }
    HHSExactPass220Q81HNANPhaseCandidateV1 output{};
    CHECK(hhs_pass220_q81_hnan_phase_candidate(
      &input,&frame,&predecessor,&root,0U,1U,2U,pairs,&output)==HHS_EXACT_STATUS_OK);
    CHECK(output.struct_size==sizeof(output));
    CHECK(output.version==HHS_PASS220_Q81_HNAN_NATIVE_PHASE_VERSION);
    CHECK(output.mediated_via_pass219_cpp_cell_wall==1U);
    CHECK(output.mediated_via_lane5_constructor==1U);
    CHECK(output.lane5_bridge.cpp_rna_cell_wall_routed==1U);
    CHECK(output.lane5_bridge.lane5_zero_bypass_interposer==1U);
    CHECK(output.lane5_bridge.g3_candidate.candidate_frame_unchanged==1U);
    CHECK(output.source_phase_native_certified==0U);
    CHECK(output.candidate_only==1U);
    CHECK(output.canonical_vm81_mutation_authority==0U);
    CHECK(output.canonical_hash72_mint_authority==0U);
    CHECK(output.canonical_hash216_mint_authority==0U);
    CHECK(output.signed_vm81_admission_invoked==0U);
    CHECK(std::memcmp(&frame,&original,sizeof(frame))==0);
    for(std::size_t i=0;i<81;++i) {
        CHECK(output.binary[i]==static_cast<std::uint8_t>((i%4)/2));
        CHECK(output.orientation[i]==static_cast<std::uint8_t>(i%2));
        CHECK(output.ordered_pair[i][0]==pairs[i][0]);
        CHECK(output.ordered_pair[i][1]==pairs[i][1]);
    }
    const auto saved=output;
    pairs[7][0]=2; pairs[7][1]=2;
    CHECK(hhs_pass220_q81_hnan_phase_candidate(
      &input,&frame,&predecessor,&root,0U,1U,2U,pairs,&output)
      ==HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(std::memcmp(&output,&saved,sizeof(output))==0);
    pairs[7][0]=cases[3][0]; pairs[7][1]=cases[3][1];
    auto forged=predecessor;
    forged.transition_identity216[0]=(forged.transition_identity216[0]=='0'?'1':'0');
    CHECK(hhs_pass220_q81_hnan_phase_candidate(
      &input,&frame,&forged,&root,0U,1U,2U,pairs,&output)!=HHS_EXACT_STATUS_OK);
    CHECK(std::memcmp(&output,&saved,sizeof(output))==0);
    root.successful_benchmark_receipt=0U;
    CHECK(hhs_pass220_q81_hnan_phase_candidate(
      &input,&frame,&predecessor,&root,0U,1U,2U,pairs,&output)
      ==HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    CHECK(std::memcmp(&output,&saved,sizeof(output))==0);
    root=witness();
    CHECK(hhs_pass220_q81_hnan_phase_candidate(
      nullptr,&frame,&predecessor,&root,0U,1U,2U,pairs,&output)
      ==HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(std::memcmp(&output,&saved,sizeof(output))==0);
    return 0;
}
