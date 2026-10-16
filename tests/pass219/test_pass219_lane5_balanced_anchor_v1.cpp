#include "hhs_pass219_lane5_balanced_anchor_v1.hpp"
#include <cassert>
int main() {
  using namespace hhs::pass219;
  const auto valid = balanced_anchor_witness();
  assert(balanced_anchor_verified(valid));
  auto corrupted = valid;
  corrupted.balanced_twice[1] = 16;
  assert(!balanced_anchor_verified(corrupted));
  corrupted = valid;
  corrupted.displacement[0] = 2;
  assert(!balanced_anchor_verified(corrupted));
  corrupted = valid;
  corrupted.gate_column = 3;
  assert(!balanced_anchor_verified(corrupted));
  return 0;
}
