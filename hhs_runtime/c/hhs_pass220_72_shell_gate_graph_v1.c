#include "hhs_pass220_72_shell_gate_graph_v1.h"
#include <string.h>
int hhs_pass220_72_shell_build_gate_graph(
 const uint8_t *source,size_t length,HHS72GateGraph *out) {
 HHS72ShellResult lowered;
 size_t i;
 if(out==NULL) return 0;
 memset(out,0,sizeof(*out));
 if(hhs_pass220_72_shell_lower(source,length,&lowered)!=HHS_72_SHELL_STRUCTURAL_ONLY) return 0;
 memcpy(out->source_sha256,lowered.source_sha256,32);
 memcpy(out->operands,lowered.inner_operands,sizeof(out->operands));
 out->outer_left=lowered.outer_left;
 out->outer_right=lowered.outer_right;
 for(i=0U;i<3U;++i) {
   out->edges[i].source_offset=lowered.gate_offsets[i];
   out->edges[i].left_node=(uint32_t)i;
   out->edges[i].right_node=(uint32_t)(i+1U);
   out->edges[i].kind=HHS_72_GATE_ORDERED_RELATION;
 }
 out->edges[3].source_offset=lowered.gate_offsets[3];
 out->edges[3].left_node=4U; /* squared entire ordered chain / (c²-a²) */
 out->edges[3].right_node=5U; /* a^4/b² */
 out->edges[3].kind=HHS_72_GATE_SQUARED_OUTER_RELATION;
 out->edge_count=4U;
 return 1;
}
