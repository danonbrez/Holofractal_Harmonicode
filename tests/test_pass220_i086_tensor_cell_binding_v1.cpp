#include "hhs_pass220_i086_tensor_cell_binding_v1.hpp"
#include <cassert>

using namespace hhs::lane5::reciprocal_nesting;

int main() {
    constexpr std::int64_t numerators[4][4] = {
        {223,13,379,106},{223,13,379,53},
        {223,13,379,106},{3988,3287,4831,15355}
    };
    constexpr std::int64_t denominators[4][4] = {
        {10,1,30,5},{20,2,60,5},
        {30,3,90,15},{693,924,1386,2772}
    };
    for (unsigned row = 0; row < 4; ++row)
        for (unsigned col = 0; col < 4; ++col) {
            const auto v = coefficient(row,col);
            assert(v.numerator == numerators[row][col]);
            assert(v.denominator == denominators[row][col]);
        }
    CellBinding candidate{};
    for (unsigned flat = 0; flat < 5184; ++flat) {
        assert(bind_cell(flat,candidate));
        assert(candidate.address.flat == flat);
        assert(candidate.kernel_row == candidate.address.cell4x4/4);
        assert(candidate.kernel_col == candidate.address.cell4x4%4);
        assert(candidate.candidate_only);
        const auto v = coefficient(candidate.kernel_row,candidate.kernel_col);
        assert(v.numerator == candidate.weight.numerator);
        assert(v.denominator == candidate.weight.denominator);
    }
    assert(!bind_cell(5184,candidate));
}
