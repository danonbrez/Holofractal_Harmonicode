#include "hhs_pass220_i086_inherited_fractal_preflight_v1.hpp"
#include <cassert>
#include <type_traits>

using namespace hhs::lane5::reciprocal_nesting;
int main() {
    auto boundaries = parse_ordered_boundaries(kUniversalConstraint);
    auto gates = derive_gate_provenance(kUniversalConstraint,boundaries);
    assert(validate_ordered_tree(kUniversalConstraint,boundaries));
    assert(validate_gate_provenance(kUniversalConstraint,boundaries,gates));
    assert(gates.size()==8);
    HHSExactPass219Hash216FractalQuditWitnessV1 witness{};
    for(unsigned index=0;index<5184;++index) {
        Address address{};
        assert(from_flat(index,address));
        witness.local5184=static_cast<std::uint16_t>(index);
        witness.hash72_major=static_cast<std::uint8_t>(address.hash_row);
        witness.hash72_minor=static_cast<std::uint8_t>(address.hash_col);
        witness.cell81=static_cast<std::uint8_t>(address.qudit);
        witness.operation64=static_cast<std::uint8_t>(index/81);
        assert(address.flat==witness.local5184);
        assert(address.hash_row==witness.hash72_major);
        assert(address.hash_col==witness.hash72_minor);
        assert(address.qudit==witness.cell81);
        assert(witness.operation64==index/81);
    }
    // No fabricated signed environment or canonical transition is created.
    // Native witness_validate execution requires the actual inherited input
    // and Hash216 parent supplied by Lane5's runtime admission pipeline.
    // Verify the actual fail-closed geometry routine, not only address math.
    witness.local5184=5183;
    Address last{};
    assert(from_flat(5183,last));
    witness.hash72_major=static_cast<std::uint8_t>(last.hash_row);
    witness.hash72_minor=static_cast<std::uint8_t>(last.hash_col);
    witness.cell81=static_cast<std::uint8_t>(last.qudit);
    witness.operation64=63;
    assert(verify_inherited_fractal_geometry(witness,kUniversalConstraint,boundaries,gates));
    ++witness.hash72_minor;
    assert(!verify_inherited_fractal_geometry(witness,kUniversalConstraint,boundaries,gates));
    --witness.hash72_minor;
    witness.operation64=62;
    assert(!verify_inherited_fractal_geometry(witness,kUniversalConstraint,boundaries,gates));
    witness.operation64=63;
    witness.local5184=5184;
    assert(!verify_inherited_fractal_geometry(witness,kUniversalConstraint,boundaries,gates));
    witness.local5184=5183;
    auto altered=gates;
    altered[0].lhs_offset++;
    assert(!verify_inherited_fractal_geometry(witness,kUniversalConstraint,boundaries,altered));
    assert(!verify_inherited_fractal_geometry(witness,"A==B",boundaries,gates));

}
