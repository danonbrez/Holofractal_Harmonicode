#include "hhs_pass220_numpy_native_array_kernel_v1.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

static HHSNumpyNativeShapeV1 shape2(uint64_t a, uint64_t b) {
    HHSNumpyNativeShapeV1 s = {0};
    s.rank = 2U;
    s.dims[0] = a;
    s.dims[1] = b;
    return s;
}

int main(void) {
    HHSNumpyNativeShapeV1 left = shape2(2U, 1U);
    HHSNumpyNativeShapeV1 right = shape2(1U, 3U);
    HHSNumpyNativeShapeV1 out = {0};
    HHSNumpyNativeShapeV1 scalar = {0};
    uint64_t count = 0U;
    uint64_t projected = 0U;

    assert(hhs_numpy_native_array_kernel_version() == 1U);
    assert(hhs_numpy_native_broadcast_shape(&left, &right, &out) == HHS_NUMPY_NATIVE_OK);
    assert(out.rank == 2U);
    assert(out.dims[0] == 2U);
    assert(out.dims[1] == 3U);
    assert(hhs_numpy_native_element_count(&out, &count) == HHS_NUMPY_NATIVE_OK);
    assert(count == 6U);

    /* Output index 5 is coordinate (1,2). Left (2,1) projects to (1,0) => 1. */
    assert(hhs_numpy_native_project_broadcast_index(&out, 5U, &left, &projected) == HHS_NUMPY_NATIVE_OK);
    assert(projected == 1U);

    /* Right (1,3) projects to (0,2) => 2. */
    assert(hhs_numpy_native_project_broadcast_index(&out, 5U, &right, &projected) == HHS_NUMPY_NATIVE_OK);
    assert(projected == 2U);

    assert(hhs_numpy_native_project_broadcast_index(&out, 4U, &scalar, &projected) == HHS_NUMPY_NATIVE_OK);
    assert(projected == 0U);

    {
        HHSNumpyNativeShapeV1 bad = shape2(2U, 2U);
        assert(hhs_numpy_native_broadcast_shape(&bad, &right, &out) == HHS_NUMPY_NATIVE_ERR_BROADCAST);
    }

    puts("PASS hhs_pass220_numpy_native_array_kernel_v1");
    return 0;
}
