#include "hhs178_physics.h"
#include <assert.h>
#include <string.h>
int main(void){
 HHS178Runtime rt;HHS178SourceIdentity sid;HHS178Model m;HHS178State s,c;HHS178RenderPacket p;uint64_t receipt=0;
 const char src[]="c^2*d_tau^2==c^2*d_t^2-d_x^2";
 HHS178Rational scalars[8]={{0,1},{0,1},{0,1},{0,1},{5,4},{3,4},{0,1},{0,1}};
 assert(hhs178_runtime_open(&rt)==HHS178_OK);
 assert(hhs178_source_ingest_exact(src,strlen(src),&sid)==HHS178_OK&&sid.byte_preserving==1U);
 assert(hhs178_model_register(&rt,HHS178_MODEL_RELATIVISTIC_FREE_PARTICLE,&sid,&m)==HHS178_OK);
 assert(hhs178_parameter_set_exact(&rt,m.model_handle,(HHS178Rational){1,16})==HHS178_OK);
 assert(hhs178_initial_state_admit(&rt,m.model_handle,scalars,8,&s)==HHS178_OK);
 assert(hhs178_step_candidate(&rt,&s,&c)==HHS178_OK);
 assert(hhs178_step_validate(&c)==HHS178_OK);
 assert(hhs178_step_commit(&rt,&c,0U)==HHS178_AUTHORITY_REQUIRED);
 assert(hhs178_step_commit(&rt,&c,1U)==HHS178_OK);
 assert(hhs178_render_packet_project(&c,&p)==HHS178_OK&&p.immutable_packet==1U&&p.renderer_feedback_authority==0U);
 assert(hhs178_receipt_export(&c,&receipt)==HHS178_OK&&receipt!=0U);
 assert(hhs178_runtime_close(&rt)==HHS178_OK);
 return 0;
}
