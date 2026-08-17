#include "../include/hhs_pass219_rna_admission_lowering_1_12.h"

#include <string.h>

static uint32_t hhs_exact_pass219_rna_lower_version_word(void) {
    return (HHS_EXACT_PASS219_RNA_LOWER_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_RNA_LOWER_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_RNA_LOWER_VERSION_PATCH;
}

static HHSExactStatus hhs_exact_pass219_rna_candidate_validate(
    const HHSExactPass219RNAAdmissionCandidateV1 *candidate
) {
    uint8_t cell81;
    int8_t lo_shu_group;
    uint8_t operation64;
    uint16_t g243;
    HHSExactStatus status;

    if (candidate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (candidate->struct_size < sizeof(*candidate) ||
        candidate->version != hhs_exact_pass219_rna_lower_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (candidate->rollback_available != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (candidate->lineage.struct_size < sizeof(candidate->lineage) ||
        candidate->lineage.version != hhs_exact_pass219_rna_rule_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (candidate->lineage.predecessor_hash72[HHS_EXACT_HASH72_LEN] != '\0' ||
        candidate->lineage.predecessor_hash216_identity[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] != '\0')
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (candidate->lineage.native_phase.ordered_source_preserved != 1U ||
        candidate->lineage.native_phase.left_basis >= HHS_EXACT_PHASE_BASIS_COUNT ||
        candidate->lineage.native_phase.right_basis >= HHS_EXACT_PHASE_BASIS_COUNT)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (memcmp(&candidate->rollback_frame, &candidate->predecessor_frame,
               sizeof(candidate->predecessor_frame)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_coordinate_to_pass189(
        &candidate->lineage.coordinate, &cell81, &lo_shu_group,
        &operation64, &g243);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    (void)cell81;
    (void)lo_shu_group;
    (void)g243;
    if (operation64 != (uint8_t)(candidate->lineage.native_phase.left_basis *
                                  HHS_EXACT_PHASE_BASIS_COUNT +
                                  candidate->lineage.native_phase.right_basis))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

uint32_t hhs_exact_pass219_rna_lower_version(void) {
    return hhs_exact_pass219_rna_lower_version_word();
}

HHSExactStatus hhs_exact_pass219_rna_admission_candidate_from_witness(
    const HHSExactPass219TranscriptionWitnessV1 *witness,
    const HHSExactVM81Frame *predecessor_frame,
    const HHSExactVM81Frame *candidate_frame,
    const uint8_t dependency_frontier_sha256[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES],
    HHSExactPass219RNAAdmissionCandidateV1 *out_candidate
) {
    size_t i;
    if (witness == NULL || predecessor_frame == NULL || candidate_frame == NULL ||
        dependency_frontier_sha256 == NULL || out_candidate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != hhs_exact_pass219_rna_rule_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->rollback_available != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_candidate, 0, sizeof(*out_candidate));
    out_candidate->struct_size = (uint32_t)sizeof(*out_candidate);
    out_candidate->version = hhs_exact_pass219_rna_lower_version_word();
    out_candidate->strand_id = witness->strand_id;
    out_candidate->program_id = witness->program_id;
    out_candidate->executed_rule_count = witness->executed_rule_count;
    out_candidate->rollback_available = witness->rollback_available;
    memcpy(out_candidate->dependency_frontier_sha256, dependency_frontier_sha256,
           HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES);
    memcpy(&out_candidate->lineage, &witness->lineage, sizeof(out_candidate->lineage));
    memcpy(&out_candidate->predecessor_frame, predecessor_frame, sizeof(*predecessor_frame));
    memcpy(&out_candidate->rollback_frame, predecessor_frame, sizeof(*predecessor_frame));
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        out_candidate->candidate_delta_xor.words[i] =
            predecessor_frame->words[i] ^ candidate_frame->words[i];

    return hhs_exact_pass219_rna_candidate_validate(out_candidate);
}

HHSExactStatus hhs_exact_pass219_rna_candidate_reconstruct(
    const HHSExactPass219RNAAdmissionCandidateV1 *candidate,
    HHSExactVM81Frame *out_candidate_frame
) {
    HHSExactStatus status;
    size_t i;
    if (out_candidate_frame == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_candidate_frame, 0, sizeof(*out_candidate_frame));
    status = hhs_exact_pass219_rna_candidate_validate(candidate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        out_candidate_frame->words[i] =
            candidate->predecessor_frame.words[i] ^ candidate->candidate_delta_xor.words[i];
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_candidate_rollback(
    const HHSExactPass219RNAAdmissionCandidateV1 *candidate,
    HHSExactVM81Frame *out_predecessor_frame
) {
    HHSExactVM81Frame staged_candidate;
    HHSExactStatus status;
    size_t i;
    if (out_predecessor_frame == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_predecessor_frame, 0, sizeof(*out_predecessor_frame));
    status = hhs_exact_pass219_rna_candidate_reconstruct(candidate, &staged_candidate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        out_predecessor_frame->words[i] =
            staged_candidate.words[i] ^ candidate->candidate_delta_xor.words[i];
    if (memcmp(out_predecessor_frame, &candidate->rollback_frame,
               sizeof(*out_predecessor_frame)) != 0) {
        memset(out_predecessor_frame, 0, sizeof(*out_predecessor_frame));
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_lower_to_vm81(
    const HHSExactPass219RNAAdmissionCandidateV1 *candidate,
    const HHSExactUQCELInputV1 *input,
    HHSExactPass219Hash216IndexResolverV1 index_resolver,
    void *index_context,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactPass219RNAAdmissionLoweringV1 *out_lowering
) {
    HHSExactVM81Frame staged_candidate;
    HHSExactVM81Frame staged_rollback;
    HHSExactVM81Frame staged_committed;
    HHSExactPass219RNAAdmissionV1 staged_admission;
    HHSExactStatus status;

    if (candidate == NULL || input == NULL || index_resolver == NULL ||
        out_committed_frame == NULL || out_lowering == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_committed_frame, 0, sizeof(*out_committed_frame));
    memset(out_lowering, 0, sizeof(*out_lowering));
    out_lowering->struct_size = (uint32_t)sizeof(*out_lowering);
    out_lowering->version = hhs_exact_pass219_rna_lower_version_word();

    status = hhs_exact_pass219_rna_candidate_validate(candidate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (memcmp(candidate->lineage.predecessor_hash72, input->previous_hash72,
               HHS_EXACT_HASH72_STRLEN) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (candidate->lineage.coordinate.cell81 != input->cell81 ||
        candidate->lineage.native_phase.left_basis != input->left_basis8 ||
        candidate->lineage.native_phase.right_basis != input->right_basis8)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_rna_candidate_reconstruct(candidate, &staged_candidate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_rna_candidate_rollback(candidate, &staged_rollback);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (memcmp(&staged_rollback, &candidate->predecessor_frame,
               sizeof(staged_rollback)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_lowering->strand_id = candidate->strand_id;
    out_lowering->program_id = candidate->program_id;
    out_lowering->executed_rule_count = candidate->executed_rule_count;
    out_lowering->authority_invoked = 1U;
    out_lowering->rollback_verified = 1U;
    memcpy(out_lowering->dependency_frontier_sha256,
           candidate->dependency_frontier_sha256,
           HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES);

    memset(&staged_committed, 0, sizeof(staged_committed));
    memset(&staged_admission, 0, sizeof(staged_admission));
    status = hhs_exact_pass219_rna_admit_composed(
        input, &staged_candidate,
        candidate->lineage.coordinate.lo_shu_group,
        candidate->lineage.coordinate.g243,
        index_resolver, index_context,
        &staged_committed, &staged_admission);
    memcpy(&out_lowering->admission, &staged_admission, sizeof(staged_admission));
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (memcmp(&staged_committed, &staged_candidate, sizeof(staged_committed)) != 0 ||
        memcmp(staged_admission.transition.previous_hash72,
               candidate->lineage.predecessor_hash72,
               HHS_EXACT_HASH72_STRLEN) != 0 ||
        staged_admission.native_phase.ordered_product.ordered_tag !=
            candidate->lineage.native_phase.ordered_product.ordered_tag ||
        staged_admission.coordinate.cell81 != candidate->lineage.coordinate.cell81 ||
        staged_admission.coordinate.operation64 != candidate->lineage.coordinate.operation64 ||
        staged_admission.coordinate.g243 != candidate->lineage.coordinate.g243) {
        memset(out_committed_frame, 0, sizeof(*out_committed_frame));
        out_lowering->frame_committed = 0U;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    memcpy(out_committed_frame, &staged_committed, sizeof(staged_committed));
    out_lowering->frame_committed = 1U;
    return HHS_EXACT_STATUS_OK;
}
