#include "hhs_p164_gcmsl.h"

#include <limits.h>
#include <string.h>

static int hhs_p164_mul_u64(uint64_t left, uint64_t right, uint64_t *output) {
    if (output == NULL) {
        return HHS_P164_INVALID_ARGUMENT;
    }
    if (left != UINT64_C(0) && right > UINT64_MAX / left) {
        return HHS_P164_OVERFLOW;
    }
    *output = left * right;
    return HHS_P164_OK;
}

static uint64_t hhs_p164_abs_i64(int64_t value) {
    if (value >= INT64_C(0)) {
        return (uint64_t)value;
    }
    return (uint64_t)(-(value + INT64_C(1))) + UINT64_C(1);
}

int hhs_p164_geometry_status(hhs_p164_geometry_t *out_geometry) {
    if (out_geometry == NULL) {
        return HHS_P164_INVALID_ARGUMENT;
    }
    out_geometry->abi_version = HHS_P164_ABI_VERSION;
    out_geometry->phase_dimension = HHS_P164_PHASE_DIMENSION;
    out_geometry->thread_dimension = HHS_P164_THREAD_DIMENSION;
    out_geometry->vm81_dimension = HHS_P164_VM81_DIMENSION;
    out_geometry->phase_squared = UINT64_C(72) * UINT64_C(72);
    out_geometry->thread_vm81_product = UINT64_C(64) * UINT64_C(81);
    out_geometry->determinant =
        (int64_t)out_geometry->thread_vm81_product -
        (int64_t)out_geometry->phase_squared;
    return HHS_P164_OK;
}

int hhs_p164_validate_geometry(const hhs_p164_geometry_t *geometry) {
    if (geometry == NULL) {
        return HHS_P164_INVALID_ARGUMENT;
    }
    if (
        geometry->abi_version != HHS_P164_ABI_VERSION ||
        geometry->phase_dimension != HHS_P164_PHASE_DIMENSION ||
        geometry->thread_dimension != HHS_P164_THREAD_DIMENSION ||
        geometry->vm81_dimension != HHS_P164_VM81_DIMENSION ||
        geometry->phase_squared != HHS_P164_BRIDGE_CARDINALITY ||
        geometry->thread_vm81_product != HHS_P164_BRIDGE_CARDINALITY ||
        geometry->determinant != INT64_C(0)
    ) {
        return HHS_P164_GEOMETRY_MISMATCH;
    }
    return HHS_P164_OK;
}

int hhs_p164_vm_thread_to_phase(
    const hhs_p164_vm_thread_coordinate_t *input,
    hhs_p164_phase_coordinate_t *output
) {
    uint32_t linear;
    if (input == NULL || output == NULL) {
        return HHS_P164_INVALID_ARGUMENT;
    }
    if (
        input->vm81_position >= HHS_P164_VM81_DIMENSION ||
        input->thread >= HHS_P164_THREAD_DIMENSION
    ) {
        return HHS_P164_OUT_OF_RANGE;
    }
    linear = input->vm81_position * HHS_P164_THREAD_DIMENSION + input->thread;
    output->phase_a = linear / HHS_P164_PHASE_DIMENSION;
    output->phase_b = linear % HHS_P164_PHASE_DIMENSION;
    return HHS_P164_OK;
}

int hhs_p164_phase_to_vm_thread(
    const hhs_p164_phase_coordinate_t *input,
    hhs_p164_vm_thread_coordinate_t *output
) {
    uint32_t linear;
    if (input == NULL || output == NULL) {
        return HHS_P164_INVALID_ARGUMENT;
    }
    if (
        input->phase_a >= HHS_P164_PHASE_DIMENSION ||
        input->phase_b >= HHS_P164_PHASE_DIMENSION
    ) {
        return HHS_P164_OUT_OF_RANGE;
    }
    linear = input->phase_a * HHS_P164_PHASE_DIMENSION + input->phase_b;
    output->vm81_position = linear / HHS_P164_THREAD_DIMENSION;
    output->thread = linear % HHS_P164_THREAD_DIMENSION;
    return HHS_P164_OK;
}

