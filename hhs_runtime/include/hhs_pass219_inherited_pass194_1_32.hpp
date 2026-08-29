#ifndef HHS_PASS219_INHERITED_PASS194_1_32_HPP
#define HHS_PASS219_INHERITED_PASS194_1_32_HPP

#include "hhs_pass219_inherited_pass194_1_32.h"

namespace hhs::rna {

class InheritedPass194StorageTrainingSnapshotAuthority final {
public:
    static constexpr uint32_t version() noexcept {
        return (HHS_EXACT_PASS219_INHERITED_PASS194_VERSION_MAJOR << 16) |
               (HHS_EXACT_PASS219_INHERITED_PASS194_VERSION_MINOR << 8) |
               HHS_EXACT_PASS219_INHERITED_PASS194_VERSION_PATCH;
    }

    static HHSExactStatus bind(
        const HHSExactPass194StorageTrainingSnapshotAuthorityWitnessV1 &witness,
        HHSExactPass219InheritedPass194BindingV1 &binding
    ) noexcept {
        return hhs_exact_pass219_bind_pass194_storage_training_snapshot_authority(&witness, &binding);
    }

    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool new_persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool vector_source_authority() noexcept { return false; }
    static constexpr bool vector_consent_authority() noexcept { return false; }
    static constexpr bool snapshot_training_authorization() noexcept { return false; }
    static constexpr bool training_provider_vm81_authority() noexcept { return false; }
    static constexpr bool browser_authority() noexcept { return false; }
    static constexpr bool singleton_vm81_authority_remains_inherited() noexcept { return true; }
    static constexpr bool default_deny_training() noexcept { return true; }
    static constexpr bool explicit_consent_license_closure() noexcept { return true; }
    static constexpr bool deterministic_replay() noexcept { return true; }
};

}  // namespace hhs::rna

#endif
