#include "../include/hhs_nfv_contract.h"

#include <stdlib.h>
#include <string.h>

#define HHS_NFV_DOMAIN_OBJECT "HHS-NFV-C-OBJECT-V1"
#define HHS_NFV_DOMAIN_PACKAGE "HHS-NFV-C-PACKAGE-V1"
#define HHS_NFV_DOMAIN_RECEIPT "HHS-NFV-C-RECEIPT-V1"
#define HHS_NFV_DOMAIN_REVERSE "HHS-NFV-C-REVERSE-V1"

typedef struct hhs_nfv_buffer {
    uint8_t* data;
    size_t size;
    size_t capacity;
} hhs_nfv_buffer;

struct hhs_nfv_handle {
    uint8_t* object_type;
    size_t object_type_size;
    uint8_t* authority_root;
    size_t authority_root_size;
    uint8_t* state;
    size_t state_size;
    size_t max_state_bytes;
    uint64_t version;
    uint64_t generation;
    HHSHash72 receipt_head;
    HHSHash216 object_index;
    hhs_nfv_vm81_admit_fn vm81_admit;
    void* user_data;
};

struct hhs_nfv_transition {
    uint8_t* constructor_id;
    size_t constructor_id_size;
    uint8_t* candidate_state;
    size_t candidate_state_size;
    uint8_t* inverse_state;
    size_t inverse_state_size;
    uint64_t expected_version;
    uint64_t expected_generation;
    uint32_t flags;
    HHSHash216 expected_object_index;
    HHSHash216 package_index;
    HHSHash72 committed_receipt;
    int committed;
    int reversed;
};

static void hhs_nfv_secure_free(void* ptr, size_t size) {
    volatile uint8_t* p = (volatile uint8_t*)ptr;
    size_t i;
    if (!ptr) {
        return;
    }
    for (i = 0; i < size; ++i) {
        p[i] = 0;
    }
    free(ptr);
}

static uint8_t* hhs_nfv_copy_bytes(const void* data, size_t size) {
    uint8_t* copy;
    if (size == 0) {
        return NULL;
    }
    if (!data) {
        return NULL;
    }
    copy = (uint8_t*)malloc(size);
    if (!copy) {
        return NULL;
    }
    memcpy(copy, data, size);
    return copy;
}

static int hhs_nfv_buffer_reserve(hhs_nfv_buffer* buffer, size_t additional) {
    size_t required;
    size_t capacity;
    uint8_t* next;
    if (additional > SIZE_MAX - buffer->size) {
        return 0;
    }
    required = buffer->size + additional;
    if (required <= buffer->capacity) {
        return 1;
    }
    capacity = buffer->capacity ? buffer->capacity : 128u;
    while (capacity < required) {
        if (capacity > SIZE_MAX / 2u) {
            capacity = required;
            break;
        }
        capacity *= 2u;
    }
    next = (uint8_t*)realloc(buffer->data, capacity);
    if (!next) {
        return 0;
    }
    buffer->data = next;
    buffer->capacity = capacity;
    return 1;
}

static int hhs_nfv_buffer_append(hhs_nfv_buffer* buffer, const void* data, size_t size) {
    if (!hhs_nfv_buffer_reserve(buffer, size)) {
        return 0;
    }
    if (size > 0) {
        memcpy(buffer->data + buffer->size, data, size);
        buffer->size += size;
    }
    return 1;
}

static int hhs_nfv_buffer_append_u64(hhs_nfv_buffer* buffer, uint64_t value) {
    uint8_t encoded[8];
    size_t i;
    for (i = 0; i < 8; ++i) {
        encoded[7u - i] = (uint8_t)(value & 0xffu);
        value >>= 8u;
    }
    return hhs_nfv_buffer_append(buffer, encoded, sizeof(encoded));
}

static int hhs_nfv_buffer_append_field(hhs_nfv_buffer* buffer, const void* data, size_t size) {
    return hhs_nfv_buffer_append_u64(buffer, (uint64_t)size) && hhs_nfv_buffer_append(buffer, data, size);
}