int hhs_p164_scale_geometry(uint32_t scale, hhs_p164_scale_geometry_t *output) {
    uint64_t scale64;
    uint64_t scale_squared;
    int status;
    if (output == NULL || scale == UINT32_C(0)) {
        return HHS_P164_INVALID_ARGUMENT;
    }
    scale64 = (uint64_t)scale;
    status = hhs_p164_mul_u64(scale64, scale64, &scale_squared);
    if (status != HHS_P164_OK) {
        return status;
    }
    output->scale = scale;
    status = hhs_p164_mul_u64(UINT64_C(81), scale64, &output->q_c);
    if (status != HHS_P164_OK) return status;
    status = hhs_p164_mul_u64(UINT64_C(72), scale64, &output->p_upper_c);
    if (status != HHS_P164_OK) return status;
    status = hhs_p164_mul_u64(UINT64_C(64), scale64, &output->p_lower_c);
    if (status != HHS_P164_OK) return status;
    status = hhs_p164_mul_u64(UINT64_C(5184), scale_squared, &output->p_upper_squared);
    if (status != HHS_P164_OK) return status;
    output->p_lower_q_product = output->p_upper_squared;
    status = hhs_p164_mul_u64(UINT64_C(15841), scale_squared, &output->dense_capacity);
    if (status != HHS_P164_OK) return status;
    return HHS_P164_OK;
}

int hhs_p164_invariant_close(
    const hhs_p164_invariant_residual_t *residual,
    int32_t *omega,
    uint64_t *residual_norm,
    int64_t *equation_lhs
) {
    const int64_t values[9] = {
        residual != NULL ? residual->authority : INT64_C(0),
        residual != NULL ? residual->geometry : INT64_C(0),
        residual != NULL ? residual->thread : INT64_C(0),
        residual != NULL ? residual->phase : INT64_C(0),
        residual != NULL ? residual->memristor : INT64_C(0),
        residual != NULL ? residual->capability_conflict : INT64_C(0),
        residual != NULL ? residual->hash_identity : INT64_C(0),
        residual != NULL ? residual->replay_reduction : INT64_C(0),
        residual != NULL ? residual->egress : INT64_C(0)
    };
    uint64_t norm = UINT64_C(0);
    int has_negative = 0;
    size_t index;
    if (residual == NULL || omega == NULL || residual_norm == NULL || equation_lhs == NULL) {
        return HHS_P164_INVALID_ARGUMENT;
    }
    for (index = 0U; index < 9U; ++index) {
        uint64_t magnitude = hhs_p164_abs_i64(values[index]);
        if (UINT64_MAX - norm < magnitude) {
            return HHS_P164_OVERFLOW;
        }
        norm += magnitude;
        if (values[index] < INT64_C(0)) {
            has_negative = 1;
        }
    }
    *residual_norm = norm;
    if (norm == UINT64_C(0)) {
        *omega = INT32_C(0);
        *equation_lhs = INT64_C(0);
        return HHS_P164_OK;
    }
    *omega = has_negative != 0 ? -INT32_C(1) : INT32_C(1);
    if (norm > (uint64_t)INT64_MAX) {
        return HHS_P164_OVERFLOW;
    }
    *equation_lhs = -(int64_t)norm;
    return HHS_P164_INVARIANT_OPEN;
}

int hhs_p164_operation_key_compare(
    const hhs_p164_operation_key_t *left,
    const hhs_p164_operation_key_t *right
) {
    int identity_compare;
    if (left == NULL || right == NULL) {
        return HHS_P164_INVALID_ARGUMENT;
    }
#define HHS_P164_COMPARE_FIELD(field) \
    do { \
        if (left->field < right->field) return -1; \
        if (left->field > right->field) return 1; \
    } while (0)
    HHS_P164_COMPARE_FIELD(epoch);
    HHS_P164_COMPARE_FIELD(level);
    HHS_P164_COMPARE_FIELD(phase);
    HHS_P164_COMPARE_FIELD(cluster);
    HHS_P164_COMPARE_FIELD(order);
    HHS_P164_COMPARE_FIELD(vm81_position);
    HHS_P164_COMPARE_FIELD(thread);
#undef HHS_P164_COMPARE_FIELD
    identity_compare = memcmp(left->identity, right->identity, sizeof(left->identity));
    if (identity_compare < 0) return -1;
    if (identity_compare > 0) return 1;
    return 0;
}
