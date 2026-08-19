#include "hhs_pass219b_universal_phase_locality_1_0.hpp"

#include <array>
#include <cassert>
#include <type_traits>

int main() {
    static_assert(std::is_standard_layout_v<HHSExactPass219BPhaseLocalityPlanV1>);
    static_assert(std::is_trivially_copyable_v<HHSExactPass219BPhaseLocalityPlanV1>);

    const std::array<HHSExactPass219BPhaseLocalityDimensionV1, 2> dims{{
        {81U, 9U}, {81U, 9U}
    }};
    const auto plan = hhs::rna::UniversalPhaseLocalityPlan::build(
        dims, true, false, 10368U);

    assert(plan.abi().potential_phase_volume == 6561U);
    assert(plan.abi().materialized_phase_volume == 81U);
    assert(plan.abi().reduction_numerator == 81U);
    assert(plan.abi().reduction_denominator == 1U);
    assert(plan.abi().required_realized_units == 839808U);
    assert(plan.verify(839808U, true, true));
    assert(!plan.verify(68024448U, true, true));
    assert(!plan.verify(839808U, false, true));
    assert(!plan.verify(839808U, true, false));
    return 0;
}
