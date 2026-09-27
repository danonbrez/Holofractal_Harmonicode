#ifndef HHS_PASS220_NUMPY_NATIVE_ARRAY_KERNEL_V1_H
#define HHS_PASS220_NUMPY_NATIVE_ARRAY_KERNEL_V1_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_NUMPY_NATIVE_ARRAY_KERNEL_VERSION 1U
#define HHS_NUMPY_NATIVE_MAX_RANK 8U

typedef enum HHSNumpyNativeStatusV1 {
    HHS_NUMPY_NATIVE_OK = 0,
    HHS_NUMPY_NATIVE_ERR_ARGUMENT = 1,
    HHS_NUMPY_NATIVE_ERR_RANK = 2,
    HHS_NUMPY_NATIVE_ERR_DIMENSION = 3,
    HHS_NUMPY_NATIVE_ERR_BROADCAST = 4,
    HHS_NUMPY_NATIVE_ERR_OVERFLOW = 5,
    HHS_NUMPY_NATIVE_ERR_INDEX = 6
} HHSNumpyNativeStatusV1;

typedef struct HHSNumpyNativeShapeV1 {
    uint32_t rank;
    uint64_t dims[HHS_NUMPY_NATIVE_MAX_RANK];
} HHSNumpyNativeShapeV1;

uint32_t hhs_numpy_native_array_kernel_version(void);

HHSNumpyNativeStatusV1 hhs_numpy_native_shape_validate(
    const HHSNumpyNativeShapeV1 *shape
);

HHSNumpyNativeStatusV1 hhs_numpy_native_element_count(
    const HHSNumpyNativeShapeV1 *shape,
    uint64_t *out_count
);

HHSNumpyNativeStatusV1 hhs_numpy_native_broadcast_shape(
    const HHSNumpyNativeShapeV1 *left,
    const HHSNumpyNativeShapeV1 *right,
    HHSNumpyNativeShapeV1 *out
);

HHSNumpyNativeStatusV1 hhs_numpy_native_project_broadcast_index(
    const HHSNumpyNativeShapeV1 *output_shape,
    uint64_t output_linear_index,
    const HHSNumpyNativeShapeV1 *input_shape,
    uint64_t *out_input_linear_index
);

#ifdef __cplusplus
}
#endif

#endif
