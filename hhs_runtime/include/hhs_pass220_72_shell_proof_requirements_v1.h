#ifndef HHS_PASS220_72_SHELL_PROOF_REQUIREMENTS_V1_H
#define HHS_PASS220_72_SHELL_PROOF_REQUIREMENTS_V1_H
#include "hhs_pass220_72_shell_gate_graph_v1.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
 uint32_t required_mask;
 uint32_t present_mask;
 uint32_t proved_mask;
 uint8_t native_admitted;
 uint8_t vm81_admitted;
} HHS72ProofRequirements;
/* Only records readiness: source-bound graph is not a proof witness. */
int hhs_pass220_72_shell_requirements(const HHS72GateGraph *graph,
 HHS72ProofRequirements *out);
#ifdef __cplusplus
}
#endif
#endif
