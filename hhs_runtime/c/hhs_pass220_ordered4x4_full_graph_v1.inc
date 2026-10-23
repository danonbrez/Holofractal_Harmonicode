/* Whole exact ordered 4x4 operation DAG: construction only, NO matrix values.
 * Each stage references inherited native source/phase/index address witnesses.
 */
#include "../include/hhs_pass220_ordered4x4_full_graph_v1.h"
#include <openssl/sha.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static int hhs220_full_binary_root(
 const char *domain,
 const uint8_t source_root[32],
 const uint8_t left_root[32], const uint8_t right_root[32],
 uint8_t output[32]
) {
 uint8_t material[256];
 size_t domain_len,cursor=0U;
 if(domain==NULL || source_root==NULL || left_root==NULL ||
    right_root==NULL || output==NULL) return 0;
 domain_len=strlen(domain);
 if(domain_len>128U) return 0;
 memcpy(material+cursor,domain,domain_len);cursor+=domain_len;
 memcpy(material+cursor,source_root,32U);cursor+=32U;
 memcpy(material+cursor,left_root,32U);cursor+=32U;
 memcpy(material+cursor,right_root,32U);cursor+=32U;
 return SHA256(material,cursor,output)!=NULL;
}

static int hhs220_full_power_root(
 const uint8_t source_root[32], const uint8_t quotient_root[32],
 uint8_t output[32]
) {
 static const char domain[]="HHS-P220-FULL-4X4-NCALC-MATRIX-POWER-V1";
 static const uint8_t token[]={'(','-','4',')'};
 uint8_t material[sizeof(domain)-1U+32U+32U+sizeof(token)];
 size_t cursor=0U;
 memcpy(material+cursor,domain,sizeof(domain)-1U);
 cursor+=sizeof(domain)-1U;
 memcpy(material+cursor,source_root,32U);cursor+=32U;
 memcpy(material+cursor,quotient_root,32U);cursor+=32U;
 memcpy(material+cursor,token,sizeof(token));cursor+=sizeof(token);
 return cursor==sizeof(material) && SHA256(material,sizeof(material),output)!=NULL;
}

static int hhs220_full_root(
 const HHS220Ordered4x4FullGraphV1 *graph,uint8_t output[32]
) {
 static const char domain[]="HHS-P220-FULL-4X4-ORDERED-NATIVE-GRAPH-V1";
 const uint8_t *fragments[10];
 uint8_t material[sizeof(domain)-1U+10U*32U];
 size_t index,cursor=0U;
 fragments[0]=graph->source_sha256;
 fragments[1]=graph->parent_reference_sha256;
 fragments[2]=graph->numerator_root_sha256;
 fragments[3]=graph->denominator_root_sha256;
 fragments[4]=graph->rhs_root_sha256;
 fragments[5]=graph->phase_root_sha256;
 fragments[6]=graph->quotient_root_sha256;
 fragments[7]=graph->negative_fourth_power_root_sha256;
 fragments[8]=graph->equality_gate_root_sha256;
 fragments[9]=graph->inherited_bound_symbolic_root_sha256;
 memcpy(material+cursor,domain,sizeof(domain)-1U);
 cursor+=sizeof(domain)-1U;
 for(index=0U;index<10U;++index) {
  memcpy(material+cursor,fragments[index],32U);
  cursor+=32U;
 }
 return cursor==sizeof(material) && SHA256(material,sizeof(material),output)!=NULL;
}

