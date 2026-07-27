#include "hhs_pass160_runtime.h"

#include <openssl/sha.h>
#include <stdlib.h>
#include <string.h>

#define HHS160_DOMAIN_TRANSITION "HHS-P160-TRANSITION-INTEGRITY-V1"
#define HHS160_DOMAIN_TRANSITION_ID "HHS-P160-TRANSITION-IDENTITY-V1"
#define HHS160_DOMAIN_SEGMENT "HHS-P160-SEGMENT-MERKLE-V1"
#define HHS160_DOMAIN_SEGMENT_ID "HHS-P160-SEGMENT-IDENTITY-V1"
#define HHS160_DOMAIN_FRONTIER "HHS-P160-FRONTIER-INTEGRITY-V1"
#define HHS160_DOMAIN_AUDIT "HHS-P160-AUDIT-EPOCH-KEY-V1"
#define HHS160_DOMAIN_PERMUTE "HHS-P160-COVERAGE-PRP-V1"
#define HHS160_DOMAIN_RECEIPT "HHS-P160-LOCAL-RECEIPT-V1"

static int hash216_equal(const HHSHash216 *a, const HHSHash216 *b) {
    return a && b && memcmp(a->value, b->value, HHS_HASH216_LEN) == 0;
}

static int integrity_equal(const HHSP160Integrity256 *a, const HHSP160Integrity256 *b) {
    return a && b && memcmp(a->bytes, b->bytes, HHS_PASS160_SHA256_BYTES) == 0;
}

static void write_u64_be(uint8_t *out, uint64_t value) {
    for (size_t i = 0; i < 8u; ++i) out[i] = (uint8_t)(value >> (56u - 8u * i));
}

static void write_u32_be(uint8_t *out, uint32_t value) {
    for (size_t i = 0; i < 4u; ++i) out[i] = (uint8_t)(value >> (24u - 8u * i));
}

static size_t append_bytes(uint8_t *out, size_t capacity, size_t cursor, const void *data, size_t size) {
    if (!out || !data || cursor > capacity || size > capacity - cursor) return SIZE_MAX;
    memcpy(out + cursor, data, size);
    return cursor + size;
}

static size_t append_u64(uint8_t *out, size_t capacity, size_t cursor, uint64_t value) {
    uint8_t encoded[8];
    write_u64_be(encoded, value);
    return append_bytes(out, capacity, cursor, encoded, sizeof(encoded));
}

static size_t append_u32(uint8_t *out, size_t capacity, size_t cursor, uint32_t value) {
    uint8_t encoded[4];
    write_u32_be(encoded, value);
    return append_bytes(out, capacity, cursor, encoded, sizeof(encoded));
}

static size_t transition_canonical(const HHSP160ValidatedTransition *t, uint8_t *out, size_t capacity) {
    size_t c = 0u;
    if (!t || !out) return SIZE_MAX;
    c = append_u32(out, capacity, c, t->struct_version);
    c = append_u64(out, capacity, c, t->transition_epoch);
    c = append_u64(out, capacity, c, t->operation_sequence);
#define APPEND_HASH(field) do { c = append_bytes(out, capacity, c, t->field.value, HHS_HASH216_LEN); if (c == SIZE_MAX) return SIZE_MAX; } while (0)
    APPEND_HASH(parent_receipt_tip);
    APPEND_HASH(parent_state_root);
    APPEND_HASH(operation_id);
    APPEND_HASH(operation_implementation_hash);
    APPEND_HASH(operation_semantic_hash);
    APPEND_HASH(canonical_input_hash);
    APPEND_HASH(canonical_delta_hash);
    APPEND_HASH(resulting_state_root);
    APPEND_HASH(resulting_receipt_tip);
    APPEND_HASH(constraint_root);
    APPEND_HASH(runtime_semantic_root);
    APPEND_HASH(operation_registry_root);
    APPEND_HASH(validation_receipt_hash);
#undef APPEND_HASH
    c = append_u64(out, capacity, c, t->maximum_steps);
    c = append_u64(out, capacity, c, t->maximum_memory_bytes);
    if (c == SIZE_MAX || capacity - c < 4u) return SIZE_MAX;
    out[c++] = t->semantically_validated;
    out[c++] = t->sealed;
    out[c++] = t->revoked;
    out[c++] = t->external_effect_free;
    return c;
}

