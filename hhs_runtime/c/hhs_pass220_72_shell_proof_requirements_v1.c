#include "hhs_pass220_72_shell_proof_requirements_v1.h"
#include <string.h>
int hhs_pass220_72_shell_requirements(const HHS72GateGraph *graph,
 HHS72ProofRequirements *out){
 size_t i;
 static const uint8_t exact_sha[32]={
  0xcd,0x63,0x09,0xc3,0xa6,0xad,0x1d,0x71,0xa0,0x82,0x58,0x32,0x2b,0x95,0xdf,0x12,
  0x7e,0x6a,0xab,0x74,0x28,0x90,0x4a,0x5f,0xf9,0x03,0x44,0x98,0x64,0x85,0x9b,0xb2};
 static const uint32_t starts[4]={1U,76U,91U,94U};
 static const uint32_t ends[4]={74U,89U,92U,99U};
 static const uint32_t offsets[4]={74U,89U,92U,112U};
 if(!out)return 0;
 memset(out,0,sizeof(*out));
 out->required_mask=15U;
 if(!graph||graph->edge_count!=4U||graph->proved_count!=0U||graph->admitted||
    memcmp(graph->source_sha256,exact_sha,sizeof(exact_sha))!=0||
    graph->outer_left.byte_start!=0U||graph->outer_left.byte_end!=112U||
    graph->outer_right.byte_start!=114U||graph->outer_right.byte_end!=121U)return 0;
 for(i=0;i<4U;++i){
  if(graph->edges[i].proved)return 0;
  if(graph->operands[i].byte_start!=starts[i]||graph->operands[i].byte_end!=ends[i])return 0;
  if(graph->edges[i].left_node!=(uint32_t)(i<3U?i:4U)||
     graph->edges[i].right_node!=(uint32_t)(i<3U?i+1U:5U))return 0;
  if(graph->edges[i].source_offset!=offsets[i])return 0;
  if(graph->edges[i].kind!=(i<3U?HHS_72_GATE_ORDERED_RELATION:HHS_72_GATE_SQUARED_OUTER_RELATION))return 0;
  out->present_mask|=(uint32_t)(1U<<i);
 }
 /* Present means source-bound, not proved; proof mask stays zero. */
 return 1;
}
