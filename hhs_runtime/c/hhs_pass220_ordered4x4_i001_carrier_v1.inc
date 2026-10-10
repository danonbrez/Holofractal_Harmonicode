/* Read-only strict Pass220 I001 exact carrier profile boundary.
 * Mirrors hhs_pass220_lo_shu_normalization_v1.serialize_offsets_5184.
 * No broad generic HARMONICODE parsing claim or VM81 mutation authority.
 */
#include "../include/hhs_pass220_ordered4x4_i001_carrier_v1.h"
#include <openssl/sha.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static int hhs220_i001_offsets(
 const HHS220Ordered4x4NativeTensorBindingV1 *binding,
 uint8_t offsets[HHS220_4X4_I001_CELLS]
) {
 size_t cell,i;
 if(binding==NULL || offsets==NULL || binding->state_utf8==NULL ||
    binding->state_bytes!=HHS220_4X4_I001_TOTAL_BYTES)
  return 0;
 for(cell=0U;cell<HHS220_4X4_I001_CELLS;++cell) {
  const uint8_t *t=binding->state_utf8+
      cell*HHS220_4X4_I001_TOKEN_BYTES;
  if(t[0]!='+' || t[21]!='/' || t[42]!='e' || t[43]!='+')
   return 0;
  for(i=1U;i<20U;++i) if(t[i]!='0') return 0;
  if(t[20]<'0' || t[20]>'8') return 0;
  for(i=22U;i<41U;++i) if(t[i]!='0') return 0;
  if(t[41]!='1') return 0;
  for(i=44U;i<64U;++i) if(t[i]!='0') return 0;
  offsets[cell]=(uint8_t)(t[20]-'0');
 }
 return 1;
}

static int hhs220_i001_root(
 const uint8_t source[32],const uint8_t parent[32],
 const uint8_t binding_root[32],const uint8_t *symbol,
 uint16_t address,const uint8_t offsets[81],uint8_t out[32]
) {
 static const char DOMAIN[]="HHS-P220-I001-NORMALIZED81-ADDRESS-PRESERVING-CARRIER-V1";
 uint8_t data[sizeof(DOMAIN)-1U+32U*3U+1U+2U+81U];
 size_t cursor=0U;
 memcpy(data+cursor,DOMAIN,sizeof(DOMAIN)-1U);
 cursor+=sizeof(DOMAIN)-1U;
 memcpy(data+cursor,source,32U);cursor+=32U;
 memcpy(data+cursor,parent,32U);cursor+=32U;
 memcpy(data+cursor,binding_root,32U);cursor+=32U;
 data[cursor++]=*symbol;
 data[cursor++]=(uint8_t)(address>>8U);
 data[cursor++]=(uint8_t)address;
 memcpy(data+cursor,offsets,81U);cursor+=81U;
 return cursor==sizeof(data) && SHA256(data,sizeof(data),out)!=NULL;
}

static int hhs220_i001_combined_root(
 const HHS220Ordered4x4I001CarrierV1 *item,
 uint8_t out[32]
) {
 static const char DOMAIN[]="HHS-P220-I001-ORDERED-S-V-CARRIER-SET-V1";
 uint8_t data[sizeof(DOMAIN)-1U+32U*5U];
 size_t cursor=0U;
 memcpy(data+cursor,DOMAIN,sizeof(DOMAIN)-1U);
 cursor+=sizeof(DOMAIN)-1U;
 memcpy(data+cursor,item->source_sha256,32U);cursor+=32U;
 memcpy(data+cursor,item->parent_reference_sha256,32U);cursor+=32U;
 memcpy(data+cursor,item->bound_graph_root_sha256,32U);cursor+=32U;
 memcpy(data+cursor,item->s_carrier_position_root_sha256,32U);cursor+=32U;
 memcpy(data+cursor,item->v_carrier_position_root_sha256,32U);cursor+=32U;
 return cursor==sizeof(data) && SHA256(data,sizeof(data),out)!=NULL;
}

