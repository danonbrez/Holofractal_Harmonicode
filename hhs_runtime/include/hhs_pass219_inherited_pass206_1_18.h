#ifndef HHS_PASS219_INHERITED_PASS206_1_18_H
#define HHS_PASS219_INHERITED_PASS206_1_18_H

#include "hhs_pass219_inherited_pass207_1_17.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS206_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS206_VERSION_MINOR 18U
#define HHS_EXACT_PASS219_INHERITED_PASS206_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS206_NUMBER 206U
#define HHS_EXACT_PASS206_FROZEN_CORE_COUNT 10U
#define HHS_EXACT_PASS206_APPROVED_SUCCESSOR_COUNT 1U
#define HHS_EXACT_PASS206_CANONICAL_MUTATION_AUTHORITY_COUNT 1U
#define HHS_EXACT_PASS206_CANONICAL_HASH72_STREAM_COUNT 1U
#define HHS_EXACT_PASS206_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS206_GIT_SHA_STRLEN 41U
#define HHS_EXACT_PASS206_SHA256_LEN 64U
#define HHS_EXACT_PASS206_SHA256_STRLEN 65U

typedef struct HHSExactPass206CumulativeEnforcementWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t enforcement_admitted;
    uint32_t frozen_core_count;
    uint32_t approved_successor_count;
    uint32_t canonical_mutation_authority_count;
    uint32_t canonical_hash72_commit_stream_count;
    uint32_t development_implementation_complete;
    uint32_t development_final_replay_complete;
    uint32_t development_completion_receipt_emitted;
    uint32_t ready_for_pass219_inherited_membrane;
    uint32_t canonical_main_verified;
    uint32_t canonical_main_promotion_authorized;
    uint32_t canonical_completion_claimed;
    uint32_t pass207_successor_preserved;
    uint32_t pass206_new_mutation_authority;
    uint32_t pass206_new_persistence_authority;
    uint32_t pass206_new_hash72_clock;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint64_t dependency_validation_run;
    uint64_t dependency_validation_exact_job;
    uint64_t dependency_validation_synthetic_job;
    uint64_t final_replay_pass206_run;
    uint64_t final_replay_pass206_exact_job;
    uint64_t final_replay_pass206_synthetic_job;
    uint64_t final_replay_cumulative_run;
    uint64_t final_replay_cumulative_exact_job;
    uint64_t final_replay_cumulative_synthetic_job;
    uint64_t completion_validation_run;
    uint64_t completion_validation_exact_job;
    uint64_t completion_validation_synthetic_job;
    char grounding_baseline[HHS_EXACT_PASS206_GIT_SHA_STRLEN];
    char sealed_predecessor[HHS_EXACT_PASS206_GIT_SHA_STRLEN];
    char freeze_checkpoint[HHS_EXACT_PASS206_GIT_SHA_STRLEN];
    char development_completion_head[HHS_EXACT_PASS206_GIT_SHA_STRLEN];
    char approved_repair_merge[HHS_EXACT_PASS206_GIT_SHA_STRLEN];
    char freeze_manifest_sha256[HHS_EXACT_PASS206_SHA256_STRLEN];
    char approved_repair_lineage_sha256[HHS_EXACT_PASS206_SHA256_STRLEN];
    char pre_receipt_matrix_sha256[HHS_EXACT_PASS206_SHA256_STRLEN];
    char completion_receipt_sha256[HHS_EXACT_PASS206_SHA256_STRLEN];
    char post_receipt_matrix_sha256[HHS_EXACT_PASS206_SHA256_STRLEN];
} HHSExactPass206CumulativeEnforcementWitnessV1;

typedef struct HHSExactPass219InheritedPass206BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t frozen_core_count;
    uint32_t approved_successor_count;
    uint32_t single_vm81_authority_bound;
    uint32_t single_hash72_stream_bound;
    uint32_t enforcement_admitted_bound;
    uint32_t development_completion_bound;
    uint32_t canonical_main_pending_bound;
    uint32_t pass207_successor_bound;
    uint32_t no_new_mutation_authority_bound;
    uint32_t no_new_persistence_authority_bound;
    uint32_t no_new_hash72_clock_bound;
    uint32_t pass219_new_canonical_mutation_authority;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    char development_completion_head[HHS_EXACT_PASS206_GIT_SHA_STRLEN];
    char completion_receipt_sha256[HHS_EXACT_PASS206_SHA256_STRLEN];
} HHSExactPass219InheritedPass206BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass206_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass206_cumulative_enforcement(
    const HHSExactPass206CumulativeEnforcementWitnessV1 *witness,
    HHSExactPass219InheritedPass206BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
