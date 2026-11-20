#ifndef HHS_PASS220_PTM_ORBIT_INDEX_V1_H
#define HHS_PASS220_PTM_ORBIT_INDEX_V1_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Exact integer index only. Does not evaluate HARMONICODE Ncalc tensor values. */
typedef struct HHSPtmOrbitStateV1 {
    uint64_t input;
    uint64_t offset;
    uint64_t state;
    uint64_t p;
    uint64_t q;
    uint64_t product;
} HHSPtmOrbitStateV1;
typedef int (*HHSPtmOrbitCallbackV1)(const HHSPtmOrbitStateV1 *, void *);
typedef int (*HHSPtmFactorCallbackV1)(const HHSPtmOrbitStateV1 *, int side, uint64_t prime, uint32_t exponent, void *);
/* Codes: 0 success; 1 invalid arg; 2 arithmetic overflow; 3 step bound; 4 callback rejected. */
int hhs_ptm_orbit_visit_v1(uint64_t start, uint64_t max_states, HHSPtmOrbitCallbackV1 callback, void *ctx, uint64_t *visited);
int hhs_ptm_factor_visit_v1(const HHSPtmOrbitStateV1 *state, HHSPtmFactorCallbackV1 callback, void *ctx);
int hhs_ptm_cell_address_v1(uint64_t length, uint64_t row, uint64_t col, uint64_t local_cell, uint64_t *address);
/* Invert flattened block/cell address without materializing a 3x3 block. */
int hhs_ptm_decode_cell_address_v1(uint64_t length, uint64_t address, uint64_t *row, uint64_t *col, uint64_t *local_cell);
#ifdef __cplusplus
}
#endif
#endif
