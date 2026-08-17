#pragma once

#include "pass219_contract.hpp"

#include <array>
#include <cstddef>
#include <cstdint>

namespace hhs::pass219 {

using Vm81Cell = std::uint64_t;

struct Frame5184 final {
    std::array<Vm81Cell, kVm81CellCount> cells{};
};

static_assert(sizeof(Frame5184) == kFrameBytes);
static_assert(sizeof(Frame5184) * 8 == kFrameBits);

}  // namespace hhs::pass219
