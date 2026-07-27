#include "hhs_pass160_runtime.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned long long positive_total = 0u;
static unsigned long long negative_total = 0u;
static unsigned long long failures = 0u;

#define POS(expr) do { if (expr) positive_total++; else failures++; } while (0)
#define NEG(expr) do { if (expr) negative_total++; else failures++; } while (0)

static HHSHash216 hash_text(const char *text) {
    HHSHash216 out;
    hhs_hash216_compute(text, strlen(text), &out);
    return out;
}

static HHSP160ValidatedTransition make_transition(uint64_t sequence, const HHSHash216 *parent_tip, const HHSHash216 *parent_state) {
    char label[96];
    HHSP160ValidatedTransition t;
    memset(&t, 0, sizeof(t));
    t.struct_size = sizeof(t);
    t.struct_version = HHS_PASS160_ABI_VERSION;
    t.transition_epoch = sequence + 1u;
    t.operation_sequence = sequence;
    t.parent_receipt_tip = *parent_tip;
    t.parent_state_root = *parent_state;
#define SET_HASH(field, suffix) do { snprintf(label, sizeof(label), "p160-%llu-%s", (unsigned long long)sequence, suffix); t.field = hash_text(label); } while (0)
    SET_HASH(operation_id, "operation");
    SET_HASH(operation_implementation_hash, "implementation");
    SET_HASH(operation_semantic_hash, "semantic");
    SET_HASH(canonical_input_hash, "input");
    SET_HASH(canonical_delta_hash, "delta");
    SET_HASH(resulting_state_root, "state");
    SET_HASH(resulting_receipt_tip, "receipt");
    SET_HASH(constraint_root, "constraint");
    SET_HASH(runtime_semantic_root, "runtime");
    SET_HASH(operation_registry_root, "registry");
    SET_HASH(validation_receipt_hash, "validation");
#undef SET_HASH
    t.maximum_steps = 7u;
    t.maximum_memory_bytes = 64u;
    t.semantically_validated = 1u;
    t.external_effect_free = 1u;
    return t;
}

