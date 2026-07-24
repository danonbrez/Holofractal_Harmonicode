#ifndef HHS_GFCC_EXACT_H
#define HHS_GFCC_EXACT_H
#include "hhs_gfcc.h"

typedef hhs_gfcc_exact hhs_gfcc_integer_or_ratio;

static inline int hhs_gfcc_exact_is_canonical(hhs_gfcc_exact value) {
    return value.denominator > 0;
}

#endif
