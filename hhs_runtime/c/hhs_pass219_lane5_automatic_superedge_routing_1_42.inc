#include "../include/hhs_pass219_lane5_automatic_superedge_routing_1_42.h"

#include <string.h>

static uint64_t hhs_lane5_auto_route_mix64(uint64_t x) {
    x ^= x >> 30;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31;
    return x;
}

static uint64_t hhs_lane5_auto_route_descriptor_signature(
    const HHSExactPass219Lane5AutomaticRouteDescriptorV1 *d
) {
    uint64_t x = UINT64_C(0x4c354155544f5232);
    x ^= hhs_lane5_auto_route_mix64((uint64_t)d->retrieval_count);
    x ^= hhs_lane5_auto_route_mix64((uint64_t)d->base_hops << 8);
    x ^= hhs_lane5_auto_route_mix64((uint64_t)d->represented_span << 16);
    x ^= hhs_lane5_auto_route_mix64((uint64_t)d->max_hierarchy_level << 24);
    x ^= hhs_lane5_auto_route_mix64((uint64_t)d->phase_slot << 32);
    x ^= hhs_lane5_auto_route_mix64((uint64_t)d->layer_index << 40);
    x ^= hhs_lane5_auto_route_mix64(d->cycle_index);
    x ^= hhs_lane5_auto_route_mix64(d->parent_signature64);
    x ^= hhs_lane5_auto_route_mix64(d->goal_signature64);
    x ^= hhs_lane5_auto_route_mix64(d->route_signature64);
    x ^= hhs_lane5_auto_route_mix64(d->ordered_candidate_signature64);
    return hhs_lane5_auto_route_mix64(x);
}

uint32_t hhs_exact_pass219_lane5_automatic_superedge_routing_version(void) {
    return HHS_EXACT_PASS219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_automatic_superedge_routing_authority(
    HHSExactPass219Lane5AutomaticRoutingAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5AutomaticRoutingAuthorityV1 value;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = HHS_EXACT_PASS219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_VERSION;
    value.full_cycle = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE;
    value.quarter_cycle = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_QUARTER;
    value.default_promotion_threshold = HHS_EXACT_PASS219_LANE5_AUTOMATIC_PROMOTION_THRESHOLD;
    value.cross_level_exact_routing = 1U;
    value.automatic_repeated_route_promotion = 1U;
    value.durable_exact_observation_ledger = 1U;
    value.integer_only_routing_cost = 1U;
    value.exact_hash216_adjacency_required = 1U;
    value.exact_target_closure_required = 1U;
    value.mixed_level_candidate_routing_allowed = 1U;
    value.mixed_level_recursive_promotion_allowed = 0U;
    value.inherited_gpu_vector_rank_non_authoritative = 1U;
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

HHSExactStatus hhs_exact_pass219_lane5_automatic_route_validate(
    const HHSExactPass219Lane5AutomaticRouteDescriptorV1 *descriptor,
    HHSExactPass219Lane5AutomaticRouteReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5AutomaticRouteReceiptV1 receipt;
    uint64_t signature;
    if (descriptor == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->struct_size != sizeof(*descriptor) ||
        descriptor->version != HHS_EXACT_PASS219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_VERSION)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->retrieval_count < HHS_EXACT_PASS219_LANE5_AUTOMATIC_ROUTE_MIN_RETRIEVALS ||
        descriptor->base_hops < descriptor->retrieval_count ||
        descriptor->represented_span < descriptor->base_hops * HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_MIN_SPAN ||
        descriptor->phase_slot >= HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->parent_signature64 == 0U ||
        descriptor->goal_signature64 == 0U ||
        descriptor->route_signature64 == 0U ||
        descriptor->ordered_candidate_signature64 == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (descriptor->exact_hash216_adjacency != 1U ||
        descriptor->exact_target_closure != 1U ||
        descriptor->dependencies_live != 1U ||
        descriptor->selected_by_integer_cost != 1U ||
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
    signature = hhs_lane5_auto_route_descriptor_signature(descriptor);
    receipt.struct_size = (uint32_t)sizeof(receipt);
    receipt.version = HHS_EXACT_PASS219_LANE5_AUTOMATIC_SUPEREDGE_ROUTING_VERSION;
    receipt.retrieval_count = descriptor->retrieval_count;
    receipt.base_hops = descriptor->base_hops;
    receipt.represented_span = descriptor->represented_span;
    receipt.max_hierarchy_level = descriptor->max_hierarchy_level;
    receipt.phase_slot = descriptor->phase_slot;
    receipt.layer_index = descriptor->layer_index;
    receipt.cycle_index = descriptor->cycle_index;
    receipt.descriptor_signature64 = signature;
    receipt.route_receipt_signature64 = hhs_lane5_auto_route_mix64(
        signature ^ descriptor->route_signature64 ^
        descriptor->ordered_candidate_signature64 ^ UINT64_C(0x2002005005140142)
    );
    receipt.accepted = 1U;
    receipt.exact_hash216_adjacency = 1U;
    receipt.exact_target_closure = 1U;
    receipt.dependencies_live = 1U;
    receipt.selected_by_integer_cost = 1U;
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