const char *hhs_pass160_status_string(HHSP160Status status) {
    switch (status) {
        case HHS160_OK: return "OK";
        case HHS160_INVALID_ARGUMENT: return "INVALID_ARGUMENT";
        case HHS160_RESOURCE_BOUNDED: return "RESOURCE_BOUNDED";
        case HHS160_INTEGRITY_MISMATCH: return "INTEGRITY_MISMATCH";
        case HHS160_IDENTITY_MISMATCH: return "IDENTITY_MISMATCH";
        case HHS160_NOT_FOUND: return "NOT_FOUND";
        case HHS160_NOT_SEALED: return "NOT_SEALED";
        case HHS160_REVOKED: return "REVOKED";
        case HHS160_QUARANTINED: return "QUARANTINED";
        case HHS160_PARENT_MISMATCH: return "PARENT_MISMATCH";
        case HHS160_MEMBERSHIP_MISMATCH: return "MEMBERSHIP_MISMATCH";
        case HHS160_OVERLAP_MISMATCH: return "OVERLAP_MISMATCH";
        case HHS160_AUTHORITY_REJECTED: return "AUTHORITY_REJECTED";
        case HHS160_REPLAY_MISMATCH: return "REPLAY_MISMATCH";
        default: return "UNKNOWN";
    }
}

void hhs_pass160_sha256(const void *data, size_t size, HHSP160Integrity256 *out) {
    if (!out) return;
    SHA256((const unsigned char *)data, size, out->bytes);
}

void hhs_pass160_hash216_bound(const char *domain, const HHSP160Integrity256 *digest, const void *projection, size_t projection_size, HHSHash216 *out) {
    size_t domain_size;
    size_t total;
    uint8_t *buffer;
    if (!domain || !digest || !out || (projection_size && !projection)) return;
    domain_size = strlen(domain);
    if (domain_size > SIZE_MAX - 1u - HHS_PASS160_SHA256_BYTES - projection_size) return;
    total = domain_size + 1u + HHS_PASS160_SHA256_BYTES + projection_size;
    buffer = (uint8_t *)malloc(total);
    if (!buffer) return;
    memcpy(buffer, domain, domain_size);
    buffer[domain_size] = 0u;
    memcpy(buffer + domain_size + 1u, digest->bytes, HHS_PASS160_SHA256_BYTES);
    if (projection_size) memcpy(buffer + domain_size + 1u + HHS_PASS160_SHA256_BYTES, projection, projection_size);
    hhs_hash216_compute(buffer, total, out);
    free(buffer);
}

HHSP160Status hhs_pass160_transition_finalize(HHSP160ValidatedTransition *transition) {
    uint8_t canonical[4096];
    size_t size;
    HHSHash216 identity;
    if (!transition || transition->struct_size < sizeof(*transition) || transition->struct_version != HHS_PASS160_ABI_VERSION) return HHS160_INVALID_ARGUMENT;
    if (!transition->semantically_validated || transition->revoked) return HHS160_AUTHORITY_REJECTED;
    size = transition_canonical(transition, canonical, sizeof(canonical));
    if (size == SIZE_MAX) return HHS160_RESOURCE_BOUNDED;
    {
        SHA256_CTX ctx;
        SHA256_Init(&ctx);
        SHA256_Update(&ctx, HHS160_DOMAIN_TRANSITION, strlen(HHS160_DOMAIN_TRANSITION));
        SHA256_Update(&ctx, canonical, size);
        SHA256_Final(transition->transition_integrity_sha256.bytes, &ctx);
    }
    hhs_pass160_hash216_bound(HHS160_DOMAIN_TRANSITION_ID, &transition->transition_integrity_sha256, canonical, size, &identity);
    transition->transition_object_hash216 = identity;
    transition->sealed = 1u;
    return HHS160_OK;
}

