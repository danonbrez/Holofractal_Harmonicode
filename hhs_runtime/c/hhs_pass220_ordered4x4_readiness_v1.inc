/* Exact read-only admission-readiness accounting for Pass220 4x4 equation.
 * This implementation has no trusted s/v rank, signed-parent or value verifier
 * and must therefore return BLOCKED for every structurally valid candidate.
 * No host arithmetic, scalar coercion, Hash72/216 minting or VM81 mutation.
 */
#include "../include/hhs_pass220_ordered4x4_readiness_v1.h"
#include <openssl/sha.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>

static int hhs220_readiness_digest(
 const HHS220Ordered4x4ReadinessV1 *w,
 uint8_t out_sha[32]
) {
 static const char DOMAIN[]="HHS-P220-4X4-READINESS-BLOCKED-AUTHORITY-ACCOUNTING-V1";
 uint8_t data[sizeof(DOMAIN)-1U+32U*4U+20U];
 size_t offset=0U;
 const uint32_t counters[5]={
   w->decision,w->preflight_verified_mask,w->required_preflight_mask,
   w->missing_authority_mask,w->required_authority_mask
 };
 size_t i;
 memcpy(data+offset,DOMAIN,sizeof(DOMAIN)-1U);
 offset+=sizeof(DOMAIN)-1U;
 memcpy(data+offset,w->source_sha256,32U);offset+=32U;
 memcpy(data+offset,w->parent_reference_sha256,32U);offset+=32U;
 memcpy(data+offset,w->proof_challenge_set_sha256,32U);offset+=32U;
 memcpy(data+offset,w->full_graph_sha256,32U);offset+=32U;
 for(i=0U;i<5U;++i) {
  data[offset++]=(uint8_t)(counters[i]>>24U);
  data[offset++]=(uint8_t)(counters[i]>>16U);
  data[offset++]=(uint8_t)(counters[i]>>8U);
  data[offset++]=(uint8_t)counters[i];
 }
 return offset==sizeof(data) && SHA256(data,sizeof(data),out_sha)!=NULL;
}

