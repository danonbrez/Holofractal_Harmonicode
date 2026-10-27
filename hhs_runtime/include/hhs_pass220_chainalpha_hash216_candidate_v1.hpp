#pragma once
// Pass 220 ChainAlpha: candidate-only exact readout witness.
// This header does NOT verify Lean, mint Hash72/Hash216, or admit VM81 state.
// Sector values are expected evidence from ChainAlpha.lean, not independently
// derived by this C++ mirror. Kernel checking must supply the proof status.
#include <array>
#include <cstdint>

namespace hhs::lane5::chainalpha {
enum class ProofGate : std::uint8_t {
  source_only = 0, kernel_verified = 1, rejected = 2
};
struct Sector final {
  std::int8_t x;
  std::int8_t y;
  std::uint32_t multiplicity;
  std::uint32_t squared_weight;
};
inline constexpr std::array<Sector, 4> expected_sectors{{
    {+1, +1, 79U, 1U},
    {+1, -1, 48U, 2U},
    {-1, +1, 42U, 3U},
    {-1, -1, 3U, 6U}
}};
struct Candidate final {
  std::array<Sector, 4> sectors;
  std::uint32_t products;
  std::uint32_t commutators;
  std::uint32_t records;
  std::uint32_t readout_denominator;
  std::uint32_t read_links;
  std::uint32_t unread_links;
  std::uint32_t center_dimension;
  std::uint32_t far_dimension;
  ProofGate proof_gate;
};
// Exact, overflow-safe for the four bounded supplied sectors.
constexpr bool structural_consistency(const Candidate& c) noexcept {
  if (c.products != 169U || c.commutators != 3U ||
      c.records != 172U || c.readout_denominator != 31104U ||
      c.read_links != 2U || c.unread_links != 1U ||
      c.center_dimension != 3U || c.far_dimension != 2U) return false;
  std::uint32_t total = 0;
  for (std::size_t i = 0; i < expected_sectors.size(); ++i) {
    const auto& a = c.sectors[i];
    const auto& e = expected_sectors[i];
    if (a.x != e.x || a.y != e.y ||
        a.multiplicity != e.multiplicity ||
        a.squared_weight != e.squared_weight) return false;
    total += a.multiplicity;
  }
  return total == c.records &&
         c.products + c.commutators == c.records &&
         (24U * 36U * 36U) == c.readout_denominator;
}
constexpr Candidate supplied_candidate() noexcept {
  return {expected_sectors, 169U, 3U, 172U, 31104U, 2U, 1U, 3U, 2U,
          ProofGate::source_only};
}
static_assert(structural_consistency(supplied_candidate()));
static_assert(supplied_candidate().proof_gate == ProofGate::source_only);
// The proof gate is never inferred from matching numerals. A kernel-verification
// receipt must be verified independently and bound to exact source bytes.
} // namespace hhs::lane5::chainalpha
