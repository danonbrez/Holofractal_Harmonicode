#ifndef HHS_PASS219_COMPRESSION_DEBT_CLOSURE_3_25_1_0_H
#define HHS_PASS219_COMPRESSION_DEBT_CLOSURE_3_25_1_0_H

#include "hhs_pass219_global_latency_policy_25_3_1_0.h"
#include "hhs_pass219_harmonic36_hash216_rna_binding_1_0.h"
#include "hhs_pass219_mandatory_genesis_scaling_1_22.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_COMPRESSION_DEBT_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_COMPRESSION_DEBT_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_COMPRESSION_DEBT_VERSION_PATCH 0U

#define HHS_EXACT_PASS219_DEBT_BOUNDARY_BITS 5184U
#define HHS_EXACT_PASS219_DEBT_BOUNDARY_BYTES 648U
#define HHS_EXACT_PASS219_DEBT_VM81_CELLS 81U
#define HHS_EXACT_PASS219_DEBT_X86_WORD_BITS 64U
#define HHS_EXACT_PASS219_DEBT_HASH72_LANES 3U
#define HHS_EXACT_PASS219_DEBT_HASH72_GLYPHS_PER_LANE 72U
#define HHS_EXACT_PASS219_DEBT_HASH216_OCCURRENCES 216U
#define HHS_EXACT_PASS219_DEBT_SHA256_BYTES 32U

#define HHS_EXACT_PASS219_DEBT_EXCHANGE_NUMERATOR 3U
#define HHS_EXACT_PASS219_DEBT_EXCHANGE_DENOMINATOR 25U
#define HHS_EXACT_PASS219_CAPACITY_EXCHANGE_NUMERATOR 25U
#define HHS_EXACT_PASS219_CAPACITY_EXCHANGE_DENOMINATOR 3U

#define HHS_EXACT_PASS219_ACTIVE_SURFACE_CELLS 7U
#define HHS_EXACT_PASS219_ACTIVE_SURFACE_TOTAL_CELLS 81U
#define HHS_EXACT_PASS219_ACTIVE_SURFACE_REDUCTION_NUMERATOR 81U
#define HHS_EXACT_PASS219_ACTIVE_SURFACE_REDUCTION_DENOMINATOR 7U
#define HHS_EXACT_PASS219_ACTIVE_SURFACE_REDUCTION_X1000 11571U

#define HHS_EXACT_PASS219_DEBT_MAX_LAYERS 81U
#define HHS_EXACT_PASS219_DEBT_MAX_TRANSFER_PAIRS 32U

typedef enum HHSExactPass219CompressionDebtTransferRoleV1 {
    HHS_EXACT_PASS219_DEBT_TRANSFER_ROLE_INVALID = 0,
    HHS_EXACT_PASS219_DEBT_TRANSFER_ROLE_SOURCE_DEBIT = 1,
    HHS_EXACT_PASS219_DEBT_TRANSFER_ROLE_TARGET_CREDIT = 2
} HHSExactPass219CompressionDebtTransferRoleV1;

typedef enum HHSExactPass219CompressionDebtScheduleDecisionV1 {
    HHS_EXACT_PASS219_DEBT_SCHEDULE_INVALID = 0,
    HHS_EXACT_PASS219_DEBT_SCHEDULE_LOCAL_WITHIN_25_3 = 1,
    HHS_EXACT_PASS219_DEBT_SCHEDULE_TRANSFER_OR_RECOMPRESS = 2
} HHSExactPass219CompressionDebtScheduleDecisionV1;

