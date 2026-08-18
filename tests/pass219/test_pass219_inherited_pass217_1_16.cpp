#include "hhs_pass219_inherited_pass217_1_16.hpp"

#include <cassert>
#include <cstring>
#include <iostream>

static void copy_text(char *target, std::size_t size, const char *value) {
    const std::size_t length = std::strlen(value);
    assert(length + 1U == size);
    std::memcpy(target, value, size);
}

static HHSExactPass217CumulativeClosureWitnessV1 witness() {
    HHSExactPass217CumulativeClosureWitnessV1 value{};
    value.struct_size = static_cast<std::uint32_t>(sizeof(value));
    value.version = hhs_exact_pass219_inherited_pass217_version();
    value.required_authority_count = 25U;
    value.published_route_count = 3U;
    value.pass042_api_route_count = 24U;
    value.bypass_omission_count = 25U;
    value.hash72_symbol_count = 72U;
    value.hash72_matrix_positions = 5184U;
    value.wrapped_direction_count = 4U;
    value.cumulative_closure_admitted = 1U;
    value.global_surface_publication_complete = 1U;
    value.required_authority_bypass_matrix_complete = 1U;
    value.authority_profile_coverage_equal = 1U;
    value.incremental_tokenization_active_path_proven = 1U;
    value.structural_closure_hardening_complete = 1U;
    value.universal_utilization_reachability_complete = 1U;
    value.i4_hash72_manifold_validated = 1U;
    value.i4_immutable_nucleus_validated = 1U;
    std::memcpy(value.closure_root_hash72, HHS_EXACT_HASH72_ALPHABET, HHS_EXACT_HASH72_STRLEN);
    copy_text(value.i4_candidate_sha256, sizeof(value.i4_candidate_sha256),
              "97379c7ae7cdaebd8031a3a3fb58559c967b361b360c7db34ec096acabfc8fe8");
    copy_text(value.i4_address_map_sha256, sizeof(value.i4_address_map_sha256),
              "2f8d8a23114b87f2dbe91f3d302ef089b750f9d91f533d744a4524e907717f5f");
    copy_text(value.i4_hash72_matrix_root_sha256, sizeof(value.i4_hash72_matrix_root_sha256),
              "6c0b2e9e354e8d7eb17a746d01c157b19aa95b58296884126cdf5bef7998e286");
    copy_text(value.i4_hash72_manifold_root_sha256, sizeof(value.i4_hash72_manifold_root_sha256),
              "c757bae150d9ab94485c680ec3143e715b674d35f445a72c6fb4ea2def6f7884");
    copy_text(value.i4_nucleus_identity_root_sha256, sizeof(value.i4_nucleus_identity_root_sha256),
              "da7b33fa1a419e00ce81eeeeb5f1c435acd6ae7b95d355e3a1749a6a238e3164");
    copy_text(value.i4_nucleus_support_root_sha256, sizeof(value.i4_nucleus_support_root_sha256),
              "ac46211412784990e08e5cf0b80df5db381aad612a7ccd8aa816815a105b0294");
    copy_text(value.i4_record_root_sha256, sizeof(value.i4_record_root_sha256),
              "5c996cda648db2074a144ab8b9b0834ef442ee8bc2b2c7ed91885bc38aa6d03f");
    copy_text(value.checkpoint15_git_sha, sizeof(value.checkpoint15_git_sha),
              "be71da59c9b8b7c7e055c03da703ca301849cfff");
    copy_text(value.integration_git_sha, sizeof(value.integration_git_sha),
              "b0656a92ab29507f81eae760e070f74e49db83f4");
    return value;
}

int main() {
    auto value = witness();
    hhs::rna::InheritedPass217Closure binding(value);
    assert(binding.status() == HHS_EXACT_STATUS_OK);
    assert(binding.wired());
    assert(binding.all_required_authorities_nonbypassable());
    assert(!binding.genesis_rom_promotion_claimed());
    assert(binding.record().pass_number == 217U);
    assert(binding.record().cxx_mutation_authority == 0U);
    assert(binding.record().vm81_mutation_authority == 0U);
    std::cout << "PASS219_INHERITED_PASS217_1_16_CPP_OK\n";
    return 0;
}
