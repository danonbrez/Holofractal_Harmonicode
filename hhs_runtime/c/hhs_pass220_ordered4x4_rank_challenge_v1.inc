/* Pass 220: deterministic challenge for authentic signed tensor rank/phase
 * evidence. The challenge is NOT a proof and grants no mutation authority.
 */
#include "../include/hhs_pass220_ordered4x4_rank_challenge_v1.h"
#include <openssl/sha.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>

static int hhs220_rank_challenge_one(
 const uint8_t source_root[32], const uint8_t parent_root[32],
 const uint8_t graph_root[32],
 const HHS220Ordered4x4PhaseAddressV1 *phase,
 const uint8_t action_root[32],
 uint8_t matrix_id,uint8_t tensor_left,
 HHS220Ordered4x4RankObligationV1 *out
) {
 static const char domain[]="HHS-P220-4X4-NATIVE-RANK-ACTION-PROOF-REQUEST-V1";
 uint8_t material[sizeof(domain)-1U+32U*6U+7U];
 size_t cursor=0U;
 if(phase==NULL || out==NULL || action_root==NULL) return 0;
 if(phase->address_roundtrip_verified!=1U ||
    phase->native_phase_operator_executed!=1U ||
    phase->native_ordered_source_preserved!=1U)
  return 0;
 memset(out,0,sizeof(*out));
 out->struct_size=(uint32_t)sizeof(*out);
 out->version=HHS220_4X4_RANK_PROOF_BINDING_VERSION;
 out->required_flags=HHS220_4X4_RANK_REQUIRED_FLAGS;
 out->vm5184_address=phase->address5184;
 out->symbol=phase->symbol;
 out->source_matrix_id=matrix_id;
 out->tensor_left_operand=tensor_left;
 out->source_matrix_rows=4U;
 out->source_matrix_columns=4U;
 memcpy(out->binding_root_sha256,phase->source_bound_symbol_root,32U);
 memcpy(out->native_phase_address_root_sha256,
        phase->directional_phase_address_root,32U);
 memcpy(out->ordered_matrix_action_root_sha256,action_root,32U);

 memcpy(material+cursor,domain,sizeof(domain)-1U);
 cursor+=sizeof(domain)-1U;
 memcpy(material+cursor,source_root,32U);cursor+=32U;
 memcpy(material+cursor,parent_root,32U);cursor+=32U;
 memcpy(material+cursor,graph_root,32U);cursor+=32U;
 memcpy(material+cursor,out->binding_root_sha256,32U);cursor+=32U;
 memcpy(material+cursor,out->native_phase_address_root_sha256,32U);cursor+=32U;
 memcpy(material+cursor,out->ordered_matrix_action_root_sha256,32U);cursor+=32U;
 material[cursor++]=out->symbol;
 material[cursor++]=out->source_matrix_id;
 material[cursor++]=out->tensor_left_operand;
 material[cursor++]=out->source_matrix_rows;
 material[cursor++]=out->source_matrix_columns;
 material[cursor++]=(uint8_t)(out->vm5184_address>>8U);
 material[cursor++]=(uint8_t)out->vm5184_address;
 return cursor==sizeof(material) &&
        SHA256(material,sizeof(material),out->challenge_root_sha256)!=NULL;
}

static int hhs220_rank_challenge_set(
 const HHS220Ordered4x4RankChallengeV1 *c,uint8_t output[32]
) {
 static const char domain[]="HHS-P220-4X4-TWO-NATIVE-ACTION-PROOF-REQUESTS-V1";
 uint8_t material[sizeof(domain)-1U+5U*32U];
 size_t cursor=0U;
 memcpy(material+cursor,domain,sizeof(domain)-1U);
 cursor+=sizeof(domain)-1U;
 memcpy(material+cursor,c->source_sha256,32U);cursor+=32U;
 memcpy(material+cursor,c->parent_reference_sha256,32U);cursor+=32U;
 memcpy(material+cursor,c->full_graph_root_sha256,32U);cursor+=32U;
 memcpy(material+cursor,c->obligations[0].challenge_root_sha256,32U);
 cursor+=32U;
 memcpy(material+cursor,c->obligations[1].challenge_root_sha256,32U);
 cursor+=32U;
 return cursor==sizeof(material) && SHA256(material,sizeof(material),output)!=NULL;
}

