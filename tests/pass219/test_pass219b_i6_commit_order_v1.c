#include "../../hhs_runtime/include/hhs_runtime_exact_abi.h"

#include <assert.h>
#include <string.h>

typedef struct I6ResolverContext {
    uint32_t calls;
    uint16_t fail_at;
} I6ResolverContext;

static HHSExactBigUIntView view1(const uint8_t *p) {
    HHSExactBigUIntView v;
    v.struct_size = (uint32_t)sizeof(v);
    v.byte_length = 1U;
    v.bytes_be = p;
    return v;
}

static HHSExactStatus resolver(
    const char transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    uint8_t lane_role,
    uint8_t lane_position72,
    uint16_t absolute_position216,
    uint8_t glyph,
    uint8_t out_sha256[HHS_EXACT_PASS219_HASH216_SHA256_BYTES],
    void *context
) {
    I6ResolverContext *ctx = (I6ResolverContext *)context;
    size_t i;

    if (transition_identity216 == NULL || out_sha256 == NULL || ctx == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (absolute_position216 !=
        (uint16_t)((uint16_t)lane_role * HHS_EXACT_HASH72_LEN + lane_position72))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    ctx->calls += 1U;
    if (absolute_position216 == ctx->fail_at)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_SHA256_BYTES; ++i) {
        out_sha256[i] = (uint8_t)(glyph ^ lane_role ^ lane_position72 ^
                                  (uint8_t)absolute_position216 ^ (uint8_t)i ^
                                  (uint8_t)transition_identity216[
                                      i % HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]);
    }
    return HHS_EXACT_STATUS_OK;
}

static int frame_is_zero(const HHSExactVM81Frame *frame) {
    size_t i;
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        if (frame->words[i] != 0U)
            return 0;
    }
    return 1;
}

int main(void) {
    HHSExactUQCELInputV1 input;
    HHSExactUQCELAdmissionV1 legacy_admission;
    HHSExactPass219RNAAdmissionV1 rna_admission;
    HHSExactPass219BGlobalRelationHydrationWitnessV1 witness;
    HHSExactVM81Frame candidate;
    HHSExactVM81Frame committed;
    I6ResolverContext ctx;
    uint8_t global_tensor_sha[HHS_EXACT_PASS219B_ZERO_SUM_SOURCE_SHA256_BYTES];
    const uint8_t P[] = {4U};
    const uint8_t p[] = {3U};
    const uint8_t q[] = {5U};
    const uint8_t delta[] = {1U};
    const uint8_t A[] = {1U};
    const uint8_t B[] = {2U};
    size_t i;

    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_FULL_SYMBOLIC_V1;
    input.P = view1(P);
    input.p = view1(p);
    input.q = view1(q);
    input.delta = view1(delta);
    input.A = view1(A);
    input.B = view1(B);
    input.cell81 = 41U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    assert(hhs_exact_pass219b_global_tensor_source_sha256(global_tensor_sha) ==
           HHS_EXACT_STATUS_OK);
    memcpy(input.source_envelope_sha256, global_tensor_sha, sizeof(global_tensor_sha));
    memset(input.previous_hash72, '0', HHS_EXACT_HASH72_LEN);
    input.previous_hash72[HHS_EXACT_HASH72_LEN] = '\0';

    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        candidate.words[i] = UINT64_C(0x219B130000000000) ^ (uint64_t)i;

    /*
     * V1 alone lacks lo_shu_group, G243, and phase origin.  It must not remain
     * an alternate canonical full-symbolic commit route.
     */
    memset(&committed, 0xA5, sizeof(committed));
    memset(&legacy_admission, 0, sizeof(legacy_admission));
    assert(hhs_exact_vm81_admit_uqcel(
        &input, &candidate, &committed, &legacy_admission) ==
        HHS_EXACT_STATUS_UNSUPPORTED_DOMAIN);
    assert(legacy_admission.decision == HHS_EXACT_UQCEL_DECISION_UNSUPPORTED_DOMAIN);
    assert(legacy_admission.frame_committed == 0U);
    assert(frame_is_zero(&committed));

    /*
     * A caller-controlled Hash216 resolver failure occurs after N/D hydration,
     * Fibonacci composition, and final identity construction but before the
     * sole VM81 finalizer.  No candidate frame may escape as committed.
     */
    memset(&committed, 0xA5, sizeof(committed));
    memset(&rna_admission, 0, sizeof(rna_admission));
    memset(&witness, 0, sizeof(witness));
    ctx.calls = 0U;
    ctx.fail_at = 17U;
    assert(hhs_exact_pass219b_global_relation_hydration_admit(
        &input, &candidate, 0, 0U, 37U,
        resolver, &ctx,
        &committed, &rna_admission, &witness) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(ctx.calls == 18U);
    assert(frame_is_zero(&committed));
    assert(rna_admission.composed.uqcel.frame_committed == 0U);
    assert(witness.uqcel.frame_committed == 0U);
    assert(witness.rna_composed_verified == 0U);

    /* Successful 216-index resolution reaches the inherited finalizer once. */
    memset(&committed, 0, sizeof(committed));
    memset(&rna_admission, 0, sizeof(rna_admission));
    memset(&witness, 0, sizeof(witness));
    ctx.calls = 0U;
    ctx.fail_at = UINT16_MAX;
    assert(hhs_exact_pass219b_global_relation_hydration_admit(
        &input, &candidate, 0, 0U, 37U,
        resolver, &ctx,
        &committed, &rna_admission, &witness) == HHS_EXACT_STATUS_OK);
    assert(ctx.calls == HHS_EXACT_PASS219_HASH216_OCCURRENCES);
    assert(memcmp(&committed, &candidate, sizeof(candidate)) == 0);
    assert(rna_admission.composed.uqcel.frame_committed == 1U);
    assert(witness.uqcel.frame_committed == 1U);
    assert(witness.rna_composed_verified == 1U);

    return 0;
}
