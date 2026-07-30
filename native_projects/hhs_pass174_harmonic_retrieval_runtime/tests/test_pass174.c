#include "hhs_pass174_runtime.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static int digest_differs(const HHS174Digest256 *left, const HHS174Digest256 *right) {
    return memcmp(left->bytes, right->bytes, HHS174_SHA256_BYTES) != 0;
}

int main(void) {
    static const char seed[] = "PASS174_NATIVE_GENESIS";
    HHS174Runtime runtime;
    assert(hhs174_genesis_init(&runtime, seed, sizeof(seed) - 1u) == HHS174_OK);
    assert(runtime.abi_version == HHS174_ABI_VERSION);
    assert(runtime.boot_admitted == 1u);
    assert(strlen(runtime.hash72_tip) == HHS174_HASH72_LEN);
    assert(runtime.current_frame.sequence == 0u);

    HHS174PhaseCoordinate phase;
    assert(hhs174_phase_coordinate(5184u, &phase) == HHS174_OK);
    assert(phase.phase64 == 0u);
    assert(phase.phase72 == 0u);
    assert(phase.phase81 == 0u);
    assert(phase.phase5184 == 0u);
    assert(phase.complete_lock == 1u);

    HHS174Frame5184 before = runtime.current_frame;
    HHS174Frame5184 candidate;
    assert(hhs174_frame_execute(&runtime, HHS174_OP_ROTATE, 3u, &candidate) == HHS174_OK);
    assert(runtime.has_candidate == 1u);
    assert(runtime.current_frame.sequence == 0u);
    assert(candidate.sequence == 1u);
    assert(digest_differs(&candidate.identity, &before.identity));
    assert(strlen(runtime.pending_hash216.value) == HHS174_HASH216_LEN);
    assert(hhs174_hash216_validate(&runtime.pending_hash216) == HHS174_OK);

    HHS174AdmissionWitness rejected = {1u,1u,1u,1u,1u,1u,1u,0u};
    assert(hhs174_frame_commit(&runtime, &rejected) == HHS174_AUTHORITY_REJECTED);
    assert(runtime.current_frame.sequence == 0u);
    assert(runtime.has_candidate == 1u);

    HHS174AdmissionWitness admitted = {1u,1u,1u,1u,1u,1u,1u,1u};
    assert(hhs174_frame_commit(&runtime, &admitted) == HHS174_OK);
    assert(runtime.current_frame.sequence == 1u);
    assert(runtime.transition_count == 1u);
    assert(runtime.store.count == 1u);
    assert(runtime.has_candidate == 0u);

    HHS174VectorObject retrieved;
    size_t object_index = 0u;
    assert(hhs174_vector_query(
        &runtime.store,
        &runtime.store.objects[0].query_identity,
        runtime.store.objects[0].transition.incoming_tip,
        &object_index
    ) == HHS174_OK);
    assert(object_index == 0u);
    assert(hhs174_vector_retrieve(
        &runtime.store,
        object_index,
        runtime.store.objects[0].transition.incoming_tip,
        &retrieved
    ) == HHS174_OK);
    assert(retrieved.authenticated == 1u);

    HHS174Frame5184 restored;
    assert(hhs174_delta_apply(&before, &retrieved.delta, &restored) == HHS174_OK);
    assert(memcmp(restored.identity.bytes, runtime.current_frame.identity.bytes, HHS174_SHA256_BYTES) == 0);

    HHS174Hash216Array altered = runtime.pending_hash216;
    altered.value[0] = altered.value[0] == '0' ? '1' : '0';
    assert(hhs174_hash216_validate(&altered) != HHS174_OK);

    HHS174Digest256 canonical;
    HHS174Digest256 instance;
    static const char challenge[] = "native-boot-challenge";
    assert(hhs174_boot_fingerprint(&runtime, challenge, sizeof(challenge) - 1u, &canonical, &instance) == HHS174_OK);
    assert(digest_differs(&canonical, &instance));

    for (size_t i = 1u; i < 72u; ++i) {
        assert(hhs174_phase_step(&runtime, HHS174_OP_XOR, (uint64_t)i) == HHS174_OK);
    }
    assert(runtime.transition_count == 72u);
    assert(runtime.phase.phase72 == 0u);
    assert(runtime.phase.complete_lock == 0u);
    assert(digest_differs(&runtime.current_frame.identity, &before.identity));

    HHS174AuditResult audit;
    static const char audit_challenge[] = "native-audit-challenge";
    assert(hhs174_genesis_audit(
        &runtime,
        audit_challenge,
        sizeof(audit_challenge) - 1u,
        8u,
        &audit
    ) == HHS174_OK);
    assert(audit.passed == 1u);
    assert(audit.executed_samples == 8u);

    HHS174Opcode opcodes[3] = {HHS174_OP_ROTATE, HHS174_OP_ADD, HHS174_OP_RECIPROCAL};
    uint64_t operands[3] = {3u, 5u, 7u};
    HHS174Digest256 replay_identity_a;
    HHS174Digest256 replay_identity_b;
    char replay_tip_a[HHS174_HASH72_LEN + 1u];
    char replay_tip_b[HHS174_HASH72_LEN + 1u];
    assert(hhs174_replay(seed, sizeof(seed) - 1u, opcodes, operands, 3u, &replay_identity_a, replay_tip_a) == HHS174_OK);
    assert(hhs174_replay(seed, sizeof(seed) - 1u, opcodes, operands, 3u, &replay_identity_b, replay_tip_b) == HHS174_OK);
    assert(memcmp(replay_identity_a.bytes, replay_identity_b.bytes, HHS174_SHA256_BYTES) == 0);
    assert(strcmp(replay_tip_a, replay_tip_b) == 0);

    HHS174StatusSnapshot snapshot;
    assert(hhs174_status(&runtime, &snapshot) == HHS174_OK);
    assert(snapshot.transition_count == runtime.transition_count);
    assert(snapshot.vector_object_count == runtime.store.count);

    size_t receipt_size = 0u;
    assert(hhs174_receipt_export(&runtime, NULL, 0u, &receipt_size) == HHS174_RESOURCE_BOUNDED);
    assert(receipt_size == sizeof(HHS174StatusSnapshot));

    puts("HHS_PASS174_NATIVE_MATRIX_PASSED");
    return 0;
}
