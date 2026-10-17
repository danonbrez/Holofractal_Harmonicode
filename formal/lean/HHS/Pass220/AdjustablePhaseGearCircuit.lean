import Std

namespace HHS.Pass220.AdjustablePhaseGearCircuit

/-- Ordered 4×4 address geometry. The reference angle is not a constant law. -/
def durer : Array (Array Nat) := #[
  #[16,2,3,13], #[5,11,10,8], #[9,7,6,12], #[4,14,15,1]
]

/-- The forward chiral permutation swaps only columns 1 and 2 (zero-based). -/
def swap23 (row : Array Nat) : Array Nat :=
  #[row[0]!, row[2]!, row[1]!, row[3]!]

theorem swap23_involutive (a b c d : Nat) :
    swap23 (swap23 #[a,b,c,d]) = #[a,b,c,d] := by
  rfl

/-- An angular phase-gear coordinate remains part of the typed input. -/
structure GearInput where
  angle : Int
  divisor : Int := 60
  addresses : Array (Array Nat) := durer
deriving Repr, BEq

def reference : GearInput := { angle := -180 }

theorem reference_angle : reference.angle = -180 := by rfl
theorem alternate_angle_distinct :
    ({ angle := 180 } : GearInput).angle ≠ reference.angle := by decide

/-- HNAN dead-site bypass: gain exactly one, original phase and
    write counter unchanged; no scalar division is performed. -/
structure Phase where
  payload : Int
  writes : Nat
deriving Repr, BEq

def bypass (p : Phase) : Phase := p

theorem bypass_preserves_phase (p : Phase) : (bypass p).payload = p.payload := by
  rfl
theorem bypass_no_write (p : Phase) : (bypass p).writes = p.writes := by
  rfl
theorem bypass_gain : (1 : Int) = 1 := by rfl

/-- A witness of symbolic matrix/angle selection is not VM81 admission. -/
structure Candidate where
  gear : GearInput
  sourceTag : String
  kernelAdmitted : Bool := false
deriving Repr, BEq

theorem candidate_default_not_admitted (g : GearInput) (tag : String) :
    ({ gear := g, sourceTag := tag } : Candidate).kernelAdmitted = false := by
  rfl

end HHS.Pass220.AdjustablePhaseGearCircuit
