#include "../include/hhs_pass219_inherited_pass182_1_44.h"

#include <string.h>

static const char P182_I144_FROZEN_I143[] = "f4ba13da3d4ac556d7fa511c667187d3c9e7ac52";
static const char P182_I144_I143_RECEIPT_BLOB[] = "4619ea215173c55fe50e68197dfa87cb6ce58276";

static uint32_t p182_i144_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS182_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS182_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS182_VERSION_PATCH;
}

static int p182_i144_git(
    const char value[HHS_EXACT_PASS182_I144_GIT_SHA_STRLEN],
    const char *expected
) {
    return value != NULL && expected != NULL &&
           value[HHS_EXACT_PASS182_I144_GIT_SHA_LEN] == '\0' &&
           memcmp(value, expected, HHS_EXACT_PASS182_I144_GIT_SHA_LEN) == 0;
}

uint32_t hhs_exact_pass219_inherited_pass182_version(void) {
    return p182_i144_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass182_universal_hydration(
    const HHSExactPass182UniversalHydrationWitnessV1 *witness,
    HHSExactPass219InheritedPass182BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p182_i144_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->normative_contract_preserved != 1U ||
        witness->repository_runtime_bound != 1U ||
        witness->read_only_tree_bound != 1U ||
        witness->universal_hydration_ir_bound != 1U ||
        witness->repository_logic_graph_bound != 1U ||
        witness->secret_safe_traversal_bound != 1U ||
        witness->incremental_dependency_scope_bound != 1U ||
        witness->sandbox_dynamic_trace_bound != 1U ||
        witness->portable_package_bound != 1U ||
        witness->cold_start_replay_bound != 1U ||
        witness->singleton_vm81_bound != 1U ||
        witness->inherited_hash72_evidence_bound != 1U ||
        witness->hash216_archival_only_bound != 1U ||
        witness->pass183_successor_preserved != 1U ||
        witness->independent_vm81_authority != 0U ||
        witness->independent_hash72_authority != 0U ||
        witness->hash216_mutation_authority != 0U ||
        witness->floating_point_canonical_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p182_i144_git(witness->frozen_i143_commit, P182_I144_FROZEN_I143) ||
        !p182_i144_git(witness->i143_validation_receipt_blob, P182_I144_I143_RECEIPT_BLOB))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p182_i144_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS182_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->read_only_tree_bound = 1U;
    out_binding->universal_hydration_ir_bound = 1U;
    out_binding->repository_logic_graph_bound = 1U;
    out_binding->secret_safe_traversal_bound = 1U;
    out_binding->incremental_dependency_scope_bound = 1U;
    out_binding->sandbox_dynamic_trace_bound = 1U;
    out_binding->portable_package_bound = 1U;
    out_binding->cold_start_replay_bound = 1U;
    out_binding->singleton_vm81_bound = 1U;
    out_binding->inherited_hash72_evidence_bound = 1U;
    out_binding->hash216_archival_only_bound = 1U;
    out_binding->no_new_authority_bound = 1U;
    memcpy(out_binding->frozen_i143_commit, P182_I144_FROZEN_I143, HHS_EXACT_PASS182_I144_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
