#include "hhs_pass220_g72_epsilon_lo_shu_gear_1_0.h"

#include <cstddef>
#include <cstdint>
#include <cstring>

namespace {

constexpr uint64_t FNV_OFFSET = UINT64_C(1469598103934665603);
constexpr uint64_t FNV_PRIME = UINT64_C(1099511628211);

constexpr int8_t EPSILON_SIGNS[3] = {-1, 0, 1};
constexpr int8_t LO_SHU[9] = {
    -1, 4, -3,
    -2, 0, 2,
    3, -4, 1,
};

uint64_t mix_byte(uint64_t hash, uint8_t value) noexcept {
    hash ^= static_cast<uint64_t>(value);
    hash *= FNV_PRIME;
    return hash;
}

uint64_t mix_u32(uint64_t hash, uint32_t value) noexcept {
    for (unsigned shift = 0U; shift < 32U; shift += 8U)
        hash = mix_byte(hash, static_cast<uint8_t>((value >> shift) & UINT32_C(0xff)));
    return hash;
}

bool state_valid(const HHSExactPass220G72StateV1& state) noexcept {
    return state.struct_size == sizeof(HHSExactPass220G72StateV1) &&
        state.version == HHS_EXACT_PASS220_G72_VERSION &&
        state.tooth_index == state.completed_routes &&
        state.tooth_index <= HHS_EXACT_PASS220_G72_ROOT_ORDER &&
        state.generator_unresolved == 1U &&
        state.epsilon_symbol == static_cast<uint8_t>('e') &&
        state.epsilon_magnitude_unresolved == 1U &&
        state.closure_emitted == 0U &&
        state.floating_point_authority == 0U;
}

void fill_route_geometry(HHSExactPass220G72RouteWitnessV1 *route) noexcept {
    for (std::size_t i = 0; i < 3U; ++i)
        route->epsilon_signs[i] = EPSILON_SIGNS[i];
    for (std::size_t i = 0; i < 9U; ++i)
        route->lo_shu_coefficients[i] = LO_SHU[i];

    for (std::size_t row = 0; row < 3U; ++row) {
        int16_t sum = 0;
        for (std::size_t column = 0; column < 3U; ++column)
            sum = static_cast<int16_t>(sum + LO_SHU[row * 3U + column]);
        route->lo_shu_row_sums[row] = sum;
    }
    for (std::size_t column = 0; column < 3U; ++column) {
        int16_t sum = 0;
        for (std::size_t row = 0; row < 3U; ++row)
            sum = static_cast<int16_t>(sum + LO_SHU[row * 3U + column]);
        route->lo_shu_column_sums[column] = sum;
    }
    route->lo_shu_diagonal_sums[0] = static_cast<int16_t>(
        LO_SHU[0] + LO_SHU[4] + LO_SHU[8]);
    route->lo_shu_diagonal_sums[1] = static_cast<int16_t>(
        LO_SHU[2] + LO_SHU[4] + LO_SHU[6]);

    int16_t total = 0;
    for (std::size_t i = 0; i < 9U; ++i)
        total = static_cast<int16_t>(total + LO_SHU[i]);
    route->lo_shu_total = total;

    bool zero_sum = total == 0;
    for (std::size_t i = 0; i < 3U; ++i)
        zero_sum = zero_sum &&
            route->lo_shu_row_sums[i] == 0 &&
            route->lo_shu_column_sums[i] == 0;
    zero_sum = zero_sum &&
        route->lo_shu_diagonal_sums[0] == 0 &&
        route->lo_shu_diagonal_sums[1] == 0;

    route->local_zero_sum =
        (EPSILON_SIGNS[0] + EPSILON_SIGNS[1] + EPSILON_SIGNS[2]) == 0 ? 1U : 0U;
    route->lo_shu_zero_sum = zero_sum ? 1U : 0U;
}

uint64_t route_signature(
    uint64_t previous,
    uint32_t from_tooth,
    uint32_t to_tooth
) noexcept {
    uint64_t hash = previous;
    hash = mix_u32(hash, from_tooth);
    hash = mix_u32(hash, to_tooth);
    for (const int8_t value : EPSILON_SIGNS)
        hash = mix_byte(hash, static_cast<uint8_t>(static_cast<int>(value) + 4));
    for (const int8_t value : LO_SHU)
        hash = mix_byte(hash, static_cast<uint8_t>(static_cast<int>(value) + 8));
    return hash;
}

}  // namespace

extern "C" uint32_t hhs_exact_pass220_g72_version(void) {
    return HHS_EXACT_PASS220_G72_VERSION;
}