typedef struct HHSExactPass219CompressionDebtPolicyV1 {
    uint32_t struct_size;
    uint32_t version;

    uint32_t boundary_bits;
    uint32_t boundary_bytes;
    uint32_t vm81_cells;
    uint32_t x86_word_bits;

    uint32_t hash72_lanes;
    uint32_t hash72_glyphs_per_lane;
    uint32_t hash216_occurrences;
    uint32_t sha256_bytes;

    uint32_t debt_exchange_numerator;
    uint32_t debt_exchange_denominator;
    uint32_t capacity_exchange_numerator;
    uint32_t capacity_exchange_denominator;

    uint32_t active_surface_cells;
    uint32_t active_surface_total_cells;
    uint32_t active_surface_reduction_numerator;
    uint32_t active_surface_reduction_denominator;
    uint32_t active_surface_reduction_x1000;

    uint8_t physical_time_monotonic;
    uint8_t timing_is_noncanonical;
    uint8_t compression_debt_is_conserved_quantity;
    uint8_t anonymous_debt_cross_boundary_allowed;
    uint8_t reciprocal_transfer_required;
    uint8_t full_vm81_frame_preserved;
    uint8_t hash216_indexes_required_for_transfer;
    uint8_t singleton_vm81_authority_preserved;
    uint8_t hash72_hash216_authority_preserved;
    uint8_t floating_point_authority;
    uint8_t reserved0[2];
} HHSExactPass219CompressionDebtPolicyV1;

typedef struct HHSExactPass219CompressionDebtExchangeV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t debt_units;

    uint64_t compression_numerator;
    uint32_t compression_denominator;
    uint32_t reserved0;

    uint64_t execution_capacity_numerator;
    uint32_t execution_capacity_denominator;
    uint32_t reserved1;

    uint8_t reciprocal_exact;
    uint8_t floating_point_authority;
    uint8_t reserved2[6];
} HHSExactPass219CompressionDebtExchangeV1;

typedef struct HHSExactPass219CompressionDebtLayerInputV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t layer_id;
    uint32_t reserved0;

    uint64_t inbound_debt;
    uint64_t issued_debt;
    uint64_t executed_settled;
    uint64_t retained_compressed;
    uint64_t transferred_out;

    uint8_t active_cell_mask[HHS_EXACT_PASS219_DEBT_VM81_CELLS];
    uint8_t canonical_authority_requested;
    uint8_t reserved1[6];
} HHSExactPass219CompressionDebtLayerInputV1;

typedef struct HHSExactPass219CompressionDebtLayerResultV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t layer_id;
    uint32_t active_cell_count;

    uint64_t inbound_debt;
    uint64_t issued_debt;
    uint64_t executed_settled;
    uint64_t retained_compressed;
    uint64_t transferred_out;
    uint64_t total_obligation;
    uint64_t accounted_obligation;
    uint64_t outstanding_debt;

    uint8_t local_zero_sum_closed;
    uint8_t active_surface_within_7_of_81;
    uint8_t full_vm81_frame_preserved;
    uint8_t canonical_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[3];
} HHSExactPass219CompressionDebtLayerResultV1;

typedef struct HHSExactPass219CompressionDebtTransferEntryV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t role;
    uint32_t source_layer_id;
    uint32_t target_layer_id;
    uint32_t modality_id;

    uint64_t amount;

    uint16_t source_slot5184;
    uint16_t target_slot5184;
    uint8_t phase_left8;
    uint8_t phase_right8;
    uint8_t witness_present;
    uint8_t canonical_authority_requested;

    char source_transition_word216[HHS_EXACT_UQCEL_HASH216_STRLEN];
    char target_transition_word216[HHS_EXACT_UQCEL_HASH216_STRLEN];
    uint8_t closure_witness_sha256[HHS_EXACT_PASS219_DEBT_SHA256_BYTES];
} HHSExactPass219CompressionDebtTransferEntryV1;

typedef struct HHSExactPass219CompressionDebtTransferPairV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219CompressionDebtTransferEntryV1 source_debit;
    HHSExactPass219CompressionDebtTransferEntryV1 target_credit;

    uint8_t reciprocal_amount_equal;
    uint8_t reciprocal_identity_equal;
    uint8_t reciprocal_address_equal;
    uint8_t reciprocal_phase_equal;
    uint8_t reciprocal_witness_equal;
    uint8_t canonical_authority;
    uint8_t floating_point_authority;
    uint8_t pair_verified;
} HHSExactPass219CompressionDebtTransferPairV1;

