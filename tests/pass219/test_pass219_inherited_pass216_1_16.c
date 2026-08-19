#include "hhs_pass219_inherited_pass216_1_16.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void copy_text(char *target, size_t size, const char *value) {
    size_t length = strlen(value);
    assert(length + 1U == size);
    memcpy(target, value, size);
}

static HHSExactPass216AlignmentWitnessV1 witness(void) {
    static const uint32_t tokens[HHS_EXACT_PASS216_SELECTED_TOKEN_COUNT] = {
        450U, 6575U, 471U, 528U, 2827U, 322U, 278U
    };
    HHSExactPass216AlignmentWitnessV1 value;
    size_t index;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = hhs_exact_pass219_inherited_pass216_version();
    value.contract_layer_complete = 1U;
    value.parent_alignment_complete = 1U;
    value.runtime_optimization_implementation_claimed = 0U;
    value.runtime_optimization_required_before_pass217 = 0U;
    value.global_strict_mode_default = 0U;
    value.unchanged_identity_requires_reexecution = 0U;
    value.unchanged_identity_requires_identity_verification = 1U;
    value.changed_transition_requires_dependency_scoped_validation = 1U;
    value.full_system_reproof_required_by_default = 0U;
    value.deterministic_truth_gate_closed_by_default = 1U;
    value.pass219_must_inherit_pass215_pass216_pass217 = 1U;
    value.floating_point_canonical_authority = 0U;
    value.lossy_authoritative_compression_allowed = 0U;
    value.selected_token_count = HHS_EXACT_PASS216_SELECTED_TOKEN_COUNT;
    for (index = 0U; index < HHS_EXACT_PASS216_SELECTED_TOKEN_COUNT; ++index)
        value.selected_token_ids[index] = tokens[index];
    copy_text(value.pass215_final_head, sizeof(value.pass215_final_head),
              "b85ea7c340976a20a78f9c7d8d89a688a1b4f8fc");
    copy_text(value.pass215_final_tree, sizeof(value.pass215_final_tree),
              "17127e80a3f4852aeaedd1b807971fb4b4fba229");
    copy_text(value.pass215_main_merge, sizeof(value.pass215_main_merge),
              "cc7a0d67d7d9e4bd1e800f62d5ef577cb4ab1086");
    copy_text(value.pass215_artifact_sha256, sizeof(value.pass215_artifact_sha256),
              "9e71ff3f48cd4da24c34854f8eadfa57f26d7c6ef5bddd1026c89e2ace63bf55");
    copy_text(value.pass216_published_head, sizeof(value.pass216_published_head),
              "0ad2759a4379376244589aa3ee241e51d779df26");
    copy_text(value.pass216_published_tree, sizeof(value.pass216_published_tree),
              "b9ff48b17f1e3c8272cd8c5c7b4381df69d4c7e9");
    copy_text(value.pass216_merge_commit, sizeof(value.pass216_merge_commit),
              "f10e453c5d7c7467cf5e57f6452958491fe763ad");
    copy_text(value.contract_git_blob, sizeof(value.contract_git_blob),
              "9e04e4aca8b127e009c0343ceb5e78092de40c43");
    copy_text(value.addendum_git_blob, sizeof(value.addendum_git_blob),
              "3e4121afe2f5750283f5ef350c0afa416eb2addd");
    return value;
}

int main(void) {
    HHSExactPass216AlignmentWitnessV1 input = witness();
    HHSExactPass219InheritedPass216BindingV1 output;
    HHSExactStatus status;

    memset(&output, 0, sizeof(output));
    status = hhs_exact_pass219_bind_pass216_alignment(&input, &output);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(output.pass_number == 216U);
    assert(output.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(output.contract_alignment_bound == 1U);
    assert(output.pass215_terminal_reference_bound == 1U);
    assert(output.truth_gate_closed_by_default == 1U);
    assert(output.dependency_scoped_validation_bound == 1U);
    assert(output.unchanged_authority_reuse_bound == 1U);
    assert(output.global_strict_mode_default == 0U);
    assert(output.runtime_optimization_implementation_claimed == 0U);
    assert(output.runtime_optimization_roadmap_complete == 0U);
    assert(output.cxx_mutation_authority == 0U);
    assert(output.vm81_mutation_authority == 0U);
    assert(output.floating_point_canonical_authority == 0U);
    assert(output.lossy_authoritative_compression_allowed == 0U);

    input = witness();
    input.runtime_optimization_implementation_claimed = 1U;
    assert(hhs_exact_pass219_bind_pass216_alignment(&input, &output) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness();
    input.global_strict_mode_default = 1U;
    assert(hhs_exact_pass219_bind_pass216_alignment(&input, &output) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness();
    input.unchanged_identity_requires_reexecution = 1U;
    assert(hhs_exact_pass219_bind_pass216_alignment(&input, &output) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness();
    input.full_system_reproof_required_by_default = 1U;
    assert(hhs_exact_pass219_bind_pass216_alignment(&input, &output) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness();
    input.floating_point_canonical_authority = 1U;
    assert(hhs_exact_pass219_bind_pass216_alignment(&input, &output) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness();
    input.lossy_authoritative_compression_allowed = 1U;
    assert(hhs_exact_pass219_bind_pass216_alignment(&input, &output) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness();
    input.selected_token_ids[3] += 1U;
    assert(hhs_exact_pass219_bind_pass216_alignment(&input, &output) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);
    input = witness();
    input.contract_git_blob[0] = '0';
    assert(hhs_exact_pass219_bind_pass216_alignment(&input, &output) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    puts("PASS219_INHERITED_PASS216_1_16_C_OK");
    return 0;
}
