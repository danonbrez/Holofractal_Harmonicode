#include "hhs_pass220_i086_reciprocal_nesting_address_v1.hpp"
#include <cassert>
#include <cstdint>

using namespace hhs::lane5::reciprocal_nesting;

int main() {
    Address a{}, b{}, c{}, d{};
    for (std::uint32_t i = 0; i < kExtent; ++i) {
        assert(from_flat(i, a));
        assert(from_nested(a.region, a.cell4x4, a.qudit, b));
        assert(from_h36(a.region, a.h36_row, a.h36_col, c));
        assert(from_flat(a.harmonic_block * kHarmonicBlock + a.harmonic_cell, d));
        assert(same_address(a, b) && same_address(a, c) && same_address(a, d));
        assert(a.flat == a.hash_row * kHashSide + a.hash_col);
        const auto mirror = mirror_flat(i);
        assert(mirror_flat(mirror) == i);
        assert(from_flat(mirror, d));
        assert(d.region == 3U - a.region);
        assert(d.cell4x4 == 15U - a.cell4x4);
        assert(d.qudit == 80U - a.qudit);
    }
    assert(!from_flat(kExtent, a));
    assert(!from_nested(4, 0, 0, a));
    assert(!from_nested(0, 16, 0, a));
    assert(!from_nested(0, 0, 81, a));
    assert(!from_h36(0, 36, 0, a));
    assert(!from_h36(0, 0, 36, a));
    NestingStep root{}, child{}, bad{};
    assert(append_step(0, 0, nullptr, root));
    assert(append_step(1, 5183, &root, child));
    assert(child.has_predecessor && child.predecessor_flat == 0);
    assert(!append_step(3, 7, &root, bad));
    assert(!append_step(1, 7, nullptr, bad));
    return 0;
}
