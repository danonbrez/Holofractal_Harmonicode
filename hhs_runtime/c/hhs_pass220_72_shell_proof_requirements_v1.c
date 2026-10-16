#include "hhs_pass220_72_shell_proof_requirements_v1.h"
#include <string.h>
int hhs_pass220_72_shell_requirements(const HHS72GateGraph *graph,
 HHS72ProofRequirements *out){
 size_t i;
 if(!out)return 0;
 memset(out,0,sizeof(*out));
 out->required_mask=15U;
 if(!graph||graph->edge_count!=4U||graph->proved_count!=0U||graph->admitted)return 0;
 for(i=0;i<4U;++i){
  if(graph->edges[i].proved)return 0;
  if(graph->edges[i].source_offset!=(uint32_t)(i==0U?74U:i==1U?89U:i==2U?92U:112U))return 0;
  if(graph->edges[i].kind!=(i<3U?HHS_72_GATE_ORDERED_RELATION:HHS_72_GATE_SQUARED_OUTER_RELATION))return 0;
  out->present_mask|=(uint32_t)(1U<<i);
 }
 /* Present means source-bound, not proved; proof mask stays zero. */
 return 1;
}
