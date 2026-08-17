#ifndef HHS_PASS219_RNA_STATE_RETRIEVAL_1_13_H
#define HHS_PASS219_RNA_STATE_RETRIEVAL_1_13_H

#include "hhs_pass219_rna_admission_lowering_1_12.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_RNA_RETRIEVAL_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_RNA_RETRIEVAL_VERSION_MINOR 13U
#define HHS_EXACT_PASS219_RNA_RETRIEVAL_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_RNA_RETRIEVAL_SHA256_BYTES 32U

typedef enum HHSExactPass219RNAStateRetrievalClass {
    HHS_EXACT_RNA_STATE_RETRIEVAL_OK = 0,
    HHS_EXACT_RNA_STATE_RETRIEVAL_UNAVAILABLE = 1,
    HHS_EXACT_RNA_STATE_RETRIEVAL_MISMATCH = 2
} HHSExactPass219RNAStateRetrievalClass;

typedef struct HHSExactPass219RNAPriorStateIdentityV1 {
    uint32_t struct_size;
    uint32_t version;
    char program_hash216[HHS_EXACT_UQCEL_HASH216_STRLEN];
    char predecessor_state_hash216[HHS_EXACT_UQCEL_HASH216_STRLEN];
    char predecessor_hash72[HHS_EXACT_HASH72_STRLEN];
    uint8_t predecessor_hash216_digest_sha256[HHS_EXACT_PASS219_RNA_RETRIEVAL_SHA256_BYTES];
    uint8_t retrieval_source_sha256[HHS_EXACT_PASS219_RNA_RETRIEVAL_SHA256_BYTES];
    uint8_t authenticated_index_sha256[HHS_EXACT_PASS219_RNA_RETRIEVAL_SHA256_BYTES];
    uint64_t checkpoint_counter;
    uint8_t dependency_frontier_sha256[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES];
} HHSExactPass219RNAPriorStateIdentityV1;

typedef struct HHSExactPass219RNAPriorStateReferenceSealV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t deterministic_replay_verified;
    HHSExactPass219RNAPriorStateIdentityV1 identity;
    HHSExactVM81Frame canonical_predecessor_frame;
} HHSExactPass219RNAPriorStateReferenceSealV1;

typedef struct HHSExactPass219RNAIndexedPriorStateV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t available;
    HHSExactPass219RNAPriorStateIdentityV1 identity;
    HHSExactVM81Frame predecessor_frame;
} HHSExactPass219RNAIndexedPriorStateV1;

typedef struct HHSExactPass219RNAStateRetrievalV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t classification;
    uint32_t reference_authenticated;
    uint32_t fallback_required;
    uint32_t index_invalidated;
    HHSExactPass219RNAPriorStateIdentityV1 identity;
    HHSExactVM81Frame predecessor_frame;
} HHSExactPass219RNAStateRetrievalV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_rna_retrieval_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_reference_seal_from_replay(
    const HHSExactPass219RNAPriorStateIdentityV1 *identity,
    const HHSExactVM81Frame *reference_frame,
    const HHSExactVM81Frame *reference_replay_frame,
    HHSExactPass219RNAPriorStateReferenceSealV1 *out_seal
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_indexed_prior_state_init(
    const HHSExactPass219RNAPriorStateIdentityV1 *identity,
    const HHSExactVM81Frame *predecessor_frame,
    HHSExactPass219RNAIndexedPriorStateV1 *out_indexed
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_state_retrieval_authenticate(
    const HHSExactPass219RNAIndexedPriorStateV1 *indexed,
    const HHSExactPass219RNAPriorStateReferenceSealV1 *reference_seal,
    HHSExactPass219RNAStateRetrievalV1 *out_retrieval
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_indexed_prior_state_invalidate(
    HHSExactPass219RNAIndexedPriorStateV1 *indexed
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_admission_candidate_from_retrieval(
    const HHSExactPass219TranscriptionWitnessV1 *witness,
    const HHSExactPass219RNAStateRetrievalV1 *retrieval,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactPass219RNAAdmissionCandidateV1 *out_candidate
);

#ifdef __cplusplus
}
#endif

#endif
