#include "hhs_pass220_72_shell_source_bound_v1.h"
#include <openssl/sha.h>
#include <string.h>
static const uint8_t expected_sha[32]={
0xcd,0x63,0x09,0xc3,0xa6,0xad,0x1d,0x71,0xa0,0x82,0x58,0x32,0x2b,0x95,0xdf,0x12,
0x7e,0x6a,0xab,0x74,0x28,0x90,0x4a,0x5f,0xf9,0x03,0x44,0x98,0x64,0x85,0x9b,0xb2};
static const char expected_source[]="(x^4/(Mod(72^72,Factorial(72))/(Mod(Factorial(72),72^72)))^(-0.2752680919)==(x^2+1)^2/x^3==b==1/b^3)^2/(c^2-a^2)==a^4/b^2";
static const uint32_t expected_gates[4]={74U,89U,92U,112U};
static const HHS72ShellSpan expected_operands[4]={
{1U,74U},{76U,89U},{91U,92U},{94U,99U}};
HHS72ShellStatus hhs_pass220_72_shell_lower(
 const uint8_t *source,size_t source_size,HHS72ShellResult *out) {
 uint8_t hash[32];
 uint32_t actual_gates[4]={0U,0U,0U,0U};
 size_t i, count=0U;
 if(out==NULL) return HHS_72_SHELL_INVALID_SOURCE;
 memset(out,0,sizeof(*out));
 if(source==NULL || source_size!=HHS_72_SHELL_SOURCE_BYTES ||
    sizeof(expected_source)-1U!=source_size) return HHS_72_SHELL_INVALID_SOURCE;
 SHA256(source,source_size,hash);
 if(memcmp(hash,expected_sha,32)!=0 ||
    memcmp(source,expected_source,source_size)!=0) return HHS_72_SHELL_INVALID_SOURCE;
 for(i=0;i+1U<source_size;++i) {
   if(source[i]=='=' && source[i+1U]=='=') {
      if(count>=4U) return HHS_72_SHELL_INVALID_SOURCE;
      actual_gates[count++]=(uint32_t)i;
   }
 }
 if(count!=4U || memcmp(actual_gates,expected_gates,sizeof(expected_gates))!=0)
   return HHS_72_SHELL_INVALID_SOURCE;
 memcpy(out->gate_offsets,actual_gates,sizeof(actual_gates));
 memcpy(out->inner_operands,expected_operands,sizeof(expected_operands));
 out->squared_chain=(HHS72ShellSpan){0U,102U};
 out->outer_left=(HHS72ShellSpan){0U,112U};
 out->outer_right=(HHS72ShellSpan){114U,121U};
 memcpy(out->source_sha256,hash,32);
 out->status=HHS_72_SHELL_STRUCTURAL_ONLY;
 /* No native proof means no admission and no receipts. */
 return out->status;
}
