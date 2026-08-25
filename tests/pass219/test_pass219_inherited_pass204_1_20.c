#include "hhs_pass219_inherited_pass204_1_20.h"

#include <assert.h>
#include <string.h>

static HHSExactPass204OpenCloudWitnessV1 witness(void) {
    HHSExactPass204OpenCloudWitnessV1 w;
    memset(&w, 0, sizeof(w));
    w.struct_size = (uint32_t)sizeof(w);
    w.version = hhs_exact_pass219_inherited_pass204_version();
    w.production_verified = 1U;
    w.declaration_count = 2939U;
    w.hydrated_count = 2939U;
    w.callable_count = 2939U;
    w.binding_gap_count = 0U;
    w.public_route_count = 470U;
    w.openapi_path_count = 441U;
    w.valid_outcome_count = 3U;
    w.all_declarations_executable = 1U;
    w.remote_users_automatically_sandboxed = 1U;
    w.ephemeral_compute = 1U;
    w.core_native_completed = 1U;
    w.project_native_accepted = 1U;
    w.pass203_inheritance_verified = 1U;
    w.pass205_successor_preserved = 1U;
    w.implementation_pull_request = 147U;
    w.final_validation_workflow_run = 30810922316ULL;
    w.final_validation_artifact_id = 8854791111ULL;
    strcpy(w.base_commit, "fe5cb897ce5ca97a0c6c7439f26743dcefb83d4f");
    strcpy(w.validated_head, "6b26fbf6f4b767d4eb5f2a790c552b03fd39d352");
    strcpy(w.merge_commit, "deb34287ee155d9538005bbbfd6519794d999ac9");
    strcpy(w.validation_receipt_blob, "2b2a3baa87ea41577b4b4397da03b1b790c5cfae");
    strcpy(w.status_hash72, "LH0bm1Oh2BoGuenUhhwB/KIc!cUG/3XON6wm+Y)pcyuZXv8x0Y2LKQyubd8g4JD)FAtnxz)0");
    strcpy(w.snapshot_root, "JCR<sW/pI9rz*w5svIUaOIs/1(Rkfo050NYBfXRSDhY+i/maOouphah7vgrK(UuIXOv)v-hm");
    strcpy(w.core_native_receipt_hash72, "KLW)NAj5T9kF6JT6ZA0kok!uVFLe!*gAYYK(><uwvpf52hlwgCXoTKkSuZHNG8Iy364Tw3VY");
    strcpy(w.project_native_receipt_hash72, "Np78ojOERbOo2pB0+Bvp47*KhGqdS1EtpcSX(Kuex(Uuf<!s2wn!<wtxqNWCYQg)lFpKlJRi");
    return w;
}

int main(void) {
    HHSExactPass204OpenCloudWitnessV1 w = witness();
    HHSExactPass219InheritedPass204BindingV1 b;
    assert(hhs_exact_pass219_bind_pass204_open_cloud_mainframe(&w, &b) == HHS_EXACT_STATUS_OK);
    assert(b.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED);
    assert(b.pass_number == 204U);
    assert(b.universal_declarations_bound == 1U);
    assert(b.zero_binding_gaps_bound == 1U);
    assert(b.fixed_sandbox_policy_bound == 1U);
    assert(b.capability_free_recall_bound == 1U);
    assert(b.immutable_history_boundary_bound == 1U);
    assert(b.canonical_core_abi_bound == 1U);
    assert(b.project_native_durable_job_bound == 1U);
    assert(b.inherited_pass204_persistence_bound == 1U);
    assert(b.pass203_inheritance_bound == 1U);
    assert(b.pass205_successor_bound == 1U);
    assert(b.pass219_new_canonical_mutation_authority == 0U);
    assert(b.pass219_new_persistence_authority == 0U);
    assert(b.pass219_new_hash72_clock == 0U);
    assert(b.cxx_mutation_authority == 0U);
    assert(b.vm81_mutation_authority == 0U);

    w = witness();
    w.binding_gap_count = 1U;
    assert(hhs_exact_pass219_bind_pass204_open_cloud_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.persistent_capability_grants = 1U;
    assert(hhs_exact_pass219_bind_pass204_open_cloud_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.session_recall_restores_capabilities = 1U;
    assert(hhs_exact_pass219_bind_pass204_open_cloud_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.host_fault_can_rewrite_admitted_hash_history = 1U;
    assert(hhs_exact_pass219_bind_pass204_open_cloud_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.valid_call_http_error = 1U;
    assert(hhs_exact_pass219_bind_pass204_open_cloud_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.pass205_successor_preserved = 0U;
    assert(hhs_exact_pass219_bind_pass204_open_cloud_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.validation_receipt_blob[0] = '0';
    assert(hhs_exact_pass219_bind_pass204_open_cloud_mainframe(&w, &b) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    w = witness();
    w.version = 0U;
    assert(hhs_exact_pass219_bind_pass204_open_cloud_mainframe(&w, &b) == HHS_EXACT_STATUS_VERSION_MISMATCH);
    return 0;
}
