#include "hhs_pass220_module196_rna_cell_wall_route_v1.h"
#include <cassert>
#include <cstring>
static int executions=0, wall_calls=0;
extern "C" HHSExactStatus hhs_exact_pass219_vm81_execute_candidate(
    const HHSExactPass219VM81ProgramV1 *program,
    const HHSExactVM81Frame *frame,
    HHSExactPass219VM81ExecutionV1 *out) {
    (void)program;
    ++executions;
    std::memcpy(&out->after_frame,frame,sizeof(*frame));
    return HHS_EXACT_STATUS_OK;
}
extern "C" HHSExactStatus hhs_exact_pass219_rna_vm5184_route(
    const HHSExactUQCELInputV1 *input,
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *predecessor,
    uint8_t lane,int8_t trinary,HHSExactPass219Holo4PreparedV1 *prepared,
    HHSExactPass219Holo4DecisionV1 *decision) {
    (void)input;(void)frame;(void)predecessor;(void)lane;
    (void)trinary;(void)prepared;(void)decision;
    ++wall_calls;
    return HHS_EXACT_STATUS_OK;
}
int main() {
    HHSExactPass219VM81ProgramV1 program{};
    HHSExactVM81Frame frame{};
    HHSExactUQCELInputV1 input{};
    HHSExactPass219Hash216TransitionViewV1 previous{};
    HHSExactPass219VM81ExecutionV1 executed{};
    HHSExactPass219Holo4PreparedV1 prepared{};
    HHSExactPass219Holo4DecisionV1 decision{};
    HHSModule196Candidate candidate{};
    auto run=[&](uint64_t ingress,uint64_t egress,
                 HHSExactPass219VM81ProgramV1 *prog) {
        return hhs_exact_pass220_module196_rna_route_v1(
            ingress,egress,prog,&frame,&input,&previous,0,0,
            &candidate,&executed,&prepared,&decision);
    };
    assert(run(40,39,&program)==HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(executions==0 && wall_calls==0 && !candidate.accepted_candidate);
    assert(run(40,41,nullptr)==HHS_EXACT_STATUS_INVALID_ARGUMENT);
    assert(executions==0 && wall_calls==0);
    assert(run(40,41,&program)==HHS_EXACT_STATUS_OK);
    assert(executions==1 && wall_calls==1);
    assert(candidate.accepted_candidate && candidate.equality_cells==18 &&
           candidate.local_p2_cells==63 && candidate.hnan_children==2025);
    assert(candidate.ingress_ns==40 && candidate.egress_ns==41);
    assert(!candidate.vm81_mutation_authority && !candidate.hash72_authority &&
           !candidate.hash216_authority);
}
