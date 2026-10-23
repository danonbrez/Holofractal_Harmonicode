#ifndef HHS_PASS220_72_SHELL_RELATION_DISPATCH_V1_H
#define HHS_PASS220_72_SHELL_RELATION_DISPATCH_V1_H
#include "hhs_pass220_72_shell_proof_input_v1.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef enum { HHS72_RELATION_UNRESOLVED=0, HHS72_RELATION_REJECTED=1,
               HHS72_RELATION_CANDIDATE=2 } HHS72RelationDecision;
typedef HHS72RelationDecision (*HHS72RelationEvaluator)(
 const HHS72ProofInput *input, uint32_t gate_index, uint32_t left_node,
 uint32_t right_node, void *context);
typedef struct {
 uint32_t evaluated_mask;
 uint32_t candidate_mask;
 uint32_t rejected_mask;
 uint32_t authoritative_proof_mask;
 uint8_t vm81_admitted;
} HHS72RelationDispatch;
int hhs_pass220_72_shell_dispatch(
 const uint8_t *source, size_t length, HHS72RelationEvaluator evaluator,
 void *context, HHS72RelationDispatch *out);
#ifdef __cplusplus
}
#endif
#endif