HHSP160Status hhs_pass160_transition_verify(const HHSP160ValidatedTransition *transition) {
    HHSP160ValidatedTransition copy;
    HHSP160Status status;
    if (!transition) return HHS160_INVALID_ARGUMENT;
    if (!transition->sealed) return HHS160_NOT_SEALED;
    if (transition->revoked) return HHS160_REVOKED;
    copy = *transition;
    copy.sealed = 0u;
    memset(copy.transition_integrity_sha256.bytes, 0, sizeof(copy.transition_integrity_sha256.bytes));
    memset(copy.transition_object_hash216.value, 0, sizeof(copy.transition_object_hash216.value));
    status = hhs_pass160_transition_finalize(&copy);
    if (status != HHS160_OK) return status;
    if (!integrity_equal(&copy.transition_integrity_sha256, &transition->transition_integrity_sha256)) return HHS160_INTEGRITY_MISMATCH;
    if (!hash216_equal(&copy.transition_object_hash216, &transition->transition_object_hash216)) return HHS160_IDENTITY_MISMATCH;
    return HHS160_OK;
}

void hhs_pass160_store_init(HHSP160TransitionStore *store) {
    if (store) memset(store, 0, sizeof(*store));
}

HHSP160Status hhs_pass160_store_admit(HHSP160TransitionStore *store, const HHSP160ValidatedTransition *transition, size_t *out_index) {
    HHSP160Status status;
    if (!store || !transition) return HHS160_INVALID_ARGUMENT;
    status = hhs_pass160_transition_verify(transition);
    if (status != HHS160_OK) return status;
    if (store->count >= HHS_PASS160_MAX_TRANSITIONS) return HHS160_RESOURCE_BOUNDED;
    for (size_t i = 0; i < HHS_PASS160_MAX_TRANSITIONS; ++i) {
        if (!store->occupied[i]) {
            store->transitions[i] = *transition;
            store->occupied[i] = 1u;
            store->count++;
            if (out_index) *out_index = i;
            return HHS160_OK;
        }
    }
    return HHS160_RESOURCE_BOUNDED;
}

HHSP160Status hhs_pass160_store_lookup(const HHSP160TransitionStore *store, const HHSHash216 *parent_tip, const HHSHash216 *parent_state, const HHSHash216 *operation_id, const HHSHash216 *input_hash, const HHSHash216 *constraint_root, const HHSHash216 *runtime_root, const HHSHash216 *implementation_hash, const HHSHash216 *registry_root, HHSP160ValidatedTransition *out_transition, size_t *out_index) {
    if (!store || !parent_tip || !parent_state || !operation_id || !input_hash || !constraint_root || !runtime_root || !implementation_hash || !registry_root) return HHS160_INVALID_ARGUMENT;
    for (size_t i = 0; i < HHS_PASS160_MAX_TRANSITIONS; ++i) {
        const HHSP160ValidatedTransition *t;
        if (!store->occupied[i]) continue;
        t = &store->transitions[i];
        if (hash216_equal(&t->parent_receipt_tip, parent_tip) &&
            hash216_equal(&t->parent_state_root, parent_state) &&
            hash216_equal(&t->operation_id, operation_id) &&
            hash216_equal(&t->canonical_input_hash, input_hash) &&
            hash216_equal(&t->constraint_root, constraint_root) &&
            hash216_equal(&t->runtime_semantic_root, runtime_root) &&
            hash216_equal(&t->operation_implementation_hash, implementation_hash) &&
            hash216_equal(&t->operation_registry_root, registry_root)) {
            HHSP160Status status = hhs_pass160_transition_verify(t);
            if (status != HHS160_OK) return status;
            if (out_transition) *out_transition = *t;
            if (out_index) *out_index = i;
            return HHS160_OK;
        }
    }
    return HHS160_NOT_FOUND;
}

