#ifndef HHS_PASS219_RNA_EXECUTION_COMPOSER_1_14_H
#define HHS_PASS219_RNA_EXECUTION_COMPOSER_1_14_H

#include "hhs_pass219_rna_state_retrieval_1_13.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_RNA_EXECUTION_COMPOSER_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_RNA_EXECUTION_COMPOSER_VERSION_MINOR 14U
#define HHS_EXACT_PASS219_RNA_EXECUTION_COMPOSER_VERSION_PATCH 0U

typedef enum HHSExactPass219RNAExecutionBypassReason {
    HHS_EXACT_PASS219_RNA_BYPASS_NONE = 0,
    HHS_EXACT_PASS219_RNA_BYPASS_FIRST_PRINCIPLES_EXPORT = 1,
    HHS_EXACT_PASS219_RNA_BYPASS_DEPENDENCY_CHANGED = 2,
    HHS_EXACT_PASS219_RNA_BYPASS_CORRUPTION_RECOVERY = 3,
    HHS_EXACT_PASS219_RNA_BYPASS_MISSING_OR_INVALID_REFERENCE_EVIDENCE = 4,
    HHS_EXACT_PASS219_RNA_BYPASS_REFERENCE_ORACLE = 5,
    HHS_EXACT_PASS219_RNA_BYPASS_ABLATION_OR_BENCHMARK_CONTROL = 6,
    HHS_EXACT_PASS219_RNA_BYPASS_UNAVAILABLE_AUTHENTICATED_PREDECESSOR = 7,
    HHS_EXACT_PASS219_RNA_BYPASS_EXPLICITLY_AUTHORIZED_AUDIT = 8
} HHSExactPass219RNAExecutionBypassReason;

typedef enum HHSExactPass219RNAExecutionRoute {
    HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_NONE = 0,
    HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_INDEXED_CONTINUATION = 1,
    HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_DEPENDENCY_SCOPED_RECOMPUTE = 2,
    HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_RECOVERY_RECOMPUTE = 3,
    HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_GENESIS_REPLAY = 4
} HHSExactPass219RNAExecutionRoute;

typedef struct HHSExactPass219RNAExecutionPlanV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t route;
    uint32_t requested_bypass_reason;
    uint32_t effective_bypass_reason;
    uint32_t indexed_lookup_observed;
    uint32_t inherited_indexed_capability_selected;
    uint32_t authenticated_predecessor_reused;
    uint32_t indexed_reuse_count;
    uint32_t genesis_replay_required;
    uint32_t genesis_replay_count;
    uint32_t dependency_scoped_recompute_required;
    uint32_t recovery_recompute_required;
    uint32_t unaffected_reuse_preserved;
    uint32_t current_dependency_frontier_verified;
    uint32_t index_invalidated;
    uint32_t retrieval_classification;
    uint64_t checkpoint_counter;
    uint8_t current_dependency_frontier_sha256[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES];
    uint8_t admitted_dependency_frontier_sha256[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES];
    char predecessor_hash72[HHS_EXACT_HASH72_STRLEN];
    char predecessor_state_hash216[HHS_EXACT_UQCEL_HASH216_STRLEN];
} HHSExactPass219RNAExecutionPlanV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_rna_execution_composer_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_execution_compose(
    const HHSExactPass219RNAStateRetrievalV1 *retrieval,
    const uint8_t current_dependency_frontier_sha256[HHS_EXACT_PASS219_DEPENDENCY_FRONTIER_SHA256_BYTES],
    uint32_t requested_bypass_reason,
    HHSExactPass219RNAExecutionPlanV1 *out_plan
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_execution_prepare_candidate(
    const HHSExactPass219RNAExecutionPlanV1 *plan,
    const HHSExactPass219RNAStateRetrievalV1 *retrieval,
    const HHSExactPass219TranscriptionWitnessV1 *witness,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactPass219RNAAdmissionCandidateV1 *out_candidate
);

#ifdef __cplusplus
}
#endif

#endif
