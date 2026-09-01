#include "hhs_runtime_exact_abi.h"

#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>

int main() {
    static_assert(HHS_EXACT_PASS219_LATENCY_MEAN_RATIO_NUMERATOR_MS == 25U);
    static_assert(HHS_EXACT_PASS219_LATENCY_MEAN_RATIO_DENOMINATOR_MS == 3U);
    static_assert(HHS_EXACT_PASS219_LATENCY_TIER1_FPS == 120U);
    static_assert(HHS_EXACT_PASS219_LATENCY_TIER2_FPS == 60U);
    static_assert(HHS_EXACT_PASS219_LATENCY_TIER3_FPS == 30U);

    HHSExactPass219GlobalLatencyPolicyV1 policy{};
    assert(hhs_exact_pass219_global_latency_policy(&policy) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_global_latency_policy_validate() == HHS_EXACT_STATUS_OK);
    assert(policy.exact_integer_classification_required == 1U);
    assert(policy.timing_is_noncanonical == 1U);
    assert(policy.singleton_vm81_authority_preserved == 1U);

    std::uint32_t tier = 0U;
    assert(hhs_exact_pass219_global_latency_classify_ns(8'333'333ULL, &tier) ==
           HHS_EXACT_STATUS_OK);
    assert(tier == HHS_EXACT_PASS219_LATENCY_TIER1_120FPS);

    HHSExactPass219LatencyWindowInputV1 input{};
    input.struct_size = sizeof(input);
    input.version = hhs_exact_pass219_global_latency_policy_version();
    input.sample_count = 7U;
    const std::uint64_t samples[7] = {
        1'300'000ULL,
        1'320'000ULL,
        1'340'000ULL,
        1'360'000ULL,
        1'380'000ULL,
        1'400'000ULL,
        1'420'000ULL,
    };
    std::memcpy(input.samples_ns, samples, sizeof(samples));

    HHSExactPass219LatencyWindowResultV1 result{};
    assert(hhs_exact_pass219_global_latency_window_evaluate(&input, &result) ==
           HHS_EXACT_STATUS_OK);
    assert(result.window_policy_met == 1U);
    assert(result.mean_tier == HHS_EXACT_PASS219_LATENCY_TIER1_120FPS);
    assert(result.p95_tier == HHS_EXACT_PASS219_LATENCY_TIER1_120FPS);
    assert(result.max_tier == HHS_EXACT_PASS219_LATENCY_TIER1_120FPS);
    assert(result.timing_is_noncanonical == 1U);

    std::cout << "PASS219_GLOBAL_LATENCY_POLICY_25_3_1_0_CPP_OK\n";
    return 0;
}
