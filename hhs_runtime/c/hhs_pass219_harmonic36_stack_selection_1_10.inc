#include "../include/hhs_pass219_harmonic36_stack_selection_1_10.h"

#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static uint64_t h36_stack_mix64(uint64_t x) {
    x += UINT64_C(0x9e3779b97f4a7c15);
    x = (x ^ (x >> 30U)) * UINT64_C(0xbf58476d1ce4e5b9);
    x = (x ^ (x >> 27U)) * UINT64_C(0x94d049bb133111eb);
    return x ^ (x >> 31U);
}

static int h36_stack_kind_valid(uint32_t kind) {
    return kind == HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10 ||
           kind == HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64;
}

static uint64_t h36_stack_ratio_x1000(
    uint64_t numerator,
    uint64_t denominator
) {
    if (denominator == 0U)
        return 0U;
    if (numerator > UINT64_MAX / UINT64_C(1000))
        return (numerator / denominator) * UINT64_C(1000);
    return (numerator * UINT64_C(1000)) / denominator;
}

static void h36_stack_vector_key216(
    uint32_t candidate_id,
    uint32_t stack_kind,
    uint64_t workload_signature36,
    uint64_t semantic_result_signature64,
    char out_key[HHS_EXACT_UQCEL_HASH216_STRLEN]
) {
    size_t i;
    uint64_t seed =
        h36_stack_mix64(
            workload_signature36 ^
            semantic_result_signature64 ^
            ((uint64_t)candidate_id << 32U) ^
            (uint64_t)stack_kind
        );
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
        seed = h36_stack_mix64(
            seed ^ ((uint64_t)(i + 1U) * UINT64_C(0x100000001b3))
        );
        out_key[i] =
            HHS_EXACT_HASH72_ALPHABET[seed % HHS_EXACT_HASH72_LEN];
    }
    out_key[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
}