static void hhs_nfv_buffer_destroy(hhs_nfv_buffer* buffer) {
    if (!buffer) {
        return;
    }
    hhs_nfv_secure_free(buffer->data, buffer->capacity);
    buffer->data = NULL;
    buffer->size = 0;
    buffer->capacity = 0;
}

static int hhs_nfv_compute_object_index(
    const hhs_nfv_handle* handle,
    const uint8_t* state,
    size_t state_size,
    uint64_t version,
    uint64_t generation,
    const HHSHash72* receipt,
    HHSHash216* out_index
) {
    hhs_nfv_buffer buffer = {0};
    int ok =
        hhs_nfv_buffer_append_field(&buffer, HHS_NFV_DOMAIN_OBJECT, sizeof(HHS_NFV_DOMAIN_OBJECT) - 1u) &&
        hhs_nfv_buffer_append_field(&buffer, handle->object_type, handle->object_type_size) &&
        hhs_nfv_buffer_append_field(&buffer, handle->authority_root, handle->authority_root_size) &&
        hhs_nfv_buffer_append_u64(&buffer, version) &&
        hhs_nfv_buffer_append_u64(&buffer, generation) &&
        hhs_nfv_buffer_append_field(&buffer, receipt->value, HHS_HASH72_LEN) &&
        hhs_nfv_buffer_append_field(&buffer, state, state_size);
    if (ok) {
        hhs_hash216_compute(buffer.data, buffer.size, out_index);
    }
    hhs_nfv_buffer_destroy(&buffer);
    return ok;
}

static int hhs_nfv_compute_package_index(
    const hhs_nfv_handle* handle,
    const hhs_nfv_transition_request* request,
    const uint8_t* inverse_state,
    size_t inverse_state_size,
    HHSHash216* out_index
) {
    hhs_nfv_buffer buffer = {0};
    int ok =
        hhs_nfv_buffer_append_field(&buffer, HHS_NFV_DOMAIN_PACKAGE, sizeof(HHS_NFV_DOMAIN_PACKAGE) - 1u) &&
        hhs_nfv_buffer_append_field(&buffer, handle->object_index.value, HHS_HASH216_LEN) &&
        hhs_nfv_buffer_append_u64(&buffer, request->expected_version) &&
        hhs_nfv_buffer_append_u64(&buffer, request->expected_generation) &&
        hhs_nfv_buffer_append_field(&buffer, request->constructor_id, request->constructor_id_size) &&
        hhs_nfv_buffer_append_field(&buffer, request->candidate_state, request->candidate_state_size) &&
        hhs_nfv_buffer_append_field(&buffer, inverse_state, inverse_state_size) &&
        hhs_nfv_buffer_append_field(&buffer, handle->authority_root, handle->authority_root_size);
    if (ok) {
        hhs_hash216_compute(buffer.data, buffer.size, out_index);
    }
    hhs_nfv_buffer_destroy(&buffer);
    return ok;
}

static int hhs_nfv_compute_receipt(
    const char* domain,
    const HHSHash72* parent,
    const HHSHash216* package_index,
    const uint8_t* state,
    size_t state_size,
    uint64_t version,
    uint64_t generation,
    HHSHash72* out_receipt
) {
    hhs_nfv_buffer buffer = {0};
    int ok =
        hhs_nfv_buffer_append_field(&buffer, domain, strlen(domain)) &&
        hhs_nfv_buffer_append_field(&buffer, parent->value, HHS_HASH72_LEN) &&
        hhs_nfv_buffer_append_field(&buffer, package_index->value, HHS_HASH216_LEN) &&
        hhs_nfv_buffer_append_u64(&buffer, version) &&
        hhs_nfv_buffer_append_u64(&buffer, generation) &&
        hhs_nfv_buffer_append_field(&buffer, state, state_size);
    if (ok) {
        hhs_hash72_compute(buffer.data, buffer.size, out_receipt);
    }
    hhs_nfv_buffer_destroy(&buffer);
    return ok;
}

hhs_nfv_status hhs_nfv_validate_abi(uint32_t abi_version) {
    return abi_version == HHS_NFV_ABI_VERSION ? HHS_NFV_STATUS_OK : HHS_NFV_STATUS_ABI_MISMATCH;
}

