#include "../../hhs_runtime/include/hhs_pass219_lane5_integer_19_shell_v1.hpp"
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
  const auto cells = balanced_anchor_proof_cells();
  assert(balanced_anchor_proof_cells_verified(cells));
  auto altered_cells = cells;
  altered_cells[0].column_one_based = 3;
  assert(!balanced_anchor_proof_cells_verified(altered_cells));
  altered_cells = cells;
  altered_cells[1].pricing_operand = 7;
  assert(!balanced_anchor_proof_cells_verified(altered_cells));
  altered_cells = cells;
  altered_cells[3].numerator = 37;
  assert(!balanced_anchor_proof_cells_verified(altered_cells));
  assert(integer_19_shell_closes(integer_19_shell));
  auto corrupted = integer_19_shell;
  corrupted[3][3] = 18;
  assert(!integer_19_shell_closes(corrupted));
  corrupted = integer_19_shell;
  corrupted[3][1] = 8;
  assert(!integer_19_shell_closes(corrupted));
  return 0;
}
