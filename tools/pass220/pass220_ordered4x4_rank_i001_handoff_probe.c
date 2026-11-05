/* Native I001-to-rank request provenance and denial probe. */
#include "hhs_runtime_exact_abi.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define CHECK(c,m) do {if(!(c)){fprintf(stderr,"FAIL:%s\n",m);return 1;}}while(0)
static uint8_t source[HHS220_ORDERED4X4_SOURCE_BYTES+1U];
static uint8_t sb[5184],vb[5184];
static HHSExactPass219Hash216TransitionViewV1 parent;
static HHS220RankI001HandoffV1 a,b,invalid;
static int run(HHS220Ordered4x4NativeTensorBindingV1 *s,
               HHS220Ordered4x4NativeTensorBindingV1 *v,
               const HHSExactPass219Hash216TransitionViewV1 *p,
               HHS220RankI001HandoffV1 *w){
 return hhs_exact_pass220_ordered4x4_rank_i001_handoff(
 source,HHS220_ORDERED4X4_SOURCE_BYTES,s,v,p,w)==HHS_EXACT_STATUS_OK;
}
int main(void){
 HHS220Ordered4x4NativeTensorBindingV1 s,v;
 HHSExactPass219Hash216TransitionViewV1 corrupt;
 uint8_t offsets[81],hold;
 size_t n,i,len;
 FILE *f=fopen("contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode","rb");
 CHECK(f!=NULL,"source open");
 n=fread(source,1U,sizeof(source),f);
 CHECK(!ferror(f)&&fclose(f)==0&&n==HHS220_ORDERED4X4_SOURCE_BYTES,"source exact");
 CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent)==HHS_EXACT_STATUS_OK,"genesis parent");
 for(i=0;i<81U;++i)offsets[i]=(uint8_t)(i%9U);
 CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_emit(offsets,sb,sizeof(sb),&len)
       ==HHS_EXACT_STATUS_OK&&len==sizeof(sb),"emit s");
 for(i=0;i<81U;++i)offsets[i]=(uint8_t)((i+4U)%9U);
 CHECK(hhs_exact_pass220_ordered4x4_i001_offsets_emit(offsets,vb,sizeof(vb),&len)
       ==HHS_EXACT_STATUS_OK&&len==sizeof(vb),"emit v");
 memset(&s,0,sizeof(s));memset(&v,0,sizeof(v));
 s.struct_size=sizeof(s);s.symbol='s';s.cell81=4U;s.operation64=9U;
 s.state_utf8=sb;s.state_bytes=sizeof(sb);
 s.predecessor_hash216=(const uint8_t*)parent.transition_identity216;
 s.predecessor_bytes=216U;
 v.struct_size=sizeof(v);v.symbol='v';v.cell81=8U;v.operation64=17U;
 v.state_utf8=vb;v.state_bytes=sizeof(vb);
 v.predecessor_hash216=(const uint8_t*)parent.transition_identity216;
 v.predecessor_bytes=216U;
 CHECK(run(&s,&v,&parent,&a)&&run(&s,&v,&parent,&b),"handoff");
 CHECK(memcmp(&a,&b,sizeof(a))==0&&a.deterministic_request_replay==1U,"replay");
 CHECK(a.candidate_only==1U&&a.unresolved_authority_mask==HHS220_4X4_BLOCK_ALL&&
       !a.authenticated_rank&&!a.authenticated_native_action&&
       !a.signed_parent_authenticated&&!a.mathematical_equality_proved&&
       !a.signed_vm81_admitted&&!a.hash72_commit_authority&&
       !a.hash216_commit_authority&&!a.canonical_vm81_mutation_authority,
       "all signed/rank/mutation authority blocked");
 CHECK(a.carrier_and_rank_crosschecked&&a.ordered_s_v_roles_checked&&
       a.all_162_positions_preserved&&a.vm5184_address[0]==265U&&
       a.vm5184_address[1]==529U&&a.tensor_left[0]==0U&&
       a.tensor_left[1]==1U,"ordered address and action pair");
 for(i=0;i<81U;++i)CHECK(a.position_digits[0][i]==i%9U&&
       a.position_digits[1][i]==(i+4U)%9U,"162 exact offset digits");
 hold=sb[20U];sb[20U]=(uint8_t)(hold=='8'?'0':hold+1U);
 CHECK(run(&s,&v,&parent,&b)&&
       memcmp(a.request_sha256[0],b.request_sha256[0],32U)!=0&&
       memcmp(a.position_sha256[0],b.position_sha256[0],32U)!=0&&
       memcmp(a.position_sha256[1],b.position_sha256[1],32U)==0,
       "s change bound only to s");
 sb[20U]=hold;
 hold=vb[80U*64U+20U];vb[80U*64U+20U]=(uint8_t)(hold=='8'?'0':hold+1U);
 CHECK(run(&s,&v,&parent,&b)&&
       memcmp(a.position_sha256[1],b.position_sha256[1],32U)!=0,
       "last v position affects its witness");
 vb[80U*64U+20U]=hold;
 v.operation64=18U;
 CHECK(run(&s,&v,&parent,&b)&&a.vm5184_address[1]!=b.vm5184_address[1],
       "different native address alters handoff");
 v.operation64=17U;
 sb[80U*64U+20U]='9';
 CHECK(!run(&s,&v,&parent,&invalid)&&!invalid.candidate_only,
       "malformed last offset blocked");
 sb[80U*64U+20U]='8';
 corrupt=parent;corrupt.occurrences[215].sha256_index_record[0]^=1U;
 CHECK(!run(&s,&v,&corrupt,&invalid),"bad indexed parent rejected");
 v.symbol='s';CHECK(!run(&s,&v,&parent,&invalid),"role swap denied");v.symbol='v';
 source[0]^=1U;CHECK(!run(&s,&v,&parent,&invalid),"source drift denied");source[0]^=1U;
 CHECK(hhs_exact_pass220_ordered4x4_rank_i001_handoff(
       source,n,&s,&v,&parent,(HHS220RankI001HandoffV1*)(void*)sb)
       ==HHS_EXACT_STATUS_INVALID_ARGUMENT&&sb[0]=='+',"overlap rejected unchanged");
 puts("{\"schema\":\"HHS_P220_RANK_I001_HANDOFF_V1\",\"positions\":162,"
      "\"rank_authenticated\":false,\"signed_vm81_admitted\":false,"
      "\"canonical_receipts\":false}");
 return 0;
}
