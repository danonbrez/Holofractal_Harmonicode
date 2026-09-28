import HHS.Mathlib.Native
import HHS.Mathlib.OrderRat
import HHS.Mathlib.Algebra.Native
import HHS.Mathlib.Algebra.Universal
import HHS.Mathlib.Rat.Equivalence
import HHS.Mathlib.Rat.Congruence
import HHS.Alignment.ReciprocalTensor

namespace HHS

/-- Root marker proving the native HHS Lean library and Mathlib compatibility slices are loaded. -/
def nativeMathlibFoundationLoaded : Bool := true

theorem nativeMathlibFoundationLoaded_eq_true :
    nativeMathlibFoundationLoaded = true := by
  rfl

end HHS
