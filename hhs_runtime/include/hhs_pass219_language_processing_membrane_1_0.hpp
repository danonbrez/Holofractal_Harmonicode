#ifndef HHS_PASS219_LANGUAGE_PROCESSING_MEMBRANE_1_0_HPP
#define HHS_PASS219_LANGUAGE_PROCESSING_MEMBRANE_1_0_HPP

#include "hhs_pass219_language_processing_membrane_1_0.h"
#include <cstdint>
#include <type_traits>

namespace hhs::pass219 {
class LanguageProcessingMembrane final {
public:
    LanguageProcessingMembrane(const char source_root_hash72[HHS_EXACT_HASH72_STRLEN], std::uint32_t source_character_count) noexcept
        : status_(hhs_exact_pass219_language_membrane_init(source_root_hash72, source_character_count, &native_)) {}
    HHSExactStatus status() const noexcept { return status_; }
    HHSExactStatus bind(const HHSExactPass219LanguageBindingV1& binding) noexcept {
        if (status_ != HHS_EXACT_STATUS_OK) return status_;
        status_ = hhs_exact_pass219_language_membrane_add(&native_, &binding);
        return status_;
    }
    HHSExactStatus validate() const noexcept {
        if (status_ != HHS_EXACT_STATUS_OK) return status_;
        return hhs_exact_pass219_language_membrane_validate(&native_);
    }
    HHSExactStatus validate_complete() const noexcept {
        if (status_ != HHS_EXACT_STATUS_OK) return status_;
        return hhs_exact_pass219_language_membrane_validate_complete(&native_);
    }
    HHSExactStatus project_rna_plan(const HHSExactPass219RNAExecutionPlanV1& plan, HHSExactPass219LanguageRNAProjectionV1& out) const noexcept {
        if (status_ != HHS_EXACT_STATUS_OK) return status_;
        return hhs_exact_pass219_language_membrane_project_rna_plan(&native_, &plan, &out);
    }
    const HHSExactPass219LanguageMembraneV1& native() const noexcept { return native_; }
    HHSExactPass219LanguageMembraneV1& native() noexcept { return native_; }
private:
    HHSExactPass219LanguageMembraneV1 native_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};
static_assert(std::is_standard_layout_v<HHSExactPass219LanguageBindingV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219LanguageMembraneV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219LanguageRNAProjectionV1>);
}  // namespace hhs::pass219
#endif
