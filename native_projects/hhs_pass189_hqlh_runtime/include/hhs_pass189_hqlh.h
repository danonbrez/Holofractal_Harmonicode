#ifndef HHS_PASS189_HQLH_H
#define HHS_PASS189_HQLH_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS189_VM81_CELLS UINT32_C(81)
#define HHS189_OPERATIONS_PER_CELL UINT32_C(64)
#define HHS189_G243_CONTROLS UINT32_C(243)
#define HHS189_PERMANENT_STATES UINT32_C(5184)
#define HHS189_PROJECTED_STATES UINT32_C(1259712)
#define HHS189_LOCAL_COORDINATES UINT32_C(41)
#define HHS189_CONTEXTUAL_STATES UINT32_C(51648192)
#define HHS189_Q144_STATES UINT32_C(144)
#define HHS189_U72_STATES UINT32_C(72)
#define HHS189_GLOBAL_NUCLEUS UINT8_C(40)

#define HHS189_OK 0
#define HHS189_ERR_NULL 1
#define HHS189_ERR_RANGE 2
#define HHS189_ERR_DRIFT 3
#define HHS189_ERR_INVARIANT 4

typedef struct HHS189ContextAddress {
    uint32_t extended;
    uint32_t projected;
    uint32_t permanent;
    uint16_t g243;
    uint8_t cell81;
    uint8_t operation64;
    uint8_t operation_class8;
    uint8_t ordered_basis8;
    uint8_t kappa41;
    int8_t local_k;
    uint8_t layer36;
    uint8_t q144_row;
    uint8_t q144_column;
    uint8_t u72_pair;
    uint8_t u72_index;
} HHS189ContextAddress;

typedef struct HHS189PartitionResult {
    uint32_t start;
    uint32_t end;
    uint64_t visited;
    uint64_t reciprocal_checks;
    uint64_t coordinate_drift;
    uint64_t checksum;
} HHS189PartitionResult;

int hhs189_decode_context(uint32_t extended, HHS189ContextAddress *out);
int hhs189_encode_context(const HHS189ContextAddress *address, uint32_t *extended_out);
int hhs189_lo_shu_delta(int8_t local_k, int8_t *delta_out);
int hhs189_local_cell(uint8_t cell81, int8_t local_k, uint8_t *cell_out);
uint8_t hhs189_xnor_bit(uint8_t a, uint8_t b);
int8_t hhs189_signed_xnor(uint8_t a, uint8_t b);
int8_t hhs189_ternary_orientation(uint8_t cell81, uint8_t nucleus81, uint8_t a, uint8_t b);
int hhs189_validate_partition(uint32_t start, uint32_t end, HHS189PartitionResult *out);
const int8_t *hhs189_lo_shu_positive_delta_table(size_t *count_out);

#ifdef __cplusplus
}
#endif

#endif
