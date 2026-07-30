#ifndef HHS_P174_RUNTIME_H
#define HHS_P174_RUNTIME_H

#include <stddef.h>
#include <stdint.h>

#include "hhs_p163_vmrc.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_P174_ABI_VERSION UINT32_C(1)
#define HHS_P174_PHASE_64 UINT32_C(64)
#define HHS_P174_PHASE_72 UINT32_C(72)
#define HHS_P174_PHASE_81 UINT32_C(81)
#define HHS_P174_PHASE_LOCK_PERIOD UINT32_C(5184)
#define HHS_P174_HASH72_CHARACTERS UINT32_C(72)
#define HHS_P174_HASH216_CHARACTERS UINT32_C(216)
#define HHS_P174_SHA256_BYTES UINT32_C(32)
#define HHS_P174_MAX_WRITES UINT32_C(5184)

typedef enum hhs_p174_status {
    HHS_P174_OK = 0,
    HHS_P174_INVALID_ARGUMENT = 1,
    HHS_P174_OUT_OF_RANGE = 2,
    HHS_P174_BUFFER_TOO_SMALL = 3,
    HHS_P174_AUTHORITY_DENIED = 4,
    HHS_P174_HASH216_LENGTH_MISMATCH = 5,
    HHS_P174_OVERLAPPING_WRITE_CONFLICT = 6
} hhs_p174_status;

typedef enum hhs_p174_execution_path {
    HHS_P174_EXECUTE_DIRECT = 0,
    HHS_P174_EXECUTE_RETRIEVAL = 1,
    HHS_P174_EXECUTE_EQUAL_COST_DIRECT = 2
} hhs_p174_execution_path;

typedef struct hhs_p174_phase_coordinate {
    uint32_t abi_version;
    uint64_t logical_step;
    uint32_t phase64;
    uint32_t phase72;
    uint32_t phase81;
    uint32_t phase5184;
    uint8_t lock64_72;
    uint8_t lock72_81;
    uint8_t full_phase_lock;
} hhs_p174_phase_coordinate;

typedef struct hhs_p174_frame_write {
    uint32_t position;
    uint32_t thread;
    uint8_t value;
} hhs_p174_frame_write;

hhs_p174_status hhs_p174_phase_at(
    uint64_t logical_step,
    hhs_p174_phase_coordinate *coordinate_out
);

hhs_p174_status hhs_p174_build_candidate_frame(
    const hhs_p163_vmrc_snapshot *source,
    const hhs_p174_frame_write *writes,
    size_t write_count,
    const void *authority_token,
    const void *expected_authority_token,
    hhs_p163_vmrc_snapshot *candidate_out
);

hhs_p174_status hhs_p174_hash216_join(
    const char *predecessor,
    size_t predecessor_length,
    const char *current,
    size_t current_length,
    const char *successor,
    size_t successor_length,
    char *combined_out,
    size_t combined_capacity
);

hhs_p174_status hhs_p174_hash216_indexes(
    const char *combined,
    size_t combined_length,
    const uint8_t logical_identity[HHS_P174_SHA256_BYTES],
    uint8_t indexes_out[HHS_P174_HASH216_CHARACTERS][HHS_P174_SHA256_BYTES],
    uint8_t index_root_out[HHS_P174_SHA256_BYTES]
);

hhs_p174_status hhs_p174_select_execution_path(
    uint64_t direct_cost_units,
    uint64_t retrieval_cost_units,
    hhs_p174_execution_path *path_out,
    int64_t *retrieval_advantage_out
);

#ifdef __cplusplus
}
#endif

#endif
