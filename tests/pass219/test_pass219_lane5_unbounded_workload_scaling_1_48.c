#define _POSIX_C_SOURCE 200809L
#include "hhs_runtime_exact_abi.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static HHSExactBigUIntView view(const uint8_t *bytes, uint32_t length) {
    HHSExactBigUIntView value;
    value.struct_size = (uint32_t)sizeof(value);
    value.byte_length = length;
    value.bytes_be = bytes;
    return value;
}

static void fill_digest(uint8_t out[32], uint8_t seed) {
    uint32_t i;
    for (i = 0U; i < 32U; ++i)
        out[i] = (uint8_t)(seed + (uint8_t)(i * 17U));
}

static void subtract_one(uint8_t *bytes, uint32_t length) {
    uint32_t i = length;
    while (i > 0U) {
        --i;
        if (bytes[i] != 0U) {
            bytes[i] = (uint8_t)(bytes[i] - 1U);
            return;
        }
        bytes[i] = UINT8_MAX;
    }
}

static uint64_t elapsed_ns(const struct timespec *start, const struct timespec *end) {
    uint64_t seconds = (uint64_t)(end->tv_sec - start->tv_sec);
    int64_t nanos = (int64_t)end->tv_nsec - (int64_t)start->tv_nsec;
    if (nanos < 0) {
        seconds -= UINT64_C(1);
        nanos += INT64_C(1000000000);
    }
    return seconds * UINT64_C(1000000000) + (uint64_t)nanos;
}

static HHSExactPass219Lane5UnboundedWorkloadRouteV1 make_route(
    const uint8_t *previous,
    uint32_t previous_len,
    const uint8_t *current,
    uint32_t current_len,
    const uint8_t *goal,
    uint32_t goal_len
) {
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 route;
    memset(&route, 0, sizeof(route));
    route.struct_size = (uint32_t)sizeof(route);
    route.version = HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION;
    route.previous_address = view(previous, previous_len);
    route.current_address = view(current, current_len);
    route.goal_address = view(goal, goal_len);
    route.candidate_address = view(goal, goal_len);
    fill_digest(route.workload_sha256, UINT8_C(0x11));
    fill_digest(route.provenance_sha256, UINT8_C(0x22));
    fill_digest(route.forbidden_boundary_sha256, UINT8_C(0x33));
    fill_digest(route.reciprocal_witness_sha256, UINT8_C(0x44));
    fill_digest(route.route_witness_sha256, UINT8_C(0x55));
    route.workload_byte_count = UINT64_C(1048576);
    route.evidence_count = 5U;
    route.contradiction_check_count = 1U;
    route.integer_route_cost = UINT64_C(7);
    route.materialized_intermediate_states = 0U;
    route.phase_slot = 54U;
    route.inverse_phase_slot = 18U;
    route.trinary_collapse = 0;
    route.binary_collapse = 0U;
    route.nested_zero_slot = 1U;
    route.workload_serialization_exact = 1U;
    route.source_digest_verified = 1U;
    route.replay_witness_verified = 1U;
    route.exact_goal_reached = 1U;
    route.contradiction_free = 1U;
    route.goal_forbidden_conflict = 0U;
    route.reciprocal_phase_verified = 1U;
    route.bigint_serialization_addressed = 1U;
    route.candidate_only = 1U;
    route.canonical_mutation_authority = 0U;
    route.canonical_hash72_authority = 0U;
    route.canonical_hash216_authority = 0U;
    route.canonical_persistence_authority = 0U;
    route.pqc_key_authority = 0U;
    route.receipt_clock_authority = 0U;
    route.requires_signed_environmental_vm81_admission = 1U;
    return route;
}

