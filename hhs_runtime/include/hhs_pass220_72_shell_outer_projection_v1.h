#ifndef HHS_PASS220_72_SHELL_OUTER_PROJECTION_V1_H
#define HHS_PASS220_72_SHELL_OUTER_PROJECTION_V1_H
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Exact canonical projection only; not native ordered-equality proof. */
int hhs_pass220_72_shell_outer_projection(char *squared_chain_n,
 size_t numerator_cap,char *squared_chain_d,size_t denominator_cap);
#ifdef __cplusplus
}
#endif
#endif
