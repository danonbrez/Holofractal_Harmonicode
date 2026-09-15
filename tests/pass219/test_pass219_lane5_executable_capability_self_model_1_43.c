#include "hhs_pass219_lane5_executable_capability_self_model_1_43.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static HHSExactPass219Lane5CapabilitySelfModelDescriptorV1 valid_descriptor(void) {
    HHSExactPass219Lane5CapabilitySelfModelDescriptorV1 value;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_VERSION;
    value.namespace_id = HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_NAMESPACE;
    value.total_entries = 3U;
    value.public_entries = 1U;
    value.native_entries = 2U;
    value.restricted_entries = 0U;
    value.canonical_boundary_entries = 1U;
    value.public_catalog_signature64 = UINT64_C(101);
    value.native_export_signature64 = UINT64_C(102);
    value.dependency_signature64 = UINT64_C(103);
    value.model_signature64 = UINT64_C(104);
    value.canonical_boundary_signature64 = UINT64_C(33);
    value.entry_signature64[0] = UINT64_C(11);
    value.entry_signature64[1] = UINT64_C(22);
    value.entry_signature64[2] = UINT64_C(33);
    value.source_kind[0] = HHS_EXACT_PASS219_LANE5_CAPABILITY_SOURCE_PUBLIC_REGISTRY;
    value.source_kind[1] = HHS_EXACT_PASS219_LANE5_CAPABILITY_SOURCE_NATIVE_EXACT_ABI;
    value.source_kind[2] = HHS_EXACT_PASS219_LANE5_CAPABILITY_SOURCE_NATIVE_EXACT_ABI;
    value.authority_class[0] = HHS_EXACT_PASS219_LANE5_CAPABILITY_AUTH_OBSERVATION;
    value.authority_class[1] = HHS_EXACT_PASS219_LANE5_CAPABILITY_AUTH_GOVERNED_TRANSFORM;
    value.authority_class[2] = HHS_EXACT_PASS219_LANE5_CAPABILITY_AUTH_CANONICAL_ADMISSION_BOUNDARY;
    value.public_registry_complete = 1U;
    value.native_exact_abi_complete = 1U;
    value.ordered_unique_identity = 1U;
    value.candidate_only = 1U;
    value.requires_signed_environmental_vm81_admission = 1U;
    return value;
}

static int rejected(HHSExactPass219Lane5CapabilitySelfModelDescriptorV1 value) {
    HHSExactPass219Lane5CapabilitySelfModelReceiptV1 receipt;
    memset(&receipt, 0, sizeof(receipt));
    return hhs_exact_pass219_lane5_capability_self_model_validate(&value, &receipt) != HHS_EXACT_STATUS_OK;
}

int main(void) {
    HHSExactPass219Lane5CapabilitySelfModelAuthorityV1 authority;
    HHSExactPass219Lane5CapabilitySelfModelDescriptorV1 descriptor;
    HHSExactPass219Lane5CapabilitySelfModelReceiptV1 receipt;
    HHSExactPass219Lane5CapabilitySelfModelDescriptorV1 bad;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_capability_self_model_version() ==
          HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_VERSION);
    CHECK(hhs_exact_pass219_lane5_capability_self_model_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.global_capability_discovery == 1U);
    CHECK(authority.public_registry_snapshot == 1U);
    CHECK(authority.native_exact_abi_snapshot == 1U);
    CHECK(authority.canonical_boundary_singleton == 1U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);

    descriptor = valid_descriptor();
    memset(&receipt, 0, sizeof(receipt));
    CHECK(hhs_exact_pass219_lane5_capability_self_model_validate(&descriptor, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 1U);
    CHECK(receipt.total_entries == 3U);
    CHECK(receipt.public_entries == 1U);
    CHECK(receipt.native_entries == 2U);
    CHECK(receipt.canonical_boundary_entries == 1U);
    CHECK(receipt.canonical_boundary_signature64 == UINT64_C(33));
    CHECK(receipt.descriptor_signature64 != 0U);
    CHECK(receipt.receipt_signature64 != 0U);
    CHECK(receipt.candidate_only == 1U);
    CHECK(receipt.canonical_vm81_mutation_authority == 0U);
    CHECK(receipt.canonical_persistence_authority == 0U);
    CHECK(receipt.requires_signed_environmental_vm81_admission == 1U);

    bad = descriptor;
    bad.entry_signature64[1] = 0U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.entry_signature64[1] = bad.entry_signature64[0];
    CHECK(rejected(bad));

    bad = descriptor;
    bad.entry_signature64[1] = UINT64_C(44);
    CHECK(rejected(bad));

    bad = descriptor;
    bad.source_kind[0] = 99U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.authority_class[0] = 99U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.public_entries = 2U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.model_signature64 = 0U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.dependency_signature64 = 0U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.authority_class[2] = HHS_EXACT_PASS219_LANE5_CAPABILITY_AUTH_GOVERNED_TRANSFORM;
    bad.canonical_boundary_entries = 0U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.authority_class[1] = HHS_EXACT_PASS219_LANE5_CAPABILITY_AUTH_CANONICAL_ADMISSION_BOUNDARY;
    bad.canonical_boundary_entries = 2U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.canonical_boundary_signature64 = UINT64_C(22);
    CHECK(rejected(bad));

    bad = descriptor;
    bad.canonical_vm81_mutation_authority = 1U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.canonical_persistence_authority = 1U;
    CHECK(rejected(bad));

    bad = descriptor;
    bad.requires_signed_environmental_vm81_admission = 0U;
    CHECK(rejected(bad));

    printf(
        "PASS219_LANE5_CAPABILITY_SELF_MODEL_PASS total=%u public=%u native=%u descriptor=%llu receipt=%llu\n",
        receipt.total_entries,
        receipt.public_entries,
        receipt.native_entries,
        (unsigned long long)receipt.descriptor_signature64,
        (unsigned long long)receipt.receipt_signature64
    );
    return 0;
}
