#include "hhs_pass220_lane5_dyadic_virtual_bridge_v1.h"
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <limits>

#define CHECK(x) do { if (!(x)) { std::fprintf(stderr, "FAIL %d: %s\\n", __LINE__, #x); return 1; } } while (0)

static void root72(char out[HHS_EXACT_HASH72_STRLEN], std::uint8_t offset) {
    for (std::size_t i=0; i<HHS_EXACT_HASH72_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i+offset)%HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN] = '\0';
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
    HHSExactBigUIntView delta{static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)),1U,&one};
    HHSExactUQCELInputV1 input{};
    input.struct_size=static_cast<std::uint32_t>(sizeof(input));
    input.uqcel_version=hhs_exact_uqcel_version();
    input.profile=HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.delta=delta;
    HHSExactVM81Frame frame{};
    frame.words[0]=UINT64_C(0x3ff0000000000000);
    frame.words[1]=9U; frame.words[2]=9U;
    const HHSExactVM81Frame initial=frame;
    HHSExactPass219Hash216TransitionViewV1 parent{};
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent)==HHS_EXACT_STATUS_OK);
    auto w=witness();
    std::array<std::uint8_t,72> digits{};
    digits[0]=71U;digits[1]=70U;
    char binding[65]{};
    for(std::size_t i=0;i<64;++i)binding[i]='a';
    HHSExactPass220Lane5DyadicVirtualCandidateV1 out{};
    CHECK(hhs_pass220_lane5_dyadic_virtual_candidate_route(
        &input,&frame,&parent,&w,0U,1U,2U,digits.data(),-5,36U,binding,&out)
        == HHS_EXACT_STATUS_OK);
    CHECK(out.struct_size==sizeof(out));
    CHECK(out.version==HHS_PASS220_LANE5_DYADIC_VIRTUAL_BRIDGE_VERSION);
    CHECK(out.signed_dyadic_exponent==-5);
    CHECK(out.phase_coordinate72==36U);
    CHECK(std::memcmp(out.radix72_address,digits.data(),72)==0);
    CHECK(std::memcmp(out.pass159_binding_sha256,binding,65)==0);
    CHECK(out.candidate_only==1U && out.cplusplus_rna_cell_wall_routed==1U);
    CHECK(out.requires_pqc_firewall==1U && out.requires_signed_environmental_vm81==1U);
    CHECK(out.source_frame_unchanged==1U);
    CHECK(out.canonical_vm81_mutation_authority==0U);
    CHECK(out.canonical_hash72_mint_authority==0U);
    CHECK(out.canonical_hash216_mint_authority==0U);
    CHECK(out.canonical_persistence_authority==0U);
    CHECK(std::memcmp(&frame,&initial,sizeof(frame))==0);
    // Independent Python byte-serialization vector for the identical frame,
    // address, exponent, phase and Pass159 digest reference. Not a PQ signature.
    constexpr std::uint8_t expected_digest[32] = {
        0x07,0xa1,0xc4,0x69,0xe4,0x09,0xe1,0xc9,
        0x11,0xcf,0x5d,0xda,0xe7,0x3a,0x34,0x19,
        0xe9,0x8d,0x2d,0xf4,0x43,0x56,0xa8,0xa0,
        0x5e,0xcb,0x72,0xbe,0x53,0xae,0x17,0x88
    };
    std::array<std::uint8_t,32> digest{};
    CHECK(hhs_pass220_lane5_dyadic_binding_material_sha256(
        &frame,digits.data(),-5,36U,binding,digest.data()) == HHS_EXACT_STATUS_OK);
    CHECK(std::memcmp(digest.data(),expected_digest,32)==0);
    const auto digest_original = digest;
    auto changed_digits = digits;
    changed_digits[0] = 70U;
    CHECK(hhs_pass220_lane5_dyadic_binding_material_sha256(
        &frame,changed_digits.data(),-5,36U,binding,digest.data()) == HHS_EXACT_STATUS_OK);
    CHECK(digest != digest_original);
    CHECK(hhs_pass220_lane5_dyadic_binding_material_sha256(
        &frame,digits.data(),-4,36U,binding,digest.data()) == HHS_EXACT_STATUS_OK);
    CHECK(digest != digest_original);
    CHECK(hhs_pass220_lane5_dyadic_binding_material_sha256(
        &frame,digits.data(),-5,37U,binding,digest.data()) == HHS_EXACT_STATUS_OK);
    CHECK(digest != digest_original);
    char another_binding[65]{};
    std::memcpy(another_binding,binding,65);
    another_binding[0] = 'b';
    CHECK(hhs_pass220_lane5_dyadic_binding_material_sha256(
        &frame,digits.data(),-5,36U,another_binding,digest.data()) == HHS_EXACT_STATUS_OK);
    CHECK(digest != digest_original);
    auto another_frame = frame;
    another_frame.words[80] = 1U;
    CHECK(hhs_pass220_lane5_dyadic_binding_material_sha256(
        &another_frame,digits.data(),-5,36U,binding,digest.data()) == HHS_EXACT_STATUS_OK);
    CHECK(digest != digest_original);
    digest.fill(0xA5);
    CHECK(hhs_pass220_lane5_dyadic_binding_material_sha256(
        &frame,digits.data(),-5,72U,binding,digest.data()) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    for(const auto value : digest) CHECK(value == 0xA5U);
    CHECK(hhs_pass220_lane5_dyadic_binding_material_sha256(
        &frame,digits.data(),std::numeric_limits<std::int64_t>::min(),
        36U,binding,digest.data()) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    for(const auto value : digest) CHECK(value == 0xA5U);
    const auto saved=out;
    auto digits_bad=digits;digits_bad[71]=72U;
    CHECK(hhs_pass220_lane5_dyadic_virtual_candidate_route(
        &input,&frame,&parent,&w,0U,1U,2U,digits_bad.data(),-5,36U,binding,&out)
        == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(std::memcmp(&out,&saved,sizeof(out))==0);
    CHECK(hhs_pass220_lane5_dyadic_virtual_candidate_route(
        &input,&frame,&parent,&w,0U,1U,2U,digits.data(),-5,72U,binding,&out)
        == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(std::memcmp(&out,&saved,sizeof(out))==0);
    CHECK(hhs_pass220_lane5_dyadic_virtual_candidate_route(
        &input,&frame,&parent,&w,0U,1U,2U,digits.data(),
        std::numeric_limits<std::int64_t>::min(),36U,binding,&out)
        == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(std::memcmp(&out,&saved,sizeof(out))==0);
    auto invalid_binding=std::array<char,65>{};
    std::memcpy(invalid_binding.data(),binding,65);
    invalid_binding[2]='z';
    CHECK(hhs_pass220_lane5_dyadic_virtual_candidate_route(
        &input,&frame,&parent,&w,0U,1U,2U,digits.data(),-5,36U,invalid_binding.data(),&out)
        == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(std::memcmp(&out,&saved,sizeof(out))==0);
    auto forged=parent;
    forged.transition_identity216[0]=
        forged.transition_identity216[0]=='0'?'1':'0';
    CHECK(hhs_pass220_lane5_dyadic_virtual_candidate_route(
        &input,&frame,&forged,&w,0U,1U,2U,digits.data(),-5,36U,binding,&out)
        != HHS_EXACT_STATUS_OK);
    CHECK(std::memcmp(&out,&saved,sizeof(out))==0);
    w.successful_benchmark_receipt=0U;
    CHECK(hhs_pass220_lane5_dyadic_virtual_candidate_route(
        &input,&frame,&parent,&w,0U,1U,2U,digits.data(),-5,36U,binding,&out)
        == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    CHECK(std::memcmp(&out,&saved,sizeof(out))==0);
    CHECK(std::memcmp(&frame,&initial,sizeof(frame))==0);
    return 0;
}
