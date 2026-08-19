#define main pass212_c_conformance_embedded_main
#include "test_pass219_inherited_pass212_1_16.c"
#undef main

#include "hhs_pass219_inherited_pass212_1_16.hpp"

#include <cassert>
#include <iostream>

int main() {
    auto input = witness();
    hhs::rna::InheritedPass212FullHydrationRecovery binding(input);
    assert(binding.status() == HHS_EXACT_STATUS_OK);
    assert(binding.wired());
    assert(binding.record().pass219_new_canonical_mutation_authority == 0U);
    assert(binding.record().cxx_mutation_authority == 0U);
    assert(binding.record().vm81_mutation_authority == 0U);
    input = witness();
    input.cxx_mutation_authority = 1U;
    hhs::rna::InheritedPass212FullHydrationRecovery rejected(input);
    assert(!rejected.wired());
    std::cout << "PASS219_INHERITED_PASS212_1_16_CPP_OK\n";
    return 0;
}
