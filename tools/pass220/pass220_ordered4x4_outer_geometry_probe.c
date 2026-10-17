/* Native denominator/RHS geometry conformance: s/v stay opaque typed tensors.
 * Do not interpret 32 source incidences as computed MatrixTimes output values.
 */
#include "hhs_runtime_exact_abi.h"
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define CHECK(test,msg) do {if(!(test)){fprintf(stderr,"FAIL:%s\n",msg);return 1;}} while(0)

static uint8_t equation[HHS220_ORDERED4X4_SOURCE_BYTES+1U];
static uint8_t s_text[5184U];
static uint8_t v_text[5184U];
static HHSExactPass219Hash216TransitionViewV1 parent;
static HHS220Ordered4x4OuterGeometryV1 a,b,changed,failed;

static HHSExactStatus geometry(
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *reference,
 HHS220Ordered4x4OuterGeometryV1 *out
) {
 return hhs_exact_pass220_ordered4x4_outer_geometry(
  equation,HHS220_ORDERED4X4_SOURCE_BYTES,s,v,reference,out);
}

static int reversed_same_operands_diff(
 const HHS220Ordered4x4OuterIncidenceV1 *edge,
 const uint8_t source_sha[32]
) {
 static const char domain[]="HHS-P220-4X4-OUTER-ORDERED-ACTION-INCIDENCE-V1";
 uint8_t data[sizeof(domain)-1U+32U+4U+64U];
 uint8_t reverse_root[32];
 size_t cursor=0U;
 memcpy(data+cursor,domain,sizeof(domain)-1U);cursor+=sizeof(domain)-1U;
 memcpy(data+cursor,source_sha,32U);cursor+=32U;
 data[cursor++]=edge->branch_id;
 data[cursor++]=edge->row;
 data[cursor++]=edge->column;
 data[cursor++]=(uint8_t)(1U-edge->source_matrix_is_left_operand);
 if(edge->source_matrix_is_left_operand) {
  memcpy(data+cursor,edge->symbol_binding_root,32U);cursor+=32U;
  memcpy(data+cursor,edge->matrix_leaf_root,32U);cursor+=32U;
 } else {
  memcpy(data+cursor,edge->matrix_leaf_root,32U);cursor+=32U;
  memcpy(data+cursor,edge->symbol_binding_root,32U);cursor+=32U;
 }
 return cursor==sizeof(data) &&
        SHA256(data,cursor,reverse_root)!=NULL &&
        memcmp(reverse_root,edge->ordered_incidence_root,32U)!=0;
}

int main(void) {
 HHS220Ordered4x4NativeTensorBindingV1 s,v;
 HHSExactPass219Hash216TransitionViewV1 forged;
 FILE *file=fopen("contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode","rb");
 size_t len,branch,r,c,i;
 CHECK(file!=NULL,"source file");
 len=fread(equation,1U,sizeof(equation),file);
 CHECK(!ferror(file) && fclose(file)==0 && len==HHS220_ORDERED4X4_SOURCE_BYTES,
       "exact equation source");
 CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent)==HHS_EXACT_STATUS_OK,
       "inherited source-bound Hash216 reference");
 memset(s_text,'X',sizeof(s_text));memset(v_text,'Y',sizeof(v_text));
 memset(&s,0,sizeof(s));memset(&v,0,sizeof(v));
 s.struct_size=sizeof(s);s.symbol='s';s.cell81=4U;s.operation64=9U;
 s.state_utf8=s_text;s.state_bytes=sizeof(s_text);
 s.predecessor_hash216=(const uint8_t*)parent.transition_identity216;
 s.predecessor_bytes=216U;
 v.struct_size=sizeof(v);v.symbol='v';v.cell81=8U;v.operation64=17U;
 v.state_utf8=v_text;v.state_bytes=sizeof(v_text);
 v.predecessor_hash216=(const uint8_t*)parent.transition_identity216;
 v.predecessor_bytes=216U;
 CHECK(geometry(&s,&v,&parent,&a)==HHS_EXACT_STATUS_OK,"ordered outer tensor actions");
 CHECK(geometry(&s,&v,&parent,&b)==HHS_EXACT_STATUS_OK,"repeat outer geometry");
 CHECK(memcmp(&a,&b,sizeof(a))==0,"deterministic full source incidence replay");
 CHECK(a.source_rows==4U && a.source_columns==4U,"source matrices 4x4");
 CHECK(a.matrix_leaf_count==32U && a.ordered_incidence_count==32U,
       "32 full 4x4 source-cell incidences");
 CHECK(a.source_identity_verified==1U &&
       a.inherited_hash216_index_preflight_verified==1U &&
       a.typed_5184_bindings_verified==1U &&
       a.ordered_operand_roles_verified==1U &&
       a.complete_source_leaf_coverage_verified==1U,
       "verified source and directional typed action structure");
 CHECK(a.s_tensor_action_shape_resolved==0U &&
       a.v_tensor_action_shape_resolved==0U,
       "unknown native tensor rank remains unresolved");
 CHECK(a.denominator_value_derived==0U && a.rhs_value_derived==0U &&
       a.quotient_value_derived==0U &&
       a.matrix_power_value_derived==0U && a.equation_equality_proved==0U,
       "never claim evaluated matrix values or proof");
 CHECK(a.parent_signed_authenticity_verified==0U &&
       a.vm81_signed_admission_executed==0U &&
       a.hash72_commit_authority==0U &&
       a.hash216_commit_authority==0U &&
       a.canonical_vm81_mutation_authority==0U,
       "no signed/commit authority");
 for(branch=0U;branch<2U;++branch) {
  const uint8_t expected_source=branch==0U?2U:3U;
  const uint8_t expected_symbol=branch==0U?'s':'v';
  const uint8_t expected_left=branch==0U?1U:0U;
  const uint16_t expected_address=branch==0U?265U:529U;
  for(r=0U;r<4U;++r) for(c=0U;c<4U;++c) {
   const HHS220Ordered4x4OuterIncidenceV1 *e;
   i=16U*branch+4U*r+c;
   e=&a.incidences[i];
   CHECK(e->branch_id==branch && e->source_matrix_id==expected_source &&
         e->row==r && e->column==c,"full ordered incidence address");
   CHECK(e->source_matrix_is_left_operand==expected_left &&
         e->tensor_symbol==expected_symbol &&
         e->tensor_vm5184_address==expected_address,
         "direction and VM81 tensor address");
   CHECK(memcmp(e->matrix_leaf_root,e->symbol_binding_root,32U)!=0,
         "matrix source leaf and whole tensor are different types");
   CHECK(memcmp(e->ordered_incidence_root,e->symbol_binding_root,32U)!=0,
         "operator incidence distinct from bound symbol");
   CHECK(reversed_same_operands_diff(e,a.source_sha256),
         "same operands in reversed order are non-equivalent without native proof");
  }
 }
 CHECK(a.incidences[0].source_literal_token==2 &&
       a.incidences[15].source_literal_token==2,
       "denominator 2/4 original source literals");
 CHECK(a.incidences[16].source_literal_token==0 &&
       a.incidences[31].source_literal_token==0,
       "right closure L lower triangle literals");
 CHECK(memcmp(a.branch_roots_sha256[0],a.branch_roots_sha256[1],32U)!=0,
       "noncommutative action directions have different roots");

 /* s changes only the denominator incidences; right branch remains identical. */
 s_text[17]='S';
 CHECK(geometry(&s,&v,&parent,&changed)==HHS_EXACT_STATUS_OK,"changed s candidate");
 CHECK(memcmp(a.branch_roots_sha256[0],changed.branch_roots_sha256[0],32U)!=0,
       "s affects MatrixTimes(D,s)");
 CHECK(memcmp(a.branch_roots_sha256[1],changed.branch_roots_sha256[1],32U)==0,
       "s cannot alter MatrixTimes(v,L)");
 s_text[17]='X';

 /* v changes only the right-side incidences; denominator stays identical. */
 v_text[22]='V';
 CHECK(geometry(&s,&v,&parent,&changed)==HHS_EXACT_STATUS_OK,"changed v candidate");
 CHECK(memcmp(a.branch_roots_sha256[0],changed.branch_roots_sha256[0],32U)==0,
       "v cannot alter MatrixTimes(D,s)");
 CHECK(memcmp(a.branch_roots_sha256[1],changed.branch_roots_sha256[1],32U)!=0,
       "v affects MatrixTimes(v,L)");
 v_text[22]='Y';

 /* Address changes are semantic even if full 5184-character state matches. */
 s.cell81=5U;
 CHECK(geometry(&s,&v,&parent,&changed)==HHS_EXACT_STATUS_OK,"new VM81 s address");
 CHECK(memcmp(a.branch_roots_sha256[0],changed.branch_roots_sha256[0],32U)!=0,
       "VM81 address changes denominator identity");
 s.cell81=4U;

 /* Fail-closed source tamper, malformed parent and malformed roles. */
 equation[0]^=1U;
 CHECK(geometry(&s,&v,&parent,&failed)!=HHS_EXACT_STATUS_OK,
       "source drift rejected");
 CHECK(failed.source_identity_verified==0U &&
       failed.vm81_signed_admission_executed==0U &&
       failed.hash216_commit_authority==0U,"fail-closed authority");
 equation[0]^=1U;
 forged=parent;
 forged.occurrences[215].sha256_index_record[0]^=1U;
 CHECK(geometry(&s,&v,&forged,&failed)!=HHS_EXACT_STATUS_OK,
       "bad last Hash216 token index rejected");
 v.symbol='s';
 CHECK(geometry(&s,&v,&parent,&failed)!=HHS_EXACT_STATUS_OK,"swapped tensor role rejected");
 v.symbol='v';
 v.state_bytes=5183U;
 CHECK(geometry(&s,&v,&parent,&failed)!=HHS_EXACT_STATUS_OK,"truncated native state rejected");
 v.state_bytes=5184U;
 CHECK(hhs_exact_pass220_ordered4x4_outer_geometry(equation,len,&s,&v,
       &parent,NULL)!=HHS_EXACT_STATUS_OK,"null destination rejected");
 puts("{\"schema\":\"HHS_PASS220_ORDERED4X4_DENOMINATOR_RHS_GEOMETRY_V1\","
      "\"source_incidences\":32,\"ordered_branches\":2,"
      "\"direction_and_address_retained\":true,"
      "\"typed_symbol_shapes_resolved\":false,"
      "\"deterministic_rebuild\":true,\"negative_cases_rejected\":true,"
      "\"matrix_values_computed\":false,\"equality_proved\":false,"
      "\"signed_VM81_admission\":false,\"canonical_receipts\":false}");
 return 0;
}
