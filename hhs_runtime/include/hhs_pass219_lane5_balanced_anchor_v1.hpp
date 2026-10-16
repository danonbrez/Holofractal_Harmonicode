#ifndef HHS_PASS219_LANE5_BALANCED_ANCHOR_V1_HPP
#define HHS_PASS219_LANE5_BALANCED_ANCHOR_V1_HPP
// Pass 219 Lane 5: exact, non-mutating fourth-column witness constructor.
// No VM81 mutation, Hash72 minting, Hash216 hashing, signing, or persistence.
#include <array>
#include <cstdint>

namespace hhs::pass219 {
struct BalancedAnchorWitnessV1 {
  std::array<std::int64_t, 4> pricing;
  std::array<std::int64_t, 4> ladder;
  std::array<std::int64_t, 4> balanced_twice;
  std::array<std::int64_t, 4> displacement;
  std::int64_t pricing_sum;
  std::int64_t ladder_sum;
  std::int64_t balanced_sum_twice;
  std::uint32_t gate_column;
  std::uint32_t denominator;
};

// Fixed-width, exact input; source positions and ordered endpoints are preserved.
constexpr std::array<std::array<std::int64_t, 3>, 4> input_channels{{
  {{1, 2, 3}}, {{2, 4, 6}}, {{3, 6, 9}}, {{4, 7, 11}}
}};
constexpr std::array<std::int64_t, 4> pricing_anchor{{5, 10, 15, 20}};
constexpr std::array<std::int64_t, 4> ladder_anchor{{4, 7, 11, 18}};

constexpr BalancedAnchorWitnessV1 balanced_anchor_witness() noexcept {
  BalancedAnchorWitnessV1 result{{}, {}, {}, {}, 0, 0, 0, 4, 2};
  for (std::uint32_t i = 0; i < 4; ++i) {
    const auto p = pricing_anchor[i], l = ladder_anchor[i];
    result.pricing[i] = p;
    result.ladder[i] = l;
    result.balanced_twice[i] = p + l;
    result.displacement[i] = p - l;
    result.pricing_sum += p;
    result.ladder_sum += l;
    result.balanced_sum_twice += p + l;
  }
  return result;
}

constexpr bool balanced_anchor_verified(const BalancedAnchorWitnessV1& w) noexcept {
  if (w.gate_column != 4 || w.denominator != 2 ||
      w.pricing_sum != 50 || w.ladder_sum != 40 ||
      w.balanced_sum_twice != 90) return false;
  constexpr std::array<std::int64_t, 4> expected_twice{{9,17,26,38}};
  constexpr std::array<std::int64_t, 4> expected_delta{{1,3,4,2}};
  for (std::uint32_t i = 0; i < 4; ++i) {
    if (w.pricing[i] != pricing_anchor[i] ||
        w.ladder[i] != ladder_anchor[i] ||
        w.balanced_twice[i] != expected_twice[i] ||
        w.displacement[i] != expected_delta[i] ||
        w.balanced_twice[i] != w.pricing[i] + w.ladder[i] ||
        w.displacement[i] != w.pricing[i] - w.ladder[i] ||
        input_channels[i][0] + input_channels[i][1] != input_channels[i][2])
      return false;
  }
  return (w.displacement[0] + w.displacement[2] == 5 &&
          w.displacement[1] + w.displacement[3] == 5);
}

static_assert(balanced_anchor_verified(balanced_anchor_witness()),
              "Pass219 balanced anchor witness must close exactly");

// Canonical integer fields are suitable as proof witness material ONLY.
// Caller must bind source identity, address, order, theorem/dependency identities,
// parent/child receipts and signed environment through inherited Hash216 admission.
} // namespace hhs::pass219
#endif