hhs_nfv_status hhs_nfv_create(
    const hhs_nfv_config* config,
    const hhs_nfv_object_descriptor* descriptor,
    hhs_nfv_handle** out_handle
) {
    hhs_nfv_handle* handle;
    static const char genesis[] = "H72-NFV-GENESIS";
    if (!config || !descriptor || !out_handle) {
        return HHS_NFV_STATUS_INVALID_ARGUMENT;
    }
    *out_handle = NULL;
    if (config->struct_size != sizeof(*config) || descriptor->struct_size != sizeof(*descriptor) ||
        config->abi_version != HHS_NFV_ABI_VERSION || descriptor->abi_version != HHS_NFV_ABI_VERSION) {
        return HHS_NFV_STATUS_ABI_MISMATCH;
    }
    if (!config->vm81_admit) {
        return HHS_NFV_STATUS_AUTHORITY_UNBOUND;
    }
    if (!descriptor->object_type || descriptor->object_type_size == 0 ||
        !descriptor->authority_root || descriptor->authority_root_size == 0 ||
        (descriptor->initial_state_size > 0 && !descriptor->initial_state) ||
        config->max_state_bytes == 0 || descriptor->initial_state_size > config->max_state_bytes) {
        return HHS_NFV_STATUS_INVALID_ARGUMENT;
    }
    handle = (hhs_nfv_handle*)calloc(1u, sizeof(*handle));
    if (!handle) {
        return HHS_NFV_STATUS_ALLOCATION_FAILED;
    }
    handle->object_type = hhs_nfv_copy_bytes(descriptor->object_type, descriptor->object_type_size);
    handle->authority_root = hhs_nfv_copy_bytes(descriptor->authority_root, descriptor->authority_root_size);
    handle->state = hhs_nfv_copy_bytes(descriptor->initial_state, descriptor->initial_state_size);
    if (!handle->object_type || !handle->authority_root || (descriptor->initial_state_size > 0 && !handle->state)) {
        hhs_nfv_close(handle);
        return HHS_NFV_STATUS_ALLOCATION_FAILED;
    }
    handle->object_type_size = descriptor->object_type_size;
    handle->authority_root_size = descriptor->authority_root_size;
    handle->state_size = descriptor->initial_state_size;
    handle->max_state_bytes = config->max_state_bytes;
    handle->vm81_admit = config->vm81_admit;
    handle->user_data = config->user_data;
    handle->version = 0;
    handle->generation = 0;
    hhs_hash72_compute(genesis, sizeof(genesis) - 1u, &handle->receipt_head);
    if (!hhs_nfv_compute_object_index(handle, handle->state, handle->state_size, 0, 0, &handle->receipt_head, &handle->object_index)) {
        hhs_nfv_close(handle);
        return HHS_NFV_STATUS_ALLOCATION_FAILED;
    }
    *out_handle = handle;
    return HHS_NFV_STATUS_OK;
}

void hhs_nfv_close(hhs_nfv_handle* handle) {
    if (!handle) {
        return;
    }
    hhs_nfv_secure_free(handle->object_type, handle->object_type_size);
    hhs_nfv_secure_free(handle->authority_root, handle->authority_root_size);
    hhs_nfv_secure_free(handle->state, handle->state_size);
    memset(handle, 0, sizeof(*handle));
    free(handle);
}

hhs_nfv_status hhs_nfv_get_metadata(const hhs_nfv_handle* handle, hhs_nfv_metadata* out_metadata) {
    if (!handle || !out_metadata) {
        return HHS_NFV_STATUS_INVALID_ARGUMENT;
    }
    if (out_metadata->struct_size != sizeof(*out_metadata) || out_metadata->abi_version != HHS_NFV_ABI_VERSION) {
        return HHS_NFV_STATUS_ABI_MISMATCH;
    }
    out_metadata->version = handle->version;
    out_metadata->generation = handle->generation;
    out_metadata->state_size = handle->state_size;
    out_metadata->receipt_head = handle->receipt_head;
    out_metadata->object_index = handle->object_index;
    return HHS_NFV_STATUS_OK;
}

