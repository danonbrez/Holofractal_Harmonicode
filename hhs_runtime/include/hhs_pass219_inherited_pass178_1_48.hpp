#ifndef HHS_PASS219_INHERITED_PASS178_1_48_HPP
#define HHS_PASS219_INHERITED_PASS178_1_48_HPP
#include "hhs_pass219_inherited_pass178_1_48.h"
namespace hhs::rna {
class InheritedPass178ExactPhysics final {
public:
 static constexpr uint32_t pass_number() noexcept { return HHS_EXACT_PASS219_INHERITED_PASS178_NUMBER; }
 static constexpr bool terminal_pass178_completion_claimed() noexcept { return false; }
 static constexpr bool repair_forward_required() noexcept { return true; }
 static constexpr bool complete_historical_constraint_corpus() noexcept { return false; }
 static constexpr uint32_t remaining_terminal_category_count() noexcept { return HHS_EXACT_PASS178_I148_REMAINING_TERMINAL_CATEGORY_COUNT; }
 static constexpr bool singleton_vm81_inherited() noexcept { return true; }
 static constexpr bool independent_vm81_authority() noexcept { return false; }
 static constexpr bool independent_hash72_commit_authority() noexcept { return false; }
 static constexpr bool hash216_mutation_authority() noexcept { return false; }
 static constexpr bool renderer_mutation_authority() noexcept { return false; }
 static constexpr bool gpu_mutation_authority() noexcept { return false; }
 static constexpr bool browser_mutation_authority() noexcept { return false; }
 static constexpr bool floating_point_canonical_authority() noexcept { return false; }
};
static_assert(InheritedPass178ExactPhysics::pass_number() == 178U);
static_assert(!InheritedPass178ExactPhysics::terminal_pass178_completion_claimed());
static_assert(InheritedPass178ExactPhysics::repair_forward_required());
static_assert(!InheritedPass178ExactPhysics::complete_historical_constraint_corpus());
static_assert(!InheritedPass178ExactPhysics::independent_vm81_authority());
static_assert(!InheritedPass178ExactPhysics::independent_hash72_commit_authority());
static_assert(!InheritedPass178ExactPhysics::hash216_mutation_authority());
static_assert(!InheritedPass178ExactPhysics::renderer_mutation_authority());
static_assert(!InheritedPass178ExactPhysics::gpu_mutation_authority());
static_assert(!InheritedPass178ExactPhysics::browser_mutation_authority());
static_assert(!InheritedPass178ExactPhysics::floating_point_canonical_authority());
}
#endif
