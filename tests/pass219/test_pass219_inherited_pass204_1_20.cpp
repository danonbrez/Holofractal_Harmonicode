#include "hhs_pass219_inherited_pass204_1_20.hpp"

#include <cassert>
#include <cstring>

static HHSExactPass204OpenCloudWitnessV1 witness() {
    HHSExactPass204OpenCloudWitnessV1 w{};
    w.struct_size = static_cast<uint32_t>(sizeof(w));
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
    std::strcpy(w.base_commit, "fe5cb897ce5ca97a0c6c7439f26743dcefb83d4f");
    std::strcpy(w.validated_head, "6b26fbf6f4b767d4eb5f2a790c552b03fd39d352");
    std::strcpy(w.merge_commit, "deb34287ee155d9538005bbbfd6519794d999ac9");
    std::strcpy(w.validation_receipt_blob, "2b2a3baa87ea41577b4b4397da03b1b790c5cfae");
    std::strcpy(w.status_hash72, "LH0bm1Oh2BoGuenUhhwB/KIc!cUG/3XON6wm+Y)pcyuZXv8x0Y2LKQyubd8g4JD)FAtnxz)0");
    std::strcpy(w.snapshot_root, "JCR<sW/pI9rz*w5svIUaOIs/1(Rkfo050NYBfXRSDhY+i/maOouphah7vgrK(UuIXOv)v-hm");
    std::strcpy(w.core_native_receipt_hash72, "KLW)NAj5T9kF6JT6ZA0kok!uVFLe!*gAYYK(><uwvpf52hlwgCXoTKkSuZHNG8Iy364Tw3VY");
    std::strcpy(w.project_native_receipt_hash72, "Np78ojOERbOo2pB0+Bvp47*KhGqdS1EtpcSX(Kuex(Uuf<!s2wn!<wtxqNWCYQg)lFpKlJRi");
    return w;
}

int main() {
    auto w = witness();
    hhs::rna::InheritedPass204OpenCloudMainframe bound(w);
    assert(bound.status() == HHS_EXACT_STATUS_OK);
    assert(bound.wired());
    assert(bound.record().pass_number == 204U);
    assert(bound.record().inherited_pass204_persistence_bound == 1U);
    assert(bound.record().pass219_new_persistence_authority == 0U);

    w = witness();
    w.direct_host_kernel_access = 1U;
    hhs::rna::InheritedPass204OpenCloudMainframe rejected(w);
    assert(rejected.status() == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(!rejected.wired());
    return 0;
}
