/* HHS Pass220: source-bound matrix-rank readiness must remain fail-closed. */
#include "hhs_runtime_exact_abi.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define CHECK(c,m) do {if(!(c)){fprintf(stderr,"FAIL:%s\n",m);return 1;}}while(0)

static uint8_t source[HHS220_ORDERED4X4_SOURCE_BYTES+1U];
static uint8_t s_state[5184U],v_state[5184U];
static HHSExactPass219Hash216TransitionViewV1 parent;
static HHS220Ordered4x4ReadinessV1 first,again,changed,invalid;

static int probe(const HHS220Ordered4x4NativeTensorBindingV1 *s,
                 const HHS220Ordered4x4NativeTensorBindingV1 *v,
                 const HHSExactPass219Hash216TransitionViewV1 *p,
                 HHS220Ordered4x4ReadinessV1 *out) {
 return hhs_exact_pass220_ordered4x4_readiness(
   source,HHS220_ORDERED4X4_SOURCE_BYTES,s,v,p,out)==HHS_EXACT_STATUS_OK;
}
static int blocked(const HHS220Ordered4x4ReadinessV1 *w) {
 return w->decision==HHS220_4X4_READINESS_BLOCKED &&
    w->required_preflight_mask==HHS220_4X4_PREFLIGHT_ALL &&
    w->preflight_verified_mask==HHS220_4X4_PREFLIGHT_ALL &&
    w->missing_authority_mask==HHS220_4X4_BLOCK_ALL &&
    w->required_authority_mask==HHS220_4X4_BLOCK_ALL &&
    w->candidate_only==1U &&
    w->phase_address_is_not_full_tensor_phase==1U &&
    w->structural_hash216_is_not_signed_parent==1U &&
    w->declared_rank_is_not_authenticated_rank==1U &&
    w->result_is_not_math_equality==1U &&
    w->signed_vm81_admission_executed==0U &&
    w->hash72_commit_authority==0U &&
    w->hash216_commit_authority==0U &&
    w->canonical_vm81_mutation_authority==0U;
}
int main(void) {
 HHS220Ordered4x4NativeTensorBindingV1 s,v;
 HHSExactPass219Hash216TransitionViewV1 corrupt;
 FILE *f=fopen("contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode","rb");
 size_t n;
 CHECK(f!=NULL,"exact source exists");
 n=fread(source,1U,sizeof(source),f);
 CHECK(!ferror(f) && fclose(f)==0 && n==HHS220_ORDERED4X4_SOURCE_BYTES,
       "verbatim source length");
 CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent)==HHS_EXACT_STATUS_OK,
       "inherited genesis 216-index reference");
 memset(s_state,'X',sizeof(s_state));memset(v_state,'Y',sizeof(v_state));
 memset(&s,0,sizeof(s));memset(&v,0,sizeof(v));
 s.struct_size=(uint32_t)sizeof(s);s.symbol='s';s.cell81=4U;s.operation64=9U;
 s.state_utf8=s_state;s.state_bytes=sizeof(s_state);
 s.predecessor_hash216=(const uint8_t*)parent.transition_identity216;
 s.predecessor_bytes=216U;
 v.struct_size=(uint32_t)sizeof(v);v.symbol='v';v.cell81=8U;v.operation64=17U;
 v.state_utf8=v_state;v.state_bytes=sizeof(v_state);
 v.predecessor_hash216=(const uint8_t*)parent.transition_identity216;
 v.predecessor_bytes=216U;

 CHECK(probe(&s,&v,&parent,&first),"native readiness preflight success");
 CHECK(blocked(&first),"candidate MUST remain blocked");
 CHECK(first.challenge_count==2U,"two rank/phase/action obligations");
 CHECK(first.deterministic_report_replay_verified==1U,"internal full replay");
 CHECK(probe(&s,&v,&parent,&again),"repeat readiness probe");
 CHECK(memcmp(&first,&again,sizeof(first))==0,"deterministic exact report");
 CHECK(first.report_identity_sha256[0]!=0U || first.report_identity_sha256[1]!=0U,
       "diagnostic witness present");

 /* A forged caller-owned "ready" flag cannot influence a fresh native output. */
 again.decision=HHS220_4X4_READINESS_READY;
 again.missing_authority_mask=0U;
 again.canonical_vm81_mutation_authority=1U;
 CHECK(probe(&s,&v,&parent,&again),"fresh native readiness rebuild");
 CHECK(memcmp(&first,&again,sizeof(first))==0 && blocked(&again),
       "forged prefilled authority erased and denied");

 s_state[45]='S';
 CHECK(probe(&s,&v,&parent,&changed),"new addressed s state");
 CHECK(blocked(&changed),"mutating s cannot confer missing proofs");
 CHECK(memcmp(changed.proof_challenge_set_sha256,
              first.proof_challenge_set_sha256,32U)!=0,
       "s changes source-bound challenge set");
 s_state[45]='X';
 v_state[90]='V';
 CHECK(probe(&s,&v,&parent,&changed),"new addressed v state");
 CHECK(blocked(&changed),"mutating v cannot confer missing proofs");
 CHECK(memcmp(changed.full_graph_sha256,first.full_graph_sha256,32U)!=0,
       "v changes complete-expression graph root");
 v_state[90]='Y';

 s.operation64=8U;
 CHECK(probe(&s,&v,&parent,&changed),"different native phase address");
 CHECK(blocked(&changed),"different phase pair cannot auto-authorize rank");
 s.operation64=9U;
 corrupt=parent;
 corrupt.occurrences[215].sha256_index_record[0]^=1U;
 CHECK(!probe(&s,&v,&corrupt,&invalid),"corrupt parent index rejected");
 CHECK(invalid.decision==HHS220_4X4_READINESS_INVALID &&
       invalid.preflight_verified_mask==0U &&
       invalid.canonical_vm81_mutation_authority==0U,
       "invalid parent clears all preflight claims");
 v.predecessor_bytes=215U;
 CHECK(!probe(&s,&v,&parent,&invalid),"truncated lineage rejected");
 v.predecessor_bytes=216U;
 source[0]^=1U;
 CHECK(!probe(&s,&v,&parent,&invalid),"source tamper rejected");
 CHECK(invalid.preflight_verified_mask==0U &&
       invalid.hash216_commit_authority==0U,"source drift stays denied");
 source[0]^=1U;
 v.symbol='s';
 CHECK(!probe(&s,&v,&parent,&invalid),"wrong typed role rejected");
 v.symbol='v';
 CHECK(hhs_exact_pass220_ordered4x4_readiness(source,n,&s,&v,&parent,NULL)
       !=HHS_EXACT_STATUS_OK,"null output denied");

 puts("{\"schema\":\"HHS_PASS220_4X4_READINESS_DENIAL_V1\","
      "\"preflight_verified_mask\":63,\"missing_authority_mask\":255,"
      "\"deterministic_full_replay\":true,\"forged_ready_rejected\":true,"
      "\"signed_parent_authenticated\":false,\"rank_proved\":false,"
      "\"tensor_values_computed\":false,\"equality_proved\":false,"
      "\"vm81_admitted\":false,\"canonical_receipts\":false}");
 return 0;
}
