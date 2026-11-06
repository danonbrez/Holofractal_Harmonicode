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


// Ordered, address-bound proof input for inherited Hash216 CHANGE material.
// This is NOT a hash, receipt, signature, or canonical mutation operation.
struct BalancedAnchorProofCellV1 {
  std::uint8_t row_one_based;
  std::uint8_t column_one_based;
  std::int64_t pricing_operand;
  std::int64_t ladder_operand;
  std::int64_t numerator;
  std::int64_t denominator;
};
constexpr std::array<BalancedAnchorProofCellV1, 4>
balanced_anchor_proof_cells() noexcept {
  std::array<BalancedAnchorProofCellV1, 4> result{};
  constexpr auto witness = balanced_anchor_witness();
  for (std::uint8_t row = 0; row < 4; ++row) {
    result[row] = {static_cast<std::uint8_t>(row + 1), 4,
                   witness.pricing[row], witness.ladder[row],
                   witness.balanced_twice[row], 2};
  }
  return result;
}
constexpr bool balanced_anchor_proof_cells_verified(
    const std::array<BalancedAnchorProofCellV1, 4>& cells) noexcept {
  if (!balanced_anchor_verified(balanced_anchor_witness())) return false;
  for (std::uint8_t row = 0; row < 4; ++row) {
    const auto& c = cells[row];
    if (c.row_one_based != row + 1 || c.column_one_based != 4 ||
        c.denominator != 2 || c.pricing_operand != pricing_anchor[row] ||
        c.ladder_operand != ladder_anchor[row] ||
        c.numerator != c.pricing_operand + c.ladder_operand) return false;
  }
  return true;
}
static_assert(balanced_anchor_proof_cells_verified(balanced_anchor_proof_cells()),
              "Ordered closure cell address and operand witness must be retained");

static_assert(balanced_anchor_verified(balanced_anchor_witness()),
              "Pass219 balanced anchor witness must close exactly");

// Canonical integer fields are suitable as proof witness material ONLY.
// Caller must bind source identity, address, order, theorem/dependency identities,
// parent/child receipts and signed environment through inherited Hash216 admission.
} // namespace hhs::pass219
#endif
