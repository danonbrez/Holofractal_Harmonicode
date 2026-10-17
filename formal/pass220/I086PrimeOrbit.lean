/- Pass 220 I086: reference projection proofs. Native HNAN and Lane 5 authority remain inherited.
   These theorems prove only finite toroidal indexing, modular recurrence, and
   deterministic replay of a supplied transition; they do NOT certify native admission. -/
namespace HHS.Pass220.I086
def Cell := Fin 81
def PrimeCoordinate := Fin 81 → Nat
def LifeGrid := Cell → Bool
def row (i : Cell) : Fin 9 := ⟨i.val / 9, by omega⟩
def col (i : Cell) : Fin 9 := ⟨i.val % 9, by omega⟩
def address (r c : Fin 9) : Cell := ⟨r.val * 9 + c.val, by omega⟩
theorem address_row_col (i : Cell) : address (row i) (col i) = i := by
  apply Fin.ext
  simp [address, row, col]
  omega
def shift (i : Fin 9) (d : Fin 9) : Fin 9 := ⟨(i.val + d.val) % 9, Nat.mod_lt _ (by omega)⟩
def neighbor (i : Cell) (dr dc : Fin 9) : Cell :=
  address (shift (row i) dr) (shift (col i) dc)
def evolve (f : LifeGrid → LifeGrid) (n : Nat) (s : LifeGrid) : LifeGrid :=
  Nat.rec s (fun _ state => f state) n
theorem evolve_zero (f : LifeGrid → LifeGrid) (s : LifeGrid) :
    evolve f 0 s = s := by rfl
theorem evolve_succ (f : LifeGrid → LifeGrid) (n : Nat) (s : LifeGrid) :
    evolve f (n+1) s = f (evolve f n s) := by rfl
def residue (p t : Nat) : Nat := t % p
theorem residue_period (p t : Nat) (hp : 0 < p) :
    residue p (t+p) = residue p t := by
  simp [residue, Nat.add_mod]
theorem deterministic_replay (f : LifeGrid → LifeGrid) (n : Nat)
    (a b : LifeGrid) (h : a = b) : evolve f n a = evolve f n b := by
  rw [h]
end HHS.Pass220.I086
