#ifndef HHS_NFV_CONTRACT_H
#define HHS_NFV_CONTRACT_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>
#include <stdint.h>

#include "hhs_hash216.h"

#define HHS_NFV_ABI_VERSION 0x00010000u
#define HHS_NFV_TRANSITION_COPY_ON_WRITE 0x00000001u

typedef enum hhs_nfv_status {
    HHS_NFV_STATUS_OK = 0,
    HHS_NFV_STATUS_INVALID_ARGUMENT = 1,
    HHS_NFV_STATUS_ABI_MISMATCH = 2,
    HHS_NFV_STATUS_RESOURCE_BOUNDED = 3,
    HHS_NFV_STATUS_BUFFER_TOO_SMALL = 4,
    HHS_NFV_STATUS_STALE_REFERENCE = 5,
    HHS_NFV_STATUS_AUTHORITY_UNBOUND = 6,
    HHS_NFV_STATUS_VM81_REJECTED = 7,
    HHS_NFV_STATUS_RECEIPT_MISMATCH = 8,
    HHS_NFV_STATUS_ALREADY_CLOSED = 9,
    HHS_NFV_STATUS_ALLOCATION_FAILED = 10,
    HHS_NFV_STATUS_INTERNAL_ERROR = 11
} hhs_nfv_status;

typedef int (*hhs_nfv_vm81_admit_fn)(
    const uint8_t* prior_state,
    size_t prior_state_size,
    const uint8_t* candidate_state,
    size_t candidate_state_size,
    void* user_data
);

typedef struct hhs_nfv_config {
    uint32_t struct_size;
    uint32_t abi_version;
    size_t max_state_bytes;
    hhs_nfv_vm81_admit_fn vm81_admit;
    void* user_data;
} hhs_nfv_config;

typedef struct hhs_nfv_object_descriptor {
    uint32_t struct_size;
    uint32_t abi_version;
    const char* object_type;
    size_t object_type_size;
    const char* authority_root;
    size_t authority_root_size;
    const uint8_t* initial_state;
    size_t initial_state_size;
} hhs_nfv_object_descriptor;

typedef struct hhs_nfv_transition_request {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t flags;
    uint32_t reserved;
    uint64_t expected_version;
    uint64_t expected_generation;
    const char* constructor_id;
    size_t constructor_id_size;
    const uint8_t* candidate_state;
    size_t candidate_state_size;
} hhs_nfv_transition_request;

typedef struct hhs_nfv_metadata {
    uint32_t struct_size;
    uint32_t abi_version;
    uint64_t version;
    uint64_t generation;
    size_t state_size;
    HHSHash72 receipt_head;
    HHSHash216 object_index;
} hhs_nfv_metadata;

typedef struct hhs_nfv_handle hhs_nfv_handle;
typedef struct hhs_nfv_transition hhs_nfv_transition;

hhs_nfv_status hhs_nfv_validate_abi(uint32_t abi_version);

hhs_nfv_status hhs_nfv_create(
    const hhs_nfv_config* config,
    const hhs_nfv_object_descriptor* descriptor,
    hhs_nfv_handle** out_handle
);

void hhs_nfv_close(hhs_nfv_handle* handle);

hhs_nfv_status hhs_nfv_get_metadata(
    const hhs_nfv_handle* handle,
    hhs_nfv_metadata* out_metadata
);

hhs_nfv_status hhs_nfv_read_state(
    const hhs_nfv_handle* handle,
    uint8_t* out_state,
    size_t* inout_state_size
);

hhs_nfv_status hhs_nfv_prepare_transition(
    const hhs_nfv_handle* handle,
    const hhs_nfv_transition_request* request,
    hhs_nfv_transition** out_transition
);

hhs_nfv_status hhs_nfv_commit_transition(
    hhs_nfv_handle* handle,
    hhs_nfv_transition* transition
);

hhs_nfv_status hhs_nfv_reverse_transition(
    hhs_nfv_handle* handle,
    hhs_nfv_transition* transition
);

void hhs_nfv_transition_close(hhs_nfv_transition* transition);

#ifdef __cplusplus
}
#endif

#endif
