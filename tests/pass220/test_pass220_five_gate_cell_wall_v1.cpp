#include "hhs_pass220_five_gate_cell_wall_v1.hpp"
#include <fstream>
#include <iterator>
#include <string>

int main() {
    constexpr auto path = "contracts/pass220/PASS_220_ORDERED_FIVE_GATE_PHASE36_72_SOURCE_V1.harmonicode";
    std::ifstream file(path, std::ios::binary);
    if (!file) return 1;
    const std::string exact(std::istreambuf_iterator<char>{file}, {});
    auto passed = hhs::lane5::audit_five_gate_candidate(exact, exact);
    if (!passed.source_exact || !passed.gate_layout_exact || !passed.order_exact ||
        !passed.candidate_only || passed.native_proof_observed ||
        passed.vm81_admission_authorized || passed.canonical_hash_mint_authorized) return 2;

    std::string phase = exact;
    auto at = phase.find("u^36==z^2");
    if (at == std::string::npos) return 3;
    phase[at + 3] = '7';
    auto changed = hhs::lane5::audit_five_gate_candidate(phase, exact);
    auto forged_authority = hhs::lane5::audit_five_gate_candidate(phase, phase);
    if (forged_authority.source_exact || forged_authority.order_exact) return 16;
    if (changed.source_exact || changed.order_exact ||
        changed.vm81_admission_authorized || changed.native_proof_observed) return 4;

    std::string swapped = exact;
    auto pair = swapped.find("(x*y-1)/b^2*(z*w-1)");
    if (pair == std::string::npos) return 5;
    swapped.replace(pair, 5, "(z*w");
    auto reordered = hhs::lane5::audit_five_gate_candidate(swapped, exact);
    if (reordered.source_exact || reordered.vm81_admission_authorized) return 6;

    std::string elided = exact;
    elided.erase(229, 2);
    auto missing = hhs::lane5::audit_five_gate_candidate(elided, exact);
    if (missing.gate_layout_exact || missing.vm81_admission_authorized) return 7;

    auto foreign = hhs::lane5::audit_five_gate_candidate(exact, phase);
    if (foreign.source_exact || foreign.vm81_admission_authorized) return 8;
    hhs::lane5::FiveGateProofFrontier frontier{};
    auto absent = hhs::lane5::audit_five_gate_proof_frontier(passed, frontier);
    if (absent.ready_for_vm81_proof_request || absent.vm81_admission_authorized) return 9;
    frontier.native_gate_verified.fill(1U);
    frontier.predecessor_witness_linked.fill(1U);
    frontier.source_graph_root_verified = true;
    frontier.native_proof_provider_verified = true;
    frontier.signed_environment_verified = true;
    auto ready = hhs::lane5::audit_five_gate_proof_frontier(passed, frontier);
    if (!ready.declarations_complete || ready.ready_for_vm81_proof_request ||
        ready.vm81_admission_authorized) return 10;
    for (unsigned i = 0; i < 5; ++i) {
        auto missing_gate = frontier;
        missing_gate.native_gate_verified[i] = 0U;
        if (hhs::lane5::audit_five_gate_proof_frontier(passed, missing_gate)
                .declarations_complete) return 11;
        auto broken_link = frontier;
        broken_link.predecessor_witness_linked[i] = 0U;
        if (hhs::lane5::audit_five_gate_proof_frontier(passed, broken_link)
                .declarations_complete) return 12;
    }
    auto untrusted_provider = frontier;
    untrusted_provider.native_proof_provider_verified = false;
    if (hhs::lane5::audit_five_gate_proof_frontier(passed, untrusted_provider)
            .declarations_complete) return 17;
    auto not_binary = frontier;
    not_binary.native_gate_verified[0] = 2U;
    if (hhs::lane5::audit_five_gate_proof_frontier(passed, not_binary)
            .declarations_complete) return 18;
    auto not_binary_link = frontier;
    not_binary_link.predecessor_witness_linked[4] = 2U;
    if (hhs::lane5::audit_five_gate_proof_frontier(passed, not_binary_link)
            .declarations_complete) return 19;
    auto wrong_source = hhs::lane5::audit_five_gate_proof_frontier(changed, frontier);
    if (wrong_source.declarations_complete) return 13;
    auto wrong_root = frontier;
    wrong_root.source_graph_root_verified = false;
    if (hhs::lane5::audit_five_gate_proof_frontier(passed, wrong_root)
            .declarations_complete) return 14;
    auto unsigned_env = frontier;
    unsigned_env.signed_environment_verified = false;
    if (hhs::lane5::audit_five_gate_proof_frontier(passed, unsigned_env)
            .declarations_complete) return 15;
    std::array<hhs::lane5::GateWitnessBinding, 5> bindings{};
    for (std::size_t i = 0; i < bindings.size(); ++i) {
        bindings[i] = {hhs::lane5::kFiveGateOffsets[i],
                       hhs::lane5::kFiveGateDepths[i],
                       static_cast<std::uint32_t>(i), true};
    }
    if (!hhs::lane5::audit_gate_witness_bindings(passed, bindings)) return 20;
    auto misordered = bindings;
    misordered[1].source_offset = hhs::lane5::kFiveGateOffsets[2];
    if (hhs::lane5::audit_gate_witness_bindings(passed, misordered)) return 21;
    auto unverified = bindings;
    unverified[3].authenticated_by_native_provider = false;
    if (hhs::lane5::audit_gate_witness_bindings(passed, unverified)) return 22;
    auto bad_predecessor = bindings;
    bad_predecessor[2].predecessor_gate = 0;
    if (hhs::lane5::audit_gate_witness_bindings(passed, bad_predecessor)) return 23;
    if (hhs::lane5::audit_gate_witness_bindings(changed, bindings)) return 24;
    if (hhs::lane5::audit_five_gate_proof_frontier(passed, frontier)
            .vm81_admission_authorized) return 25;
    return 0;
}
