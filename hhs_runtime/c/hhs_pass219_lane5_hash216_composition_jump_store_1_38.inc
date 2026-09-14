#include "../include/hhs_pass219_lane5_hash216_composition_jump_store_1_38.h"

#include <string.h>

static uint64_t hhs_lane5_jump_mix64(uint64_t x) {
    x ^= x >> 30;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31;
    return x;
}

static uint64_t hhs_lane5_jump_signature(
    const HHSExactPass219Lane5CompositionJumpDescriptorV1 *d
) {
    uint64_t x = UINT64_C(0x4c354a554d503138);
    x ^= hhs_lane5_jump_mix64((uint64_t)d->jump_span);
    x ^= hhs_lane5_jump_mix64((uint64_t)d->phase_slot << 32);
    x ^= hhs_lane5_jump_mix64(d->cycle_index);
    x ^= hhs_lane5_jump_mix64((uint64_t)d->layer_index);
    x ^= hhs_lane5_jump_mix64(d->parent_signature64);
    x ^= hhs_lane5_jump_mix64(d->child_signature64);
    x ^= hhs_lane5_jump_mix64(d->composition_signature64);
    return hhs_lane5_jump_mix64(x);
}

uint32_t hhs_exact_pass219_lane5_composition_jump_version(void) {
    return HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_composition_jump_authority(
    HHSExactPass219Lane5CompositionJumpAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5CompositionJumpAuthorityV1 value;
    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_VERSION;
    value.full_cycle = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE;
    value.validated_hash216_jump_store = 1U;
    value.exact_registration_replay_required = 1U;
    value.direct_candidate_reuse_allowed = 1U;
    value.prime_fingerprint_search_bound = 1U;
    value.recursive_layer_tagged = 1U;
    value.immutable_composition_seal_required = 1U;
    value.gpu_vector_search_candidate_only = 1U;
    value.canonical_vm81_mutation_authority = 0U;
    value.canonical_hash72_authority = 0U;
    value.canonical_hash216_authority = 0U;
    value.canonical_persistence_authority = 0U;
    value.requires_signed_environmental_vm81_admission = 1U;
    value.floating_point_canonical_authority = 0U;
    *out_authority = value;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_composition_jump_validate(
    const HHSExactPass219Lane5CompositionJumpDescriptorV1 *descriptor,
    HHSExactPass219Lane5CompositionJumpReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5CompositionJumpReceiptV1 receipt;
    uint64_t signature;
    if (descriptor == NULL || out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->struct_size != sizeof(*descriptor) ||
        descriptor->version != HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_VERSION)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->jump_span < HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_MIN_SPAN ||
        descriptor->phase_slot >= HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->parent_signature64 == 0U ||
        descriptor->child_signature64 == 0U ||
        descriptor->composition_signature64 == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (descriptor->validated != 1U || descriptor->candidate_only != 1U ||
        descriptor->canonical_mutation_authority != 0U ||
        descriptor->canonical_hash72_authority != 0U ||
        descriptor->canonical_hash216_authority != 0U ||
        descriptor->requires_signed_environmental_vm81_admission != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(&receipt, 0, sizeof(receipt));
    signature = hhs_lane5_jump_signature(descriptor);
    receipt.struct_size = (uint32_t)sizeof(receipt);
    receipt.version = HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_VERSION;
    receipt.jump_span = descriptor->jump_span;
    receipt.phase_slot = descriptor->phase_slot;
    receipt.cycle_index = descriptor->cycle_index;
    receipt.layer_index = descriptor->layer_index;
    receipt.descriptor_signature64 = signature;
    receipt.reuse_signature64 = hhs_lane5_jump_mix64(
        signature ^ descriptor->composition_signature64 ^ UINT64_C(0x200200500513)
    );
    receipt.accepted = 1U;
    receipt.validated_hash216_lineage = 1U;
    receipt.candidate_only = 1U;
    receipt.canonical_mutation_authority = 0U;
    receipt.canonical_hash72_authority = 0U;
    receipt.canonical_hash216_authority = 0U;
    receipt.requires_signed_environmental_vm81_admission = 1U;
    *out_receipt = receipt;
    return HHS_EXACT_STATUS_OK;
}
