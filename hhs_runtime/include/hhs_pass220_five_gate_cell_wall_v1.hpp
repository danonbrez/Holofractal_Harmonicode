#ifndef HHS_PASS220_FIVE_GATE_CELL_WALL_V1_HPP
#define HHS_PASS220_FIVE_GATE_CELL_WALL_V1_HPP

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>
#include <openssl/evp.h>
#include <cstring>

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
    bool declarations_complete{false};
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
    out.declarations_complete =
        source.source_exact && source.order_exact && source.gate_layout_exact &&
        out.all_five_native_gates && out.ordered_predecessor_chain &&
        out.source_graph_root_verified && proof.native_proof_provider_verified &&
        proof.signed_environment_verified;
    // Caller-supplied flags are declarations, never authentic proof evidence.
    // No source-dependent native provider is bound here: fail closed.
    out.ready_for_vm81_proof_request = false;
    // Readiness for a native proof request is never admission itself.
    out.vm81_admission_authorized = false;
    return out;
}

inline constexpr std::array<std::size_t, 5> kFiveGateOffsets{54U,139U,223U,229U,276U};
inline constexpr std::array<int, 5> kFiveGateDepths{3,3,1,0,1};

inline bool source_digest_pinned(std::string_view source) noexcept {
    constexpr std::array<unsigned char, 32> expected{
        0xce,0xec,0x28,0x24,0x99,0xdd,0xaf,0x48,
        0xeb,0xa1,0xd2,0x5b,0x63,0x13,0xc4,0x07,
        0xd9,0x46,0x6d,0x37,0x9e,0x32,0x1b,0x47,
        0xf9,0xa6,0xb3,0xf7,0x52,0xc2,0xa4,0x99
    };
    if (source.size() != 283U) return false;
    std::array<unsigned char, EVP_MAX_MD_SIZE> digest{};
    unsigned int size = 0U;
    if (EVP_Digest(source.data(), source.size(), digest.data(), &size,
                   EVP_sha256(), nullptr) != 1 || size != expected.size())
        return false;
    return std::memcmp(digest.data(), expected.data(), expected.size()) == 0;
}


struct GateWitnessBinding final {
    std::size_t source_offset{};
    int source_depth{};
    std::uint32_t predecessor_gate{};
    bool native_provider_claimed_verification{false};
};

// Ordered witness addresses are deliberately not interpreted as algebraic truth.
// A caller cannot set an authority bit to promote any of these declarations.
inline bool audit_gate_witness_bindings(
    const FiveGateAudit& source,
    const std::array<GateWitnessBinding, 5>& bindings
) noexcept {
    if (!source.source_exact || !source.order_exact || !source.gate_layout_exact)
        return false;
    for (std::size_t i = 0; i < bindings.size(); ++i) {
        if (bindings[i].source_offset != kFiveGateOffsets[i] ||
            bindings[i].source_depth != kFiveGateDepths[i] ||
            bindings[i].predecessor_gate != static_cast<std::uint32_t>(i) ||
            !bindings[i].native_provider_claimed_verification)
            return false;
    }
    return true;
}


using GateDigest = std::array<unsigned char, 32>;
struct GateLineageDeclaration final {
    GateDigest predecessor{};
    GateDigest claimed_digest{};
};

// Fixed-width, big-endian position encoding; domain separation forbids
// confusing a layout declaration with an admitted Hash72/Hash216 receipt.
inline GateDigest gate_layout_digest(
    const GateDigest& prior, std::size_t gate_index
) noexcept {
    GateDigest result{};
    if (gate_index >= kFiveGateOffsets.size()) return result;
    EVP_MD_CTX* ctx = EVP_MD_CTX_new();
    if (ctx == nullptr) return result;
    constexpr unsigned char domain[] = "HHS-P220-GATE-LAYOUT-DECL-V1";
    constexpr GateDigest source_id{
        0xce,0xec,0x28,0x24,0x99,0xdd,0xaf,0x48,
        0xeb,0xa1,0xd2,0x5b,0x63,0x13,0xc4,0x07,
        0xd9,0x46,0x6d,0x37,0x9e,0x32,0x1b,0x47,
        0xf9,0xa6,0xb3,0xf7,0x52,0xc2,0xa4,0x99
    };
    const std::array<unsigned char, 4> address{
        static_cast<unsigned char>(gate_index),
        static_cast<unsigned char>((kFiveGateOffsets[gate_index] >> 8U) & 255U),
        static_cast<unsigned char>(kFiveGateOffsets[gate_index] & 255U),
        static_cast<unsigned char>(kFiveGateDepths[gate_index])
    };
    unsigned int length = 0;
    const bool ok = EVP_DigestInit_ex(ctx, EVP_sha256(), nullptr) == 1 &&
        EVP_DigestUpdate(ctx, domain, sizeof(domain) - 1U) == 1 &&
        EVP_DigestUpdate(ctx, source_id.data(), source_id.size()) == 1 &&
        EVP_DigestUpdate(ctx, prior.data(), prior.size()) == 1 &&
        EVP_DigestUpdate(ctx, address.data(), address.size()) == 1 &&
        EVP_DigestFinal_ex(ctx, result.data(), &length) == 1 &&
        length == result.size();
    EVP_MD_CTX_free(ctx);
    if (!ok) result.fill(0U);
    return result;
}

inline bool audit_gate_lineage_declarations(
    const FiveGateAudit& source,
    const std::array<GateLineageDeclaration, 5>& lineage,
    const GateDigest& genesis
) noexcept {
    if (!source.source_exact || !source.order_exact || !source.gate_layout_exact)
        return false;
    GateDigest prior = genesis;
    for (std::size_t i = 0; i < lineage.size(); ++i) {
        if (lineage[i].predecessor != prior) return false;
        const GateDigest expected = gate_layout_digest(prior, i);
        if (lineage[i].claimed_digest != expected) return false;
        prior = expected;
    }
    return true;
}

inline FiveGateAudit audit_five_gate_candidate(
    std::string_view source, std::string_view authoritative_source
) noexcept {
    FiveGateAudit out{};
    out.source_exact = source == authoritative_source && source_digest_pinned(source);
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
