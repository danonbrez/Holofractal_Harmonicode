#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static void assert_anchor_surface_matches_existing_exact_table(void) {
    HHSExactPass219OctonionSurfaceV1 surface;
    uint8_t left;
    uint8_t right;

    assert(hhs_exact_pass219_octonion_surface(18U, 54U, 18U, 54U, &surface) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_octonion_validate_surface(&surface) == HHS_EXACT_STATUS_OK);

    assert(surface.state.x == 18U);
    assert(surface.state.y == 54U);
    assert(surface.state.z == 18U);
    assert(surface.state.w == 54U);
    assert(surface.state.xy == 0U);
    assert(surface.state.yx == 36U);
    assert(surface.state.zw == 0U);
    assert(surface.state.wz == 36U);
    assert(surface.state.xy != surface.state.yx);
    assert(surface.state.zw != surface.state.wz);
    assert(surface.product_count == 64U);

    for (left = 0U; left < HHS_EXACT_PHASE_BASIS_COUNT; ++left) {
        for (right = 0U; right < HHS_EXACT_PHASE_BASIS_COUNT; ++right) {
            HHSExactPhaseProduct anchor;
            const uint8_t index = (uint8_t)(left * HHS_EXACT_PHASE_BASIS_COUNT + right);
            const HHSExactPass219OctonionProductV1 *actual = &surface.products[index];
            assert(hhs_exact_phase_product(left, right, &anchor) == HHS_EXACT_STATUS_OK);
            assert(actual->left_basis == left);
            assert(actual->right_basis == right);
            assert(actual->ordered_pair_index == index);
            assert(actual->raw_additive_phase == anchor.raw_additive_phase);
            assert(actual->phase == anchor.phase);
            assert(actual->orientation == anchor.orientation);
            assert(actual->closure == anchor.closure);
            assert(actual->ordered_tag == anchor.ordered_tag);
        }
    }
}

static void assert_dynamic_order_is_preserved(void) {
    HHSExactPass219OctonionSurfaceV1 surface;
    HHSExactPass219OctonionProductV1 xy;
    HHSExactPass219OctonionProductV1 yx;
    HHSExactPass219OctonionProductV1 zw;
    HHSExactPass219OctonionProductV1 wz;

    assert(hhs_exact_pass219_octonion_surface(1U, 2U, 3U, 4U, &surface) == HHS_EXACT_STATUS_OK);
    assert(surface.state.x == 1U);
    assert(surface.state.y == 2U);
    assert(surface.state.z == 3U);
    assert(surface.state.w == 4U);
    assert(surface.state.xy == 3U);
    assert(surface.state.yx == 39U);
    assert(surface.state.zw == 7U);
    assert(surface.state.wz == 43U);

    assert(hhs_exact_pass219_octonion_multiply(&surface.state, HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &xy) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_octonion_multiply(&surface.state, HHS_EXACT_PHASE_Y, HHS_EXACT_PHASE_X, &yx) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_octonion_multiply(&surface.state, HHS_EXACT_PHASE_Z, HHS_EXACT_PHASE_W, &zw) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_octonion_multiply(&surface.state, HHS_EXACT_PHASE_W, HHS_EXACT_PHASE_Z, &wz) == HHS_EXACT_STATUS_OK);

    assert(xy.phase == 3U);
    assert(yx.phase == 39U);
    assert(zw.phase == 7U);
    assert(wz.phase == 43U);
    assert(xy.phase != yx.phase);
    assert(zw.phase != wz.phase);
    assert(xy.orientation == HHS_EXACT_PASS219_OCTONION_DIRECT);
    assert(yx.orientation == HHS_EXACT_PASS219_OCTONION_REVERSED);
    assert(zw.orientation == HHS_EXACT_PASS219_OCTONION_DIRECT);
    assert(wz.orientation == HHS_EXACT_PASS219_OCTONION_REVERSED);
    assert(hhs_exact_pass219_octonion_validate_surface(&surface) == HHS_EXACT_STATUS_OK);
}

static void assert_vm81_projection_uses_exact_kernel_fold(void) {
    HHSExactVM81Frame frame;
    HHSExactPass219OctonionSurfaceV1 surface;

    memset(&frame, 0, sizeof(frame));
    frame.words[0] = UINT64_C(1);
    frame.words[1] = UINT64_C(2);
    frame.words[2] = UINT64_C(3);
    frame.words[3] = UINT64_C(4);

    assert(hhs_exact_pass219_octonion_from_vm81(&frame, 0U, 1U, 2U, 3U, &surface) == HHS_EXACT_STATUS_OK);
    assert(surface.state.x == 1U);
    assert(surface.state.y == 2U);
    assert(surface.state.z == 3U);
    assert(surface.state.w == 4U);
    assert(surface.state.xy == 3U);
    assert(surface.state.yx == 39U);
    assert(surface.state.zw == 7U);
    assert(surface.state.wz == 43U);
}

static void assert_negative_cases_fail_closed(void) {
    HHSExactPass219OctonionStateV1 state;
    HHSExactPass219OctonionSurfaceV1 surface;
    HHSExactPass219OctonionDescriptorV1 descriptor;

    assert(hhs_exact_pass219_octonion_descriptor(&descriptor) == HHS_EXACT_STATUS_OK);
    assert(descriptor.ordered_basis_count == 8U);
    assert(descriptor.ordered_product_count == 64U);
    assert(descriptor.exact_integer_phase_arithmetic == 1U);
    assert(descriptor.floating_point_authority == 0U);
    assert(descriptor.vm81_mutation_authority == 0U);
    assert(descriptor.hash72_commit_authority == 0U);

    assert(hhs_exact_pass219_octonion_expand(72U, 0U, 0U, 0U, &state) == HHS_EXACT_STATUS_RANGE_ERROR);
    assert(hhs_exact_pass219_octonion_surface(1U, 2U, 3U, 4U, &surface) == HHS_EXACT_STATUS_OK);
    surface.state.yx = surface.state.xy;
    assert(hhs_exact_pass219_octonion_validate_surface(&surface) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
}

int main(void) {
    assert(hhs_exact_abi_validate() == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_octonion_version() == ((1U << 16) | (19U << 8)));
    assert_anchor_surface_matches_existing_exact_table();
    assert_dynamic_order_is_preserved();
    assert_vm81_projection_uses_exact_kernel_fold();
    assert_negative_cases_fail_closed();
    return 0;
}
