#ifndef HHS_PASS220_FIVE_GATE_CELL_WALL_V1_HPP
#define HHS_PASS220_FIVE_GATE_CELL_WALL_V1_HPP

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace hhs::lane5 {
struct FiveGateAudit final {
    bool source_exact{false};
    bool order_exact{false};
    bool gate_layout_exact{false};
    bool candidate_only{true};
    bool native_proof_observed{false};
    bool vm81_admission_authorized{false};
    bool canonical_hash_mint_authorized{false};
};

inline constexpr std::array<std::size_t, 5> kFiveGateOffsets{54U,139U,223U,229U,276U};
inline constexpr std::array<int, 5> kFiveGateDepths{3,3,1,0,1};

inline FiveGateAudit audit_five_gate_candidate(
    std::string_view source, std::string_view authoritative_source
) noexcept {
    FiveGateAudit out{};
    out.source_exact = source == authoritative_source && source.size() == 283U;
    std::size_t gate = 0U;
    int depth = 0;
    bool balanced = true;
    for (std::size_t i = 0; i < source.size(); ++i) {
        if (source[i] == '(') ++depth;
        else if (source[i] == ')') {
            --depth;
            if (depth < 0) { balanced = false; break; }
        }
        if (i + 1U < source.size() && source[i] == '=' && source[i+1U] == '=') {
            if (gate >= kFiveGateOffsets.size() ||
                i != kFiveGateOffsets[gate] || depth != kFiveGateDepths[gate]) {
                balanced = false;
                break;
            }
            ++gate;
            ++i;
        }
    }
    out.gate_layout_exact = balanced && depth == 0 && gate == 5U;
    out.order_exact = out.source_exact && out.gate_layout_exact;
    // No candidate audit can mint VM81 authority, regardless of input.
    return out;
}
}  // namespace hhs::lane5
#endif
