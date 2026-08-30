#include "hhs_pass219_multimodal_optimization_generalization_1_0.h"

#include <assert.h>
#include <string.h>

static HHSExactPass219OptimizationTargetEvidenceV1 base_evidence(void) {
    HHSExactPass219OptimizationTargetEvidenceV1 evidence;
    memset(&evidence, 0, sizeof(evidence));
    evidence.struct_size = (uint32_t)sizeof(evidence);
    evidence.version = hhs_exact_pass219_multimodal_optimization_generalization_version();
    evidence.descriptor_schema_match = 1U;
    evidence.object_semantics_compatible = 1U;
    evidence.runtime_authority_match = 1U;
    evidence.exactness_domain_match = 1U;
    return evidence;
}

int main(void) {
    HHSExactPass219OptimizationTargetEvidenceV1 evidence = base_evidence();
    HHSExactPass219OptimizationTargetDecisionV1 decision;

    assert(hhs_exact_pass219_multimodal_optimization_generalization_validate() ==
           HHS_EXACT_STATUS_OK);

    assert(hhs_exact_pass219_classify_optimization_target(&evidence, &decision) ==
           HHS_EXACT_STATUS_OK);
    assert(decision.classification == HHS_EXACT_PASS219_OPT_VALIDATION_REQUIRED);
    assert(decision.validation_required == 1U);
    assert(decision.compatible == 1U);

    evidence.validation_executed = 1U;
    evidence.safety_verified = 1U;
    evidence.benefit_verified = 1U;
    assert(hhs_exact_pass219_classify_optimization_target(&evidence, &decision) ==
           HHS_EXACT_STATUS_OK);
    assert(decision.classification == HHS_EXACT_PASS219_OPT_GENERALIZE_REQUIRED);
    assert(decision.generalization_required == 1U);

    evidence = base_evidence();
    evidence.validation_executed = 1U;
    evidence.explicit_local_exception = 1U;
    evidence.exception_reason = HHS_EXACT_PASS219_OPT_EXCEPTION_UNSAFE;
    evidence.exception_evidence_present = 1U;
    assert(hhs_exact_pass219_classify_optimization_target(&evidence, &decision) ==
           HHS_EXACT_STATUS_OK);
    assert(decision.classification == HHS_EXACT_PASS219_OPT_LOCAL_EXCEPTION_ALLOWED);
    assert(decision.locality_allowed == 1U);

    evidence = base_evidence();
    evidence.validation_executed = 1U;
    evidence.safety_verified = 1U;
    evidence.benefit_verified = 0U;
    assert(hhs_exact_pass219_classify_optimization_target(&evidence, &decision) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    evidence = base_evidence();
    evidence.descriptor_schema_match = 0U;
    assert(hhs_exact_pass219_classify_optimization_target(&evidence, &decision) ==
           HHS_EXACT_STATUS_OK);
    assert(decision.classification == HHS_EXACT_PASS219_OPT_NOT_APPLICABLE);
    assert(decision.compatible == 0U);
    return 0;
}
