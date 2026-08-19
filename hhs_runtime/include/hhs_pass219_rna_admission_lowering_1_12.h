#ifndef HHS_PASS219_RNA_ADMISSION_LOWERING_1_12_H
#define HHS_PASS219_RNA_ADMISSION_LOWERING_1_12_H

#include "hhs_pass219_rna_rule_grammar_1_11.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_RNA_LOWER_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_RNA_LOWER_VERSION_MINOR 12U
#define HHS_EXACT_PASS219_RNA_LOWER_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES 32U

typedef struct HHSExactPass219RNAAdmissionCandidateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t strand_id;
    uint32_t program_id;
    uint32_t executed_rule_count;
    uint32_t rollback_available;
    uint8_t dependency_frontier_sha256[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES];
    HHSExactPass219RNALineageV1 lineage;
    HHSExactVM81Frame predecessor_frame;
    HHSExactVM81Frame candidate_delta_xor;
    HHSExactVM81Frame rollback_frame;
} HHSExactPass219RNAAdmissionCandidateV1;

typedef struct HHSExactPass219RNAAdmissionLoweringV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t strand_id;
    uint32_t program_id;
    uint32_t executed_rule_count;
    uint32_t authority_invoked;
    uint32_t frame_committed;
    uint32_t rollback_verified;
    uint8_t dependency_frontier_sha256[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES];
    HHSExactPass219RNAAdmissionV1 admission;
} HHSExactPass219RNAAdmissionLoweringV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_rna_lower_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_admission_candidate_from_witness(
    const HHSExactPass219TranscriptionWitnessV1 *witness,
    const HHSExactVM81Frame *predecessor_frame,
    const HHSExactVM81Frame *candidate_frame,
    const uint8_t dependency_frontier_sha256[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES],
    HHSExactPass219RNAAdmissionCandidateV1 *out_candidate
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_candidate_reconstruct(
    const HHSExactPass219RNAAdmissionCandidateV1 *candidate,
    HHSExactVM81Frame *out_candidate_frame
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_candidate_rollback(
    const HHSExactPass219RNAAdmissionCandidateV1 *candidate,
    HHSExactVM81Frame *out_predecessor_frame
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_lower_to_vm81(
    const HHSExactPass219RNAAdmissionCandidateV1 *candidate,
    const HHSExactUQCELInputV1 *input,
    HHSExactPass219Hash216IndexResolverV1 index_resolver,
    void *index_context,
    HHSExactVM81Frame *out_committed_frame,
    HHSExactPass219RNAAdmissionLoweringV1 *out_lowering
);

#ifdef __cplusplus
}
#endif

#endif
