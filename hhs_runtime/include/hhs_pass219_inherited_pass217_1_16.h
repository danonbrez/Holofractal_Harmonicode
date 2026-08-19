#ifndef HHS_PASS219_INHERITED_PASS217_1_16_H
#define HHS_PASS219_INHERITED_PASS217_1_16_H

#include "hhs_pass219_inherited_pass218_1_16.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS217_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS217_VERSION_MINOR 16U
#define HHS_EXACT_PASS219_INHERITED_PASS217_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS217_NUMBER 217U
#define HHS_EXACT_PASS217_REQUIRED_AUTHORITY_COUNT 25U
#define HHS_EXACT_PASS217_PUBLISHED_ROUTE_COUNT 3U
#define HHS_EXACT_PASS217_API_ROUTE_COUNT 24U
#define HHS_EXACT_PASS217_BYPASS_OMISSION_COUNT 25U
#define HHS_EXACT_PASS217_HASH72_SYMBOL_COUNT 72U
#define HHS_EXACT_PASS217_HASH72_MATRIX_POSITIONS 5184U
#define HHS_EXACT_PASS217_WRAPPED_DIRECTION_COUNT 4U
#define HHS_EXACT_PASS217_SHA256_HEX_LEN 64U
#define HHS_EXACT_PASS217_SHA256_HEX_STRLEN 65U
#define HHS_EXACT_PASS217_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS217_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass217CumulativeClosureWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t required_authority_count;
    uint32_t published_route_count;
    uint32_t pass042_api_route_count;
    uint32_t bypass_omission_count;
    uint32_t hash72_symbol_count;
    uint32_t hash72_matrix_positions;
    uint32_t wrapped_direction_count;
    uint32_t cumulative_closure_admitted;
    uint32_t global_surface_publication_complete;
    uint32_t required_authority_bypass_matrix_complete;
    uint32_t authority_profile_coverage_equal;
    uint32_t incremental_tokenization_active_path_proven;
    uint32_t structural_closure_hardening_complete;
    uint32_t universal_utilization_reachability_complete;
    uint32_t synthetic_bypass_fixtures_are_runtime_evidence;
    uint32_t optional_profile_classes_promoted_to_core;
    uint32_t experimental_profile_classes_promoted_to_core;
    uint32_t floating_point_authority;
    uint32_t i4_hash72_manifold_validated;
    uint32_t i4_immutable_nucleus_validated;
    uint32_t i4_canonical_authority_promoted;
    uint32_t i4_runtime_mutation_performed;
    char closure_root_hash72[HHS_EXACT_HASH72_STRLEN];
    char i4_candidate_sha256[HHS_EXACT_PASS217_SHA256_HEX_STRLEN];
    char i4_address_map_sha256[HHS_EXACT_PASS217_SHA256_HEX_STRLEN];
    char i4_hash72_matrix_root_sha256[HHS_EXACT_PASS217_SHA256_HEX_STRLEN];
    char i4_hash72_manifold_root_sha256[HHS_EXACT_PASS217_SHA256_HEX_STRLEN];
    char i4_nucleus_identity_root_sha256[HHS_EXACT_PASS217_SHA256_HEX_STRLEN];
    char i4_nucleus_support_root_sha256[HHS_EXACT_PASS217_SHA256_HEX_STRLEN];
    char i4_record_root_sha256[HHS_EXACT_PASS217_SHA256_HEX_STRLEN];
    char checkpoint15_git_sha[HHS_EXACT_PASS217_GIT_SHA_STRLEN];
    char integration_git_sha[HHS_EXACT_PASS217_GIT_SHA_STRLEN];
} HHSExactPass217CumulativeClosureWitnessV1;

typedef struct HHSExactPass219InheritedPass217BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t required_authority_count;
    uint32_t published_route_count;
    uint32_t bypass_omission_count;
    uint32_t cumulative_closure_bound;
    uint32_t all_required_authorities_nonbypassable;
    uint32_t canonical_execution_reachable;
    uint32_t hash72_manifold_bound;
    uint32_t immutable_nucleus_bound;
    uint32_t exact_incremental_tokenization_bound;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint32_t genesis_rom_promotion_claimed;
    char closure_root_hash72[HHS_EXACT_HASH72_STRLEN];
    char i4_hash72_manifold_root_sha256[HHS_EXACT_PASS217_SHA256_HEX_STRLEN];
    char i4_nucleus_identity_root_sha256[HHS_EXACT_PASS217_SHA256_HEX_STRLEN];
    char checkpoint15_git_sha[HHS_EXACT_PASS217_GIT_SHA_STRLEN];
    char integration_git_sha[HHS_EXACT_PASS217_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass217BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass217_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass217_cumulative_closure(
    const HHSExactPass217CumulativeClosureWitnessV1 *witness,
    HHSExactPass219InheritedPass217BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
