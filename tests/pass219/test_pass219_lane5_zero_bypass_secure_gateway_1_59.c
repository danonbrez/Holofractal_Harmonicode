#include "../../hhs_runtime/include/hhs_runtime_exact_abi.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct Owners { uint8_t P,p,q,delta,A,B; } Owners;
static HHSExactBigUIntView v(const uint8_t*x){HHSExactBigUIntView r={0};r.struct_size=sizeof(r);r.byte_length=1;r.bytes_be=x;return r;}
static void key(void){static const char d[]="0123456789abcdef";char h[129];size_t i;for(i=0;i<64;i++){uint8_t x=(uint8_t)(i+1);h[2*i]=d[x>>4];h[2*i+1]=d[x&15];}h[128]=0;assert(setenv(HHS_EXACT_PASS219_VM81_PQC_KEY_ENV,h,1)==0);}
int main(void){
 HHSExactPass219Lane5ZeroBypassGatewayDescriptorV1 d={0}; uint8_t in16[16]={0,0,0,0,0,0,0,128,0,0,128,127,1,0,192,127},out16[16]={0}; size_t n=0;
 assert(hhs_exact_pass219_lane5_zero_bypass_gateway_validate()==HHS_EXACT_STATUS_OK);
 assert(hhs_exact_pass219_lane5_zero_bypass_gateway_descriptor(&d)==HHS_EXACT_STATUS_OK);
 assert(d.single_public_mutation_gateway==1&&d.ieee754_payload_passthrough_allowed==1&&d.floating_point_canonical_authority==0&&d.constraint_forced_execution==1&&d.policy_choice_authority==0&&d.hash216_memory_carries_forward==1);
 assert(hhs_exact_pass219_lane5_payload_roundtrip_exact(in16,sizeof(in16),out16,sizeof(out16),&n)==HHS_EXACT_STATUS_OK&&n==sizeof(in16)&&memcmp(in16,out16,n)==0);
 key();
 assert(hhs_exact_pass219_vm81_pqc_signature_provider_available(HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65)==1U);
 HHSExactPass219Hash216TransitionViewV1 parent={0}; assert(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent)==HHS_EXACT_STATUS_OK);
 Owners o={4,3,5,1,16,16}; HHSExactUQCELInputV1 q={0}; q.struct_size=sizeof(q);q.uqcel_version=hhs_exact_uqcel_version();q.profile=HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;q.P=v(&o.P);q.p=v(&o.p);q.q=v(&o.q);q.delta=v(&o.delta);q.A=v(&o.A);q.B=v(&o.B);q.cell81=41;q.left_basis8=HHS_EXACT_PHASE_X;q.right_basis8=HHS_EXACT_PHASE_Y;assert(hhs_exact_uqcel_source_sha256(q.source_envelope_sha256)==HHS_EXACT_STATUS_OK);memcpy(q.previous_hash72,parent.receipt_hash72,HHS_EXACT_HASH72_STRLEN);
 HHSExactVM81Frame f={0}; for(size_t i=0;i<81;i++)f.words[i]=UINT64_C(0x0F1E2D3C4B5A6978)^(uint64_t)(i*37U); uint8_t raw[648],committed[648];size_t rl=0,cl=0;assert(hhs_exact_vm81_frame_export_le(&f,raw,sizeof(raw),&rl)==HHS_EXACT_STATUS_OK);
 HHSExactPass219RNAAdmissionV1 a={0};HHSExactPass219VM81PQCFirewallReceiptV1 fw={0};HHSExactPass219VM81PQCSignatureReceiptV1 sg={0};HHSExactPass219VM81EnvironmentReceiptV1 ev={0};HHSExactPass219Lane5ZeroBypassGatewayReceiptV1 gr={0};
 assert(hhs_exact_pass219_lane5_gateway_admit_raw5184(220,HHS_EXACT_PASS219_VM81_PQC_SIGNATURE_ALGORITHM_ML_DSA_65,&q,raw,rl,&parent,0,0,HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,0,committed,sizeof(committed),&cl,&a,&fw,&sg,&ev,&gr)==HHS_EXACT_STATUS_OK);
 assert(cl==648&&memcmp(raw,committed,648)==0&&gr.cpp_rna_cell_wall_routed==1&&gr.pqc_authenticated==1&&gr.pqc_signature_verified==1&&gr.environmental_witness_verified==1&&gr.parent_hash216_verified==1&&gr.child_hash216_verified==1&&gr.vm81_canonical_commit_observed==1&&gr.hash216_continuation_eligible==1);
 puts("PASS lane5 zero-bypass secure gateway 1.59");return 0;
}