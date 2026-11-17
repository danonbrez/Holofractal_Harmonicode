#include "hhs_pass220_ptm_orbit_index_v1.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

typedef struct Counters { uint64_t length; uint64_t final; uint64_t transitions; uint64_t factor_occurrences; uint64_t target; } Counters;
static int on_factor(const HHSPtmOrbitStateV1 *state,int side,uint64_t prime,uint32_t exponent,void *ctx) {
    Counters *c=ctx; (void)state;(void)side;
    if (prime<2 || exponent==0) return 1;
    c->factor_occurrences++;
    return 0;
}
static int on_state(const HHSPtmOrbitStateV1 *state,void *ctx) {
    Counters *c=ctx;
    if (state->offset!=c->length || state->product!=state->p*state->q) return 1;
    if (state->state>1 && state->state*state->state-state->product!=1) return 1;
    if (state->state==1 && state->product!=0) return 1;
    if (hhs_ptm_factor_visit_v1(state,on_factor,ctx)!=0) return 1;
    c->length++;c->final=state->state;
    return 0;
}
static int reject_state(const HHSPtmOrbitStateV1 *state,void *ctx) {(void)state;(void)ctx;return 1;}
static int accept_state(const HHSPtmOrbitStateV1 *state,void *ctx) {(void)state;(void)ctx;return 0;}
int main(void) {
    const uint64_t starts[3]={9041,9042,9043};
    const uint64_t expected_factors[3]={829,828,831};
    uint64_t i, visited,addr;
    for(i=0;i<3;i++) {
        Counters c={0};int rc=hhs_ptm_orbit_visit_v1(starts[i],1000,on_state,&c,&visited);
        if(rc || visited!=185 || c.length!=185 || c.final!=1 || c.factor_occurrences!=expected_factors[i]) {fprintf(stderr,"orbit failure %" PRIu64 " rc=%d count=%" PRIu64 "\n",starts[i],rc,visited);return 1;}
        printf("start=%" PRIu64 " length=%" PRIu64 " prime_occurrences=%" PRIu64 "\n", starts[i],visited,c.factor_occurrences);
    }
    if(hhs_ptm_cell_address_v1(185,184,184,8,&addr) || addr!=308024) return 2;
    if(hhs_ptm_cell_address_v1(185,185,0,0,&addr)!=1) return 3;
    if(hhs_ptm_orbit_visit_v1(3,1,reject_state,NULL,&visited)!=4) return 4;
    if(hhs_ptm_orbit_visit_v1((UINT64_MAX-1)/3+1,2,accept_state,NULL,&visited)!=2) return 5;
    puts("PASS: exact orbit/product/factor callback and 3x3 address checks");
    return 0;
}
