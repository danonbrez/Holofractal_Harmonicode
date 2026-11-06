#include "hhs_pass220_72_shell_relation_dispatch_v1.h"
#include <string.h>
int hhs_pass220_72_shell_dispatch(
 const uint8_t *source,size_t length,HHS72RelationEvaluator evaluator,
 void *context,HHS72RelationDispatch *out) {
 HHS72ProofInput input;
 uint32_t i;
 if(!out)return 0;
 memset(out,0,sizeof(*out));
 if(!evaluator||!hhs_pass220_72_shell_prepare_proof_input(source,length,&input)||
    !input.provenance_authenticated||input.required_gate_mask!=15U||
    input.proven_gate_mask||input.vm81_admitted)return 0;
 for(i=0U;i<4U;++i) {
   HHS72RelationDecision d=evaluator(&input,i,input.ordered_left_node[i],
                                       input.ordered_right_node[i],context);
   out->evaluated_mask|=(1U<<i);
   if(d==HHS72_RELATION_CANDIDATE)out->candidate_mask|=(1U<<i);
   else if(d==HHS72_RELATION_REJECTED) {out->rejected_mask|=(1U<<i);break;}
   else if(d!=HHS72_RELATION_UNRESOLVED){memset(out,0,sizeof(*out));return 0;}
   else break; /* A later ordered gate cannot execute past an unresolved predecessor. */
 }
 /* Candidate answers from a callback are not native authority witnesses. */
 return 1;
}
