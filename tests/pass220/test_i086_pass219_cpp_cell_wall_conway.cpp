#include "hhs_pass219_core_holographic_rna_cell_wall_1_24.hpp"
#include "hhs_pass220_i086_lane5_conway_cell_wall_v1.h"
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>

#define CHECK(x) do { if (!(x)) { std::fprintf(stderr, "FAIL line %d: %s\\n", __LINE__, #x); return 1; } } while (0)


static void root72(char out[HHS_EXACT_HASH72_STRLEN], std::uint8_t offset) {
    for (std::size_t i = 0; i < HHS_EXACT_HASH72_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN] = '\0';
}
static HHSExactPass220I028Lane5ConstructorWitnessV1 valid_witness() {
    HHSExactPass220I028Lane5ConstructorWitnessV1 w{};
    w.struct_size = static_cast<std::uint32_t>(sizeof(w));
    w.version = HHS_EXACT_PASS220_I028_LANE5_G3_VERSION;
    root72(w.pipeline_root_hash72, 13U);
    root72(w.constructor_graph_root_hash72, 17U);
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
    std::uint8_t one = 1U;
    HHSExactBigUIntView a2{static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)), 1U, &one};
    hhs::rna::OrthogonalGlyphMembrane membrane(a2, a2);
    CHECK(membrane.status() == HHS_EXACT_STATUS_OK);
    hhs::rna::CoreHolographicRNACellWall wall(membrane);
    std::array<std::uint8_t, 81> seed{};
    std::array<std::uint8_t, 81> next{};
    CHECK(wall.evolve_conway81(seed, next) == HHS_EXACT_STATUS_OK);
    CHECK(next == seed); // Empty configuration is stable.
    seed[4*9+3] = seed[4*9+4] = seed[4*9+5] = 1U;
    CHECK(wall.evolve_conway81(seed, next) == HHS_EXACT_STATUS_OK);
    std::array<std::uint8_t, 81> vertical{};
    vertical[3*9+4] = vertical[4*9+4] = vertical[5*9+4] = 1U;
    CHECK(next == vertical);
    CHECK(wall.evolve_conway81(next, next) == HHS_EXACT_STATUS_OK);
    CHECK(next == seed); // Period two, including alias-safe output.
    seed.fill(0U);
    seed[4*9+8] = seed[4*9+0] = seed[4*9+1] = 1U;
    CHECK(wall.evolve_conway81(seed, next) == HHS_EXACT_STATUS_OK);
    vertical.fill(0U);
    vertical[3*9+0] = vertical[4*9+0] = vertical[5*9+0] = 1U;
    CHECK(next == vertical); // Toroidal column wrap.
    HHSExactUQCELInputV1 ingress{};
    ingress.struct_size=static_cast<std::uint32_t>(sizeof(ingress));
    ingress.uqcel_version=hhs_exact_uqcel_version();
    ingress.profile=HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    ingress.delta=a2;
    HHSExactVM81Frame frame{};
    frame.words[0]=UINT64_C(0x3ff0000000000000);
    frame.words[1]=9U;
    frame.words[2]=9U;
    frame.words[4*9+3]=frame.words[4*9+4]=frame.words[4*9+5]=1U;
    const HHSExactVM81Frame initial=frame;
    HHSExactPass219Hash216TransitionViewV1 predecessor{};
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&predecessor)==HHS_EXACT_STATUS_OK);
    auto constructor=valid_witness();
    HHSExactPass220I086Lane5ConwayCandidateV1 candidate{};
    CHECK(hhs_pass220_i086_lane5_conway81_cell_wall(
        &ingress,&frame,&predecessor,&constructor,0U,1U,2U,&candidate)
        == HHS_EXACT_STATUS_OK);
    CHECK(candidate.struct_size==sizeof(candidate));
    CHECK(candidate.mediated_via_pass219_rna_cell_wall==1U);
    CHECK(candidate.mediated_via_lane5_bios==1U);
    CHECK(candidate.holo4_four_lanes_prepared==1U);
    CHECK(candidate.predecessor_hash216_verified==1U);
    CHECK(candidate.candidate_only==1U);
    CHECK(candidate.canonical_vm81_mutation_authority==0U);
    CHECK(candidate.canonical_hash72_mint_authority==0U);
    CHECK(candidate.canonical_hash216_mint_authority==0U);
    CHECK(candidate.canonical_persistence_authority==0U);
    CHECK(candidate.signed_environmental_admission_invoked==0U);
    CHECK(std::memcmp(&frame,&initial,sizeof(frame))==0);
    std::array<std::uint8_t,81> expected_before{},expected_after{};
    for(std::size_t i=0;i<81;++i)
        expected_before[i]=static_cast<std::uint8_t>(frame.words[i]&1U);
    CHECK(wall.evolve_conway81(expected_before,expected_after)==HHS_EXACT_STATUS_OK);
    for(std::size_t i=0;i<81;++i) {
        CHECK(candidate.occupancy_before[i]==expected_before[i]);
        CHECK(candidate.occupancy_after[i]==expected_after[i]);
    }
    const auto saved=candidate;
    auto forged=predecessor;
    forged.transition_identity216[0]=
        forged.transition_identity216[0]=='0'?'1':'0';
    CHECK(hhs_pass220_i086_lane5_conway81_cell_wall(
        &ingress,&frame,&forged,&constructor,0U,1U,2U,&candidate)
        != HHS_EXACT_STATUS_OK);
    CHECK(std::memcmp(&candidate,&saved,sizeof(candidate))==0);
    constructor.successful_benchmark_receipt=0U;
    CHECK(hhs_pass220_i086_lane5_conway81_cell_wall(
        &ingress,&frame,&predecessor,&constructor,0U,1U,2U,&candidate)
        == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    CHECK(std::memcmp(&candidate,&saved,sizeof(candidate))==0);
    constructor=valid_witness();
    CHECK(hhs_pass220_i086_lane5_conway81_cell_wall(
        nullptr,&frame,&predecessor,&constructor,0U,1U,2U,&candidate)
        == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(std::memcmp(&candidate,&saved,sizeof(candidate))==0);
    CHECK(hhs_pass220_i086_lane5_conway81_cell_wall(
        &ingress,nullptr,&predecessor,&constructor,0U,1U,2U,&candidate)
        == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(std::memcmp(&candidate,&saved,sizeof(candidate))==0);
    // Invalid outer UQCEL envelopes must fail before the Pass219/Lane5 route.
    auto invalid_ingress = ingress;
    invalid_ingress.struct_size = 0U;
    CHECK(hhs_pass220_i086_lane5_conway81_cell_wall(
        &invalid_ingress,&frame,&predecessor,&constructor,0U,1U,2U,&candidate)
        == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(std::memcmp(&candidate,&saved,sizeof(candidate))==0);
    invalid_ingress = ingress;
    invalid_ingress.uqcel_version ^= 1U;
    CHECK(hhs_pass220_i086_lane5_conway81_cell_wall(
        &invalid_ingress,&frame,&predecessor,&constructor,0U,1U,2U,&candidate)
        == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(std::memcmp(&candidate,&saved,sizeof(candidate))==0);
    invalid_ingress = ingress;
    invalid_ingress.profile = 0U;
    CHECK(hhs_pass220_i086_lane5_conway81_cell_wall(
        &invalid_ingress,&frame,&predecessor,&constructor,0U,1U,2U,&candidate)
        == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(std::memcmp(&candidate,&saved,sizeof(candidate))==0);
    seed[0] = 2U;
    next.fill(7U);
    CHECK(wall.evolve_conway81(seed, next) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    for (auto v : next) CHECK(v == 7U); // Fail closed, no partial output.
    return 0;
}
