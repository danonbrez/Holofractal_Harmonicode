#ifndef HHS_PASS174_RUNTIME_H
#define HHS_PASS174_RUNTIME_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS174_ABI_VERSION 1u
#define HHS174_FRAME_WORDS 81u
#define HHS174_WORD_BITS 64u
#define HHS174_FRAME_BITS 5184u
#define HHS174_HASH72_LEN 72u
#define HHS174_HASH216_LEN 216u
#define HHS174_SHA256_BYTES 32u
#define HHS174_PHASE_LOCK_PERIOD 5184u
#define HHS174_MAX_VECTOR_OBJECTS 128u
#define HHS174_MAX_ACTIVE_SUFFIX 64u

#define HHS174_TERMINAL_CLASSIFICATION \
    "HHS_PASS_174_HARMONIC_PHASE_GEAR_ENCRYPTED_HASH216_RETRIEVAL_ACCELERATED_VM81_WHOLE_STATE_RUNTIME_VERIFIED"

typedef enum HHS174Status {
    HHS174_OK = 0,
    HHS174_INVALID_ARGUMENT = -1,
    HHS174_FRAME_GEOMETRY_ERROR = -2,
    HHS174_NO_CANDIDATE = -3,
    HHS174_STALE_CANDIDATE = -4,
    HHS174_AUTHORITY_REJECTED = -5,
    HHS174_HASH72_MISMATCH = -6,
    HHS174_HASH216_MISMATCH = -7,
    HHS174_INDEX_MISMATCH = -8,
    HHS174_STORE_FULL = -9,
    HHS174_NOT_FOUND = -10,
    HHS174_QUARANTINED = -11,
    HHS174_FRONTIER_MISMATCH = -12,
    HHS174_REPLAY_MISMATCH = -13,
    HHS174_RESOURCE_BOUNDED = -14
} HHS174Status;

typedef enum HHS174Opcode {
    HHS174_OP_ROTATE = 1,
    HHS174_OP_XOR = 2,
    HHS174_OP_ADD = 3,
    HHS174_OP_PERMUTE = 4,
    HHS174_OP_RECIPROCAL = 5,
    HHS174_OP_HARMONIC = 6,
    HHS174_OP_MIXED = 7
} HHS174Opcode;

typedef struct HHS174Digest256 {
    uint8_t bytes[HHS174_SHA256_BYTES];
} HHS174Digest256;

typedef struct HHS174Frame5184 {
    uint64_t words[HHS174_FRAME_WORDS];
    uint64_t sequence;
    HHS174Digest256 identity;
} HHS174Frame5184;

typedef struct HHS174PhaseCoordinate {
    uint64_t transition;
    uint16_t phase64;
    uint16_t phase72;
    uint16_t phase81;
    uint16_t phase5184;
    uint8_t lock64;
    uint8_t lock72;
    uint8_t lock81;
    uint8_t complete_lock;
} HHS174PhaseCoordinate;

typedef struct HHS174Hash72Transition {
    char predecessor_lane[HHS174_HASH72_LEN + 1u];
    char current_lane[HHS174_HASH72_LEN + 1u];
    char successor_lane[HHS174_HASH72_LEN + 1u];
    char incoming_tip[HHS174_HASH72_LEN + 1u];
    char outgoing_tip[HHS174_HASH72_LEN + 1u];
    HHS174Digest256 previous_frame_identity;
    HHS174Digest256 current_frame_identity;
    HHS174Digest256 successor_frame_identity;
    HHS174Digest256 operator_identity;
    HHS174Digest256 witness_identity;
    HHS174PhaseCoordinate phase;
} HHS174Hash72Transition;

typedef struct HHS174Hash216Array {
    char value[HHS174_HASH216_LEN + 1u];
    HHS174Digest256 logical_identity;
    HHS174Digest256 character_indexes[HHS174_HASH216_LEN];
    HHS174Digest256 index_root;
} HHS174Hash216Array;

