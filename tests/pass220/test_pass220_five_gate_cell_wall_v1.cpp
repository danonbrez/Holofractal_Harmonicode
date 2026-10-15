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
    return 0;
}
