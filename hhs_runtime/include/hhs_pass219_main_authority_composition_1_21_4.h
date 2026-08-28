#ifndef HHS_PASS219_MAIN_AUTHORITY_COMPOSITION_1_21_4_H
#define HHS_PASS219_MAIN_AUTHORITY_COMPOSITION_1_21_4_H

#include "hhs_pass219_pass159_vm81_proof_bridge_1_21_2.h"
#include "hhs_pass219_exact_vm81_candidate_adapter_1_21_3.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_MAIN_AUTHORITY_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_MAIN_AUTHORITY_VERSION_MINOR 21U
#define HHS_EXACT_PASS219_MAIN_AUTHORITY_VERSION_PATCH 4U
#define HHS_EXACT_PASS219_MAIN_AUTHORITY_HASH216_LEN 216U
#define HHS_EXACT_PASS219_MAIN_AUTHORITY_HASH216_STRLEN 217U

typedef enum HHSExactPass219MainAuthorityDecisionV1 {
    HHS_EXACT_PASS219_MAIN_AUTHORITY_INVALID = 0,
    HHS_EXACT_PASS219_MAIN_AUTHORITY_VMIR_EFFECT_BINDING_REQUIRED = 1,
    HHS_EXACT_PASS219_MAIN_AUTHORITY_CANONICAL_PROVEN = 2
} HHSExactPass219MainAuthorityDecisionV1;

typedef struct HHSExactPass219MainAuthorityCompositionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t decision;

    HHSExactPass219Pass159ProofV1 pass159;
    HHSExactPass219VM81ProgramV1 candidate_program;
    HHSExactPass219VM81ExecutionV1 candidate_execution;
    HHSExactPass219VM81ReplayV1 candidate_replay;

    char composition_hash216[HHS_EXACT_PASS219_MAIN_AUTHORITY_HASH216_STRLEN];

    uint8_t native_source_identity_equal;
    uint8_t pass159_source_pipeline_verified;
    uint8_t pass159_vmir_identity_present;
    uint8_t candidate_program_source_bound;
    uint8_t candidate_completion_only;
    uint8_t candidate_exact_kernel_execution_verified;
    uint8_t candidate_exact_replay_verified;
    uint8_t pass159_vmir_effect_binding_observed;
    uint8_t whole_expression_semantics_resolved;
    uint8_t canonical_monolithic_proof;
    uint8_t requires_pass169_authority;
    uint8_t floating_point_authority;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t reserved0[2];
} HHSExactPass219MainAuthorityCompositionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_main_authority_version(void);

/*
 * Compose the inherited Pass159 source/AST/constraint-graph/HIR/VMIR identity
 * pipeline with the I121.3 exact VM81 candidate execution and replay surface.
 *
 * This API deliberately does NOT infer that Pass159 VMIR emitted the I121.3
 * candidate-completion instructions. Until that effect correspondence is
 * independently implemented and replay-proven, successful composition returns
 * HHS_EXACT_PASS219_MAIN_AUTHORITY_VMIR_EFFECT_BINDING_REQUIRED and preserves
 * canonical_monolithic_proof == 0.
 *
 * The candidate executes on an isolated exact frame and this composition owns
 * no canonical VM81 mutation or Hash72 commit authority.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_compose_main_authority(
    const HHSExactVM81Frame *candidate_frame,
    HHSExactPass219MainAuthorityCompositionV1 *out_composition
);

#ifdef __cplusplus
}
#endif

#endif
