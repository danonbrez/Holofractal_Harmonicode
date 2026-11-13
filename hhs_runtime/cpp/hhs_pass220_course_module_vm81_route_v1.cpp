#include "hhs_pass220_course_module_vm81_route_v1.h"

#include <cstring>

extern "C" HHSExactStatus hhs_exact_pass220_course_module_execute_route(
    uint32_t module_number,
    const HHSExactPass219VM81ProgramV1 *lowered_program,
    const HHSExactVM81Frame *input_frame,
    const HHSExactUQCELInputV1 *input,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219VM81ExecutionV1 *out_execution,
    HHSExactPass219Holo4PreparedV1 *out_prepared,
    HHSExactPass219Holo4DecisionV1 *out_decision
) {
    if (out_execution != nullptr)
        std::memset(out_execution, 0, sizeof(*out_execution));
    if (out_prepared != nullptr)
        std::memset(out_prepared, 0, sizeof(*out_prepared));
    if (out_decision != nullptr)
        std::memset(out_decision, 0, sizeof(*out_decision));

    if (module_number >= HHS_COURSE_MODULE_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (lowered_program == nullptr || input_frame == nullptr || input == nullptr ||
        transition == nullptr || out_execution == nullptr ||
        out_prepared == nullptr || out_decision == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    HHSExactPass219VM81ExecutionV1 executed{};
    const HHSExactStatus lowered_status = hhs_exact_pass219_vm81_execute_candidate(
        lowered_program, input_frame, &executed);
    if (lowered_status != HHS_EXACT_STATUS_OK)
        return lowered_status;

    HHSExactPass219Holo4PreparedV1 prepared{};
    HHSExactPass219Holo4DecisionV1 decision{};
    const HHSExactStatus routed_status = hhs_exact_pass219_rna_vm5184_route(
        input, &executed.after_frame, transition, feedback_lane,
        feedback_trinary, &prepared, &decision);
    if (routed_status != HHS_EXACT_STATUS_OK)
        return routed_status;

    std::memcpy(out_execution, &executed, sizeof(executed));
    std::memcpy(out_prepared, &prepared, sizeof(prepared));
    std::memcpy(out_decision, &decision, sizeof(decision));
    return HHS_EXACT_STATUS_OK;
}