static HHSExactStatus hhs220_rank_challenge_once(
 const uint8_t *source,size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220Ordered4x4RankChallengeV1 *out
) {
 HHS220Ordered4x4FullGraphV1 graph;
 HHS220Ordered4x4PhaseAddressGateV1 phase;
 HHSExactStatus status;
 memset(out,0,sizeof(*out));
 out->struct_size=(uint32_t)sizeof(*out);
 out->version=HHS220_4X4_RANK_PROOF_BINDING_VERSION;

 status=hhs_exact_pass220_ordered4x4_full_graph(
    source,source_bytes,s,v,parent,&graph);
 if(status!=HHS_EXACT_STATUS_OK ||
    graph.source_verified!=1U ||
    graph.full_216_index_parent_reference_verified!=1U ||
    graph.native_phase_address_verified!=1U ||
    graph.deterministic_full_graph_replay_verified!=1U ||
    graph.tensor_action_rank_proved!=0U ||
    graph.native_matrix_values_derived!=0U ||
    graph.equality_mathematically_proved!=0U ||
    graph.signed_vm81_admission_executed!=0U ||
    graph.hash72_commit_authority!=0U ||
    graph.hash216_commit_authority!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 status=hhs_exact_pass220_ordered4x4_phase_address_gate(
    source,source_bytes,s,v,parent,&phase);
 if(status!=HHS_EXACT_STATUS_OK ||
    phase.both_phase_address_roundtrips_verified!=1U ||
    phase.both_native_phase_products_verified!=1U ||
    phase.tensor_action_rank_resolved!=0U ||
    phase.tensor_phase_state_fully_verified!=0U ||
    phase.signed_vm81_admitted!=0U ||
    phase.hash216_commit_authority!=0U ||
    memcmp(phase.source_sha256,graph.source_sha256,32U)!=0 ||
    memcmp(phase.parent_reference_sha256,
           graph.parent_reference_sha256,32U)!=0 ||
    memcmp(phase.phase_geometry_root_sha256,
           graph.phase_root_sha256,32U)!=0)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 memcpy(out->source_sha256,graph.source_sha256,32U);
 memcpy(out->parent_reference_sha256,graph.parent_reference_sha256,32U);
 memcpy(out->full_graph_root_sha256,graph.full_graph_root_sha256,32U);

 /* s: MatrixTimes(D,s) => right-hand tensor operand; v: MatrixTimes(v,L)
  * => left-hand tensor operand. NEVER transpose or swap these roles. */
 if(!hhs220_rank_challenge_one(
       out->source_sha256,out->parent_reference_sha256,
       out->full_graph_root_sha256,&phase.bindings[0],
       graph.denominator_root_sha256,2U,0U,&out->obligations[0]) ||
    !hhs220_rank_challenge_one(
       out->source_sha256,out->parent_reference_sha256,
       out->full_graph_root_sha256,&phase.bindings[1],
       graph.rhs_root_sha256,3U,1U,&out->obligations[1]) ||
    out->obligations[0].symbol!='s' ||
    out->obligations[1].symbol!='v' ||
    !hhs220_rank_challenge_set(out,out->challenge_set_root_sha256))
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 out->challenge_count=HHS220_4X4_RANK_OBLIGATIONS;
 out->required_flags=HHS220_4X4_RANK_REQUIRED_FLAGS;
 out->complete_expression_source_verified=1U;
 out->hash216_parent_index_structure_verified=1U;
 out->full_native_graph_constructed=1U;
 out->native_phase_addresses_verified=1U;
 out->complete_proof_challenges_derived=1U;
 /* All rank/phase-action/full equality/admission flags remain zero. */
 return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass220_ordered4x4_rank_challenge(
 const uint8_t *source,size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent,
 HHS220Ordered4x4RankChallengeV1 *out_challenge
) {
 HHS220Ordered4x4RankChallengeV1 replay;
 HHSExactStatus status;
 if(out_challenge==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out_challenge,0,sizeof(*out_challenge));
 out_challenge->struct_size=(uint32_t)sizeof(*out_challenge);
 out_challenge->version=HHS220_4X4_RANK_PROOF_BINDING_VERSION;
 if(source==NULL || s==NULL || v==NULL || parent==NULL)
  return HHS_EXACT_STATUS_INVALID_ARGUMENT;

 status=hhs220_rank_challenge_once(source,source_bytes,s,v,parent,out_challenge);
 if(status!=HHS_EXACT_STATUS_OK) goto fail;
 status=hhs220_rank_challenge_once(source,source_bytes,s,v,parent,&replay);
 if(status!=HHS_EXACT_STATUS_OK ||
    memcmp(out_challenge,&replay,sizeof(replay))!=0) {
  status=HHS_EXACT_STATUS_INVARIANT_FAILURE;
  goto fail;
 }
 out_challenge->deterministic_challenges_replayed=1U;
 return HHS_EXACT_STATUS_OK;
fail:
 memset(out_challenge,0,sizeof(*out_challenge));
 out_challenge->struct_size=(uint32_t)sizeof(*out_challenge);
 out_challenge->version=HHS220_4X4_RANK_PROOF_BINDING_VERSION;
 return status;
}
