import HHS.Mathlib.Rat.Congruence

namespace HHS.Mathlib.Rat.Value

open HHS.Mathlib.OrderRat
open HHS.Mathlib.Rat.Equivalence
open HHS.Mathlib.Rat.Congruence

/-- I053 cross-product equivalence packaged as a Lean Setoid. -/
def exactRatSetoid : Setoid ExactRat where
  r := ExactRat.eqv
  iseqv := {
    refl := fun a => eqv_refl a
    symm := fun h => eqv_symm h
    trans := fun h₁ h₂ => eqv_trans h₁ h₂
  }

/-- Rational-value layer. Stored pair identity is intentionally not the
identity of this quotient type. -/
abbrev ExactRatValue := Quotient exactRatSetoid

namespace ExactRatValue

def ofPair (q : ExactRat) : ExactRatValue :=
  Quotient.mk exactRatSetoid q

theorem ofPair_eq_of_eqv {a b : ExactRat}
    (h : a.eqv b) :
    ofPair a = ofPair b :=
  Quotient.sound h

theorem ofPair_eq_iff_eqv (a b : ExactRat) :
    ofPair a = ofPair b ↔ a.eqv b := by
  constructor
  · intro h
    change exactRatSetoid.r a b
    exact Quotient.exact h
  · intro h
    exact Quotient.sound h

/-- Negation lifted through the quotient using I053 congruence. -/
def neg (q : ExactRatValue) : ExactRatValue :=
  Quotient.liftOn q
    (fun a => ofPair (negExactRat a))
    (fun _ _ h => Quotient.sound (eqv_neg_congr h))

/-- Addition lifted through the quotient using I054 binary congruence. -/
def add (x y : ExactRatValue) : ExactRatValue :=
  Quotient.liftOn₂ x y
    (fun a b => ofPair (addExactRat a b))
    (fun _ _ _ _ ha hb => Quotient.sound (eqv_add_congr ha hb))

/-- Multiplication lifted through the quotient using I054 binary congruence. -/
def mul (x y : ExactRatValue) : ExactRatValue :=
  Quotient.liftOn₂ x y
    (fun a b => ofPair (mulExactRat a b))
    (fun _ _ _ _ ha hb => Quotient.sound (eqv_mul_congr ha hb))

instance : Neg ExactRatValue := ⟨neg⟩
instance : Add ExactRatValue := ⟨add⟩
instance : Mul ExactRatValue := ⟨mul⟩

@[simp] theorem neg_ofPair (a : ExactRat) :
    neg (ofPair a) = ofPair (negExactRat a) := by
  rfl

@[simp] theorem add_ofPair (a b : ExactRat) :
    add (ofPair a) (ofPair b) = ofPair (addExactRat a b) := by
  rfl

@[simp] theorem mul_ofPair (a b : ExactRat) :
    mul (ofPair a) (ofPair b) = ofPair (mulExactRat a b) := by
  rfl

end ExactRatValue

/-- Provenance-bearing object retains the exact unreduced input pair alongside
its quotient value. This layer is deliberately not quotiented. -/
structure ExactRatProvenance where
  pair : ExactRat
  value : ExactRatValue
  valueFromPair : value = ExactRatValue.ofPair pair

def ExactRatProvenance.ofPair (q : ExactRat) : ExactRatProvenance :=
  {
    pair := q
    value := ExactRatValue.ofPair q
    valueFromPair := rfl
  }

/-- Concrete witness that quotient value equality and stored pair identity are
different notions. -/
def half12 : ExactRat :=
  {
    numerator := 1
    denominator := 2
    denominatorPos := by decide
  }

def half24 : ExactRat :=
  {
    numerator := 2
    denominator := 4
    denominatorPos := by decide
  }

theorem half12_eqv_half24 :
    half12.eqv half24 := by
  rfl

theorem half_pair_objects_distinct :
    half12 ≠ half24 := by
  intro h
  have hn := congrArg ExactRat.numerator h
  change (1 : Int) = 2 at hn
  exact (by decide : (1 : Int) ≠ 2) hn

theorem half_values_equal :
    ExactRatValue.ofPair half12 = ExactRatValue.ofPair half24 :=
  ExactRatValue.ofPair_eq_of_eqv half12_eqv_half24

theorem half_provenance_objects_distinct :
    ExactRatProvenance.ofPair half12 ≠ ExactRatProvenance.ofPair half24 := by
  intro h
  have hp := congrArg ExactRatProvenance.pair h
  exact half_pair_objects_distinct hp

theorem half_provenance_values_equal :
    (ExactRatProvenance.ofPair half12).value =
      (ExactRatProvenance.ofPair half24).value :=
  half_values_equal

structure ExactRatValueStatus where
  quotientConstructed : Bool
  negLifted : Bool
  addLifted : Bool
  mulLifted : Bool
  provenancePreservedSeparately : Bool
  quotientRepresentativeRecoverable : Bool
  genericHHSCommutationAuthorized : Bool
  runtimeArithmeticChanged : Bool
deriving Repr, BEq, DecidableEq

def valueStatus : ExactRatValueStatus :=
  {
    quotientConstructed := true
    negLifted := true
    addLifted := true
    mulLifted := true
    provenancePreservedSeparately := true
    quotientRepresentativeRecoverable := false
    genericHHSCommutationAuthorized := false
    runtimeArithmeticChanged := false
  }

theorem quotient_value_layer_constructed :
    valueStatus.quotientConstructed = true := by
  rfl

theorem provenance_retained_outside_quotient :
    valueStatus.provenancePreservedSeparately = true := by
  rfl

theorem quotient_does_not_claim_representative_recovery :
    valueStatus.quotientRepresentativeRecoverable = false := by
  rfl

theorem value_layer_does_not_authorize_generic_hhs_commutation :
    valueStatus.genericHHSCommutationAuthorized = false := by
  rfl

theorem value_layer_does_not_change_runtime_arithmetic :
    valueStatus.runtimeArithmeticChanged = false := by
  rfl

end HHS.Mathlib.Rat.Value
