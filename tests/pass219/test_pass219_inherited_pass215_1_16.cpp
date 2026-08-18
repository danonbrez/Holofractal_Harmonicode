#include "hhs_pass219_inherited_pass215_1_16.hpp"

#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>

static void copy_text(char *target, std::size_t size, const char *value) {
    const std::size_t length = std::strlen(value);
    assert(length + 1U == size);
    std::memcpy(target, value, size);
}

static HHSExactPass215TerminalClosureWitnessV1 witness() {
    static constexpr std::uint32_t tokens[HHS_EXACT_PASS215_SELECTED_TOKEN_COUNT] = {
        450U, 6575U, 471U, 528U, 2827U, 322U, 278U
    };
    HHSExactPass215TerminalClosureWitnessV1 value{};
    value.struct_size = static_cast<std::uint32_t>(sizeof(value));
    value.version = hhs_exact_pass219_inherited_pass215_version();
    value.cumulative_test_count = 240U;
    value.selected_token_count = HHS_EXACT_PASS215_SELECTED_TOKEN_COUNT;
    for (std::size_t index = 0U; index < HHS_EXACT_PASS215_SELECTED_TOKEN_COUNT; ++index)
        value.selected_token_ids[index] = tokens[index];
    value.terminal_iteration = 20U;
    value.contracted_benchmark_complete = 1U;
    value.bounded_profile_only = 1U;
    value.cross_process_replay = 1U;
    value.semantic_exactness = 1U;
    value.reused_unique_chunk_count = 36U;
    value.reused_compressed_blob_bytes = 28375966ULL;
    value.incremental_later_compressed_blob_bytes = 125510422ULL;
    value.later_standalone_compressed_blob_bytes = 153886388ULL;
    value.shared_store_savings_bytes = 28375966ULL;
    value.validation_run = 31325831364ULL;
    value.validation_job = 93275935886ULL;
    copy_text(value.final_head, sizeof(value.final_head), "b85ea7c340976a20a78f9c7d8d89a688a1b4f8fc");
    copy_text(value.final_tree, sizeof(value.final_tree), "17127e80a3f4852aeaedd1b807971fb4b4fba229");
    copy_text(value.main_merge, sizeof(value.main_merge), "cc7a0d67d7d9e4bd1e800f62d5ef577cb4ab1086");
    copy_text(value.artifact_sha256, sizeof(value.artifact_sha256), "9e71ff3f48cd4da24c34854f8eadfa57f26d7c6ef5bddd1026c89e2ace63bf55");
    copy_text(value.model_sha256, sizeof(value.model_sha256), "6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04");
    copy_text(value.earlier_checkpoint_root_hash216, sizeof(value.earlier_checkpoint_root_hash216), "151113337a143adb29eecfa9cb1f4df41b6458953afb2c5258b97dff5f3643b4");
    copy_text(value.later_checkpoint_root_hash216, sizeof(value.later_checkpoint_root_hash216), "bff3f18e1324caacdbd610b833b3ebd6ebe35e525821c0ffad349fc81ad9474f");
    copy_text(value.shared_content_store_root_hash216, sizeof(value.shared_content_store_root_hash216), "b7a9eb1678f263f20c5b61c0d9d3f01b76b152e2786b7e887ecb8265cbe454da");
    copy_text(value.shared_checkpoint_bundle_root_hash216, sizeof(value.shared_checkpoint_bundle_root_hash216), "14953737a095ee9365386e436706cedd7a77328a04eb4dc3d5e45935cd367c8a");
    copy_text(value.sequential_checkpoint_reuse_root_hash216, sizeof(value.sequential_checkpoint_reuse_root_hash216), "52980a2e4b7890d136e549a4812dd859cc75e0ea4f442872dc99392e261ed7c0");
    copy_text(value.terminal_completion_root_hash216, sizeof(value.terminal_completion_root_hash216), "3dfb034753309c5f45f56f9bec5bf2178b1eb74974264cc306e46c8d6551f76a");
    copy_text(value.suite_root_hash216, sizeof(value.suite_root_hash216), "3be955aecac999e945cdf48df63e0be13d2c353de8e20c6869a2364c2ba72234");
    copy_text(value.evidence_root_hash216, sizeof(value.evidence_root_hash216), "5a8a17e10b1dc10db2912bc2df40aa67306fc520439716eab47596dc1e8aac1e");
    copy_text(value.receipt_hash72, sizeof(value.receipt_hash72), "rimw6Mf!E(*xCD5DK1/WGTK)*WRAl<RWjBQyi!qSI+rXW>H0L9AtWuu/3Cs5HKZ!B)JCwUTM");
    return value;
}

int main() {
    auto value = witness();
    hhs::rna::InheritedPass215TerminalClosure binding(value);
    assert(binding.status() == HHS_EXACT_STATUS_OK);
    assert(binding.wired());
    assert(binding.bounded_profile_only());
    assert(!binding.broader_generation_authority_promoted());
    assert(binding.record().strict_argmax_chain_bound == 1U);
    assert(binding.record().zero_restore_replay_bound == 1U);
    assert(binding.record().cxx_mutation_authority == 0U);
    assert(binding.record().vm81_mutation_authority == 0U);
    std::cout << "PASS219_INHERITED_PASS215_1_16_CPP_OK\n";
    return 0;
}