extern "C" HHSExactStatus hhs_exact_pass220_g72_descriptor(
    HHSExactPass220G72DescriptorV1 *out_descriptor
) {
    if (out_descriptor == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    HHSExactPass220G72DescriptorV1 descriptor{};
    descriptor.struct_size = static_cast<uint32_t>(sizeof(descriptor));
    descriptor.version = HHS_EXACT_PASS220_G72_VERSION;
    descriptor.radicand = HHS_EXACT_PASS220_G72_RADICAND;
    descriptor.root_order = HHS_EXACT_PASS220_G72_ROOT_ORDER;
    descriptor.harmonic_cells = HHS_EXACT_PASS220_G72_HARMONIC_CELLS;
    descriptor.lo_shu_cells = HHS_EXACT_PASS220_G72_LO_SHU_CELLS;
    descriptor.vm5184 = HHS_EXACT_PASS220_G72_VM5184;
    descriptor.fractal_orbit = HHS_EXACT_PASS220_G72_FRACTAL_ORBIT;
    descriptor.immutable_generator = 1U;
    descriptor.noncommutative_ordered_transition = 1U;
    descriptor.scalar_evaluation_allowed = 0U;
    descriptor.epsilon_symbolic_magnitude = 1U;
    descriptor.lo_shu_route_required = 1U;
    descriptor.exact_integer_only = 1U;
    descriptor.floating_point_authority = 0U;
    descriptor.canonical_admission_authority = 0U;
    *out_descriptor = descriptor;
    return HHS_EXACT_STATUS_OK;
}

extern "C" HHSExactStatus hhs_exact_pass220_g72_state_init(
    HHSExactPass220G72StateV1 *out_state
) {
    if (out_state == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    HHSExactPass220G72StateV1 state{};
    state.struct_size = static_cast<uint32_t>(sizeof(state));
    state.version = HHS_EXACT_PASS220_G72_VERSION;
    state.tooth_index = 0U;
    state.completed_routes = 0U;
    state.route_signature64 = FNV_OFFSET;
    state.generator_unresolved = 1U;
    state.epsilon_symbol = static_cast<uint8_t>('e');
    state.epsilon_magnitude_unresolved = 1U;
    state.closure_emitted = 0U;
    state.floating_point_authority = 0U;
    *out_state = state;
    return HHS_EXACT_STATUS_OK;
}

extern "C" HHSExactStatus hhs_exact_pass220_g72_advance(
    const HHSExactPass220G72StateV1 *state,
    HHSExactPass220G72StateV1 *out_next_state,
    HHSExactPass220G72RouteWitnessV1 *out_route
) {
    if (state == nullptr || out_next_state == nullptr || out_route == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!state_valid(*state))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (state->tooth_index >= HHS_EXACT_PASS220_G72_ROOT_ORDER)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    HHSExactPass220G72RouteWitnessV1 route{};
    route.struct_size = static_cast<uint32_t>(sizeof(route));
    route.version = HHS_EXACT_PASS220_G72_VERSION;
    route.from_tooth = state->tooth_index;
    route.to_tooth = state->tooth_index + 1U;
    route.previous_route_signature64 = state->route_signature64;
    route.generator_unresolved_before = 1U;
    route.generator_unresolved_after = 1U;
    route.epsilon_magnitude_unresolved = 1U;
    route.scalar_resolution_performed = 0U;
    route.floating_point_authority = 0U;
    fill_route_geometry(&route);
    if (route.local_zero_sum != 1U || route.lo_shu_zero_sum != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    route.route_signature64 = route_signature(
        state->route_signature64, route.from_tooth, route.to_tooth);

    HHSExactPass220G72StateV1 next = *state;
    next.tooth_index = route.to_tooth;
    next.completed_routes = state->completed_routes + 1U;
    next.route_signature64 = route.route_signature64;
    next.generator_unresolved = 1U;
    next.epsilon_magnitude_unresolved = 1U;
    next.closure_emitted = 0U;

    *out_route = route;
    *out_next_state = next;
    return HHS_EXACT_STATUS_OK;
}

extern "C" HHSExactStatus hhs_exact_pass220_g72_close(
    const HHSExactPass220G72StateV1 *state,
    HHSExactPass220G72ClosureV1 *out_closure
) {
    if (state == nullptr || out_closure == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    std::memset(out_closure, 0, sizeof(*out_closure));
    if (!state_valid(*state))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (state->completed_routes != HHS_EXACT_PASS220_G72_ROOT_ORDER ||
        state->tooth_index != HHS_EXACT_PASS220_G72_ROOT_ORDER)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    HHSExactPass220G72ClosureV1 closure{};
    closure.struct_size = static_cast<uint32_t>(sizeof(closure));
    closure.version = HHS_EXACT_PASS220_G72_VERSION;
    closure.routed_cycles = state->completed_routes;
    closure.required_cycles = HHS_EXACT_PASS220_G72_ROOT_ORDER;
    closure.emergent_binary_coefficient = HHS_EXACT_PASS220_G72_RADICAND;
    closure.u_exponent =
        HHS_EXACT_PASS220_G72_ROOT_ORDER * HHS_EXACT_PASS220_G72_ROOT_ORDER;
    closure.f_exponent =
        HHS_EXACT_PASS220_G72_HARMONIC_CELLS * HHS_EXACT_PASS220_G72_ROOT_ORDER;
    closure.final_route_signature64 = state->route_signature64;
    closure.exact_closure =
        closure.u_exponent == HHS_EXACT_PASS220_G72_VM5184 &&
        closure.f_exponent == HHS_EXACT_PASS220_G72_FRACTAL_ORBIT ? 1U : 0U;
    closure.generator_still_unresolved = 1U;
    closure.premature_scalar_resolution = 0U;
    closure.epsilon_orientation_preserved = 1U;
    closure.lo_shu_routing_preserved = 1U;
    closure.floating_point_authority = 0U;
    closure.canonical_admission_authority = 0U;
    if (closure.exact_closure != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    *out_closure = closure;
    return HHS_EXACT_STATUS_OK;
}
