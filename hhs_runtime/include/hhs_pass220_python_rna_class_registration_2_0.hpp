#ifndef HHS_PASS220_PYTHON_RNA_CLASS_REGISTRATION_2_0_HPP
#define HHS_PASS220_PYTHON_RNA_CLASS_REGISTRATION_2_0_HPP

#include "hhs_pass220_python_rna_class_registration_2_0.h"
#include "hhs_pass219_rna_rule_grammar_1_11.hpp"

#include <type_traits>

namespace hhs::rna {

class PythonClassRegistration final {
public:
    explicit PythonClassRegistration(
        const HHSExactPass220PythonRNAClassDescriptorV1& descriptor
    ) noexcept {
        status_ = hhs_exact_pass220_python_rna_class_register(
            &descriptor,
            &record_);
    }

    HHSExactStatus status() const noexcept { return status_; }

    const HHSExactPass220PythonRNAClassRegistrationV1& record() const noexcept {
        return record_;
    }

    const HHSExactPass219RNAStrandV1& strand() const noexcept {
        return record_.strand;
    }

    const HHSExactPass219RNAProgramV1& registration_program() const noexcept {
        return record_.program;
    }

    bool registration_only() const noexcept {
        return record_.registration_only == 1U;
    }

    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool hash72_commit_authority() noexcept { return false; }
    static constexpr bool hash216_persistence_authority() noexcept { return false; }
    static constexpr bool floating_point_authority() noexcept { return false; }
    static constexpr bool instance_transition_requires_rna_admission() noexcept {
        return true;
    }

private:
    HHSExactPass220PythonRNAClassRegistrationV1 record_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass220PythonRNAClassMemberV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass220PythonRNAClassMemberV1>);
static_assert(std::is_standard_layout_v<HHSExactPass220PythonRNAClassDescriptorV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass220PythonRNAClassDescriptorV1>);
static_assert(std::is_standard_layout_v<HHSExactPass220PythonRNAClassRegistrationV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass220PythonRNAClassRegistrationV1>);

}  // namespace hhs::rna

#endif
