import HHS.Mathlib.Native

namespace HHS

/-- Root marker proving the HHS native Lean library is materialized as a real module tree. -/
def nativeMathlibFoundationLoaded : Bool := true

theorem nativeMathlibFoundationLoaded_eq_true :
    nativeMathlibFoundationLoaded = true := by
  rfl

end HHS
