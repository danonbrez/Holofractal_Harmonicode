#include "../include/hhs_pass219_lane5_executable_capability_self_model_1_43.h"

#include <string.h>

static uint64_t hhs_lane5_capability_self_model_mix_u64(uint64_t hash, uint64_t value) {
    unsigned shift;
    for (shift = 0U; shift < 64U; shift += 8U) {
        hash ^= (value >> shift) & UINT64_C(0xff);
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

uint32_t hhs_exact_pass219_lane5_capability_self_model_version(void) {
    return HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_capability_self_model_authority(
    HHSExactPass219Lane5CapabilitySelfModelAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5CapabilitySelfModelAuthorityV1 authority;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(&authority, 0, sizeof(authority));
    authority.struct_size = (uint32_t)sizeof(authority);
    authority.version = HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_VERSION;
    authority.namespace_id = HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_NAMESPACE;
    authority.max_entries = HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_MAX_ENTRIES;
    authority.global_capability_discovery = 1U;
    authority.public_registry_snapshot = 1U;
    authority.native_exact_abi_snapshot = 1U;
    authority.ordered_identity = 1U;
    authority.dependency_topology = 1U;
    authority.authority_classification = 1U;
    authority.deterministic_replay = 1U;
    authority.canonical_boundary_singleton = 1U;
    authority.candidate_only = 1U;
    authority.exact_integer_only = 1U;
    authority.canonical_vm81_mutation_authority = 0U;
    authority.canonical_hash72_authority = 0U;
    authority.canonical_hash216_authority = 0U;
    authority.canonical_persistence_authority = 0U;
    authority.pqc_key_authority = 0U;
    authority.receipt_clock_authority = 0U;
    authority.floating_point_canonical_authority = 0U;
    authority.requires_signed_environmental_vm81_admission = 1U;
    *out_authority = authority;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_capability_self_model_validate(
    const HHSExactPass219Lane5CapabilitySelfModelDescriptorV1 *descriptor,
    HHSExactPass219Lane5CapabilitySelfModelReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5CapabilitySelfModelReceiptV1 receipt;
    uint64_t descriptor_signature = UINT64_C(1469598103934665603);
    uint64_t receipt_signature = UINT64_C(1469598103934665603);
    uint32_t public_entries = 0U;
    uint32_t native_entries = 0U;
    uint32_t restricted_entries = 0U;
    uint32_t boundary_entries = 0U;
    uint64_t boundary_signature = 0U;
    uint64_t previous_signature = 0U;
    uint32_t i;

    if (out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_receipt, 0, sizeof(*out_receipt));

    if (descriptor == NULL ||
        descriptor->struct_size != (uint32_t)sizeof(*descriptor) ||
        descriptor->version != HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_VERSION ||
        descriptor->namespace_id != HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_NAMESPACE ||
        descriptor->total_entries == 0U ||
        descriptor->total_entries > HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_MAX_ENTRIES ||
        descriptor->public_catalog_signature64 == 0U ||
        descriptor->native_export_signature64 == 0U ||
        descriptor->dependency_signature64 == 0U ||
        descriptor->model_signature64 == 0U ||
        descriptor->canonical_boundary_signature64 == 0U ||
        descriptor->public_registry_complete != 1U ||
        descriptor->native_exact_abi_complete != 1U ||
        descriptor->ordered_unique_identity != 1U ||
        descriptor->candidate_only != 1U ||
        descriptor->canonical_vm81_mutation_authority != 0U ||
        descriptor->canonical_hash72_authority != 0U ||
        descriptor->canonical_hash216_authority != 0U ||
        descriptor->canonical_persistence_authority != 0U ||
        descriptor->pqc_key_authority != 0U ||
        descriptor->receipt_clock_authority != 0U ||
        descriptor->floating_point_canonical_authority != 0U ||
        descriptor->requires_signed_environmental_vm81_admission != 1U) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }

    for (i = 0U; i < descriptor->total_entries; ++i) {
        const uint64_t entry_signature = descriptor->entry_signature64[i];
        const uint8_t source_kind = descriptor->source_kind[i];
        const uint8_t authority_class = descriptor->authority_class[i];

        if (entry_signature == 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (i > 0U && entry_signature <= previous_signature)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        previous_signature = entry_signature;

        if (source_kind == HHS_EXACT_PASS219_LANE5_CAPABILITY_SOURCE_PUBLIC_REGISTRY) {
            ++public_entries;
        } else if (source_kind == HHS_EXACT_PASS219_LANE5_CAPABILITY_SOURCE_NATIVE_EXACT_ABI) {
            ++native_entries;
        } else {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        if (authority_class < HHS_EXACT_PASS219_LANE5_CAPABILITY_AUTH_OBSERVATION ||
            authority_class > HHS_EXACT_PASS219_LANE5_CAPABILITY_AUTH_RESTRICTED_OR_UNAVAILABLE) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        if (authority_class == HHS_EXACT_PASS219_LANE5_CAPABILITY_AUTH_RESTRICTED_OR_UNAVAILABLE)
            ++restricted_entries;
        if (authority_class == HHS_EXACT_PASS219_LANE5_CAPABILITY_AUTH_CANONICAL_ADMISSION_BOUNDARY) {
            ++boundary_entries;
            boundary_signature = entry_signature;
        }

        descriptor_signature = hhs_lane5_capability_self_model_mix_u64(
            descriptor_signature, entry_signature);
        descriptor_signature = hhs_lane5_capability_self_model_mix_u64(
            descriptor_signature, (uint64_t)source_kind);
        descriptor_signature = hhs_lane5_capability_self_model_mix_u64(
            descriptor_signature, (uint64_t)authority_class);
    }

    if (public_entries != descriptor->public_entries ||
        native_entries != descriptor->native_entries ||
        restricted_entries != descriptor->restricted_entries ||
        boundary_entries != descriptor->canonical_boundary_entries ||
        boundary_entries != 1U ||
        boundary_signature != descriptor->canonical_boundary_signature64) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    descriptor_signature = hhs_lane5_capability_self_model_mix_u64(
        descriptor_signature, descriptor->public_catalog_signature64);
    descriptor_signature = hhs_lane5_capability_self_model_mix_u64(
        descriptor_signature, descriptor->native_export_signature64);
    descriptor_signature = hhs_lane5_capability_self_model_mix_u64(
        descriptor_signature, descriptor->dependency_signature64);
    descriptor_signature = hhs_lane5_capability_self_model_mix_u64(
        descriptor_signature, descriptor->model_signature64);
    descriptor_signature = hhs_lane5_capability_self_model_mix_u64(
        descriptor_signature, descriptor->canonical_boundary_signature64);
    descriptor_signature = hhs_lane5_capability_self_model_mix_u64(
        descriptor_signature, descriptor->total_entries);
    if (descriptor_signature == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    receipt_signature = hhs_lane5_capability_self_model_mix_u64(
        receipt_signature, descriptor_signature);
    receipt_signature = hhs_lane5_capability_self_model_mix_u64(
        receipt_signature, descriptor->model_signature64);
    receipt_signature = hhs_lane5_capability_self_model_mix_u64(
        receipt_signature, descriptor->dependency_signature64);
    receipt_signature = hhs_lane5_capability_self_model_mix_u64(
        receipt_signature, descriptor->canonical_boundary_signature64);
    receipt_signature = hhs_lane5_capability_self_model_mix_u64(
        receipt_signature, descriptor->public_entries);
    receipt_signature = hhs_lane5_capability_self_model_mix_u64(
        receipt_signature, descriptor->native_entries);
    if (receipt_signature == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(&receipt, 0, sizeof(receipt));
    receipt.struct_size = (uint32_t)sizeof(receipt);
    receipt.version = HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_VERSION;
    receipt.namespace_id = HHS_EXACT_PASS219_LANE5_CAPABILITY_SELF_MODEL_NAMESPACE;
    receipt.total_entries = descriptor->total_entries;
    receipt.public_entries = public_entries;
    receipt.native_entries = native_entries;
    receipt.restricted_entries = restricted_entries;
    receipt.canonical_boundary_entries = boundary_entries;
    receipt.public_catalog_signature64 = descriptor->public_catalog_signature64;
    receipt.native_export_signature64 = descriptor->native_export_signature64;
    receipt.dependency_signature64 = descriptor->dependency_signature64;
    receipt.model_signature64 = descriptor->model_signature64;
    receipt.canonical_boundary_signature64 = boundary_signature;
    receipt.descriptor_signature64 = descriptor_signature;
    receipt.receipt_signature64 = receipt_signature;
    receipt.accepted = 1U;
    receipt.public_registry_complete = 1U;
    receipt.native_exact_abi_complete = 1U;
    receipt.ordered_unique_identity = 1U;
    receipt.candidate_only = 1U;
    receipt.canonical_vm81_mutation_authority = 0U;
    receipt.canonical_hash72_authority = 0U;
    receipt.canonical_hash216_authority = 0U;
    receipt.canonical_persistence_authority = 0U;
    receipt.pqc_key_authority = 0U;
    receipt.receipt_clock_authority = 0U;
    receipt.requires_signed_environmental_vm81_admission = 1U;
    *out_receipt = receipt;
    return HHS_EXACT_STATUS_OK;
}