int main(void) {
    HHSP160TransitionStore store;
    HHSP160ValidatedTransition transitions[7];
    HHSHash216 tip = hash_text("genesis-tip");
    HHSHash216 state = hash_text("genesis-state");
    HHSP160SegmentCertificate left, right;
    HHSP160HistoricalFrontier frontier;
    HHSP160NestedRuntime runtime;
    HHSP160AuditEpoch audit;
    uint8_t visited[64] = {0};
    uint64_t quota_sum = 0u;

    hhs_pass160_store_init(&store);
    POS(store.count == 0u);

    for (size_t i = 0; i < 7u; ++i) {
        size_t index = SIZE_MAX;
        transitions[i] = make_transition(i, &tip, &state);
        POS(hhs_pass160_transition_finalize(&transitions[i]) == HHS160_OK);
        POS(hhs_pass160_transition_verify(&transitions[i]) == HHS160_OK);
        POS(hhs_pass160_store_admit(&store, &transitions[i], &index) == HHS160_OK);
        POS(index == i);
        tip = transitions[i].resulting_receipt_tip;
        state = transitions[i].resulting_state_root;
    }
    POS(store.count == 7u);

    {
        HHSP160ValidatedTransition found;
        size_t index = SIZE_MAX;
        POS(hhs_pass160_store_lookup(&store,
            &transitions[3].parent_receipt_tip,
            &transitions[3].parent_state_root,
            &transitions[3].operation_id,
            &transitions[3].canonical_input_hash,
            &transitions[3].constraint_root,
            &transitions[3].runtime_semantic_root,
            &transitions[3].operation_implementation_hash,
            &transitions[3].operation_registry_root,
            &found, &index) == HHS160_OK);
        POS(index == 3u);
        POS(memcmp(found.transition_object_hash216.value, transitions[3].transition_object_hash216.value, HHS_HASH216_LEN) == 0);
    }

    POS(hhs_pass160_segment_seal(&store, 1u, 0u, 4u, 0u, 2u, &left) == HHS160_OK);
    POS(hhs_pass160_segment_seal(&store, 2u, 2u, 4u, 2u, 0u, &right) == HHS160_OK);
    POS(hhs_pass160_segment_verify_overlap(&left, &right) == HHS160_OK);
    {
        HHSP160SegmentCertificate segments[2] = {left, right};
        POS(hhs_pass160_frontier_seal(segments, 2u, &transitions[5], 6u, &frontier) == HHS160_OK);
    }
    POS(frontier.sealed && frontier.current && frontier.replay_verified);
    POS(hhs_pass160_nested_begin(&frontier, 81u, 100u, 1024u, &runtime) == HHS160_OK);
    POS(runtime.capability_count == 0u);
    POS(hhs_pass160_nested_reuse(&runtime, &transitions[6], &frontier) == HHS160_OK);
    POS(runtime.local_sequence == 1u);
    POS(hhs_pass160_commit_verify(&runtime, &frontier, 0u) == HHS160_AUTHORITY_REJECTED);
    POS(hhs_pass160_commit_verify(&runtime, &frontier, 1u) == HHS160_OK);

    POS(hhs_pass160_fibonacci(9u) == 34u);
    POS(hhs_pass160_temporal_cycle(9u, 5u) == 170u);
    for (uint64_t b = 0u; b < 170u; ++b) quota_sum += hhs_pass160_bucket_quota(b, 64u, 170u);
    POS(quota_sum == 64u);

    POS(hhs_pass160_audit_begin(9u, 64u, 170u, "audit-seed", 10u, &audit) == HHS160_OK);
    for (uint64_t ordinal = 0u; ordinal < 64u; ++ordinal) {
        uint64_t index = UINT64_MAX;
        HHSP160Integrity256 digest;
        POS(hhs_pass160_audit_permutation(&audit, ordinal, &index) == HHS160_OK);
        POS(index < 64u);
        POS(visited[index] == 0u);
        visited[index] = 1u;
        hhs_pass160_sha256(&index, sizeof(index), &digest);
        POS(hhs_pass160_audit_step(&audit, ordinal, &digest, 1u) == HHS160_OK);
    }
    POS(hhs_pass160_audit_complete(&audit) == HHS160_OK);
    POS(audit.complete_permutation && audit.every_index_visited_once && audit.failed_count == 0u);

    for (size_t i = 0u; i < 160u; ++i) {
        HHSP160ValidatedTransition bad = transitions[i % 7u];
        bad.transition_integrity_sha256.bytes[i % 32u] ^= (uint8_t)(i + 1u);
        NEG(hhs_pass160_transition_verify(&bad) == HHS160_INTEGRITY_MISMATCH);
    }

    {
        HHSP160SegmentCertificate bad = right;
        bad.overlap_prefix_sha256.bytes[0] ^= 1u;
        NEG(hhs_pass160_segment_verify_overlap(&left, &bad) == HHS160_OVERLAP_MISMATCH);
    }
    {
        HHSP160HistoricalFrontier stale = frontier;
        stale.frontier_hash216.value[0] = stale.frontier_hash216.value[0] == '0' ? '1' : '0';
        NEG(hhs_pass160_nested_reuse(&runtime, &transitions[6], &stale) == HHS160_PARENT_MISMATCH);
    }
    {
        HHSP160NestedRuntime escaped = runtime;
        escaped.capability_count = 1u;
        NEG(hhs_pass160_commit_verify(&escaped, &frontier, 1u) == HHS160_AUTHORITY_REJECTED);
    }

    printf("{\"classification\":\"HHS_PASS_160_NATIVE_RUNTIME_EXECUTED_PENDING_FULL_CLOSURE\",\"positive_total\":%llu,\"negative_total\":%llu,\"failures\":%llu,\"hash216_sha256_binding\":true,\"exact_lookup\":true,\"overlap_verified\":true,\"coverage_domain\":64,\"capability_zero\":true,\"terminal_claimed\":false}\n",
        positive_total, negative_total, failures);
    return failures == 0u ? EXIT_SUCCESS : EXIT_FAILURE;
}