static HHSExactStatus hhs220_i001_carrier_stage_validate(
 const uint8_t *source,size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220Ordered4x4I001CarrierV1 *out
) {
 HHS220Ordered4x4ReadinessV1 readiness;
 HHS220Ordered4x4BoundExecutionV1 bound;
 uint8_t replay_s[81],replay_v[81],replay_root[32];
 HHSExactStatus status;
 if(out==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out,0,sizeof(*out));
 out->struct_size=(uint32_t)sizeof(*out);
 out->version=HHS220_4X4_I001_PROFILE_VERSION;
 if(source==NULL || s==NULL || v==NULL || parent==NULL)
  return HHS_EXACT_STATUS_INVALID_ARGUMENT;

 /* Decode exactly the inherited I001 profile, never accept mere 5184 chars. */
 if(!hhs220_i001_offsets(s,out->s_81_offset_digits) ||
    !hhs220_i001_offsets(v,out->v_81_offset_digits))
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 status=hhs_exact_pass220_ordered4x4_readiness(
   source,source_bytes,s,v,parent,&readiness);
 if(status!=HHS_EXACT_STATUS_OK ||
    readiness.decision!=HHS220_4X4_READINESS_BLOCKED ||
    readiness.preflight_verified_mask!=HHS220_4X4_PREFLIGHT_ALL ||
    readiness.missing_authority_mask!=HHS220_4X4_BLOCK_ALL ||
    readiness.signed_vm81_admission_executed!=0U ||
    readiness.hash216_commit_authority!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 status=hhs_exact_pass220_ordered4x4_execute_bound(
   source,source_bytes,s,v,&bound);
 if(status!=HHS_EXACT_STATUS_OK ||
    bound.source_identity_verified!=1U ||
    bound.typed_bindings_shape_verified!=1U ||
    bound.ordered_type_graph_executed!=1U ||
    bound.vm81_admission_executed!=0U ||
    bound.hash216_commit_authority!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 out->s_vm5184_address=bound.s_vm5184_address;
 out->v_vm5184_address=bound.v_vm5184_address;
 memcpy(out->source_sha256,readiness.source_sha256,32U);
 memcpy(out->parent_reference_sha256,readiness.parent_reference_sha256,32U);
 memcpy(out->bound_graph_root_sha256,readiness.full_graph_sha256,32U);
 if(!hhs220_i001_root(out->source_sha256,out->parent_reference_sha256,
       bound.binding_roots_sha256[0],(const uint8_t *)"s",
       out->s_vm5184_address,out->s_81_offset_digits,
       out->s_carrier_position_root_sha256) ||
    !hhs220_i001_root(out->source_sha256,out->parent_reference_sha256,
       bound.binding_roots_sha256[1],(const uint8_t *)"v",
       out->v_vm5184_address,out->v_81_offset_digits,
       out->v_carrier_position_root_sha256) ||
    !hhs220_i001_combined_root(out,out->carrier_profile_root_sha256))
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 if(!hhs220_i001_offsets(s,replay_s) ||
    !hhs220_i001_offsets(v,replay_v) ||
    memcmp(replay_s,out->s_81_offset_digits,81U)!=0 ||
    memcmp(replay_v,out->v_81_offset_digits,81U)!=0 ||
    !hhs220_i001_combined_root(out,replay_root) ||
    memcmp(replay_root,out->carrier_profile_root_sha256,32U)!=0)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 out->profile_cells=HHS220_4X4_I001_CELLS;
 out->profile_token_bytes=HHS220_4X4_I001_TOKEN_BYTES;
 out->s_valid_cells=HHS220_4X4_I001_CELLS;
 out->v_valid_cells=HHS220_4X4_I001_CELLS;
 out->source_identity_verified=1U;
 out->inherited_hash216_structure_verified=1U;
 out->I001_normalization_token_profile_verified=1U;
 out->s_all_81_tokens_canonical=1U;
 out->v_all_81_tokens_canonical=1U;
 out->original_vm81_addresses_preserved=1U;
 out->original_noncommutative_graph_preserved=1U;
 out->deterministic_profile_replay_verified=1U;
 /* Rank, phase-action values, equation closure, signed VM81 authority false. */
 return HHS_EXACT_STATUS_OK;
}


/* All-or-nothing output publication:
 * - caller-controlled partial results are never accepted as inputs;
 * - even if token 0..80 decode and downstream auth checks fail, staged
 *   private offsets/roots never reach the caller;
 * - all return paths leave the output fully zero on failure;
 * - original s/v ingress buffers and VM81 canonical state are read-only.
 * This wrapper is an isolation gate, NOT an HHS signed admission.
 */
HHSExactStatus hhs_exact_pass220_ordered4x4_i001_carrier_validate(
 const uint8_t *source,size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220Ordered4x4I001CarrierV1 *out
) {
 HHS220Ordered4x4I001CarrierV1 staged;
 HHSExactStatus status;
 if(out==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out,0,sizeof(*out));
 if(source==NULL || s==NULL || v==NULL || parent==NULL)
  return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(&staged,0,sizeof(staged));
 status=hhs220_i001_carrier_stage_validate(
    source,source_bytes,s,v,parent,&staged);
 if(status!=HHS_EXACT_STATUS_OK) {
  /* The stage may already have decoded early cells. Do not expose them. */
  memset(&staged,0,sizeof(staged));
  return status;
 }
 if(staged.profile_cells!=HHS220_4X4_I001_CELLS ||
    staged.profile_token_bytes!=HHS220_4X4_I001_TOKEN_BYTES ||
    staged.s_valid_cells!=HHS220_4X4_I001_CELLS ||
    staged.v_valid_cells!=HHS220_4X4_I001_CELLS ||
    staged.I001_normalization_token_profile_verified!=1U ||
    staged.s_all_81_tokens_canonical!=1U ||
    staged.v_all_81_tokens_canonical!=1U ||
    staged.original_vm81_addresses_preserved!=1U ||
    staged.original_noncommutative_graph_preserved!=1U ||
    staged.deterministic_profile_replay_verified!=1U ||
    staged.signed_predecessor_authenticated!=0U ||
    staged.authenticated_tensor_rank_proved!=0U ||
    staged.full_phase_action_proved!=0U ||
    staged.native_matrix_values_computed!=0U ||
    staged.equation_equality_proved!=0U ||
    staged.signed_vm81_admission_executed!=0U ||
    staged.hash72_commit_authority!=0U ||
    staged.hash216_commit_authority!=0U ||
    staged.canonical_vm81_mutation_authority!=0U) {
  memset(&staged,0,sizeof(staged));
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 }
 memcpy(out,&staged,sizeof(staged));
 memset(&staged,0,sizeof(staged));
 return HHS_EXACT_STATUS_OK;
}
