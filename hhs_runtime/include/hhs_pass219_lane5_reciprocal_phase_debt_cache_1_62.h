#ifndef HHS_PASS219_LANE5_RECIPROCAL_PHASE_DEBT_CACHE_1_62_H
#define HHS_PASS219_LANE5_RECIPROCAL_PHASE_DEBT_CACHE_1_62_H

#include "hhs_runtime_uqcel_1_8.h"
#include "hhs_hash216_bytes.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VERSION UINT32_C(0x0001003e)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_NAMESPACE UINT32_C(0x0002193e)

#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_VM81_CELLS UINT32_C(81)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_RECIPROCAL_CLASSES UINT32_C(41)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_OUTER_PAIRS UINT32_C(40)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_CENTER_POSITION UINT32_C(41)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_FINGERPRINT_CELLS UINT32_C(9)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_OPERATION64_STATES UINT32_C(64)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_PHASE_MODULUS UINT32_C(72)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_HALF_CYCLE UINT32_C(36)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_ORBIT_STEP UINT32_C(16)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_LO_SHU_SUM INT32_C(45)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_PAIR_SUM INT32_C(90)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_CLOSURE_OFFSET INT32_C(-45)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_QUANT_DENOMINATOR INT32_C(9)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_QUANT_NUMERATOR_ABS_MAX INT32_C(81)
#define HHS_EXACT_PASS219_LANE5_PHASE_DEBT_SERIALIZATION_CHARS UINT32_C(5184)

typedef enum HHSExactPass219Lane5PhaseDebtReasonV1 {
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_NONE = 0,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_CLASS_RANGE = 1,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_CENTER_NOT_PAIR = 2,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_ORIENTATION = 3,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_QUANTIZATION_RANGE = 4,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_PHASE_RANGE = 5,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_DIRECTION = 6,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_WITNESS_FLAG = 7,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_OPERATION64_RANGE = 8,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_STACK_OVERFLOW = 9,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_STACK_UNDERFLOW = 10,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_STACK_CLASS_MISMATCH = 11,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_RECIPROCAL_ORIENTATION_MISMATCH = 12,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_QUANTIZATION_RECIPROCAL_MISMATCH = 13,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_PHASE_RECIPROCAL_MISMATCH = 14,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_LINEAGE_MISMATCH = 15,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_OPERATION64_IDENTITY_MISMATCH = 16,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_BOUNDARY_MISMATCH = 17,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_REASON_PHASE_ACCUMULATOR_OVERFLOW = 18
} HHSExactPass219Lane5PhaseDebtReasonV1;

typedef enum HHSExactPass219Lane5PhaseDebtEventKindV1 {
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_OPEN = 1,
    HHS_EXACT_PASS219_LANE5_PHASE_DEBT_EVENT_CLOSE = 2
} HHSExactPass219Lane5PhaseDebtEventKindV1;

typedef struct HHSExactPass219Lane5PhaseDebtAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t namespace_id;
    uint32_t vm81_cells;
    uint32_t reciprocal_classes;
    uint32_t outer_pair_count;
    uint32_t fingerprint_cells;
    uint32_t operation64_states;
    uint32_t serialization_characters;
    uint32_t phase_modulus;
    uint32_t half_cycle;
    uint32_t orbit_step;
    int32_t lo_shu_sum;
    int32_t pair_sum;
    int32_t closure_offset;
    int32_t quantization_denominator;
    int32_t quantization_numerator_abs_max;

    uint8_t one_fixed_nucleus_plus_40_pairs;
    uint8_t center_self_reciprocal;
    uint8_t reciprocal_position_sum_82;
    uint8_t shared_canonical_fingerprint_required;
    uint8_t reciprocal_fingerprint_10_minus_rotate180;
    uint8_t pair_mean_normalizes_to_45;
    uint8_t closure_offset_minus45_to_zero;
    uint8_t exact_one_ninth_quantization;
    uint8_t half_cycle_phase36;
    uint8_t bidirectional_orbit_step16;
    uint8_t operation64_is_ordered_8x8;
    uint8_t recursive_debt_is_separate_from_lane5_skip;
    uint8_t validated_witness_may_skip_compute;
    uint8_t validated_witness_may_skip_closure;
    uint8_t caller_workspace_controls_nesting_capacity;
    uint8_t commit_requires_all_40_pairs_covered;
    uint8_t commit_requires_zero_open_debt;
    uint8_t exact_integer_only;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_commit_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t reserved0[8];
} HHSExactPass219Lane5PhaseDebtAuthorityV1;

typedef struct HHSExactPass219Lane5PhaseDebtPairV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t class_id;
    uint8_t direct_position;
    uint8_t reciprocal_position;
    uint8_t fixed_center;
    uint8_t direct_fingerprint[9];
    uint8_t reciprocal_fingerprint[9];
    uint8_t canonical_fingerprint[9];
    int16_t direct_sum;
    int16_t reciprocal_sum;
    int16_t pair_sum;
    int16_t pair_mean;
    int16_t normalization_offset;
    int16_t normalized_mean;
    uint8_t reciprocal_phase_delta;
    uint8_t quantization_denominator;
    uint8_t operation64_states;
    uint8_t reserved0;
} HHSExactPass219Lane5PhaseDebtPairV1;

