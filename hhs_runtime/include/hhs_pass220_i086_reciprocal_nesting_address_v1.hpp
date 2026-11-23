#ifndef HHS_PASS220_I086_RECIPROCAL_NESTING_ADDRESS_V1_HPP
#define HHS_PASS220_I086_RECIPROCAL_NESTING_ADDRESS_V1_HPP

#include <cstdint>

namespace hhs::lane5::reciprocal_nesting {

// Positional circuit coordinates only. Native VM81, H36, HNAN, Hash72 and
// Hash216 operations, operator order, closure and admission remain inherited.
inline constexpr std::uint32_t kExtent = 5184;
inline constexpr std::uint32_t kQudit = 81;
inline constexpr std::uint32_t kBlocks = 64;
inline constexpr std::uint32_t kRegions = 4;
inline constexpr std::uint32_t kCellsPerRegion = 16;
inline constexpr std::uint32_t kRegionWidth = 1296;
inline constexpr std::uint32_t kH36 = 36;
inline constexpr std::uint32_t kHarmonicBlock = 144;
inline constexpr std::uint32_t kHashSide = 72;

struct Address final {
    std::uint32_t flat{};
    std::uint32_t region{};
    std::uint32_t cell4x4{};
    std::uint32_t qudit{};
    std::uint32_t h36_row{};
    std::uint32_t h36_col{};
    std::uint32_t harmonic_block{};
    std::uint32_t harmonic_cell{};
    std::uint32_t hash_row{};
    std::uint32_t hash_col{};
};

constexpr bool from_flat(std::uint32_t flat, Address& out) noexcept {
    if (flat >= kExtent) return false;
    const std::uint32_t within = flat % kRegionWidth;
    out = Address{
        flat,
        flat / kRegionWidth,
        within / kQudit,
        within % kQudit,
        within / kH36,
        within % kH36,
        flat / kHarmonicBlock,
        flat % kHarmonicBlock,
        flat / kHashSide,
        flat % kHashSide
    };
    return true;
}

constexpr bool from_nested(std::uint32_t region,
                           std::uint32_t cell4x4,
                           std::uint32_t qudit,
                           Address& out) noexcept {
    if (region >= kRegions || cell4x4 >= kCellsPerRegion || qudit >= kQudit)
        return false;
    return from_flat(region * kRegionWidth + cell4x4 * kQudit + qudit, out);
}

constexpr bool from_h36(std::uint32_t region,
                        std::uint32_t row,
                        std::uint32_t col,
                        Address& out) noexcept {
    if (region >= kRegions || row >= kH36 || col >= kH36) return false;
    return from_flat(region * kRegionWidth + row * kH36 + col, out);
}

// Palindromic partner is positional: no commutation of ordered native operands.
constexpr std::uint32_t mirror_flat(std::uint32_t flat) noexcept {
    return kExtent - 1U - flat;
}

constexpr bool same_address(const Address& a, const Address& b) noexcept {
    return a.flat == b.flat && a.region == b.region &&
           a.cell4x4 == b.cell4x4 && a.qudit == b.qudit &&
           a.h36_row == b.h36_row && a.h36_col == b.h36_col &&
           a.harmonic_block == b.harmonic_block &&
           a.harmonic_cell == b.harmonic_cell &&
           a.hash_row == b.hash_row && a.hash_col == b.hash_col;
}

// Each recursive depth adds an ordered address digit without reinterpreting
// a native state. Caller owns the ancestor chain and the admission gate.
struct NestingStep final {
    std::uint32_t depth{};
    Address address{};
    std::uint32_t predecessor_flat{};
    bool has_predecessor{};
};

constexpr bool append_step(std::uint32_t depth,
                           std::uint32_t flat,
                           const NestingStep* parent,
                           NestingStep& out) noexcept {
    if (parent && (depth == 0U || parent->depth + 1U != depth)) return false;
    if (!parent && depth != 0U) return false;
    Address address{};
    if (!from_flat(flat, address)) return false;
    out = NestingStep{depth, address, parent ? parent->address.flat : 0U,
                      parent != nullptr};
    return true;
}

static_assert(kExtent == kQudit * kBlocks);
static_assert(kExtent == kHashSide * kHashSide);
static_assert(kExtent == kRegions * kCellsPerRegion * kQudit);
static_assert(kExtent == kRegions * kH36 * kH36);
static_assert(kExtent == 36U * kHarmonicBlock);
static_assert(kRegionWidth == 9U * kHarmonicBlock);
}  // namespace hhs::lane5::reciprocal_nesting
#endif
