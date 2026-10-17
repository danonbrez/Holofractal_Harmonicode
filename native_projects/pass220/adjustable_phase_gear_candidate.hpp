#pragma once
// Pass 220: pure candidate geometry for Lane 5. No VM81 state mutation,
// no Hash72 or Hash216 minting, and no alternate admission authority.
#include <array>
#include <cstdint>
#include <stdexcept>
#include <string>

namespace hhs::pass220 {
using Matrix4 = std::array<std::array<std::int64_t,4>,4>;
inline constexpr Matrix4 kDurer{{
    {{16,2,3,13}}, {{5,11,10,8}}, {{9,7,6,12}}, {{4,14,15,1}}
}};
inline constexpr Matrix4 kFibonacciLucas{{
    {{1,2,3,5}}, {{2,4,6,10}}, {{3,6,9,15}}, {{4,7,11,18}}
}};
struct GearCandidate {
    std::int64_t angle; // reference -180, adjustable at ingress
    std::int64_t quantization{60};
    Matrix4 reference_addresses{kDurer};
    bool admitted{false};
    bool phase_written{false};
};
inline constexpr Matrix4 swap_inner_columns(const Matrix4& m) {
    Matrix4 out=m;
    for(std::size_t i=0;i<4;++i) {
        out[i][1]=m[i][2]; out[i][2]=m[i][1];
    }
    return out;
}
inline constexpr Matrix4 covariant(const Matrix4& a,const Matrix4& b) {
    Matrix4 r{};
    for(std::size_t i=0;i<4;++i)
        for(std::size_t j=0;j<4;++j)
            for(std::size_t k=0;k<4;++k)
                r[i][j]+=a[i][k]*b[k][j];
    return r;
}
// Candidate-only source metadata: byte-identity of all inputs and ordering
// must be passed to the inherited RNA C++ cell wall for canonical admission.
inline GearCandidate prepare_candidate(std::int64_t angle) {
    return GearCandidate{angle};
}
struct PhasePayload { std::int64_t phase; std::uint64_t write_count; };
inline constexpr PhasePayload hnan_bypass(PhasePayload original) {
    return original; // gain 1; no phase write
}
static_assert(swap_inner_columns(swap_inner_columns(kDurer))==kDurer);
static_assert(covariant(kFibonacciLucas,swap_inner_columns(kDurer))[0][0]==73);
static_assert(covariant(kFibonacciLucas,swap_inner_columns(kDurer))[3][3]==258);
static_assert(hnan_bypass({7,9}).write_count==9);
} // namespace hhs::pass220
