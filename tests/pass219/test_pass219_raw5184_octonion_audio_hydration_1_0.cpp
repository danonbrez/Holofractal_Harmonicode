#include "hhs_pass219_raw5184_octonion_audio_hydration_1_0.hpp"

#include <array>
#include <cassert>
#include <cstdint>

int main() {
    std::array<char, HHS_EXACT_PASS219_AUDIO5184_RAW_BITS> bits{};
    for (std::size_t i = 0; i < bits.size(); ++i)
        bits[i] = ((i * 7U + 3U) % 11U) < 5U ? '1' : '0';

    HHSExactVM81Frame frame{};
    assert(
        hhs::pass219::Raw5184OctonionAudioHydration::import_bits(
            bits.data(), bits.size(), frame) == HHS_EXACT_STATUS_OK
    );

    HHSExactPass219Audio5184HydrationV1 hydration{};
    assert(hhs::pass219::Raw5184OctonionAudioHydration::hydrate(frame, hydration) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs::pass219::Raw5184OctonionAudioHydration::validate(frame, hydration));

    int64_t quarter{};
    assert(hhs::pass219::Raw5184OctonionAudioHydration::sine_pcm64(18U, quarter) ==
           HHS_EXACT_STATUS_OK);
    assert(quarter == HHS_EXACT_PASS219_AUDIO5184_SINE_Q62_SCALE);
    assert(hydration.quads[0].stereo_ternary.role_pcm64[0] == INT64_MIN);
    assert(hydration.quads[0].stereo_ternary.role_pcm64[1] == 0);
    assert(hydration.quads[0].stereo_ternary.role_pcm64[2] == INT64_MAX);
    return 0;
}
