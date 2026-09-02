#include <assert.h>
#include <string.h>
#include "hhs_runtime_exact_abi.h"

static void fill(char out[HHS_EXACT_PASS182_I144_GIT_SHA_STRLEN], const char *value) {
    memcpy(out, value, HHS_EXACT_PASS182_I144_GIT_SHA_LEN);
    out[HHS_EXACT_PASS182_I144_GIT_SHA_LEN] = '\0';
}

int main(void) {
    HHSExactPass182UniversalHydrationWitnessV1 w;
    HHSExactPass219InheritedPass182BindingV1 b;
    memset(&w, 0, sizeof(w));
    w.struct_size = sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass182_version();
    w.normative_contract_preserved = 1U;
    w.repository_runtime_bound = 1U;
    w.read_only_tree_bound = 1U;
    w.universal_hydration_ir_bound = 1U;
    w.repository_logic_graph_bound = 1U;
    w.secret_safe_traversal_bound = 1U;
    w.incremental_dependency_scope_bound = 1U;
    w.sandbox_dynamic_trace_bound = 1U;
    w.portable_package_bound = 1U;
    w.cold_start_replay_bound = 1U;
    w.singleton_vm81_bound = 1U;
    w.inherited_hash72_evidence_bound = 1U;
    w.hash216_archival_only_bound = 1U;
    w.pass183_successor_preserved = 1U;
    fill(w.frozen_i143_commit, "f4ba13da3d4ac556d7fa511c667187d3c9e7ac52");
    fill(w.i143_validation_receipt_blob, "4619ea215173c55fe50e68197dfa87cb6ce58276");

    assert(hhs_exact_pass219_bind_pass182_universal_hydration(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.pass_number == 182U);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.read_only_tree_bound == 1U);
    assert(b.singleton_vm81_bound == 1U);
    assert(b.hash216_archival_only_bound == 1U);
    assert(b.no_new_authority_bound == 1U);
    assert(b.independent_vm81_authority == 0U);
    assert(b.independent_hash72_authority == 0U);
    assert(b.hash216_mutation_authority == 0U);
    assert(b.floating_point_canonical_authority == 0U);

    w.independent_hash72_authority = 1U;
    assert(hhs_exact_pass219_bind_pass182_universal_hydration(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    return 0;
}
