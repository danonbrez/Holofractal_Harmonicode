#ifndef HHS_PASS160_RUNTIME_H
#define HHS_PASS160_RUNTIME_H

#include <stddef.h>
#include <stdint.h>
#include "hhs_hash216.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_PASS160_ABI_VERSION 1u
#define HHS_PASS160_SHA256_BYTES 32u
#define HHS_PASS160_MAX_TRANSITIONS 4096u
#define HHS_PASS160_TERMINAL_CLASSIFICATION "HHS_PASS_160_FIBONACCI_PRIME_PSEUDORANDOM_OVERLAP_RECEIPT_TIP_VALIDATED_TRANSITION_RUNTIME_VERIFIED"

typedef enum {
    HHS160_OK = 0,
    HHS160_INVALID_ARGUMENT = -1,
    HHS160_RESOURCE_BOUNDED = -2,
    HHS160_INTEGRITY_MISMATCH = -3,
    HHS160_IDENTITY_MISMATCH = -4,
    HHS160_NOT_FOUND = -5,
    HHS160_NOT_SEALED = -6,
    HHS160_REVOKED = -7,
    HHS160_QUARANTINED = -8,
    HHS160_PARENT_MISMATCH = -9,
    HHS160_MEMBERSHIP_MISMATCH = -10,
    HHS160_OVERLAP_MISMATCH = -11,
    HHS160_AUTHORITY_REJECTED = -12,
    HHS160_REPLAY_MISMATCH = -13
} HHSP160Status;

typedef struct { uint8_t bytes[HHS_PASS160_SHA256_BYTES]; } HHSP160Integrity256;

typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
    uint64_t transition_epoch;
    uint64_t operation_sequence;
    HHSHash216 parent_receipt_tip;
    HHSHash216 parent_state_root;
    HHSHash216 operation_id;
    HHSHash216 operation_implementation_hash;
    HHSHash216 operation_semantic_hash;
    HHSHash216 canonical_input_hash;
    HHSHash216 canonical_delta_hash;
    HHSHash216 resulting_state_root;
    HHSHash216 resulting_receipt_tip;
    HHSHash216 constraint_root;
    HHSHash216 runtime_semantic_root;
    HHSHash216 operation_registry_root;
    HHSHash216 validation_receipt_hash;
    HHSHash216 transition_object_hash216;
    HHSP160Integrity256 transition_integrity_sha256;
    uint64_t maximum_steps;
    uint64_t maximum_memory_bytes;
    uint8_t semantically_validated;
    uint8_t sealed;
    uint8_t revoked;
    uint8_t external_effect_free;
} HHSP160ValidatedTransition;

typedef struct {
    uint64_t segment_id;
    uint64_t start_index;
    uint64_t transition_count;
    uint64_t overlap_prefix_count;
    uint64_t overlap_suffix_count;
    HHSHash216 segment_hash216;
    HHSP160Integrity256 merkle_root_sha256;
    HHSP160Integrity256 overlap_prefix_sha256;
    HHSP160Integrity256 overlap_suffix_sha256;
    uint8_t sealed;
    uint8_t quarantined;
    uint8_t revoked;
    uint8_t coverage_valid;
} HHSP160SegmentCertificate;

typedef struct {
    HHSHash216 terminal_receipt_tip;
    HHSHash216 terminal_state_root;
    HHSHash216 runtime_semantic_root;
    HHSHash216 operation_registry_root;
    HHSHash216 frontier_hash216;
    HHSP160Integrity256 frontier_sha256;
    uint64_t epoch;
    uint8_t sealed;
    uint8_t current;
    uint8_t revoked;
    uint8_t replay_verified;
} HHSP160HistoricalFrontier;

typedef struct {
    HHSP160ValidatedTransition transitions[HHS_PASS160_MAX_TRANSITIONS];
    uint8_t occupied[HHS_PASS160_MAX_TRANSITIONS];
    size_t count;
} HHSP160TransitionStore;

