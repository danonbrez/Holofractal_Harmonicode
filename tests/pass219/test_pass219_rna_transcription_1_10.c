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

static HHSExactStatus test_index_resolver(
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
    for (i = 0U; i < HHS_EXACT_PASS219_HASH216_SHA256_BYTES; ++i) {
        out_sha256[i] = (uint8_t)(glyph ^ lane_role ^ lane_position72 ^
                                  (uint8_t)absolute_position216 ^ (uint8_t)i ^
                                  (uint8_t)transition_identity216[i % HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]);
    }
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
    HHSExactVM81Frame frame;
    HHSExactVM81Frame roundtrip;
    uint8_t bytes[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t seen[HHS_EXACT_PASS219_TRIT_COUNT][HHS_EXACT_PASS219_HYDRATION_SLOT_COUNT];
    char previous[HHS_EXACT_HASH72_STRLEN];
    char change[HHS_EXACT_HASH72_STRLEN];
    char receipt[HHS_EXACT_HASH72_STRLEN];
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
    ResolverContext resolver_context = {0U};
    size_t output_length = 0U;
    uint32_t o;
    uint32_t g;
    uint8_t out_cell;
    int8_t out_group;
    uint8_t out_operation;
    uint16_t out_g243;
    size_t i;

    CHECK(hhs_exact_pass219_rna_version() == ((1U << 16) | (10U << 8)));

    CHECK(hhs_exact_pass219_native_phase_witness(
              HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &xy) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_native_phase_witness(
              HHS_EXACT_PHASE_Y, HHS_EXACT_PHASE_X, &yx) == HHS_EXACT_STATUS_OK);
    CHECK(xy.ordered_source_preserved == 1U);
    CHECK(yx.ordered_source_preserved == 1U);
    CHECK(xy.ordered_product.ordered_tag != yx.ordered_product.ordered_tag);
    CHECK(xy.ordered_product.phase != yx.ordered_product.phase);

    for (i = 0U; i < HHS_EXACT_PASS219_TRIT_COUNT; ++i) {
        CHECK(hhs_exact_pass219_trinary_phase_gate((uint8_t)i, &gate) == HHS_EXACT_STATUS_OK);
        CHECK(gate.trit == i);
        CHECK(gate.identity == i);
        CHECK(gate.center_relation == HHS_EXACT_PASS219_CENTER_RELATION_X_PLUS_Y);
        CHECK(gate.left_xy.ordered_tag != gate.right_yx.ordered_tag);
        CHECK(gate.ordered_left_right_preserved == 1U);
    }
    CHECK(hhs_exact_pass219_trinary_phase_gate(3U, &gate) == HHS_EXACT_STATUS_RANGE_ERROR);

    memset(seen, 0, sizeof(seen));
    for (o = 0U; o < HHS_EXACT_PASS219_OPERATION64_COUNT; ++o) {
        for (g = 0U; g < HHS_EXACT_PASS219_G243_COUNT; ++g) {
            CHECK(hhs_exact_pass219_coordinate_from_pass189(
                      80U, 20, (uint8_t)o, (uint16_t)g, &coordinate) == HHS_EXACT_STATUS_OK);
            CHECK(coordinate.trit < HHS_EXACT_PASS219_TRIT_COUNT);
            CHECK(coordinate.slot5184 < HHS_EXACT_PASS219_HYDRATION_SLOT_COUNT);
            CHECK(seen[coordinate.trit][coordinate.slot5184] == 0U);
            seen[coordinate.trit][coordinate.slot5184] = 1U;
            CHECK(hhs_exact_pass219_coordinate_to_pass189(
                      &coordinate, &out_cell, &out_group, &out_operation, &out_g243) == HHS_EXACT_STATUS_OK);
            CHECK(out_cell == 80U);
            CHECK(out_group == 20);
            CHECK(out_operation == o);
            CHECK(out_g243 == g);
        }
    }
    for (i = 0U; i < HHS_EXACT_PASS219_TRIT_COUNT; ++i) {
        size_t slot;
        for (slot = 0U; slot < HHS_EXACT_PASS219_HYDRATION_SLOT_COUNT; ++slot)
            CHECK(seen[i][slot] == 1U);
    }
    CHECK(hhs_exact_pass219_coordinate_from_pass189(
              80U, 20, 63U, 242U, &coordinate) == HHS_EXACT_STATUS_OK);
    CHECK(coordinate.trit == 2U);
    CHECK(coordinate.slot5184 == 5183U);
    CHECK(hhs_exact_pass219_coordinate_from_pass189(
              81U, 0, 0U, 0U, &coordinate) == HHS_EXACT_STATUS_RANGE_ERROR);

    fill_hash72(previous, 0U);
    fill_hash72(change, 1U);
    fill_hash72(receipt, 2U);
    fill_identity216(identity);
    CHECK(hhs_exact_pass219_hash216_transition_init(
              previous, change, receipt, identity, &transition) == HHS_EXACT_STATUS_OK);
    CHECK(transition.occurrences[0].lane_role == HHS_EXACT_PASS219_HASH216_LANE_PREVIOUS);
    CHECK(transition.occurrences[71].lane_position72 == 71U);
    CHECK(transition.occurrences[72].lane_role == HHS_EXACT_PASS219_HASH216_LANE_CHANGE);
    CHECK(transition.occurrences[144].lane_role == HHS_EXACT_PASS219_HASH216_LANE_RECEIPT);
    CHECK(transition.occurrences[215].absolute_position216 == 215U);
    CHECK(hhs_exact_pass219_hash216_indexes_complete(&transition) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(hhs_exact_pass219_hash216_resolve_indexes(
              &transition, test_index_resolver, &resolver_context) == HHS_EXACT_STATUS_OK);
    CHECK(resolver_context.calls == HHS_EXACT_PASS219_HASH216_OCCURRENCES);
    CHECK(hhs_exact_pass219_hash216_indexes_complete(&transition) == HHS_EXACT_STATUS_OK);

    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] = UINT64_C(0x0102030405060708) ^ (uint64_t)i;
    CHECK(hhs_exact_vm81_frame_export_le(
              &frame, bytes, sizeof(bytes), &output_length) == HHS_EXACT_STATUS_OK);
    CHECK(output_length == HHS_EXACT_VM81_FRAME_BYTES);
    CHECK(hhs_exact_vm81_frame_import_le(
              bytes, sizeof(bytes), &roundtrip) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(&frame, &roundtrip, sizeof(frame)) == 0);

    CHECK(hhs_exact_pass219_rna_admit_composed(
              NULL, &frame, 0, 0U, test_index_resolver, &resolver_context,
              &roundtrip, NULL) == HHS_EXACT_STATUS_INVALID_ARGUMENT);

    return 0;
}
