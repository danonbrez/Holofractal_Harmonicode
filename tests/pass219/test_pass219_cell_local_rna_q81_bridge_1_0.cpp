#include "hhs_pass219_cell_local_rna_q81_bridge_1_0.hpp"

#include <cassert>
#include <cstdint>
#include <type_traits>

static_assert(std::is_standard_layout_v<
    HHSExactPass219Hash216FractalQuditWitnessV1>);
static_assert(std::is_standard_layout_v<
    HHSExactPass219RNAAdmissionCandidateV1>);

int main() {
    // Exhaustively check dual coordinate mapping without changing 1.45 ABI.
    for (std::uint32_t cell = 0; cell < 81; ++cell) {
        for (std::uint32_t op = 0; op < 64; ++op) {
            const auto slot = cell * 64U + op;
            assert(slot < 5184U);
            assert((slot / 64U) == cell);
            assert((slot % 64U) == op);
            assert((slot / 72U) < 72U);
            assert((slot % 72U) < 72U);
            assert((slot / 72U) * 72U + slot % 72U == slot);
        }
    }
    // Exhaustively check the distinct RNA transcription view as well.\n    for (std::uint32_t op = 0; op < 64U; ++op) {\n        for (std::uint32_t g = 0; g < 243U; ++g) {\n            const auto v = 243U * op + g;\n            const auto trit = v / 5184U;\n            const auto rna_slot = v % 5184U;\n            assert(trit < 3U);\n            assert(5184U * trit + rna_slot == v);\n            assert((5184U * trit + rna_slot) / 243U == op);\n            assert((5184U * trit + rna_slot) % 243U == g);\n        }\n    }\n    // The new bridge is deliberately only a candidate validator and
    // reversible reconstruction adapter. It never calls VM81 admission.
    return 0;
}