static void merkle_root(const HHSP160TransitionStore *store, size_t start, size_t count, HHSP160Integrity256 *out) {
    HHSP160Integrity256 *level;
    size_t n = count;
    if (!out) return;
    memset(out, 0, sizeof(*out));
    if (!store || count == 0u) return;
    level = (HHSP160Integrity256 *)calloc(count, sizeof(*level));
    if (!level) return;
    for (size_t i = 0; i < count; ++i) level[i] = store->transitions[start + i].transition_integrity_sha256;
    while (n > 1u) {
        size_t next = (n + 1u) / 2u;
        for (size_t i = 0; i < next; ++i) {
            uint8_t pair[64];
            size_t left = i * 2u;
            size_t right = left + 1u < n ? left + 1u : left;
            memcpy(pair, level[left].bytes, 32u);
            memcpy(pair + 32u, level[right].bytes, 32u);
            {
                SHA256_CTX ctx;
                SHA256_Init(&ctx);
                SHA256_Update(&ctx, HHS160_DOMAIN_SEGMENT, strlen(HHS160_DOMAIN_SEGMENT));
                SHA256_Update(&ctx, pair, sizeof(pair));
                SHA256_Final(level[i].bytes, &ctx);
            }
        }
        n = next;
    }
    *out = level[0];
    free(level);
}

HHSP160Status hhs_pass160_segment_seal(const HHSP160TransitionStore *store, uint64_t segment_id, size_t start, size_t count, size_t overlap_prefix, size_t overlap_suffix, HHSP160SegmentCertificate *out) {
    uint8_t projection[64];
    size_t c = 0u;
    if (!store || !out || count == 0u || start > HHS_PASS160_MAX_TRANSITIONS || count > HHS_PASS160_MAX_TRANSITIONS - start || overlap_prefix >= count || overlap_suffix >= count) return HHS160_INVALID_ARGUMENT;
    for (size_t i = 0; i < count; ++i) {
        if (!store->occupied[start + i]) return HHS160_NOT_FOUND;
        if (hhs_pass160_transition_verify(&store->transitions[start + i]) != HHS160_OK) return HHS160_INTEGRITY_MISMATCH;
    }
    memset(out, 0, sizeof(*out));
    out->segment_id = segment_id;
    out->start_index = start;
    out->transition_count = count;
    out->overlap_prefix_count = overlap_prefix;
    out->overlap_suffix_count = overlap_suffix;
    merkle_root(store, start, count, &out->merkle_root_sha256);
    if (overlap_prefix) merkle_root(store, start, overlap_prefix, &out->overlap_prefix_sha256);
    if (overlap_suffix) merkle_root(store, start + count - overlap_suffix, overlap_suffix, &out->overlap_suffix_sha256);
    c = append_u64(projection, sizeof(projection), c, segment_id);
    c = append_u64(projection, sizeof(projection), c, start);
    c = append_u64(projection, sizeof(projection), c, count);
    c = append_u64(projection, sizeof(projection), c, overlap_prefix);
    c = append_u64(projection, sizeof(projection), c, overlap_suffix);
    hhs_pass160_hash216_bound(HHS160_DOMAIN_SEGMENT_ID, &out->merkle_root_sha256, projection, c, &out->segment_hash216);
    out->sealed = 1u;
    out->coverage_valid = 1u;
    return HHS160_OK;
}

HHSP160Status hhs_pass160_segment_verify_overlap(const HHSP160SegmentCertificate *left, const HHSP160SegmentCertificate *right) {
    if (!left || !right) return HHS160_INVALID_ARGUMENT;
    if (!left->sealed || !right->sealed) return HHS160_NOT_SEALED;
    if (left->revoked || right->revoked) return HHS160_REVOKED;
    if (left->quarantined || right->quarantined) return HHS160_QUARANTINED;
    if (left->overlap_suffix_count == 0u || left->overlap_suffix_count != right->overlap_prefix_count) return HHS160_OVERLAP_MISMATCH;
    if (!integrity_equal(&left->overlap_suffix_sha256, &right->overlap_prefix_sha256)) return HHS160_OVERLAP_MISMATCH;
    return HHS160_OK;
}