typedef struct HHS174SparseDelta {
    HHS174Digest256 source_identity;
    HHS174Digest256 destination_identity;
    uint64_t changed_cell_mask_low;
    uint64_t changed_cell_mask_high;
    uint64_t replacement_words[HHS174_FRAME_WORDS];
    uint64_t changed_bit_masks[HHS174_FRAME_WORDS];
    uint16_t changed_cells;
    uint16_t changed_bits;
} HHS174SparseDelta;

typedef struct HHS174AdmissionWitness {
    uint8_t genesis_valid;
    uint8_t predecessor_valid;
    uint8_t current_valid;
    uint8_t continuation_valid;
    uint8_t vm81_valid;
    uint8_t hash72_valid;
    uint8_t hash216_valid;
    uint8_t authenticated_encryption_valid;
} HHS174AdmissionWitness;

typedef struct HHS174VectorObject {
    HHS174Digest256 logical_identity;
    HHS174Digest256 parent_identity;
    HHS174Digest256 query_identity;
    HHS174Frame5184 destination_frame;
    HHS174Hash72Transition transition;
    HHS174Hash216Array hash216;
    HHS174SparseDelta delta;
    uint64_t sequence;
    uint32_t key_version;
    uint8_t authenticated;
    uint8_t quarantined;
    uint8_t occupied;
} HHS174VectorObject;

typedef struct HHS174VectorStore {
    HHS174VectorObject objects[HHS174_MAX_VECTOR_OBJECTS];
    size_t count;
    HHS174Digest256 active_suffix[HHS174_MAX_ACTIVE_SUFFIX];
    size_t active_suffix_count;
} HHS174VectorStore;

typedef struct HHS174CostUnits {
    uint64_t decoded_bytecodes;
    uint64_t cell_reads;
    uint64_t cell_writes;
    uint64_t bit_rotations;
    uint64_t lane_permutations;
    uint64_t modular_operations;
    uint64_t constraint_evaluations;
    uint64_t harmonic_relations;
    uint64_t sha256_index_validations;
    uint64_t hash72_projections;
    uint64_t hash216_operations;
    uint64_t active_suffix_records;
    uint64_t closure_iterations;
} HHS174CostUnits;

typedef struct HHS174EfficiencyRecord {
    HHS174Digest256 query_identity;
    uint64_t direct_cost;
    uint64_t retrieval_cost;
    uint64_t hybrid_cost;
    uint64_t successful_retrievals;
    uint64_t rejected_retrievals;
    uint64_t avoided_work;
    int64_t retrieval_advantage;
    uint8_t retrieval_preferred;
} HHS174EfficiencyRecord;

typedef struct HHS174AuditResult {
    HHS174Digest256 seed_identity;
    uint64_t requested_samples;
    uint64_t executed_samples;
    uint64_t failed_samples;
    uint8_t passed;
} HHS174AuditResult;

typedef struct HHS174Runtime {
    uint32_t abi_version;
    HHS174Digest256 genesis_identity;
    HHS174Frame5184 previous_frame;
    HHS174Frame5184 current_frame;
    HHS174Frame5184 candidate_frame;
    HHS174PhaseCoordinate phase;
    char hash72_tip[HHS174_HASH72_LEN + 1u];
    HHS174Hash72Transition pending_transition;
    HHS174Hash216Array pending_hash216;
    HHS174VectorStore store;
    HHS174EfficiencyRecord efficiency;
    HHS174CostUnits last_cost;
    uint64_t transition_count;
    uint8_t has_candidate;
    uint8_t boot_admitted;
} HHS174Runtime;

typedef struct HHS174StatusSnapshot {
    uint32_t abi_version;
    uint64_t transition_count;
    HHS174PhaseCoordinate phase;
    HHS174Digest256 current_frame_identity;
    char hash72_tip[HHS174_HASH72_LEN + 1u];
    size_t vector_object_count;
    size_t active_suffix_count;
    uint8_t has_candidate;
    uint8_t boot_admitted;
} HHS174StatusSnapshot;

