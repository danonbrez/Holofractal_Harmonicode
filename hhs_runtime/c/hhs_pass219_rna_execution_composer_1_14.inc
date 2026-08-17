#include "../include/hhs_pass219_rna_execution_composer_1_14.h"

#include <string.h>

static uint32_t hhs_exact_pass219_rna_execution_composer_version_word(void) {
    return (HHS_EXACT_PASS219_RNA_EXECUTION_COMPOSER_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_RNA_EXECUTION_COMPOSER_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_RNA_EXECUTION_COMPOSER_VERSION_PATCH;
}

static int hhs_exact_pass219_rna_execution_reason_valid(uint32_t reason) {
    return reason <= HHS_EXACT_PASS219_RNA_BYPASS_EXPLICITLY_AUTHORIZED_AUDIT;
}

static int hhs_exact_pass219_rna_execution_reason_is_explicit_replay(uint32_t reason) {
    return reason == HHS_EXACT_PASS219_RNA_BYPASS_FIRST_PRINCIPLES_EXPORT ||
           reason == HHS_EXACT_PASS219_RNA_BYPASS_REFERENCE_ORACLE ||
           reason == HHS_EXACT_PASS219_RNA_BYPASS_ABLATION_OR_BENCHMARK_CONTROL ||
           reason == HHS_EXACT_PASS219_RNA_BYPASS_EXPLICITLY_AUTHORIZED_AUDIT;
}

static HHSExactStatus hhs_exact_pass219_rna_execution_validate_retrieval(
    const HHSExactPass219RNAStateRetrievalV1 *retrieval
) {
    if (retrieval == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (retrieval->struct_size < sizeof(*retrieval) ||
        retrieval->version != hhs_exact_pass219_rna_retrieval_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (retrieval->classification == HHS_EXACT_RNA_STATE_RETRIEVAL_OK) {
        if (retrieval->reference_authenticated != 1U ||
            retrieval->fallback_required != 0U ||
            retrieval->index_invalidated != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (retrieval->identity.struct_size < sizeof(retrieval->identity) ||
            retrieval->identity.version != hhs_exact_pass219_rna_retrieval_version())
            return HHS_EXACT_STATUS_VERSION_MISMATCH;
        if (retrieval->identity.predecessor_hash72[HHS_EXACT_HASH72_LEN] != '\0' ||
            retrieval->identity.predecessor_state_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] != '\0')
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        return HHS_EXACT_STATUS_OK;
    }

    if (retrieval->classification == HHS_EXACT_RNA_STATE_RETRIEVAL_UNAVAILABLE) {
        if (retrieval->reference_authenticated != 0U ||
            retrieval->fallback_required != 1U ||
            retrieval->index_invalidated != 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        return HHS_EXACT_STATUS_OK;
    }

    if (retrieval->classification == HHS_EXACT_RNA_STATE_RETRIEVAL_MISMATCH) {
        if (retrieval->reference_authenticated != 0U ||
            retrieval->fallback_required != 1U ||
            retrieval->index_invalidated != 1U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        return HHS_EXACT_STATUS_OK;
    }

    return HHS_EXACT_STATUS_RANGE_ERROR;
}

static void hhs_exact_pass219_rna_execution_copy_identity(
    const HHSExactPass219RNAStateRetrievalV1 *retrieval,
    HHSExactPass219RNAExecutionPlanV1 *out_plan
) {
    out_plan->checkpoint_counter = retrieval->identity.checkpoint_counter;
    memcpy(out_plan->admitted_dependency_frontier_sha256,
           retrieval->identity.dependency_frontier_sha256,
           HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES);
    memcpy(out_plan->predecessor_hash72,
           retrieval->identity.predecessor_hash72,
           HHS_EXACT_HASH72_STRLEN);
    memcpy(out_plan->predecessor_state_hash216,
           retrieval->identity.predecessor_state_hash216,
           HHS_EXACT_UQCEL_HASH216_STRLEN);
}

static void hhs_exact_pass219_rna_execution_select_genesis(
    HHSExactPass219RNAExecutionPlanV1 *out_plan,
    uint32_t effective_reason
) {
    out_plan->route = HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_GENESIS_REPLAY;
    out_plan->effective_bypass_reason = effective_reason;
    out_plan->genesis_replay_required = 1U;
    out_plan->genesis_replay_count = 1U;
}

uint32_t hhs_exact_pass219_rna_execution_composer_version(void) {
    return hhs_exact_pass219_rna_execution_composer_version_word();
}

HHSExactStatus hhs_exact_pass219_rna_execution_compose(
    const HHSExactPass219RNAStateRetrievalV1 *retrieval,
    const uint8_t current_dependency_frontier_sha256[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES],
    uint32_t requested_bypass_reason,
    HHSExactPass219RNAExecutionPlanV1 *out_plan
) {
    HHSExactStatus status;
    int frontier_matches;

    if (retrieval == NULL || current_dependency_frontier_sha256 == NULL || out_plan == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_exact_pass219_rna_execution_reason_valid(requested_bypass_reason))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_plan, 0, sizeof(*out_plan));
    out_plan->struct_size = (uint32_t)sizeof(*out_plan);
    out_plan->version = hhs_exact_pass219_rna_execution_composer_version_word();
    out_plan->requested_bypass_reason = requested_bypass_reason;
    out_plan->effective_bypass_reason = requested_bypass_reason;
    out_plan->indexed_lookup_observed = 1U;
    memcpy(out_plan->current_dependency_frontier_sha256,
           current_dependency_frontier_sha256,
           HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES);

    status = hhs_exact_pass219_rna_execution_validate_retrieval(retrieval);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    out_plan->retrieval_classification = retrieval->classification;
    out_plan->index_invalidated = retrieval->index_invalidated;

    if (retrieval->classification == HHS_EXACT_RNA_STATE_RETRIEVAL_OK) {
        hhs_exact_pass219_rna_execution_copy_identity(retrieval, out_plan);
        frontier_matches = memcmp(
            current_dependency_frontier_sha256,
            retrieval->identity.dependency_frontier_sha256,
            HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES) == 0;
        out_plan->current_dependency_frontier_verified = frontier_matches ? 1U : 0U;

        if (!frontier_matches) {
            if (requested_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_NONE ||
                requested_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_DEPENDENCY_CHANGED) {
                out_plan->route = HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_DEPENDENCY_SCOPED_RECOMPUTE;
                out_plan->effective_bypass_reason = HHS_EXACT_PASS219_RNA_BYPASS_DEPENDENCY_CHANGED;
                out_plan->dependency_scoped_recompute_required = 1U;
                out_plan->unaffected_reuse_preserved = 1U;
                return HHS_EXACT_STATUS_OK;
            }
            if (hhs_exact_pass219_rna_execution_reason_is_explicit_replay(requested_bypass_reason)) {
                hhs_exact_pass219_rna_execution_select_genesis(out_plan, requested_bypass_reason);
                return HHS_EXACT_STATUS_OK;
            }
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        if (requested_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_NONE) {
            out_plan->route = HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_INDEXED_CONTINUATION;
            out_plan->effective_bypass_reason = HHS_EXACT_PASS219_RNA_BYPASS_NONE;
            out_plan->inherited_indexed_capability_selected = 1U;
            out_plan->authenticated_predecessor_reused = 1U;
            out_plan->indexed_reuse_count = 1U;
            return HHS_EXACT_STATUS_OK;
        }

        if (hhs_exact_pass219_rna_execution_reason_is_explicit_replay(requested_bypass_reason)) {
            hhs_exact_pass219_rna_execution_select_genesis(out_plan, requested_bypass_reason);
            return HHS_EXACT_STATUS_OK;
        }

        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (retrieval->classification == HHS_EXACT_RNA_STATE_RETRIEVAL_UNAVAILABLE) {
        if (requested_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_NONE ||
            requested_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_UNAVAILABLE_AUTHENTICATED_PREDECESSOR) {
            hhs_exact_pass219_rna_execution_select_genesis(
                out_plan,
                HHS_EXACT_PASS219_RNA_BYPASS_UNAVAILABLE_AUTHENTICATED_PREDECESSOR);
            return HHS_EXACT_STATUS_OK;
        }
        if (requested_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_MISSING_OR_INVALID_REFERENCE_EVIDENCE ||
            hhs_exact_pass219_rna_execution_reason_is_explicit_replay(requested_bypass_reason)) {
            hhs_exact_pass219_rna_execution_select_genesis(out_plan, requested_bypass_reason);
            return HHS_EXACT_STATUS_OK;
        }
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    if (requested_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_NONE ||
        requested_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_CORRUPTION_RECOVERY ||
        requested_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_MISSING_OR_INVALID_REFERENCE_EVIDENCE) {
        out_plan->route = HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_RECOVERY_RECOMPUTE;
        out_plan->effective_bypass_reason =
            requested_bypass_reason == HHS_EXACT_PASS219_RNA_BYPASS_MISSING_OR_INVALID_REFERENCE_EVIDENCE
                ? requested_bypass_reason
                : HHS_EXACT_PASS219_RNA_BYPASS_CORRUPTION_RECOVERY;
        out_plan->recovery_recompute_required = 1U;
        return HHS_EXACT_STATUS_OK;
    }
    if (hhs_exact_pass219_rna_execution_reason_is_explicit_replay(requested_bypass_reason)) {
        hhs_exact_pass219_rna_execution_select_genesis(out_plan, requested_bypass_reason);
        return HHS_EXACT_STATUS_OK;
    }
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_rna_execution_prepare_candidate(
    const HHSExactPass219RNAExecutionPlanV1 *plan,
    const HHSExactPass219RNAStateRetrievalV1 *retrieval,
    const HHSExactPass219TranscriptionWitnessV1 *witness,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactPass219RNAAdmissionCandidateV1 *out_candidate
) {
    HHSExactStatus status;
    if (plan == NULL || retrieval == NULL || witness == NULL ||
        candidate_frame == NULL || out_candidate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (plan->struct_size < sizeof(*plan) ||
        plan->version != hhs_exact_pass219_rna_execution_composer_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    status = hhs_exact_pass219_rna_execution_validate_retrieval(retrieval);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (plan->route != HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_INDEXED_CONTINUATION ||
        plan->requested_bypass_reason != HHS_EXACT_PASS219_RNA_BYPASS_NONE ||
        plan->effective_bypass_reason != HHS_EXACT_PASS219_RNA_BYPASS_NONE ||
        plan->inherited_indexed_capability_selected != 1U ||
        plan->authenticated_predecessor_reused != 1U ||
        plan->indexed_reuse_count != 1U ||
        plan->genesis_replay_required != 0U ||
        plan->genesis_replay_count != 0U ||
        plan->current_dependency_frontier_verified != 1U ||
        retrieval->classification != HHS_EXACT_RNA_STATE_RETRIEVAL_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (memcmp(plan->current_dependency_frontier_sha256,
               retrieval->identity.dependency_frontier_sha256,
               HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES) != 0 ||
        memcmp(plan->admitted_dependency_frontier_sha256,
               retrieval->identity.dependency_frontier_sha256,
               HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES) != 0 ||
        memcmp(plan->predecessor_hash72,
               retrieval->identity.predecessor_hash72,
               HHS_EXACT_HASH72_STRLEN) != 0 ||
        memcmp(plan->predecessor_state_hash216,
               retrieval->identity.predecessor_state_hash216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return hhs_exact_pass219_rna_admission_candidate_from_retrieval(
        witness, retrieval, candidate_frame, out_candidate);
}