static HHSExactStatus hhs220_readiness_once(
 const uint8_t *source,size_t source_size,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220Ordered4x4ReadinessV1 *out
) {
 HHS220Ordered4x4RankChallengeV1 request;
 HHS220Ordered4x4FullGraphV1 graph;
 HHSExactStatus status;
 size_t i;
 memset(out,0,sizeof(*out));
 out->struct_size=(uint32_t)sizeof(*out);
 out->version=UINT32_C(0x00010000);
 out->decision=HHS220_4X4_READINESS_INVALID;
 status=hhs_exact_pass220_ordered4x4_rank_challenge(
   source,source_size,s,v,parent,&request);
 if(status!=HHS_EXACT_STATUS_OK ||
    request.complete_expression_source_verified!=1U ||
    request.hash216_parent_index_structure_verified!=1U ||
    request.full_native_graph_constructed!=1U ||
    request.native_phase_addresses_verified!=1U ||
    request.complete_proof_challenges_derived!=1U ||
    request.deterministic_challenges_replayed!=1U ||
    request.challenge_count!=2U ||
    request.required_flags!=HHS220_4X4_RANK_REQUIRED_FLAGS ||
    request.registered_rank_witness_verified!=0U ||
    request.native_action_semantics_verified!=0U ||
    request.mathematical_equality_proved!=0U ||
    request.signed_vm81_admission_executed!=0U ||
    request.hash72_commit_authority!=0U ||
    request.hash216_commit_authority!=0U ||
    request.canonical_vm81_mutation_authority!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 for(i=0U;i<2U;++i) {
  const HHS220Ordered4x4RankObligationV1 *item=&request.obligations[i];
  if(item->rank_proved!=0U || item->phase_action_proved!=0U ||
     item->definition_source_authenticated!=0U ||
     item->signed_vm81_state_authenticated!=0U ||
     item->matrix_action_value_authorized!=0U ||
     item->required_flags!=HHS220_4X4_RANK_REQUIRED_FLAGS)
   return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 }
 status=hhs_exact_pass220_ordered4x4_full_graph(
   source,source_size,s,v,parent,&graph);
 if(status!=HHS_EXACT_STATUS_OK ||
    graph.source_verified!=1U ||
    graph.full_216_index_parent_reference_verified!=1U ||
    graph.typed_s_v_identity_verified!=1U ||
    graph.native_phase_address_verified!=1U ||
    graph.deterministic_full_graph_replay_verified!=1U ||
    graph.tensor_action_rank_proved!=0U ||
    graph.native_matrix_values_derived!=0U ||
    graph.native_quotient_value_derived!=0U ||
    graph.native_matrix_power_value_derived!=0U ||
    graph.equality_mathematically_proved!=0U ||
    graph.predecessor_pqc_signature_authenticated!=0U ||
    graph.signed_vm81_admission_executed!=0U ||
    graph.hash72_commit_authority!=0U ||
    graph.hash216_commit_authority!=0U ||
    graph.canonical_vm81_mutation_authority!=0U ||
    memcmp(request.source_sha256,graph.source_sha256,32U)!=0 ||
    memcmp(request.parent_reference_sha256,graph.parent_reference_sha256,32U)!=0 ||
    memcmp(request.full_graph_root_sha256,graph.full_graph_root_sha256,32U)!=0)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 out->decision=HHS220_4X4_READINESS_BLOCKED;
 out->preflight_verified_mask=HHS220_4X4_PREFLIGHT_ALL;
 out->required_preflight_mask=HHS220_4X4_PREFLIGHT_ALL;
 /* Each currently unsatisfied obligation is authoritative only to a
  * registered verifier. This path MUST NOT clear any of these eight bits. */
 out->missing_authority_mask=HHS220_4X4_BLOCK_ALL;
 out->required_authority_mask=HHS220_4X4_BLOCK_ALL;
 out->challenge_count=request.challenge_count;
 out->candidate_only=1U;
 out->phase_address_is_not_full_tensor_phase=1U;
 out->structural_hash216_is_not_signed_parent=1U;
 out->declared_rank_is_not_authenticated_rank=1U;
 out->result_is_not_math_equality=1U;
 memcpy(out->source_sha256,request.source_sha256,32U);
 memcpy(out->parent_reference_sha256,request.parent_reference_sha256,32U);
 memcpy(out->proof_challenge_set_sha256,request.challenge_set_root_sha256,32U);
 memcpy(out->full_graph_sha256,graph.full_graph_root_sha256,32U);
 if(!hhs220_readiness_digest(out,out->report_identity_sha256))
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass220_ordered4x4_readiness(
 const uint8_t *source,size_t source_size,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220Ordered4x4ReadinessV1 *out_readiness
) {
 HHS220Ordered4x4ReadinessV1 replay;
 HHSExactStatus status;
 if(out_readiness==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out_readiness,0,sizeof(*out_readiness));
 out_readiness->struct_size=(uint32_t)sizeof(*out_readiness);
 out_readiness->version=UINT32_C(0x00010000);
 if(source==NULL || s==NULL || v==NULL || parent==NULL)
  return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 status=hhs220_readiness_once(
   source,source_size,s,v,parent,out_readiness);
 if(status!=HHS_EXACT_STATUS_OK) goto fail;
 status=hhs220_readiness_once(source,source_size,s,v,parent,&replay);
 if(status!=HHS_EXACT_STATUS_OK ||
    memcmp(out_readiness,&replay,sizeof(replay))!=0 ||
    out_readiness->decision!=HHS220_4X4_READINESS_BLOCKED ||
    out_readiness->preflight_verified_mask!=HHS220_4X4_PREFLIGHT_ALL ||
    out_readiness->missing_authority_mask!=HHS220_4X4_BLOCK_ALL ||
    out_readiness->candidate_only!=1U ||
    out_readiness->signed_vm81_admission_executed!=0U ||
    out_readiness->hash72_commit_authority!=0U ||
    out_readiness->hash216_commit_authority!=0U ||
    out_readiness->canonical_vm81_mutation_authority!=0U) {
  status=HHS_EXACT_STATUS_INVARIANT_FAILURE;
  goto fail;
 }
 out_readiness->deterministic_report_replay_verified=1U;
 return HHS_EXACT_STATUS_OK;
fail:
 memset(out_readiness,0,sizeof(*out_readiness));
 out_readiness->struct_size=(uint32_t)sizeof(*out_readiness);
 out_readiness->version=UINT32_C(0x00010000);
 return status;
}
