#ifndef HHS_PASS219_HARMONIC36_STACK_SELECTION_1_10_H
#define HHS_PASS219_HARMONIC36_STACK_SELECTION_1_10_H

#include "hhs_pass219_harmonic36_ka10_monitor_profile_1_9.h"
#include "hhs_pass219_harmonic36_hash216_rna_binding_1_0.h"
#include "hhs_pass219_multimodal_optimization_generalization_1_0.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_STACK_SELECTION_VERSION UINT32_C(0x0001000A)
#define HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10 UINT32_C(1)
#define HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64 UINT32_C(2)
#define HHS_EXACT_PASS219_H36_STACK_CANDIDATE_COUNT UINT32_C(2)

typedef struct HHSExactPass219H36StackCandidateEvidenceV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t candidate_id;
    uint32_t stack_kind;
    uint64_t workload_signature36;
    uint64_t semantic_result_signature64;
    uint64_t median_ns;
    uint32_t sample_count;
    uint32_t rounds_per_sample;
    uint32_t process_working_state_bytes;
    uint32_t resource_events;
    uint8_t exact_result_equal;
    uint8_t measurement_executed;
    uint8_t candidate_only;
    uint8_t vector_key216_present;
    uint8_t hash216_lineage_claim;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[2];
    char vector_key216[HHS_EXACT_UQCEL_HASH216_STRLEN];
} HHSExactPass219H36StackCandidateEvidenceV1;

typedef struct HHSExactPass219H36StackSelectionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t candidate_count;
    uint32_t selected_candidate_id;
    uint32_t selected_stack_kind;
    uint64_t workload_signature36;
    uint64_t semantic_result_signature64;
    uint64_t selected_median_ns;
    uint64_t runner_up_median_ns;
    uint64_t speedup_x1000;
    uint8_t exact_equality_before_timing;
    uint8_t timing_executed;
    uint8_t measured_winner;
    uint8_t stable_tie_break_by_candidate_id;
    uint8_t candidate_only;
    uint8_t vector_store_metadata_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0;
    char selected_vector_key216[HHS_EXACT_UQCEL_HASH216_STRLEN];
} HHSExactPass219H36StackSelectionV1;

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_stack_candidate_prepare(
    uint32_t candidate_id,
    uint32_t stack_kind,
    uint64_t workload_signature36,
    uint64_t semantic_result_signature64,
    uint64_t median_ns,
    uint32_t sample_count,
    uint32_t rounds_per_sample,
    uint32_t process_working_state_bytes,
    uint32_t resource_events,
    uint8_t exact_result_equal,
    HHSExactPass219H36StackCandidateEvidenceV1 *out_candidate);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_stack_select(
    const HHSExactPass219H36StackCandidateEvidenceV1 *first,
    const HHSExactPass219H36StackCandidateEvidenceV1 *second,
    HHSExactPass219H36StackSelectionV1 *out_selection);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_stack_generalization_decision(
    const HHSExactPass219H36StackSelectionV1 *selection,
    const HHSExactPass219OptimizationTargetEvidenceV1 *target_evidence,
    HHSExactPass219OptimizationTargetDecisionV1 *out_decision);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_h36_stack_selection_validate(
    const HHSExactPass219H36StackSelectionV1 *selection);

#ifdef __cplusplus
}
#endif
#endif
