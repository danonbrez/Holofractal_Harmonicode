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

// Full native circuit: four 4x4 blocks in the exact 8x8 placement.
// T1 upper-left; T2 upper-right; T4 lower-left; T3 lower-right.
// The eight outer computational vectors are independently addressable
// phase-gear inputs. Four choices at eight slots yield 4^8=65536
// potential vector configurations, distinct from the 64 cell positions.
using OuterPhaseVectors = std::array<std::int64_t, 8>;
using Circuit8 = std::array<std::array<std::int64_t, 8>, 8>;
inline constexpr std::size_t kCircuitCells = 64;
inline constexpr std::size_t kPhaseConfigurations = 65536;
enum class CircuitBlock : std::uint8_t { T1=0, T2=1, T3=2, T4=3 };
inline constexpr std::size_t circuit_row(CircuitBlock b,std::size_t local) {
    return ((b==CircuitBlock::T3 || b==CircuitBlock::T4)?4U:0U)+(local/4U);
}
inline constexpr std::size_t circuit_col(CircuitBlock b,std::size_t local) {
    return ((b==CircuitBlock::T2 || b==CircuitBlock::T3)?4U:0U)+(local%4U);
}
inline constexpr std::size_t circuit_index(CircuitBlock b,std::size_t local) {
    return circuit_row(b,local)*8U+circuit_col(b,local);
}
inline constexpr Circuit8 compose8(const Matrix4& t1,const Matrix4& t2,
                                  const Matrix4& t3,const Matrix4& t4) {
    Circuit8 out{};
    for(std::size_t i=0;i<16;++i) {
        out[circuit_row(CircuitBlock::T1,i)][circuit_col(CircuitBlock::T1,i)]=t1[i/4][i%4];
        out[circuit_row(CircuitBlock::T2,i)][circuit_col(CircuitBlock::T2,i)]=t2[i/4][i%4];
        out[circuit_row(CircuitBlock::T3,i)][circuit_col(CircuitBlock::T3,i)]=t3[i/4][i%4];
        out[circuit_row(CircuitBlock::T4,i)][circuit_col(CircuitBlock::T4,i)]=t4[i/4][i%4];
    }
    return out;
}
struct FullCircuitCandidate {
    OuterPhaseVectors phase_vectors{};
    Circuit8 cells{};
    std::array<std::uint16_t,64> inherited_linear5184{};
    std::array<std::string,64> exact_bigint_digits{};
    std::string parent_hash216;
    bool candidate_only{true};
};
inline FullCircuitCandidate project_full_circuit(
    const OuterPhaseVectors& phases, const Circuit8& cells,
    const std::array<std::uint16_t,64>& addresses,
    const std::array<std::string,64>& digits, const std::string& parent) {
    if(parent.size()!=216) throw std::invalid_argument("invalid parent Hash216 length");
    for(std::size_t i=0;i<64;++i) {
        if(addresses[i]>=5184) throw std::invalid_argument("outside VM81 5184 geometry");
        const auto& s=digits[i];
        if(s.empty()) throw std::invalid_argument("empty BigInt serialization");
        std::size_t k=(s[0]=='-')?1U:0U;
        if(k==s.size()) throw std::invalid_argument("invalid BigInt");
        for(;k<s.size();++k)
            if(s[k]<'0'||s[k]>'9') throw std::invalid_argument("noninteger BigInt");
    }
    return {phases,cells,addresses,digits,parent,true};
}
static_assert(kPhaseConfigurations==4*4*4*4*4*4*4*4);
static_assert(circuit_index(CircuitBlock::T1,0)==0);
static_assert(circuit_index(CircuitBlock::T2,0)==4);
static_assert(circuit_index(CircuitBlock::T4,0)==32);
static_assert(circuit_index(CircuitBlock::T3,15)==63);

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
inline constexpr bool matrix_equal(const Matrix4& a, const Matrix4& b) {
    for(std::size_t row=0;row<4;++row)
        for(std::size_t col=0;col<4;++col)
            if(a[row][col]!=b[row][col]) return false;
    return true;
}
static_assert(matrix_equal(swap_inner_columns(swap_inner_columns(kDurer)),kDurer));
static_assert(covariant(kFibonacciLucas,swap_inner_columns(kDurer))[0][0]==73);
static_assert(covariant(kFibonacciLucas,swap_inner_columns(kDurer))[3][3]==258);
static_assert(hnan_bypass({7,9}).write_count==9);
} // namespace hhs::pass220
