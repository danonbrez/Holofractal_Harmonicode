#ifndef HHS_PASS159_IR_H
#define HHS_PASS159_IR_H
#include "hhs_pass159_types.h"
typedef enum {
    HHS159_IR_TOKENS = 1,
    HHS159_IR_HIR = 2,
    HHS159_IR_VMIR = 3,
    HHS159_IR_ASSEMBLY = 4,
    HHS159_IR_TRACE = 5
} HHS159IRStage;
#endif