typedef struct HHSExactPass219Lane5PhaseDebtTopologyReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t oriented_fingerprint_count;
    uint32_t reciprocal_class_count;
    uint32_t outer_pair_count;
    uint32_t operation64_count;
    uint32_t vm5184_coordinate_count;
    uint8_t all_81_oriented_fingerprints_unique;
    uint8_t all_41_canonical_keys_unique;
    uint8_t all_40_outer_classes_size_two;
    uint8_t center_is_single_fixed_class;
    uint8_t center_is_lo_shu;
    uint8_t center_self_reciprocal;
    uint8_t reciprocal_involution_all_81;
    uint8_t all_outer_pair_means_45;
    uint8_t all_outer_normalized_means_zero;
    uint8_t operation64_bijection;
    uint8_t vm81_x_operation64_is_5184;
    uint8_t exact_integer_only;
    uint8_t topology_valid;
    uint8_t candidate_only;
    uint8_t reserved0[2];
    char receipt_hash216[HHS_HASH216_BYTES_STRLEN];
} HHSExactPass219Lane5PhaseDebtTopologyReceiptV1;

typedef struct HHSExactPass219Lane5PhaseDebtEventV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t kind;
    uint8_t class_id;
    uint8_t orientation;
    uint8_t phase_index;
    int8_t clock_direction;
    int16_t quantized_ninth_numerator;
    uint8_t operation64;
    uint8_t validated_computation_witness;
    uint64_t lineage_token;
} HHSExactPass219Lane5PhaseDebtEventV1;

typedef struct HHSExactPass219Lane5PhaseDebtFrameV1 {
    uint8_t class_id;
    uint8_t opening_orientation;
    uint8_t opening_phase_index;
    int8_t clock_direction;
    int16_t quantized_ninth_numerator;
    uint8_t operation64;
    uint8_t validated_computation_witness;
    uint64_t lineage_token;
    uint8_t canonical_fingerprint[9];
    uint8_t reserved0[7];
} HHSExactPass219Lane5PhaseDebtFrameV1;

typedef struct HHSExactPass219Lane5PhaseDebtCacheV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219Lane5PhaseDebtFrameV1 *frames;
    size_t frame_capacity;
    size_t depth;
    uint64_t closed_pair_mask;
    uint64_t open_event_count;
    uint64_t close_event_count;
    uint64_t rejected_event_count;
    uint64_t validated_witness_replay_count;
    uint64_t forward_clock_steps;
    uint64_t reverse_clock_steps;
    int64_t lifted_phase_units;
    uint8_t current_phase_index;
    uint8_t nucleus_verified;
    uint8_t topology_verified;
    uint8_t exact_integer_only;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t reserved0[3];
} HHSExactPass219Lane5PhaseDebtCacheV1;

typedef struct HHSExactPass219Lane5PhaseDebtEventReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t reason;
    uint32_t kind;
    uint8_t accepted;
    uint8_t class_id;
    uint8_t orientation;
    uint8_t reciprocal_orientation;
    uint8_t phase_index;
    uint8_t expected_reciprocal_phase;
    uint8_t operation64;
    uint8_t validated_computation_witness;
    int8_t clock_direction;
    int16_t quantized_ninth_numerator;
    int16_t normalized_pair_mean;
    uint64_t lineage_token;
    uint64_t depth_before;
    uint64_t depth_after;
    uint64_t closed_pair_mask;
    int64_t lifted_phase_units;
    uint8_t current_phase_index;
    uint8_t all_40_pairs_covered;
    uint8_t zero_open_debt;
    uint8_t commit_ready;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_commit_authority;
    uint8_t reserved0;
    char receipt_hash216[HHS_HASH216_BYTES_STRLEN];
} HHSExactPass219Lane5PhaseDebtEventReceiptV1;

typedef struct HHSExactPass219Lane5PhaseDebtCommitReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t closed_pair_mask;
    uint64_t open_event_count;
    uint64_t close_event_count;
    uint64_t rejected_event_count;
    uint64_t validated_witness_replay_count;
    int64_t lifted_phase_units;
    uint64_t depth;
    uint8_t current_phase_index;
    uint8_t all_40_pairs_covered;
    uint8_t zero_open_debt;
    uint8_t nucleus_verified;
    uint8_t topology_verified;
    uint8_t phase_at_genesis;
    uint8_t commit_ready;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t reserved0[7];
    char receipt_hash216[HHS_HASH216_BYTES_STRLEN];
} HHSExactPass219Lane5PhaseDebtCommitReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_phase_debt_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_phase_debt_authority(
    HHSExactPass219Lane5PhaseDebtAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_phase_debt_pair(
    uint8_t class_id,
    HHSExactPass219Lane5PhaseDebtPairV1 *out_pair
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_phase_debt_topology_verify(
    HHSExactPass219Lane5PhaseDebtTopologyReceiptV1 *out_receipt
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_phase_debt_operation64_encode(
    uint8_t left_basis8,
    uint8_t right_basis8,
    uint8_t *out_operation64
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_phase_debt_operation64_decode(
    uint8_t operation64,
    uint8_t *out_left_basis8,
    uint8_t *out_right_basis8
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_phase_debt_cache_init(
    HHSExactPass219Lane5PhaseDebtCacheV1 *cache,
    HHSExactPass219Lane5PhaseDebtFrameV1 *frames,
    size_t frame_capacity
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_phase_debt_cache_apply(
    HHSExactPass219Lane5PhaseDebtCacheV1 *cache,
    const HHSExactPass219Lane5PhaseDebtEventV1 *event,
    HHSExactPass219Lane5PhaseDebtEventReceiptV1 *out_receipt
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_phase_debt_commit_status(
    const HHSExactPass219Lane5PhaseDebtCacheV1 *cache,
    HHSExactPass219Lane5PhaseDebtCommitReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif
