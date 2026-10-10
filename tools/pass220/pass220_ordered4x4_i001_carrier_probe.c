/* Exact Pass 220 I001 rational scientific 81x64 carrier conformance.
 * THIS IS A SPECIFIC NORMALIZATION PROFILE, not all native tensor formats.
 */
#include "hhs_runtime_exact_abi.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define CHECK(c,msg) do{if(!(c)){fprintf(stderr,"FAIL:%s\n",msg);return 1;}}while(0)

static const uint8_t zero_token[] =
 "+00000000000000000000/00000000000000000001e+00000000000000000000";
static uint8_t source[HHS220_ORDERED4X4_SOURCE_BYTES+1U];
static uint8_t s_state[5184U],v_state[5184U];
static HHSExactPass219Hash216TransitionViewV1 parent;
static HHS220Ordered4x4I001CarrierV1 original,repeat,changed,invalid;

static void encode_offset_profile(uint8_t *state, uint8_t seed) {
 size_t cell;
 for(cell=0U;cell<81U;++cell) {
  uint8_t *token=state+64U*cell;
  memcpy(token,zero_token,64U);
  token[20]=(uint8_t)('0'+(seed+(uint8_t)cell)%9U);
 }
}
static int check(const HHS220Ordered4x4NativeTensorBindingV1 *s,
                 const HHS220Ordered4x4NativeTensorBindingV1 *v,
                 HHS220Ordered4x4I001CarrierV1 *out) {
 return hhs_exact_pass220_ordered4x4_i001_carrier_validate(
  source,HHS220_ORDERED4X4_SOURCE_BYTES,s,v,&parent,out)==HHS_EXACT_STATUS_OK;
}
/* Invalid input MUST NOT leak a partially decoded 81-cell state, even if the
 * caller filled the output with forged authority markers before this call. */
static int witness_is_fully_zero(const HHS220Ordered4x4I001CarrierV1 *value) {
 const uint8_t *bytes=(const uint8_t *)value;
 size_t i;
 for(i=0U;i<sizeof(*value);++i) {
  if(bytes[i]!=0U) return 0;
 }
 return 1;
}

