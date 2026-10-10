/* Native rank/action proof requests: deterministic, signed admission DENIED. */
#include "hhs_runtime_exact_abi.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define REQUIRE(c,msg) do {if(!(c)){fprintf(stderr,"FAIL:%s\n",msg);return 1;}}while(0)

static uint8_t source[HHS220_ORDERED4X4_SOURCE_BYTES+1U];
static uint8_t s_state[5184U],v_state[5184U];
static HHSExactPass219Hash216TransitionViewV1 parent,changed_parent;
static HHS220Ordered4x4RankChallengeV1 a,b,c,failed;

static int derive(const HHS220Ordered4x4NativeTensorBindingV1 *s,
                  const HHS220Ordered4x4NativeTensorBindingV1 *v,
                  const HHSExactPass219Hash216TransitionViewV1 *reference,
                  HHS220Ordered4x4RankChallengeV1 *out) {
 return hhs_exact_pass220_ordered4x4_rank_challenge(
  source,HHS220_ORDERED4X4_SOURCE_BYTES,s,v,reference,out)==HHS_EXACT_STATUS_OK;
}
static int rank_is_closed(const HHS220Ordered4x4RankChallengeV1 *request) {
 size_t i;
 if(request->registered_rank_witness_verified ||
    request->native_action_semantics_verified ||
    request->mathematical_equality_proved ||
    request->signed_vm81_admission_executed ||
    request->hash72_commit_authority ||
    request->hash216_commit_authority ||
    request->canonical_vm81_mutation_authority)
  return 0;
 for(i=0U;i<2U;++i) {
  const HHS220Ordered4x4RankObligationV1 *q=&request->obligations[i];
  if(q->rank_proved || q->phase_action_proved ||
     q->definition_source_authenticated ||
     q->signed_vm81_state_authenticated ||
     q->matrix_action_value_authorized) return 0;
 }
 return 1;
}
int main(void) {
 HHS220Ordered4x4NativeTensorBindingV1 s,v;
 FILE *f=fopen("contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode","rb");
 size_t n;
 REQUIRE(f!=NULL,"source open");
 n=fread(source,1U,sizeof(source),f);
 REQUIRE(!ferror(f) && fclose(f)==0 &&
         n==HHS220_ORDERED4X4_SOURCE_BYTES,"verbatim source");
 REQUIRE(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent)==HHS_EXACT_STATUS_OK,
         "inherited Hash216 complete indexed reference");
 memset(s_state,'X',sizeof(s_state));
 memset(v_state,'Y',sizeof(v_state));
 memset(&s,0,sizeof(s));memset(&v,0,sizeof(v));
 s.struct_size=(uint32_t)sizeof(s);s.symbol='s';s.cell81=4U;s.operation64=9U;
 s.state_utf8=s_state;s.state_bytes=sizeof(s_state);
 s.predecessor_hash216=(const uint8_t *)parent.transition_identity216;
 s.predecessor_bytes=216U;
 v.struct_size=(uint32_t)sizeof(v);v.symbol='v';v.cell81=8U;v.operation64=17U;
 v.state_utf8=v_state;v.state_bytes=sizeof(v_state);
 v.predecessor_hash216=(const uint8_t *)parent.transition_identity216;
 v.predecessor_bytes=216U;

 REQUIRE(derive(&s,&v,&parent,&a),"rank/action challenge");
 REQUIRE(derive(&s,&v,&parent,&b),"repeat challenge");
 REQUIRE(memcmp(&a,&b,sizeof(a))==0,"deterministic whole descriptor");
 REQUIRE(a.challenge_count==2U &&
         a.required_flags==HHS220_4X4_RANK_REQUIRED_FLAGS,
         "two mandatory full proof requests");
 REQUIRE(a.complete_expression_source_verified==1U &&
         a.hash216_parent_index_structure_verified==1U &&
         a.full_native_graph_constructed==1U &&
         a.native_phase_addresses_verified==1U &&
         a.complete_proof_challenges_derived==1U &&
         a.deterministic_challenges_replayed==1U,
         "complete source and native witness provenance");
 REQUIRE(rank_is_closed(&a),"all unauthorized rank/admission outputs closed");
 REQUIRE(a.obligations[0].symbol=='s' &&
         a.obligations[0].source_matrix_id==2U &&
         a.obligations[0].tensor_left_operand==0U &&
         a.obligations[0].vm5184_address==265U,
         "s remains right operand in MatrixTimes(D,s)");
 REQUIRE(a.obligations[1].symbol=='v' &&
         a.obligations[1].source_matrix_id==3U &&
         a.obligations[1].tensor_left_operand==1U &&
         a.obligations[1].vm5184_address==529U,
         "v remains left operand in MatrixTimes(v,L)");
 REQUIRE(a.obligations[0].source_matrix_rows==4U &&
         a.obligations[1].source_matrix_columns==4U,
         "source matrices retain fixed 4x4 geometry");
 REQUIRE(memcmp(a.obligations[0].challenge_root_sha256,
                a.obligations[1].challenge_root_sha256,32U)!=0,
         "right action versus left action cannot silently unify");

 s_state[30]='S';
 REQUIRE(derive(&s,&v,&parent,&c),"changed s creates new query");
 REQUIRE(memcmp(a.obligations[0].binding_root_sha256,
                c.obligations[0].binding_root_sha256,32U)!=0,
         "s tensor is not scalarized out of identity");
 REQUIRE(memcmp(a.obligations[1].binding_root_sha256,
                c.obligations[1].binding_root_sha256,32U)==0,
         "s cannot change unrelated v tensor identity");
 REQUIRE(memcmp(a.challenge_set_root_sha256,
                c.challenge_set_root_sha256,32U)!=0,
         "full query binds modified s");
 REQUIRE(rank_is_closed(&c),"modified s cannot mint rank proof");
 s_state[30]='X';

 v_state[44]='V';
 REQUIRE(derive(&s,&v,&parent,&c),"changed v creates new query");
 REQUIRE(memcmp(a.obligations[0].binding_root_sha256,
                c.obligations[0].binding_root_sha256,32U)==0,
         "v cannot change unrelated s tensor identity");
 REQUIRE(memcmp(a.obligations[1].binding_root_sha256,
                c.obligations[1].binding_root_sha256,32U)!=0,
         "v state changes its addressed proof request");
 REQUIRE(rank_is_closed(&c),"modified v cannot mint rank proof");
 v_state[44]='Y';

 s.operation64=8U;
 REQUIRE(derive(&s,&v,&parent,&c),"changed native phase operation");
 REQUIRE(memcmp(a.obligations[0].native_phase_address_root_sha256,
                c.obligations[0].native_phase_address_root_sha256,32U)!=0,
         "phase-address changes affect the exact rank challenge");
 s.operation64=9U;
 v.cell81=9U;
 REQUIRE(derive(&s,&v,&parent,&c),"changed v native address");
 REQUIRE(memcmp(a.obligations[1].challenge_root_sha256,
                c.obligations[1].challenge_root_sha256,32U)!=0,
         "cell identity participates in challenge");
 v.cell81=8U;

 changed_parent=parent;
 changed_parent.occurrences[215].sha256_index_record[0]^=1U;
 REQUIRE(!derive(&s,&v,&changed_parent,&failed),"altered Hash216 index rejected");
 REQUIRE(rank_is_closed(&failed) &&
         !failed.complete_proof_challenges_derived,"rejected parent no authority");
 v.predecessor_bytes=215U;
 REQUIRE(!derive(&s,&v,&parent,&failed),"short ancestry rejected");
 v.predecessor_bytes=216U;
 s.cell81=81U;
 REQUIRE(!derive(&s,&v,&parent,&failed),"invalid tensor address rejected");
 s.cell81=4U;
 v.symbol='s';
 REQUIRE(!derive(&s,&v,&parent,&failed),"role reversal rejected");
 v.symbol='v';
 source[0]^=1U;
 REQUIRE(!derive(&s,&v,&parent,&failed),"source tamper rejected");
 REQUIRE(rank_is_closed(&failed),"rejected source never gains authority");
 source[0]^=1U;
 REQUIRE(hhs_exact_pass220_ordered4x4_rank_challenge(
   source,n,&s,&v,&parent,NULL)!=HHS_EXACT_STATUS_OK,"null destination rejected");

 puts("{\"schema\":\"HHS_PASS220_ORDERED4X4_RANK_ACTION_PROOF_REQUEST_V1\","
      "\"proof_requests\":2,\"native_state_identity_bound\":true,"
      "\"ordered_tensor_action_direction_bound\":true,"
      "\"full_source_phase_and_parent_bound\":true,"
      "\"deterministic_request_replay\":true,"
      "\"rank_proved\":false,\"matrix_values_computed\":false,"
      "\"signed_parent_authenticated\":false,\"vm81_admitted\":false,"
      "\"canonical_receipts\":false}");
 return 0;
}
