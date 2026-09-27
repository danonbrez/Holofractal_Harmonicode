#include "hhs_pass220_numpy_native_array_kernel_v1.h"

#include <limits.h>
#include <stddef.h>

static void zero_shape(HHSNumpyNativeShapeV1 *shape) {
    uint32_t i;
    if (shape == NULL) return;
    shape->rank = 0U;
    for (i = 0U; i < HHS_NUMPY_NATIVE_MAX_RANK; ++i) shape->dims[i] = 0U;
}

uint32_t hhs_numpy_native_array_kernel_version(void) {
    return HHS_NUMPY_NATIVE_ARRAY_KERNEL_VERSION;
}

HHSNumpyNativeStatusV1 hhs_numpy_native_shape_validate(
    const HHSNumpyNativeShapeV1 *shape
) {
    uint32_t i;
    if (shape == NULL) return HHS_NUMPY_NATIVE_ERR_ARGUMENT;
    if (shape->rank > HHS_NUMPY_NATIVE_MAX_RANK) return HHS_NUMPY_NATIVE_ERR_RANK;
    for (i = 0U; i < shape->rank; ++i) {
        if (shape->dims[i] == 0U) return HHS_NUMPY_NATIVE_ERR_DIMENSION;
    }
    return HHS_NUMPY_NATIVE_OK;
}

HHSNumpyNativeStatusV1 hhs_numpy_native_element_count(
    const HHSNumpyNativeShapeV1 *shape,
    uint64_t *out_count
) {
    uint64_t count = 1U;
    uint32_t i;
    HHSNumpyNativeStatusV1 status;
    if (out_count == NULL) return HHS_NUMPY_NATIVE_ERR_ARGUMENT;
    status = hhs_numpy_native_shape_validate(shape);
    if (status != HHS_NUMPY_NATIVE_OK) return status;
    if (shape->rank == 0U) {
        *out_count = 1U;
        return HHS_NUMPY_NATIVE_OK;
    }
    for (i = 0U; i < shape->rank; ++i) {
        if (count > UINT64_MAX / shape->dims[i]) return HHS_NUMPY_NATIVE_ERR_OVERFLOW;
        count *= shape->dims[i];
    }
    *out_count = count;
    return HHS_NUMPY_NATIVE_OK;
}

HHSNumpyNativeStatusV1 hhs_numpy_native_broadcast_shape(
    const HHSNumpyNativeShapeV1 *left,
    const HHSNumpyNativeShapeV1 *right,
    HHSNumpyNativeShapeV1 *out
) {
    uint32_t out_rank;
    uint32_t offset;
    HHSNumpyNativeStatusV1 status;
    if (out == NULL) return HHS_NUMPY_NATIVE_ERR_ARGUMENT;
    status = hhs_numpy_native_shape_validate(left);
    if (status != HHS_NUMPY_NATIVE_OK) return status;
    status = hhs_numpy_native_shape_validate(right);
    if (status != HHS_NUMPY_NATIVE_OK) return status;

    zero_shape(out);
    out_rank = left->rank > right->rank ? left->rank : right->rank;
    out->rank = out_rank;

    for (offset = 0U; offset < out_rank; ++offset) {
        uint64_t ld = 1U;
        uint64_t rd = 1U;
        uint32_t out_index = out_rank - 1U - offset;
        if (offset < left->rank) ld = left->dims[left->rank - 1U - offset];
        if (offset < right->rank) rd = right->dims[right->rank - 1U - offset];
        if (ld != rd && ld != 1U && rd != 1U) {
            zero_shape(out);
            return HHS_NUMPY_NATIVE_ERR_BROADCAST;
        }
        out->dims[out_index] = ld > rd ? ld : rd;
    }
    return HHS_NUMPY_NATIVE_OK;
}

HHSNumpyNativeStatusV1 hhs_numpy_native_project_broadcast_index(
    const HHSNumpyNativeShapeV1 *output_shape,
    uint64_t output_linear_index,
    const HHSNumpyNativeShapeV1 *input_shape,
    uint64_t *out_input_linear_index
) {
    uint64_t output_count;
    uint64_t input_count;
    uint64_t remaining;
    uint64_t input_linear = 0U;
    uint64_t input_stride = 1U;
    uint64_t output_coords[HHS_NUMPY_NATIVE_MAX_RANK] = {0U};
    uint32_t i;
    HHSNumpyNativeStatusV1 status;

    if (out_input_linear_index == NULL) return HHS_NUMPY_NATIVE_ERR_ARGUMENT;
    status = hhs_numpy_native_element_count(output_shape, &output_count);
    if (status != HHS_NUMPY_NATIVE_OK) return status;
    status = hhs_numpy_native_element_count(input_shape, &input_count);
    if (status != HHS_NUMPY_NATIVE_OK) return status;
    if (output_linear_index >= output_count) return HHS_NUMPY_NATIVE_ERR_INDEX;

    /* Validate broadcast compatibility by aligning input trailing dimensions. */
    for (i = 0U; i < input_shape->rank; ++i) {
        uint32_t input_index = input_shape->rank - 1U - i;
        uint32_t output_index;
        uint64_t in_dim;
        uint64_t out_dim;
        if (i >= output_shape->rank) return HHS_NUMPY_NATIVE_ERR_BROADCAST;
        output_index = output_shape->rank - 1U - i;
        in_dim = input_shape->dims[input_index];
        out_dim = output_shape->dims[output_index];
        if (in_dim != out_dim && in_dim != 1U) return HHS_NUMPY_NATIVE_ERR_BROADCAST;
    }

    remaining = output_linear_index;
    for (i = output_shape->rank; i > 0U; --i) {
        uint32_t index = i - 1U;
        uint64_t dim = output_shape->dims[index];
        output_coords[index] = remaining % dim;
        remaining /= dim;
    }

    if (input_shape->rank == 0U) {
        *out_input_linear_index = 0U;
        return HHS_NUMPY_NATIVE_OK;
    }

    for (i = input_shape->rank; i > 0U; --i) {
        uint32_t input_index = i - 1U;
        uint32_t output_index = output_shape->rank - (input_shape->rank - input_index);
        uint64_t coord = input_shape->dims[input_index] == 1U
            ? 0U
            : output_coords[output_index];
        if (coord >= input_shape->dims[input_index]) return HHS_NUMPY_NATIVE_ERR_INDEX;
        if (coord != 0U && input_stride > UINT64_MAX / coord) {
            return HHS_NUMPY_NATIVE_ERR_OVERFLOW;
        }
        input_linear += coord * input_stride;
        if (input_index > 0U) {
            if (input_stride > UINT64_MAX / input_shape->dims[input_index]) {
                return HHS_NUMPY_NATIVE_ERR_OVERFLOW;
            }
            input_stride *= input_shape->dims[input_index];
        }
    }

    if (input_linear >= input_count) return HHS_NUMPY_NATIVE_ERR_INDEX;
    *out_input_linear_index = input_linear;
    return HHS_NUMPY_NATIVE_OK;
}
