#include "../include/hhs_pass219_inherited_pass204_1_20.h"

#include <stddef.h>
#include <string.h>

static const char P204_BASE_COMMIT[] = "fe5cb897ce5ca97a0c6c7439f26743dcefb83d4f";
static const char P204_VALIDATED_HEAD[] = "6b26fbf6f4b767d4eb5f2a790c552b03fd39d352";
static const char P204_MERGE_COMMIT[] = "deb34287ee155d9538005bbbfd6519794d999ac9";
static const char P204_VALIDATION_RECEIPT_BLOB[] = "2b2a3baa87ea41577b4b4397da03b1b790c5cfae";
static const char P204_STATUS_HASH72[] = "LH0bm1Oh2BoGuenUhhwB/KIc!cUG/3XON6wm+Y)pcyuZXv8x0Y2LKQyubd8g4JD)FAtnxz)0";
static const char P204_SNAPSHOT_ROOT[] = "JCR<sW/pI9rz*w5svIUaOIs/1(Rkfo050NYBfXRSDhY+i/maOouphah7vgrK(UuIXOv)v-hm";
static const char P204_CORE_NATIVE_RECEIPT[] = "KLW)NAj5T9kF6JT6ZA0kok!uVFLe!*gAYYK(><uwvpf52hlwgCXoTKkSuZHNG8Iy364Tw3VY";
static const char P204_PROJECT_NATIVE_RECEIPT[] = "Np78ojOERbOo2pB0+Bvp47*KhGqdS1EtpcSX(Kuex(Uuf<!s2wn!<wtxqNWCYQg)lFpKlJRi";

