namespace HHS.Hash72GenesisPhase
def phaseDim : Nat := 4 * (9 + 9)
def phaseCells : Nat := phaseDim * phaseDim
theorem dimension72 : phaseDim = 72 := by decide
theorem phaseCells5184 : phaseCells = 5184 := by decide
theorem factorization : 16 * (18 * 18) = 5184 := by decide
def phase (n : Nat) : Fin 72 := ⟨n % 72, Nat.mod_lt _ (by decide)⟩
def product (a b : Fin 72) : Fin 72 := phase (a.val+b.val)
def inverse (a : Fin 72) : Fin 72 := phase (72-a.val)
theorem reciprocal (a : Fin 72) : product a (inverse a) = phase 0 := by
  apply Fin.ext
  simp only [product, inverse, phase, Fin.val_mk]
  have ha : a.val ≤ 72 := Nat.le_of_lt a.isLt
  rw [Nat.add_sub_of_le ha]
  simp
end HHS.Hash72GenesisPhase
