#include "hhs_pass220_72_shell_gate_graph_v1.h"
#include <stdio.h>
#include <string.h>
static const uint8_t s[]="(x^4/(Mod(72^72,Factorial(72))/(Mod(Factorial(72),72^72)))^(-0.2752680919)==(x^2+1)^2/x^3==b==1/b^3)^2/(c^2-a^2)==a^4/b^2";
int main(void) {
 HHS72GateGraph g;
 uint8_t bad[sizeof(s)-1U];
 const uint32_t expected_offsets[4]={74U,89U,92U,112U};
 if(!hhs_pass220_72_shell_build_gate_graph(s,sizeof(s)-1U,&g)) return 1;
 if(g.edge_count!=4U||g.proved_count||g.admitted) return 2;
 for(size_t i=0U;i<4U;++i){
  if(g.edges[i].source_offset!=expected_offsets[i]||g.edges[i].proved) return 3;
  if(i<3U&&(g.edges[i].kind!=HHS_72_GATE_ORDERED_RELATION||
             g.edges[i].left_node!=i||g.edges[i].right_node!=i+1U)) return 4;
 }
 if(g.edges[3].kind!=HHS_72_GATE_SQUARED_OUTER_RELATION||
    g.edges[3].left_node!=4U||g.edges[3].right_node!=5U) return 5;
 if(g.outer_left.byte_end!=112U||g.outer_right.byte_start!=114U) return 6;
 memcpy(bad,s,sizeof(bad));bad[92]^=1U;
 if(hhs_pass220_72_shell_build_gate_graph(bad,sizeof(bad),&g)) return 7;
 if(g.edge_count||g.proved_count||g.admitted) return 8;
 puts("PASS 3 inner ordered edges + distinct squared outer edge, fail-closed");
 return 0;
}
