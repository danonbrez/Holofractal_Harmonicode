#ifndef HHS_PASS220_LITERT_NATIVE_EXECUTION_GRAPH_V1_HPP
#define HHS_PASS220_LITERT_NATIVE_EXECUTION_GRAPH_V1_HPP

#include "hhs_pass220_litert_native_execution_graph_v1.h"

#include <type_traits>

namespace hhs::litert {

class NativeExecutionGraph final {
public:
    explicit NativeExecutionGraph(
        const HHSLiteRTNativeGraphDescriptorV1& descriptor
    ) noexcept {
        status_ = hhs_litert_native_graph_register(&descriptor, &record_);
    }

    HHSLiteRTNativeGraphStatusV1 status() const noexcept { return status_; }

    const HHSLiteRTNativeGraphRegistrationV1& record() const noexcept {
        return record_;
    }

    static constexpr bool topology_authority() noexcept { return true; }
    static constexpr bool numeric_execution_authority() noexcept { return false; }
    static constexpr bool numpy1_numeric_lowering_required() noexcept { return true; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool host_float_canonical_authority() noexcept { return false; }

private:
    HHSLiteRTNativeGraphRegistrationV1 record_{};
    HHSLiteRTNativeGraphStatusV1 status_{HHS_LITERT_NATIVE_GRAPH_ERR_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSLiteRTNativeGraphTensorV1>);
static_assert(std::is_trivially_copyable_v<HHSLiteRTNativeGraphTensorV1>);
static_assert(std::is_standard_layout_v<HHSLiteRTNativeGraphOperationV1>);
static_assert(std::is_trivially_copyable_v<HHSLiteRTNativeGraphOperationV1>);
static_assert(std::is_standard_layout_v<HHSLiteRTNativeGraphDescriptorV1>);
static_assert(std::is_trivially_copyable_v<HHSLiteRTNativeGraphDescriptorV1>);

}  // namespace hhs::litert

#endif
