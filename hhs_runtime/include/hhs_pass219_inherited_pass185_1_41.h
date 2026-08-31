#ifndef HHS_PASS219_INHERITED_PASS185_1_41_H
#define HHS_PASS219_INHERITED_PASS185_1_41_H
#include "hhs_pass219_inherited_pass186_1_40.h"
#ifdef __cplusplus
extern "C" {
#endif
#define HHS_EXACT_PASS219_INHERITED_PASS185_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS185_VERSION_MINOR 41U
#define HHS_EXACT_PASS219_INHERITED_PASS185_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS185_NUMBER 185U
#define HHS_EXACT_PASS185_I141_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS185_I141_GIT_SHA_STRLEN 41U
typedef struct HHSExactPass185CumulativeClosureWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t contract_preserved;
    uint32_t phase7_matrix_verified;
    uint32_t cumulative_local_closure_verified;
    uint32_t exact_production_entrypoint_verified;
    uint32_t browser_trace_verified;
    uint32_t zero_local_gaps;
    uint32_t zero_local_waivers;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_clock;
    uint32_t frontend_mutation_authority;
    char cumulative_validated_head[HHS_EXACT_PASS185_I141_GIT_SHA_STRLEN];
    char cumulative_receipt_blob[HHS_EXACT_PASS185_I141_GIT_SHA_STRLEN];
} HHSExactPass185CumulativeClosureWitnessV1;
typedef struct HHSExactPass219InheritedPass185BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t cumulative_local_closure_bound;
    uint32_t production_runtime_os_bound;
    uint32_t browser_trace_bound;
    uint32_t no_new_authority_bound;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_clock;
    uint32_t frontend_mutation_authority;
    char cumulative_validated_head[HHS_EXACT_PASS185_I141_GIT_SHA_STRLEN];
    char cumulative_receipt_blob[HHS_EXACT_PASS185_I141_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass185BindingV1;
HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass185_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass185_cumulative_closure(
    const HHSExactPass185CumulativeClosureWitnessV1 *witness,
    HHSExactPass219InheritedPass185BindingV1 *out_binding
);
#ifdef __cplusplus
}
#endif
#endif
