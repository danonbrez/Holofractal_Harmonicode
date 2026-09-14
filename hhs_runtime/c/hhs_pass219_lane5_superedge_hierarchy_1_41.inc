#include "../include/hhs_pass219_lane5_superedge_hierarchy_1_41.h"

#include <string.h>

static uint64_t hhs_lane5_superedge_mix64(uint64_t x) {
    x ^= x >> 30;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31;
    return x;
}

static uint64_t hhs_lane5_superedge_descriptor_signature(
    const HHSExactPass219Lane5SuperedgeDescriptorV1 *d
) {
    uint64_t x = UINT64_C(0x4c35535550455241);
    x ^= hhs_lane5_superedge_mix64((uint64_t)d->hierarchy_level);
    x ^= hhs_lane5_superedge_mix64((uint64_t)d->direct_component_count << 8);
    x ^= hhs_lane5_superedge_mix64((uint64_t)d->base_hops << 16);
    x ^= hhs_lane5_superedge_mix64((uint64_t)d->total_span << 1);
    x ^= hhs_lane5_superedge_mix64((uint64_t)d->phase_slot << 32);
    x ^= hhs_lane5_superedge_mix64((uint64_t)d->layer_index << 24);
    x ^= hhs_lane5_superedge_mix64(d->cycle_index);
    x ^= hhs_lane5_superedge_mix64(d->parent_signature64);
    x ^= hhs_lane5_superedge_mix64(d->child_signature64);
    x ^= hhs_lane5_superedge_mix64(d->route_signature64);
    x ^= hhs_lane5_superedge_mix64(d->hierarchy_signature64);
    x ^= hhs_lane5_superedge_mix64(d->metadata_signature64);
    x ^= hhs_lane5_superedge_mix64(d->component_lineage_signature64);
    x ^= hhs_lane5_superedge_mix64(d->flattened_leaf_signature64);
    return hhs_lane5_superedge_mix64(x);
}

uint32_t hhs_exact_pass219_lane5_superedge_hierarchy_version(void) {
    return HHS_EXACT_PASS219_LANE5_SUPEREDGE_HIERARCHY_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_superedge_hierarchy_authority(
    HHSExactPass219Lane5SuperedgeHierarchyAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5SuperedgeHierarchyAuthorityV1 value;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = HHS_EXACT_PASS219_LANE5_SUPEREDGE_HIERARCHY_VERSION;
    value.full_cycle = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE;
    value.quarter_cycle = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_QUARTER;
    value.recursive_superedge_hierarchy = 1U;
    value.restart_rehydratable_superedges = 1U;
    value.one_snapshot_direct_reuse = 1U;
    value.transitive_flattened_provenance_required = 1U;
    value.hash216_hierarchy_seal_required = 1U;
    value.exact_component_adjacency_required = 1U;
    value.leaf_quarantine_propagation_required = 1U;
    value.inherited_gpu_vector_rank_allowed = 1U;
    value.candidate_only = 1U;
    value.canonical_vm81_mutation_authority = 0U;
    value.canonical_hash72_authority = 0U;
    value.canonical_hash216_authority = 0U;
    value.canonical_persistence_authority = 0U;
    value.pqc_key_authority = 0U;
    value.receipt_clock_authority = 0U;
    value.requires_signed_environmental_vm81_admission = 1U;
    value.floating_point_canonical_authority = 0U;
    *out_authority = value;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_superedge_validate(
    const HHSExactPass219Lane5SuperedgeDescriptorV1 *descriptor,
    HHSExactPass219Lane5SuperedgeReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5SuperedgeReceiptV1 receipt;
    uint64_t signature;
    if (descriptor == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->struct_size != sizeof(*descriptor) ||
        descriptor->version != HHS_EXACT_PASS219_LANE5_SUPEREDGE_HIERARCHY_VERSION)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->hierarchy_level < HHS_EXACT_PASS219_LANE5_SUPEREDGE_MIN_LEVEL ||
        descriptor->direct_component_count < HHS_EXACT_PASS219_LANE5_SUPEREDGE_MIN_COMPONENTS ||
        descriptor->base_hops < descriptor->direct_component_count ||
        descriptor->total_span < descriptor->base_hops * HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_MIN_SPAN ||
        descriptor->phase_slot >= HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->parent_signature64 == 0U ||
        descriptor->child_signature64 == 0U ||
        descriptor->route_signature64 == 0U ||
        descriptor->hierarchy_signature64 == 0U ||
        descriptor->metadata_signature64 == 0U ||
        descriptor->component_lineage_signature64 == 0U ||
        descriptor->flattened_leaf_signature64 == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (descriptor->exact_component_adjacency != 1U ||
        descriptor->lower_level_replay_authenticated != 1U ||
        descriptor->terminal_snapshot_encrypted != 1U ||
        descriptor->hierarchy_sealed != 1U ||
        descriptor->leaf_dependencies_live != 1U ||
        descriptor->candidate_only != 1U ||
        descriptor->canonical_mutation_authority != 0U ||
        descriptor->canonical_hash72_authority != 0U ||
        descriptor->canonical_hash216_authority != 0U ||
        descriptor->canonical_persistence_authority != 0U ||
        descriptor->pqc_key_authority != 0U ||
        descriptor->receipt_clock_authority != 0U ||
        descriptor->requires_signed_environmental_vm81_admission != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(&receipt, 0, sizeof(receipt));
    signature = hhs_lane5_superedge_descriptor_signature(descriptor);
    receipt.struct_size = (uint32_t)sizeof(receipt);
    receipt.version = HHS_EXACT_PASS219_LANE5_SUPEREDGE_HIERARCHY_VERSION;
    receipt.hierarchy_level = descriptor->hierarchy_level;
    receipt.direct_component_count = descriptor->direct_component_count;
    receipt.base_hops = descriptor->base_hops;
    receipt.total_span = descriptor->total_span;
    receipt.phase_slot = descriptor->phase_slot;
    receipt.layer_index = descriptor->layer_index;
    receipt.cycle_index = descriptor->cycle_index;
    receipt.descriptor_signature64 = signature;
    receipt.hierarchy_receipt_signature64 = hhs_lane5_superedge_mix64(
        signature ^ descriptor->hierarchy_signature64 ^
        descriptor->flattened_leaf_signature64 ^ UINT64_C(0x2002005005140141)
    );
    receipt.accepted = 1U;
    receipt.exact_component_adjacency = 1U;
    receipt.lower_level_replay_authenticated = 1U;
    receipt.terminal_snapshot_encrypted = 1U;
    receipt.hierarchy_sealed = 1U;
    receipt.leaf_dependencies_live = 1U;
    receipt.one_snapshot_direct_reuse = 1U;
    receipt.candidate_only = 1U;
    receipt.canonical_mutation_authority = 0U;
    receipt.canonical_hash72_authority = 0U;
    receipt.canonical_hash216_authority = 0U;
    receipt.canonical_persistence_authority = 0U;
    receipt.pqc_key_authority = 0U;
    receipt.receipt_clock_authority = 0U;
    receipt.requires_signed_environmental_vm81_admission = 1U;
    *out_receipt = receipt;
    return HHS_EXACT_STATUS_OK;
}
