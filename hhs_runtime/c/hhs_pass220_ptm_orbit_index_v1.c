#include "hhs_pass220_ptm_orbit_index_v1.h"
#include <stdint.h>
#include <limits.h>

static int safe_mul(uint64_t a,uint64_t b,uint64_t *out) {
    if (b && a>UINT64_MAX/b) return 0;
    *out=a*b;return 1;
}
int hhs_ptm_orbit_visit_v1(uint64_t start, uint64_t max_states, HHSPtmOrbitCallbackV1 callback, void *ctx, uint64_t *visited) {
    uint64_t n=start,i;
    if (visited) *visited=0;
    if (!start || !max_states || !callback || !visited) return 1;
    for (i=0;i<max_states;i++) {
        HHSPtmOrbitStateV1 v;
        if (n==UINT64_MAX) return 2;
        v.input=start;v.offset=i;v.state=n;v.p=n-1;v.q=n+1;
        if (!safe_mul(v.p,v.q,&v.product)) return 2;
        if (callback(&v,ctx)!=0) return 4;
        ++*visited;
        if (n==1) return 0;
        if (n%2==0) n/=2;
        else {
            if (n>(UINT64_MAX-1)/3) return 2;
            n=3*n+1;
        }
    }
    return 3;
}
int hhs_ptm_factor_visit_v1(const HHSPtmOrbitStateV1 *state, HHSPtmFactorCallbackV1 callback, void *ctx) {
    int side;
    if (!state || !callback) return 1;
    for (side=0;side<2;side++) {
        uint64_t n=side==0?state->p:state->q;
        uint64_t divisor=2;
        while (divisor<=n/divisor) {
            uint32_t exp=0;
            while (n%divisor==0) {n/=divisor;exp++;}
            if (exp && callback(state,side,divisor,exp,ctx)) return 4;
            divisor=divisor==2?3:divisor+2;
        }
        if (n>1 && callback(state,side,n,1,ctx)) return 4;
    }
    return 0;
}
int hhs_ptm_cell_address_v1(uint64_t length, uint64_t row, uint64_t col, uint64_t local_cell, uint64_t *address) {
    uint64_t block;
    if (!address || !length || row>=length || col>=length || local_cell>=9) return 1;
    if (!safe_mul(row,length,&block) || block>UINT64_MAX-col) return 2;
    block+=col;
    if (block>(UINT64_MAX-local_cell)/9) return 2;
    *address=9*block+local_cell;
    return 0;
}

int hhs_ptm_decode_cell_address_v1(uint64_t length, uint64_t address, uint64_t *row, uint64_t *col, uint64_t *local_cell) {
    uint64_t blocks,total,block;
    if (!row || !col || !local_cell || !length) return 1;
    if (!safe_mul(length,length,&blocks) || !safe_mul(blocks,UINT64_C(9),&total)) return 2;
    if (address>=total) return 1;
    block=address/UINT64_C(9);
    *row=block/length;
    *col=block%length;
    *local_cell=address%UINT64_C(9);
    return 0;
}
