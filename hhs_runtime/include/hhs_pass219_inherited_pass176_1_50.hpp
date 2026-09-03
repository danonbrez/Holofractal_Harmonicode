#ifndef HHS_PASS219_INHERITED_PASS176_1_50_HPP
#define HHS_PASS219_INHERITED_PASS176_1_50_HPP
#include "hhs_pass219_inherited_pass176_1_50.h"
namespace hhs::rna {
class InheritedPass176TerminalIDE final {
public:
 static constexpr uint32_t pass_number() noexcept { return HHS_EXACT_PASS219_INHERITED_PASS176_NUMBER; }
 static constexpr bool terminal_pass176_completion_claimed() noexcept { return true; }
 static constexpr bool runtime_os_public_root_preserved() noexcept { return true; }
 static constexpr bool additive_pass176_route_preserved() noexcept { return true; }
 static constexpr bool singleton_vm81_inherited() noexcept { return true; }
 static constexpr uint32_t hash72_commit_streams() noexcept { return 1U; }
 static constexpr bool independent_vm81_authority() noexcept { return false; }
 static constexpr bool independent_hash72_commit_authority() noexcept { return false; }
 static constexpr bool hash216_mutation_authority() noexcept { return false; }
};
static_assert(InheritedPass176TerminalIDE::pass_number() == 176U);
static_assert(InheritedPass176TerminalIDE::terminal_pass176_completion_claimed());
static_assert(InheritedPass176TerminalIDE::runtime_os_public_root_preserved());
static_assert(InheritedPass176TerminalIDE::additive_pass176_route_preserved());
static_assert(InheritedPass176TerminalIDE::hash72_commit_streams() == 1U);
static_assert(!InheritedPass176TerminalIDE::independent_vm81_authority());
static_assert(!InheritedPass176TerminalIDE::independent_hash72_commit_authority());
static_assert(!InheritedPass176TerminalIDE::hash216_mutation_authority());
}
#endif
