#include "hhs_pass220_72_shell_relation_dispatch_v1.h"
#include <stdio.h>
#include <string.h>
static const uint8_t s[]="(x^4/(Mod(72^72,Factorial(72))/(Mod(Factorial(72),72^72)))^(-0.2752680919)==(x^2+1)^2/x^3==b==1/b^3)^2/(c^2-a^2)==a^4/b^2";
static HHS72RelationDecision evaluate(const HHS72ProofInput *in,uint32_t gate,
 uint32_t left,uint32_t right,void *ctx){
 uint32_t *calls=(uint32_t*)ctx;
 if(!in||gate>=4U||left!=(gate<3U?gate:4U)||
    right!=(gate<3U?gate+1U:5U))return HHS72_RELATION_REJECTED;
 if(memcmp(in->source_bytes,s,sizeof(s)-1U)!=0||
    in->operand_spans[0].byte_start!=1U||
    in->operand_spans[3].byte_end!=99U||
    in->outer_left_span.byte_end!=112U||
    in->outer_right_span.byte_start!=114U)return HHS72_RELATION_REJECTED;
 ++*calls;
 return HHS72_RELATION_CANDIDATE;
}
static HHS72RelationDecision reject_second(const HHS72ProofInput *in,uint32_t gate,uint32_t left,uint32_t right,void *ctx){
 (void)in;(void)left;(void)right;
 ++*(uint32_t*)ctx;
 return gate==1U?HHS72_RELATION_REJECTED:HHS72_RELATION_CANDIDATE;
}
static HHS72RelationDecision invalid_code(const HHS72ProofInput *in,uint32_t gate,uint32_t left,uint32_t right,void *ctx){
 (void)in;(void)gate;(void)left;(void)right;(void)ctx;
 return (HHS72RelationDecision)99;
}
static HHS72RelationDecision unresolved_second(const HHS72ProofInput *in,uint32_t gate,uint32_t left,uint32_t right,void *ctx){
 (void)in;(void)left;(void)right;
 ++*(uint32_t*)ctx;
 return gate==1U?HHS72_RELATION_UNRESOLVED:HHS72_RELATION_CANDIDATE;
}
int main(void){
 HHS72RelationDispatch r;uint32_t calls=0;uint8_t bad[sizeof(s)-1U];
 if(!hhs_pass220_72_shell_dispatch(s,sizeof(s)-1U,evaluate,&calls,&r))return 1;
 if(calls!=4U||r.evaluated_mask!=15U||r.candidate_mask!=15U||
    r.authoritative_proof_mask||r.vm81_admitted)return 2;
 memcpy(bad,s,sizeof(bad));bad[74]^=1U;
 if(hhs_pass220_72_shell_dispatch(bad,sizeof(bad),evaluate,&calls,&r))return 3;
 if(r.authoritative_proof_mask||r.vm81_admitted)return 4;
 if(hhs_pass220_72_shell_dispatch(s,sizeof(s)-1U,NULL,&calls,&r))return 5;
 calls=0;
 if(!hhs_pass220_72_shell_dispatch(s,sizeof(s)-1U,reject_second,&calls,&r))return 6;
 if(calls!=2U||r.evaluated_mask!=3U||r.candidate_mask!=1U||
    r.rejected_mask!=2U||r.authoritative_proof_mask||r.vm81_admitted)return 7;
 calls=0;
 if(!hhs_pass220_72_shell_dispatch(s,sizeof(s)-1U,unresolved_second,&calls,&r))return 8;
 if(calls!=2U||r.evaluated_mask!=3U||r.candidate_mask!=1U||
    r.rejected_mask||r.authoritative_proof_mask||r.vm81_admitted)return 9;
 if(hhs_pass220_72_shell_dispatch(s,sizeof(s)-1U,invalid_code,&calls,&r))return 10;
 if(r.evaluated_mask||r.candidate_mask||r.rejected_mask||
    r.authoritative_proof_mask||r.vm81_admitted)return 11;
 puts("PASS ordered dispatch, early rejection, unresolved stop, invalid-code reset");
 return 0;
}
