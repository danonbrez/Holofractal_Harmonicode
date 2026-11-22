#ifndef HHS_PASS220_GENESIS_C4_ZERO_SUM_GATE_V1_HPP
#define HHS_PASS220_GENESIS_C4_ZERO_SUM_GATE_V1_HPP
/* Additive exact rational specialization of the HARMONICODE C4 gate.
 * Irrational/algebraic K must remain typed symbolic HARMONICODE input,
 * not approximated as a host floating point value.
 * No canonical mutation or independent Hash72/Hash216 receipt authority.
 */
#include <array>
#include <cstddef>
#include <boost/multiprecision/cpp_int.hpp>
#include <boost/rational.hpp>

namespace hhs::rosetta::c4 {
using Integer = boost::multiprecision::cpp_int;
using Rational = boost::rational<Integer>;

struct Complex final {
    Rational real{}, imag{};
};
inline Complex add(const Complex& x, const Complex& y) {
    return {x.real+y.real,x.imag+y.imag};
}
inline Complex sub(const Complex& x, const Complex& y) {
    return {x.real-y.real,x.imag-y.imag};
}
inline Complex multiply(const Complex& x, const Complex& y) {
    return {x.real*y.real-x.imag*y.imag,x.real*y.imag+x.imag*y.real};
}
inline Complex scalar(const Rational& x) { return {x,Rational(0)}; }
inline bool equal(const Complex& x, const Complex& y) {
    return x.real==y.real && x.imag==y.imag;
}
inline Complex square(const Complex& x) { return multiply(x,x); }
inline Complex fourth(const Complex& x) { return square(square(x)); }
inline Complex rotate_i(const Complex& x) { return {-x.imag,x.real}; }

struct Bus final {
    Rational x{}, y{}, b_squared{}, c_squared{}, K{};
};
struct Witness final {
    bool domain_defined{};
    bool radial_binding{};
    bool annihilation_zero{};
    bool sextic_zero{};
    std::array<bool,4> quartic_zero{};
    std::array<bool,4> unsquared_zero{};
    std::array<bool,4> original_chain_zero{};
    std::array<bool,4> admitted{};
    Rational s{}, P{}, R{}, sextic_residual{};
    Complex compatibility_lhs{};
};

/* K^2*(x^2+y^2)=(x^2-y^2)^2 and K carries the positive-radial sign.
 * This exact rational check requires no host sqrt or float arithmetic.
 */
inline bool radial_constraint(const Bus& b) {
    const Rational radius2=b.x*b.x+b.y*b.y;
    const Rational delta=b.x*b.x-b.y*b.y;
    if (radius2<=Rational(0)) return false;
    if (b.K*b.K*radius2!=delta*delta) return false;
    return delta==Rational(0) ? b.K==Rational(0) :
           (delta>Rational(0) ? b.K>Rational(0) : b.K<Rational(0));
}
inline Rational sextic_residual(const Bus& b) {
    const Rational s=b.c_squared-b.b_squared;
    const Rational p=b.x*b.y;
    const Rational u=s*s*s+Rational(2)*b.b_squared*s*s-
                     b.b_squared*s-(p+Rational(1))*b.K;
    return u*u-Rational(4)*b.b_squared*b.b_squared*
                (b.b_squared*s*s+b.K*s);
}

/* C4: seed a, i*a, -a, -i*a. Retain all four phase identities even
 * when the k and k+2 candidates have identical a^2 projections.
 */
inline Witness evaluate(const Bus& b, const Complex& seed_a) {
    Witness w{};
    w.s=b.c_squared-b.b_squared;
    w.P=b.x*b.y;
    w.domain_defined=w.s!=Rational(0) && w.P!=Rational(0) &&
                      (b.x*b.x+b.y*b.y)!=Rational(0);
    if (!w.domain_defined) return w;
    w.radial_binding=radial_constraint(b);
    if (!w.radial_binding) return w;
    w.R=b.b_squared+b.K/w.s;
    // i^3=-i and (i-i^3)*(i+i^3)=0 exactly.
    const Complex imag{Rational(0),Rational(1)};
    const Complex imag3=multiply(square(imag),imag);
    w.annihilation_zero=equal(
        multiply(sub(imag,imag3),add(imag,imag3)),scalar(Rational(0)));
    w.sextic_residual=sextic_residual(b);
    w.sextic_zero=w.sextic_residual==Rational(0);
    const Rational U=w.s*w.s*w.s+Rational(2)*b.b_squared*w.s*w.s-
                      b.b_squared*w.s-(w.P+Rational(1))*b.K;
    w.compatibility_lhs=scalar(U);
    Complex a=seed_a;
    for (std::size_t k=0;k<4;++k) {
        const Complex a2=square(a), a4=square(a2);
        w.quartic_zero[k]=equal(a4,scalar(w.R));
        w.unsquared_zero[k]=equal(w.compatibility_lhs,
                                 multiply(scalar(Rational(2)*b.b_squared*w.s),a2));
        // Check original chain without squaring away phase information.
        const Complex first=sub(a4,scalar(b.b_squared));
        const Complex second=sub(scalar(b.c_squared*b.c_squared),
                                 square(add(scalar(b.b_squared),a2)));
        w.original_chain_zero[k]=
            equal(first,scalar(b.K/w.s)) &&
            equal(multiply(scalar(w.P),first),second);
        w.admitted[k]=w.annihilation_zero && w.sextic_zero &&
                      w.quartic_zero[k] && w.unsquared_zero[k] &&
                      w.original_chain_zero[k];
        a=rotate_i(a);
    }
    return w;
}
}
#endif
