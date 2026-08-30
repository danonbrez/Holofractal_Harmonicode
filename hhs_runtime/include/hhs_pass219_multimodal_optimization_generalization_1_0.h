#ifndef HHS_PASS219_MULTIMODAL_OPTIMIZATION_GENERALIZATION_1_0_H
#define HHS_PASS219_MULTIMODAL_OPTIMIZATION_GENERALIZATION_1_0_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_MOG_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_MOG_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_MOG_VERSION_PATCH 0U

typedef enum HHSExactPass219OptimizationClassification {
    HHS_EXACT_PASS219_OPT_NOT_APPLICABLE = 0,
    HHS_EXACT_PASS219_OPT_VALIDATION_REQUIRED = 1,
    HHS_EXACT_PASS219_OPT_GENERALIZE_REQUIRED = 2,
    HHS_EXACT_PASS219_OPT_LOCAL_EXCEPTION_ALLOWED = 3
} HHSExactPass219OptimizationClassification;

typedef enum HHSExactPass219OptimizationExceptionReason {
    HHS_EXACT_PASS219_OPT_EXCEPTION_NONE = 0,
    HHS_EXACT_PASS219_OPT_EXCEPTION_UNSAFE = 1,
    HHS_EXACT_PASS219_OPT_EXCEPTION_NO_MEANINGFUL_BENEFIT = 2,
    HHS_EXACT_PASS219_OPT_EXCEPTION_CONTEXT_SPECIFIC = 3,
    HHS_EXACT_PASS219_OPT_EXCEPTION_METADATA_INCOMPATIBLE = 4,
    HHS_EXACT_PASS219_OPT_EXCEPTION_OBJECT_INCOMPATIBLE = 5,
    HHS_EXACT_PASS219_OPT_EXCEPTION_INTERFACE_ONLY = 6,
    HHS_EXACT_PASS219_OPT_EXCEPTION_INGRESS_ONLY = 7,
    HHS_EXACT_PASS219_OPT_EXCEPTION_EGRESS_ONLY = 8,
    HHS_EXACT_PASS219_OPT_EXCEPTION_EXPLICIT_ONE_OFF = 9
} HHSExactPass219OptimizationExceptionReason;

typedef struct HHSExactPass219OptimizationTargetEvidenceV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t descriptor_schema_match;
    uint32_t object_semantics_compatible;
    uint32_t runtime_authority_match;
    uint32_t exactness_domain_match;
    uint32_t validation_executed;
    uint32_t safety_verified;
    uint32_t benefit_verified;
    uint32_t explicit_local_exception;
    uint32_t exception_reason;
    uint32_t exception_evidence_present;
} HHSExactPass219OptimizationTargetEvidenceV1;

typedef struct HHSExactPass219OptimizationTargetDecisionV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t classification;
    uint32_t compatible;
    uint32_t validation_required;
    uint32_t generalization_required;
    uint32_t locality_allowed;
    uint32_t exception_reason;
} HHSExactPass219OptimizationTargetDecisionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_multimodal_optimization_generalization_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_classify_optimization_target(
    const HHSExactPass219OptimizationTargetEvidenceV1 *evidence,
    HHSExactPass219OptimizationTargetDecisionV1 *out_decision
);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_multimodal_optimization_generalization_validate(void);

#ifdef __cplusplus
}
#endif
#endif
