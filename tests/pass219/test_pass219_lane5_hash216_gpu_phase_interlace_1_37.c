#include "hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37.h"

#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "CHECK failed: %s at %s:%d\n", #expr, __FILE__, __LINE__); \
        return 1; \
    } \
} while (0)

static HHSExactPass219Lane5PrimeMatrixV1 valid_matrix(void) {
    HHSExactPass219Lane5PrimeMatrixV1 matrix;
    static const uint32_t cells[HHS_EXACT_PASS219_LANE5_PRIME_MATRIX_ENTRIES] = {
        17U, 19U, 23U, 29U,
         0U, 31U, 37U, 41U,
         0U,  0U, 43U, 47U,
         0U,  0U,  0U, 53U
    };
    static const uint32_t offsets[HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES] = {
        101U, 211U, 307U, 401U
    };
    memset(&matrix, 0, sizeof(matrix));
    matrix.struct_size = (uint32_t)sizeof(matrix);
    matrix.version = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_VERSION;
    memcpy(matrix.cell, cells, sizeof(cells));
    memcpy(matrix.offset, offsets, sizeof(offsets));
    return matrix;
}

static uint32_t mixed_key(const HHSExactPass219Lane5PhaseAddressV1 *address) {
    uint32_t key = 0U;
    uint32_t multiplier = 1U;
    static const uint32_t radix[HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES] = {
        20U, 28U, 44U, 52U
    };
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES; ++i) {
        const uint32_t local = address->residues[i] * HHS_EXACT_PASS219_LANE5_PHASE_STATES + address->phases[i];
        key += local * multiplier;
        multiplier *= radix[i];
    }
    return key;
}

int main(void) {
    HHSExactPass219Lane5PhaseInterlaceAuthorityV1 authority;
    HHSExactPass219Lane5PhaseAddressV1 address;
    HHSExactPass219Lane5PrimeMatrixV1 matrix;
    HHSExactPass219Lane5PrimeMatrixV1 tampered;
    HHSExactPass219Lane5PrimeRouteReceiptV1 route_a;
    HHSExactPass219Lane5PrimeRouteReceiptV1 route_b;
    static const uint32_t expected_quarters[4][4] = {
        {0U, 0U, 0U, 0U},
        {1U, 3U, 3U, 1U},
        {2U, 2U, 2U, 2U},
        {3U, 1U, 1U, 3U}
    };
    static uint8_t seen[20U * 28U * 44U * 52U];
    uint32_t tick;
    uint32_t i;
    uint32_t unique = 0U;

    memset(&authority, 0, sizeof(authority));
    CHECK(hhs_exact_pass219_lane5_phase_interlace_version() == HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_VERSION);
    CHECK(hhs_exact_pass219_lane5_phase_interlace_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.struct_size == sizeof(authority));
    CHECK(authority.full_cycle == 20020U);
    CHECK(authority.quarter_cycle == 5005U);
    CHECK(authority.lane_count == 4U);
    CHECK(authority.phase_states_per_lane == 4U);
    CHECK(authority.base_periods[0] == 5U);
    CHECK(authority.base_periods[1] == 7U);
    CHECK(authority.base_periods[2] == 11U);
    CHECK(authority.base_periods[3] == 13U);
    CHECK(authority.fixed_full_cycle_20020 == 1U);
    CHECK(authority.quarter_sync_5005 == 1U);
    CHECK(authority.prime_matrix_fingerprint_routing == 1U);
    CHECK(authority.validated_hash216_read_only == 1U);
    CHECK(authority.hash216_three_hash72_vector_search == 1U);
    CHECK(authority.pass205_continuation_hash216_bound == 1U);
    CHECK(authority.pass207_gpu_vector_search_bound == 1U);
    CHECK(authority.gpu_candidate_only == 1U);
    CHECK(authority.exact_cpu_vm81_replay_required == 1U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.canonical_persistence_authority == 0U);
    CHECK(authority.requires_lane5_mediation == 1U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);
    CHECK(authority.floating_point_canonical_authority == 0U);

    for (i = 0U; i < 4U; ++i) {
        CHECK(hhs_exact_pass219_lane5_phase_address((uint64_t)i * 5005U, &address) == HHS_EXACT_STATUS_OK);
        CHECK(address.quarter_index == i);
        CHECK(address.phases[0] == expected_quarters[i][0]);
        CHECK(address.phases[1] == expected_quarters[i][1]);
        CHECK(address.phases[2] == expected_quarters[i][2]);
        CHECK(address.phases[3] == expected_quarters[i][3]);
        CHECK(address.address_signature64 != 0U);
    }
    CHECK(hhs_exact_pass219_lane5_phase_address(20020U, &address) == HHS_EXACT_STATUS_OK);
    CHECK(address.tick_mod_cycle == 0U);
    CHECK(address.quarter_index == 0U);
    CHECK(address.phases[0] == 0U && address.phases[1] == 0U && address.phases[2] == 0U && address.phases[3] == 0U);

    memset(seen, 0, sizeof(seen));
    for (tick = 0U; tick < 20020U; ++tick) {
        uint32_t key;
        CHECK(hhs_exact_pass219_lane5_phase_address(tick, &address) == HHS_EXACT_STATUS_OK);
        key = mixed_key(&address);
        CHECK(key < sizeof(seen));
        CHECK(seen[key] == 0U);
        seen[key] = 1U;
        ++unique;
    }
    CHECK(unique == 20020U);

    matrix = valid_matrix();
    memset(&route_a, 0, sizeof(route_a));
    memset(&route_b, 0, sizeof(route_b));
    CHECK(hhs_exact_pass219_lane5_prime_route(1234U, &matrix, &route_a) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_lane5_prime_route(1234U, &matrix, &route_b) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(&route_a, &route_b, sizeof(route_a)) == 0);
    CHECK(route_a.matrix_signature64 != 0U);
    CHECK(route_a.route_signature64 != 0U);
    CHECK(route_a.prime_cells_validated == 1U);
    CHECK(route_a.upper_triangular == 1U);
    CHECK(route_a.invertible_mod_cycle == 1U);
    CHECK(route_a.candidate_only == 1U);
    CHECK(route_a.canonical_mutation_authority == 0U);
    CHECK(route_a.canonical_hash72_authority == 0U);
    CHECK(route_a.canonical_hash216_authority == 0U);
    CHECK(route_a.requires_exact_cpu_vm81_replay == 1U);
    for (i = 0U; i < 4U; ++i)
        CHECK(route_a.routed_slot[i] < 20020U);

    tampered = matrix;
    tampered.cell[0] = 5U;
    CHECK(hhs_exact_pass219_lane5_prime_route(1234U, &tampered, &route_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = matrix;
    tampered.cell[1] = 21U;
    CHECK(hhs_exact_pass219_lane5_prime_route(1234U, &tampered, &route_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    tampered = matrix;
    tampered.cell[4] = 17U;
    CHECK(hhs_exact_pass219_lane5_prime_route(1234U, &tampered, &route_b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    printf(
        "PASS219_LANE5_HASH216_GPU_PHASE_INTERLACE_PASS unique=%u route=%u,%u,%u,%u signature=%llu\n",
        unique,
        route_a.routed_slot[0], route_a.routed_slot[1],
        route_a.routed_slot[2], route_a.routed_slot[3],
        (unsigned long long)route_a.route_signature64);
    return 0;
}
