#ifndef HHS_PASS219_INHERITED_PASS218_1_16_H
#define HHS_PASS219_INHERITED_PASS218_1_16_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS218_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS218_VERSION_MINOR 16U
#define HHS_EXACT_PASS219_INHERITED_PASS218_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS218_NUMBER 218U
#define HHS_EXACT_PASS219_HASH216_STRLEN 217U
#define HHS_EXACT_PASS219_SHA256_BYTES 32U

typedef enum HHSExactPass219InheritedPassClassification {
    HHS_EXACT_PASS219_INHERITED_PASS_UNCLASSIFIED = 0,
    HHS_EXACT_PASS219_INHERITED_PASS_WIRED = 1,
    HHS_EXACT_PASS219_INHERITED_PASS_PRESENT_BUT_BYPASSED = 2,
    HHS_EXACT_PASS219_INHERITED_PASS_MISSING_MEMBRANE_EXPOSURE = 3,
    HHS_EXACT_PASS219_INHERITED_PASS_INTEGRATION_DEFECT = 4
} HHSExactPass219InheritedPassClassification;

typedef struct HHSExactPass218CompletionWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t manifest_source_count;
    uint32_t completed_source_count;
    uint32_t terminal_completion_verified;
    uint32_t authoritative_manifest_exhausted;
    uint32_t final_cursor_exhausted;
    uint32_t pass219_handoff_authority_minted;
    uint32_t vm81_authorization_invoked;
    char i47_receipt_hash72[HHS_EXACT_HASH72_STRLEN];
    char i33_advance_receipt_hash72[HHS_EXACT_HASH72_STRLEN];
    char i48_receipt_hash72[HHS_EXACT_HASH72_STRLEN];
    char completion_proof_hash72[HHS_EXACT_HASH72_STRLEN];
    char curriculum_identity_hash72[HHS_EXACT_HASH72_STRLEN];
    char final_closure_hash72[HHS_EXACT_HASH72_STRLEN];
    char i48_hash216[HHS_EXACT_PASS219_HASH216_STRLEN];
    uint8_t final_cursor_sha256[HHS_EXACT_PASS219_SHA256_BYTES];
    uint8_t i30_generation_sha256[HHS_EXACT_PASS219_SHA256_BYTES];
} HHSExactPass218CompletionWitnessV1;

typedef struct HHSExactPass219InheritedPass218BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t manifest_source_count;
    uint32_t completed_source_count;
    uint32_t completion_seal_bound;
    uint32_t receipt_semantics_preserved;
    uint32_t continuation_identity_exposed;
    uint32_t canonical_execution_reachable;
    uint32_t cxx_mutation_authority;
    uint32_t vm81_mutation_authority;
    uint32_t pass219_handoff_authority_minted;
    char i48_receipt_hash72[HHS_EXACT_HASH72_STRLEN];
    char completion_proof_hash72[HHS_EXACT_HASH72_STRLEN];
    char curriculum_identity_hash72[HHS_EXACT_HASH72_STRLEN];
    char final_closure_hash72[HHS_EXACT_HASH72_STRLEN];
    char i48_hash216[HHS_EXACT_PASS219_HASH216_STRLEN];
    uint8_t final_cursor_sha256[HHS_EXACT_PASS219_SHA256_BYTES];
    uint8_t i30_generation_sha256[HHS_EXACT_PASS219_SHA256_BYTES];
} HHSExactPass219InheritedPass218BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass218_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass218_completion(
    const HHSExactPass218CompletionWitnessV1 *witness,
    HHSExactPass219InheritedPass218BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif

#endif