int main(int argc, char **argv) {
 HHS220Ordered4x4NativeTensorBindingV1 s,v;
 uint8_t crosslang_s[5184U],crosslang_v[5184U];
 FILE *f=fopen("contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode","rb");
 size_t n,i;
 CHECK(sizeof(zero_token)-1U==64U,"exact 64-character inherited I001 token");
 CHECK(f!=NULL,"verbatim equation open");
 n=fread(source,1U,sizeof(source),f);
 CHECK(!ferror(f) && fclose(f)==0 && n==HHS220_ORDERED4X4_SOURCE_BYTES,
       "verbatim 366 bytes");
 CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent)==HHS_EXACT_STATUS_OK,
       "indexed inherited Hash216 reference");
 encode_offset_profile(s_state,0U);
 encode_offset_profile(v_state,4U);
 memset(&s,0,sizeof(s));memset(&v,0,sizeof(v));
 s.struct_size=(uint32_t)sizeof(s);s.symbol='s';s.cell81=4U;s.operation64=9U;
 s.state_utf8=s_state;s.state_bytes=sizeof(s_state);
 s.predecessor_hash216=(const uint8_t*)parent.transition_identity216;
 s.predecessor_bytes=216U;
 v.struct_size=(uint32_t)sizeof(v);v.symbol='v';v.cell81=8U;v.operation64=17U;
 v.state_utf8=v_state;v.state_bytes=sizeof(v_state);
 v.predecessor_hash216=(const uint8_t*)parent.transition_identity216;
 v.predecessor_bytes=216U;
 CHECK(argc==1 || argc==3,"optional pair of independently serialized I001 fixtures");
 if(argc==3) {
  FILE *fs=fopen(argv[1],"rb"), *fv=fopen(argv[2],"rb");
  size_t ns,nv;
  CHECK(fs!=NULL && fv!=NULL,"Python reference fixtures readable");
  ns=fread(crosslang_s,1U,sizeof(crosslang_s),fs);
  nv=fread(crosslang_v,1U,sizeof(crosslang_v),fv);
  CHECK(!ferror(fs) && !ferror(fv) &&
        fclose(fs)==0 && fclose(fv)==0 &&
        ns==5184U && nv==5184U,"reference exact 5184 byte width");
  CHECK(memcmp(crosslang_s,s_state,5184U)==0 &&
        memcmp(crosslang_v,v_state,5184U)==0,
        "C exact I001 normalized carrier bytes match inherited Python serializer");
  s.state_utf8=crosslang_s;v.state_utf8=crosslang_v;
  CHECK(check(&s,&v,&changed),
        "independent Python serializer fixtures accepted by native C verifier");
  s.state_utf8=s_state;v.state_utf8=v_state;
 }

 CHECK(check(&s,&v,&original),"strict two-carrier validation");
 CHECK(check(&s,&v,&repeat),"deterministic carrier repeat");
 CHECK(memcmp(&original,&repeat,sizeof(original))==0,"full native witness replay");
 CHECK(original.profile_cells==81U && original.profile_token_bytes==64U &&
       original.s_valid_cells==81U && original.v_valid_cells==81U,
       "complete original 81x64 I001 token matrix");
 CHECK(original.source_identity_verified==1U &&
       original.I001_normalization_token_profile_verified==1U &&
       original.s_all_81_tokens_canonical==1U &&
       original.v_all_81_tokens_canonical==1U &&
       original.deterministic_profile_replay_verified==1U,"true exact token profile");
 CHECK(original.s_vm5184_address==265U && original.v_vm5184_address==529U,
       "s/v typed addresses retained");
 for(i=0U;i<81U;++i) {
  CHECK(original.s_81_offset_digits[i]==(uint8_t)(i%9U),
        "s original 81 exact offsets");
  CHECK(original.v_81_offset_digits[i]==(uint8_t)((i+4U)%9U),
        "v original 81 exact offsets");
 }
 CHECK(!original.signed_predecessor_authenticated &&
       !original.authenticated_tensor_rank_proved &&
       !original.full_phase_action_proved &&
       !original.native_matrix_values_computed &&
       !original.equation_equality_proved &&
       !original.signed_vm81_admission_executed &&
       !original.hash72_commit_authority &&
       !original.hash216_commit_authority &&
       !original.canonical_vm81_mutation_authority,
       "I001 canonical token shape never implies signed rank/value authority");

 s_state[20]='8';
 CHECK(check(&s,&v,&changed),"new exact I001 offset candidate");
 CHECK(memcmp(changed.s_carrier_position_root_sha256,
              original.s_carrier_position_root_sha256,32U)!=0,
       "changed s cell content changes source-bound root");
 CHECK(memcmp(changed.v_carrier_position_root_sha256,
              original.v_carrier_position_root_sha256,32U)==0,
       "s change retains independent v profile root");
 encode_offset_profile(s_state,0U);
 v.cell81=9U;
 CHECK(check(&s,&v,&changed),"new exact v tensor address");
 CHECK(memcmp(changed.v_carrier_position_root_sha256,
              original.v_carrier_position_root_sha256,32U)!=0,
       "same tensor string at another address is not same object");
 v.cell81=8U;

 /* These strings pass old UTF-8 length checks but are NOT I001 tokens. */
 memset(s_state,'X',sizeof(s_state));
 memset(&invalid,0xA5,sizeof(invalid));
 CHECK(!check(&s,&v,&invalid),"shape-only X*5184 rejected");
 CHECK(witness_is_fully_zero(&invalid),"shape-only input publishes no partial offsets");
 CHECK(!invalid.I001_normalization_token_profile_verified &&
       !invalid.hash216_commit_authority,"invalid shape no authority");
 encode_offset_profile(s_state,0U);
 s_state[20]='9';
 CHECK(!check(&s,&v,&invalid),"offset >8 rejected");
 s_state[20]='0';
 s_state[21]='*';
 CHECK(!check(&s,&v,&invalid),"wrong rational separator rejected");
 s_state[21]='/';
 s_state[41]='0';
 CHECK(!check(&s,&v,&invalid),"zero denominator rejected");
 s_state[41]='1';
 s_state[42]='E';
 CHECK(!check(&s,&v,&invalid),"wrong scientific exponent marker rejected");
 s_state[42]='e';
 s_state[43]='-';
 CHECK(!check(&s,&v,&invalid),"negative exponent forbidden in I001 canonical");
 s_state[43]='+';
 s_state[63]='1';
 CHECK(!check(&s,&v,&invalid),"non-zero exponent forbidden in I001 profile");
 s_state[63]='0';
 s_state[0]='-';
 CHECK(!check(&s,&v,&invalid),"negative signed zero is not normalized I001");
 s_state[0]='+';
 s_state[2]='1';
 CHECK(!check(&s,&v,&invalid),"canonical numerator padding enforced");
 s_state[2]='0';
 v_state[64U*80U+41U]='0';
 memset(&invalid,0xA5,sizeof(invalid));
 CHECK(!check(&s,&v,&invalid),"last token denominator drift rejected");
 CHECK(witness_is_fully_zero(&invalid),"late v token failure cannot expose valid s or earlier v cells");
 v_state[64U*80U+41U]='1';
 s.state_bytes=5183U;
 CHECK(!check(&s,&v,&invalid),"truncated 5184 carrier denied");
 s.state_bytes=5184U;
 source[0]^=1U;
 memset(&invalid,0xA5,sizeof(invalid));
 CHECK(!check(&s,&v,&invalid),"modified equation source denied");
 CHECK(witness_is_fully_zero(&invalid),"downstream source gate failure cannot expose decoded tensor offsets");
 source[0]^=1U;
 v.predecessor_bytes=215U;
 memset(&invalid,0xA5,sizeof(invalid));
 CHECK(!check(&s,&v,&invalid),"invalid parent width denied");
 CHECK(witness_is_fully_zero(&invalid),"lineage rejection zeroizes staged output");
 v.predecessor_bytes=216U;
 CHECK(hhs_exact_pass220_ordered4x4_i001_carrier_validate(
   source,n,&s,&v,&parent,NULL)!=HHS_EXACT_STATUS_OK,
   "null proof output rejected");

 puts("{\"schema\":\"HHS_PASS220_4X4_I001_EXACT_CARRIER_PROFILE_V1\","
      "\"cells_per_state\":81,\"bytes_per_token\":64,"
      "\"strict_rational_tokens\":true,\"shape_only_payload_rejected\":true,"
      "\"position_aware\":true,\"deterministic_replay\":true,"
      "\"signed_parent_authenticated\":false,\"rank_proved\":false,"
      "\"matrix_values_computed\":false,\"equality_proved\":false,"
      "\"vm81_admitted\":false,\"canonical_receipts\":false}");
 return 0;
}
