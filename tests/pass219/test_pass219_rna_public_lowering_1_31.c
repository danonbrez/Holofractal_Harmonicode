#include "hhs_runtime_exact_abi.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

typedef struct ResolverContext {
    uint32_t calls;
} ResolverContext;

static HHSExactStatus diagnostic_resolver(
    const char transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    uint8_t lane_role,
    uint8_t lane_position72,
    uint16_t absolute_position216,
    uint8_t glyph,
    uint8_t out_sha256[HHS_EXACT_PASS219_HASH216_SHA256_BYTES],
    void *context
) {
    ResolverContext *ctx = (ResolverContext *)context;
    size_t i;
    if (transition_identity216 == NULL || out_sha256 == NULL || ctx == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (absolute_position216 != (uint16_t)((uint16_t)lane_role * 72U + lane_position72))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_SHA256_BYTES; ++i)
        out_sha256[i] = (uint8_t)(glyph ^ lane_role ^ lane_position72 ^
                                  (uint8_t)absolute_position216 ^ (uint8_t)i ^
                                  (uint8_t)transition_identity216[i % HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]);
    ctx->calls += 1U;
    return HHS_EXACT_STATUS_OK;
}

static void fill_hash72(char out[HHS_EXACT_HASH72_STRLEN], uint8_t offset) {
    size_t i;
    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

static void fill_identity216(char out[HHS_EXACT_UQCEL_HASH216_STRLEN]) {
    size_t i;
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i * 7U + 3U) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
}

int main(void) {
    HHSExactPass219NativePhaseWitnessV1 xy;
    HHSExactPass219NativePhaseWitnessV1 yx;
    HHSExactPass219TrinaryPhaseGateV1 gate;
    HHSExactPass219HydrationCoordinateV1 coordinate;
    HHSExactPass219Hash216TransitionViewV1 transition;
    char previous[HHS_EXACT_HASH72_STRLEN];
    char change[HHS_EXACT_HASH72_STRLEN];
    char receipt[HHS_EXACT_HASH72_STRLEN];
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
    ResolverContext diagnostic = {0U};
    uint8_t out_cell;
    int8_t out_group;
    uint8_t out_operation;
    uint16_t out_g243;

    CHECK(hhs_exact_pass219_rna_version() == ((1U << 16) | (10U << 8)));

    CHECK(hhs_exact_pass219_native_phase_witness(
              HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &xy) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_native_phase_witness(
              HHS_EXACT_PHASE_Y, HHS_EXACT_PHASE_X, &yx) == HHS_EXACT_STATUS_OK);
    CHECK(xy.ordered_source_preserved == 1U);
    CHECK(yx.ordered_source_preserved == 1U);
    CHECK(xy.ordered_product.ordered_tag != yx.ordered_product.ordered_tag);
    CHECK(xy.ordered_product.phase != yx.ordered_product.phase);

    CHECK(hhs_exact_pass219_trinary_phase_gate(0U, &gate) == HHS_EXACT_STATUS_OK);
    CHECK(gate.ordered_left_right_preserved == 1U);
    CHECK(hhs_exact_pass219_trinary_phase_gate(3U, &gate) == HHS_EXACT_STATUS_RANGE_ERROR);

    CHECK(hhs_exact_pass219_coordinate_from_pass189(
              80U, 20, 63U, 242U, &coordinate) == HHS_EXACT_STATUS_OK);
    CHECK(coordinate.trit == 2U);
    CHECK(coordinate.slot5184 == 5183U);
    CHECK(hhs_exact_pass219_coordinate_to_pass189(
              &coordinate, &out_cell, &out_group, &out_operation, &out_g243) == HHS_EXACT_STATUS_OK);
    CHECK(out_cell == 80U);
    CHECK(out_group == 20);
    CHECK(out_operation == 63U);
    CHECK(out_g243 == 242U);

    /* Generic transition/index helpers remain diagnostic lowering surfaces. */
    fill_hash72(previous, 0U);
    fill_hash72(change, 1U);
    fill_hash72(receipt, 2U);
    fill_identity216(identity);
    CHECK(hhs_exact_pass219_hash216_transition_init(
              previous, change, receipt, identity, &transition) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_hash216_indexes_complete(&transition) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(hhs_exact_pass219_hash216_resolve_indexes(
              &transition, diagnostic_resolver, &diagnostic) == HHS_EXACT_STATUS_OK);
    CHECK(diagnostic.calls == HHS_EXACT_PASS219_HASH216_OCCURRENCES);
    CHECK(hhs_exact_pass219_hash216_indexes_complete(&transition) == HHS_EXACT_STATUS_OK);

    /* Production firewall never trusts this diagnostic resolver; its own
     * reference verifier re-derives every positional record internally. */
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&transition) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    return 0;
}
