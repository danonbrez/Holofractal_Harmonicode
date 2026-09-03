#ifndef HHS_PASS219_INHERITED_PASS176_1_50_H
#define HHS_PASS219_INHERITED_PASS176_1_50_H

#include "hhs_pass219_inherited_pass177_1_49.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS176_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS176_VERSION_MINOR 50U
#define HHS_EXACT_PASS219_INHERITED_PASS176_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS176_NUMBER 176U
#define HHS_EXACT_PASS176_I150_SHA256_LEN 64U
#define HHS_EXACT_PASS176_I150_SHA256_STRLEN 65U

typedef struct HHSExactPass176TerminalWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t terminal_pass176_completion;
    uint32_t all_verifier_checks_green;
    uint32_t runtime_os_public_root_preserved;
    uint32_t pass176_additive_route_preserved;
    uint32_t browser_evidence_green;
    uint32_t frontend_non_authority_verified;
    uint32_t singleton_vm81_admission_preserved;
    uint32_t hash72_commit_streams;
    uint32_t pass177_successor_preserved;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_commit_authority;
    uint32_t hash216_mutation_authority;
    char terminal_receipt_sha256[HHS_EXACT_PASS176_I150_SHA256_STRLEN];
    char artifact_sha256[HHS_EXACT_PASS176_I150_SHA256_STRLEN];
} HHSExactPass176TerminalWitnessV1;

typedef struct HHSExactPass219InheritedPass176BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t terminal_completion_claimed;
    uint32_t browser_evidence_bound;
    uint32_t runtime_os_public_root_preserved;
    uint32_t additive_pass176_route_preserved;
    uint32_t no_new_authority_bound;
    uint32_t singleton_vm81_admission_preserved;
    uint32_t hash72_commit_streams;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_commit_authority;
    uint32_t hash216_mutation_authority;
    char terminal_receipt_sha256[HHS_EXACT_PASS176_I150_SHA256_STRLEN];
    char artifact_sha256[HHS_EXACT_PASS176_I150_SHA256_STRLEN];
} HHSExactPass219InheritedPass176BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass176_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass176_terminal_ide(
    const HHSExactPass176TerminalWitnessV1 *witness,
    HHSExactPass219InheritedPass176BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif
#endif
