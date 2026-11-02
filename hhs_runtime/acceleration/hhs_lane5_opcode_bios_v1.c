#include "hhs_lane5_opcode_bios_v1.h"
#include <limits.h>
#include <string.h>
#include <stdlib.h>
static uint8_t m72(uint64_t v) { return (uint8_t)(v % UINT64_C(72)); }
int hhs_bios_bind(hhs_bios_cache *c, const hhs_bios_view *v) {
    if (!c || !v || !v->hash216_snapshot || !v->frame_snapshot || !v->generation)
        return HHS_BIOS_BAD_ARGUMENT;
    /* No copying/minting. Owner guarantees snapshots remain resident and
       immutable until invalidation; callers synchronize access. */
    c->view=*v; c->bound_generation=v->generation; c->bound=1;
    return HHS_BIOS_OK;
}
static int ready(const hhs_bios_cache *c, uint64_t generation) {
    return c && c->bound && c->bound_generation == generation &&
           c->view.generation == generation &&
           c->view.hash216_snapshot && c->view.frame_snapshot;
}
int hhs_bios_read216(const hhs_bios_cache *c, uint64_t g,
                     uint16_t offset, uint8_t *value) {
    if (!value || offset >= HHS_BIOS_HASH216_BYTES) return HHS_BIOS_BAD_ARGUMENT;
    if (!ready(c,g)) return HHS_BIOS_STALE;
    *value=c->view.hash216_snapshot[offset]; return HHS_BIOS_OK;
}
int hhs_bios_read_frame(const hhs_bios_cache *c, uint64_t g,
                        uint16_t offset, uint8_t *value) {
    if (!value || offset >= HHS_BIOS_FRAME_BYTES) return HHS_BIOS_BAD_ARGUMENT;
    if (!ready(c,g)) return HHS_BIOS_STALE;
    *value=c->view.frame_snapshot[offset]; return HHS_BIOS_OK;
}
void hhs_bios_invalidate(hhs_bios_cache *c) {
    if (c) memset(c,0,sizeof(*c));
}
/* Ordered phase anchors are a diagnostic/candidate projection only. The
 * authoritative phase constructor in the C++ cell wall must validate results. */
static uint8_t phase_anchor(uint8_t basis) {
    static const uint8_t a[8]={18,54,18,54,0,36,0,36};
    return a[basis];
}
static int compute(const hhs_bios_instruction *in, hhs_bios_result *r) {
    memset(r,0,sizeof(*r));
    switch(in->opcode) {
    case HHS_BIOS_COPY: r->value=in->left; break;
    case HHS_BIOS_ADD_U64:
        if (UINT64_MAX-in->left < in->right) return HHS_BIOS_OVERFLOW;
        r->value=in->left+in->right; break;
    case HHS_BIOS_SUB_U64:
        if(in->left<in->right) return HHS_BIOS_OVERFLOW;
        r->value=in->left-in->right; break;
    case HHS_BIOS_XOR_U64: r->value=in->left^in->right; break;
    case HHS_BIOS_MOD72: r->value=m72(in->left); break;
    case HHS_BIOS_PHASE_PAIR: {
        if(in->left_basis>=8 || in->right_basis>=8)
            return HHS_BIOS_BAD_ARGUMENT;
        uint8_t l=in->left_basis, b=in->right_basis;
        uint8_t p=(uint8_t)((phase_anchor(l)+phase_anchor(b))%72u);
        if((l==0 && b==1)||(l==2 && b==3)) {p=0;r->orientation=1;}
        if((l==1 && b==0)||(l==3 && b==2)) {p=36;r->orientation=2;}
        r->phase=p;r->closure=(uint8_t)(p==0 || p==36);
        r->value=p;break;
    }
    default: return HHS_BIOS_BAD_OPCODE;
    }
    return HHS_BIOS_OK;
}
int hhs_bios_dispatch(const hhs_bios_cache *c, uint64_t g,
                      const hhs_bios_instruction *ops, size_t n,
                      hhs_bios_result *out) {
    if (!ready(c,g)) return HHS_BIOS_STALE;
    if (!ops || !out || n==0 || n>65536u) return HHS_BIOS_BAD_ARGUMENT;
    if(n>SIZE_MAX/sizeof(*out)) return HHS_BIOS_BAD_ARGUMENT;
    /* Fail atomically: no partial result buffers on invalid operations. */
    hhs_bios_result *tmp=(hhs_bios_result *)malloc(n*sizeof(*tmp));
    if(!tmp) return HHS_BIOS_BAD_ARGUMENT;
    int status=HHS_BIOS_OK;
    for(size_t i=0;i<n;i++) {
        if(ops[i].reserved) {status=HHS_BIOS_BAD_ARGUMENT;break;}
        status=compute(&ops[i],&tmp[i]);
        if(status!=HHS_BIOS_OK) break;
    }
    if(status==HHS_BIOS_OK) memcpy(out,tmp,n*sizeof(*tmp));
    free(tmp);
    return status;
}
