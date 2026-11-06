/- Pass219 fourth-column midpoint: exact numerator and denominator proof.
   Nat values are an exact projection only; the ordered native HNAN gate is inherited. -/
import HHS.Pass220.HNANPhase5184

namespace HHS.Pass219.BalancedAnchor

def pricing : Fin 4 → Nat
  | ⟨0, _⟩ => 5
  | ⟨1, _⟩ => 10
  | ⟨2, _⟩ => 15
  | _ => 20

def ladder : Fin 4 → Nat
  | ⟨0, _⟩ => 4
  | ⟨1, _⟩ => 7
  | ⟨2, _⟩ => 11
  | _ => 18

def midpointNumerator (i : Fin 4) : Nat := pricing i + ladder i
def midpointDenominator : Nat := 2

theorem orderedMidpoint (i : Fin 4) :
    midpointDenominator = 2 ∧
    midpointNumerator i = pricing i + ladder i := by
  exact ⟨rfl, rfl⟩

theorem midpointNumerators :
    (midpointNumerator 0, midpointNumerator 1,
     midpointNumerator 2, midpointNumerator 3) = (9,17,26,38) := by
  decide

theorem anchorSums :
    pricing 0 + pricing 1 + pricing 2 + pricing 3 = 50 ∧
    ladder 0 + ladder 1 + ladder 2 + ladder 3 = 40 := by
  decide

theorem midpointSum :
    midpointNumerator 0 + midpointNumerator 1 +
    midpointNumerator 2 + midpointNumerator 3 = 90 := by
  decide

theorem displacementWitness :
    pricing 0 = ladder 0 + 1 ∧
    pricing 1 = ladder 1 + 3 ∧
    pricing 2 = ladder 2 + 4 ∧
    pricing 3 = ladder 3 + 2 := by
  decide

theorem phaseEightValue :
    2^3 = 8 ∧ 3 + 5 = 8 ∧ 3^2 = 8 + 1 := by
  decide

theorem loShuOuterAndCenter :
    4+9+2+3+7+8+1+6 = 40 ∧ 40+5 = 45 := by
  decide

end HHS.Pass219.BalancedAnchor
