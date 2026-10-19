#ifndef HHS_PASS219_LANE5_INTEGER_19_SHELL_V1_HPP
#define HHS_PASS219_LANE5_INTEGER_19_SHELL_V1_HPP
// Canonical integer 19-shell; midpoint scaffold is not the admitted constructor.
// Pure, typed witness candidate. No canonical VM81/Hash216 mint authority.
#include <array>
#include <cstdint>
namespace hhs::pass219 {
using ShellRow = std::array<std::int64_t,4>;
constexpr std::array<ShellRow,4> integer_19_shell{{
    ShellRow{{1,2,3,5}}, ShellRow{{2,4,6,10}},
    ShellRow{{3,6,9,15}}, ShellRow{{4,7,11,19}}
}};
constexpr bool integer_19_shell_closes(const std::array<ShellRow,4>& m) noexcept {
    constexpr std::array<std::int64_t,4> expected_rows{{11,22,33,41}};
    constexpr std::array<std::int64_t,4> expected_cols{{10,19,29,49}};
    std::array<std::int64_t,4> cols{{0,0,0,0}};
    std::int64_t total=0;
    for(std::size_t r=0;r<4;++r) {
        std::int64_t row_sum=0;
        for(std::size_t c=0;c<4;++c) {
            row_sum+=m[r][c];
            cols[c]+=m[r][c];
        }
        if(row_sum!=expected_rows[r])return false;
        if(m[r][0]+m[r][1]!=m[r][2] ||
           3*m[r][0]+m[r][1]!=m[r][3])return false;
        total+=row_sum;
    }
    if(cols!=expected_cols || total!=107)return false;
    return m[3][3]==19 && 2*m[3][3]==18+20 &&
           m[3][0]==4 && m[3][1]==7 && m[3][2]==11;
}
static_assert(integer_19_shell_closes(integer_19_shell),
              "Integer 19-shell closure, rotated kernel and totals must hold");
} // namespace hhs::pass219
#endif
