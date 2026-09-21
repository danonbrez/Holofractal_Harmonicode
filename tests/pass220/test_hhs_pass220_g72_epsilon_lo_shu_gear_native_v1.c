#include "hhs_pass220_g72_epsilon_lo_shu_gear_1_0.h"

#include <stdint.h>
#include <stdio.h>

#define REQUIRE(expr) do { \
    if (!(expr)) { \
        fprintf(stderr, "requirement failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

int main(void) {
    HHSExactPass220G72DescriptorV1 descriptor;
    HHSExactPass220G72StateV1 state;
    HHSExactPass220G72StateV1 next;
    HHSExactPass220G72RouteWitnessV1 route;
    HHSExactPass220G72ClosureV1 closure;

    REQUIRE(hhs_exact_pass220_g72_version() == HHS_EXACT_PASS220_G72_VERSION);
    REQUIRE(hhs_exact_pass220_g72_descriptor(&descriptor) == HHS_EXACT_STATUS_OK);
    REQUIRE(descriptor.radicand == 2U);
    REQUIRE(descriptor.root_order == 72U);
    REQUIRE(descriptor.harmonic_cells == 144U);
    REQUIRE(descriptor.lo_shu_cells == 9U);
    REQUIRE(descriptor.vm5184 == 5184U);
    REQUIRE(descriptor.fractal_orbit == 10368U);
    REQUIRE(descriptor.immutable_generator == 1U);
    REQUIRE(descriptor.noncommutative_ordered_transition == 1U);
    REQUIRE(descriptor.scalar_evaluation_allowed == 0U);
    REQUIRE(descriptor.epsilon_symbolic_magnitude == 1U);
    REQUIRE(descriptor.lo_shu_route_required == 1U);
    REQUIRE(descriptor.exact_integer_only == 1U);
    REQUIRE(descriptor.floating_point_authority == 0U);
    REQUIRE(descriptor.canonical_admission_authority == 0U);

    REQUIRE(hhs_exact_pass220_g72_state_init(&state) == HHS_EXACT_STATUS_OK);
    REQUIRE(state.tooth_index == 0U);
    REQUIRE(state.completed_routes == 0U);
    REQUIRE(state.generator_unresolved == 1U);
    REQUIRE(state.epsilon_symbol == (uint8_t)'e');
    REQUIRE(state.epsilon_magnitude_unresolved == 1U);

    REQUIRE(hhs_exact_pass220_g72_close(&state, &closure) ==
            HHS_EXACT_STATUS_INVARIANT_FAILURE);

    uint64_t previous_signature = state.route_signature64;
    for (uint32_t tooth = 0U; tooth < 72U; ++tooth) {
        REQUIRE(hhs_exact_pass220_g72_advance(&state, &next, &route) ==
                HHS_EXACT_STATUS_OK);
        REQUIRE(route.from_tooth == tooth);
        REQUIRE(route.to_tooth == tooth + 1U);
        REQUIRE(route.epsilon_signs[0] == -1);
        REQUIRE(route.epsilon_signs[1] == 0);
        REQUIRE(route.epsilon_signs[2] == 1);
        REQUIRE(route.lo_shu_coefficients[0] == -1);
        REQUIRE(route.lo_shu_coefficients[1] == 4);
        REQUIRE(route.lo_shu_coefficients[2] == -3);
        REQUIRE(route.lo_shu_coefficients[3] == -2);
        REQUIRE(route.lo_shu_coefficients[4] == 0);
        REQUIRE(route.lo_shu_coefficients[5] == 2);
        REQUIRE(route.lo_shu_coefficients[6] == 3);
        REQUIRE(route.lo_shu_coefficients[7] == -4);
        REQUIRE(route.lo_shu_coefficients[8] == 1);
        for (size_t i = 0U; i < 3U; ++i) {
            REQUIRE(route.lo_shu_row_sums[i] == 0);
            REQUIRE(route.lo_shu_column_sums[i] == 0);
        }
        REQUIRE(route.lo_shu_diagonal_sums[0] == 0);
        REQUIRE(route.lo_shu_diagonal_sums[1] == 0);
        REQUIRE(route.lo_shu_total == 0);
        REQUIRE(route.local_zero_sum == 1U);
        REQUIRE(route.lo_shu_zero_sum == 1U);
        REQUIRE(route.generator_unresolved_before == 1U);
        REQUIRE(route.generator_unresolved_after == 1U);
        REQUIRE(route.epsilon_magnitude_unresolved == 1U);
        REQUIRE(route.scalar_resolution_performed == 0U);
        REQUIRE(route.floating_point_authority == 0U);
        REQUIRE(route.previous_route_signature64 == previous_signature);
        REQUIRE(route.route_signature64 != previous_signature);

        state = next;
        previous_signature = route.route_signature64;

        if (tooth < 71U)
            REQUIRE(hhs_exact_pass220_g72_close(&state, &closure) ==
                    HHS_EXACT_STATUS_INVARIANT_FAILURE);
    }

    REQUIRE(state.tooth_index == 72U);
    REQUIRE(state.completed_routes == 72U);
    REQUIRE(state.generator_unresolved == 1U);
    REQUIRE(hhs_exact_pass220_g72_advance(&state, &next, &route) ==
            HHS_EXACT_STATUS_RANGE_ERROR);

    REQUIRE(hhs_exact_pass220_g72_close(&state, &closure) == HHS_EXACT_STATUS_OK);
    REQUIRE(closure.routed_cycles == 72U);
    REQUIRE(closure.required_cycles == 72U);
    REQUIRE(closure.emergent_binary_coefficient == 2U);
    REQUIRE(closure.u_exponent == 5184U);
    REQUIRE(closure.f_exponent == 10368U);
    REQUIRE(closure.final_route_signature64 == state.route_signature64);
    REQUIRE(closure.exact_closure == 1U);
    REQUIRE(closure.generator_still_unresolved == 1U);
    REQUIRE(closure.premature_scalar_resolution == 0U);
    REQUIRE(closure.epsilon_orientation_preserved == 1U);
    REQUIRE(closure.lo_shu_routing_preserved == 1U);
    REQUIRE(closure.floating_point_authority == 0U);
    REQUIRE(closure.canonical_admission_authority == 0U);

    puts("PASS220_I021_NATIVE_G72_GEAR_OK");
    return 0;
}
