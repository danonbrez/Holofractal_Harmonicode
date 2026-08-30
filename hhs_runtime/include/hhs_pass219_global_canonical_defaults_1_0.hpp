#ifndef HHS_PASS219_GLOBAL_CANONICAL_DEFAULTS_1_0_HPP
#define HHS_PASS219_GLOBAL_CANONICAL_DEFAULTS_1_0_HPP
#include "hhs_pass219_global_canonical_defaults_1_0.h"
namespace hhs::rna {
class GlobalCanonicalDefaults final {
public:
 static constexpr uint32_t version() noexcept { return (HHS_EXACT_PASS219_GLOBAL_DEFAULT_VERSION_MAJOR<<16)|(HHS_EXACT_PASS219_GLOBAL_DEFAULT_VERSION_MINOR<<8)|HHS_EXACT_PASS219_GLOBAL_DEFAULT_VERSION_PATCH; }
 static constexpr bool numbered_passes_are_additive() noexcept { return true; }
 static constexpr bool successful_implementations_must_remain_reachable() noexcept { return true; }
 static constexpr bool standalone_passes_allowed() noexcept { return false; }
 static constexpr bool isolated_native_project_is_canonical_substitute() noexcept { return false; }
 static constexpr bool cross_cutting_defaults_are_mandatory() noexcept { return true; }
 static constexpr bool retroactive_repair_forward_required() noexcept { return true; }
 static constexpr bool grandfather_bypass_allowed() noexcept { return false; }
 static constexpr bool explicit_upgrade_or_deprecation_required() noexcept { return true; }
 static constexpr bool singleton_vm81_authority_preserved() noexcept { return true; }
 static constexpr bool exact_symbolic_authority_required() noexcept { return true; }
 static constexpr uint32_t wired_ceiling_pass() noexcept { return HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_CEILING; }
 static constexpr uint32_t wired_floor_pass() noexcept { return HHS_EXACT_PASS219_GLOBAL_DEFAULT_WIRED_FLOOR; }
 static constexpr uint32_t registered_binding_count() noexcept { return HHS_EXACT_PASS219_GLOBAL_DEFAULT_BINDING_COUNT; }
 static HHSExactStatus validate() noexcept { return hhs_exact_pass219_global_canonical_defaults_validate(); }
};
template <uint16_t PassNumber,uint8_t Variant=HHS_EXACT_PASS219_BINDING_VARIANT_NONE>
struct CumulativePassGlobalDefaults final {
 static constexpr uint16_t pass_number=PassNumber; static constexpr uint8_t variant=Variant; static constexpr bool cumulative_reachability_required=true; static constexpr bool global_defaults_required=true; static constexpr bool repair_forward_on_gap=true; static constexpr bool standalone_application=false; static constexpr bool optional_cross_cutting_defaults=false;
};
static_assert(GlobalCanonicalDefaults::numbered_passes_are_additive());
static_assert(GlobalCanonicalDefaults::successful_implementations_must_remain_reachable());
static_assert(!GlobalCanonicalDefaults::standalone_passes_allowed());
static_assert(!GlobalCanonicalDefaults::isolated_native_project_is_canonical_substitute());
static_assert(GlobalCanonicalDefaults::cross_cutting_defaults_are_mandatory());
static_assert(GlobalCanonicalDefaults::retroactive_repair_forward_required());
static_assert(!GlobalCanonicalDefaults::grandfather_bypass_allowed());
static_assert(GlobalCanonicalDefaults::explicit_upgrade_or_deprecation_required());
static_assert(GlobalCanonicalDefaults::singleton_vm81_authority_preserved());
static_assert(GlobalCanonicalDefaults::exact_symbolic_authority_required());
}
#endif
