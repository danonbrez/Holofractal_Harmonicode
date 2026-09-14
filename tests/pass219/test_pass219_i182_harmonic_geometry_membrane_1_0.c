#include "hhs_pass219_i182_harmonic_geometry_membrane_1_0.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    static const uint32_t pairs[5][2] = {
        {3U, 3U}, {3U, 4U}, {3U, 5U}, {4U, 3U}, {5U, 3U}
    };
    static const uint32_t closures[5][3] = {
        {4U, 6U, 4U},
        {6U, 12U, 8U},
        {12U, 30U, 20U},
        {8U, 12U, 6U},
        {20U, 30U, 12U}
    };
    HHSExactPass219I182GeometryFactorWitnessV1 factor;
    HHSExactPass219I182PentagonalWitnessV1 pentagon;
    HHSExactPass219I182PlatonicClosureV1 closure;
    HHSExactPass219I182GeometryMembraneWitnessV1 witness;
    HHSExactPass219I182GeometryMembraneWitnessV1 tampered;
    uint32_t i;

    assert(hhs_exact_pass219_i182_geometry_membrane_version() == (1U << 16U));

    assert(hhs_exact_pass219_i182_geometry_factor_witness(72U, 72U, &factor) ==
           HHS_EXACT_STATUS_OK);
    assert(factor.product == 5184U && factor.exact == 1U);
    assert(hhs_exact_pass219_i182_geometry_factor_witness(36U, 143U, &factor) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(hhs_exact_pass219_i182_pentagonal_witness(&pentagon) ==
           HHS_EXACT_STATUS_OK);
    assert(pentagon.hydration_quantum == 5184U);
    assert(pentagon.half_sector == 36U);
    assert(pentagon.external == 72U);
    assert(pentagon.interior == 108U);
    assert(pentagon.supplementary == 144U);
    assert(pentagon.sides * pentagon.external == 360U);
    assert(pentagon.zero_phase_closure == 0U);

    for (i = 0U; i < 5U; ++i) {
        assert(hhs_exact_pass219_i182_derive_platonic_closure(
            pairs[i][0], pairs[i][1], &closure) == HHS_EXACT_STATUS_OK);
        assert(closure.vertices == closures[i][0]);
        assert(closure.edges == closures[i][1]);
        assert(closure.faces == closures[i][2]);
        assert(closure.euler == 2U);
        assert(hhs_exact_pass219_i182_validate_platonic_candidate(&closure) ==
               HHS_EXACT_STATUS_OK);
    }

    assert(hhs_exact_pass219_i182_derive_platonic_closure(5U, 4U, &closure) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(hhs_exact_pass219_i182_derive_dodecahedral_closure(&closure) ==
           HHS_EXACT_STATUS_OK);
    assert(closure.p == 5U && closure.q == 3U);
    assert(closure.vertices == 20U && closure.edges == 30U && closure.faces == 12U);

    closure.edges = 31U;
    assert(hhs_exact_pass219_i182_validate_platonic_candidate(&closure) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    assert(hhs_exact_pass219_i182_geometry_membrane_build(&witness) ==
           HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_i182_geometry_membrane_validate(&witness) ==
           HHS_EXACT_STATUS_OK);
    assert(witness.singleton_vm81_authority_preserved == 1U);
    assert(witness.vm81_authority_minted == 0U);
    assert(witness.vm81_direct_mutation_authority == 0U);
    assert(witness.hash72_authority_minted == 0U);
    assert(witness.hash216_persistence_authority == 0U);
    assert(witness.cxx_mutation_authority == 0U);
    assert(witness.public_operation_authority == 0U);
    assert(witness.capability_binding_authority == 0U);
    assert(witness.rendering_authority == 0U);
    assert(witness.canonical_float_authority == 0U);
    assert(witness.authoritative_vertex_table_used == 0U);

    memcpy(&tampered, &witness, sizeof(tampered));
    tampered.vm81_authority_minted = 1U;
    assert(hhs_exact_pass219_i182_geometry_membrane_validate(&tampered) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE);

    puts("PASS219 I182 native HARMONIC geometry membrane C ABI: PASS");
    return 0;
}
