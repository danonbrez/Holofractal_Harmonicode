#include "hhs_p164_gcmsl.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void test_geometry(void) {
    hhs_p164_geometry_t geometry;
    assert(hhs_p164_geometry_status(&geometry) == HHS_P164_OK);
    assert(hhs_p164_validate_geometry(&geometry) == HHS_P164_OK);
    assert(geometry.phase_squared == UINT64_C(5184));
    assert(geometry.thread_vm81_product == UINT64_C(5184));
    assert(geometry.determinant == INT64_C(0));
    geometry.phase_dimension = UINT32_C(71);
    assert(hhs_p164_validate_geometry(&geometry) == HHS_P164_GEOMETRY_MISMATCH);
}

static void test_all_coordinates(void) {
    uint32_t vm81_position;
    uint32_t thread;
    uint8_t phase_seen[HHS_P164_BRIDGE_CARDINALITY];
    memset(phase_seen, 0, sizeof(phase_seen));
    for (vm81_position = 0U; vm81_position < HHS_P164_VM81_DIMENSION; ++vm81_position) {
        for (thread = 0U; thread < HHS_P164_THREAD_DIMENSION; ++thread) {
            hhs_p164_vm_thread_coordinate_t vm_thread = {vm81_position, thread};
            hhs_p164_phase_coordinate_t phase;
            hhs_p164_vm_thread_coordinate_t inverse;
            uint32_t phase_index;
            assert(hhs_p164_vm_thread_to_phase(&vm_thread, &phase) == HHS_P164_OK);
            phase_index = phase.phase_a * HHS_P164_PHASE_DIMENSION + phase.phase_b;
            assert(phase_index < HHS_P164_BRIDGE_CARDINALITY);
            assert(phase_seen[phase_index] == 0U);
            phase_seen[phase_index] = 1U;
            assert(hhs_p164_phase_to_vm_thread(&phase, &inverse) == HHS_P164_OK);
            assert(inverse.vm81_position == vm81_position);
            assert(inverse.thread == thread);
        }
    }
    for (vm81_position = 0U; vm81_position < HHS_P164_BRIDGE_CARDINALITY; ++vm81_position) {
        assert(phase_seen[vm81_position] == 1U);
    }
}

static void test_scale(void) {
    hhs_p164_scale_geometry_t scale;
    assert(hhs_p164_scale_geometry(UINT32_C(2), &scale) == HHS_P164_OK);
    assert(scale.q_c == UINT64_C(162));
    assert(scale.p_upper_c == UINT64_C(144));
    assert(scale.p_lower_c == UINT64_C(128));
    assert(scale.p_upper_squared == UINT64_C(20736));
    assert(scale.p_lower_q_product == UINT64_C(20736));
    assert(scale.dense_capacity == UINT64_C(63364));
    assert(hhs_p164_scale_geometry(UINT32_C(0), &scale) == HHS_P164_INVALID_ARGUMENT);
}

static void test_invariant(void) {
    hhs_p164_invariant_residual_t residual;
    int32_t omega;
    uint64_t norm;
    int64_t lhs;
    memset(&residual, 0, sizeof(residual));
    assert(hhs_p164_invariant_close(&residual, &omega, &norm, &lhs) == HHS_P164_OK);
    assert(omega == INT32_C(0));
    assert(norm == UINT64_C(0));
    assert(lhs == INT64_C(0));
    residual.geometry = INT64_C(1);
    residual.thread = -INT64_C(1);
    assert(hhs_p164_invariant_close(&residual, &omega, &norm, &lhs) == HHS_P164_INVARIANT_OPEN);
    assert(omega == -INT32_C(1));
    assert(norm == UINT64_C(2));
    assert(lhs == -INT64_C(2));
}

static void test_stable_key(void) {
    hhs_p164_operation_key_t left;
    hhs_p164_operation_key_t right;
    memset(&left, 0, sizeof(left));
    memset(&right, 0, sizeof(right));
    left.epoch = UINT64_C(1);
    right.epoch = UINT64_C(1);
    left.order = UINT32_C(1);
    right.order = UINT32_C(2);
    assert(hhs_p164_operation_key_compare(&left, &right) < 0);
    right.order = UINT32_C(1);
    assert(hhs_p164_operation_key_compare(&left, &right) == 0);
    right.identity[31] = UINT8_C(1);
    assert(hhs_p164_operation_key_compare(&left, &right) < 0);
}

int main(void) {
    test_geometry();
    test_all_coordinates();
    test_scale();
    test_invariant();
    test_stable_key();
    puts("HHS_PASS_164_NATIVE_TESTS_PASS");
    return 0;
}
