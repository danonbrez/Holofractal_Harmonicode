#ifndef HHS_PASS168_PARAMETER_CIRCUIT_1_0_C_FORWARD_H
#define HHS_PASS168_PARAMETER_CIRCUIT_1_0_C_FORWARD_H

/*
 * Standalone-ABI compatibility forwarding header.
 *
 * Historical consumers compile hhs_runtime/c/hhs_runtime_abi.c with only
 * -Ihhs_runtime/c.  Pass168's public declaration remains authoritative under
 * hhs_runtime/include; this forwarding header preserves that historical
 * compile contract without duplicating declarations or changing ABI surface.
 */
#include "../include/hhs_pass168_parameter_circuit_1_0.h"

#endif
