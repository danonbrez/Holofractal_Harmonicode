import HHS.Pass220.Module26TickSeedBoundary

/-!
I087 conditional normal-form proof. The native ordered reconciliation
implementation must discharge both premises before this theorem applies.
No assumption here is a canonical VM81/Hash72/Hash216 admission receipt.
-/

namespace HHS.Pass220.I087

universe u
variable {State : Type u}

/-- The native normalizer maps candidates to globally admissible states.
    This is a proof obligation of the runtime, not an axiom of HHS. -/
theorem idempotent_of_global_admission
    (normalize : State → State)
    (Admissible : State → Prop)
    (hProduces : ∀ s, Admissible (normalize s))
    (hFixed : ∀ s, Admissible s → normalize s = s)
    (s : State) :
    normalize (normalize s) = normalize s := by
  exact hFixed (normalize s) (hProduces s)

/-- Once admitted, a state remains a fixed point without erasing its type,
    address, or provenance: State is the complete typed state. -/
theorem admissible_is_fixed
    (normalize : State → State)
    (Admissible : State → Prop)
    (hFixed : ∀ s, Admissible s → normalize s = s)
    (s : State) (h : Admissible s) :
    normalize s = s :=
  hFixed s h

end HHS.Pass220.I087
