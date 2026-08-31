#ifndef HHS_PASS219_INHERITED_PASS183_1_43_H
#define HHS_PASS219_INHERITED_PASS183_1_43_H

#include "hhs_pass219_inherited_pass184_1_42.h"
#include "../../native_projects/hhs_pass183_probability_hydration/include/hhs_p183.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS183_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS183_VERSION_MINOR 43U
#define HHS_EXACT_PASS219_INHERITED_PASS183_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS183_NUMBER 183U
#define HHS_EXACT_PASS183_I143_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS183_I143_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass183ProbabilityHydrationWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t historical_contract_preserved;
    uint32_t historical_implementation_preserved;
    uint32_t historical_ci_green;
    uint32_t exact_probability_runtime_bound;
    uint32_t factorial72_reciprocal_bound;
    uint32_t membrane_boundary_bound;
    uint32_t typed_zero_bypass_bound;
    uint32_t global_modulus_bound;
    uint32_t singleton_vm81_bound;
    uint32_t canonical_hash72_after_vm81_bound;
    uint32_t hash216_archive_after_hash72_bound;
    uint32_t deterministic_replay_bound;
    uint32_t runtime_os_gui_bound;
    uint32_t legacy_native_hash_witness_noncanonical;
    uint32_t native_hash72_authority;
    uint32_t native_hash216_authority;
    uint32_t hash216_precommit_authority;
    uint32_t independent_vm81_authority;
    uint32_t floating_point_canonical_authority;
    uint32_t pass184_successor_preserved;
    char implementation_commit[HHS_EXACT_PASS183_I143_GIT_SHA_STRLEN];
    char historical_green_head[HHS_EXACT_PASS183_I143_GIT_SHA_STRLEN];
    char frozen_i142_commit[HHS_EXACT_PASS183_I143_GIT_SHA_STRLEN];
    char i142_validation_receipt_blob[HHS_EXACT_PASS183_I143_GIT_SHA_STRLEN];
} HHSExactPass183ProbabilityHydrationWitnessV1;

typedef struct HHSExactPass219InheritedPass183BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t exact_probability_runtime_bound;
    uint32_t singleton_vm81_bound;
    uint32_t canonical_hash72_receipt_bound;
    uint32_t hash216_archival_only_bound;
    uint32_t deterministic_replay_bound;
    uint32_t runtime_os_gui_bound;
    uint32_t legacy_native_hash_witness_noncanonical;
    uint32_t no_new_authority_bound;
    uint32_t native_hash72_authority;
    uint32_t native_hash216_authority;
    uint32_t hash216_precommit_authority;
    uint32_t independent_vm81_authority;
    uint32_t floating_point_canonical_authority;
    char implementation_commit[HHS_EXACT_PASS183_I143_GIT_SHA_STRLEN];
    char frozen_i142_commit[HHS_EXACT_PASS183_I143_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass183BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass183_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass183_probability_hydration(
    const HHSExactPass183ProbabilityHydrationWitnessV1 *witness,
    HHSExactPass219InheritedPass183BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif
#endif
