#pragma once

#include "frame5184.hpp"
#include "inherited_bindings.hpp"
#include "pass219_contract.hpp"

#include <cstdint>

namespace hhs::pass219 {

enum class MembraneAdmission : std::uint8_t {
    Unclassified = 0,
    Admissible,
    Rejected
};

struct MembraneInput final {
    const Frame5184* frame{nullptr};
    const InheritedBindings* inherited{nullptr};
};

struct MembraneReceipt final {
    MembraneAdmission admission{MembraneAdmission::Unclassified};
    std::int64_t delta_e{kDeltaE};
};

// Declaration surface only.
// No Pass 219 execution implementation exists in Iteration 1.
class CellWallMembrane final {
public:
    CellWallMembrane() = delete;

    [[nodiscard]]
    static MembraneReceipt inspect(const MembraneInput&) noexcept;
};

}  // namespace hhs::pass219