int main(void) {
    HHSExactPass219Lane5UnboundedWorkloadAuthorityV1 authority;
    HHSExactPass219Lane5UnboundedWorkloadReceiptV1 receipt;
    HHSExactPass219Lane5UnboundedWorkloadStreamV1 stream;
    HHSExactPass219Lane5UnboundedWorkloadStreamV1 saturated_stream;
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 route;
    HHSExactPass219Lane5UnboundedWorkloadRouteV1 mutated;
    uint8_t modulus[HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES];
    uint8_t max_address[HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES];
    uint8_t zero[1] = {0U};
    uint8_t one[1] = {1U};
    uint8_t noncanonical_one[2] = {0U, 1U};
    uint64_t workload_sizes[] = {
        UINT64_C(0), UINT64_C(1), UINT64_C(1048576),
        UINT64_C(1099511627776), UINT64_MAX
    };
    size_t modulus_length = 0U;
    uint32_t i;
    uint8_t admitted = 0U;
    struct timespec started;
    struct timespec finished;
    uint64_t duration;
    const uint32_t scale_candidates = UINT32_C(1000000);

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_scaling_version() ==
          HHS_EXACT_PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_VERSION);
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_scaling_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.struct_size == sizeof(authority));
    CHECK(authority.full_manifold_address_bytes == 56U);
    CHECK(authority.full_manifold_bigint_addressing == 1U);
    CHECK(authority.modulus_is_72_pow_72 == 1U);
    CHECK(authority.any_byte_serializable_workload == 1U);
    CHECK(authority.workload_class_agnostic == 1U);
    CHECK(authority.streaming_candidate_ingress == 1U);
    CHECK(authority.constant_memory_candidate_reduction == 1U);
    CHECK(authority.fixed_candidate_batch_required == 0U);
    CHECK(authority.intermediate_materialization_required == 0U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.pqc_key_authority == 0U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);
    CHECK(authority.floating_point_canonical_authority == 0U);

    CHECK(hhs_exact_pass219_full_manifold_modulus72_72(
        modulus, sizeof(modulus), &modulus_length
    ) == HHS_EXACT_STATUS_OK);
    CHECK(modulus_length == sizeof(modulus));
    memcpy(max_address, modulus, sizeof(max_address));
    subtract_one(max_address, (uint32_t)sizeof(max_address));

    route = make_route(zero, 1U, one, 1U, max_address, (uint32_t)sizeof(max_address));
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_route_validate(&route, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.accepted == 1U);
    CHECK(receipt.candidate_address_length == sizeof(max_address));
    CHECK(memcmp(receipt.candidate_address_be, max_address, sizeof(max_address)) == 0);
    CHECK(receipt.full_manifold_coordinate_capable == 1U);
    CHECK(receipt.workload_class_agnostic == 1U);
    CHECK(receipt.materialized_intermediate_states == 0U);
    CHECK(receipt.canonical_mutation_authority == 0U);
    CHECK(receipt.canonical_hash216_authority == 0U);

    for (i = 0U; i < (uint32_t)(sizeof(workload_sizes) / sizeof(workload_sizes[0])); ++i) {
        route.workload_byte_count = workload_sizes[i];
        CHECK(hhs_exact_pass219_lane5_unbounded_workload_route_validate(&route, &receipt) == HHS_EXACT_STATUS_OK);
        CHECK(receipt.workload_byte_count == workload_sizes[i]);
    }
    route.workload_byte_count = UINT64_C(1048576);

    mutated = route;
    mutated.goal_address = view(modulus, (uint32_t)sizeof(modulus));
    mutated.candidate_address = mutated.goal_address;
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_route_validate(&mutated, &receipt) != HHS_EXACT_STATUS_OK);

    mutated = route;
    mutated.current_address = view(noncanonical_one, 2U);
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_route_validate(&mutated, &receipt) != HHS_EXACT_STATUS_OK);

    mutated = route;
    mutated.candidate_address = view(one, 1U);
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_route_validate(&mutated, &receipt) != HHS_EXACT_STATUS_OK);

    mutated = route;
    mutated.materialized_intermediate_states = 1U;
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_route_validate(&mutated, &receipt) != HHS_EXACT_STATUS_OK);

    mutated = route;
    mutated.goal_forbidden_conflict = 1U;
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_route_validate(&mutated, &receipt) != HHS_EXACT_STATUS_OK);

    mutated = route;
    mutated.canonical_hash216_authority = 1U;
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_route_validate(&mutated, &receipt) != HHS_EXACT_STATUS_OK);

    CHECK(hhs_exact_pass219_lane5_unbounded_workload_stream_init(&stream) == HHS_EXACT_STATUS_OK);
    route.evidence_count = 6U;
    route.integer_route_cost = UINT64_C(8);
    CHECK(clock_gettime(CLOCK_MONOTONIC, &started) == 0);
    for (i = 0U; i < scale_candidates; ++i) {
        uint32_t j;
        for (j = 0U; j < 32U; ++j)
            route.route_witness_sha256[j] = (uint8_t)(UINT32_C(255) - ((i + j) & UINT32_C(255)));
        if (i + 1U == scale_candidates) {
            route.evidence_count = 5U;
            route.integer_route_cost = UINT64_C(7);
            memset(route.route_witness_sha256, 0, sizeof(route.route_witness_sha256));
        }
        CHECK(hhs_exact_pass219_lane5_unbounded_workload_stream_consider(&stream, &route, &admitted) == HHS_EXACT_STATUS_OK);
        CHECK(admitted == 1U);
    }
    CHECK(clock_gettime(CLOCK_MONOTONIC, &finished) == 0);
    duration = elapsed_ns(&started, &finished);
    CHECK(stream.candidates_seen == scale_candidates);
    CHECK(stream.admissible_candidates == scale_candidates);
    CHECK(stream.rejected_candidates == 0U);
    CHECK(stream.has_binding == 1U && stream.has_best == 1U);
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_stream_finalize(&stream, &receipt) == HHS_EXACT_STATUS_OK);
    CHECK(receipt.optimizer_selected == 1U);
    CHECK(receipt.integer_route_cost == 7U);
    CHECK(receipt.materialized_intermediate_states == 0U);
    CHECK(memcmp(receipt.route_witness_sha256, (uint8_t[32]){0}, 32U) == 0);

    CHECK(hhs_exact_pass219_lane5_unbounded_workload_stream_init(&stream) == HHS_EXACT_STATUS_OK);
    route.evidence_count = 5U;
    route.integer_route_cost = UINT64_C(7);
    fill_digest(route.route_witness_sha256, UINT8_C(0x55));
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_stream_consider(&stream, &route, &admitted) == HHS_EXACT_STATUS_OK);
    CHECK(admitted == 1U);
    mutated = route;
    mutated.workload_sha256[0] ^= UINT8_C(0x80);
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_stream_consider(&stream, &mutated, &admitted) == HHS_EXACT_STATUS_OK);
    CHECK(admitted == 0U);
    CHECK(stream.rejected_candidates == 1U);
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_stream_finalize(&stream, &receipt) == HHS_EXACT_STATUS_OK);

    CHECK(hhs_exact_pass219_lane5_unbounded_workload_stream_init(&saturated_stream) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_stream_consider(&saturated_stream, &route, &admitted) == HHS_EXACT_STATUS_OK);
    CHECK(admitted == 1U);
    saturated_stream.candidates_seen = UINT64_MAX;
    saturated_stream.admissible_candidates = UINT64_MAX;
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_stream_consider(&saturated_stream, &route, &admitted) == HHS_EXACT_STATUS_OK);
    CHECK(admitted == 1U);
    CHECK(saturated_stream.count_saturated == 1U);
    CHECK(saturated_stream.candidates_seen == UINT64_MAX);
    CHECK(saturated_stream.admissible_candidates == UINT64_MAX);
    CHECK(hhs_exact_pass219_lane5_unbounded_workload_stream_finalize(&saturated_stream, &receipt) == HHS_EXACT_STATUS_OK);

    printf(
        "{\"result\":\"PASS\",\"full_manifold_address_bytes\":%u,"
        "\"stream_state_bytes\":%zu,\"scale_candidates\":%u,"
        "\"elapsed_ns\":%" PRIu64 ",\"candidates_per_second_floor\":%" PRIu64 ","
        "\"materialized_intermediate_states\":0,\"count_saturation_continues\":true}\n",
        HHS_EXACT_PASS219_LANE5_UNBOUNDED_ADDRESS_BYTES,
        sizeof(HHSExactPass219Lane5UnboundedWorkloadStreamV1),
        scale_candidates,
        duration,
        ((uint64_t)scale_candidates * UINT64_C(1000000000)) / (duration == 0U ? UINT64_C(1) : duration)
    );
    puts("PASS219_LANE5_UNBOUNDED_WORKLOAD_SCALING_1_48_PASS");
    return 0;
}
