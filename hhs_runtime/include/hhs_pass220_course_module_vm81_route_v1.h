#ifndef HHS_PASS220_COURSE_MODULE_VM81_ROUTE_V1_H
#define HHS_PASS220_COURSE_MODULE_VM81_ROUTE_V1_H

#include "hhs_pass219_exact_vm81_candidate_adapter_1_21_3.h"
#include "hhs_pass219_rna_vm5184_abi_1_33.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_COURSE_MODULE_COUNT 191U

/*
 * Course module M000..M190 service-port entry.
 *
 * The caller supplies the module's lowered VM81 opcode program. The inherited
 * C candidate executor performs those opcodes; the resulting VM81 frame then
 * enters the existing Pass219 C++ membrane through its public C ABI. No new
 * opcode map, phase normalization or admission path is created here.
 *
 * This route does not itself compile course equations into VM81 instructions.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_course_module_execute_route(
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
);

#ifdef __cplusplus
}
#endif

#endif
