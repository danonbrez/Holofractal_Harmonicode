#include "../include/hhs_pass219_lane5_recursive_hash216_composition_graph_1_40.h"

#include <string.h>

static uint64_t hhs_lane5_graph_mix64(uint64_t x) {
    x ^= x >> 30;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31;
    return x;
}

static uint64_t hhs_lane5_graph_descriptor_signature(
    const HHSExactPass219Lane5RecursiveCompositionGraphDescriptorV1 *d
) {
    uint64_t x = UINT64_C(0x4c35475241503140);
    x ^= hhs_lane5_graph_mix64((uint64_t)d->hop_count);
    x ^= hhs_lane5_graph_mix64((uint64_t)d->total_span << 1);
    x ^= hhs_lane5_graph_mix64((uint64_t)d->phase_slot << 32);
    x ^= hhs_lane5_graph_mix64(d->cycle_index);
    x ^= hhs_lane5_graph_mix64(d->start_signature64);
    x ^= hhs_lane5_graph_mix64(d->goal_signature64);
    x ^= hhs_lane5_graph_mix64(d->terminal_signature64);
    x ^= hhs_lane5_graph_mix64(d->path_signature64);
    x ^= hhs_lane5_graph_mix64(d->ordered_lineage_signature64);
    return hhs_lane5_graph_mix64(x);
}

uint32_t hhs_exact_pass219_lane5_recursive_composition_graph_version(void) {
    return HHS_EXACT_PASS219_LANE5_RECURSIVE_COMPOSITION_GRAPH_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_recursive_composition_graph_authority(
    HHSExactPass219Lane5RecursiveCompositionGraphAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5RecursiveCompositionGraphAuthorityV1 value;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = HHS_EXACT_PASS219_LANE5_RECURSIVE_COMPOSITION_GRAPH_VERSION;
    value.full_cycle = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE;
    value.quarter_cycle = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_QUARTER;
    value.persistent_composition_graph = 1U;
    value.recursive_multi_hop_search = 1U;
    value.hash216_path_seal_required = 1U;
    value.exact_hash216_adjacency_required = 1U;
    value.persistent_edge_authentication_required = 1U;
    value.inherited_gpu_vector_rank_required = 1U;
    value.prime_phase_cycle_bound = 1U;
    value.no_vertex_revisit_required = 1U;
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

HHSExactStatus hhs_exact_pass219_lane5_recursive_composition_graph_validate(
    const HHSExactPass219Lane5RecursiveCompositionGraphDescriptorV1 *descriptor,
    HHSExactPass219Lane5RecursiveCompositionGraphReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5RecursiveCompositionGraphReceiptV1 receipt;
    uint64_t signature;
    if (descriptor == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->struct_size != sizeof(*descriptor) ||
        descriptor->version != HHS_EXACT_PASS219_LANE5_RECURSIVE_COMPOSITION_GRAPH_VERSION)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->hop_count < HHS_EXACT_PASS219_LANE5_RECURSIVE_COMPOSITION_GRAPH_MIN_HOPS ||
        descriptor->total_span < descriptor->hop_count * HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_MIN_SPAN ||
        descriptor->phase_slot >= HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->start_signature64 == 0U ||
        descriptor->goal_signature64 == 0U ||
        descriptor->terminal_signature64 == 0U ||
        descriptor->path_signature64 == 0U ||
        descriptor->ordered_lineage_signature64 == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (descriptor->exact_adjacency != 1U ||
        descriptor->persistent_edges_authenticated != 1U ||
        descriptor->path_sealed != 1U ||
        descriptor->no_vertex_revisit != 1U ||
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
    signature = hhs_lane5_graph_descriptor_signature(descriptor);
    receipt.struct_size = (uint32_t)sizeof(receipt);
    receipt.version = HHS_EXACT_PASS219_LANE5_RECURSIVE_COMPOSITION_GRAPH_VERSION;
    receipt.hop_count = descriptor->hop_count;
    receipt.total_span = descriptor->total_span;
    receipt.phase_slot = descriptor->phase_slot;
    receipt.cycle_index = descriptor->cycle_index;
    receipt.descriptor_signature64 = signature;
    receipt.graph_route_signature64 = hhs_lane5_graph_mix64(
        signature ^ descriptor->path_signature64 ^
        descriptor->ordered_lineage_signature64 ^ UINT64_C(0x2002005005140140)
    );
    receipt.accepted = 1U;
    receipt.exact_adjacency = 1U;
    receipt.persistent_edges_authenticated = 1U;
    receipt.path_sealed = 1U;
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
