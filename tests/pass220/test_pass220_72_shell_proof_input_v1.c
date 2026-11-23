#include "hhs_pass220_72_shell_proof_input_v1.h"
#include <string.h>
#include <stdio.h>
static const uint8_t s[]="(x^4/(Mod(72^72,Factorial(72))/(Mod(Factorial(72),72^72)))^(-0.2752680919)==(x^2+1)^2/x^3==b==1/b^3)^2/(c^2-a^2)==a^4/b^2";
int main(void){
 HHS72ProofInput p;
 uint8_t bad[sizeof(s)-1U];
 if(!hhs_pass220_72_shell_prepare_proof_input(s,sizeof(s)-1U,&p))return 1;
 if(!p.provenance_authenticated||!p.exact_residue_verified||!p.canonical_projection_verified||p.required_gate_mask!=15U||
     p.proven_gate_mask||p.evaluator_bound||p.vm81_admitted)return 2;
 if(memcmp(p.source_bytes,s,sizeof(s)-1U)!=0||
    p.outer_left_span.byte_end!=112U||
    p.outer_right_span.byte_start!=114U)return 7;
 for(size_t i=0;i<4U;++i){
  const uint32_t starts[4]={1U,76U,91U,94U};
  const uint32_t ends[4]={74U,89U,92U,99U};
  if(p.operand_spans[i].byte_start!=starts[i]||
     p.operand_spans[i].byte_end!=ends[i])return 8;
  if(p.source_gate_offsets[i]!=(uint32_t)(i==0U?74U:i==1U?89U:i==2U?92U:112U))return 3;
  if(p.ordered_left_node[i]!=(uint32_t)(i<3U?i:4U)||
     p.ordered_right_node[i]!=(uint32_t)(i<3U?i+1U:5U))return 4;
 }
 for(size_t i=0;i<sizeof(bad);++i){
  memcpy(bad,s,sizeof(bad));bad[i]^=1U;
  if(hhs_pass220_72_shell_prepare_proof_input(bad,sizeof(bad),&p))return 5;
  if(p.provenance_authenticated||p.exact_residue_verified||p.canonical_projection_verified||p.proven_gate_mask||p.evaluator_bound||p.vm81_admitted)return 6;
 }
 puts("PASS source-bound native evaluator-input construction and 121 mutations");
 return 0;
}
