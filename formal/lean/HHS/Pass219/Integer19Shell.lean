/- Final integer 19-shell, independent of the superseded rational scaffold. -/
import HHS.Pass219.BalancedAnchor
namespace HHS.Pass219.Integer19Shell
def cell : Fin 4 → Fin 4 → Nat
  | ⟨0,_⟩, ⟨0,_⟩ => 1
  | ⟨0,_⟩, ⟨1,_⟩ => 2
  | ⟨0,_⟩, ⟨2,_⟩ => 3
  | ⟨0,_⟩, _ => 5
  | ⟨1,_⟩, ⟨0,_⟩ => 2
  | ⟨1,_⟩, ⟨1,_⟩ => 4
  | ⟨1,_⟩, ⟨2,_⟩ => 6
  | ⟨1,_⟩, _ => 10
  | ⟨2,_⟩, ⟨0,_⟩ => 3
  | ⟨2,_⟩, ⟨1,_⟩ => 6
  | ⟨2,_⟩, ⟨2,_⟩ => 9
  | ⟨2,_⟩, _ => 15
  | _, ⟨0,_⟩ => 4
  | _, ⟨1,_⟩ => 7
  | _, ⟨2,_⟩ => 11
  | _, _ => 19

theorem closure (r : Fin 4) :
    cell r 0 + cell r 1 = cell r 2 ∧
    3 * cell r 0 + cell r 1 = cell r 3 := by
  have h : ∀ j : Fin 4, cell j 0 + cell j 1 = cell j 2 ∧
                 3 * cell j 0 + cell j 1 = cell j 3 := by decide
  exact h r

theorem sums :
    (cell 0 0 + cell 1 0 + cell 2 0 + cell 3 0 = 10) ∧
    (cell 0 1 + cell 1 1 + cell 2 1 + cell 3 1 = 19) ∧
    (cell 0 2 + cell 1 2 + cell 2 2 + cell 3 2 = 29) ∧
    (cell 0 3 + cell 1 3 + cell 2 3 + cell 3 3 = 49) := by
  decide

theorem primeHinge : 2 * cell 3 3 = 18 + 20 := by decide
theorem mass : (11:Nat)+22+33+41=107 := by decide
end HHS.Pass219.Integer19Shell
