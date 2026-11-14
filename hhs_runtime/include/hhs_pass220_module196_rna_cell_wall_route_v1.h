#ifndef HHS_PASS220_MODULE196_RNA_CELL_WALL_ROUTE_V1_H
#define HHS_PASS220_MODULE196_RNA_CELL_WALL_ROUTE_V1_H
#include "hhs_module196_lane5_coprocessor.h"
#include "hhs_pass220_course_module_vm81_route_v1.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Additive M196 route. This cannot produce a signed VM81 admission or Hash216
   receipt. It requires a previously lowered and validated VM81 program. */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_module196_rna_route_v1(
    uint64_t ingress_ns, uint64_t egress_ns,
    const HHSExactPass219VM81ProgramV1 *lowered_program,
    const HHSExactVM81Frame *input_frame,
    const HHSExactUQCELInputV1 *input,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint8_t feedback_lane, int8_t feedback_trinary,
    HHSModule196Candidate *out_module196,
    HHSExactPass219VM81ExecutionV1 *out_execution,
    HHSExactPass219Holo4PreparedV1 *out_prepared,
    HHSExactPass219Holo4DecisionV1 *out_decision);
#ifdef __cplusplus
}
#endif
#endif
