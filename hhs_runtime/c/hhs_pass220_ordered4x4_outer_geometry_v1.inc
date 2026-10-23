/* Pass 220: read-only denominator and RHS ordered tensor-action geometry.
 * Uses the inherited source lock, 5184 tensor bindings and 216-index preflight.
 * Native source-cell incidences are NOT evaluated MatrixTimes result cells.
 */
#include "../include/hhs_pass220_ordered4x4_outer_geometry_v1.h"
#include <openssl/sha.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static int hhs220_outer_leaf(
 const uint8_t source_digest[32], uint8_t matrix_id,
 uint8_t row, uint8_t column, int8_t literal, uint8_t output[32]
) {
 static const char domain[]="HHS-P220-4X4-OUTER-MATRIX-SOURCE-LEAF-V1";
 uint8_t bytes[sizeof(domain)-1U+32U+4U];
 size_t offset=0U;
 memcpy(bytes+offset,domain,sizeof(domain)-1U);
 offset+=sizeof(domain)-1U;
 memcpy(bytes+offset,source_digest,32U);
 offset+=32U;
 bytes[offset++]=matrix_id;
 bytes[offset++]=row;
 bytes[offset++]=column;
 bytes[offset++]=(uint8_t)literal;
 return offset==sizeof(bytes) && SHA256(bytes,sizeof(bytes),output)!=NULL;
}

static int hhs220_outer_ordered_incidence(
 const uint8_t source_digest[32],
 uint8_t branch_id,uint8_t row,uint8_t column,
 uint8_t matrix_first,
 const uint8_t matrix_root[32],const uint8_t tensor_root[32],
 uint8_t output[32]
) {
 static const char domain[]="HHS-P220-4X4-OUTER-ORDERED-ACTION-INCIDENCE-V1";
 uint8_t bytes[sizeof(domain)-1U+32U+4U+64U];
 size_t offset=0U;
 memcpy(bytes+offset,domain,sizeof(domain)-1U);
 offset+=sizeof(domain)-1U;
 memcpy(bytes+offset,source_digest,32U);
 offset+=32U;
 bytes[offset++]=branch_id;
 bytes[offset++]=row;
 bytes[offset++]=column;
 bytes[offset++]=matrix_first;
 if(matrix_first!=0U) {
  memcpy(bytes+offset,matrix_root,32U);offset+=32U;
  memcpy(bytes+offset,tensor_root,32U);offset+=32U;
 } else {
  memcpy(bytes+offset,tensor_root,32U);offset+=32U;
  memcpy(bytes+offset,matrix_root,32U);offset+=32U;
 }
 return offset==sizeof(bytes) && SHA256(bytes,sizeof(bytes),output)!=NULL;
}

static int hhs220_outer_branch_root(
 const uint8_t source_digest[32],const uint8_t parent_digest[32],
 const uint8_t binding_root[32],uint8_t branch,
 const HHS220Ordered4x4OuterIncidenceV1 *edges,
 uint8_t output[32]
) {
 static const char domain[]="HHS-P220-4X4-OUTER-BRANCH-SOURCE-ORDER-V1";
 uint8_t bytes[sizeof(domain)-1U+32U+32U+32U+1U+16U*32U];
 size_t offset=0U,k;
 memcpy(bytes+offset,domain,sizeof(domain)-1U);
 offset+=sizeof(domain)-1U;
 memcpy(bytes+offset,source_digest,32U);offset+=32U;
 memcpy(bytes+offset,parent_digest,32U);offset+=32U;
 memcpy(bytes+offset,binding_root,32U);offset+=32U;
 bytes[offset++]=branch;
 for(k=0U;k<16U;++k) {
  if(edges[k].branch_id!=branch ||
     edges[k].row!=k/4U || edges[k].column!=k%4U)
   return 0;
  memcpy(bytes+offset,edges[k].ordered_incidence_root,32U);
  offset+=32U;
 }
 return offset==sizeof(bytes) && SHA256(bytes,sizeof(bytes),output)!=NULL;
}

static int hhs220_outer_total_root(
 const HHS220Ordered4x4OuterGeometryV1 *geometry,
 uint8_t output[32]
) {
 static const char domain[]="HHS-P220-4X4-OUTER-BOTH-ORDERED-ACTIONS-V1";
 uint8_t bytes[sizeof(domain)-1U+5U*32U];
 size_t offset=0U;
 memcpy(bytes+offset,domain,sizeof(domain)-1U);
 offset+=sizeof(domain)-1U;
 memcpy(bytes+offset,geometry->source_sha256,32U);offset+=32U;
 memcpy(bytes+offset,geometry->parent_reference_sha256,32U);offset+=32U;
 memcpy(bytes+offset,geometry->bound_graph_root_sha256,32U);offset+=32U;
 memcpy(bytes+offset,geometry->branch_roots_sha256[0],32U);offset+=32U;
 memcpy(bytes+offset,geometry->branch_roots_sha256[1],32U);offset+=32U;
 return offset==sizeof(bytes) && SHA256(bytes,sizeof(bytes),output)!=NULL;
}

