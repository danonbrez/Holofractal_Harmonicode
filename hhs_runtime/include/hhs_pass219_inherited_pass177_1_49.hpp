#ifndef HHS_PASS219_INHERITED_PASS177_1_49_HPP
#define HHS_PASS219_INHERITED_PASS177_1_49_HPP
#include "hhs_pass219_inherited_pass177_1_49.h"
namespace hhs::rna {
class InheritedPass177CreationWorkflows final {
public:
 static constexpr uint32_t pass_number() noexcept { return HHS_EXACT_PASS219_INHERITED_PASS177_NUMBER; }
 static constexpr bool terminal_pass177_completion_claimed() noexcept { return false; }
 static constexpr bool repair_forward_required() noexcept { return true; }
 static constexpr uint32_t remaining_terminal_category_count() noexcept { return HHS_EXACT_PASS177_I149_REMAINING_TERMINAL_CATEGORY_COUNT; }
 static constexpr bool singleton_vm81_inherited() noexcept { return true; }
 static constexpr bool independent_vm81_authority() noexcept { return false; }
 static constexpr bool independent_hash72_commit_authority() noexcept { return false; }
 static constexpr bool hash216_mutation_authority() noexcept { return false; }
 static constexpr bool browser_identity_authority() noexcept { return false; }
 static constexpr bool memory_checkpoint_authority() noexcept { return false; }
 static constexpr bool historical_stage_truth_preserved() noexcept { return true; }
};
static_assert(InheritedPass177CreationWorkflows::pass_number() == 177U);
static_assert(!InheritedPass177CreationWorkflows::terminal_pass177_completion_claimed());
static_assert(InheritedPass177CreationWorkflows::repair_forward_required());
static_assert(!InheritedPass177CreationWorkflows::independent_vm81_authority());
static_assert(!InheritedPass177CreationWorkflows::independent_hash72_commit_authority());
static_assert(!InheritedPass177CreationWorkflows::hash216_mutation_authority());
static_assert(!InheritedPass177CreationWorkflows::browser_identity_authority());
static_assert(!InheritedPass177CreationWorkflows::memory_checkpoint_authority());
}
#endif
