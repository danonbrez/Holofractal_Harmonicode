#include "hhs_pass219_inherited_pass216_1_16.hpp"

#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>

static void copy_text(char *target, std::size_t size, const char *value) {
    const std::size_t length = std::strlen(value);
    assert(length + 1U == size);
    std::memcpy(target, value, size);
}

static HHSExactPass216AlignmentWitnessV1 witness() {
    static constexpr std::uint32_t tokens[HHS_EXACT_PASS216_SELECTED_TOKEN_COUNT] = {
        450U, 6575U, 471U, 528U, 2827U, 322U, 278U
    };
    HHSExactPass216AlignmentWitnessV1 value{};
    value.struct_size = static_cast<std::uint32_t>(sizeof(value));
    value.version = hhs_exact_pass219_inherited_pass216_version();
    value.contract_layer_complete = 1U;
    value.parent_alignment_complete = 1U;
    value.unchanged_identity_requires_identity_verification = 1U;
    value.changed_transition_requires_dependency_scoped_validation = 1U;
    value.deterministic_truth_gate_closed_by_default = 1U;
    value.pass219_must_inherit_pass215_pass216_pass217 = 1U;
    value.selected_token_count = HHS_EXACT_PASS216_SELECTED_TOKEN_COUNT;
    for (std::size_t index = 0U; index < HHS_EXACT_PASS216_SELECTED_TOKEN_COUNT; ++index)
        value.selected_token_ids[index] = tokens[index];
    copy_text(value.pass215_final_head, sizeof(value.pass215_final_head),
              "b85ea7c340976a20a78f9c7d8d89a688a1b4f8fc");
    copy_text(value.pass215_final_tree, sizeof(value.pass215_final_tree),
              "17127e80a3f4852aeaedd1b807971fb4b4fba229");
    copy_text(value.pass215_main_merge, sizeof(value.pass215_main_merge),
              "cc7a0d67d7d9e4bd1e800f62d5ef577cb4ab1086");
    copy_text(value.pass215_artifact_sha256, sizeof(value.pass215_artifact_sha256),
              "9e71ff3f48cd4da24c34854f8eadfa57f26d7c6ef5bddd1026c89e2ace63bf55");
    copy_text(value.pass216_published_head, sizeof(value.pass216_published_head),
              "0ad2759a4379376244589aa3ee241e51d779df26");
    copy_text(value.pass216_published_tree, sizeof(value.pass216_published_tree),
              "b9ff48b17f1e3c8272cd8c5c7b4381df69d4c7e9");
    copy_text(value.pass216_merge_commit, sizeof(value.pass216_merge_commit),
              "f10e453c5d7c7467cf5e57f6452958491fe763ad");
    copy_text(value.contract_git_blob, sizeof(value.contract_git_blob),
              "9e04e4aca8b127e009c0343ceb5e78092de40c43");
    copy_text(value.addendum_git_blob, sizeof(value.addendum_git_blob),
              "3e4121afe2f5750283f5ef350c0afa416eb2addd");
    return value;
}

int main() {
    auto value = witness();
    hhs::rna::InheritedPass216Alignment binding(value);
    assert(binding.status() == HHS_EXACT_STATUS_OK);
    assert(binding.wired());
    assert(binding.dependency_scoped_validation_bound());
    assert(!binding.runtime_optimization_implementation_claimed());
    assert(!binding.runtime_optimization_roadmap_complete());
    assert(binding.record().global_strict_mode_default == 0U);
    assert(binding.record().cxx_mutation_authority == 0U);
    assert(binding.record().vm81_mutation_authority == 0U);
    std::cout << "PASS219_INHERITED_PASS216_1_16_CPP_OK\n";
    return 0;
}