hhs_nfv_status hhs_nfv_read_state(const hhs_nfv_handle* handle, uint8_t* out_state, size_t* inout_state_size) {
    if (!handle || !inout_state_size) {
        return HHS_NFV_STATUS_INVALID_ARGUMENT;
    }
    if (!out_state || *inout_state_size < handle->state_size) {
        *inout_state_size = handle->state_size;
        return HHS_NFV_STATUS_BUFFER_TOO_SMALL;
    }
    if (handle->state_size > 0) {
        memcpy(out_state, handle->state, handle->state_size);
    }
    *inout_state_size = handle->state_size;
    return HHS_NFV_STATUS_OK;
}

hhs_nfv_status hhs_nfv_prepare_transition(
    const hhs_nfv_handle* handle,
    const hhs_nfv_transition_request* request,
    hhs_nfv_transition** out_transition
) {
    hhs_nfv_transition* transition;
    if (!handle || !request || !out_transition) {
        return HHS_NFV_STATUS_INVALID_ARGUMENT;
    }
    *out_transition = NULL;
    if (request->struct_size != sizeof(*request) || request->abi_version != HHS_NFV_ABI_VERSION) {
        return HHS_NFV_STATUS_ABI_MISMATCH;
    }
    if (!request->constructor_id || request->constructor_id_size == 0 ||
        (request->candidate_state_size > 0 && !request->candidate_state)) {
        return HHS_NFV_STATUS_INVALID_ARGUMENT;
    }
    if (request->candidate_state_size > handle->max_state_bytes) {
        return HHS_NFV_STATUS_RESOURCE_BOUNDED;
    }
    if (request->expected_version != handle->version || request->expected_generation != handle->generation) {
        return HHS_NFV_STATUS_STALE_REFERENCE;
    }
    transition = (hhs_nfv_transition*)calloc(1u, sizeof(*transition));
    if (!transition) {
        return HHS_NFV_STATUS_ALLOCATION_FAILED;
    }
    transition->constructor_id = hhs_nfv_copy_bytes(request->constructor_id, request->constructor_id_size);
    transition->candidate_state = hhs_nfv_copy_bytes(request->candidate_state, request->candidate_state_size);
    transition->inverse_state = hhs_nfv_copy_bytes(handle->state, handle->state_size);
    if (!transition->constructor_id ||
        (request->candidate_state_size > 0 && !transition->candidate_state) ||
        (handle->state_size > 0 && !transition->inverse_state)) {
        hhs_nfv_transition_close(transition);
        return HHS_NFV_STATUS_ALLOCATION_FAILED;
    }
    transition->constructor_id_size = request->constructor_id_size;
    transition->candidate_state_size = request->candidate_state_size;
    transition->inverse_state_size = handle->state_size;
    transition->expected_version = request->expected_version;
    transition->expected_generation = request->expected_generation;
    transition->flags = request->flags;
    transition->expected_object_index = handle->object_index;
    if (!hhs_nfv_compute_package_index(handle, request, transition->inverse_state, transition->inverse_state_size, &transition->package_index)) {
        hhs_nfv_transition_close(transition);
        return HHS_NFV_STATUS_ALLOCATION_FAILED;
    }
    *out_transition = transition;
    return HHS_NFV_STATUS_OK;
}

