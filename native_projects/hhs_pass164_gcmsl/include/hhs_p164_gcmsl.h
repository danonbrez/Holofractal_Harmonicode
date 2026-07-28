#ifndef HHS_P164_GCMSL_H
#define HHS_P164_GCMSL_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_P164_ABI_VERSION UINT32_C(1)
#define HHS_P164_PHASE_DIMENSION UINT32_C(72)
#define HHS_P164_THREAD_DIMENSION UINT32_C(64)
#define HHS_P164_VM81_DIMENSION UINT32_C(81)
#define HHS_P164_BRIDGE_CARDINALITY UINT32_C(5184)
#define HHS_P164_DENSE_CAPACITY UINT32_C(15841)

#define HHS_P164_OK 0
#define HHS_P164_INVALID_ARGUMENT 1
#define HHS_P164_OUT_OF_RANGE 2
#define HHS_P164_GEOMETRY_MISMATCH 3
#define HHS_P164_OVERFLOW 4
#define HHS_P164_INVARIANT_OPEN 5

typedef struct hhs_p164_geometry {
    uint32_t abi_version;
    uint32_t phase_dimension;
    uint32_t thread_dimension;
    uint32_t vm81_dimension;
    uint64_t phase_squared;
    uint64_t thread_vm81_product;
    int64_t determinant;
} hhs_p164_geometry_t;

typedef struct hhs_p164_vm_thread_coordinate {
    uint32_t vm81_position;
    uint32_t thread;
} hhs_p164_vm_thread_coordinate_t;

typedef struct hhs_p164_phase_coordinate {
    uint32_t phase_a;
    uint32_t phase_b;
} hhs_p164_phase_coordinate_t;

typedef struct hhs_p164_scale_geometry {
    uint32_t scale;
    uint64_t q_c;
    uint64_t p_upper_c;
    uint64_t p_lower_c;
    uint64_t p_upper_squared;
    uint64_t p_lower_q_product;
    uint64_t dense_capacity;
} hhs_p164_scale_geometry_t;

typedef struct hhs_p164_invariant_residual {
    int64_t authority;
    int64_t geometry;
    int64_t thread;
    int64_t phase;
    int64_t memristor;
    int64_t capability_conflict;
    int64_t hash_identity;
    int64_t replay_reduction;
    int64_t egress;
} hhs_p164_invariant_residual_t;

typedef struct hhs_p164_operation_key {
    uint64_t epoch;
    uint32_t level;
    uint32_t phase;
    uint32_t cluster;
    uint32_t order;
    uint32_t vm81_position;
    uint32_t thread;
    uint8_t identity[32];
} hhs_p164_operation_key_t;

int hhs_p164_geometry_status(hhs_p164_geometry_t *out_geometry);
int hhs_p164_validate_geometry(const hhs_p164_geometry_t *geometry);
int hhs_p164_vm_thread_to_phase(
    const hhs_p164_vm_thread_coordinate_t *input,
    hhs_p164_phase_coordinate_t *output
);
int hhs_p164_phase_to_vm_thread(
    const hhs_p164_phase_coordinate_t *input,
    hhs_p164_vm_thread_coordinate_t *output
);
int hhs_p164_scale_geometry(uint32_t scale, hhs_p164_scale_geometry_t *output);
int hhs_p164_invariant_close(
    const hhs_p164_invariant_residual_t *residual,
    int32_t *omega,
    uint64_t *residual_norm,
    int64_t *equation_lhs
);
int hhs_p164_operation_key_compare(
    const hhs_p164_operation_key_t *left,
    const hhs_p164_operation_key_t *right
);

#ifdef __cplusplus
}
#endif

#endif
