-- Exact finite address lemmas; Genesis-derived nesting is a separate constructor theorem.
namespace HHS.Hash72OrderedFactorization
def rows : Nat := 4 * (9 + 9)
def count : Nat := rows * rows
theorem rows_eq : rows = 72 := by decide
theorem count_eq : count = 5184 := by decide
theorem spinor_factorization : 16 * (18 * 18) = 5184 := by decide
theorem byte_block_factorization : 81 * 8 * 8 = 5184 := by decide
def row (n i j : Nat) : Nat := n*i+j
def column (n i j : Nat) : Nat := n*j+i
theorem transpose_address (n i j : Nat) : column n i j = row n j i := rfl
theorem row_div (n i j : Nat) (hn : 0 < n) (hj : j < n) :
    (row n i j) / n = i := by
  simp [row, Nat.mul_add_div hn, Nat.div_eq_of_lt hj]
theorem row_mod (n i j : Nat) (hn : 0 < n) (hj : j < n) :
    (row n i j) % n = j := by
  simp [row, Nat.mul_add_mod, Nat.mod_eq_of_lt hj]
end HHS.Hash72OrderedFactorization