hhs_nfv_status hhs_nfv_commit_transition(hhs_nfv_handle* handle, hhs_nfv_transition* transition) {
    uint8_t* next_state;
    uint64_t next_version;
    uint64_t next_generation;
    HHSHash72 next_receipt;
    HHSHash216 next_index;
    if (!handle || !transition) {
        return HHS_NFV_STATUS_INVALID_ARGUMENT;
    }
    if (transition->committed || transition->reversed) {
        return HHS_NFV_STATUS_ALREADY_CLOSED;
    }
    if (transition->expected_version != handle->version || transition->expected_generation != handle->generation ||
        !hhs_hash216_equal(&transition->expected_object_index, &handle->object_index)) {
        return HHS_NFV_STATUS_STALE_REFERENCE;
    }
    if (!handle->vm81_admit) {
        return HHS_NFV_STATUS_AUTHORITY_UNBOUND;
    }
    if (!handle->vm81_admit(handle->state, handle->state_size, transition->candidate_state, transition->candidate_state_size, handle->user_data)) {
        return HHS_NFV_STATUS_VM81_REJECTED;
    }
    next_state = hhs_nfv_copy_bytes(transition->candidate_state, transition->candidate_state_size);
    if (transition->candidate_state_size > 0 && !next_state) {
        return HHS_NFV_STATUS_ALLOCATION_FAILED;
    }
    next_version = handle->version + 1u;
    next_generation = handle->generation + ((transition->flags & HHS_NFV_TRANSITION_COPY_ON_WRITE) ? 1u : 0u);
    if (!hhs_nfv_compute_receipt(HHS_NFV_DOMAIN_RECEIPT, &handle->receipt_head, &transition->package_index,
                                 next_state, transition->candidate_state_size, next_version, next_generation, &next_receipt) ||
        !hhs_nfv_compute_object_index(handle, next_state, transition->candidate_state_size,
                                      next_version, next_generation, &next_receipt, &next_index)) {
        hhs_nfv_secure_free(next_state, transition->candidate_state_size);
        return HHS_NFV_STATUS_ALLOCATION_FAILED;
    }
    hhs_nfv_secure_free(handle->state, handle->state_size);
    handle->state = next_state;
    handle->state_size = transition->candidate_state_size;
    handle->version = next_version;
    handle->generation = next_generation;
    handle->receipt_head = next_receipt;
    handle->object_index = next_index;
    transition->committed_receipt = next_receipt;
    transition->committed = 1;
    return HHS_NFV_STATUS_OK;
}

hhs_nfv_status hhs_nfv_reverse_transition(hhs_nfv_handle* handle, hhs_nfv_transition* transition) {
    uint8_t* next_state;
    uint64_t next_version;
    HHSHash72 next_receipt;
    HHSHash216 next_index;
    if (!handle || !transition) {
        return HHS_NFV_STATUS_INVALID_ARGUMENT;
    }
    if (!transition->committed || transition->reversed) {
        return HHS_NFV_STATUS_ALREADY_CLOSED;
    }
    if (!hhs_hash72_equal(&handle->receipt_head, &transition->committed_receipt)) {
        return HHS_NFV_STATUS_RECEIPT_MISMATCH;
    }
    if (!handle->vm81_admit(handle->state, handle->state_size, transition->inverse_state, transition->inverse_state_size, handle->user_data)) {
        return HHS_NFV_STATUS_VM81_REJECTED;
    }
    next_state = hhs_nfv_copy_bytes(transition->inverse_state, transition->inverse_state_size);
    if (transition->inverse_state_size > 0 && !next_state) {
        return HHS_NFV_STATUS_ALLOCATION_FAILED;
    }
    next_version = handle->version + 1u;
    if (!hhs_nfv_compute_receipt(HHS_NFV_DOMAIN_REVERSE, &handle->receipt_head, &transition->package_index,
                                 next_state, transition->inverse_state_size, next_version, handle->generation, &next_receipt) ||
        !hhs_nfv_compute_object_index(handle, next_state, transition->inverse_state_size,
                                      next_version, handle->generation, &next_receipt, &next_index)) {
        hhs_nfv_secure_free(next_state, transition->inverse_state_size);
        return HHS_NFV_STATUS_ALLOCATION_FAILED;
    }
    hhs_nfv_secure_free(handle->state, handle->state_size);
    handle->state = next_state;
    handle->state_size = transition->inverse_state_size;
    handle->version = next_version;
    handle->receipt_head = next_receipt;
    handle->object_index = next_index;
    transition->reversed = 1;
    return HHS_NFV_STATUS_OK;
}

void hhs_nfv_transition_close(hhs_nfv_transition* transition) {
    if (!transition) {
        return;
    }
    hhs_nfv_secure_free(transition->constructor_id, transition->constructor_id_size);
    hhs_nfv_secure_free(transition->candidate_state, transition->candidate_state_size);
    hhs_nfv_secure_free(transition->inverse_state, transition->inverse_state_size);
    memset(transition, 0, sizeof(*transition));
    free(transition);
}
