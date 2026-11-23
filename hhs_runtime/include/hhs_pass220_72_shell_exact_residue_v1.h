#ifndef HHS_PASS220_72_SHELL_EXACT_RESIDUE_V1_H
#define HHS_PASS220_72_SHELL_EXACT_RESIDUE_V1_H
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Produces the exact reduced rational modular residue. No native admission. */
int hhs_pass220_72_shell_exact_residue(char *numerator, size_t numerator_capacity,
                                      char *denominator, size_t denominator_capacity);
#ifdef __cplusplus
}
#endif
#endif
