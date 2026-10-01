#include <cassert>
#include <cstddef>

#include "hhs_pass219_lane5_global_capability_visibility_cell_wall_1_76.hpp"

using hhs::pass219::Lane5CapabilityVisibilityDecision176;
using hhs::pass219::Lane5CapabilityVisibilityEvidence176;
using hhs::pass219::Lane5GlobalCapabilityVisibilityCellWall176;

int main() {
    Lane5CapabilityVisibilityEvidence176 ok{
        true,   // visible_to_lane5
        false,  // classification_is_visibility_filter
        false,  // discovery_executes_discovered_code
        false,  // direct_linux_or_service_bypass_authority
        false,  // canonical_vm81_mutation_authority
        false,  // canonical_hash72_mint_authority
        false,  // canonical_hash216_mint_authority
        false,  // canonical_persistence_authority
        216U,
    };
    assert(
        Lane5GlobalCapabilityVisibilityCellWall176::validate(ok) ==
        Lane5CapabilityVisibilityDecision176::ACCEPT_CANDIDATE_VISIBILITY
    );

    auto hidden = ok;
    hidden.visible_to_lane5 = false;
    assert(
        Lane5GlobalCapabilityVisibilityCellWall176::validate(hidden) ==
        Lane5CapabilityVisibilityDecision176::REJECT_HIDDEN_CAPABILITY
    );

    auto filtered = ok;
    filtered.classification_is_visibility_filter = true;
    assert(
        Lane5GlobalCapabilityVisibilityCellWall176::validate(filtered) ==
        Lane5CapabilityVisibilityDecision176::REJECT_CLASSIFICATION_FILTER
    );

    auto executes = ok;
    executes.discovery_executes_discovered_code = true;
    assert(
        Lane5GlobalCapabilityVisibilityCellWall176::validate(executes) ==
        Lane5CapabilityVisibilityDecision176::REJECT_DISCOVERY_EXECUTION
    );

    auto bypass = ok;
    bypass.direct_linux_or_service_bypass_authority = true;
    assert(
        Lane5GlobalCapabilityVisibilityCellWall176::validate(bypass) ==
        Lane5CapabilityVisibilityDecision176::REJECT_DIRECT_BYPASS_AUTHORITY
    );

    auto authority = ok;
    authority.canonical_hash216_mint_authority = true;
    assert(
        Lane5GlobalCapabilityVisibilityCellWall176::validate(authority) ==
        Lane5CapabilityVisibilityDecision176::REJECT_CANONICAL_AUTHORITY_ESCALATION
    );

    auto width = ok;
    width.hash216_characters = 215U;
    assert(
        Lane5GlobalCapabilityVisibilityCellWall176::validate(width) ==
        Lane5CapabilityVisibilityDecision176::REJECT_HASH216_WIDTH
    );

    return 0;
}
