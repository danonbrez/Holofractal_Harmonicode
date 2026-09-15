#define _POSIX_C_SOURCE 200809L
#include "hhs_pass219_lane5_direct_witness_routing_1_46.h"

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define CHECK(expr) do { if (!(expr)) { fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); return 1; } } while (0)

static uint64_t monotonic_ns(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        return UINT64_C(0);
    }
    return (uint64_t)ts.tv_sec * UINT64_C(1000000000) + (uint64_t)ts.tv_nsec;
}

static HHSExactPass219Lane5DirectWitnessRouteV1 make_route(uint32_t index) {
    static const uint32_t phases[4] = {0U, 18U, 36U, 54U};
    static const int8_t trinary[3] = {-1, 0, 1};
    HHSExactPass219Lane5DirectWitnessRouteV1 route;
    memset(&route, 0, sizeof(route));
    route.struct_size = (uint32_t)sizeof(route);
    route.version = HHS_EXACT_PASS219_LANE5_DIRECT_WITNESS_ROUTING_VERSION;
    route.previous_signature64 = UINT64_C(0x10010000) + (uint64_t)index;
    route.current_signature64 = UINT64_C(0x20020000) + (uint64_t)index;
    route.provenance_signature64 = UINT64_C(0x30030000) + (uint64_t)index;
    route.goal_signature64 = UINT64_C(0x40040000);
    route.forbidden_boundary_signature64 = UINT64_C(0x50050000) + (uint64_t)index;
    route.reciprocal_inverse_signature64 = UINT64_C(0x60060000) + (uint64_t)index;
    route.candidate_signature64 = route.goal_signature64;
    route.route_signature64 = UINT64_C(0x90000000) - (uint64_t)index;
    route.represented_span = (uint64_t)(index + 1U) * UINT64_C(1000000);
    route.evidence_count = 5U;
    route.contradiction_check_count = 2U;
    route.integer_route_cost = UINT64_C(8);
    route.materialized_intermediate_states = 0U;
    route.phase_slot = phases[index % 4U];
    route.inverse_phase_slot = (route.phase_slot + 36U) % 72U;
    route.trinary_collapse = trinary[index % 3U];
    route.binary_collapse = (uint8_t)(index % 2U);
    route.nested_zero_slot = route.binary_collapse == 0U ? 1U : 0U;
    route.replay_witness_verified = 1U;
    route.exact_goal_reached = 1U;
    route.contradiction_free = 1U;
    route.goal_forbidden_conflict = 0U;
    route.reciprocal_phase_verified = 1U;
    route.bigint_serialization_addressed = 1U;
    route.candidate_only = 1U;
    route.requires_signed_environmental_vm81_admission = 1U;
    return route;
}

static int run_case(uint32_t count, uint32_t iterations, int first) {
    HHSExactPass219Lane5DirectWitnessRouteV1 *routes;
    HHSExactPass219Lane5DirectWitnessReceiptV1 receipt;
    uint64_t started;
    uint64_t elapsed;
    uint64_t expected_span;
    uint64_t expected_avoided;
    uint32_t i;

    routes = (HHSExactPass219Lane5DirectWitnessRouteV1 *)calloc(count, sizeof(*routes));
    if (routes == NULL) {
        return 1;
    }
    for (i = 0U; i < count; ++i) {
        routes[i] = make_route(i);
    }
    expected_span = (uint64_t)count * UINT64_C(1000000);
    expected_avoided = expected_span - UINT64_C(1);

    for (i = 0U; i < 256U; ++i) {
        memset(&receipt, 0, sizeof(receipt));
        if (hhs_exact_pass219_lane5_direct_witness_route_optimize(routes, count, &receipt) != HHS_EXACT_STATUS_OK) {
            free(routes);
            return 1;
        }
    }

    started = monotonic_ns();
    for (i = 0U; i < iterations; ++i) {
        memset(&receipt, 0, sizeof(receipt));
        if (hhs_exact_pass219_lane5_direct_witness_route_optimize(routes, count, &receipt) != HHS_EXACT_STATUS_OK) {
            free(routes);
            return 1;
        }
        if (receipt.accepted != 1U || receipt.optimizer_selected != 1U ||
            receipt.selected_candidate_index != count - 1U ||
            receipt.represented_span != expected_span ||
            receipt.avoided_intermediate_states != expected_avoided ||
            receipt.integer_route_cost != UINT64_C(8) ||
            receipt.candidate_only != 1U || receipt.canonical_hash216_authority != 0U ||
            receipt.requires_signed_environmental_vm81_admission != 1U) {
            free(routes);
            return 1;
        }
    }
    elapsed = monotonic_ns() - started;
    if (!first) {
        printf(",");
    }
    printf("{\"candidate_count\":%u,\"iterations\":%u,\"total_ns\":%" PRIu64
           ",\"mean_ns_floor\":%" PRIu64 ",\"optimizations_per_second_floor\":%" PRIu64
           ",\"selected_index\":%u,\"represented_span\":%" PRIu64
           ",\"avoided_intermediate_states\":%" PRIu64 ",\"materialized_intermediate_states\":0}",
           count,
           iterations,
           elapsed,
           elapsed / (uint64_t)iterations,
           ((uint64_t)iterations * UINT64_C(1000000000)) / (elapsed == 0U ? UINT64_C(1) : elapsed),
           count - 1U,
           expected_span,
           expected_avoided);
    free(routes);
    return 0;
}

int main(void) {
    HHSExactPass219Lane5DirectWitnessAuthorityV1 authority;
    HHSExactPass219Lane5DirectWitnessReceiptV1 receipt;
    HHSExactPass219Lane5DirectWitnessRouteV1 tampered;
    static const uint32_t counts[4] = {4U, 16U, 64U, 256U};
    static const uint32_t iterations[4] = {50000U, 20000U, 5000U, 2000U};
    uint32_t i;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_direct_witness_routing_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.direct_composition_jump == 1U);
    CHECK(authority.intermediate_materialization_required == 0U);
    CHECK(authority.candidate_only == 1U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);

    tampered = make_route(0U);
    tampered.materialized_intermediate_states = 1U;
    CHECK(hhs_exact_pass219_lane5_direct_witness_route_validate(&tampered, &receipt) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    printf("{\"schema\":\"HHS_PASS219_LANE5_DIRECT_WITNESS_NATIVE_BENCHMARK_1_47\","
           "\"timing_clock\":\"CLOCK_MONOTONIC\",\"timing_is_canonical\":false,"
           "\"candidate_only\":true,\"canonical_hash216_authority\":false,"
           "\"requires_signed_environmental_vm81_admission\":true,\"negative_control_passed\":true,\"cases\":[");
    for (i = 0U; i < 4U; ++i) {
        if (run_case(counts[i], iterations[i], i == 0U) != 0) {
            return 1;
        }
    }
    printf("],\"result\":\"PASS\"}\n");
    return 0;
}
