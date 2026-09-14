#include "hhs_pass219_lane5_hash216_composition_jump_store_1_38.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); \
        return 1; \
    } \
} while (0)

int main(void) {
    HHSExactPass219Lane5CompositionJumpAuthorityV1 authority;
    HHSExactPass219Lane5CompositionJumpDescriptorV1 descriptor;
    HHSExactPass219Lane5CompositionJumpDescriptorV1 tampered;
    HHSExactPass219Lane5CompositionJumpReceiptV1 receipt_a;
    HHSExactPass219Lane5CompositionJumpReceiptV1 receipt_b;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_composition_jump_version() == HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_VERSION);
    CHECK(hhs_exact_pass219_lane5_composition_jump_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.struct_size == sizeof(authority));
    CHECK(authority.full_cycle == 20020U);
    CHECK(authority.validated_hash216_jump_store == 1U);
    CHECK(authority.exact_registration_replay_required == 1U);
    CHECK(authority.direct_candidate_reuse_allowed == 1U);
    CHECK(authority.prime_fingerprint_search_bound == 1U);
    CHECK(authority.recursive_layer_tagged == 1U);
    CHECK(authority.immutable_composition_seal_required == 1U);
    CHECK(authority.gpu_vector_search_candidate_only == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);
    CHECK(authority.floating_point_canonical_authority == 0U);

    memset(&descriptor, 0, sizeof(descriptor));
    descriptor.struct_size = (uint32_t)sizeof(descriptor);
    descriptor.version = HHS_EXACT_PASS219_LANE5_COMPOSITION_JUMP_VERSION;
    descriptor.jump_span = 32U;
    descriptor.phase_slot = 15015U;
    descriptor.cycle_index = UINT64_C(29);
    descriptor.layer_index = 4U;
    descriptor.parent_signature64 = UINT64_C(0x1101);
    descriptor.child_signature64 = UINT64_C(0x1102);
    descriptor.composition_signature64 = UINT64_C(0x1103);
    descriptor.validated = 1U;
    descriptor.candidate_only = 1U;
    descriptor.requires_signed_environmental_vm81_admission = 1U;

    memset(&receipt_a, 0, sizeof(receipt_a));
    memset(&receipt_b, 0, sizeof(receipt_b));
    CHECK(hhs_exact_pass219_lane5_composition_jump_validate(&descriptor, &receipt_a) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_composition_jump_validate(&descriptor, &receipt_b) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(&receipt_a, &receipt_b, sizeof(receipt_a)) == 0);
    CHECK(receipt_a.accepted == 1U);
    CHECK(receipt_a.validated_hash216_lineage == 1U);
    CHECK(receipt_a.candidate_only == 1U);
    CHECK(receipt_a.canonical_mutation_authority == 0U);
    CHECK(receipt_a.requires_signed_environmental_vm81_admission == 1U);

    tampered = descriptor;
    tampered.validated = 0U;
    CHECK(hhs_exact_pass219_lane5_composition_jump_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.composition_signature64 = 0U;
    CHECK(hhs_exact_pass219_lane5_composition_jump_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    tampered = descriptor;
    tampered.phase_slot = 20020U;
    CHECK(hhs_exact_pass219_lane5_composition_jump_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    tampered = descriptor;
    tampered.canonical_hash216_authority = 1U;
    CHECK(hhs_exact_pass219_lane5_composition_jump_validate(&tampered, &receipt_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    printf(
        "PASS219_LANE5_HASH216_COMPOSITION_JUMP_STORE_PASS span=%u phase=%u layer=%u reuse=%llu\n",
        receipt_a.jump_span,
        receipt_a.phase_slot,
        receipt_a.layer_index,
        (unsigned long long)receipt_a.reuse_signature64);
    return 0;
}
