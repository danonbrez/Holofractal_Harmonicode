#include "hhs_pass220_foreign_proof_guard_v1.hpp"
#include <algorithm>
#include <iterator>

int main() {
    HHSExactPass219Pass169AuthorityProofV1 foreign{};
    // Inherited I162 is source-bound to the older Pass219 combined equation.
    constexpr unsigned char pass219_source[32] = {
        0x33,0x15,0x64,0x1c,0x8d,0x6a,0xa9,0xfc,
        0x4f,0x39,0x18,0xec,0xcd,0xa8,0xe3,0xa4,
        0x0c,0x84,0x45,0xcc,0x41,0x7a,0x65,0xe5,
        0xde,0xa6,0x83,0xf6,0x80,0x20,0xcf,0x53
    };
    std::copy(std::begin(pass219_source), std::end(pass219_source),
              std::begin(foreign.combined_source_sha256));
    foreign.gate_count = 5U;
    foreign.source_reconstruction_verified = 1U;
    auto inherited = hhs::lane5::inspect_pass219_proof_for_five_gate_source(foreign);
    if (inherited.source_identity_matches ||
        !inherited.five_gate_count_matches ||
        !inherited.source_reconstruction_declared ||
        inherited.proof_import_admitted ||
        inherited.vm81_admission_authorized) return 1;

    // Even a forged source identity and all declared flags cannot mint authority.
    std::copy(hhs::lane5::kPhase3672SourceSha.begin(),
              hhs::lane5::kPhase3672SourceSha.end(),
              std::begin(foreign.combined_source_sha256));
    auto claimed = hhs::lane5::inspect_pass219_proof_for_five_gate_source(foreign);
    if (!claimed.source_identity_matches ||
        claimed.proof_import_admitted ||
        claimed.vm81_admission_authorized) return 2;
    foreign.gate_count = 4U;
    if (hhs::lane5::inspect_pass219_proof_for_five_gate_source(foreign)
            .five_gate_count_matches) return 3;
    foreign.gate_count = 5U;
    foreign.source_reconstruction_verified = 0U;
    if (hhs::lane5::inspect_pass219_proof_for_five_gate_source(foreign)
            .source_reconstruction_declared) return 4;
    return 0;
}
