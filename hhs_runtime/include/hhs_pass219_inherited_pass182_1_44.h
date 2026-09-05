#ifndef HHS_PASS219_INHERITED_PASS182_1_44_H
#define HHS_PASS219_INHERITED_PASS182_1_44_H

#include "hhs_pass219_inherited_pass183_1_43.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_INHERITED_PASS182_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_INHERITED_PASS182_VERSION_MINOR 44U
#define HHS_EXACT_PASS219_INHERITED_PASS182_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_INHERITED_PASS182_NUMBER 182U
#define HHS_EXACT_PASS182_I144_GIT_SHA_LEN 40U
#define HHS_EXACT_PASS182_I144_GIT_SHA_STRLEN 41U

typedef struct HHSExactPass182UniversalHydrationWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t normative_contract_preserved;
    uint32_t repository_runtime_bound;
    uint32_t read_only_tree_bound;
    uint32_t universal_hydration_ir_bound;
    uint32_t repository_logic_graph_bound;
    uint32_t secret_safe_traversal_bound;
    uint32_t incremental_dependency_scope_bound;
    uint32_t sandbox_dynamic_trace_bound;
    uint32_t portable_package_bound;
    uint32_t cold_start_replay_bound;
    uint32_t singleton_vm81_bound;
    uint32_t inherited_hash72_evidence_bound;
    uint32_t hash216_archival_only_bound;
    uint32_t pass183_successor_preserved;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_authority;
    uint32_t hash216_mutation_authority;
    uint32_t floating_point_canonical_authority;
    char frozen_i143_commit[HHS_EXACT_PASS182_I144_GIT_SHA_STRLEN];
    char i143_validation_receipt_blob[HHS_EXACT_PASS182_I144_GIT_SHA_STRLEN];
} HHSExactPass182UniversalHydrationWitnessV1;

typedef struct HHSExactPass219InheritedPass182BindingV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t pass_number;
    uint32_t classification;
    uint32_t read_only_tree_bound;
    uint32_t universal_hydration_ir_bound;
    uint32_t repository_logic_graph_bound;
    uint32_t secret_safe_traversal_bound;
    uint32_t incremental_dependency_scope_bound;
    uint32_t sandbox_dynamic_trace_bound;
    uint32_t portable_package_bound;
    uint32_t cold_start_replay_bound;
    uint32_t singleton_vm81_bound;
    uint32_t inherited_hash72_evidence_bound;
    uint32_t hash216_archival_only_bound;
    uint32_t no_new_authority_bound;
    uint32_t independent_vm81_authority;
    uint32_t independent_hash72_authority;
    uint32_t hash216_mutation_authority;
    uint32_t floating_point_canonical_authority;
    char frozen_i143_commit[HHS_EXACT_PASS182_I144_GIT_SHA_STRLEN];
} HHSExactPass219InheritedPass182BindingV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_inherited_pass182_version(void);
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_bind_pass182_universal_hydration(
    const HHSExactPass182UniversalHydrationWitnessV1 *witness,
    HHSExactPass219InheritedPass182BindingV1 *out_binding
);

#ifdef __cplusplus
}
#endif
#endif