HHSP160Status hhs_pass160_frontier_seal(const HHSP160SegmentCertificate *segments, size_t segment_count, const HHSP160ValidatedTransition *terminal, uint64_t epoch, HHSP160HistoricalFrontier *out) {
    SHA256_CTX ctx;
    uint8_t projection[1024];
    size_t c = 0u;
    if (!segments || segment_count == 0u || !terminal || !out) return HHS160_INVALID_ARGUMENT;
    if (hhs_pass160_transition_verify(terminal) != HHS160_OK) return HHS160_INTEGRITY_MISMATCH;
    memset(out, 0, sizeof(*out));
    SHA256_Init(&ctx);
    SHA256_Update(&ctx, HHS160_DOMAIN_FRONTIER, strlen(HHS160_DOMAIN_FRONTIER));
    for (size_t i = 0; i < segment_count; ++i) {
        if (!segments[i].sealed || segments[i].revoked || segments[i].quarantined) return HHS160_AUTHORITY_REJECTED;
        SHA256_Update(&ctx, segments[i].merkle_root_sha256.bytes, 32u);
    }
    SHA256_Update(&ctx, terminal->resulting_receipt_tip.value, HHS_HASH216_LEN);
    SHA256_Update(&ctx, terminal->resulting_state_root.value, HHS_HASH216_LEN);
    SHA256_Final(out->frontier_sha256.bytes, &ctx);
    out->terminal_receipt_tip = terminal->resulting_receipt_tip;
    out->terminal_state_root = terminal->resulting_state_root;
    out->runtime_semantic_root = terminal->runtime_semantic_root;
    out->operation_registry_root = terminal->operation_registry_root;
    out->epoch = epoch;
    c = append_u64(projection, sizeof(projection), c, epoch);
    c = append_bytes(projection, sizeof(projection), c, out->terminal_receipt_tip.value, HHS_HASH216_LEN);
    c = append_bytes(projection, sizeof(projection), c, out->terminal_state_root.value, HHS_HASH216_LEN);
    hhs_pass160_hash216_bound(HHS160_DOMAIN_FRONTIER, &out->frontier_sha256, projection, c, &out->frontier_hash216);
    out->sealed = 1u;
    out->current = 1u;
    out->replay_verified = 1u;
    return HHS160_OK;
}

HHSP160Status hhs_pass160_nested_begin(const HHSP160HistoricalFrontier *frontier, uint64_t runtime_instance_id, uint64_t maximum_steps, uint64_t maximum_memory_bytes, HHSP160NestedRuntime *out) {
    if (!frontier || !out || !frontier->sealed || !frontier->current || frontier->revoked || !frontier->replay_verified || maximum_steps == 0u || maximum_memory_bytes == 0u) return HHS160_AUTHORITY_REJECTED;
    memset(out, 0, sizeof(*out));
    out->runtime_instance_id = runtime_instance_id;
    out->base_frontier = *frontier;
    out->maximum_steps = maximum_steps;
    out->maximum_memory_bytes = maximum_memory_bytes;
    out->capability_count = 0u;
    hhs_hash216_compute(frontier->frontier_hash216.value, HHS_HASH216_LEN, &out->local_receipt_root);
    return HHS160_OK;
}

