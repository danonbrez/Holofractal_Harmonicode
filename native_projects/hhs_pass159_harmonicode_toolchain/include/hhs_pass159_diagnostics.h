#ifndef HHS_PASS159_DIAGNOSTICS_H
#define HHS_PASS159_DIAGNOSTICS_H
#include "hhs_pass159_types.h"
typedef enum {
    HHS159_DIAG_INFO = 1,
    HHS159_DIAG_WARNING = 2,
    HHS159_DIAG_ERROR = 3,
    HHS159_DIAG_FATAL = 4
} HHS159DiagnosticSeverity;
#endif
