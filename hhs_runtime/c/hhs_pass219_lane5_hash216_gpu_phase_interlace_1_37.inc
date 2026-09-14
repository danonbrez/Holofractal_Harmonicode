#include "hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37.h"

#include <string.h>

static const uint32_t HHS_P219_LANE5_PERIODS_137[
    HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES
] = {UINT32_C(5), UINT32_C(7), UINT32_C(11), UINT32_C(13)};

static uint64_t hhs_p219_lane5_137_mix_u64(uint64_t hash, uint64_t value) {
    unsigned shift;
    for (shift = 0U; shift < 64U; shift += 8U) {
        hash ^= (value >> shift) & UINT64_C(0xff);
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

static uint32_t hhs_p219_lane5_137_gcd(uint32_t a, uint32_t b) {
    while (b != 0U) {
        const uint32_t r = a % b;
        a = b;
        b = r;
    }
    return a;
}

static uint8_t hhs_p219_lane5_137_is_prime(uint32_t value) {
    uint32_t divisor;
    if (value < 2U)
        return 0U;
    if (value == 2U)
        return 1U;
    if ((value & 1U) == 0U)
        return 0U;
    for (divisor = 3U; divisor <= value / divisor; divisor += 2U) {
        if ((value % divisor) == 0U)
            return 0U;
    }
    return 1U;
}

uint32_t hhs_exact_pass219_lane5_phase_interlace_version(void) {
    return HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_phase_interlace_authority(
    HHSExactPass219Lane5PhaseInterlaceAuthorityV1 *out_authority
) {
    HHSExactPass219Lane5PhaseInterlaceAuthorityV1 authority;
    uint32_t i;

    if (out_authority == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(&authority, 0, sizeof(authority));
    authority.struct_size = (uint32_t)sizeof(authority);
    authority.version = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_VERSION;
    authority.full_cycle = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE;
    authority.quarter_cycle = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_QUARTER;
    authority.lane_count = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES;
    authority.phase_states_per_lane = HHS_EXACT_PASS219_LANE5_PHASE_STATES;
    for (i = 0U; i < HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES; ++i)
        authority.base_periods[i] = HHS_P219_LANE5_PERIODS_137[i];

    authority.fixed_full_cycle_20020 = 1U;
    authority.quarter_sync_5005 = 1U;
    authority.prime_matrix_fingerprint_routing = 1U;
    authority.consecutive_prime_cells_supported = 1U;
    authority.validated_hash216_read_only = 1U;
    authority.hash216_three_hash72_vector_search = 1U;
    authority.pass205_continuation_hash216_bound = 1U;
    authority.pass207_gpu_vector_search_bound = 1U;
    authority.four_lane_parallel_encoding_search = 1U;
    authority.gpu_candidate_only = 1U;
    authority.exact_cpu_vm81_replay_required = 1U;
    authority.canonical_vm81_mutation_authority = 0U;
    authority.canonical_hash72_authority = 0U;
    authority.canonical_hash216_authority = 0U;
    authority.canonical_persistence_authority = 0U;
    authority.requires_lane5_mediation = 1U;
    authority.requires_signed_environmental_vm81_admission = 1U;
    authority.floating_point_canonical_authority = 0U;

    *out_authority = authority;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_phase_address(
    uint64_t tick,
    HHSExactPass219Lane5PhaseAddressV1 *out_address
) {
    HHSExactPass219Lane5PhaseAddressV1 address;
    const uint32_t tick_mod = (uint32_t)(tick % HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE);
    uint64_t signature = UINT64_C(1469598103934665603);
    uint32_t i;

    if (out_address == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(&address, 0, sizeof(address));
    address.struct_size = (uint32_t)sizeof(address);
    address.version = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_VERSION;
    address.tick_mod_cycle = tick_mod;
    address.quarter_index = tick_mod / HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_QUARTER;

    signature = hhs_p219_lane5_137_mix_u64(signature, tick_mod);
    signature = hhs_p219_lane5_137_mix_u64(signature, address.quarter_index);
    for (i = 0U; i < HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES; ++i) {
        const uint32_t period = HHS_P219_LANE5_PERIODS_137[i];
        address.residues[i] = tick_mod % period;
        address.phases[i] = (uint32_t)((tick / period) % HHS_EXACT_PASS219_LANE5_PHASE_STATES);
        signature = hhs_p219_lane5_137_mix_u64(signature, address.residues[i]);
        signature = hhs_p219_lane5_137_mix_u64(signature, address.phases[i]);
    }
    if (signature == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    address.address_signature64 = signature;

    *out_address = address;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_prime_route(
    uint64_t tick,
    const HHSExactPass219Lane5PrimeMatrixV1 *matrix,
    HHSExactPass219Lane5PrimeRouteReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5PrimeRouteReceiptV1 receipt;
    uint32_t base[HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES];
    uint64_t matrix_signature = UINT64_C(1469598103934665603);
    uint64_t route_signature = UINT64_C(1469598103934665603);
    const uint32_t cycle = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE;
    const uint32_t quarter = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_QUARTER;
    const uint32_t tick_mod = (uint32_t)(tick % cycle);
    uint32_t row;
    uint32_t column;

    if (out_receipt == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_receipt, 0, sizeof(*out_receipt));
    if (matrix == NULL ||
        matrix->struct_size != (uint32_t)sizeof(*matrix) ||
        matrix->version != HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_VERSION) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }

    for (row = 0U; row < HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES; ++row) {
        if (matrix->offset[row] >= cycle)
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        matrix_signature = hhs_p219_lane5_137_mix_u64(matrix_signature, matrix->offset[row]);
        for (column = 0U; column < HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES; ++column) {
            const uint32_t value = matrix->cell[row * HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES + column];
            matrix_signature = hhs_p219_lane5_137_mix_u64(matrix_signature, value);
            if (column < row) {
                if (value != 0U)
                    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            } else {
                if (!hhs_p219_lane5_137_is_prime(value) ||
                    hhs_p219_lane5_137_gcd(value, cycle) != 1U) {
                    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
                }
            }
        }
    }
    if (matrix_signature == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (column = 0U; column < HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES; ++column)
        base[column] = (tick_mod + column * quarter) % cycle;

    memset(&receipt, 0, sizeof(receipt));
    receipt.struct_size = (uint32_t)sizeof(receipt);
    receipt.version = HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_VERSION;
    receipt.tick_mod_cycle = tick_mod;
    receipt.matrix_signature64 = matrix_signature;

    route_signature = hhs_p219_lane5_137_mix_u64(route_signature, tick_mod);
    route_signature = hhs_p219_lane5_137_mix_u64(route_signature, matrix_signature);
    for (row = 0U; row < HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES; ++row) {
        uint64_t accumulator = matrix->offset[row];
        for (column = 0U; column < HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES; ++column) {
            accumulator += (uint64_t)matrix->cell[
                row * HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES + column
            ] * (uint64_t)base[column];
        }
        receipt.routed_slot[row] = (uint32_t)(accumulator % cycle);
        route_signature = hhs_p219_lane5_137_mix_u64(route_signature, receipt.routed_slot[row]);
    }
    if (route_signature == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    receipt.route_signature64 = route_signature;
    receipt.prime_cells_validated = 1U;
    receipt.upper_triangular = 1U;
    receipt.invertible_mod_cycle = 1U;
    receipt.candidate_only = 1U;
    receipt.canonical_mutation_authority = 0U;
    receipt.canonical_hash72_authority = 0U;
    receipt.canonical_hash216_authority = 0U;
    receipt.requires_exact_cpu_vm81_replay = 1U;

    *out_receipt = receipt;
    return HHS_EXACT_STATUS_OK;
}
