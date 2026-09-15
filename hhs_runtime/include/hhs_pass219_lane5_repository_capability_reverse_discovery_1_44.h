#ifndef HHS_PASS219_LANE5_REPOSITORY_CAPABILITY_REVERSE_DISCOVERY_1_44_H
#define HHS_PASS219_LANE5_REPOSITORY_CAPABILITY_REVERSE_DISCOVERY_1_44_H

#include "hhs_pass219_lane5_executable_capability_self_model_1_43.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_VERSION UINT32_C(0x0001002C)
#define HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_NAMESPACE UINT32_C(0x0002192C)
#define HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_MAX_ENTRIES UINT32_C(2048)

enum {
    HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_SOURCE_PUBLIC_REGISTRY = 1,
    HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_SOURCE_NATIVE_EXACT_ABI = 2,
    HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_SOURCE_PYTHON_OPERATION_REGISTRY = 3
};

enum {
    HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_AUTH_OBSERVATION = 1,
    HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_AUTH_GOVERNED_TRANSFORM = 2,
    HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_AUTH_CANONICAL_ADMISSION_BOUNDARY = 3,
    HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_AUTH_RESTRICTED_OR_UNAVAILABLE = 4
};

typedef struct HHSExactPass219Lane5RepositoryCapabilityAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t max_entries;
    uint8_t global_capability_discovery;
    uint8_t public_registry_snapshot;
    uint8_t native_exact_abi_snapshot;
    uint8_t python_operation_registry_snapshot;
    uint8_t structural_registry_keys_only;
    uint8_t ordered_identity;
    uint8_t dependency_topology;
    uint8_t authority_classification;
    uint8_t deterministic_replay;
    uint8_t canonical_boundary_singleton;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t auto_hash216_composition_promotion;
    uint8_t auto_superedge_promotion;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t reserved0[2];
} HHSExactPass219Lane5RepositoryCapabilityAuthorityV1;

typedef struct HHSExactPass219Lane5RepositoryCapabilityDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t total_entries;
    uint32_t public_entries;
    uint32_t native_entries;
    uint32_t python_registry_entries;
    uint32_t restricted_entries;
    uint32_t canonical_boundary_entries;
    uint64_t public_catalog_signature64;
    uint64_t native_export_signature64;
    uint64_t python_registry_signature64;
    uint64_t dependency_signature64;
    uint64_t model_signature64;
    uint64_t canonical_boundary_signature64;
    uint64_t entry_signature64[HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_MAX_ENTRIES];
    uint8_t source_kind[HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_MAX_ENTRIES];
    uint8_t authority_class[HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_MAX_ENTRIES];
    uint8_t public_registry_complete;
    uint8_t native_exact_abi_complete;
    uint8_t python_operation_registry_complete;
    uint8_t structural_registry_keys_only;
    uint8_t ordered_unique_identity;
    uint8_t candidate_only;
    uint8_t auto_hash216_composition_promotion;
    uint8_t auto_superedge_promotion;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t requires_signed_environmental_vm81_admission;
} HHSExactPass219Lane5RepositoryCapabilityDescriptorV1;

typedef struct HHSExactPass219Lane5RepositoryCapabilityReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t total_entries;
    uint32_t public_entries;
    uint32_t native_entries;
    uint32_t python_registry_entries;
    uint32_t restricted_entries;
    uint32_t canonical_boundary_entries;
    uint64_t public_catalog_signature64;
    uint64_t native_export_signature64;
    uint64_t python_registry_signature64;
    uint64_t dependency_signature64;
    uint64_t model_signature64;
    uint64_t canonical_boundary_signature64;
    uint64_t descriptor_signature64;
    uint64_t receipt_signature64;
    uint8_t accepted;
    uint8_t public_registry_complete;
    uint8_t native_exact_abi_complete;
    uint8_t python_operation_registry_complete;
    uint8_t structural_registry_keys_only;
    uint8_t ordered_unique_identity;
    uint8_t candidate_only;
    uint8_t auto_hash216_composition_promotion;
    uint8_t auto_superedge_promotion;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t pqc_key_authority;
    uint8_t receipt_clock_authority;
    uint8_t requires_signed_environmental_vm81_admission;
} HHSExactPass219Lane5RepositoryCapabilityReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_repository_capability_reverse_discovery_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_repository_capability_reverse_discovery_authority(
    HHSExactPass219Lane5RepositoryCapabilityAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_repository_capability_reverse_discovery_validate(
    const HHSExactPass219Lane5RepositoryCapabilityDescriptorV1 *descriptor,
    HHSExactPass219Lane5RepositoryCapabilityReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
