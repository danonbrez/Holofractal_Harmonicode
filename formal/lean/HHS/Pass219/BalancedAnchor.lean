/- Exact rational projection of the Pass 219 fourth-column closure gate.
   This proof does not scalarize native HNAN operands or mint Hash216 receipts. -/
import Mathlib

namespace HHS.Pass219.BalancedAnchor

def pricing : Fin 4 → ℤ
  | ⟨0, _⟩ => 5
  | ⟨1, _⟩ => 10
  | ⟨2, _⟩ => 15
  | _ => 20

def ladder : Fin 4 → ℤ
  | ⟨0, _⟩ => 4
  | ⟨1, _⟩ => 7
  | ⟨2, _⟩ => 11
  | _ => 18

def balanced (i : Fin 4) : ℚ :=
  ((pricing i : ℚ) + (ladder i : ℚ)) / 2

theorem midpoint (i : Fin 4) :
    2 * balanced i = (pricing i : ℚ) + (ladder i : ℚ) := by
  simp [balanced]
  ring

theorem balanced_values :
    (balanced 0, balanced 1, balanced 2, balanced 3) =
      ((9 : ℚ)/2, (17 : ℚ)/2, 13, 19) := by
  norm_num [balanced, pricing, ladder]

theorem anchor_sums :
    (pricing 0 + pricing 1 + pricing 2 + pricing 3 = 50) ∧
    (ladder 0 + ladder 1 + ladder 2 + ladder 3 = 40) := by
  norm_num [pricing, ladder]

theorem balanced_total :
    balanced 0 + balanced 1 + balanced 2 + balanced 3 = 45 := by
  norm_num [balanced, pricing, ladder]

theorem displacement :
    (pricing 0 - ladder 0 = 1) ∧
    (pricing 1 - ladder 1 = 3) ∧
    (pricing 2 - ladder 2 = 4) ∧
    (pricing 3 - ladder 3 = 2) := by
  norm_num [pricing, ladder]

theorem eight_closure :
    (2:ℤ)^3 = 8 ∧ 3 + 5 = 8 ∧ 3^2 - 1 = 8 := by
  norm_num

theorem lo_shu_outer_center :
    (4+9+2+3+7+8+1+6 : ℤ) = 40 ∧
    (40+5 : ℤ) = 45 := by
  norm_num

end HHS.Pass219.BalancedAnchor
