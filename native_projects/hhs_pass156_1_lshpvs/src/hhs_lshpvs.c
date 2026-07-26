#include "hhs_lshpvs.h"
#include "hhs_hash216.h"

#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DOMAIN_ENTRY "HHS-P156.1-LSHPVS-ENTRY-V1"
#define DOMAIN_STATE "HHS-P156.1-LSHPVS-STATE-V1"
#define DOMAIN_PACKAGE "HHS-P156.1-LSHPVS-TRANSITION-V1"
#define DOMAIN_CHAIN "HHS-P156.1-LSHPVS-CHAIN-V1"

#include "hhs_lshpvs_arithmetic.inc"
#include "hhs_lshpvs_matrix.inc"
#include "hhs_lshpvs_execution.inc"
#include "hhs_lshpvs_store.inc"
