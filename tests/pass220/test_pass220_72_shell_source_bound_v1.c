#include "hhs_pass220_72_shell_source_bound_v1.h"
#include <stdio.h>
#include <string.h>
static const unsigned char source[]="(x^4/(Mod(72^72,Factorial(72))/(Mod(Factorial(72),72^72)))^(-0.2752680919)==(x^2+1)^2/x^3==b==1/b^3)^2/(c^2-a^2)==a^4/b^2";
int main(void){
 HHS72ShellResult result;
 unsigned char changed[sizeof(source)-1];
 if(hhs_pass220_72_shell_lower(source,sizeof(source)-1,&result)!=HHS_72_SHELL_STRUCTURAL_ONLY) return 1;
 if(result.native_proof_admitted || result.vm81_admitted ||
    result.outer_right.byte_start!=114U || result.inner_operands[3].byte_end!=99U ||
    result.squared_chain.byte_start!=0U || result.squared_chain.byte_end!=102U ||
    result.outer_left.byte_end!=112U || source[101]!='2' || source[102]!='/') return 2;
 memcpy(changed,source,sizeof(changed));
 changed[70]^=1U;
 if(hhs_pass220_72_shell_lower(changed,sizeof(changed),&result)!=HHS_72_SHELL_INVALID_SOURCE) return 3;
 if(result.status!=HHS_72_SHELL_INVALID_SOURCE || result.vm81_admitted) return 4;
 for(size_t i=0;i<sizeof(changed);++i){memcpy(changed,source,sizeof(changed));changed[i]^=1U;if(hhs_pass220_72_shell_lower(changed,sizeof(changed),&result)!=HHS_72_SHELL_INVALID_SOURCE)return 5;if(result.native_proof_admitted||result.vm81_admitted)return 6;}
 if(hhs_pass220_72_shell_lower(NULL,sizeof(source)-1,&result)!=HHS_72_SHELL_INVALID_SOURCE)return 7;
 if(hhs_pass220_72_shell_lower(source,sizeof(source)-2,&result)!=HHS_72_SHELL_INVALID_SOURCE)return 8;
 if(hhs_pass220_72_shell_lower(source,sizeof(source)-1,NULL)!=HHS_72_SHELL_INVALID_SOURCE)return 9;
 if(hhs_pass220_72_shell_lower(source,sizeof(source)-1,&result)!=HHS_72_SHELL_STRUCTURAL_ONLY)return 10;
 for(size_t i=0;i<4;++i){const uint32_t offsets[4]={74U,89U,92U,112U};if(result.gate_offsets[i]!=offsets[i])return 11;}
 puts("PASS exact source, 121 single-byte mutations, invalid inputs, four gates, fail closed");
 return 0;
}
