#ifndef HHS_GFCC_ERRORS_H
#define HHS_GFCC_ERRORS_H
#include "hhs_gfcc.h"

static inline int hhs_gfcc_status_is_success(hhs_gfcc_status status) {
    return status == HHS_GFCC_OK;
}

#endif
