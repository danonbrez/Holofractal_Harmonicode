#include "hhs_pass220_module196_rna_cell_wall_route_v1.h"
#include <cassert>
#include <cstdint>
#include <cstring>
#include <cstdio>

int main() {
    HHSExactPass219VM81ProgramV1 program{};
    HHSExactVM81Frame frame{};
    HHSExactUQCELInputV1 input{};
    HHSExactPass219Hash216TransitionViewV1 predecessor{};
    HHSModule196Candidate witness{};
    HHSExactPass219VM81ExecutionV1 executed{};
    HHSExactPass219Holo4PreparedV1 prepared{};
    HHSExactPass219Holo4DecisionV1 decision{};
    uint8_t one=1U;
    assert(hhs_exact_pass219_vm81_lower_monolithic_structure(&program)==HHS_EXACT_STATUS_OK);
    for(std::uint32_t k=0;k<HHS_EXACT_VM81_CELLS;k++)
        frame.words[k]=UINT64_C(0x0102030405060708) ^
              ((std::uint64_t)(k+1U)*UINT64_C(0x9E3779B97F4A7C15));
    assert(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&predecessor)==HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&predecessor)==HHS_EXACT_STATUS_OK);
    input.struct_size=(uint32_t)sizeof(input);
    input.uqcel_version=hhs_exact_uqcel_version();
    input.profile=HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.delta.struct_size=(uint32_t)sizeof(input.delta);
    input.delta.byte_length=1U;
    input.delta.bytes_be=&one;
    const HHSExactStatus status=hhs_exact_pass220_module196_rna_route_v1(
        179971179971ULL,179971179972ULL,&program,&frame,&input,&predecessor,
        HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,0,
        &witness,&executed,&prepared,&decision);
    if(status!=HHS_EXACT_STATUS_OK) {
        std::fprintf(stderr,"module196_real_native_route_status=%d\n",(int)status);
        return 2;
    }
    assert(witness.accepted_candidate==1U);
    assert(witness.equality_cells==18U && witness.local_p2_cells==63U);
    assert(witness.hnan_addresses==25U && witness.hnan_children==2025U);
    assert(witness.sum==9105 && witness.trace==1297);
    assert(witness.ingress_ns==179971179971ULL && witness.egress_ns==179971179972ULL);
    assert(!witness.vm81_mutation_authority && !witness.hash72_authority && !witness.hash216_authority);
    assert(executed.halted==1U && executed.candidate_frame_bound==1U);
    assert(prepared.word_visits==81U && prepared.hash216_positions_complete==1U);
    assert(prepared.candidate_only==1U && decision.candidate_only==1U);
    assert(!executed.vm81_mutation_authority && !executed.hash72_commit_authority);
    HHSExactPass219VM81ReplayV1 replay{};
    assert(hhs_exact_pass219_vm81_replay_candidate(&program,&frame,&executed,&replay)==HHS_EXACT_STATUS_OK);
    assert(replay.replay_verified==1U && replay.authority_boundary_equal==1U);

    // Bad declared source identity must fail without publishing any output.
    HHSExactPass219VM81ProgramV1 tampered=program;
    tampered.source_sha256[0]^=1U;
    HHSModule196Candidate denied{};
    denied.accepted_candidate=77U;
    assert(hhs_exact_pass220_module196_rna_route_v1(
       179971179971ULL,179971179972ULL,&tampered,&frame,&input,&predecessor,
       HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,0,
       &denied,&executed,&prepared,&decision)==HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(denied.accepted_candidate==77U);

    // The predecessor must not be silently reconstructed on bad input.
    HHSExactPass219Hash216TransitionViewV1 bad=predecessor;
    bad.transition_identity216[0] = bad.transition_identity216[0]=='0'?'1':'0';
    assert(hhs_exact_pass220_module196_rna_route_v1(
       179971179971ULL,179971179972ULL,&program,&frame,&input,&bad,
       HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,0,
       &denied,&executed,&prepared,&decision)==HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(denied.accepted_candidate==77U);
    std::puts("MODULE196_REAL_LINKED_CANDIDATE_REPLAY=PASS; canonical_VM81_admission=NOT_INVOKED");
    return 0;
}
