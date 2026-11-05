/* Pass 220: join exact positional carrier to source-locked rank requests. */
#include "../include/hhs_pass220_ordered4x4_rank_i001_handoff_v1.h"
#include <openssl/sha.h>
#include <stdint.h>
#include <string.h>
static int hhs220_rank_i001_overlap(const void *a,size_t n,const void *b,size_t m){
 uintptr_t x,y;
 if(!a||!b||!n||!m)return 0;
 x=(uintptr_t)a;y=(uintptr_t)b;
 if(n>UINTPTR_MAX-x||m>UINTPTR_MAX-y)return 1;
 return x<y+m&&y<x+n;
}
static int hhs220_rank_i001_digest(const HHS220RankI001HandoffV1 *w,uint8_t out[32]){
 static const char d[]="HHS-P220-I001-RANK-ACTION-S-V-HANDOFF-UNSIGNED-V1";
 uint8_t data[sizeof(d)-1U+11U*32U+162U+10U];
 size_t j=0U,i;
 const uint8_t *roots[5]={w->source_sha256,w->parent_sha256,
   w->full_graph_sha256,w->carrier_sha256,w->challenge_set_sha256};
 memcpy(data+j,d,sizeof(d)-1U);j+=sizeof(d)-1U;
 for(i=0;i<5U;++i){memcpy(data+j,roots[i],32U);j+=32U;}
 for(i=0;i<2U;++i){
  memcpy(data+j,w->binding_sha256[i],32U);j+=32U;
  memcpy(data+j,w->position_sha256[i],32U);j+=32U;
  memcpy(data+j,w->request_sha256[i],32U);j+=32U;
  memcpy(data+j,w->position_digits[i],81U);j+=81U;
  data[j++]=w->symbols[i];data[j++]=w->source_matrix_ids[i];
  data[j++]=w->tensor_left[i];
  data[j++]=(uint8_t)(w->vm5184_address[i]>>8U);
  data[j++]=(uint8_t)w->vm5184_address[i];
 }
 return j==sizeof(data)&&SHA256(data,sizeof(data),out)!=NULL;
}
static HHSExactStatus hhs220_rank_i001_once(
 const uint8_t *source,size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,HHS220RankI001HandoffV1 *w
){
 HHS220Ordered4x4I001CarrierV1 carrier;
 HHS220Ordered4x4RankChallengeV1 challenge;
 HHS220Ordered4x4BoundExecutionV1 bound;
 const HHS220Ordered4x4NativeTensorBindingV1 *t[2]={s,v};
 const uint8_t *digits[2],*position[2];
 HHSExactStatus status;
 size_t i;
 memset(w,0,sizeof(*w));
 status=hhs_exact_pass220_ordered4x4_i001_carrier_validate(
   source,source_bytes,s,v,parent,&carrier);
 if(status!=HHS_EXACT_STATUS_OK ||
    carrier.s_all_81_tokens_canonical!=1U||carrier.v_all_81_tokens_canonical!=1U||
    carrier.original_vm81_addresses_preserved!=1U||
    carrier.original_noncommutative_graph_preserved!=1U||
    carrier.authenticated_tensor_rank_proved!=0U||
    carrier.signed_predecessor_authenticated!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 status=hhs_exact_pass220_ordered4x4_rank_challenge(
   source,source_bytes,s,v,parent,&challenge);
 if(status!=HHS_EXACT_STATUS_OK||challenge.challenge_count!=2U||
    challenge.deterministic_challenges_replayed!=1U||
    challenge.required_flags!=HHS220_4X4_RANK_REQUIRED_FLAGS||
    challenge.registered_rank_witness_verified!=0U||
    challenge.native_action_semantics_verified!=0U||
    challenge.signed_vm81_admission_executed!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 status=hhs_exact_pass220_ordered4x4_execute_bound(
   source,source_bytes,s,v,&bound);
 if(status!=HHS_EXACT_STATUS_OK||
    bound.deterministic_bound_graph_replay_verified!=1U||
    bound.native_binding_authenticity_verified!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 if(memcmp(carrier.source_sha256,challenge.source_sha256,32U)!=0||
    memcmp(carrier.parent_reference_sha256,challenge.parent_reference_sha256,32U)!=0||
    memcmp(carrier.bound_graph_root_sha256,challenge.full_graph_root_sha256,32U)!=0)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 digits[0]=carrier.s_81_offset_digits;digits[1]=carrier.v_81_offset_digits;
 position[0]=carrier.s_carrier_position_root_sha256;
 position[1]=carrier.v_carrier_position_root_sha256;
 for(i=0;i<2U;++i){
  const HHS220Ordered4x4RankObligationV1 *q=&challenge.obligations[i];
  uint16_t address=(uint16_t)((uint16_t)t[i]->cell81*64U+t[i]->operation64);
  if(q->symbol!=(i==0U?'s':'v')||
     q->source_matrix_id!=(i==0U?2U:3U)||
     q->tensor_left_operand!=(i==0U?0U:1U)||
     q->source_matrix_rows!=4U||q->source_matrix_columns!=4U||
     q->vm5184_address!=address||
     (i==0U?carrier.s_vm5184_address:carrier.v_vm5184_address)!=address||
     (i==0U?bound.s_vm5184_address:bound.v_vm5184_address)!=address||
     q->rank_proved||q->phase_action_proved||
     q->definition_source_authenticated||
     q->signed_vm81_state_authenticated||q->matrix_action_value_authorized||
     memcmp(q->binding_root_sha256,bound.binding_roots_sha256[i],32U)!=0)
   return HHS_EXACT_STATUS_INVARIANT_FAILURE;
  w->vm5184_address[i]=address;
  w->symbols[i]=q->symbol;
  w->source_matrix_ids[i]=q->source_matrix_id;
  w->tensor_left[i]=q->tensor_left_operand;
  memcpy(w->position_digits[i],digits[i],81U);
  memcpy(w->binding_sha256[i],q->binding_root_sha256,32U);
  memcpy(w->position_sha256[i],position[i],32U);
  memcpy(w->request_sha256[i],q->challenge_root_sha256,32U);
 }
 w->struct_size=(uint32_t)sizeof(*w);w->version=HHS220_RANK_I001_HANDOFF_VERSION;
 w->unresolved_authority_mask=HHS220_4X4_BLOCK_ALL;
 memcpy(w->source_sha256,challenge.source_sha256,32U);
 memcpy(w->parent_sha256,challenge.parent_reference_sha256,32U);
 memcpy(w->full_graph_sha256,challenge.full_graph_root_sha256,32U);
 memcpy(w->carrier_sha256,carrier.carrier_profile_root_sha256,32U);
 memcpy(w->challenge_set_sha256,challenge.challenge_set_root_sha256,32U);
 if(!hhs220_rank_i001_digest(w,w->handoff_sha256))
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 w->candidate_only=1U;w->carrier_and_rank_crosschecked=1U;
 w->ordered_s_v_roles_checked=1U;w->all_162_positions_preserved=1U;
 return HHS_EXACT_STATUS_OK;
}
HHSExactStatus hhs_exact_pass220_ordered4x4_rank_i001_handoff(
 const uint8_t *source,size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,HHS220RankI001HandoffV1 *out
){
 HHS220RankI001HandoffV1 first,replay;
 HHSExactStatus status;
 if(!out)return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 if(source&&s&&v&&parent&&(
    hhs220_rank_i001_overlap(out,sizeof(*out),source,source_bytes)||
    hhs220_rank_i001_overlap(out,sizeof(*out),s,sizeof(*s))||
    hhs220_rank_i001_overlap(out,sizeof(*out),v,sizeof(*v))||
    hhs220_rank_i001_overlap(out,sizeof(*out),parent,sizeof(*parent))||
    hhs220_rank_i001_overlap(out,sizeof(*out),s->state_utf8,s->state_bytes)||
    hhs220_rank_i001_overlap(out,sizeof(*out),v->state_utf8,v->state_bytes)||
    hhs220_rank_i001_overlap(out,sizeof(*out),s->predecessor_hash216,s->predecessor_bytes)||
    hhs220_rank_i001_overlap(out,sizeof(*out),v->predecessor_hash216,v->predecessor_bytes)))
  return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out,0,sizeof(*out));
 if(!source||!s||!v||!parent)return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 status=hhs220_rank_i001_once(source,source_bytes,s,v,parent,&first);
 if(status!=HHS_EXACT_STATUS_OK)goto fail;
 status=hhs220_rank_i001_once(source,source_bytes,s,v,parent,&replay);
 if(status!=HHS_EXACT_STATUS_OK||memcmp(&first,&replay,sizeof(first))!=0||
    first.unresolved_authority_mask!=HHS220_4X4_BLOCK_ALL||
    first.authenticated_rank||first.authenticated_native_action||
    first.signed_parent_authenticated||first.mathematical_equality_proved||
    first.signed_vm81_admitted||first.hash72_commit_authority||
    first.hash216_commit_authority||first.canonical_vm81_mutation_authority){
  status=HHS_EXACT_STATUS_INVARIANT_FAILURE;goto fail;
 }
 first.deterministic_request_replay=1U;
 memcpy(out,&first,sizeof(first));
 memset(&first,0,sizeof(first));memset(&replay,0,sizeof(replay));
 return HHS_EXACT_STATUS_OK;
fail:
 memset(&first,0,sizeof(first));memset(&replay,0,sizeof(replay));
 return status;
}
