#include "hhs_pass220_rank1_hnan_v1.hpp"
#include <string_view>
int main() {
    using namespace hhs::lane5;
    const PhaseState prior{"curvature:original","phase:u^36",17};
    const Rank1Circuit circuit{"t^3-t","0",54,3};
    const auto bypass = evaluate_rank1_boundary(circuit, prior, true);
    if (!bypass.bypassed || bypass.requires_native_gate ||
        bypass.gain_numerator != 1 || bypass.gain_denominator != 1 ||
        bypass.state.curvature != prior.curvature ||
        bypass.state.phase != prior.phase ||
        bypass.state.phase_writes != prior.phase_writes ||
        bypass.authorized_commit || bypass.typed_zero_authenticated ||
        !bypass.candidate_only) return 1;
    // A textual zero without a native witness must not trigger HNAN.
    const auto unproven = evaluate_rank1_boundary(circuit, prior, false);
    if (unproven.bypassed || !unproven.requires_native_gate ||
        unproven.authorized_commit || unproven.typed_zero_authenticated ||
        unproven.state.phase_writes != prior.phase_writes) return 2;
    const Rank1Circuit nonzero{"t^3-t","u^72",54,3};
    const auto active = evaluate_rank1_boundary(nonzero, prior, false);
    if (active.bypassed || !active.requires_native_gate ||
        active.state.phase != prior.phase || active.authorized_commit ||
        active.typed_zero_authenticated || !active.candidate_only) return 3;
    return 0;
}
