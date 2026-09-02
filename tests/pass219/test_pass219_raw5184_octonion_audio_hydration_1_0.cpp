#include "hhs_pass219_raw5184_octonion_audio_hydration_1_0.hpp"

#include <cassert>
#include <cstdint>
#include <string>

int main() {
    std::string bits(5184, '0');
    for (std::size_t i = 0; i < bits.size(); ++i) {
        if (((i * 13U) + 5U) % 7U < 3U) bits[i] = '1';
    }

    HHSExactVM81Frame frame{};
    assert(hhs::pass219::Raw5184OctonionAudioHydration::import_bits(
               bits.data(), bits.size(), frame) == HHS_EXACT_STATUS_OK);

    HHSExactPass219Audio5184HydrationV1 hydration{};
    assert(hhs::pass219::Raw5184OctonionAudioHydration::hydrate(
               frame, hydration) == HHS_EXACT_STATUS_OK);
    assert(hhs::pass219::Raw5184OctonionAudioHydration::validate(
               frame, hydration));

    const auto& q = hydration.quads[0].stereo_ternary;
    assert(q.numerator_role[0] == -1);
    assert(q.numerator_role[1] == 0);
    assert(q.numerator_role[2] == 1);
    assert(q.role_pcm64[0] == INT64_MIN);
    assert(q.role_pcm64[1] == 0);
    assert(q.role_pcm64[2] == INT64_MAX);
    assert(q.center_zero_over_zero_u0_mod_u72 == 1U);
    assert(q.center_xy_sum_over_zw_sum_u0 == 1U);
    assert(q.center_mono_xy_sum_colon_zw_sum == 1U);
    assert(q.scalar_projection_runtime_authority == 0U);
    return 0;
}
