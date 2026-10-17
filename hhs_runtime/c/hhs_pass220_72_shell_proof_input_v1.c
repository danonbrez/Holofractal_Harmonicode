#include "hhs_pass220_72_shell_proof_input_v1.h"
#include "hhs_pass220_72_shell_exact_residue_v1.h"
#include "hhs_pass220_72_shell_outer_projection_v1.h"
#include <string.h>
int hhs_pass220_72_shell_prepare_proof_input(
 const uint8_t *source,size_t size,HHS72ProofInput *out){
 HHS72GateGraph graph;
 char rn[160],rd[160],pn[16],pd[16];
 static const char expected_n[]="775710873160901421359061468620360862729920180854006643986760192036";
 static const char expected_d[]="3110094060648844770831880556173301180945943326884396380767822265625";
 HHS72ProofRequirements requirements;
 size_t i;
 if(!out)return 0;
 memset(out,0,sizeof(*out));
 if(!hhs_pass220_72_shell_build_gate_graph(source,size,&graph)||
    !hhs_pass220_72_shell_requirements(&graph,&requirements)||
    requirements.present_mask!=15U||requirements.proved_mask!=0U)return 0;
 if(!hhs_pass220_72_shell_exact_residue(rn,sizeof(rn),rd,sizeof(rd))||
    strcmp(rn,expected_n)!=0||strcmp(rd,expected_d)!=0)return 0;
 out->exact_residue_verified=1U;
 if(!hhs_pass220_72_shell_outer_projection(pn,sizeof(pn),pd,sizeof(pd))||
    strcmp(pn,"1")!=0||strcmp(pd,"1")!=0)return 0;
 out->canonical_projection_verified=1U;
 memcpy(out->source_sha256,graph.source_sha256,sizeof(out->source_sha256));
 memcpy(out->source_bytes,source,HHS_72_SHELL_SOURCE_BYTES);
 memcpy(out->operand_spans,graph.operands,sizeof(out->operand_spans));
 out->outer_left_span=graph.outer_left;
 out->outer_right_span=graph.outer_right;
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
