#include "../include/hhs_pass219_octonion_runtime_1_19.h"

#include <string.h>

static uint32_t hhs_exact_pass219_octonion_version_word(void) {
    return (HHS_EXACT_PASS219_OCTONION_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_OCTONION_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_OCTONION_VERSION_PATCH;
}

static uint8_t hhs_exact_pass219_wrap72_u16(uint16_t value) {
    return (uint8_t)(value % HHS_EXACT_HASH72_LEN);
}

static HHSExactStatus hhs_exact_pass219_state_phase_unchecked(
    const HHSExactPass219OctonionStateV1 *state,
    uint8_t basis,
    uint8_t *out_phase
) {
    switch (basis) {
        case HHS_EXACT_PHASE_X:  *out_phase = state->x;  return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PHASE_Y:  *out_phase = state->y;  return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PHASE_Z:  *out_phase = state->z;  return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PHASE_W:  *out_phase = state->w;  return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PHASE_XY: *out_phase = state->xy; return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PHASE_YX: *out_phase = state->yx; return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PHASE_ZW: *out_phase = state->zw; return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PHASE_WZ: *out_phase = state->wz; return HHS_EXACT_STATUS_OK;
        default: return HHS_EXACT_STATUS_RANGE_ERROR;
    }
}

static HHSExactStatus hhs_exact_pass219_product_from_phases(
    uint8_t left_basis,
    uint8_t right_basis,
    uint8_t left_phase,
    uint8_t right_phase,
    HHSExactPass219OctonionProductV1 *out_product
) {
    HHSExactPhaseProduct anchor;
    uint8_t anchor_delta;
    uint8_t raw;

    if (out_product == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (left_basis >= HHS_EXACT_PHASE_BASIS_COUNT ||
        right_basis >= HHS_EXACT_PHASE_BASIS_COUNT ||
        left_phase >= HHS_EXACT_HASH72_LEN ||
        right_phase >= HHS_EXACT_HASH72_LEN)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    if (hhs_exact_phase_product(left_basis, right_basis, &anchor) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    anchor_delta = hhs_exact_pass219_wrap72_u16(
        (uint16_t)anchor.phase + HHS_EXACT_HASH72_LEN - anchor.raw_additive_phase);
    raw = hhs_exact_pass219_wrap72_u16((uint16_t)left_phase + right_phase);

    memset(out_product, 0, sizeof(*out_product));
    out_product->struct_size = (uint32_t)sizeof(*out_product);
    out_product->version = hhs_exact_pass219_octonion_version_word();
    out_product->left_basis = left_basis;
    out_product->right_basis = right_basis;
    out_product->left_phase = left_phase;
    out_product->right_phase = right_phase;
    out_product->raw_additive_phase = raw;
    out_product->phase = hhs_exact_pass219_wrap72_u16((uint16_t)raw + anchor_delta);
    out_product->orientation = anchor.orientation;
    out_product->closure = (uint8_t)(out_product->phase == 0U || out_product->phase == 36U);
    out_product->ordered_pair_index = (uint8_t)(left_basis * HHS_EXACT_PHASE_BASIS_COUNT + right_basis);
    out_product->ordered_tag = anchor.ordered_tag;
    return HHS_EXACT_STATUS_OK;
}

static uint8_t hhs_exact_pass219_fold_word72(uint64_t word) {
    uint32_t accumulator = 0U;
    uint8_t byte_index;
    for (byte_index = 0U; byte_index < 8U; ++byte_index) {
        uint8_t byte_value = (uint8_t)((word >> (8U * byte_index)) & UINT64_C(0xFF));
        accumulator += (uint32_t)byte_value * (uint32_t)(byte_index + 1U);
    }
    return (uint8_t)(accumulator % HHS_EXACT_HASH72_LEN);
}

uint32_t hhs_exact_pass219_octonion_version(void) {
    return hhs_exact_pass219_octonion_version_word();
}

HHSExactStatus hhs_exact_pass219_octonion_descriptor(
    HHSExactPass219OctonionDescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs_exact_pass219_octonion_version_word();
    out_descriptor->ordered_basis_count = HHS_EXACT_PASS219_OCTONION_CHANNEL_COUNT;
    out_descriptor->ordered_product_count = HHS_EXACT_PASS219_OCTONION_PRODUCT_COUNT;
    out_descriptor->vm81_projection_supported = 1U;
    out_descriptor->exact_integer_phase_arithmetic = 1U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->vm81_mutation_authority = 0U;
    out_descriptor->hash72_commit_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_octonion_expand(
    uint8_t x,
    uint8_t y,
    uint8_t z,
    uint8_t w,
    HHSExactPass219OctonionStateV1 *out_state
) {
    HHSExactPass219OctonionProductV1 product;

    if (out_state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (x >= HHS_EXACT_HASH72_LEN || y >= HHS_EXACT_HASH72_LEN ||
        z >= HHS_EXACT_HASH72_LEN || w >= HHS_EXACT_HASH72_LEN)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_state, 0, sizeof(*out_state));
    out_state->struct_size = (uint32_t)sizeof(*out_state);
    out_state->version = hhs_exact_pass219_octonion_version_word();
    out_state->x = x;
    out_state->y = y;
    out_state->z = z;
    out_state->w = w;

    if (hhs_exact_pass219_product_from_phases(HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y,
                                              x, y, &product) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_state->xy = product.phase;

    if (hhs_exact_pass219_product_from_phases(HHS_EXACT_PHASE_Y, HHS_EXACT_PHASE_X,
                                              y, x, &product) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_state->yx = product.phase;

    if (hhs_exact_pass219_product_from_phases(HHS_EXACT_PHASE_Z, HHS_EXACT_PHASE_W,
                                              z, w, &product) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_state->zw = product.phase;

    if (hhs_exact_pass219_product_from_phases(HHS_EXACT_PHASE_W, HHS_EXACT_PHASE_Z,
                                              w, z, &product) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_state->wz = product.phase;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_octonion_channel_phase(
    const HHSExactPass219OctonionStateV1 *state,
    uint8_t basis,
    uint8_t *out_phase
) {
    if (state == NULL || out_phase == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (state->struct_size < sizeof(*state) ||
        state->version != hhs_exact_pass219_octonion_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (basis >= HHS_EXACT_PHASE_BASIS_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    return hhs_exact_pass219_state_phase_unchecked(state, basis, out_phase);
}

HHSExactStatus hhs_exact_pass219_octonion_multiply(
    const HHSExactPass219OctonionStateV1 *state,
    uint8_t left_basis,
    uint8_t right_basis,
    HHSExactPass219OctonionProductV1 *out_product
) {
    uint8_t left_phase;
    uint8_t right_phase;
    HHSExactStatus status;

    if (state == NULL || out_product == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (state->struct_size < sizeof(*state) ||
        state->version != hhs_exact_pass219_octonion_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (left_basis >= HHS_EXACT_PHASE_BASIS_COUNT ||
        right_basis >= HHS_EXACT_PHASE_BASIS_COUNT)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    status = hhs_exact_pass219_state_phase_unchecked(state, left_basis, &left_phase);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_state_phase_unchecked(state, right_basis, &right_phase);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    return hhs_exact_pass219_product_from_phases(
        left_basis, right_basis, left_phase, right_phase, out_product);
}

HHSExactStatus hhs_exact_pass219_octonion_surface(
    uint8_t x,
    uint8_t y,
    uint8_t z,
    uint8_t w,
    HHSExactPass219OctonionSurfaceV1 *out_surface
) {
    uint8_t left;
    uint8_t right;
    HHSExactStatus status;

    if (out_surface == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_surface, 0, sizeof(*out_surface));
    out_surface->struct_size = (uint32_t)sizeof(*out_surface);
    out_surface->version = hhs_exact_pass219_octonion_version_word();
    out_surface->product_count = HHS_EXACT_PASS219_OCTONION_PRODUCT_COUNT;
    out_surface->noncommutative_generator_pairs = 2U;

    status = hhs_exact_pass219_octonion_expand(x, y, z, w, &out_surface->state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    for (left = 0U; left < HHS_EXACT_PHASE_BASIS_COUNT; ++left) {
        for (right = 0U; right < HHS_EXACT_PHASE_BASIS_COUNT; ++right) {
            uint8_t index = (uint8_t)(left * HHS_EXACT_PHASE_BASIS_COUNT + right);
            status = hhs_exact_pass219_octonion_multiply(
                &out_surface->state, left, right, &out_surface->products[index]);
            if (status != HHS_EXACT_STATUS_OK)
                return status;
        }
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_octonion_from_vm81(
    const HHSExactVM81Frame *frame,
    uint8_t x_cell,
    uint8_t y_cell,
    uint8_t z_cell,
    uint8_t w_cell,
    HHSExactPass219OctonionSurfaceV1 *out_surface
) {
    if (frame == NULL || out_surface == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (x_cell >= HHS_EXACT_VM81_CELLS || y_cell >= HHS_EXACT_VM81_CELLS ||
        z_cell >= HHS_EXACT_VM81_CELLS || w_cell >= HHS_EXACT_VM81_CELLS)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    return hhs_exact_pass219_octonion_surface(
        hhs_exact_pass219_fold_word72(frame->words[x_cell]),
        hhs_exact_pass219_fold_word72(frame->words[y_cell]),
        hhs_exact_pass219_fold_word72(frame->words[z_cell]),
        hhs_exact_pass219_fold_word72(frame->words[w_cell]),
        out_surface);
}

HHSExactStatus hhs_exact_pass219_octonion_validate_state(
    const HHSExactPass219OctonionStateV1 *state
) {
    HHSExactPass219OctonionStateV1 expected;
    HHSExactStatus status;

    if (state == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (state->struct_size < sizeof(*state) ||
        state->version != hhs_exact_pass219_octonion_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (state->x >= HHS_EXACT_HASH72_LEN || state->y >= HHS_EXACT_HASH72_LEN ||
        state->z >= HHS_EXACT_HASH72_LEN || state->w >= HHS_EXACT_HASH72_LEN ||
        state->xy >= HHS_EXACT_HASH72_LEN || state->yx >= HHS_EXACT_HASH72_LEN ||
        state->zw >= HHS_EXACT_HASH72_LEN || state->wz >= HHS_EXACT_HASH72_LEN)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    status = hhs_exact_pass219_octonion_expand(state->x, state->y, state->z, state->w, &expected);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (state->xy != expected.xy || state->yx != expected.yx ||
        state->zw != expected.zw || state->wz != expected.wz)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (state->xy == state->yx || state->zw == state->wz)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_octonion_validate_surface(
    const HHSExactPass219OctonionSurfaceV1 *surface
) {
    uint8_t left;
    uint8_t right;
    HHSExactStatus status;

    if (surface == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (surface->struct_size < sizeof(*surface) ||
        surface->version != hhs_exact_pass219_octonion_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (surface->product_count != HHS_EXACT_PASS219_OCTONION_PRODUCT_COUNT ||
        surface->noncommutative_generator_pairs != 2U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_octonion_validate_state(&surface->state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    for (left = 0U; left < HHS_EXACT_PHASE_BASIS_COUNT; ++left) {
        for (right = 0U; right < HHS_EXACT_PHASE_BASIS_COUNT; ++right) {
            uint8_t index = (uint8_t)(left * HHS_EXACT_PHASE_BASIS_COUNT + right);
            HHSExactPass219OctonionProductV1 expected;
            const HHSExactPass219OctonionProductV1 *actual = &surface->products[index];
            status = hhs_exact_pass219_octonion_multiply(&surface->state, left, right, &expected);
            if (status != HHS_EXACT_STATUS_OK)
                return status;
            if (actual->struct_size < sizeof(*actual) ||
                actual->version != hhs_exact_pass219_octonion_version_word() ||
                actual->left_basis != expected.left_basis ||
                actual->right_basis != expected.right_basis ||
                actual->left_phase != expected.left_phase ||
                actual->right_phase != expected.right_phase ||
                actual->raw_additive_phase != expected.raw_additive_phase ||
                actual->phase != expected.phase ||
                actual->orientation != expected.orientation ||
                actual->closure != expected.closure ||
                actual->ordered_pair_index != expected.ordered_pair_index ||
                actual->ordered_tag != expected.ordered_tag)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }
    return HHS_EXACT_STATUS_OK;
}
