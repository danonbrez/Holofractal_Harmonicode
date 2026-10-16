#include "hhs_pass220_72_shell_proof_input_v1.h"
#include <string.h>
int hhs_pass220_72_shell_prepare_proof_input(
 const uint8_t *source,size_t size,HHS72ProofInput *out){
 HHS72GateGraph graph;
 HHS72ProofRequirements requirements;
 size_t i;
 if(!out)return 0;
 memset(out,0,sizeof(*out));
 if(!hhs_pass220_72_shell_build_gate_graph(source,size,&graph)||
    !hhs_pass220_72_shell_requirements(&graph,&requirements)||
    requirements.present_mask!=15U||requirements.proved_mask!=0U)return 0;
 memcpy(out->source_sha256,graph.source_sha256,sizeof(out->source_sha256));
 for(i=0;i<4U;++i){
  out->source_gate_offsets[i]=graph.edges[i].source_offset;
  out->ordered_left_node[i]=graph.edges[i].left_node;
  out->ordered_right_node[i]=graph.edges[i].right_node;
 }
 out->required_gate_mask=requirements.required_mask;
 out->proven_gate_mask=0U;
 out->provenance_authenticated=1U; /* Pinned source hash and graph spans only. */
 return 1; /* No evaluator, VM81 mutation, or Hash216 receipt. */
}
