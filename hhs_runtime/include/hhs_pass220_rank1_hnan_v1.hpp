#ifndef HHS_PASS220_RANK1_HNAN_V1_HPP
#define HHS_PASS220_RANK1_HNAN_V1_HPP
#include <cstdint>
#include <string_view>

namespace hhs::lane5 {
struct Rank1Circuit final {
    std::string_view periodicity_modulus;
    std::string_view quantization_unit;
    std::uint32_t source_position{};
    std::uint32_t predecessor_gate{};
};
struct PhaseState final {
    std::string_view curvature;
    std::string_view phase;
    std::uint64_t phase_writes{};
};
struct HnanResult final {
    PhaseState state{};
    std::uint32_t gain_numerator{1};
    std::uint32_t gain_denominator{1};
    bool bypassed{};
    bool requires_native_gate{};
    bool authorized_commit{};
};
inline HnanResult evaluate_rank1_boundary(
    const Rank1Circuit& circuit, const PhaseState& prior,
    bool quantization_zero_proven
) noexcept {
    HnanResult result{};
    result.state = prior;
    // Only a native typed zero witness may select the HNAN branch.
    // Empty strings and literal "0" are not proof of typed zero.
    if (quantization_zero_proven) {
        result.bypassed = true;
        return result; // gain 1, unchanged curvature, phase, write count
    }
    result.requires_native_gate = true;
    return result; // no scalar division or fabricated phase write
}
} // namespace hhs::lane5
#endif