typedef struct {
    uint64_t runtime_instance_id;
    HHSP160HistoricalFrontier base_frontier;
    HHSHash216 local_receipt_root;
    uint64_t local_sequence;
    uint64_t maximum_steps;
    uint64_t maximum_memory_bytes;
    uint64_t consumed_steps;
    uint64_t consumed_memory_bytes;
    uint8_t capability_count;
    uint8_t finalized;
} HHSP160NestedRuntime;

typedef struct {
    uint64_t audit_epoch;
    uint64_t domain_length;
    uint64_t temporal_cycle_length;
    uint64_t coverage_cursor;
    uint64_t sampled_count;
    uint64_t failed_count;
    HHSP160Integrity256 seed_commitment;
    HHSP160Integrity256 result_accumulator;
    uint8_t complete_permutation;
    uint8_t every_index_visited_once;
} HHSP160AuditEpoch;

const char *hhs_pass160_status_string(HHSP160Status status);
void hhs_pass160_sha256(const void *data, size_t size, HHSP160Integrity256 *out);
void hhs_pass160_hash216_bound(const char *domain, const HHSP160Integrity256 *digest, const void *projection, size_t projection_size, HHSHash216 *out);
HHSP160Status hhs_pass160_transition_finalize(HHSP160ValidatedTransition *transition);
HHSP160Status hhs_pass160_transition_verify(const HHSP160ValidatedTransition *transition);
void hhs_pass160_store_init(HHSP160TransitionStore *store);
HHSP160Status hhs_pass160_store_admit(HHSP160TransitionStore *store, const HHSP160ValidatedTransition *transition, size_t *out_index);
HHSP160Status hhs_pass160_store_lookup(const HHSP160TransitionStore *store, const HHSHash216 *parent_tip, const HHSHash216 *parent_state, const HHSHash216 *operation_id, const HHSHash216 *input_hash, const HHSHash216 *constraint_root, const HHSHash216 *runtime_root, const HHSHash216 *implementation_hash, const HHSHash216 *registry_root, HHSP160ValidatedTransition *out_transition, size_t *out_index);
HHSP160Status hhs_pass160_segment_seal(const HHSP160TransitionStore *store, uint64_t segment_id, size_t start, size_t count, size_t overlap_prefix, size_t overlap_suffix, HHSP160SegmentCertificate *out);
HHSP160Status hhs_pass160_segment_verify_overlap(const HHSP160SegmentCertificate *left, const HHSP160SegmentCertificate *right);
HHSP160Status hhs_pass160_frontier_seal(const HHSP160SegmentCertificate *segments, size_t segment_count, const HHSP160ValidatedTransition *terminal, uint64_t epoch, HHSP160HistoricalFrontier *out);
HHSP160Status hhs_pass160_nested_begin(const HHSP160HistoricalFrontier *frontier, uint64_t runtime_instance_id, uint64_t maximum_steps, uint64_t maximum_memory_bytes, HHSP160NestedRuntime *out);
HHSP160Status hhs_pass160_nested_reuse(HHSP160NestedRuntime *runtime, const HHSP160ValidatedTransition *transition, const HHSP160HistoricalFrontier *current_frontier);
HHSP160Status hhs_pass160_commit_verify(const HHSP160NestedRuntime *runtime, const HHSP160HistoricalFrontier *current_frontier, uint8_t outer_capability_present);
uint64_t hhs_pass160_fibonacci(uint32_t index);
uint64_t hhs_pass160_temporal_cycle(uint32_t fibonacci_index, uint64_t prime_multiplier);
uint64_t hhs_pass160_bucket_quota(uint64_t bucket, uint64_t domain_length, uint64_t temporal_cycle_length);
HHSP160Status hhs_pass160_audit_begin(uint64_t epoch, uint64_t domain_length, uint64_t temporal_cycle_length, const void *seed, size_t seed_size, HHSP160AuditEpoch *out);
HHSP160Status hhs_pass160_audit_permutation(const HHSP160AuditEpoch *audit, uint64_t ordinal, uint64_t *out_index);
HHSP160Status hhs_pass160_audit_step(HHSP160AuditEpoch *audit, uint64_t ordinal, const HHSP160Integrity256 *record_digest, uint8_t record_valid);
HHSP160Status hhs_pass160_audit_complete(HHSP160AuditEpoch *audit);

#ifdef __cplusplus
}
#endif
#endif
