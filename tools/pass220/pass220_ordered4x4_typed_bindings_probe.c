/* Bound HHS tensor state ingress: branch-specific roots; no scalar fallback. */
#include "hhs_runtime_exact_abi.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define CHECK(c,m) do {if (!(c)){fprintf(stderr,"FAIL:%s\n",m);return 1;}}while(0)
static uint8_t source[HHS220_ORDERED4X4_SOURCE_BYTES+1U];
static uint8_t state_s[HHS220_ORDERED4X4_MAX_UTF8_BYTES+1U];
static uint8_t state_v[HHS220_ORDERED4X4_MAX_UTF8_BYTES+1U];
static uint8_t predecessor[HHS220_ORDERED4X4_PARENT_GLYPHS];
static uint8_t mismatched_parent[HHS220_ORDERED4X4_PARENT_GLYPHS];
static HHS220Ordered4x4BoundExecutionV1 a,b,c;

static int run(const HHS220Ordered4x4NativeTensorBindingV1 *s,
               const HHS220Ordered4x4NativeTensorBindingV1 *v,
               HHS220Ordered4x4BoundExecutionV1 *out) {
 return hhs_exact_pass220_ordered4x4_execute_bound(
  source,HHS220_ORDERED4X4_SOURCE_BYTES,s,v,out)==HHS_EXACT_STATUS_OK;
}
int main(void) {
 HHS220Ordered4x4NativeTensorBindingV1 s,v;
 FILE *f=fopen("contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode","rb");
 size_t n;
 CHECK(f!=NULL,"source open");
 n=fread(source,1U,sizeof(source),f);
 CHECK(!ferror(f) && fclose(f)==0 && n==HHS220_ORDERED4X4_SOURCE_BYTES,"source width");
 memset(state_s,'X',sizeof(state_s));
 memset(state_v,'Y',sizeof(state_v));
 memset(predecessor,'Q',sizeof(predecessor));
 memset(mismatched_parent,'R',sizeof(mismatched_parent));
 memset(&s,0,sizeof(s));
 memset(&v,0,sizeof(v));
 s.struct_size=(uint32_t)sizeof(s); s.symbol='s'; s.cell81=4U;s.operation64=9U;
 s.state_utf8=state_s;s.state_bytes=5184U;
 s.predecessor_hash216=predecessor;s.predecessor_bytes=216U;
 v.struct_size=(uint32_t)sizeof(v); v.symbol='v';v.cell81=8U;v.operation64=17U;
 v.state_utf8=state_v;v.state_bytes=5184U;
 v.predecessor_hash216=predecessor;v.predecessor_bytes=216U;

 CHECK(run(&s,&v,&a),"bind source-locked tensor states");
 CHECK(run(&s,&v,&b),"bound graph deterministic rerun");
 CHECK(memcmp(&a,&b,sizeof(a))==0,"deterministic full bound proof witness");
 CHECK(a.source_identity_verified==1U && a.ordered_type_graph_executed==1U,"source and type graph");
 CHECK(a.deterministic_bound_graph_replay_verified==1U && a.ordered_opcodes==15U,"15 native construction operators replayed");
 CHECK(a.s_codepoints==5184U && a.v_codepoints==5184U,"5184 Unicode chars, not bytes assumption");
 CHECK(a.s_serialized_bytes==5184U && a.v_serialized_bytes==5184U,"exact ASCII fixture");
 CHECK(a.s_vm5184_address==265U && a.v_vm5184_address==529U,"typed address preserved");
 CHECK(a.native_predecessor_identity_matched==1U && a.native_binding_authenticity_verified==0U,"shape is not cryptographic authentication");
 CHECK(!a.s_value_scalarized && !a.v_value_scalarized,"no scalarization");
 CHECK(!a.matrix_times_value_derived && !a.matrix_quotient_value_derived && !a.matrix_power_value_derived,"no fake tensor evaluation");
 CHECK(!a.equation_equality_proved && !a.vm81_admission_executed,"no fake proof or VM81 execution");
 CHECK(!a.hash72_commit_authority && !a.hash216_commit_authority && !a.canonical_vm81_mutation_authority,"no commit or mutation");
 CHECK(memcmp(a.ordered_node_roots[14],a.result_root_sha256,32U)==0,"final ordered equality root");

 /* Mutating s propagates into the quotient/power side, but not v*L. */
 state_s[17]='S';
 CHECK(run(&s,&v,&c),"modified s accepted as new candidate");
 CHECK(memcmp(a.ordered_node_roots[10],c.ordered_node_roots[10],32U)!=0,"s changes power path");
 CHECK(memcmp(a.ordered_node_roots[13],c.ordered_node_roots[13],32U)==0,"s cannot modify independent v RHS branch");
 CHECK(memcmp(a.result_root_sha256,c.result_root_sha256,32U)!=0,"s changes outer ordered equality root");
 state_s[17]='X';

 /* Mutating v affects only the v-side product and outer ordered equality. */
 state_v[9]='V';
 CHECK(run(&s,&v,&c),"modified v accepted as new candidate");
 CHECK(memcmp(a.ordered_node_roots[10],c.ordered_node_roots[10],32U)==0,"v cannot modify independent LHS power");
 CHECK(memcmp(a.ordered_node_roots[13],c.ordered_node_roots[13],32U)!=0,"v changes RHS");
 CHECK(memcmp(a.result_root_sha256,c.result_root_sha256,32U)!=0,"v changes closure relation");
 state_v[9]='Y';

 /* Address is native identity, not a detached numeral. */
 s.cell81=5U;
 CHECK(run(&s,&v,&c),"new typed cell address");
 CHECK(memcmp(a.binding_roots_sha256[0],c.binding_roots_sha256[0],32U)!=0,"cell identity changes binding");
 s.cell81=4U;
 s.operation64=10U;
 CHECK(run(&s,&v,&c),"new ordered opcode address");
 CHECK(memcmp(a.binding_roots_sha256[0],c.binding_roots_sha256[0],32U)!=0,"opcode address changes binding");
 s.operation64=9U;

 /* UTF-8 represents characters, NOT byte-equivalent scalar values. */
 memmove(state_s+2U,state_s+1U,5183U);
 state_s[0]=0xCEU;state_s[1]=0x94U; /* Δ followed by 5183 X */
 s.state_bytes=5185U;
 CHECK(run(&s,&v,&c),"5184 Unicode codepoints with 5185 bytes");
 CHECK(c.s_codepoints==5184U && c.s_serialized_bytes==5185U,"Unicode counts and UTF-8 width retained");
 state_s[0]=0xC0U;
 CHECK(!run(&s,&v,&c),"overlong UTF-8 rejected");
 state_s[0]=0xCEU;state_s[1]=0x00U;
 CHECK(!run(&s,&v,&c),"embedded null/invalid continuation rejected");
 state_s[0]='X';state_s[1]='X';s.state_bytes=5184U;
 memset(state_s,'X',5184U);

 v.predecessor_hash216=mismatched_parent;
 CHECK(!run(&s,&v,&c),"mismatched VM81 predecessors rejected");
 v.predecessor_hash216=predecessor;
 s.cell81=81U;
 CHECK(!run(&s,&v,&c),"invalid VM81 cell rejected");
 s.cell81=4U;
 v.operation64=64U;
 CHECK(!run(&s,&v,&c),"invalid ordered operation address rejected");
 v.operation64=17U;
 v.symbol='s';
 CHECK(!run(&s,&v,&c),"swapped role rejected");
 v.symbol='v';
 s.state_bytes=5183U;
 CHECK(!run(&s,&v,&c),"wrong 5184 character width rejected");
 s.state_bytes=5184U;
 source[0]^=1U;
 CHECK(!run(&s,&v,&c),"source identity drift rejected");
 source[0]^=1U;
 CHECK(c.ordered_type_graph_executed==0U && c.hash72_commit_authority==0U,"rejection never mints receipt");
 puts("{\"schema\":\"HHS_PASS220_ORDERED4X4_TYPED_BOUND_HIR_V1\","
      "\"typed_5184_unicode\":true,\"bound_operand_locality\":true,"
      "\"address_provenance\":true,\"deterministic_replay\":true,"
      "\"negative_paths\":true,\"binding_authenticity_verified\":false,"
      "\"equation_proved\":false,\"matrix_values_computed\":false,"
      "\"vm81_admission\":false,\"hash72_commit\":false,\"hash216_commit\":false}");
 return 0;
}
