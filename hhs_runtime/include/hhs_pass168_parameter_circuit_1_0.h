#ifndef HHS_PASS168_PARAMETER_CIRCUIT_1_0_H
#define HHS_PASS168_PARAMETER_CIRCUIT_1_0_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_PASS168_VERSION_MAJOR 1U
#define HHS_PASS168_VERSION_MINOR 0U
#define HHS_PASS168_VERSION_PATCH 0U
#define HHS_PASS168_PARAMETER_COUNT 40U
#define HHS_PASS168_P_COUNT 28U
#define HHS_PASS168_E_COUNT 12U
#define HHS_PASS168_THREAD_COUNT 64U
#define HHS_PASS168_RAW_THREAD_COUNT 40U
#define HHS_PASS168_DERIVED_THREAD_COUNT 24U
#define HHS_PASS168_CELLS_PER_THREAD 81U
#define HHS_PASS168_BANKS_PER_THREAD 9U
#define HHS_PASS168_CELLS_PER_BANK 9U
#define HHS_PASS168_TOTAL_CELLS 5184U
#define HHS_PASS168_SOURCE_BYTES 424U
#define HHS_PASS168_HASH216_LEN 216U
#define HHS_PASS168_HASH216_STRLEN 217U
#define HHS_PASS168_SOURCE_SHA256_HEX_LEN 64U
#define HHS_PASS168_SOURCE_SHA256_HEX_STRLEN 65U
#define HHS_PASS168_MAX_ABS_INVERSE_DEPTH 8

#define HHS_PASS168_TERMINAL_CLASSIFICATION \
    "HHS_PASS_168_VM81_5184_CELL_HARMONICODE_PARAMETER_CIRCUIT_AND_SPARSE_TENSOR_CONTROL_FABRIC_VERIFIED"

typedef enum HHSPass168Decision {
    HHS_PASS168_DECISION_UNRESOLVED = 0,
    HHS_PASS168_DECISION_ADMIT = 1,
    HHS_PASS168_DECISION_REJECT = 2
} HHSPass168Decision;

typedef enum HHSPass168RejectReason {
    HHS_PASS168_REASON_NONE = 0,
    HHS_PASS168_REASON_STRUCT_SIZE = 1,
    HHS_PASS168_REASON_STALE_PRIOR_ROOT = 2,
    HHS_PASS168_REASON_INVALID_PARAMETER = 3,
    HHS_PASS168_REASON_ZERO_DENOMINATOR_ROLE = 4,
    HHS_PASS168_REASON_INVERSE_DEPTH_DOMAIN = 5,
    HHS_PASS168_REASON_RATIONAL_OVERFLOW = 6,
    HHS_PASS168_REASON_MATRIX_DOMAIN = 7,
    HHS_PASS168_REASON_RECEIPT_MISMATCH = 8
} HHSPass168RejectReason;

typedef struct HHSPass168Rational {
    int64_t numerator;
    uint64_t denominator;
} HHSPass168Rational;

typedef struct HHSPass168Matrix3 {
    HHSPass168Rational v[9];
} HHSPass168Matrix3;

typedef struct HHSPass168SourceStats {
    uint32_t struct_size;
    uint32_t source_bytes;
    uint32_t matched_parenthesis_pairs;
    uint32_t literal_equals_count;
    uint32_t double_equals_token_count;
    uint32_t source_preserved;
    char source_sha256_hex[HHS_PASS168_SOURCE_SHA256_HEX_STRLEN];
    char source_hash72[HHS_EXACT_HASH72_STRLEN];
} HHSPass168SourceStats;

typedef struct HHSPass168ParameterSpan {
    uint8_t parameter_id;
    uint8_t thread_id;
    uint8_t nesting_depth;
    uint8_t reserved0;
    uint16_t open_offset;
    uint16_t close_offset;
} HHSPass168ParameterSpan;

typedef struct HHSPass168EqualityGate {
    uint8_t gate_id;
    uint8_t thread_id;
    uint8_t comparator_id;
    uint8_t side;
    uint16_t source_offset;
    uint16_t reserved0;
} HHSPass168EqualityGate;

typedef struct HHSPass168Address {
    uint16_t global_index;
    uint8_t global_row;
    uint8_t global_col;
    uint8_t thread_id;
    uint8_t thread_row;
    uint8_t thread_col;
    uint8_t local_index;
    uint8_t local_row;
    uint8_t local_col;
    uint8_t bank_id;
    uint8_t bank_row;
    uint8_t bank_col;
    uint8_t loshu_index;
    uint8_t loshu_row;
    uint8_t loshu_col;
} HHSPass168Address;

typedef struct HHSPass168CircuitState {
    uint32_t struct_size;
    uint32_t version;
    uint64_t generation;
    HHSPass168Rational raw[HHS_PASS168_PARAMETER_COUNT];
    HHSPass168Rational derived[HHS_PASS168_DERIVED_THREAD_COUNT];
    HHSPass168Matrix3 upper;
    HHSPass168Matrix3 lower;
    HHSPass168Matrix3 successor;
    char state_hash216[HHS_PASS168_HASH216_STRLEN];
    char last_receipt_hash72[HHS_EXACT_HASH72_STRLEN];
    uint8_t committed;
    uint8_t reserved0[7];
} HHSPass168CircuitState;

typedef struct HHSPass168Candidate {
    uint32_t struct_size;
    uint32_t version;
    uint64_t update_mask;
    uint64_t affected_thread_bitmap;
    HHSPass168Rational values[HHS_PASS168_PARAMETER_COUNT];
    char expected_prior_hash216[HHS_PASS168_HASH216_STRLEN];
} HHSPass168Candidate;

