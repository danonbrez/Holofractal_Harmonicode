#include "hhs_runtime_exact_abi.h"

#include <cassert>
#include <cstdint>
#include <iostream>

int main() {
    HHSExactPass219CompressionDebtPolicyV1 policy{};
    assert(hhs_exact_pass219_compression_debt_policy(&policy) ==
           HHS_EXACT_STATUS_OK);
    assert(policy.boundary_bits == 5184U);
    assert(policy.boundary_bytes == 648U);
    assert(policy.active_surface_cells == 7U);
    assert(policy.active_surface_reduction_numerator == 81U);
    assert(policy.active_surface_reduction_denominator == 7U);

    HHSExactPass219CompressionDebtExchangeV1 exchange{};
    assert(hhs_exact_pass219_compression_debt_exchange(25U, &exchange) ==
           HHS_EXACT_STATUS_OK);
    assert(exchange.compression_numerator == 75U);
    assert(exchange.compression_denominator == 25U);
    assert(exchange.execution_capacity_numerator == 625U);
    assert(exchange.execution_capacity_denominator == 3U);

    HHSExactPass219CompressionDebtLayerInputV1 input{};
    input.struct_size = sizeof(input);
    input.version = hhs_exact_pass219_compression_debt_version();
    input.layer_id = 1U;
    input.issued_debt = 9U;
    input.executed_settled = 3U;
    input.retained_compressed = 6U;
    for (std::uint32_t i = 0; i < 7U; ++i)
        input.active_cell_mask[i * 9U] = 1U;

    HHSExactPass219CompressionDebtLayerResultV1 result{};
    assert(hhs_exact_pass219_compression_debt_layer_close(&input, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.local_zero_sum_closed == 1U);
    assert(result.active_cell_count == 7U);
    assert(result.outstanding_debt == 6U);
    assert(result.canonical_authority == 0U);

    HHSExactPass219CompressionDebtScheduleResultV1 schedule{};
    assert(hhs_exact_pass219_compression_debt_schedule_evaluate(
        UINT64_C(8333333), &result, &schedule) == HHS_EXACT_STATUS_OK);
    assert(schedule.within_25_over_3_ms == 1U);
    assert(schedule.physical_time_monotonic == 1U);
    assert(schedule.timing_is_noncanonical == 1U);

    assert(hhs_exact_pass219_compression_debt_schedule_evaluate(
        UINT64_C(8333334), &result, &schedule) == HHS_EXACT_STATUS_OK);
    assert(schedule.within_25_over_3_ms == 0U);

    std::cout << "PASS219 compression-debt C++ conformance: PASS\n";
    return 0;
}
