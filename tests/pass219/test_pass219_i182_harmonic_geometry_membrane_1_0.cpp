#include "hhs_pass219_i182_harmonic_geometry_membrane_1_0.hpp"

#include <cassert>
#include <iostream>

int main() {
    hhs::rna::I182HarmonicGeometryMembrane membrane;
    assert(membrane.status() == HHS_EXACT_STATUS_OK);
    assert(membrane.wired());
    assert(membrane.singleton_vm81_authority_preserved());

    auto tampered = membrane.record();
    tampered.hash72_authority_minted = 1U;
    hhs::rna::I182HarmonicGeometryMembrane rejected(tampered);
    assert(rejected.status() == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    assert(!rejected.wired());

    std::cout << "PASS219 I182 native HARMONIC geometry membrane C++ wrapper: PASS\n";
    return 0;
}