HHSP160Status hhs_pass160_nested_reuse(HHSP160NestedRuntime *runtime, const HHSP160ValidatedTransition *transition, const HHSP160HistoricalFrontier *current_frontier) {
    uint8_t receipt[HHS_HASH216_LEN * 2u + 24u];
    size_t c = 0u;
    if (!runtime || !transition || !current_frontier || runtime->finalized) return HHS160_INVALID_ARGUMENT;
    if (runtime->capability_count != 0u) return HHS160_AUTHORITY_REJECTED;
    if (!hash216_equal(&runtime->base_frontier.frontier_hash216, &current_frontier->frontier_hash216)) return HHS160_PARENT_MISMATCH;
    if (!hash216_equal(&transition->parent_receipt_tip, &current_frontier->terminal_receipt_tip) || !hash216_equal(&transition->parent_state_root, &current_frontier->terminal_state_root)) return HHS160_PARENT_MISMATCH;
    if (hhs_pass160_transition_verify(transition) != HHS160_OK) return HHS160_INTEGRITY_MISMATCH;
    if (!transition->external_effect_free) return HHS160_AUTHORITY_REJECTED;
    if (runtime->consumed_steps > runtime->maximum_steps - transition->maximum_steps || runtime->consumed_memory_bytes > runtime->maximum_memory_bytes - transition->maximum_memory_bytes) return HHS160_RESOURCE_BOUNDED;
    runtime->consumed_steps += transition->maximum_steps;
    runtime->consumed_memory_bytes += transition->maximum_memory_bytes;
    runtime->local_sequence++;
    c = append_bytes(receipt, sizeof(receipt), c, runtime->local_receipt_root.value, HHS_HASH216_LEN);
    c = append_bytes(receipt, sizeof(receipt), c, transition->transition_object_hash216.value, HHS_HASH216_LEN);
    c = append_u64(receipt, sizeof(receipt), c, runtime->local_sequence);
    hhs_hash216_compute(receipt, c, &runtime->local_receipt_root);
    return HHS160_OK;
}

HHSP160Status hhs_pass160_commit_verify(const HHSP160NestedRuntime *runtime, const HHSP160HistoricalFrontier *current_frontier, uint8_t outer_capability_present) {
    if (!runtime || !current_frontier) return HHS160_INVALID_ARGUMENT;
    if (!outer_capability_present) return HHS160_AUTHORITY_REJECTED;
    if (runtime->capability_count != 0u) return HHS160_AUTHORITY_REJECTED;
    if (!hash216_equal(&runtime->base_frontier.frontier_hash216, &current_frontier->frontier_hash216)) return HHS160_PARENT_MISMATCH;
    if (!current_frontier->sealed || !current_frontier->current || current_frontier->revoked || !current_frontier->replay_verified) return HHS160_AUTHORITY_REJECTED;
    return HHS160_OK;
}

uint64_t hhs_pass160_fibonacci(uint32_t index) {
    uint64_t a = 0u, b = 1u;
    for (uint32_t i = 0u; i < index; ++i) {
        uint64_t next = a + b;
        if (next < b) return UINT64_MAX;
        a = b;
        b = next;
    }
    return a;
}

uint64_t hhs_pass160_temporal_cycle(uint32_t fibonacci_index, uint64_t prime_multiplier) {
    uint64_t f = hhs_pass160_fibonacci(fibonacci_index);
    if (f == UINT64_MAX || prime_multiplier == 0u || f > UINT64_MAX / prime_multiplier) return 0u;
    return f * prime_multiplier;
}

uint64_t hhs_pass160_bucket_quota(uint64_t bucket, uint64_t domain_length, uint64_t temporal_cycle_length) {
    __uint128_t left, right;
    if (temporal_cycle_length == 0u || bucket >= temporal_cycle_length) return 0u;
    left = ((__uint128_t)(bucket + 1u) * domain_length) / temporal_cycle_length;
    right = ((__uint128_t)bucket * domain_length) / temporal_cycle_length;
    return (uint64_t)(left - right);
}

static uint64_t digest_u64(const HHSP160Integrity256 *seed, uint64_t round, uint64_t half) {
    uint8_t input[48];
    HHSP160Integrity256 digest;
    memcpy(input, seed->bytes, 32u);
    write_u64_be(input + 32u, round);
    write_u64_be(input + 40u, half);
    {
        SHA256_CTX ctx;
        SHA256_Init(&ctx);
        SHA256_Update(&ctx, HHS160_DOMAIN_PERMUTE, strlen(HHS160_DOMAIN_PERMUTE));
        SHA256_Update(&ctx, input, sizeof(input));
        SHA256_Final(digest.bytes, &ctx);
    }
    return ((uint64_t)digest.bytes[0] << 56u) | ((uint64_t)digest.bytes[1] << 48u) | ((uint64_t)digest.bytes[2] << 40u) | ((uint64_t)digest.bytes[3] << 32u) | ((uint64_t)digest.bytes[4] << 24u) | ((uint64_t)digest.bytes[5] << 16u) | ((uint64_t)digest.bytes[6] << 8u) | digest.bytes[7];
}