static uint32_t p204_version_word(void) {
    return (HHS_EXACT_PASS219_INHERITED_PASS204_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_INHERITED_PASS204_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_INHERITED_PASS204_VERSION_PATCH;
}

static int p204_text(const char *value, size_t size, const char *expected, size_t expected_len) {
    return value != NULL && expected != NULL && size == expected_len + 1U &&
           value[expected_len] == '\0' && memcmp(value, expected, expected_len) == 0;
}

static int p204_git(const char value[HHS_EXACT_PASS204_GIT_SHA_STRLEN], const char *expected) {
    return p204_text(value, HHS_EXACT_PASS204_GIT_SHA_STRLEN, expected, HHS_EXACT_PASS204_GIT_SHA_LEN);
}

static int p204_hash72(const char value[HHS_EXACT_PASS204_HASH72_STRLEN], const char *expected) {
    return p204_text(value, HHS_EXACT_PASS204_HASH72_STRLEN, expected, HHS_EXACT_PASS204_HASH72_LEN);
}

uint32_t hhs_exact_pass219_inherited_pass204_version(void) { return p204_version_word(); }

HHSExactStatus hhs_exact_pass219_bind_pass204_open_cloud_mainframe(
    const HHSExactPass204OpenCloudWitnessV1 *witness,
    HHSExactPass219InheritedPass204BindingV1 *out_binding
) {
    if (witness == NULL || out_binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) || witness->version != p204_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    if (witness->production_verified != 1U ||
        witness->declaration_count != HHS_EXACT_PASS204_DECLARATION_COUNT ||
        witness->hydrated_count != HHS_EXACT_PASS204_DECLARATION_COUNT ||
        witness->callable_count != HHS_EXACT_PASS204_DECLARATION_COUNT ||
        witness->binding_gap_count != HHS_EXACT_PASS204_BINDING_GAP_COUNT ||
        witness->public_route_count != HHS_EXACT_PASS204_PUBLIC_ROUTE_COUNT ||
        witness->openapi_path_count != HHS_EXACT_PASS204_OPENAPI_PATH_COUNT ||
        witness->valid_outcome_count != HHS_EXACT_PASS204_VALID_OUTCOME_COUNT ||
        witness->all_declarations_executable != 1U ||
        witness->valid_call_http_error != 0U ||
        witness->remote_users_automatically_sandboxed != 1U ||
        witness->ephemeral_compute != 1U ||
        witness->persistent_capability_grants != 0U ||
        witness->direct_host_kernel_access != 0U ||
        witness->caller_adjustable_internal_policy != 0U ||
        witness->session_recall_restores_capabilities != 0U ||
        witness->admitted_history_mutable != 0U ||
        witness->constraint_authority_mutable != 0U ||
        witness->host_fault_can_rewrite_admitted_hash_history != 0U ||
        witness->host_fault_can_mutate_constraint_contract != 0U ||
        witness->canonical_ctypes_raw_pointer_exposed != 0U ||
        witness->project_native_pointer_exposed != 0U ||
        witness->core_native_completed != 1U ||
        witness->project_native_accepted != 1U ||
        witness->pass203_inheritance_verified != 1U ||
        witness->pass205_successor_preserved != 1U ||
        witness->pass219_new_canonical_mutation_authority != 0U ||
        witness->pass219_new_persistence_authority != 0U ||
        witness->pass219_new_hash72_clock != 0U ||
        witness->cxx_mutation_authority != 0U ||
        witness->vm81_mutation_authority != 0U ||
        witness->implementation_pull_request != 147U ||
        witness->final_validation_workflow_run != 30810922316ULL ||
        witness->final_validation_artifact_id != 8854791111ULL)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (!p204_git(witness->base_commit, P204_BASE_COMMIT) ||
        !p204_git(witness->validated_head, P204_VALIDATED_HEAD) ||
        !p204_git(witness->merge_commit, P204_MERGE_COMMIT) ||
        !p204_git(witness->validation_receipt_blob, P204_VALIDATION_RECEIPT_BLOB) ||
        !p204_hash72(witness->status_hash72, P204_STATUS_HASH72) ||
        !p204_hash72(witness->snapshot_root, P204_SNAPSHOT_ROOT) ||
        !p204_hash72(witness->core_native_receipt_hash72, P204_CORE_NATIVE_RECEIPT) ||
        !p204_hash72(witness->project_native_receipt_hash72, P204_PROJECT_NATIVE_RECEIPT))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_binding, 0, sizeof(*out_binding));
    out_binding->struct_size = (uint32_t)sizeof(*out_binding);
    out_binding->version = p204_version_word();
    out_binding->pass_number = HHS_EXACT_PASS219_INHERITED_PASS204_NUMBER;
    out_binding->classification = HHS_EXACT_PASS219_INHERITED_PASS_WIRED;
    out_binding->universal_declarations_bound = 1U;
    out_binding->zero_binding_gaps_bound = 1U;
    out_binding->fixed_sandbox_policy_bound = 1U;
    out_binding->capability_free_recall_bound = 1U;
    out_binding->immutable_history_boundary_bound = 1U;
    out_binding->canonical_core_abi_bound = 1U;
    out_binding->project_native_durable_job_bound = 1U;
    out_binding->inherited_pass204_persistence_bound = 1U;
    out_binding->pass203_inheritance_bound = 1U;
    out_binding->pass205_successor_bound = 1U;
    out_binding->no_new_canonical_mutation_authority_bound = 1U;
    out_binding->no_new_persistence_authority_bound = 1U;
    out_binding->no_new_hash72_clock_bound = 1U;
    out_binding->pass219_new_canonical_mutation_authority = 0U;
    out_binding->pass219_new_persistence_authority = 0U;
    out_binding->pass219_new_hash72_clock = 0U;
    out_binding->cxx_mutation_authority = 0U;
    out_binding->vm81_mutation_authority = 0U;
    memcpy(out_binding->merge_commit, witness->merge_commit, HHS_EXACT_PASS204_GIT_SHA_STRLEN);
    memcpy(out_binding->validation_receipt_blob, witness->validation_receipt_blob, HHS_EXACT_PASS204_GIT_SHA_STRLEN);
    memcpy(out_binding->status_hash72, witness->status_hash72, HHS_EXACT_PASS204_HASH72_STRLEN);
    memcpy(out_binding->snapshot_root, witness->snapshot_root, HHS_EXACT_PASS204_HASH72_STRLEN);
    return HHS_EXACT_STATUS_OK;
}
