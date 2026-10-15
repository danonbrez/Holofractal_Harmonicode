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


struct FiveGateProofFrontier final {
    // Inputs must originate from the native typed proof provider, not this audit.
    std::array<std::uint8_t, 5> native_gate_verified{};
    std::array<std::uint8_t, 5> predecessor_witness_linked{};
    bool source_graph_root_verified{false};
    bool native_proof_provider_verified{false};
    bool signed_environment_verified{false};
};

struct FiveGateProofReadiness final {
    bool all_five_native_gates{false};
    bool ordered_predecessor_chain{false};
    bool source_graph_root_verified{false};
    bool ready_for_vm81_proof_request{false};
    bool vm81_admission_authorized{false};
};

inline FiveGateProofReadiness audit_five_gate_proof_frontier(
    const FiveGateAudit& source, const FiveGateProofFrontier& proof
) noexcept {
    FiveGateProofReadiness out{};
    out.all_five_native_gates = true;
    out.ordered_predecessor_chain = true;
    for (std::size_t i = 0U; i < 5U; ++i) {
        out.all_five_native_gates =
            out.all_five_native_gates && proof.native_gate_verified[i] == 1U;
        out.ordered_predecessor_chain =
            out.ordered_predecessor_chain && proof.predecessor_witness_linked[i] == 1U;
    }
    out.source_graph_root_verified = proof.source_graph_root_verified;
    out.ready_for_vm81_proof_request =
        source.source_exact && source.order_exact && source.gate_layout_exact &&
        out.all_five_native_gates && out.ordered_predecessor_chain &&
        out.source_graph_root_verified && proof.native_proof_provider_verified &&
        proof.signed_environment_verified;
    // Readiness for a native proof request is never admission itself.
    out.vm81_admission_authorized = false;
    return out;
}

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