HHSExactStatus hhs_exact_pass220_ordered4x4_outer_geometry(
 const uint8_t *source,size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent_reference,
 HHS220Ordered4x4OuterGeometryV1 *out_geometry
) {
 HHS220Ordered4x4ParentPreflightV1 parent_witness;
 HHS220Ordered4x4BoundExecutionV1 bound;
 HHSExactVM81Frame source_candidate;
 HHS220Ordered4x4HIRWitnessV1 source_witness;
 size_t branch,row,column,k;
 HHSExactStatus status;
 if(out_geometry==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out_geometry,0,sizeof(*out_geometry));
 out_geometry->struct_size=(uint32_t)sizeof(*out_geometry);
 out_geometry->version=UINT32_C(0x00010000);
 if(source==NULL || s==NULL || v==NULL || parent_reference==NULL)
  return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 status=hhs_exact_pass220_ordered4x4_parent_preflight(
    source,source_bytes,s,v,parent_reference,&parent_witness);
 if(status!=HHS_EXACT_STATUS_OK ||
    parent_witness.inherited_hash216_structure_verified!=1U ||
    parent_witness.all_216_indexes_verified!=1U ||
    parent_witness.s_parent_matches_verified_reference!=1U ||
    parent_witness.v_parent_matches_verified_reference!=1U ||
    parent_witness.bound_graph_executed!=1U ||
    parent_witness.deterministic_bound_graph_replay_verified!=1U ||
    parent_witness.parent_signed_authenticity_verified!=0U ||
    parent_witness.vm81_environment_signed_admission!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 status=hhs_exact_pass220_ordered4x4_execute_bound(
    source,source_bytes,s,v,&bound);
 if(status!=HHS_EXACT_STATUS_OK ||
    bound.source_identity_verified!=1U ||
    bound.ordered_type_graph_executed!=1U ||
    bound.deterministic_bound_graph_replay_verified!=1U ||
    memcmp(bound.result_root_sha256,
           parent_witness.bound_result_root_sha256,32U)!=0 ||
    bound.matrix_times_value_derived!=0U ||
    bound.matrix_quotient_value_derived!=0U ||
    bound.matrix_power_value_derived!=0U ||
    bound.equation_equality_proved!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 status=hhs_exact_pass220_ordered4x4_lower(
     source,source_bytes,&source_candidate,&source_witness);
 if(status!=HHS_EXACT_STATUS_OK ||
    source_witness.source_identity_verified!=1U ||
    source_witness.ordered_topology_verified!=1U ||
    source_witness.literal_cells!=64U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 memcpy(out_geometry->source_sha256,source_witness.source_sha256,32U);
 memcpy(out_geometry->parent_reference_sha256,
        parent_witness.parent_transition_identity_sha256,32U);
 memcpy(out_geometry->bound_graph_root_sha256,bound.result_root_sha256,32U);

 for(branch=0U;branch<2U;++branch) {
  const HHS220Ordered4x4NativeTensorBindingV1 *tensor=branch==0U?s:v;
  const uint8_t *binding_root=bound.binding_roots_sha256[branch];
  uint8_t matrix_id=branch==0U?2U:3U;
  uint8_t matrix_first=branch==0U?1U:0U;
  for(row=0U;row<4U;++row) {
   for(column=0U;column<4U;++column) {
    HHS220Ordered4x4OuterIncidenceV1 *edge;
    k=branch*16U+row*4U+column;
    edge=&out_geometry->incidences[k];
    edge->branch_id=(uint8_t)branch;
    edge->source_matrix_id=matrix_id;
    edge->row=(uint8_t)row;
    edge->column=(uint8_t)column;
    edge->source_literal_token=HHS220_ORDERED4X4_CELLS[matrix_id][row*4U+column];
    edge->source_matrix_is_left_operand=matrix_first;
    edge->tensor_symbol=tensor->symbol;
    edge->tensor_cell81=tensor->cell81;
    edge->tensor_operation64=tensor->operation64;
    edge->tensor_vm5184_address=(uint16_t)(
       (uint16_t)(tensor->cell81*64U)+(uint16_t)tensor->operation64);
    memcpy(edge->symbol_binding_root,binding_root,32U);
    if(!hhs220_outer_leaf(out_geometry->source_sha256,
          matrix_id,(uint8_t)row,(uint8_t)column,
          edge->source_literal_token,edge->matrix_leaf_root) ||
       !hhs220_outer_ordered_incidence(out_geometry->source_sha256,
          (uint8_t)branch,(uint8_t)row,(uint8_t)column,matrix_first,
          edge->matrix_leaf_root,binding_root,edge->ordered_incidence_root))
      return HHS_EXACT_STATUS_INVARIANT_FAILURE;
   }
  }
  if(!hhs220_outer_branch_root(out_geometry->source_sha256,
        out_geometry->parent_reference_sha256,binding_root,(uint8_t)branch,
        &out_geometry->incidences[branch*16U],
        out_geometry->branch_roots_sha256[branch]))
   return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 }
 if(!hhs220_outer_total_root(out_geometry,out_geometry->outer_geometry_root_sha256))
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 out_geometry->matrix_leaf_count=HHS220_ORDERED4X4_OUTER_INCIDENCES;
 out_geometry->ordered_incidence_count=HHS220_ORDERED4X4_OUTER_INCIDENCES;
 out_geometry->source_rows=4U;
 out_geometry->source_columns=4U;
 out_geometry->source_identity_verified=1U;
 out_geometry->inherited_hash216_index_preflight_verified=1U;
 out_geometry->typed_5184_bindings_verified=1U;
 out_geometry->ordered_operand_roles_verified=1U;
 out_geometry->complete_source_leaf_coverage_verified=1U;
 out_geometry->deterministic_outer_geometry_replay_verified=0U;
 /* No s/v rank is assumed. All value, equality, signed-auth and commit flags
  * deliberately remain false. */
 return HHS_EXACT_STATUS_OK;
}
