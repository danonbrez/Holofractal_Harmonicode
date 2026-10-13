#ifndef HHS_PASS220_I086_LANE5_CONWAY_CELL_WALL_V1_H
#define HHS_PASS220_I086_LANE5_CONWAY_CELL_WALL_V1_H

#include "hhs_pass219_vm81_pqc_firewall_1_30.h"

#ifdef __cplusplus
extern "C" {
#endif

/* 81 bytes, row-major, each 0 or 1. Caller supplies a valid existing
 * Pass 219 UQCEL membrane input. This is candidate evolution only.
 * Failure leaves next81 unchanged; in-place buffers are supported.
 */
HHS_EXACT_API HHSExactStatus hhs_pass220_i086_lane5_conway81_cell_wall(
    const HHSExactUQCELInputV1* input,
    const unsigned char* occupancy81,
    unsigned char* next81
) 
#ifdef __cplusplus
noexcept
#endif
;

#ifdef __cplusplus
}
#endif
#endif
