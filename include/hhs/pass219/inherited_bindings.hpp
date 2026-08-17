#pragma once

#include <cstdint>

namespace hhs::pass219 {

// Forward declarations only.
// Concrete adapters remain inherited and are not redefined by I1.

struct NativePhaseState;
struct Vm81State;
struct Hash72Primitive;
struct Hash216Index;
struct TrinaryLoShuQudit;
struct HydrationCoordinate;
struct HydrationRomView;
struct ExactSerializedState;

struct InheritedBindings final {
    const NativePhaseState* phase_state{nullptr};
    const Vm81State* vm81_state{nullptr};
    const Hash72Primitive* hash72{nullptr};
    const Hash216Index* hash216{nullptr};
    const TrinaryLoShuQudit* qudit{nullptr};
    const HydrationRomView* hydration_rom{nullptr};
    const ExactSerializedState* serialization{nullptr};
};

}  // namespace hhs::pass219