static HHSExactStatus hhs220_full_graph_once(
 const uint8_t *source,size_t source_size,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220Ordered4x4FullGraphV1 *out
) {
 static const char quotient_domain[]="HHS-P220-FULL-4X4-ORDERED-QUOTIENT-V1";
 static const char equality_domain[]="HHS-P220-FULL-4X4-ORDERED-EQUALITY-GATE-V1";
 HHS220Ordered4x4NumeratorTermsV1 numerator;
 HHS220Ordered4x4OuterGeometryV1 outer;
 HHS220Ordered4x4PhaseAddressGateV1 phase;
 HHS220Ordered4x4BoundExecutionV1 bound;
 HHSExactStatus status;
 memset(out,0,sizeof(*out));
 out->struct_size=(uint32_t)sizeof(*out);
 out->version=UINT32_C(0x00010000);

 status=hhs_exact_pass220_ordered4x4_numerator_terms(source,source_size,&numerator);
 if(status!=HHS_EXACT_STATUS_OK ||
    numerator.original_source_verified!=1U ||
    numerator.ordered_left_right_preserved!=1U ||
    numerator.ordered_reduction_k_preserved!=1U ||
    numerator.source_leaf_address_verified!=1U ||
    numerator.term_count!=64U || numerator.ordered_sum_count!=16U ||
    numerator.matrix_operator_value_derived!=0U ||
    numerator.canonical_hash72_commit_authority!=0U ||
    numerator.canonical_hash216_commit_authority!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 status=hhs_exact_pass220_ordered4x4_outer_geometry(
   source,source_size,s,v,parent,&outer);
 if(status!=HHS_EXACT_STATUS_OK ||
    outer.source_identity_verified!=1U ||
    outer.inherited_hash216_index_preflight_verified!=1U ||
    outer.typed_5184_bindings_verified!=1U ||
    outer.ordered_operand_roles_verified!=1U ||
    outer.ordered_incidence_count!=32U ||
    outer.source_rows!=4U || outer.source_columns!=4U ||
    outer.incidences[0].source_matrix_is_left_operand!=1U ||
    outer.incidences[16].source_matrix_is_left_operand!=0U ||
    outer.denominator_value_derived!=0U ||
    outer.rhs_value_derived!=0U ||
    outer.equation_equality_proved!=0U ||
    outer.hash216_commit_authority!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 status=hhs_exact_pass220_ordered4x4_phase_address_gate(
    source,source_size,s,v,parent,&phase);
 if(status!=HHS_EXACT_STATUS_OK ||
    phase.verbatim_source_verified!=1U ||
    phase.inherited_parent_index_verified!=1U ||
    phase.ordered_outer_geometry_verified!=1U ||
    phase.both_phase_address_roundtrips_verified!=1U ||
    phase.both_native_phase_products_verified!=1U ||
    phase.tensor_action_rank_resolved!=0U ||
    phase.tensor_phase_state_fully_verified!=0U ||
    phase.signed_vm81_admitted!=0U ||
    phase.hash72_commit_authority!=0U ||
    phase.hash216_commit_authority!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 status=hhs_exact_pass220_ordered4x4_execute_bound(
    source,source_size,s,v,&bound);
 if(status!=HHS_EXACT_STATUS_OK ||
    bound.source_identity_verified!=1U ||
    bound.ordered_type_graph_executed!=1U ||
    bound.deterministic_bound_graph_replay_verified!=1U ||
    bound.equation_equality_proved!=0U ||
    bound.hash72_commit_authority!=0U ||
    bound.hash216_commit_authority!=0U ||
    memcmp(bound.result_root_sha256,outer.bound_graph_root_sha256,32U)!=0 ||
    memcmp(numerator.source_sha256,outer.source_sha256,32U)!=0 ||
    memcmp(numerator.source_sha256,phase.source_sha256,32U)!=0 ||
    memcmp(outer.parent_reference_sha256,phase.parent_reference_sha256,32U)!=0 ||
    memcmp(bound.binding_roots_sha256[0],
           phase.bindings[0].source_bound_symbol_root,32U)!=0 ||
    memcmp(bound.binding_roots_sha256[1],
           phase.bindings[1].source_bound_symbol_root,32U)!=0 ||
    memcmp(outer.incidences[0].symbol_binding_root,
           bound.binding_roots_sha256[0],32U)!=0 ||
    memcmp(outer.incidences[16].symbol_binding_root,
           bound.binding_roots_sha256[1],32U)!=0)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 memcpy(out->source_sha256,numerator.source_sha256,32U);
 memcpy(out->parent_reference_sha256,outer.parent_reference_sha256,32U);
 memcpy(out->numerator_root_sha256,numerator.numerator_expression_root,32U);
 memcpy(out->denominator_root_sha256,outer.branch_roots_sha256[0],32U);
 memcpy(out->rhs_root_sha256,outer.branch_roots_sha256[1],32U);
 memcpy(out->phase_root_sha256,phase.phase_geometry_root_sha256,32U);
 memcpy(out->inherited_bound_symbolic_root_sha256,bound.result_root_sha256,32U);

 if(!hhs220_full_binary_root(quotient_domain,out->source_sha256,
       out->numerator_root_sha256,out->denominator_root_sha256,
       out->quotient_root_sha256) ||
    !hhs220_full_power_root(out->source_sha256,
       out->quotient_root_sha256,out->negative_fourth_power_root_sha256) ||
    !hhs220_full_binary_root(equality_domain,out->source_sha256,
       out->negative_fourth_power_root_sha256,out->rhs_root_sha256,
       out->equality_gate_root_sha256) ||
    !hhs220_full_root(out,out->full_graph_root_sha256))
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 out->numerator_ordered_product_terms=64U;
 out->numerator_ordered_sum_nodes=16U;
 out->denominator_source_incidences=16U;
 out->rhs_source_incidences=16U;
 out->source_verified=1U;
 out->full_216_index_parent_reference_verified=1U;
 out->typed_s_v_identity_verified=1U;
 out->native_phase_address_verified=1U;
 out->numerator_64_term_graph_executed=1U;
 out->denominator_direction_verified=1U;
 out->rhs_direction_verified=1U;
 out->quotient_order_verified=1U;
 out->negative_fourth_power_order_verified=1U;
 out->equality_gate_source_order_verified=1U;
 /* No tensor value, mathematical equality or canonical mutation authority. */
 return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass220_ordered4x4_full_graph(
 const uint8_t *source,size_t source_size,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220Ordered4x4FullGraphV1 *out_graph
) {
 HHS220Ordered4x4FullGraphV1 replay;
 HHSExactStatus status;
 if(out_graph==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out_graph,0,sizeof(*out_graph));
 out_graph->struct_size=(uint32_t)sizeof(*out_graph);
 out_graph->version=UINT32_C(0x00010000);
 if(source==NULL || s==NULL || v==NULL || parent==NULL)
  return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 status=hhs220_full_graph_once(source,source_size,s,v,parent,out_graph);
 if(status!=HHS_EXACT_STATUS_OK) {
  memset(out_graph,0,sizeof(*out_graph));
  out_graph->struct_size=(uint32_t)sizeof(*out_graph);
  out_graph->version=UINT32_C(0x00010000);
  return status;
 }
 status=hhs220_full_graph_once(source,source_size,s,v,parent,&replay);
 if(status!=HHS_EXACT_STATUS_OK ||
    memcmp(out_graph,&replay,sizeof(replay))!=0) {
  memset(out_graph,0,sizeof(*out_graph));
  out_graph->struct_size=(uint32_t)sizeof(*out_graph);
  out_graph->version=UINT32_C(0x00010000);
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 }
 out_graph->deterministic_full_graph_replay_verified=1U;
 return HHS_EXACT_STATUS_OK;
}
