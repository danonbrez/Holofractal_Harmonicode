#include "hhs_pass219_core_holographic_rna_cell_wall_1_24.hpp"
#include "hhs_pass220_i086_lane5_conway_cell_wall_v1.h"
#include <array>
#include <cstdint>
#include <cstdio>

#define CHECK(x) do { if (!(x)) { std::fprintf(stderr, "FAIL line %d: %s\\n", __LINE__, #x); return 1; } } while (0)

int main() {
    std::uint8_t one = 1U;
    HHSExactBigUIntView a2{static_cast<std::uint32_t>(sizeof(HHSExactBigUIntView)), 1U, &one};
    hhs::rna::OrthogonalGlyphMembrane membrane(a2, a2);
    CHECK(membrane.status() == HHS_EXACT_STATUS_OK);
    hhs::rna::CoreHolographicRNACellWall wall(membrane);
    std::array<std::uint8_t, 81> seed{};
    std::array<std::uint8_t, 81> next{};
    CHECK(wall.evolve_conway81(seed, next) == HHS_EXACT_STATUS_OK);
    CHECK(next == seed); // Empty configuration is stable.
    seed[4*9+3] = seed[4*9+4] = seed[4*9+5] = 1U;
    CHECK(wall.evolve_conway81(seed, next) == HHS_EXACT_STATUS_OK);
    std::array<std::uint8_t, 81> vertical{};
    vertical[3*9+4] = vertical[4*9+4] = vertical[5*9+4] = 1U;
    CHECK(next == vertical);
    CHECK(wall.evolve_conway81(next, next) == HHS_EXACT_STATUS_OK);
    CHECK(next == seed); // Period two, including alias-safe output.
    seed.fill(0U);
    seed[4*9+8] = seed[4*9+0] = seed[4*9+1] = 1U;
    CHECK(wall.evolve_conway81(seed, next) == HHS_EXACT_STATUS_OK);
    vertical.fill(0U);
    vertical[3*9+0] = vertical[4*9+0] = vertical[5*9+0] = 1U;
    CHECK(next == vertical); // Toroidal column wrap.
    HHSExactUQCELInputV1 ingress{};
    ingress.delta = a2;
    std::array<std::uint8_t, 81> ingress_output{};
    CHECK(hhs_pass220_i086_lane5_conway81_cell_wall(&ingress, seed.data(), ingress_output.data()) == HHS_EXACT_STATUS_OK);
    CHECK(ingress_output == vertical);
    CHECK(hhs_pass220_i086_lane5_conway81_cell_wall(nullptr, seed.data(), ingress_output.data()) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    seed[0] = 2U;
    next.fill(7U);
    CHECK(wall.evolve_conway81(seed, next) == HHS_EXACT_STATUS_INVALID_ARGUMENT);
    for (auto v : next) CHECK(v == 7U); // Fail closed, no partial output.
    return 0;
}
