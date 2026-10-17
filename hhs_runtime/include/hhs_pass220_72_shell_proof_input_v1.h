#ifndef HHS_PASS220_72_SHELL_PROOF_INPUT_V1_H
#define HHS_PASS220_72_SHELL_PROOF_INPUT_V1_H
#include "hhs_pass220_72_shell_proof_requirements_v1.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
 uint8_t source_sha256[32];
 uint32_t source_gate_offsets[4];
 uint8_t source_bytes[HHS_72_SHELL_SOURCE_BYTES];
 HHS72ShellSpan operand_spans[4];
 HHS72ShellSpan outer_left_span;
 HHS72ShellSpan outer_right_span;
 uint32_t ordered_left_node[4];
 uint32_t ordered_right_node[4];
 uint32_t required_gate_mask;
 uint32_t proven_gate_mask;
 uint8_t provenance_authenticated;
 uint8_t exact_residue_verified;
 uint8_t canonical_projection_verified;
 uint8_t evaluator_bound;
 uint8_t vm81_admitted;
} HHS72ProofInput;
int hhs_pass220_72_shell_prepare_proof_input(
 const uint8_t *source,size_t size,HHS72ProofInput *out);
#ifdef __cplusplus
}
#endif
#endif
