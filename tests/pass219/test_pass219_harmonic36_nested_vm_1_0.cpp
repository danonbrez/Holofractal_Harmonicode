#include "hhs_pass219_harmonic36_nested_vm_1_0.hpp"

#include <cassert>
#include <cstdint>

int main() {
    HHSExactPass219H36CoordinateV1 c{};
    assert(hhs_exact_pass219_h36_coordinate(5183U, &c) == HHS_EXACT_STATUS_OK);
    assert(c.word144 == 143U);
    assert(c.bit36 == 35U);
    assert(c.vm81_cell81 == 80U);
    assert(c.vm81_operation64 == 63U);
    assert(c.hash72_row72 == 71U);
    assert(c.hash72_col72 == 71U);

    auto word = hhs::rna::Harmonic36Word::render(
        HHS_EXACT_PASS219_H36_RULE_COLTRANE_THREE_TONIC, 0U);
    assert(word.transposed(12U).raw() == word.raw());

    hhs::rna::Harmonic36NestedVM vm;
    vm.seed_equal_temperament();
    static_assert(!hhs::rna::Harmonic36NestedVM::independent_vm81_authority);
    static_assert(!hhs::rna::Harmonic36NestedVM::independent_hash72_authority);
    return 0;
}
