#include "hhs_pass220_module196_rna_cell_wall_route_v1.h"
#include <cstring>
extern "C" HHSExactStatus hhs_exact_pass220_module196_rna_route_v1(
    uint64_t ingress_ns, uint64_t egress_ns,
    const HHSExactPass219VM81ProgramV1 *lowered_program,
    const HHSExactVM81Frame *input_frame,
    const HHSExactUQCELInputV1 *input,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint8_t feedback_lane, int8_t feedback_trinary,
    HHSModule196Candidate *out_module196,
    HHSExactPass219VM81ExecutionV1 *out_execution,
    HHSExactPass219Holo4PreparedV1 *out_prepared,
    HHSExactPass219Holo4DecisionV1 *out_decision
) {
    if (out_module196 == nullptr || out_execution == nullptr ||
        out_prepared == nullptr || out_decision == nullptr ||
        lowered_program == nullptr || input_frame == nullptr ||
        input == nullptr || transition == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    HHSModule196Candidate candidate{};
    if (!hhs_m196_evaluate(ingress_ns, egress_ns, &candidate))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    /* Inherit the established C VM81 candidate executor, then C++ RNA cell
       wall. Do not mint receipts or promote this candidate to authority. */
    HHSExactPass219VM81ExecutionV1 executed{};
    const HHSExactStatus execution = hhs_exact_pass219_vm81_execute_candidate(
        lowered_program, input_frame, &executed);
    if (execution != HHS_EXACT_STATUS_OK)
        return execution;
    HHSExactPass219Holo4PreparedV1 prepared{};
    HHSExactPass219Holo4DecisionV1 decision{};
    const HHSExactStatus cell_wall = hhs_exact_pass219_rna_vm5184_route(
        input, &executed.after_frame, transition,
        feedback_lane, feedback_trinary, &prepared, &decision);
    if (cell_wall != HHS_EXACT_STATUS_OK)
        return cell_wall;

    std::memcpy(out_module196, &candidate, sizeof(candidate));
    std::memcpy(out_execution, &executed, sizeof(executed));
    std::memcpy(out_prepared, &prepared, sizeof(prepared));
    std::memcpy(out_decision, &decision, sizeof(decision));
    return HHS_EXACT_STATUS_OK;
}
