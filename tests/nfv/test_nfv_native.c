#include "hhs_nfv_contract.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct gate_state {
    int allow;
    unsigned calls;
} gate_state;

static int vm81_gate(
    const uint8_t* prior_state,
    size_t prior_state_size,
    const uint8_t* candidate_state,
    size_t candidate_state_size,
    void* user_data
) {
    gate_state* gate = (gate_state*)user_data;
    assert(prior_state || prior_state_size == 0);
    assert(candidate_state || candidate_state_size == 0);
    gate->calls += 1u;
    return gate->allow;
}

static hhs_nfv_metadata metadata_of(const hhs_nfv_handle* handle) {
    hhs_nfv_metadata metadata;
    memset(&metadata, 0, sizeof(metadata));
    metadata.struct_size = sizeof(metadata);
    metadata.abi_version = HHS_NFV_ABI_VERSION;
    assert(hhs_nfv_get_metadata(handle, &metadata) == HHS_NFV_STATUS_OK);
    return metadata;
}

int main(void) {
    const uint8_t initial[] = {1u, 2u, 3u};
    const uint8_t candidate[] = {4u, 5u};
    const uint8_t cow_candidate[] = {9u};
    gate_state gate = {0, 0u};
    hhs_nfv_config config = {sizeof(config), HHS_NFV_ABI_VERSION, 64u, vm81_gate, &gate};
    hhs_nfv_object_descriptor descriptor = {
        sizeof(descriptor), HHS_NFV_ABI_VERSION,
        "STATE_VECTOR", sizeof("STATE_VECTOR") - 1u,
        "VM81-A", sizeof("VM81-A") - 1u,
        initial, sizeof(initial)
    };
    hhs_nfv_handle* handle = NULL;
    hhs_nfv_transition* transition = NULL;
    hhs_nfv_transition* stale = NULL;
    hhs_nfv_transition* cow = NULL;
    hhs_nfv_metadata before;
    hhs_nfv_metadata after;
    hhs_nfv_transition_request request;
    hhs_nfv_transition_request cow_request;
    uint8_t state[8];
    size_t state_size;

    assert(hhs_nfv_validate_abi(HHS_NFV_ABI_VERSION) == HHS_NFV_STATUS_OK);
    assert(hhs_nfv_validate_abi(0u) == HHS_NFV_STATUS_ABI_MISMATCH);
    assert(hhs_nfv_create(&config, &descriptor, &handle) == HHS_NFV_STATUS_OK);
    assert(handle != NULL);
    before = metadata_of(handle);
    assert(before.version == 0u && before.generation == 0u && before.state_size == sizeof(initial));

    memset(&request, 0, sizeof(request));
    request.struct_size = sizeof(request);
    request.abi_version = HHS_NFV_ABI_VERSION;
    request.expected_version = before.version;
    request.expected_generation = before.generation;
    request.constructor_id = "INVOKE";
    request.constructor_id_size = sizeof("INVOKE") - 1u;
    request.candidate_state = candidate;
    request.candidate_state_size = sizeof(candidate);

    assert(hhs_nfv_prepare_transition(handle, &request, &transition) == HHS_NFV_STATUS_OK);
    assert(hhs_nfv_prepare_transition(handle, &request, &stale) == HHS_NFV_STATUS_OK);
    assert(hhs_nfv_commit_transition(handle, transition) == HHS_NFV_STATUS_VM81_REJECTED);
    assert(metadata_of(handle).version == before.version);

    gate.allow = 1;
    assert(hhs_nfv_commit_transition(handle, transition) == HHS_NFV_STATUS_OK);
    after = metadata_of(handle);
    assert(after.version == 1u && after.generation == 0u && after.state_size == sizeof(candidate));
    assert(!hhs_hash72_equal(&before.receipt_head, &after.receipt_head));
    assert(!hhs_hash216_equal(&before.object_index, &after.object_index));
    assert(hhs_nfv_commit_transition(handle, stale) == HHS_NFV_STATUS_STALE_REFERENCE);

    state_size = 1u;
    assert(hhs_nfv_read_state(handle, state, &state_size) == HHS_NFV_STATUS_BUFFER_TOO_SMALL);
    assert(state_size == sizeof(candidate));
    state_size = sizeof(state);
    assert(hhs_nfv_read_state(handle, state, &state_size) == HHS_NFV_STATUS_OK);
    assert(state_size == sizeof(candidate) && memcmp(state, candidate, sizeof(candidate)) == 0);

    memset(&cow_request, 0, sizeof(cow_request));
    cow_request.struct_size = sizeof(cow_request);
    cow_request.abi_version = HHS_NFV_ABI_VERSION;
    cow_request.flags = HHS_NFV_TRANSITION_COPY_ON_WRITE;
    cow_request.expected_version = after.version;
    cow_request.expected_generation = after.generation;
    cow_request.constructor_id = "COPY_ON_WRITE";
    cow_request.constructor_id_size = sizeof("COPY_ON_WRITE") - 1u;
    cow_request.candidate_state = cow_candidate;
    cow_request.candidate_state_size = sizeof(cow_candidate);
    assert(hhs_nfv_prepare_transition(handle, &cow_request, &cow) == HHS_NFV_STATUS_OK);
    assert(hhs_nfv_commit_transition(handle, cow) == HHS_NFV_STATUS_OK);
    after = metadata_of(handle);
    assert(after.version == 2u && after.generation == 1u);
    assert(hhs_nfv_reverse_transition(handle, cow) == HHS_NFV_STATUS_OK);
    after = metadata_of(handle);
    assert(after.version == 3u && after.generation == 1u);
    state_size = sizeof(state);
    assert(hhs_nfv_read_state(handle, state, &state_size) == HHS_NFV_STATUS_OK);
    assert(state_size == sizeof(candidate) && memcmp(state, candidate, sizeof(candidate)) == 0);

    assert(gate.calls == 4u);
    hhs_nfv_transition_close(cow);
    hhs_nfv_transition_close(stale);
    hhs_nfv_transition_close(transition);
    hhs_nfv_close(handle);
    puts("HHS_NFV_NATIVE_CORE_VERIFIED");
    return 0;
}