const char *hhs174_status_string(HHS174Status status);
HHS174Status hhs174_status(const HHS174Runtime *runtime, HHS174StatusSnapshot *out);
HHS174Status hhs174_genesis_init(HHS174Runtime *runtime, const void *seed, size_t seed_size);
HHS174Status hhs174_boot_fingerprint(const HHS174Runtime *runtime, const void *challenge, size_t challenge_size, HHS174Digest256 *canonical, HHS174Digest256 *instance);
HHS174Status hhs174_frame_read(const HHS174Runtime *runtime, HHS174Frame5184 *out);
HHS174Status hhs174_frame_execute(HHS174Runtime *runtime, HHS174Opcode opcode, uint64_t operand, HHS174Frame5184 *out_candidate);
HHS174Status hhs174_frame_commit(HHS174Runtime *runtime, const HHS174AdmissionWitness *witness);
HHS174Status hhs174_phase_coordinate(uint64_t transition, HHS174PhaseCoordinate *out);
HHS174Status hhs174_phase_step(HHS174Runtime *runtime, HHS174Opcode opcode, uint64_t operand);
HHS174Status hhs174_phase_closure(const HHS174PhaseCoordinate *phase, uint8_t *out_complete);
HHS174Status hhs174_harmonic_compile(const void *source, size_t source_size, HHS174Digest256 *operator_identity);
HHS174Status hhs174_harmonic_execute(HHS174Runtime *runtime, uint64_t numerator, uint64_t denominator, HHS174Frame5184 *out_candidate);
HHS174Status hhs174_hash72_project(const void *data, size_t size, char out_hash72[HHS174_HASH72_LEN + 1u]);
HHS174Status hhs174_hash72_tip(const HHS174Runtime *runtime, char out_hash72[HHS174_HASH72_LEN + 1u]);
HHS174Status hhs174_hash216_build(const HHS174Hash72Transition *transition, HHS174Hash216Array *out);
HHS174Status hhs174_hash216_index_character(const HHS174Hash216Array *array, uint16_t position, const HHS174Digest256 *previous_index, HHS174Digest256 *out);
HHS174Status hhs174_hash216_validate(const HHS174Hash216Array *array);
HHS174Status hhs174_vector_query(const HHS174VectorStore *store, const HHS174Digest256 *query_identity, const char *incoming_tip, size_t *out_index);
HHS174Status hhs174_vector_retrieve(const HHS174VectorStore *store, size_t index, const char *incoming_tip, HHS174VectorObject *out);
HHS174Status hhs174_vector_admit(HHS174VectorStore *store, const HHS174VectorObject *object, const HHS174AdmissionWitness *witness, size_t *out_index);
HHS174Status hhs174_vector_quarantine(HHS174VectorStore *store, const HHS174Digest256 *identity);
HHS174Status hhs174_delta_apply(const HHS174Frame5184 *source, const HHS174SparseDelta *delta, HHS174Frame5184 *out);
HHS174Status hhs174_efficiency_compare(HHS174EfficiencyRecord *record);
HHS174Status hhs174_efficiency_update(HHS174EfficiencyRecord *record, const HHS174CostUnits *cost, uint8_t retrieval_path, uint8_t accepted);
HHS174Status hhs174_genesis_audit(const HHS174Runtime *runtime, const void *challenge, size_t challenge_size, uint64_t sample_count, HHS174AuditResult *out);
HHS174Status hhs174_replay(const void *seed, size_t seed_size, const HHS174Opcode *opcodes, const uint64_t *operands, size_t operation_count, HHS174Digest256 *out_frame_identity, char out_hash72[HHS174_HASH72_LEN + 1u]);
HHS174Status hhs174_receipt_export(const HHS174Runtime *runtime, void *buffer, size_t buffer_size, size_t *out_size);

#ifdef __cplusplus
}
#endif

#endif
