#include "hhs_runtime_exact_abi.h"

#include <array>
#include <cassert>
#include <cstdint>

int main() {
    HHSExactPass219OctonionSurfaceV1 surface{};
    HHSExactPass219OctonionDescriptorV1 descriptor{};

    static_assert(HHS_EXACT_PASS219_OCTONION_CHANNEL_COUNT == 8U, "eight ordered channels required");
    static_assert(HHS_EXACT_PASS219_OCTONION_PRODUCT_COUNT == 64U, "8x8 ordered surface required");

    assert(hhs_exact_pass219_octonion_descriptor(&descriptor) == HHS_EXACT_STATUS_OK);
    assert(descriptor.floating_point_authority == 0U);
    assert(hhs_exact_pass219_octonion_surface(5U, 11U, 17U, 23U, &surface) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_octonion_validate_surface(&surface) == HHS_EXACT_STATUS_OK);

    const std::array<std::uint8_t, 8> channels = {
        surface.state.x,
        surface.state.y,
        surface.state.z,
        surface.state.w,
        surface.state.xy,
        surface.state.yx,
        surface.state.zw,
        surface.state.wz,
    };

    assert(channels[0] == 5U);
    assert(channels[1] == 11U);
    assert(channels[2] == 17U);
    assert(channels[3] == 23U);
    assert(channels[4] == 16U);
    assert(channels[5] == 52U);
    assert(channels[6] == 40U);
    assert(channels[7] == 4U);
    assert(channels[4] != channels[5]);
    assert(channels[6] != channels[7]);

    for (std::uint8_t basis = 0U; basis < 8U; ++basis) {
        std::uint8_t phase = 0U;
        assert(hhs_exact_pass219_octonion_channel_phase(&surface.state, basis, &phase) == HHS_EXACT_STATUS_OK);
        assert(phase == channels[basis]);
    }

    return 0;
}