static uint32_t bit_width(uint64_t value) {
    uint32_t bits = 0u;
    while (value) { bits++; value >>= 1u; }
    return bits ? bits : 1u;
}

static uint64_t feistel(const HHSP160Integrity256 *seed, uint64_t value, uint32_t bits) {
    uint32_t half_bits = bits / 2u;
    uint64_t mask = half_bits == 64u ? UINT64_MAX : ((UINT64_C(1) << half_bits) - 1u);
    uint64_t left = (value >> half_bits) & mask;
    uint64_t right = value & mask;
    for (uint64_t round = 0u; round < 4u; ++round) {
        uint64_t f = digest_u64(seed, round, right) & mask;
        uint64_t next = left ^ f;
        left = right;
        right = next;
    }
    return ((left & mask) << half_bits) | (right & mask);
}

HHSP160Status hhs_pass160_audit_begin(uint64_t epoch, uint64_t domain_length, uint64_t temporal_cycle_length, const void *seed, size_t seed_size, HHSP160AuditEpoch *out) {
    SHA256_CTX ctx;
    uint8_t encoded_epoch[8];
    if (!out || !seed || seed_size == 0u || domain_length == 0u || temporal_cycle_length == 0u) return HHS160_INVALID_ARGUMENT;
    memset(out, 0, sizeof(*out));
    out->audit_epoch = epoch;
    out->domain_length = domain_length;
    out->temporal_cycle_length = temporal_cycle_length;
    write_u64_be(encoded_epoch, epoch);
    SHA256_Init(&ctx);
    SHA256_Update(&ctx, HHS160_DOMAIN_AUDIT, strlen(HHS160_DOMAIN_AUDIT));
    SHA256_Update(&ctx, encoded_epoch, sizeof(encoded_epoch));
    SHA256_Update(&ctx, seed, seed_size);
    SHA256_Final(out->seed_commitment.bytes, &ctx);
    return HHS160_OK;
}

HHSP160Status hhs_pass160_audit_permutation(const HHSP160AuditEpoch *audit, uint64_t ordinal, uint64_t *out_index) {
    uint32_t bits;
    uint64_t candidate;
    uint64_t guard = 0u;
    if (!audit || !out_index || ordinal >= audit->domain_length) return HHS160_INVALID_ARGUMENT;
    bits = bit_width(audit->domain_length - 1u);
    if (bits & 1u) bits++;
    candidate = ordinal;
    do {
        candidate = feistel(&audit->seed_commitment, candidate, bits);
        if (++guard > UINT64_C(1048576)) return HHS160_RESOURCE_BOUNDED;
    } while (candidate >= audit->domain_length);
    *out_index = candidate;
    return HHS160_OK;
}

HHSP160Status hhs_pass160_audit_step(HHSP160AuditEpoch *audit, uint64_t ordinal, const HHSP160Integrity256 *record_digest, uint8_t record_valid) {
    uint8_t input[72];
    if (!audit || !record_digest || ordinal != audit->coverage_cursor || ordinal >= audit->domain_length) return HHS160_INVALID_ARGUMENT;
    memcpy(input, audit->result_accumulator.bytes, 32u);
    memcpy(input + 32u, record_digest->bytes, 32u);
    write_u64_be(input + 64u, ordinal);
    hhs_pass160_sha256(input, sizeof(input), &audit->result_accumulator);
    audit->coverage_cursor++;
    audit->sampled_count++;
    if (!record_valid) audit->failed_count++;
    return HHS160_OK;
}

HHSP160Status hhs_pass160_audit_complete(HHSP160AuditEpoch *audit) {
    if (!audit) return HHS160_INVALID_ARGUMENT;
    if (audit->coverage_cursor != audit->domain_length || audit->sampled_count != audit->domain_length) return HHS160_RESOURCE_BOUNDED;
    audit->complete_permutation = 1u;
    audit->every_index_visited_once = 1u;
    return audit->failed_count == 0u ? HHS160_OK : HHS160_INTEGRITY_MISMATCH;
}
