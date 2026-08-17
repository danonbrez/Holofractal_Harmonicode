#pragma once

#include <cstddef>
#include <cstdint>

namespace hhs::pass219 {

inline constexpr std::uint32_t kPassNumber = 219;
inline constexpr std::uint32_t kIterationNumber = 1;

inline constexpr std::size_t kVm81CellCount = 81;
inline constexpr std::size_t kCellWidthBits = 64;
inline constexpr std::size_t kFrameBits =
    kVm81CellCount * kCellWidthBits;

inline constexpr std::size_t kFrameBytes = kFrameBits / 8;

// Pass 219 I1 energy/state invariant.
inline constexpr std::int64_t kDeltaE = 0;

static_assert(kFrameBits == 5184);
static_assert(kFrameBytes == 648);
static_assert(kDeltaE == 0);

enum class Authority : std::uint8_t {
    HeaderStubOnly = 0
};

inline constexpr Authority kAuthority =
    Authority::HeaderStubOnly;

}  // namespace hhs::pass219
