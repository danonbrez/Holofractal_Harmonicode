#ifndef HHS_PASS219_RAW5184_OCTONION_AUDIO_HYDRATION_1_0_HPP
#define HHS_PASS219_RAW5184_OCTONION_AUDIO_HYDRATION_1_0_HPP

#include "hhs_pass219_raw5184_octonion_audio_hydration_1_0.h"

#include <cstddef>

namespace hhs::pass219 {

class Raw5184OctonionAudioHydration final {
public:
    static HHSExactStatus import_bits(
        const char* bits,
        std::size_t length,
        HHSExactVM81Frame& frame) noexcept {
        return hhs_exact_pass219_audio5184_bitstring_import(bits, length, &frame);
    }

    static HHSExactStatus hydrate(
        const HHSExactVM81Frame& frame,
        HHSExactPass219Audio5184HydrationV1& out) noexcept {
        return hhs_exact_pass219_audio5184_hydrate(&frame, &out);
    }

    static bool validate(
        const HHSExactVM81Frame& frame,
        const HHSExactPass219Audio5184HydrationV1& hydration) noexcept {
        return hhs_exact_pass219_audio5184_hydration_validate(&frame, &hydration) ==
            HHS_EXACT_STATUS_OK;
    }
};

}  // namespace hhs::pass219

#endif
