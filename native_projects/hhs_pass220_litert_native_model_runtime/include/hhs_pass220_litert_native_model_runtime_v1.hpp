#ifndef HHS_PASS220_LITERT_NATIVE_MODEL_RUNTIME_V1_HPP
#define HHS_PASS220_LITERT_NATIVE_MODEL_RUNTIME_V1_HPP

#include "hhs_pass220_litert_native_model_runtime_v1.h"

#include <type_traits>

namespace hhs::litert {

class NativeModelRuntimeRegistration final {
public:
    explicit NativeModelRuntimeRegistration(
        const HHSLiteRTNativeModelDescriptorV1& descriptor
    ) noexcept {
        status_ = hhs_litert_native_model_register(&descriptor, &record_);
    }

    HHSLiteRTNativeStatusV1 status() const noexcept { return status_; }

    const HHSLiteRTNativeModelRegistrationV1& record() const noexcept {
        return record_;
    }

    static constexpr bool model_output_advisory_only() noexcept { return true; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool hash72_commit_authority() noexcept { return false; }
    static constexpr bool hash216_persistence_authority() noexcept { return false; }
    static constexpr bool floating_point_canonical_authority() noexcept { return false; }
    static constexpr bool external_litert_compatibility_supported() noexcept {
        return true;
    }
};

static_assert(std::is_standard_layout_v<HHSLiteRTNativeTensorSpecV1>);
static_assert(std::is_trivially_copyable_v<HHSLiteRTNativeTensorSpecV1>);
static_assert(std::is_standard_layout_v<HHSLiteRTNativeModelDescriptorV1>);
static_assert(std::is_trivially_copyable_v<HHSLiteRTNativeModelDescriptorV1>);
static_assert(std::is_standard_layout_v<HHSLiteRTNativeModelRegistrationV1>);
static_assert(std::is_trivially_copyable_v<HHSLiteRTNativeModelRegistrationV1>);

}  // namespace hhs::litert

#endif
