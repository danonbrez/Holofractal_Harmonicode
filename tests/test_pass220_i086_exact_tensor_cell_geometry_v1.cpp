#include "hhs_pass220_i086_reciprocal_nesting_address_v1.hpp"
#include <array>
#include <cassert>
#include <cstdint>

namespace {
struct Rational {
    std::int64_t n;
    std::int64_t d;
};
constexpr bool eq(Rational a, Rational b) noexcept {
    return a.n * b.d == b.n * a.d;
}
constexpr std::array<std::array<int,4>,4> fibonacci = {{
    {{1,2,3,5}}, {{2,4,6,10}}, {{3,6,9,15}}, {{4,7,11,18}}
}};
constexpr std::array<std::array<int,4>,4> durer = {{
    {{16,3,2,13}}, {{5,10,11,8}}, {{9,6,7,12}}, {{4,15,14,1}}
}};
// Exact coefficients from the user's first tensor. The equation-valued
// closure factor is deliberately not scalarized or evaluated in this test.
constexpr Rational expected[4][4] = {
    {{223,10},{13,1},{379,30},{106,5}},
    {{223,20},{13,2},{379,60},{53,5}},
    {{223,30},{13,3},{379,90},{106,15}},
    {{3988,693},{3287,924},{4831,1386},{15355,2772}}
};
constexpr std::int64_t gcd(std::int64_t a, std::int64_t b) noexcept {
    while (b != 0) {
        const auto next = a % b;
        a = b; b = next;
    }
    return a < 0 ? -a : a;
}
constexpr Rational add(Rational a, Rational b) noexcept {
    const auto g = gcd(a.d,b.d);
    const auto n = a.n*(b.d/g)+b.n*(a.d/g);
    const auto d = a.d*(b.d/g);
    const auto g2=gcd(n,d);
    return {n/g2,d/g2};
}
constexpr Rational product_cell(int row, int col) noexcept {
    Rational value{0,1};
    for (int k=0;k<4;++k)
        value=add(value,{durer[k][col],fibonacci[row][k]});
    return value;
}
constexpr bool all_exact() noexcept {
    for (int i=0;i<4;++i)
        for (int j=0;j<4;++j)
            if(!eq(product_cell(i,j),expected[i][j])) return false;
    return true;
}
constexpr bool inherited_magic_and_recurrence() noexcept {
    for (int i=0;i<4;++i) {
        int row=0,col=0;
        for(int j=0;j<4;++j) {
            row+=durer[i][j]; col+=durer[j][i];
        }
        if (row!=34 || col!=34) return false;
    }
    for (int i=0;i<4;++i)
        for(int j=0;j<4;++j)
            if(durer[i][j]+durer[3-i][3-j]!=17) return false;
    for (int i=0;i<4;++i) {
        if(fibonacci[i][2]!=fibonacci[i][0]+fibonacci[i][1] ||
           fibonacci[i][3]!=fibonacci[i][1]+fibonacci[i][2]) return false;
    }
    return true;
}
// Exact, integer-only supergolden characteristic recurrence P(n+3)=P(n+2)+P(n).
// This is an algebraic recurrence witness, not a substitute for the
// source-ordered modular-factorial expression or native Pisot cell admission.
constexpr bool pisot_recurrence() noexcept {
    std::int64_t a=0,b=0,c=1;
    constexpr std::int64_t expected_terms[] = {1,1,1,2,3,4,6,9,13,19,28,41,60,88};
    for(const auto value : expected_terms) {
        if(c!=value) return false;
        const auto next = c+a;
        a=b; b=c; c=next;
    }
    return true;
}
static_assert(all_exact(), "4x4 reciprocal tensor coefficient mismatch");
static_assert(inherited_magic_and_recurrence(), "magic/recurrence geometry lost");
static_assert(pisot_recurrence(), "supergolden integer recurrence mismatch");
}

int main() {
    using namespace hhs::lane5::reciprocal_nesting;
    for(unsigned region=0;region<4;++region)
      for(unsigned cell=0;cell<16;++cell) {
        Address start{},end{};
        assert(from_nested(region,cell,0,start));
        assert(from_nested(region,cell,80,end));
        assert(start.flat + 80 == end.flat);
        assert(start.region == end.region && start.cell4x4 == end.cell4x4);
      }
    assert(all_exact());
    assert(inherited_magic_and_recurrence());
    assert(pisot_recurrence());
}
