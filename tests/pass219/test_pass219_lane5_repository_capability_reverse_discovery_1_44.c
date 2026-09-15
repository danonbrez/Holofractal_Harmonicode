#include "hhs_pass219_lane5_repository_capability_reverse_discovery_1_44.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static HHSExactPass219Lane5RepositoryCapabilityDescriptorV1 valid_descriptor(void) {
    HHSExactPass219Lane5RepositoryCapabilityDescriptorV1 value;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_VERSION;
    value.namespace_id = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_NAMESPACE;
    value.total_entries = 4U;
    value.public_entries = 1U;
    value.native_entries = 2U;
    value.python_registry_entries = 1U;
    value.restricted_entries = 0U;
    value.canonical_boundary_entries = 1U;
    value.public_catalog_signature64 = UINT64_C(101);
    value.native_export_signature64 = UINT64_C(102);
    value.python_registry_signature64 = UINT64_C(103);
    value.dependency_signature64 = UINT64_C(104);
    value.model_signature64 = UINT64_C(105);
    value.canonical_boundary_signature64 = UINT64_C(33);
    value.entry_signature64[0] = UINT64_C(11);
    value.entry_signature64[1] = UINT64_C(22);
    value.entry_signature64[2] = UINT64_C(33);
    value.entry_signature64[3] = UINT64_C(44);
    value.source_kind[0] = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_SOURCE_PUBLIC_REGISTRY;
    value.source_kind[1] = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_SOURCE_NATIVE_EXACT_ABI;
    value.source_kind[2] = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_SOURCE_NATIVE_EXACT_ABI;
    value.source_kind[3] = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_SOURCE_PYTHON_OPERATION_REGISTRY;
    value.authority_class[0] = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_AUTH_OBSERVATION;
    value.authority_class[1] = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_AUTH_GOVERNED_TRANSFORM;
    value.authority_class[2] = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_AUTH_CANONICAL_ADMISSION_BOUNDARY;
    value.authority_class[3] = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_AUTH_OBSERVATION;
    value.public_registry_complete = 1U;
    value.native_exact_abi_complete = 1U;
    value.python_operation_registry_complete = 1U;
    value.structural_registry_keys_only = 1U;
    value.ordered_unique_identity = 1U;
    value.candidate_only = 1U;
    value.requires_signed_environmental_vm81_admission = 1U;
    return value;
}

static int rejected(HHSExactPass219Lane5RepositoryCapabilityDescriptorV1 value) {
    HHSExactPass219Lane5RepositoryCapabilityReceiptV1 receipt;
    memset(&receipt, 0, sizeof(receipt));
    return hhs_exact_pass219_lane5_repository_capability_reverse_discovery_validate(
        &value, &receipt
    ) != HHS_EXACT_STATUS_OK;
}

int main(void) {
    HHSExactPass219Lane5RepositoryCapabilityAuthorityV1 authority;
    HHSExactPass219Lane5RepositoryCapabilityDescriptorV1 descriptor;
    HHSExactPass219Lane5RepositoryCapabilityReceiptV1 receipt;
    HHSExactPass219Lane5RepositoryCapabilityDescriptorV1 bad;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_repository_capability_reverse_discovery_version() ==
          HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_VERSION);
    CHECK(hhs_exact_pass219_lane5_repository_capability_reverse_discovery_authority(
              &authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.global_capability_discovery == 1U);
    CHECK(authority.public_registry_snapshot == 1U);
    CHECK(authority.native_exact_abi_snapshot == 1U);
    CHECK(authority.python_operation_registry_snapshot == 1U);
    CHECK(authority.structural_registry_keys_only == 1U);
    CHECK(authority.canonical_boundary_singleton == 1U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.auto_hash216_composition_promotion == 0U);
    CHECK(authority.auto_superedge_promotion == 0U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);

    descriptor = valid_descriptor();
    memset(&receipt, 0, sizeof(receipt));
    CHECK(hhs_exact_pass219_lane5_repository_capability_reverse_discovery_validate(
              &descriptor, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 1U);
    CHECK(receipt.total_entries == 4U);
    CHECK(receipt.public_entries == 1U);
    CHECK(receipt.native_entries == 2U);
    CHECK(receipt.python_registry_entries == 1U);
    CHECK(receipt.canonical_boundary_entries == 1U);
    CHECK(receipt.canonical_boundary_signature64 == UINT64_C(33));
    CHECK(receipt.descriptor_signature64 != 0U);
    CHECK(receipt.receipt_signature64 != 0U);
    CHECK(receipt.python_operation_registry_complete == 1U);
    CHECK(receipt.structural_registry_keys_only == 1U);
    CHECK(receipt.auto_hash216_composition_promotion == 0U);
    CHECK(receipt.auto_superedge_promotion == 0U);

    bad = descriptor;
    bad.python_registry_signature64 = 0U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.entry_signature64[3] = bad.entry_signature64[2];
    CHECK(rejected(bad));

    bad = descriptor;
    bad.entry_signature64[2] = UINT64_C(55);
    CHECK(rejected(bad));

    bad = descriptor;
    bad.source_kind[3] = 99U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.python_registry_entries = 2U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.authority_class[3] = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_AUTH_GOVERNED_TRANSFORM;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.authority_class[3] = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_AUTH_CANONICAL_ADMISSION_BOUNDARY;
    bad.canonical_boundary_entries = 2U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.source_kind[2] = HHS_EXACT_PASS219_LANE5_REPOSITORY_CAPABILITY_SOURCE_PUBLIC_REGISTRY;
    bad.public_entries = 2U;
    bad.native_entries = 1U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.auto_hash216_composition_promotion = 1U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.auto_superedge_promotion = 1U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.canonical_vm81_mutation_authority = 1U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.requires_signed_environmental_vm81_admission = 0U;
    CHECK(rejected(bad));

    printf(
        "PASS219_LANE5_REPOSITORY_CAPABILITY_REVERSE_DISCOVERY_PASS total=%u public=%u native=%u python=%u descriptor=%llu receipt=%llu\n",
        receipt.total_entries,
        receipt.public_entries,
        receipt.native_entries,
        receipt.python_registry_entries,
        (unsigned long long)receipt.descriptor_signature64,
        (unsigned long long)receipt.receipt_signature64
    );
    return 0;
}
