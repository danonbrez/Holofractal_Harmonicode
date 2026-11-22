#ifndef HHS_PASS220_GENESIS_LOSHU_QUARTIC_NATIVE_V1_HPP
#define HHS_PASS220_GENESIS_LOSHU_QUARTIC_NATIVE_V1_HPP

/* Additive exact candidate tensor algebra. The 64 phase regions are supplied
 * as complete ordered native objects. This module DOES NOT assign phases,
 * equate the new 64-region tensor with the octonion product surface, mutate
 * VM81, or create a Hash72/Hash216 receipt.
 */
#include <array>
#include <cstddef>
#include <cstdint>

namespace hhs::rosetta {

struct Gaussian final {
    std::int64_t real{0}, imag{0};
};
constexpr Gaussian operator+(Gaussian a, Gaussian b) noexcept {
    return {a.real+b.real, a.imag+b.imag};
}
constexpr Gaussian operator-(Gaussian a, Gaussian b) noexcept {
    return {a.real-b.real, a.imag-b.imag};
}
constexpr Gaussian operator*(Gaussian a, Gaussian b) noexcept {
    return {a.real*b.real-a.imag*b.imag, a.real*b.imag+a.imag*b.real};
}
constexpr bool operator==(Gaussian a, Gaussian b) noexcept {
    return a.real==b.real && a.imag==b.imag;
}

using Matrix3 = std::array<std::array<Gaussian, 3>, 3>;

constexpr Matrix3 matrix_times(const Matrix3& a, const Matrix3& b) noexcept {
    Matrix3 result{};
    for (std::size_t i=0;i<3;++i)
        for (std::size_t j=0;j<3;++j)
            for (std::size_t k=0;k<3;++k)
                result[i][j] = result[i][j] + a[i][k]*b[k][j];
    return result;
}

constexpr Matrix3 elementwise_sum(const Matrix3& a, const Matrix3& b) noexcept {
    Matrix3 result{};
    for (std::size_t i=0;i<3;++i)
        for (std::size_t j=0;j<3;++j)
            result[i][j]=a[i][j]+b[i][j];
    return result;
}

constexpr Matrix3 elementwise_difference(const Matrix3& a, const Matrix3& b) noexcept {
    Matrix3 result{};
    for (std::size_t i=0;i<3;++i)
        for (std::size_t j=0;j<3;++j)
            result[i][j]=a[i][j]-b[i][j];
    return result;
}

constexpr Matrix3 lo_shu_shifted_two() noexcept {
    constexpr std::int64_t l[3][3]={{4,9,2},{3,5,7},{8,1,6}};
    Matrix3 result{};
    for (std::size_t i=0;i<3;++i)
        for (std::size_t j=0;j<3;++j)
            result[i][j]={l[i][j]-2,0};
    return result;
}
constexpr Matrix3 quartic_q() noexcept {
    // I^2=-1. Ordered phase roles and positions remain distinct.
    return {{{{0,1},{1,0},{0,-1}},
             {{1,0},{-1,0},{1,0}},
             {{0,-1},{1,0},{0,1}}}};
}

constexpr Matrix3 ordered_quartic_product() noexcept {
    const Matrix3 x=lo_shu_shifted_two();
    const Matrix3 q=quartic_q();
    // Deliberately preserve the requested MatrixTimes parenthesization.
    return matrix_times(matrix_times(elementwise_difference(x,q),
                                     elementwise_sum(x,q)),
                        matrix_times(x,q));
}

constexpr Gaussian determinant(const Matrix3& m) noexcept {
    return m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
         - m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
         + m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]);
}

constexpr bool same_matrix(const Matrix3& a, const Matrix3& b) noexcept {
    for (std::size_t i=0;i<3;++i)
        for (std::size_t j=0;j<3;++j)
            if (!(a[i][j]==b[i][j])) return false;
    return true;
}
struct PhaseRegion final {
    std::uint8_t region_index{};
    std::array<std::uint64_t,9> ordered_nucleus_words{};
    Matrix3 native_ordered_projection{};
};
struct Native64PhaseTensor final {
    std::array<PhaseRegion,64> regions{};

    bool validate() const noexcept {
        for (std::size_t p=0;p<regions.size();++p)
            if (regions[p].region_index!=p) return false;
        return true;
    }
    bool exact_reconstruction(const Native64PhaseTensor& source) const noexcept {
        if (!validate() || !source.validate()) return false;
        for (std::size_t p=0;p<regions.size();++p) {
            const auto& a=regions[p];
            const auto& b=source.regions[p];
            if (a.ordered_nucleus_words!=b.ordered_nucleus_words ||
                !same_matrix(a.native_ordered_projection,b.native_ordered_projection))
                return false;
        }
        return true;
    }
};

constexpr Matrix3 EXPECTED_QUARTIC_PRODUCT =
    {{{{128,8},{368,-32},{224,24}},
      {{208,80},{304,64},{208,-144}},
      {{384,-88},{48,-32},{288,120}}}};
static_assert(same_matrix(ordered_quartic_product(),EXPECTED_QUARTIC_PRODUCT),
              "ordered quartic Lo Shu MatrixTimes drift");
static_assert(determinant(ordered_quartic_product())==
              Gaussian{-13271040,-38707200},
              "ordered quartic determinant drift");
}  // namespace hhs::rosetta
#endif