typedef struct HHSExactPass219CompressionDebtGlobalResultV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t layer_count;
    uint32_t transfer_pair_count;

    uint64_t created_total;
    uint64_t settled_total;
    uint64_t retained_total;
    uint64_t internal_transfer_debit_total;
    uint64_t internal_transfer_credit_total;
    uint64_t global_outstanding_debt;

    uint8_t all_layers_closed;
    uint8_t internal_transfers_cancel;
    uint8_t issued_equals_settled_plus_outstanding;
    uint8_t global_zero_sum_closed;
    uint8_t canonical_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[2];
} HHSExactPass219CompressionDebtGlobalResultV1;

typedef struct HHSExactPass219CompressionDebtScheduleResultV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t latency_tier;
    uint32_t decision;

    uint64_t observed_ns;
    uint64_t outstanding_debt;

    uint8_t within_25_over_3_ms;
    uint8_t local_ledger_closed;
    uint8_t active_surface_within_7_of_81;
    uint8_t timing_is_noncanonical;
    uint8_t physical_time_monotonic;
    uint8_t canonical_authority;
    uint8_t reserved0[2];
} HHSExactPass219CompressionDebtScheduleResultV1;

typedef struct HHSExactPass219NativeClosureBoundaryResultV1 {
    uint32_t struct_size;
    uint32_t version;

    uint32_t boundary_bits;
    uint32_t boundary_bytes;
    uint32_t active_cell_count;
    uint32_t transfer_pair_count;

    uint64_t transferred_debt_verified;
    uint64_t outstanding_debt;

    uint8_t vm81_frame_roundtrip_exact;
    uint8_t genesis_sudoku_zero_sum_valid;
    uint8_t ordered_phase_witness_valid;
    uint8_t hash216_lane_order_valid;
    uint8_t hash216_sha256_indexes_complete;
    uint8_t hash216_native_5184_binding_valid;
    uint8_t debt_local_zero_sum_closed;
    uint8_t transferred_debt_fully_typed;
    uint8_t active_surface_within_7_of_81;
    uint8_t latency_policy_bound;
    uint8_t singleton_vm81_authority_preserved;
    uint8_t hash72_hash216_authority_preserved;
    uint8_t canonical_authority;
    uint8_t floating_point_authority;
    uint8_t native_boundary_valid;
    uint8_t reserved0;
} HHSExactPass219NativeClosureBoundaryResultV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_compression_debt_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_compression_debt_policy(
    HHSExactPass219CompressionDebtPolicyV1 *out_policy
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_compression_debt_policy_validate(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_compression_debt_exchange(
    uint64_t debt_units,
    HHSExactPass219CompressionDebtExchangeV1 *out_exchange
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_compression_debt_layer_close(
    const HHSExactPass219CompressionDebtLayerInputV1 *input,
    HHSExactPass219CompressionDebtLayerResultV1 *out_result
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_compression_debt_transfer_pair_verify(
    HHSExactPass219CompressionDebtTransferPairV1 *pair
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_compression_debt_transfer_pair_verify_bound(
    HHSExactPass219CompressionDebtTransferPairV1 *pair,
    const HHSExactPass219Hash216TransitionViewV1 *source_transition,
    const HHSExactPass219Hash216TransitionViewV1 *target_transition
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_compression_debt_global_close(
    const HHSExactPass219CompressionDebtLayerResultV1 *layers,
    size_t layer_count,
    HHSExactPass219CompressionDebtTransferPairV1 *pairs,
    size_t pair_count,
    HHSExactPass219CompressionDebtGlobalResultV1 *out_result
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_compression_debt_schedule_evaluate(
    uint64_t observed_ns,
    const HHSExactPass219CompressionDebtLayerResultV1 *layer,
    HHSExactPass219CompressionDebtScheduleResultV1 *out_result
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_native_5184_closure_boundary_verify(
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *source_transition,
    const HHSExactPass219NativePhaseWitnessV1 *phase_witness,
    const HHSExactPass219CompressionDebtLayerResultV1 *layer,
    HHSExactPass219CompressionDebtTransferPairV1 *pairs,
    size_t pair_count,
    const HHSExactPass219Hash216TransitionViewV1 *target_transitions,
    size_t target_transition_count,
    HHSExactPass219NativeClosureBoundaryResultV1 *out_result
);

#ifdef __cplusplus
}
#endif

#endif
