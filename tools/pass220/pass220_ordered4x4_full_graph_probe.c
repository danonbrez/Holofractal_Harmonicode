/* Exact whole-expression ordered construction probe (no tensor value claims). */
#include "hhs_runtime_exact_abi.h"
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define REQUIRE(pred,msg) do { if (!(pred)) { fprintf(stderr,"FAIL:%s\n",msg); return 1; } } while (0)

static uint8_t source[HHS220_ORDERED4X4_SOURCE_BYTES+1U];
static uint8_t state_s[5184U],state_v[5184U];
static HHSExactPass219Hash216TransitionViewV1 parent,altered_parent;
static HHS220Ordered4x4FullGraphV1 original,replay,changed,rejected;

static HHSExactStatus evaluate(
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *reference,
 HHS220Ordered4x4FullGraphV1 *out
) {
 return hhs_exact_pass220_ordered4x4_full_graph(
   source,HHS220_ORDERED4X4_SOURCE_BYTES,s,v,reference,out);
}

static int flipped_order_is_distinct(
 const uint8_t source_root[32],const char *domain,
 const uint8_t canonical_root[32],const uint8_t right[32],
 const uint8_t left[32]
) {
 uint8_t bytes[256],root[32];
 size_t n=0U,domain_length=strlen(domain);
 if(domain_length>128U) return 0;
 memcpy(bytes+n,domain,domain_length);n+=domain_length;
 memcpy(bytes+n,source_root,32U);n+=32U;
 memcpy(bytes+n,right,32U);n+=32U;
 memcpy(bytes+n,left,32U);n+=32U;
 return SHA256(bytes,n,root)!=NULL && memcmp(root,canonical_root,32U)!=0;
}

int main(void) {
 HHS220Ordered4x4NativeTensorBindingV1 s,v;
 FILE *file=fopen("contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode","rb");
 size_t n;
 REQUIRE(file!=NULL,"verbatim source exists");
 n=fread(source,1U,sizeof(source),file);
 REQUIRE(!ferror(file) && fclose(file)==0 && n==HHS220_ORDERED4X4_SOURCE_BYTES,
         "verbatim source width");
 REQUIRE(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent)==HHS_EXACT_STATUS_OK,
         "inherited indexed Hash216 reference");
 memset(&s,0,sizeof(s));memset(&v,0,sizeof(v));
 memset(state_s,'X',sizeof(state_s));memset(state_v,'Y',sizeof(state_v));
 s.struct_size=(uint32_t)sizeof(s);s.symbol='s';s.cell81=4U;s.operation64=9U;
 s.state_utf8=state_s;s.state_bytes=sizeof(state_s);
 s.predecessor_hash216=(const uint8_t *)parent.transition_identity216;
 s.predecessor_bytes=216U;
 v.struct_size=(uint32_t)sizeof(v);v.symbol='v';v.cell81=8U;v.operation64=17U;
 v.state_utf8=state_v;v.state_bytes=sizeof(state_v);
 v.predecessor_hash216=(const uint8_t *)parent.transition_identity216;
 v.predecessor_bytes=216U;

 REQUIRE(evaluate(&s,&v,&parent,&original)==HHS_EXACT_STATUS_OK,"complete native graph");
 REQUIRE(evaluate(&s,&v,&parent,&replay)==HHS_EXACT_STATUS_OK,"complete graph repeat");
 REQUIRE(memcmp(&original,&replay,sizeof(original))==0,"deterministic full byte replay");
 REQUIRE(original.deterministic_full_graph_replay_verified==1U,"internal two-pass replay");
 REQUIRE(original.numerator_ordered_product_terms==64U &&
         original.numerator_ordered_sum_nodes==16U &&
         original.denominator_source_incidences==16U &&
         original.rhs_source_incidences==16U,"all source operation terms admitted");
 REQUIRE(original.source_verified==1U &&
         original.full_216_index_parent_reference_verified==1U &&
         original.typed_s_v_identity_verified==1U &&
         original.native_phase_address_verified==1U &&
         original.numerator_64_term_graph_executed==1U &&
         original.denominator_direction_verified==1U &&
         original.rhs_direction_verified==1U &&
         original.quotient_order_verified==1U &&
         original.negative_fourth_power_order_verified==1U &&
         original.equality_gate_source_order_verified==1U,
         "all ordered source construction steps present");
 REQUIRE(original.tensor_action_rank_proved==0U &&
         original.native_matrix_values_derived==0U &&
         original.native_quotient_value_derived==0U &&
         original.native_matrix_power_value_derived==0U &&
         original.equality_mathematically_proved==0U,"no unproved values or equality");
 REQUIRE(original.predecessor_pqc_signature_authenticated==0U &&
         original.signed_vm81_admission_executed==0U &&
         original.hash72_commit_authority==0U &&
         original.hash216_commit_authority==0U &&
         original.canonical_vm81_mutation_authority==0U,
         "no signed or mutation authority");

 REQUIRE(flipped_order_is_distinct(
    original.source_sha256,"HHS-P220-FULL-4X4-ORDERED-QUOTIENT-V1",
    original.quotient_root_sha256,
    original.denominator_root_sha256,original.numerator_root_sha256),
    "denominator/numerator reversal is different");
 REQUIRE(flipped_order_is_distinct(
    original.source_sha256,"HHS-P220-FULL-4X4-ORDERED-EQUALITY-GATE-V1",
    original.equality_gate_root_sha256,
    original.rhs_root_sha256,original.negative_fourth_power_root_sha256),
    "outer relation operand reversal is different");

 /* Modifying s changes only denominator-dependent path. */
 state_s[17]='S';
 REQUIRE(evaluate(&s,&v,&parent,&changed)==HHS_EXACT_STATUS_OK,"s-change complete graph");
 REQUIRE(memcmp(original.numerator_root_sha256,changed.numerator_root_sha256,32U)==0,
         "s does not modify numerator literal source");
 REQUIRE(memcmp(original.rhs_root_sha256,changed.rhs_root_sha256,32U)==0,
         "s cannot alter independent RHS");
 REQUIRE(memcmp(original.denominator_root_sha256,changed.denominator_root_sha256,32U)!=0,
         "s changes denominator path");
 REQUIRE(memcmp(original.quotient_root_sha256,changed.quotient_root_sha256,32U)!=0,
         "s changes typed quotient node");
 REQUIRE(memcmp(original.negative_fourth_power_root_sha256,
                changed.negative_fourth_power_root_sha256,32U)!=0,
         "s change propagates through negative-fourth-power constructor");
 REQUIRE(memcmp(original.equality_gate_root_sha256,
                changed.equality_gate_root_sha256,32U)!=0,
         "s change propagates to equality gate");
 state_s[17]='X';

 /* Modifying v changes RHS/equality but cannot modify quotient/power. */
 state_v[27]='V';
 REQUIRE(evaluate(&s,&v,&parent,&changed)==HHS_EXACT_STATUS_OK,"v-change complete graph");
 REQUIRE(memcmp(original.numerator_root_sha256,changed.numerator_root_sha256,32U)==0,
         "v does not modify numerator literal source");
 REQUIRE(memcmp(original.denominator_root_sha256,changed.denominator_root_sha256,32U)==0,
         "v cannot alter denominator");
 REQUIRE(memcmp(original.quotient_root_sha256,changed.quotient_root_sha256,32U)==0,
         "v cannot alter quotient");
 REQUIRE(memcmp(original.negative_fourth_power_root_sha256,
                changed.negative_fourth_power_root_sha256,32U)==0,
         "v cannot alter negative-fourth-power LHS");
 REQUIRE(memcmp(original.rhs_root_sha256,changed.rhs_root_sha256,32U)!=0,
         "v affects RHS only");
 REQUIRE(memcmp(original.equality_gate_root_sha256,
                changed.equality_gate_root_sha256,32U)!=0,
         "v change affects outer equality gate");
 state_v[27]='Y';

 s.cell81=5U;
 REQUIRE(evaluate(&s,&v,&parent,&changed)==HHS_EXACT_STATUS_OK,"new native s address");
 REQUIRE(memcmp(original.denominator_root_sha256,changed.denominator_root_sha256,32U)!=0,
         "tensor address identity changes denominator graph");
 s.cell81=4U;

 altered_parent=parent;
 altered_parent.occurrences[215].sha256_index_record[0]^=1U;
 REQUIRE(evaluate(&s,&v,&altered_parent,&rejected)!=HHS_EXACT_STATUS_OK,
         "corrupt final indexed ancestor rejected");
 REQUIRE(!rejected.equality_gate_source_order_verified &&
         !rejected.hash216_commit_authority,"rejected parent gives no authority");
 v.predecessor_bytes=215U;
 REQUIRE(evaluate(&s,&v,&parent,&rejected)!=HHS_EXACT_STATUS_OK,
         "wrong ancestor width rejected");
 v.predecessor_bytes=216U;
 source[0]^=1U;
 REQUIRE(evaluate(&s,&v,&parent,&rejected)!=HHS_EXACT_STATUS_OK,
         "changed original equation rejected");
 REQUIRE(!rejected.source_verified && !rejected.signed_vm81_admission_executed,
         "rejected source does not execute admission");
 source[0]^=1U;
 v.symbol='s';
 REQUIRE(evaluate(&s,&v,&parent,&rejected)!=HHS_EXACT_STATUS_OK,
         "swapped symbol role rejected");
 v.symbol='v';
 REQUIRE(hhs_exact_pass220_ordered4x4_full_graph(source,n,&s,&v,&parent,NULL)
         !=HHS_EXACT_STATUS_OK,"null out rejected");

 puts("{\"schema\":\"HHS_PASS220_ORDERED4X4_FULL_NATIVE_EXPRESSION_GRAPH_V1\","
      "\"numerator_terms\":64,\"numerator_ordered_sums\":16,"
      "\"denominator_source_incidences\":16,\"rhs_source_incidences\":16,"
      "\"source_bound_quotient_negative_fourth_power_and_equality\":true,"
      "\"strict_direction_and_dependency_tests\":true,"
      "\"internal_deterministic_replay\":true,\"native_matrix_values\":false,"
      "\"tensor_rank_proved\":false,\"equality_proved\":false,"
      "\"signed_predecessor_authenticated\":false,"
      "\"vm81_admission\":false,\"canonical_receipts\":false}");
 return 0;
}