static HHSExactStatus h36_stack_candidate_validate(
    const HHSExactPass219H36StackCandidateEvidenceV1 *candidate
) {
    size_t i;
    if (candidate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (candidate->struct_size != sizeof(*candidate) ||
        candidate->version != HHS_EXACT_PASS219_H36_STACK_SELECTION_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (candidate->candidate_id == 0U ||
        !h36_stack_kind_valid(candidate->stack_kind) ||
        candidate->workload_signature36 == 0U ||
        (candidate->workload_signature36 &
         ~HHS_EXACT_PASS219_H36_WORD_MASK) != 0U ||
        candidate->semantic_result_signature64 == 0U ||
        candidate->median_ns == 0U ||
        candidate->sample_count == 0U ||
        candidate->rounds_per_sample == 0U ||
        candidate->exact_result_equal != 1U ||
        candidate->measurement_executed != 1U ||
        candidate->candidate_only != 1U ||
        candidate->vector_key216_present != 1U ||
        candidate->hash216_lineage_claim != 0U ||
        candidate->canonical_mutation_authority != 0U ||
        candidate->canonical_hash72_authority != 0U ||
        candidate->canonical_hash216_authority != 0U ||
        candidate->canonical_persistence_authority != 0U ||
        candidate->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (candidate->vector_key216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] != '\0')
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
        if (strchr(HHS_EXACT_HASH72_ALPHABET,
                   candidate->vector_key216[i]) == NULL)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_h36_stack_candidate_prepare(
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
    HHSExactPass219H36StackCandidateEvidenceV1 *out_candidate
) {
    if (out_candidate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (candidate_id == 0U ||
        !h36_stack_kind_valid(stack_kind) ||
        workload_signature36 == 0U ||
        (workload_signature36 & ~HHS_EXACT_PASS219_H36_WORD_MASK) != 0U ||
        semantic_result_signature64 == 0U ||
        median_ns == 0U ||
        sample_count == 0U ||
        rounds_per_sample == 0U ||
        exact_result_equal != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_candidate, 0, sizeof(*out_candidate));
    out_candidate->struct_size = (uint32_t)sizeof(*out_candidate);
    out_candidate->version =
        HHS_EXACT_PASS219_H36_STACK_SELECTION_VERSION;
    out_candidate->candidate_id = candidate_id;
    out_candidate->stack_kind = stack_kind;
    out_candidate->workload_signature36 =
        workload_signature36 & HHS_EXACT_PASS219_H36_WORD_MASK;
    out_candidate->semantic_result_signature64 =
        semantic_result_signature64;
    out_candidate->median_ns = median_ns;
    out_candidate->sample_count = sample_count;
    out_candidate->rounds_per_sample = rounds_per_sample;
    out_candidate->process_working_state_bytes =
        process_working_state_bytes;
    out_candidate->resource_events = resource_events;
    out_candidate->exact_result_equal = 1U;
    out_candidate->measurement_executed = 1U;
    out_candidate->candidate_only = 1U;
    out_candidate->vector_key216_present = 1U;
    out_candidate->hash216_lineage_claim = 0U;
    out_candidate->canonical_mutation_authority = 0U;
    out_candidate->canonical_hash72_authority = 0U;
    out_candidate->canonical_hash216_authority = 0U;
    out_candidate->canonical_persistence_authority = 0U;
    out_candidate->floating_point_authority = 0U;
    h36_stack_vector_key216(
        candidate_id,
        stack_kind,
        out_candidate->workload_signature36,
        semantic_result_signature64,
        out_candidate->vector_key216
    );
    return h36_stack_candidate_validate(out_candidate);
}

HHSExactStatus hhs_exact_pass219_h36_stack_select(
    const HHSExactPass219H36StackCandidateEvidenceV1 *first,
    const HHSExactPass219H36StackCandidateEvidenceV1 *second,
    HHSExactPass219H36StackSelectionV1 *out_selection
) {
    const HHSExactPass219H36StackCandidateEvidenceV1 *winner;
    const HHSExactPass219H36StackCandidateEvidenceV1 *runner_up;
    HHSExactStatus status;

    if (out_selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = h36_stack_candidate_validate(first);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = h36_stack_candidate_validate(second);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (first->candidate_id == second->candidate_id ||
        first->stack_kind == second->stack_kind ||
        first->workload_signature36 != second->workload_signature36 ||
        first->semantic_result_signature64 !=
            second->semantic_result_signature64 ||
        first->rounds_per_sample != second->rounds_per_sample)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (first->median_ns < second->median_ns ||
        (first->median_ns == second->median_ns &&
         first->candidate_id < second->candidate_id)) {
        winner = first;
        runner_up = second;
    } else {
        winner = second;
        runner_up = first;
    }

    memset(out_selection, 0, sizeof(*out_selection));
    out_selection->struct_size = (uint32_t)sizeof(*out_selection);
    out_selection->version =
        HHS_EXACT_PASS219_H36_STACK_SELECTION_VERSION;
    out_selection->candidate_count =
        HHS_EXACT_PASS219_H36_STACK_CANDIDATE_COUNT;
    out_selection->selected_candidate_id = winner->candidate_id;
    out_selection->selected_stack_kind = winner->stack_kind;
    out_selection->workload_signature36 = winner->workload_signature36;
    out_selection->semantic_result_signature64 =
        winner->semantic_result_signature64;
    out_selection->selected_median_ns = winner->median_ns;
    out_selection->runner_up_median_ns = runner_up->median_ns;
    out_selection->speedup_x1000 =
        h36_stack_ratio_x1000(runner_up->median_ns, winner->median_ns);
    out_selection->exact_equality_before_timing = 1U;
    out_selection->timing_executed = 1U;
    out_selection->measured_winner = 1U;
    out_selection->stable_tie_break_by_candidate_id = 1U;
    out_selection->candidate_only = 1U;
    out_selection->vector_store_metadata_only = 1U;
    out_selection->canonical_mutation_authority = 0U;
    out_selection->canonical_hash72_authority = 0U;
    out_selection->canonical_hash216_authority = 0U;
    out_selection->canonical_persistence_authority = 0U;
    out_selection->floating_point_authority = 0U;
    memcpy(
        out_selection->selected_vector_key216,
        winner->vector_key216,
        sizeof(out_selection->selected_vector_key216)
    );
    return hhs_exact_pass219_h36_stack_selection_validate(out_selection);
}

HHSExactStatus hhs_exact_pass219_h36_stack_generalization_decision(
    const HHSExactPass219H36StackSelectionV1 *selection,
    const HHSExactPass219OptimizationTargetEvidenceV1 *target_evidence,
    HHSExactPass219OptimizationTargetDecisionV1 *out_decision
) {
    HHSExactStatus status;
    if (target_evidence == NULL || out_decision == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_h36_stack_selection_validate(selection);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_exact_pass219_classify_optimization_target(
        target_evidence, out_decision);
}

HHSExactStatus hhs_exact_pass219_h36_stack_selection_validate(
    const HHSExactPass219H36StackSelectionV1 *selection
) {
    size_t i;
    if (selection == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (selection->struct_size != sizeof(*selection) ||
        selection->version != HHS_EXACT_PASS219_H36_STACK_SELECTION_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (selection->candidate_count !=
            HHS_EXACT_PASS219_H36_STACK_CANDIDATE_COUNT ||
        selection->selected_candidate_id == 0U ||
        !h36_stack_kind_valid(selection->selected_stack_kind) ||
        selection->workload_signature36 == 0U ||
        (selection->workload_signature36 &
         ~HHS_EXACT_PASS219_H36_WORD_MASK) != 0U ||
        selection->semantic_result_signature64 == 0U ||
        selection->selected_median_ns == 0U ||
        selection->runner_up_median_ns == 0U ||
        selection->speedup_x1000 == 0U ||
        selection->exact_equality_before_timing != 1U ||
        selection->timing_executed != 1U ||
        selection->measured_winner != 1U ||
        selection->stable_tie_break_by_candidate_id != 1U ||
        selection->candidate_only != 1U ||
        selection->vector_store_metadata_only != 1U ||
        selection->canonical_mutation_authority != 0U ||
        selection->canonical_hash72_authority != 0U ||
        selection->canonical_hash216_authority != 0U ||
        selection->canonical_persistence_authority != 0U ||
        selection->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (selection->selected_vector_key216[
            HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] != '\0')
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
        if (strchr(HHS_EXACT_HASH72_ALPHABET,
                   selection->selected_vector_key216[i]) == NULL)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}