typedef struct HHSPass168Transition {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;
    uint32_t reject_reason;
    uint64_t generation_before;
    uint64_t generation_after;
    uint64_t update_mask;
    uint64_t affected_thread_bitmap;
    HHSPass168Rational before_raw[HHS_PASS168_PARAMETER_COUNT];
    HHSPass168Rational after_raw[HHS_PASS168_PARAMETER_COUNT];
    char prior_state_hash216[HHS_PASS168_HASH216_STRLEN];
    char committed_state_hash216[HHS_PASS168_HASH216_STRLEN];
    char prior_receipt_hash72[HHS_EXACT_HASH72_STRLEN];
    char change_hash72[HHS_EXACT_HASH72_STRLEN];
    char receipt_hash72[HHS_EXACT_HASH72_STRLEN];
    char hash216_triplet[HHS_PASS168_HASH216_STRLEN];
    char hash216_identity[HHS_PASS168_HASH216_STRLEN];
    uint8_t committed;
    uint8_t fallback_used;
    uint8_t reserved0[6];
} HHSPass168Transition;

typedef struct HHSPass168SelfTest {
    uint32_t struct_size;
    uint32_t source_preserved;
    uint32_t parenthesis_parameters_registered;
    uint32_t equality_half_gates_registered;
    uint32_t threads_registered;
    uint32_t raw_threads;
    uint32_t derived_threads;
    uint32_t cells_covered;
    uint32_t duplicate_addresses;
    uint32_t inverse_address_failures;
    uint32_t banks_per_thread;
    uint32_t cells_per_bank;
    uint32_t exact_rational_authority;
    uint32_t floating_point_canonical_authority;
    uint32_t baseline_upper_equals_361L;
    uint32_t baseline_lower_equals_360L;
    uint32_t successor_residual_equals_L;
    uint32_t loshu_square_identity;
    uint32_t gauge_cancellation_verified;
    uint32_t ratio_channels_verified;
    uint32_t comparators_verified;
    uint32_t sparse_dependency_updates_verified;
    uint32_t single_vm81_commit_authority;
    uint32_t hash72_receipts_verified;
    uint32_t hash216_identity_verified;
    uint32_t rollback_verified;
    uint32_t repair_verified;
    uint32_t deterministic_replay_verified;
    uint32_t x86_64_verified;
    uint32_t arm64_verified;
    uint32_t fallback_used;
    char deterministic_record_hash216[HHS_PASS168_HASH216_STRLEN];
} HHSPass168SelfTest;

HHS_EXACT_API uint32_t hhs_pass168_version(void);
HHS_EXACT_API const char *hhs_pass168_source_text(void);
HHS_EXACT_API const char *hhs_pass168_source_sha256_hex(void);
HHS_EXACT_API HHSExactStatus hhs_pass168_source_stats(HHSPass168SourceStats *out);
HHS_EXACT_API HHSExactStatus hhs_pass168_parameter_registry(
    HHSPass168ParameterSpan out[HHS_PASS168_P_COUNT]
);
HHS_EXACT_API HHSExactStatus hhs_pass168_equality_registry(
    HHSPass168EqualityGate out[HHS_PASS168_E_COUNT]
);
HHS_EXACT_API HHSExactStatus hhs_pass168_address_encode(
    uint8_t thread_id,
    uint8_t local_index,
    HHSPass168Address *out
);
HHS_EXACT_API HHSExactStatus hhs_pass168_address_decode(
    uint16_t global_index,
    HHSPass168Address *out
);
HHS_EXACT_API HHSExactStatus hhs_pass168_rational_normalize(
    int64_t numerator,
    uint64_t denominator,
    HHSPass168Rational *out
);
HHS_EXACT_API HHSExactStatus hhs_pass168_matrix_invariants(void);
HHS_EXACT_API HHSExactStatus hhs_pass168_state_initialize(HHSPass168CircuitState *out);
HHS_EXACT_API HHSExactStatus hhs_pass168_cell_value(
    const HHSPass168CircuitState *state,
    uint16_t global_index,
    HHSPass168Rational *out
);
HHS_EXACT_API HHSExactStatus hhs_pass168_candidate_begin(
    const HHSPass168CircuitState *state,
    HHSPass168Candidate *out
);
HHS_EXACT_API HHSExactStatus hhs_pass168_candidate_set(
    HHSPass168Candidate *candidate,
    uint8_t parameter_index,
    int64_t numerator,
    uint64_t denominator
);
HHS_EXACT_API HHSExactStatus hhs_pass168_candidate_validate(
    const HHSPass168CircuitState *prior,
    HHSPass168Candidate *candidate,
    uint32_t *out_reject_reason
);
HHS_EXACT_API HHSExactStatus hhs_pass168_candidate_apply(
    const HHSPass168CircuitState *prior,
    HHSPass168Candidate *candidate,
    HHSPass168CircuitState *out_candidate
);
HHS_EXACT_API HHSExactStatus hhs_pass168_commit_candidate(
    const HHSPass168CircuitState *prior,
    HHSPass168Candidate *candidate,
    HHSPass168CircuitState *out_committed,
    HHSPass168Transition *out_transition
);
HHS_EXACT_API HHSExactStatus hhs_pass168_replay_transition(
    const HHSPass168CircuitState *prior,
    const HHSPass168Transition *transition,
    HHSPass168CircuitState *out_replayed
);
HHS_EXACT_API HHSExactStatus hhs_pass168_rollback_transition(
    const HHSPass168Transition *transition,
    HHSPass168CircuitState *out_prior
);
HHS_EXACT_API HHSExactStatus hhs_pass168_repair_transition(
    const HHSPass168Transition *transition,
    HHSPass168CircuitState *out_repaired
);
HHS_EXACT_API HHSExactStatus hhs_pass168_self_test(HHSPass168SelfTest *out);

#ifdef __cplusplus
}
#endif

#endif
