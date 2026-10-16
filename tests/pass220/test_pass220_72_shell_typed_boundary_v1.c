#include "hhs_pass220_72_shell_typed_boundary_v1.h"
#include <string.h>
#include <stdio.h>
static const uint8_t s[]="(x^4/(Mod(72^72,Factorial(72))/(Mod(Factorial(72),72^72)))^(-0.2752680919)==(x^2+1)^2/x^3==b==1/b^3)^2/(c^2-a^2)==a^4/b^2";
int main(void) {
 HHS72ShellProofResult p;
 uint8_t bad[sizeof(s)-1U];
 if(hhs_pass220_72_shell_typed_boundary(s,sizeof(s)-1U,&p)!=HHS_72_SHELL_PROOF_UNRESOLVED)return 1;
 if(!p.exact_residue_verified||p.required_gates!=4U||p.proven_gates!=0U||p.vm81_admitted||p.native_proof_admitted)return 2;
 memcpy(bad,s,sizeof(bad));bad[89]^=1U;
 if(hhs_pass220_72_shell_typed_boundary(bad,sizeof(bad),&p)!=HHS_72_SHELL_PROOF_INVALID)return 3;
 if(p.exact_residue_verified||p.proven_gates||p.vm81_admitted||p.native_proof_admitted)return 4;
 puts("PASS source-bound typed boundary remains unresolved and fail-closed");
 return 0;
}
