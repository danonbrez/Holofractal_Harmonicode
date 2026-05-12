// hhs_runtime/include/hhs_tensor81.h
//
// HHS / HARMONICODE
// Canonical Tensor81 Geometry ABI
//
// Runtime Principle:
//
//   Tensor81
//   =
//   canonical runtime manifold geometry
//
// NOT:
//   VM-local execution storage
//

#ifndef HHS_TENSOR81_H
#define HHS_TENSOR81_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

#define HHS_TENSOR81_SIZE 81
#define HHS_LOSHU_CLUSTER_COUNT 9
#define HHS_PHASE_LAYER_COUNT 4

/*
 * Canonical Lo Shu topology.
 */

static const uint8_t HHS_LOSHU[9] = {
    4, 9, 2,
    3, 5, 7,
    8, 1, 6
};

/*
 * Canonical Tensor81 cell.
 */

typedef struct HHSVMCell {

    int64_t value;

    uint8_t phase;
    uint8_t occupied;

} HHSVMCell;

/*
 * Canonical Tensor81 manifold geometry.
 */

typedef struct HHSTensor81 {

    HHSVMCell cells[
        HHS_TENSOR81_SIZE
    ];

} HHSTensor81;

/*
 * Tensor81 API
 */

void hhs_tensor81_clear(
    HHSTensor81* tensor
);

HHSVMCell* hhs_tensor81_cell(
    HHSTensor81* tensor,
    uint32_t index
);

const HHSVMCell* hhs_tensor81_const_cell(
    const HHSTensor81* tensor,
    uint32_t index
);

uint8_t hhs_tensor81_cluster(
    uint32_t index
);

uint8_t hhs_tensor81_phase_layer(
    uint32_t index
);

#ifdef __cplusplus
}
#endif

#endif