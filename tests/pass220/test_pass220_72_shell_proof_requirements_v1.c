#include "hhs_pass220_72_shell_proof_requirements_v1.h"
#include <stdio.h>
#include <string.h>
static const uint8_t s[]="(x^4/(Mod(72^72,Factorial(72))/(Mod(Factorial(72),72^72)))^(-0.2752680919)==(x^2+1)^2/x^3==b==1/b^3)^2/(c^2-a^2)==a^4/b^2";
int main(void){
 HHS72GateGraph g;HHS72ProofRequirements p;
 if(!hhs_pass220_72_shell_build_gate_graph(s,sizeof(s)-1U,&g))return 1;
 if(!hhs_pass220_72_shell_requirements(&g,&p))return 2;
 if(p.required_mask!=15U||p.present_mask!=15U||p.proved_mask||p.native_admitted||p.vm81_admitted)return 3;
 g.source_sha256[0]^=1U;
 if(hhs_pass220_72_shell_requirements(&g,&p)||p.present_mask)return 4;
 if(!hhs_pass220_72_shell_build_gate_graph(s,sizeof(s)-1U,&g))return 5;
 g.operands[0].byte_end--;
 if(hhs_pass220_72_shell_requirements(&g,&p))return 6;
 if(!hhs_pass220_72_shell_build_gate_graph(s,sizeof(s)-1U,&g))return 7;
 g.edges[3].right_node=4U;
 if(hhs_pass220_72_shell_requirements(&g,&p))return 8;
 if(!hhs_pass220_72_shell_build_gate_graph(s,sizeof(s)-1U,&g))return 9;
 g.outer_left.byte_end=111U;
 if(hhs_pass220_72_shell_requirements(&g,&p))return 10;
 if(!hhs_pass220_72_shell_build_gate_graph(s,sizeof(s)-1U,&g))return 11;
 g.edges[1].proved=1U;
 if(hhs_pass220_72_shell_requirements(&g,&p))return 4;
 if(p.proved_mask||p.native_admitted||p.vm81_admitted)return 5;
 puts("PASS gate requirements mask; no structural proof promotion");
 return 0;
}
