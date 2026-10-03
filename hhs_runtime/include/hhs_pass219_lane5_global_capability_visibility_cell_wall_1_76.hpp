#pragma once

#include <cstddef>
#include <cstdint>

namespace hhs::pass219 {

struct Lane5CapabilityVisibilityEvidence176 {
    bool visible_to_lane5;
    bool classification_is_visibility_filter;
    bool discovery_executes_discovered_code;
    bool direct_linux_or_service_bypass_authority;
    bool canonical_vm81_mutation_authority;
    bool canonical_hash72_mint_authority;
    bool canonical_hash216_mint_authority;
    bool canonical_persistence_authority;
    std::size_t hash216_characters;
};

enum class Lane5CapabilityVisibilityDecision176 : std::uint32_t {
    ACCEPT_CANDIDATE_VISIBILITY = 0,
    REJECT_HIDDEN_CAPABILITY = 1,
    REJECT_CLASSIFICATION_FILTER = 2,
    REJECT_DISCOVERY_EXECUTION = 3,
    REJECT_DIRECT_BYPASS_AUTHORITY = 4,
    REJECT_CANONICAL_AUTHORITY_ESCALATION = 5,
    REJECT_HASH216_WIDTH = 6,
};

class Lane5GlobalCapabilityVisibilityCellWall176 final {
public:
    static constexpr std::size_t kHash216Characters = 216U;

    [[nodiscard]] static constexpr Lane5CapabilityVisibilityDecision176 validate(
        const Lane5CapabilityVisibilityEvidence176& evidence) noexcept {
        if (!evidence.visible_to_lane5) {
            return Lane5CapabilityVisibilityDecision176::REJECT_HIDDEN_CAPABILITY;
        }
        if (evidence.classification_is_visibility_filter) {
            return Lane5CapabilityVisibilityDecision176::REJECT_CLASSIFICATION_FILTER;
        }
        if (evidence.discovery_executes_discovered_code) {
            return Lane5CapabilityVisibilityDecision176::REJECT_DISCOVERY_EXECUTION;
        }
        if (evidence.direct_linux_or_service_bypass_authority) {
            return Lane5CapabilityVisibilityDecision176::REJECT_DIRECT_BYPASS_AUTHORITY;
        }
        if (evidence.canonical_vm81_mutation_authority ||
            evidence.canonical_hash72_mint_authority ||
            evidence.canonical_hash216_mint_authority ||
            evidence.canonical_persistence_authority) {
            return Lane5CapabilityVisibilityDecision176::REJECT_CANONICAL_AUTHORITY_ESCALATION;
        }
        if (evidence.hash216_characters != kHash216Characters) {
            return Lane5CapabilityVisibilityDecision176::REJECT_HASH216_WIDTH;
        }
        return Lane5CapabilityVisibilityDecision176::ACCEPT_CANDIDATE_VISIBILITY;
    }
};

}  // namespace hhs::pass219
