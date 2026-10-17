#pragma once
// Pass 220: pure candidate geometry for Lane 5. No VM81 state mutation,
// no Hash72 or Hash216 minting, and no alternate admission authority.
#include <array>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

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
// An address-bearing projection into the INHERITED 81 x 64 = 5184 graph.
// This is NOT an independent store or a serialized canonical VM81 state.
struct Lane5GraphCandidate {
    GearCandidate gear;
    std::array<std::uint16_t, 16> linear5184{};
    std::array<std::string, 16> ordered_bigint_digits{};
    std::string parent_hash216; // existing admitted lineage, read-only
    bool native_cell_wall_checked{false};
    bool signed_environment_admitted{false};
    bool canonical_hash216_minted{false};
};
inline Lane5GraphCandidate project_existing_graph(
    GearCandidate gear,
    const std::array<std::uint16_t,16>& addresses,
    const std::array<std::string,16>& exact_digits,
    const std::string& admitted_parent_hash216) {
    if (admitted_parent_hash216.size()!=216)
        throw std::invalid_argument("inherited Hash216 lineage must be 216 symbols");
    for (auto cell : addresses)
        if (cell>=5184)
            throw std::invalid_argument("5184-address out of range");
    for (const auto& digits : exact_digits) {
        if (digits.empty()) throw std::invalid_argument("missing BigInt digits");
        std::size_t start=digits[0]=='-' ? 1U : 0U;
        if (start==digits.size()) throw std::invalid_argument("invalid BigInt digits");
        for (std::size_t i=start;i<digits.size();++i)
            if (digits[i]<'0' || digits[i]>'9')
                throw std::invalid_argument("nondecimal BigInt digits");
    }
    return {gear,addresses,exact_digits,admitted_parent_hash216};
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
