#ifndef HHS_PASS219_INHERITED_PASS213_1_16_H
#define HHS_PASS219_INHERITED_PASS213_1_16_H

#include "hhs_pass219_inherited_pass214_1_16.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS213_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS213_VERSION_MINOR 16U
#define HHS_EXACT_PASS219_INHERITED_PASS213_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS213_NUMBER 213U
#define HHS_EXACT_PASS213_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS213_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS213_SHA256_HEX_LEN 64U
#define HHS_EXACT_PASS213_SHA256_HEX_STRLEN 65U
#define HHS_EXACT_PASS213_HASH72_STRLEN 73U
#define HHS_EXACT_PASS213_NATIVE_DISPATCH_ID_COUNT 9U

typedef struct HHSExactPass213ClosureWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t final_iteration;
    uint32_t implementation_complete;
    uint32_t inherited_passes_001_through_212;
    uint32_t superseded_authority_count;
    uint32_t correction_before_interpretation;
    uint32_t correction_before_execution;
    uint32_t recovery_admission_required;
    uint32_t native_protected_memory_required;
    uint32_t zeroization_before_release_required;
    uint32_t dependency_scoped_semantic_revalidation;
    uint32_t persistent_inventory_and_tombstones_required;
    uint32_t pqc_enclosure_required;
    uint32_t rfc3161_external_timestamp_required;
    uint32_t no_float_canonical_authority;
    uint32_t governed_surface_projection_only;
    uint32_t network_capability_issuance_forbidden;
    uint32_t protected_material_nonexposure_required;
    uint32_t physical_tensor_mapping_nonexposure_required;
    uint32_t singleton_vm81_admission;
    uint32_t immutable_compiled_rom_entries;
    uint32_t native_dispatch_real_c_abi_required;
    uint32_t native_dispatch_dynamic_allocation_forbidden;
    uint32_t native_dispatch_ambient_state_forbidden;
    uint32_t inherited_governed_canonical_mutation_authority;
    uint32_t pass219_new_mutation_authority;
    uint32_t pass219_cxx_mutation_authority;
    uint32_t pass219_vm81_direct_mutation_authority;
    uint32_t raw_native_dispatch_bypass_forbidden;
    uint32_t full_hydration_bits;
    uint32_t full_hydration_bytes;
    uint32_t affine_seed_bytes;
    uint32_t compressed_payload_bytes;
    uint32_t missing_shard_count;
    uint32_t moving_tensor_domain;
    uint32_t exact_lookup_iterations;
    uint32_t parametric_iterations;
    uint32_t tensor_route_iterations;
    uint32_t native_dispatch_iterations;
    uint32_t recovery_boundary_sequence;
    uint32_t dispatch_final_sequence;
    uint32_t uninterrupted_resumed_receipts_equal;
    uint32_t ledger_chains_valid;
    uint32_t performance_timings_canonical;
    uint32_t native_dispatch_id_count;
    uint32_t main_tests_passed;
    uint64_t branch_validation_run;
    uint64_t branch_validation_job;
    uint64_t main_validation_run;
    uint64_t main_validation_job;
    char final_branch_head[HHS_EXACT_PASS213_GIT_SHA_STRLEN];
    char main_merge_head[HHS_EXACT_PASS213_GIT_SHA_STRLEN];
    char branch_artifact_sha256[HHS_EXACT_PASS213_SHA256_HEX_STRLEN];
    char main_artifact_sha256[HHS_EXACT_PASS213_SHA256_HEX_STRLEN];
    char semantic_root_hash216[HHS_EXACT_PASS213_SHA256_HEX_STRLEN];
    char terminal_receipt_hash72[HHS_EXACT_PASS213_HASH72_STRLEN];
    char observation_root_hash216[HHS_EXACT_PASS213_SHA256_HEX_STRLEN];
    char pass214_gate_preservation_root_hash216[HHS_EXACT_PASS213_SHA256_HEX_STRLEN];
    char contract_git_blob[HHS_EXACT_PASS213_GIT_SHA_STRLEN];
    char final_evidence_git_blob[HHS_EXACT_PASS213_GIT_SHA_STRLEN];
    char native_dispatch_source_git_blob[HHS_EXACT_PASS213_GIT_SHA_STRLEN];
    char secure_arena_source_git_blob[HHS_EXACT_PASS213_GIT_SHA_STRLEN];
    char governed_authority_git_blob[HHS_EXACT_PASS213_GIT_SHA_STRLEN];
} HHSExactPass213ClosureWitnessV1;

typedef struct HHSExactPass219InheritedPass213BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t terminal_closure_bound;
    uint32_t compiled_rom_authority_bound;
    uint32_t correction_before_interpretation_bound;
    uint32_t protected_memory_bound;
    uint32_t pqc_timestamp_tensor_bound;
    uint32_t governed_native_dispatch_bound;
    uint32_t persistent_ledger_bound;
    uint32_t interruption_recovery_bound;
    uint32_t pass214_gate_preservation_bound;
    uint32_t inherited_governed_canonical_mutation_authority;
    uint32_t pass219_new_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_direct_mutation_authority;
    uint32_t raw_native_dispatch_bypass_forbidden;
    uint32_t native_dispatch_id_count;
    uint32_t native_dispatch_iterations;
    uint32_t recovery_boundary_sequence;
    char main_merge_head[HHS_EXACT_PASS213_GIT_SHA_STRLEN];
    char semantic_root_hash216[HHS_EXACT_PASS213_SHA256_HEX_STRLEN];
    char terminal_receipt_hash72[HHS_EXACT_PASS213_HASH72_STRLEN];
    char pass214_gate_preservation_root_hash216[HHS_EXACT_PASS213_SHA256_HEX_STRLEN];
} HHSExactPass219InheritedPass213BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass213_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass213_compiled_rom_authority(
    const HHSExactPass213ClosureWitnessV1 *witness,
    HHSExactPass219InheritedPass213BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
