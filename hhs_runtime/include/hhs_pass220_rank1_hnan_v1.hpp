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
    bool typed_zero_authenticated{};
    bool candidate_only{true};
};
inline HnanResult evaluate_rank1_boundary(
    const Rank1Circuit& circuit, const PhaseState& prior,
    bool quantization_zero_declared
) noexcept {
    (void)circuit;  // The circuit is preserved for later typed evaluation; no scalar inspection here.
    HnanResult result{};
    result.state = prior;
    // The caller's zero declaration selects a diagnostic candidate only.
    // It is NOT a native witness or authorization to evaluate/commit.
    if (quantization_zero_declared) {
        result.bypassed = true;
        result.typed_zero_authenticated = false;
        return result; // gain 1, unchanged curvature, phase, write count
    }
    result.requires_native_gate = true;
    return result; // no scalar division or fabricated phase write
}
} // namespace hhs::lane5
#endif
