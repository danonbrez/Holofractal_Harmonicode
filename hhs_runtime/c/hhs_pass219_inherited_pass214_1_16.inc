#include "../include/hhs_pass219_inherited_pass214_1_16.h"

#include <stddef.h>
#include <string.h>

static const char HHS_EXACT_PASS214_VALIDATED_TERMINAL_HEAD[] =
    "fb167f0ae88346c7894d60b794eeba0e1967a971";
static const char HHS_EXACT_PASS214_MERGE_COMMIT[] =
    "1114a50c677f3f205d5858bc09b1249d3d365842";
static const char HHS_EXACT_PASS214_MAIN_CLOSURE_COMMIT[] =
    "063bcc1426b5bba106e139cb7dba1c540df090df";
static const char HHS_EXACT_PASS214_MAIN_CLOSURE_TREE[] =
    "9b21320cc72f3c77c79a9d76b083fe8b0c97f9d5";
static const char HHS_EXACT_PASS214_MAIN_CLOSURE_ARTIFACT_SHA256[] =
    "8b2dc496bb856cc5627f1c66c79ee878b6305a2e5bdc4ff0bec94b0ff1a615c6";
static const char HHS_EXACT_PASS214_REPOSITORY_SCAN_ROOT[] =
    "8d527e0a562e05b0bac6a180cce1601f5808f22e2c1c9e5455b12b024b3d3d6a";
static const char HHS_EXACT_PASS214_OPTIMIZATION_REGISTRY_ROOT[] =
    "32d73ff8e68fd8893fc347fb4aa97c4c8027b75dfd61bc3dab45aeae44f6a5dc";
static const char HHS_EXACT_PASS214_COMPATIBILITY_GRAPH_ROOT[] =
    "b229bddea971f76b386b615316a0926473a4f66b37de9e49ec661b85567a6439";
static const char HHS_EXACT_PASS214_WORKLOAD_CORPUS_ROOT[] =
    "c4f00ab874c2f1daaffd073ff6c0a85113314a4e6c70b5c30474ced43ece1f99";
static const char HHS_EXACT_PASS214_BENCHMARK_METHOD_ROOT[] =
    "b1973a3145e370f4a85503dac540a5b9a12f7050bd6ccdb14f11f6a7506c6b0f";
static const char HHS_EXACT_PASS214_COMPOUND_EVIDENCE_ROOT[] =
    "983a947ac2f625b8bdca689d6fc15b270f9ea7b8550c814484a158d96e624361";
static const char HHS_EXACT_PASS214_AUTHORITY_ROOT[] =
    "c1d7875acd45f02da75101f5953541b6e1ce8ea3bb2cac39645004ab2509aeb8";
static const char HHS_EXACT_PASS214_PASS215_PROFILE_ROOT[] =
    "a3079f0f0b94d9fb485970662455482d4dab86e01802ca5bfdef6af3fbb6d85e";
static const char HHS_EXACT_PASS214_PASS213_GATE_ROOT[] =
    "214106621723b579ffe4813c74d5df98a7e14387293b8ecc3e1edc81bf066092";
static const char HHS_EXACT_PASS214_COMPOUND_BENCHMARK_ROOT[] =
    "3193f1cf30306d193b3d4a19e0670e396f26943c148c29ef45d20ffad456e21b";
static const char HHS_EXACT_PASS214_TERMINAL_RECEIPT_HASH72[] =
    "!(KTNH1zFC/ikVVJ1qCp8OKfOX8IoP<O8-/Df(NcNLYbY<<i+ICL5g2luJlws)AOvyX9XvJD";
static const char HHS_EXACT_PASS214_SEMANTIC_REUSE_HEAD[] =
    "54295e674d6bae1868bdb66b5d2aff0edaaac1d4";
static const char HHS_EXACT_PASS214_SEMANTIC_REUSE_TREE[] =
    "9e28fcb36de76440e2ee5909c2b82c1bf5a4314d";
static const char HHS_EXACT_PASS214_SEMANTIC_REUSE_ARTIFACT_SHA256[] =
    "33a237ee8d76c598656b253f70ecf2a72a285a5e71d165414b6bf938b4f103f8";
static const char HHS_EXACT_PASS214_EXACT_VM81_KERNEL_GIT_BLOB[] =
    "81d9699b2d28d5d6a09ea4763653f3ba9eda9e15";
static const char HHS_EXACT_PASS214_VM81_REBIND_SCRIPT_COMMIT[] =
    "cf18b65bd1e3d7a3dce0081b97e1d4ff89b2c7d0";
