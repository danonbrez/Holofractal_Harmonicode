#ifndef HHS_PASS219_HHCQ_RECIPROCAL_ECONOMY_1_29_H
#define HHS_PASS219_HHCQ_RECIPROCAL_ECONOMY_1_29_H

#include "hhs_pass219_hhcq_temporal_cubic_1_28.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HHCQ_RECIPROCAL_ECONOMY_VERSION UINT32_C(0x0001001D)
#define HHS_EXACT_PASS219_HHCQ_ECONOMY_PARITY_UNITS UINT64_C(5184)
#define HHS_EXACT_PASS219_HHCQ_ECONOMY_MAX_CANDIDATES UINT32_C(16)

typedef enum HHSExactPass219HHCQEconomyDecisionV1 {
    HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_INVALID = 0,
    HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_REJECTED = 1,
    HHS_EXACT_PASS219_HHCQ_ECONOMY_DECISION_ADMITTED = 2
} HHSExactPass219HHCQEconomyDecisionV1;

typedef struct HHSExactPass219HHCQReciprocalEconomyDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t inherited_policy_state_bytes;
    uint32_t max_candidates;
    uint64_t parity_units;
    uint8_t reciprocal_1_over_n_to_n_boundary;
    uint8_t n_must_be_phase5_divisor;
    uint8_t separate_axis_ledgers;
    uint8_t exact_one_to_one_information_closure;
    uint8_t lower_resolution_recovery_allowed;
    uint8_t spendable_savings_budget;
    uint8_t one_step_translation_required;
    uint8_t all_native_modalities_required;
    uint8_t phase5_resolution_locked;
    uint8_t fixed_size_policy_state;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[3];
} HHSExactPass219HHCQReciprocalEconomyDescriptorV1;

typedef struct HHSExactPass219HHCQEconomyCandidateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t route_id;
    uint16_t reciprocal_n;
    uint8_t intrinsic_resolution_index;
    uint8_t effective_resolution_index;
    uint8_t required_resolution_index;
    uint8_t reserved0;

    uint64_t latency_units;
    uint64_t memory_units;
    uint64_t compression_units;
    uint64_t translation_units;

    uint64_t redundancy_spend_units;
    uint64_t ecc_spend_units;
    uint64_t precision_spend_units;
    uint64_t learning_spend_units;

    uint32_t lossy_information_units;
    uint32_t recovered_information_units;

    uint8_t exact_semantic_closure;
    uint8_t exact_reconstruction;
    uint8_t all_native_modalities_translatable;
    uint8_t one_step_translation;
    uint8_t phase5_resolution_locked;
    uint8_t candidate_only;
    uint8_t canonical_authority_requested;
    uint8_t floating_point_authority_requested;
} HHSExactPass219HHCQEconomyCandidateV1;

typedef struct HHSExactPass219HHCQEconomyResultV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t route_id;
    uint32_t decision;

    uint16_t reciprocal_n;
    uint16_t intrinsic_resolution_parameters;
    uint16_t effective_resolution_parameters;
    uint16_t required_resolution_parameters;
    uint64_t reciprocal_lower_bound_units;
    uint64_t reciprocal_upper_bound_units;

    uint64_t latency_credit_units;
    uint64_t memory_credit_units;
    uint64_t compression_credit_units;
    uint64_t translation_credit_units;
    uint64_t latency_debt_units;
    uint64_t memory_debt_units;
    uint64_t compression_debt_units;
    uint64_t translation_debt_units;

    uint64_t total_savings_units;
    uint64_t total_axis_debt_units;
    uint64_t total_spend_units;
    int64_t net_budget_units;

    uint32_t lossy_information_units;
    uint32_t recovered_information_units;

    uint8_t reciprocal_bounds_met;
    uint8_t information_one_to_one;
    uint8_t effective_resolution_met;
    uint8_t lower_resolution_recovered;
    uint8_t exact_semantic_closure;
    uint8_t exact_reconstruction;
    uint8_t all_native_modalities_translatable;
    uint8_t one_step_translation;
    uint8_t phase5_resolution_locked;
    uint8_t budget_nonnegative;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    uint8_t reserved1[2];
    uint64_t result_signature64;
} HHSExactPass219HHCQEconomyResultV1;

typedef struct HHSExactPass219HHCQEconomySelectionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t candidate_count;
    uint32_t admitted_count;
    uint32_t selected_route_id;
    uint32_t selected_candidate_index;
    uint8_t selected_effective_resolution_index;
    uint8_t selected_intrinsic_resolution_index;
    uint16_t selected_effective_resolution_parameters;
    int64_t selected_net_budget_units;
    uint64_t selection_signature64;
    uint8_t exact_integer_only;
    uint8_t candidate_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    uint8_t reserved0[4];
} HHSExactPass219HHCQEconomySelectionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_hhcq_reciprocal_economy_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_reciprocal_economy_descriptor(
    HHSExactPass219HHCQReciprocalEconomyDescriptorV1 *out_descriptor);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_reciprocal_economy_evaluate(
    const HHSExactPass219HHCQEconomyCandidateV1 *candidate,
    HHSExactPass219HHCQEconomyResultV1 *out_result);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_reciprocal_economy_select(
    const HHSExactPass219HHCQEconomyCandidateV1 *candidates,
    size_t candidate_count,
    HHSExactPass219HHCQEconomySelectionV1 *out_selection);

#ifdef __cplusplus
}
#endif

#endif
