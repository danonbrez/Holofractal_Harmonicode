#include "../include/hhs_pass219_rna_state_retrieval_1_13.h"

#include <string.h>

static uint32_t hhs_exact_pass219_rna_retrieval_version_word(void) {
    return (HHS_EXACT_PASS219_RNA_RETRIEVAL_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_RNA_RETRIEVAL_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_RNA_RETRIEVAL_VERSION_PATCH;
}

static HHSExactStatus hhs_exact_pass219_rna_prior_identity_validate(
    const HHSExactPass219RNAPriorStateIdentityV1 *identity
) {
    if (identity == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (identity->struct_size < sizeof(*identity) ||
        identity->version != hhs_exact_pass219_rna_retrieval_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (identity->program_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] != '\0' ||
        identity->predecessor_state_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] != '\0' ||
        identity->predecessor_hash72[HHS_EXACT_HASH72_LEN] != '\0')
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (memchr(identity->program_hash216, '\0', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN) != NULL ||
        memchr(identity->predecessor_state_hash216, '\0', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN) != NULL ||
        memchr(identity->predecessor_hash72, '\0', HHS_EXACT_HASH72_LEN) != NULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static int hhs_exact_pass219_rna_prior_identity_equal(
    const HHSExactPass219RNAPriorStateIdentityV1 *left,
    const HHSExactPass219RNAPriorStateIdentityV1 *right
) {
    return left->checkpoint_counter == right->checkpoint_counter &&
           memcmp(left->program_hash216, right->program_hash216,
                  HHS_EXACT_UQCEL_HASH216_STRLEN) == 0 &&
           memcmp(left->predecessor_state_hash216, right->predecessor_state_hash216,
                  HHS_EXACT_UQCEL_HASH216_STRLEN) == 0 &&
           memcmp(left->predecessor_hash72, right->predecessor_hash72,
                  HHS_EXACT_HASH72_STRLEN) == 0 &&
           memcmp(left->predecessor_hash216_digest_sha256,
                  right->predecessor_hash216_digest_sha256,
                  HHS_EXACT_PASS219_RNA_RETRIEVAL_SHA256_BYTES) == 0 &&
           memcmp(left->retrieval_source_sha256, right->retrieval_source_sha256,
                  HHS_EXACT_PASS219_RNA_RETRIEVAL_SHA256_BYTES) == 0 &&
           memcmp(left->authenticated_index_sha256, right->authenticated_index_sha256,
                  HHS_EXACT_PASS219_RNA_RETRIEVAL_SHA256_BYTES) == 0 &&
           memcmp(left->dependency_frontier_sha256, right->dependency_frontier_sha256,
                  HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES) == 0;
}

uint32_t hhs_exact_pass219_rna_retrieval_version(void) {
    return hhs_exact_pass219_rna_retrieval_version_word();
}

HHSExactStatus hhs_exact_pass219_rna_reference_seal_from_replay(
    const HHSExactPass219RNAPriorStateIdentityV1 *identity,
    const HHSExactVM81Frame *reference_frame,
    const HHSExactVM81Frame *reference_replay_frame,
    HHSExactPass219RNAPriorStateReferenceSealV1 *out_seal
) {
    HHSExactStatus status;
    if (reference_frame == NULL || reference_replay_frame == NULL || out_seal == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_seal, 0, sizeof(*out_seal));
    status = hhs_exact_pass219_rna_prior_identity_validate(identity);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (memcmp(reference_frame, reference_replay_frame, sizeof(*reference_frame)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    out_seal->struct_size = (uint32_t)sizeof(*out_seal);
    out_seal->version = hhs_exact_pass219_rna_retrieval_version_word();
    out_seal->deterministic_replay_verified = 1U;
    memcpy(&out_seal->identity, identity, sizeof(*identity));
    memcpy(&out_seal->canonical_predecessor_frame, reference_frame, sizeof(*reference_frame));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_indexed_prior_state_init(
    const HHSExactPass219RNAPriorStateIdentityV1 *identity,
    const HHSExactVM81Frame *predecessor_frame,
    HHSExactPass219RNAIndexedPriorStateV1 *out_indexed
) {
    HHSExactStatus status;
    if (predecessor_frame == NULL || out_indexed == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_indexed, 0, sizeof(*out_indexed));
    status = hhs_exact_pass219_rna_prior_identity_validate(identity);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    out_indexed->struct_size = (uint32_t)sizeof(*out_indexed);
    out_indexed->version = hhs_exact_pass219_rna_retrieval_version_word();
    out_indexed->available = 1U;
    memcpy(&out_indexed->identity, identity, sizeof(*identity));
    memcpy(&out_indexed->predecessor_frame, predecessor_frame, sizeof(*predecessor_frame));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_state_retrieval_authenticate(
    const HHSExactPass219RNAIndexedPriorStateV1 *indexed,
    const HHSExactPass219RNAPriorStateReferenceSealV1 *reference_seal,
    HHSExactPass219RNAStateRetrievalV1 *out_retrieval
) {
    HHSExactStatus status;
    if (indexed == NULL || reference_seal == NULL || out_retrieval == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_retrieval, 0, sizeof(*out_retrieval));
    out_retrieval->struct_size = (uint32_t)sizeof(*out_retrieval);
    out_retrieval->version = hhs_exact_pass219_rna_retrieval_version_word();
    out_retrieval->classification = HHS_EXACT_RNA_STATE_RETRIEVAL_MISMATCH;
    out_retrieval->fallback_required = 1U;

    if (indexed->struct_size < sizeof(*indexed) ||
        indexed->version != hhs_exact_pass219_rna_retrieval_version_word() ||
        reference_seal->struct_size < sizeof(*reference_seal) ||
        reference_seal->version != hhs_exact_pass219_rna_retrieval_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (indexed->available > 1U || reference_seal->deterministic_replay_verified != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_exact_pass219_rna_prior_identity_validate(&reference_seal->identity);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_rna_prior_identity_validate(&indexed->identity);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    if (indexed->available == 0U) {
        out_retrieval->classification = HHS_EXACT_RNA_STATE_RETRIEVAL_UNAVAILABLE;
        return HHS_EXACT_STATUS_OK;
    }

    if (!hhs_exact_pass219_rna_prior_identity_equal(&indexed->identity,
                                                     &reference_seal->identity) ||
        memcmp(&indexed->predecessor_frame,
               &reference_seal->canonical_predecessor_frame,
               sizeof(indexed->predecessor_frame)) != 0) {
        out_retrieval->classification = HHS_EXACT_RNA_STATE_RETRIEVAL_MISMATCH;
        out_retrieval->index_invalidated = 1U;
        return HHS_EXACT_STATUS_OK;
    }

    out_retrieval->classification = HHS_EXACT_RNA_STATE_RETRIEVAL_OK;
    out_retrieval->reference_authenticated = 1U;
    out_retrieval->fallback_required = 0U;
    out_retrieval->index_invalidated = 0U;
    memcpy(&out_retrieval->identity, &indexed->identity, sizeof(indexed->identity));
    memcpy(&out_retrieval->predecessor_frame, &indexed->predecessor_frame,
           sizeof(indexed->predecessor_frame));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_indexed_prior_state_invalidate(
    HHSExactPass219RNAIndexedPriorStateV1 *indexed
) {
    if (indexed == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (indexed->struct_size < sizeof(*indexed) ||
        indexed->version != hhs_exact_pass219_rna_retrieval_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    indexed->available = 0U;
    memset(&indexed->predecessor_frame, 0, sizeof(indexed->predecessor_frame));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_admission_candidate_from_retrieval(
    const HHSExactPass219TranscriptionWitnessV1 *witness,
    const HHSExactPass219RNAStateRetrievalV1 *retrieval,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactPass219RNAAdmissionCandidateV1 *out_candidate
) {
    HHSExactStatus status;
    if (witness == NULL || retrieval == NULL || candidate_frame == NULL || out_candidate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (retrieval->struct_size < sizeof(*retrieval) ||
        retrieval->version != hhs_exact_pass219_rna_retrieval_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (retrieval->classification != HHS_EXACT_RNA_STATE_RETRIEVAL_OK ||
        retrieval->reference_authenticated != 1U || retrieval->fallback_required != 0U ||
        retrieval->index_invalidated != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    status = hhs_exact_pass219_rna_prior_identity_validate(&retrieval->identity);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != hhs_exact_pass219_rna_rule_version())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (memcmp(witness->lineage.predecessor_hash72,
               retrieval->identity.predecessor_hash72,
               HHS_EXACT_HASH72_STRLEN) != 0 ||
        memcmp(witness->lineage.predecessor_hash216_identity,
               retrieval->identity.predecessor_state_hash216,
               HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return hhs_exact_pass219_rna_admission_candidate_from_witness(
        witness, &retrieval->predecessor_frame, candidate_frame,
        retrieval->identity.dependency_frontier_sha256, out_candidate);
}