static const char HHS_EXACT_PASS214_VM81_REBIND_TEST_COMMIT[] =
    "2b753167522c0829a4f7e23eb4378d824c82eafe";

static uint32_t hhs_exact_pass219_inherited_pass214_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS214_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS214_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS214_VERSION_PATCH;
}

static int hhs_exact_pass214_exact_text(
    const char *value,
    size_t value_size,
    const char *expected,
    size_t expected_length
) {
    if (value == NULL || expected == NULL || value_size != expected_length + 1U)
        return 0;
    if (value[expected_length] != '\0')
        return 0;
    return memcmp(value, expected, expected_length) == 0;
}

static int hhs_exact_pass214_exact_git_sha(
    const char value[HHS_EXACT_PASS214_GIT_SHA_STRLEN],
    const char expected[HHS_EXACT_PASS214_GIT_SHA_STRLEN]
) {
    return hhs_exact_pass214_exact_text(
        value,
        HHS_EXACT_PASS214_GIT_SHA_STRLEN,
        expected,
        HHS_EXACT_PASS214_GIT_SHA_LEN);
}

static int hhs_exact_pass214_exact_sha256(
    const char value[HHS_EXACT_PASS214_SHA256_HEX_STRLEN],
    const char expected[HHS_EXACT_PASS214_SHA256_HEX_STRLEN]
) {
    return hhs_exact_pass214_exact_text(
        value,
        HHS_EXACT_PASS214_SHA256_HEX_STRLEN,
        expected,
        HHS_EXACT_PASS214_SHA256_HEX_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass214_version(void) {
    return hhs_exact_pass219_inherited_pass214_version_word();
}

HHSExactStatus hhs_exact_pass219_bind_pass214_benchmark_authority(
    const HHSExactPass214BenchmarkAuthorityWitnessV1 *witness,
    HHSExactPass219InheritedPass214BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != hhs_exact_pass219_inherited_pass214_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->terminal_iteration != 8U ||
        witness->terminal_roots_minted != 1U ||
        witness->benchmark_authority_promoted != 1U ||
        witness->pass215_authorized != 1U ||
        witness->pass213_gates_preserved != 1U ||
        witness->runtime_mutation_authority_promoted != 0U ||
        witness->canonical_mutation_authorized != 0U ||
        witness->migration_active != 0U ||
        witness->pass213_live_admission_required_before_canonical_mutation != 1U ||
        witness->workload_families != 15U ||
        witness->workload_modes_per_family != 11U ||
        witness->mode_executions != 165U ||
        witness->mandatory_ablations != 26U ||
        witness->benchmark_stage_count != 10U ||
        witness->pass197_address_comparisons != 1658880U ||
        witness->pass212_full_hydration_bits != 50388480U ||
        witness->pass212_full_state_recoveries != 3U ||
        witness->cross_process_replays != 15U ||
        witness->semantic_reuse_execution_authority_changed != 0U ||
        witness->semantic_reuse_automatic_promotion != 0U ||
        witness->semantic_reuse_registry_entries != 306U ||
        witness->semantic_reuse_remaining_backlog != 1383U ||
        witness->exact_vm81_kernel_rebound != 1U ||
        witness->main_closure_run != 31195458960ULL ||
        witness->semantic_reuse_run != 31259979177ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!hhs_exact_pass214_exact_git_sha(witness->validated_terminal_head, HHS_EXACT_PASS214_VALIDATED_TERMINAL_HEAD) ||
        !hhs_exact_pass214_exact_git_sha(witness->merge_commit, HHS_EXACT_PASS214_MERGE_COMMIT) ||
        !hhs_exact_pass214_exact_git_sha(witness->main_closure_commit, HHS_EXACT_PASS214_MAIN_CLOSURE_COMMIT) ||
        !hhs_exact_pass214_exact_git_sha(witness->main_closure_tree, HHS_EXACT_PASS214_MAIN_CLOSURE_TREE) ||
        !hhs_exact_pass214_exact_sha256(witness->main_closure_artifact_sha256, HHS_EXACT_PASS214_MAIN_CLOSURE_ARTIFACT_SHA256) ||
        !hhs_exact_pass214_exact_sha256(witness->repository_scan_root_hash216, HHS_EXACT_PASS214_REPOSITORY_SCAN_ROOT) ||
        !hhs_exact_pass214_exact_sha256(witness->optimization_registry_root_hash216, HHS_EXACT_PASS214_OPTIMIZATION_REGISTRY_ROOT) ||
        !hhs_exact_pass214_exact_sha256(witness->compatibility_graph_root_hash216, HHS_EXACT_PASS214_COMPATIBILITY_GRAPH_ROOT) ||
        !hhs_exact_pass214_exact_sha256(witness->workload_corpus_root_hash216, HHS_EXACT_PASS214_WORKLOAD_CORPUS_ROOT) ||
        !hhs_exact_pass214_exact_sha256(witness->benchmark_method_root_hash216, HHS_EXACT_PASS214_BENCHMARK_METHOD_ROOT) ||
        !hhs_exact_pass214_exact_sha256(witness->compound_evidence_root_hash216, HHS_EXACT_PASS214_COMPOUND_EVIDENCE_ROOT) ||
        !hhs_exact_pass214_exact_sha256(witness->authority_root_hash216, HHS_EXACT_PASS214_AUTHORITY_ROOT) ||
        !hhs_exact_pass214_exact_sha256(witness->pass215_profile_root_hash216, HHS_EXACT_PASS214_PASS215_PROFILE_ROOT) ||
        !hhs_exact_pass214_exact_sha256(witness->pass213_gate_preservation_root_hash216, HHS_EXACT_PASS214_PASS213_GATE_ROOT) ||
        !hhs_exact_pass214_exact_sha256(witness->compound_benchmark_root_hash216, HHS_EXACT_PASS214_COMPOUND_BENCHMARK_ROOT) ||
        !hhs_exact_pass214_exact_text(witness->terminal_receipt_hash72,
                                      HHS_EXACT_PASS214_HASH72_STRLEN,
                                      HHS_EXACT_PASS214_TERMINAL_RECEIPT_HASH72,
                                      HHS_EXACT_HASH72_LEN) ||
        !hhs_exact_pass214_exact_git_sha(witness->semantic_reuse_head, HHS_EXACT_PASS214_SEMANTIC_REUSE_HEAD) ||
        !hhs_exact_pass214_exact_git_sha(witness->semantic_reuse_tree, HHS_EXACT_PASS214_SEMANTIC_REUSE_TREE) ||
        !hhs_exact_pass214_exact_sha256(witness->semantic_reuse_artifact_sha256, HHS_EXACT_PASS214_SEMANTIC_REUSE_ARTIFACT_SHA256) ||
        !hhs_exact_pass214_exact_git_sha(witness->exact_vm81_kernel_git_blob, HHS_EXACT_PASS214_EXACT_VM81_KERNEL_GIT_BLOB) ||
        !hhs_exact_pass214_exact_git_sha(witness->vm81_rebind_script_commit, HHS_EXACT_PASS214_VM81_REBIND_SCRIPT_COMMIT) ||
        !hhs_exact_pass214_exact_git_sha(witness->vm81_rebind_test_commit, HHS_EXACT_PASS214_VM81_REBIND_TEST_COMMIT))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = hhs_exact_pass219_inherited_pass214_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS214_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->terminal_benchmark_authority_bound = 1U;
    out_binding->eight_root_terminal_closure_bound = 1U;
    out_binding->pass215_profile_authorization_bound = 1U;
    out_binding->semantic_equivalence_reuse_bound = 1U;
    out_binding->exact_vm81_kernel_rebind_bound = 1U;
    out_binding->pass213_gates_preserved = 1U;
    out_binding->runtime_mutation_authority_promoted = 0U;
    out_binding->canonical_mutation_authorized = 0U;
    out_binding->migration_active = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    out_binding->workload_families = witness->workload_families;
    out_binding->mandatory_ablations = witness->mandatory_ablations;
    memcpy(out_binding->main_closure_commit, witness->main_closure_commit, HHS_EXACT_PASS214_GIT_SHA_STRLEN);
    memcpy(out_binding->authority_root_hash216, witness->authority_root_hash216, HHS_EXACT_PASS214_SHA256_HEX_STRLEN);
    memcpy(out_binding->pass215_profile_root_hash216, witness->pass215_profile_root_hash216, HHS_EXACT_PASS214_SHA256_HEX_STRLEN);
    memcpy(out_binding->pass213_gate_preservation_root_hash216, witness->pass213_gate_preservation_root_hash216, HHS_EXACT_PASS214_SHA256_HEX_STRLEN);
    memcpy(out_binding->terminal_receipt_hash72, witness->terminal_receipt_hash72, HHS_EXACT_PASS214_HASH72_STRLEN);
    memcpy(out_binding->semantic_reuse_head, witness->semantic_reuse_head, HHS_EXACT_PASS214_GIT_SHA_STRLEN);
    memcpy(out_binding->exact_vm81_kernel_git_blob, witness->exact_vm81_kernel_git_blob, HHS_EXACT_PASS214_GIT_SHA_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
