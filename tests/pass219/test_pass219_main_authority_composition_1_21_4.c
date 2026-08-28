#include "hhs_pass219_main_authority_composition_1_21_4.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

static HHSExactVM81Frame build_candidate(uint64_t salt) {
    HHSExactVM81Frame frame;
    uint32_t i;
    memset(&frame, 0, sizeof(frame));
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        frame.words[i] = UINT64_C(0x0102030405060708) ^
                         ((uint64_t)(i + 1U) * UINT64_C(0x9E3779B97F4A7C15));
    }
    frame.words[40] ^= salt;
    return frame;
}

static int hash216_valid(
    const char value[HHS_EXACT_PASS219_MAIN_AUTHORITY_HASH216_STRLEN]
) {
    size_t i;
    if (value == NULL || value[HHS_EXACT_PASS219_MAIN_AUTHORITY_HASH216_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_MAIN_AUTHORITY_HASH216_LEN; ++i) {
        if (value[i] == '\0' || strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static int assert_main_aligned_candidate(
    const HHSExactPass219MainAuthorityCompositionV1 *composition
) {
    if (composition == NULL)
        return 0;
    if (composition->struct_size != sizeof(*composition) ||
        composition->version != hhs_exact_pass219_main_authority_version() ||
        composition->decision !=
            HHS_EXACT_PASS219_MAIN_AUTHORITY_VMIR_EFFECT_BINDING_REQUIRED)
        return 0;

    if (composition->native_source_identity_equal != 1U ||
        composition->pass159_source_pipeline_verified != 1U ||
        composition->pass159_vmir_identity_present != 1U ||
        composition->candidate_program_source_bound != 1U ||
        composition->candidate_completion_only != 1U ||
        composition->candidate_exact_kernel_execution_verified != 1U ||
        composition->candidate_exact_replay_verified != 1U)
        return 0;

    if (composition->pass159.pass159_vmir_effectful != 0U ||
        composition->pass159.candidate_binding_supported != 0U ||
        composition->pass159_vmir_effect_binding_observed != 0U ||
        composition->whole_expression_semantics_resolved != 0U ||
        composition->canonical_monolithic_proof != 0U ||
        composition->requires_pass169_authority != 1U)
        return 0;

    if (composition->candidate_program.source_structure_thread_count !=
            HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS ||
        composition->candidate_program.derived_thread_count !=
            HHS_EXACT_PASS219_VM81_CANDIDATE_COMPLETION_THREADS ||
        composition->candidate_program.source_semantics_complete != 0U ||
        composition->candidate_execution.source_semantics_complete != 0U ||
        composition->candidate_execution.canonical_monolithic_proof != 0U)
        return 0;

    if (composition->floating_point_authority != 0U ||
        composition->vm81_mutation_authority != 0U ||
        composition->hash72_commit_authority != 0U ||
        composition->candidate_execution.floating_point_authority != 0U ||
        composition->candidate_execution.vm81_mutation_authority != 0U ||
        composition->candidate_execution.hash72_commit_authority != 0U)
        return 0;

    return hash216_valid(composition->composition_hash216);
}

int main(void) {
    HHSExactVM81Frame candidate = build_candidate(UINT64_C(0));
    HHSExactVM81Frame changed = build_candidate(UINT64_C(1));
    HHSExactPass219MainAuthorityCompositionV1 first;
    HHSExactPass219MainAuthorityCompositionV1 second;
    HHSExactPass219MainAuthorityCompositionV1 changed_result;
    HHSExactStatus status;

    if (hhs_exact_pass219_main_authority_version() !=
        ((1U << 16U) | (21U << 8U) | 4U))
        return 1;

    memset(&first, 0, sizeof(first));
    status = hhs_exact_pass219_compose_main_authority(&candidate, &first);
    if (status != HHS_EXACT_STATUS_OK || !assert_main_aligned_candidate(&first))
        return 2;

    memset(&second, 0, sizeof(second));
    status = hhs_exact_pass219_compose_main_authority(&candidate, &second);
    if (status != HHS_EXACT_STATUS_OK || !assert_main_aligned_candidate(&second))
        return 3;

    if (memcmp(first.composition_hash216,
               second.composition_hash216,
               HHS_EXACT_PASS219_MAIN_AUTHORITY_HASH216_STRLEN) != 0 ||
        memcmp(&first.candidate_execution.after_frame,
               &second.candidate_execution.after_frame,
               sizeof(first.candidate_execution.after_frame)) != 0 ||
        first.candidate_replay.replay_verified != 1U ||
        second.candidate_replay.replay_verified != 1U)
        return 4;

    memset(&changed_result, 0, sizeof(changed_result));
    status = hhs_exact_pass219_compose_main_authority(&changed, &changed_result);
    if (status != HHS_EXACT_STATUS_OK ||
        !assert_main_aligned_candidate(&changed_result))
        return 5;

    if (memcmp(first.composition_hash216,
               changed_result.composition_hash216,
               HHS_EXACT_PASS219_MAIN_AUTHORITY_HASH216_STRLEN) == 0)
        return 6;

    if (hhs_exact_pass219_compose_main_authority(NULL, &first) !=
            HHS_EXACT_STATUS_INVALID_ARGUMENT ||
        hhs_exact_pass219_compose_main_authority(&candidate, NULL) !=
            HHS_EXACT_STATUS_INVALID_ARGUMENT)
        return 7;

    puts("PASS219_MAIN_AUTHORITY_COMPOSITION_1_21_4_OK_VMIR_EFFECT_BINDING_REQUIRED");
    return 0;
}
