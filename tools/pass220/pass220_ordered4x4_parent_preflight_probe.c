/* Native read-only Hash216 index preflight: no signature/mutation authority. */
#include "hhs_runtime_exact_abi.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define REQUIRE(c,msg) do{if(!(c)){fprintf(stderr,"FAIL:%s\n",msg);return 1;}}while(0)
static uint8_t src[HHS220_ORDERED4X4_SOURCE_BYTES+1U];
static uint8_t s_state[5184U],v_state[5184U];
static HHSExactPass219Hash216TransitionViewV1 parent,tampered;
static HHS220Ordered4x4ParentPreflightV1 result,repeat,rejected;

static int call(
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *ref,
 HHS220Ordered4x4ParentPreflightV1 *out
) {
 return hhs_exact_pass220_ordered4x4_parent_preflight(
  src,HHS220_ORDERED4X4_SOURCE_BYTES,s,v,ref,out)==HHS_EXACT_STATUS_OK;
}

int main(void) {
 HHS220Ordered4x4NativeTensorBindingV1 s,v;
 FILE *f=fopen("contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode","rb");
 size_t n;
 REQUIRE(f!=NULL,"source open");
 n=fread(src,1U,sizeof(src),f);
 REQUIRE(!ferror(f) && fclose(f)==0 && n==HHS220_ORDERED4X4_SOURCE_BYTES,"source read");

 memset(s_state,'X',sizeof(s_state));memset(v_state,'Y',sizeof(v_state));
 REQUIRE(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent)==HHS_EXACT_STATUS_OK,"inherited genesis 216 reference");
 REQUIRE(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&parent)==HHS_EXACT_STATUS_OK,"native 216 index verification");
 memset(&s,0,sizeof(s));memset(&v,0,sizeof(v));
 s.struct_size=sizeof(s);s.symbol='s';s.cell81=5U;s.operation64=9U;
 s.state_utf8=s_state;s.state_bytes=5184U;
 s.predecessor_hash216=(const uint8_t *)parent.transition_identity216;s.predecessor_bytes=216U;
 v.struct_size=sizeof(v);v.symbol='v';v.cell81=8U;v.operation64=17U;
 v.state_utf8=v_state;v.state_bytes=5184U;
 v.predecessor_hash216=(const uint8_t *)parent.transition_identity216;v.predecessor_bytes=216U;
 REQUIRE(call(&s,&v,&parent,&result),"complete parent preflight");
 REQUIRE(call(&s,&v,&parent,&repeat),"deterministic parent replay");
 REQUIRE(memcmp(&result,&repeat,sizeof(result))==0,"parent preflight deterministic witness");
 REQUIRE(result.inherited_hash216_structure_verified==1U &&
         result.all_216_indexes_verified==1U,"all 216 inherited indices");
 REQUIRE(result.s_parent_matches_verified_reference==1U &&
         result.v_parent_matches_verified_reference==1U,"parent-bound s/v");
 REQUIRE(result.bound_graph_executed==1U &&
         result.deterministic_bound_graph_replay_verified==1U,"native typed operator program");
 REQUIRE(result.parent_signed_authenticity_verified==0U &&
         result.vm81_environment_signed_admission==0U &&
         result.tensor_equality_proved==0U,"no false signature, admission, equality");
 REQUIRE(result.hash72_commit_authority==0U &&
         result.hash216_commit_authority==0U &&
         result.canonical_vm81_mutation_authority==0U,"no canonical authority");

 tampered=parent;
 tampered.occurrences[0].glyph=(uint8_t)(
  tampered.occurrences[0].glyph=='0'?'1':'0');
 REQUIRE(!call(&s,&v,&tampered,&rejected),"altered token rejected");
 REQUIRE(!rejected.bound_graph_executed && !rejected.hash72_commit_authority,
         "no authority after token mismatch");
 tampered=parent;
 tampered.occurrences[215].sha256_index_record[0]^=1U;
 REQUIRE(!call(&s,&v,&tampered,&rejected),"altered tail SHA256 index rejected");
 tampered=parent;
 tampered.transition_identity216[72]^=1;
 REQUIRE(!call(&s,&v,&tampered,&rejected),"altered transition identity rejected");
 tampered=parent;
 tampered.resolved_index_count=215U;
 REQUIRE(!call(&s,&v,&tampered,&rejected),"incomplete index coverage rejected");

 v.predecessor_hash216=(const uint8_t *)parent.transition_word216;
 REQUIRE(!call(&s,&v,&parent,&rejected),"mismatched v parent rejected");
 v.predecessor_hash216=(const uint8_t *)parent.transition_identity216;
 v.predecessor_bytes=215U;
 REQUIRE(!call(&s,&v,&parent,&rejected),"truncated parent rejected");
 v.predecessor_bytes=216U;
 src[0]^=1U;
 REQUIRE(!call(&s,&v,&parent,&rejected),"source drift rejected");
 src[0]^=1U;
 REQUIRE(!rejected.bound_graph_executed &&
         !rejected.parent_signed_authenticity_verified &&
         !rejected.hash216_commit_authority,"no false authority on rejected result");
 puts("{\"schema\":\"HHS_PASS220_ORDERED4X4_INHERITED_HASH216_PARENT_PREFLIGHT_V1\","
      "\"all_216_indexes_verified\":true,\"s_v_predecessor_match\":true,"
      "\"bound_graph_deterministic\":true,\"negative_cases_rejected\":true,"
      "\"signed_parent_authenticated\":false,\"vm81_admitted\":false,"
      "\"equation_proved\":false,\"canonical_commit\":false}");
 return 0;
}
