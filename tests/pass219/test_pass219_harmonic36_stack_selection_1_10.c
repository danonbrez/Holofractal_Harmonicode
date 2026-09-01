#include "hhs_runtime_exact_abi.h"

#include <assert.h>
#include <stdint.h>
#include <string.h>

static HHSExactPass219OptimizationTargetEvidenceV1 base_target(void) {
    HHSExactPass219OptimizationTargetEvidenceV1 evidence;
    memset(&evidence, 0, sizeof(evidence));
    evidence.struct_size = (uint32_t)sizeof(evidence);
    evidence.version =
        hhs_exact_pass219_multimodal_optimization_generalization_version();
    evidence.descriptor_schema_match = 1U;
    evidence.object_semantics_compatible = 1U;
    evidence.runtime_authority_match = 1U;
    evidence.exactness_domain_match = 1U;
    return evidence;
}

int main(void) {
    HHSExactPass219H36StackCandidateEvidenceV1 h36;
    HHSExactPass219H36StackCandidateEvidenceV1 linux;
    HHSExactPass219H36StackCandidateEvidenceV1 bad;
    HHSExactPass219H36StackSelectionV1 selection;
    HHSExactPass219OptimizationTargetEvidenceV1 target = base_target();
    HHSExactPass219OptimizationTargetDecisionV1 decision;
    const uint64_t workload36 = UINT64_C(012345670123);
    const uint64_t result64 = UINT64_C(0xA55A123456789ABC);

    assert(hhs_exact_pass219_h36_stack_candidate_prepare(
        1U,
        HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10,
        workload36,
        result64,
        UINT64_C(1000),
        9U,
        32U,
        4096U,
        14U,
        1U,
        &h36
    ) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_h36_stack_candidate_prepare(
        2U,
        HHS_EXACT_PASS219_H36_STACK_CANDIDATE_LINUX_X86_64,
        workload36,
        result64,
        UINT64_C(2000),
        9U,
        32U,
        2048U,
        20U,
        1U,
        &linux
    ) == HHS_EXACT_STATUS_OK);
    assert(strlen(h36.vector_key216) ==
           HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    assert(strlen(linux.vector_key216) ==
           HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    assert(strcmp(h36.vector_key216, linux.vector_key216) != 0);
    assert(h36.hash216_lineage_claim == 0U);
    assert(linux.hash216_lineage_claim == 0U);

    assert(hhs_exact_pass219_h36_stack_select(
        &h36, &linux, &selection) == HHS_EXACT_STATUS_OK);
    assert(selection.selected_candidate_id == 1U);
    assert(selection.selected_stack_kind ==
           HHS_EXACT_PASS219_H36_STACK_CANDIDATE_H36_KA10);
    assert(selection.speedup_x1000 == UINT64_C(2000));
    assert(selection.exact_equality_before_timing == 1U);
    assert(selection.vector_store_metadata_only == 1U);
    assert(selection.canonical_mutation_authority == 0U);
    assert(selection.canonical_hash72_authority == 0U);
    assert(selection.canonical_hash216_authority == 0U);
    assert(selection.canonical_persistence_authority == 0U);

    assert(hhs_exact_pass219_h36_stack_generalization_decision(
        &selection, &target, &decision) == HHS_EXACT_STATUS_OK);
    assert(decision.classification ==
           HHS_EXACT_PASS219_OPT_VALIDATION_REQUIRED);

    target.validation_executed = 1U;
    target.safety_verified = 1U;
    target.benefit_verified = 1U;
    assert(hhs_exact_pass219_h36_stack_generalization_decision(
        &selection, &target, &decision) == HHS_EXACT_STATUS_OK);
    assert(decision.classification ==
           HHS_EXACT_PASS219_OPT_GENERALIZE_REQUIRED);
    assert(decision.generalization_required == 1U);

    bad = linux;
    bad.semantic_result_signature64 ^= UINT64_C(1);
    assert(hhs_exact_pass219_h36_stack_select(
        &h36, &bad, &selection) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);

    bad = linux;
    bad.exact_result_equal = 0U;
    assert(hhs_exact_pass219_h36_stack_select(
        &h36, &bad, &selection) ==
        HHS_EXACT_STATUS_INVARIANT_FAILURE);

    return 0;
}
