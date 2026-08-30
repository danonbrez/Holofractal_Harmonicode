#include "../include/hhs_pass219_multimodal_optimization_generalization_1_0.h"

#include <string.h>

static uint32_t hhs_pass219_mog_version_word(void) {
    return (HHS_EXACT_PASS219_MOG_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_MOG_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_MOG_VERSION_PATCH;
}

uint32_t hhs_exact_pass219_multimodal_optimization_generalization_version(void) {
    return hhs_pass219_mog_version_word();
}

static int hhs_pass219_mog_reason_is_bounded(uint32_t reason) {
    return reason >= HHS_EXACT_PASS219_OPT_EXCEPTION_UNSAFE &&
           reason <= HHS_EXACT_PASS219_OPT_EXCEPTION_EXPLICIT_ONE_OFF;
}

HHSExactStatus hhs_exact_pass219_classify_optimization_target(
    const HHSExactPass219OptimizationTargetEvidenceV1 *evidence,
    HHSExactPass219OptimizationTargetDecisionV1 *out_decision
) {
    uint32_t compatible;

    if (evidence == NULL || out_decision == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    if (evidence->struct_size != sizeof(*evidence) ||
        evidence->version != hhs_pass219_mog_version_word()) {
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    }

    compatible =
        evidence->descriptor_schema_match == 1U &&
        evidence->object_semantics_compatible == 1U &&
        evidence->runtime_authority_match == 1U &&
        evidence->exactness_domain_match == 1U;

    memset(out_decision, 0, sizeof(*out_decision));
    out_decision->struct_size = (uint32_t)sizeof(*out_decision);
    out_decision->version = hhs_pass219_mog_version_word();
    out_decision->compatible = compatible;

    if (!compatible) {
        out_decision->classification = HHS_EXACT_PASS219_OPT_NOT_APPLICABLE;
        return HHS_EXACT_STATUS_OK;
    }

    if (evidence->explicit_local_exception == 1U) {
        if (!hhs_pass219_mog_reason_is_bounded(evidence->exception_reason) ||
            evidence->exception_evidence_present != 1U) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        if (evidence->exception_reason == HHS_EXACT_PASS219_OPT_EXCEPTION_UNSAFE &&
            (evidence->validation_executed != 1U || evidence->safety_verified != 0U)) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        if (evidence->exception_reason == HHS_EXACT_PASS219_OPT_EXCEPTION_NO_MEANINGFUL_BENEFIT &&
            (evidence->validation_executed != 1U ||
             evidence->safety_verified != 1U ||
             evidence->benefit_verified != 0U)) {
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        out_decision->classification = HHS_EXACT_PASS219_OPT_LOCAL_EXCEPTION_ALLOWED;
        out_decision->locality_allowed = 1U;
        out_decision->exception_reason = evidence->exception_reason;
        return HHS_EXACT_STATUS_OK;
    }

    if (evidence->validation_executed != 1U) {
        out_decision->classification = HHS_EXACT_PASS219_OPT_VALIDATION_REQUIRED;
        out_decision->validation_required = 1U;
        return HHS_EXACT_STATUS_OK;
    }

    if (evidence->safety_verified == 1U && evidence->benefit_verified == 1U) {
        out_decision->classification = HHS_EXACT_PASS219_OPT_GENERALIZE_REQUIRED;
        out_decision->generalization_required = 1U;
        return HHS_EXACT_STATUS_OK;
    }

    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_multimodal_optimization_generalization_validate(void) {
    HHSExactPass219OptimizationTargetEvidenceV1 evidence;
    HHSExactPass219OptimizationTargetDecisionV1 decision;

    memset(&evidence, 0, sizeof(evidence));
    evidence.struct_size = (uint32_t)sizeof(evidence);
    evidence.version = hhs_pass219_mog_version_word();
    evidence.descriptor_schema_match = 1U;
    evidence.object_semantics_compatible = 1U;
    evidence.runtime_authority_match = 1U;
    evidence.exactness_domain_match = 1U;

    if (hhs_exact_pass219_classify_optimization_target(&evidence, &decision) !=
            HHS_EXACT_STATUS_OK ||
        decision.classification != HHS_EXACT_PASS219_OPT_VALIDATION_REQUIRED ||
        decision.validation_required != 1U) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    evidence.validation_executed = 1U;
    evidence.safety_verified = 1U;
    evidence.benefit_verified = 1U;
    if (hhs_exact_pass219_classify_optimization_target(&evidence, &decision) !=
            HHS_EXACT_STATUS_OK ||
        decision.classification != HHS_EXACT_PASS219_OPT_GENERALIZE_REQUIRED ||
        decision.generalization_required != 1U) {
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    return HHS_EXACT_STATUS_OK;
}
