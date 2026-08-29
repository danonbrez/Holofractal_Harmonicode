#ifndef HHS_PASS219_INHERITED_PASS186_1_40_H
#define HHS_PASS219_INHERITED_PASS186_1_40_H

#include "hhs_pass219_inherited_pass187_1_39.h"
#include "../../native_projects/hhs_pass186_x64_vm81_q144/include/hhs_pass186_x64_vm81_q144_abi.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS186_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS186_VERSION_MINOR 40U
#define HHS_EXACT_PASS219_INHERITED_PASS186_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS186_NUMBER 186U
#define HHS_EXACT_PASS186_I140_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass186CumulativeAuthorityWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t contract_preserved;
    uint32_t implementation_commit_preserved;
    uint32_t exact_q144_verified;
    uint32_t factorial7_boundary_verified;
    uint32_t vm81_crosswalk_verified;
    uint32_t hydrated_roundtrip_states;
    uint32_t ordered_noncommutative_identity_verified;
    uint32_t x86_64_register_probe_verified;
    uint32_t no_float_disassembly_verified;
    uint32_t pass187_successor_preserved;
    uint32_t independent_opcode_authority;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_clock;
    uint32_t float_canonical_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;

    char pass186_implementation_commit[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN];
    char frozen_i139_commit[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN];
    char contract_blob[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN];
    char receipt_blob[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN];
    char makefile_blob[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN];
    char abi_header_blob[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN];
    char abi_source_blob[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN];
    char register_probe_blob[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN];
    char smoke_test_blob[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN];
    char frozen_pass187_header_blob[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN];
} HHSExactPass186CumulativeAuthorityWitnessV1;

typedef struct HHSExactPass219InheritedPass186BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t historical_abi_bound;
    uint32_t exact_q144_bound;
    uint32_t factorial7_boundary_bound;
    uint32_t vm81_crosswalk_bound;
    uint32_t hydrated_projection_bound;
    uint32_t hydrated_roundtrip_states;
    uint32_t ordered_noncommutative_identity_bound;
    uint32_t x86_64_register_mapping_bound;
    uint32_t no_float_canonical_bound;
    uint32_t pass187_successor_bound;
    uint32_t no_new_authority_bound;
    uint32_t independent_opcode_authority;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_clock;
    uint32_t float_is_canonical_authority;
    uint32_t pass219_new_candidate_authority;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t pass219_new_persistence_authority;
    uint32_t pass219_new_hash72_clock;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char pass186_implementation_commit[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN];
    char frozen_i139_commit[HHS_EXACT_PASS186_I140_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass186BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass186_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass186_cumulative_authority(
    const HHSExactPass186CumulativeAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass186BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
