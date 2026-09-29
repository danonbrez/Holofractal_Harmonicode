import HHS.Mathlib.Rat.Value

namespace HHS.Mathlib.Rat.ValueLaws

open HHS.Mathlib.OrderRat
open HHS.Mathlib.Rat.Equivalence
open HHS.Mathlib.Rat.Congruence
open HHS.Mathlib.Rat.Value

def zeroPair : ExactRat :=
  {
    numerator := 0
    denominator := 1
    denominatorPos := by decide
  }

def onePair : ExactRat :=
  {
    numerator := 1
    denominator := 1
    denominatorPos := by decide
  }

namespace ExactRatValue

def zeroValue : ExactRatValue :=
  ExactRatValue.ofPair zeroPair

def oneValue : ExactRatValue :=
  ExactRatValue.ofPair onePair

instance : Zero ExactRatValue := ⟨zeroValue⟩
instance : One ExactRatValue := ⟨oneValue⟩

end ExactRatValue

theorem add_zero_pair_eqv (a : ExactRat) :
    (addExactRat a zeroPair).eqv a := by
  simp [addExactRat, ExactRat.eqv, zeroPair]

theorem zero_add_pair_eqv (a : ExactRat) :
    (addExactRat zeroPair a).eqv a := by
  simp [addExactRat, ExactRat.eqv, zeroPair]

theorem mul_one_pair_eqv (a : ExactRat) :
    (mulExactRat a onePair).eqv a := by
  simp [mulExactRat, ExactRat.eqv, onePair]

theorem one_mul_pair_eqv (a : ExactRat) :
    (mulExactRat onePair a).eqv a := by
  simp [mulExactRat, ExactRat.eqv, onePair]

theorem add_neg_pair_eqv_zero (a : ExactRat) :
    (addExactRat a (negExactRat a)).eqv zeroPair := by
  have hnum :
      a.numerator * Int.ofNat a.denominator +
          (-a.numerator) * Int.ofNat a.denominator = 0 := by
    rw [← Int.add_mul, Int.add_right_neg, Int.zero_mul]
  simpa [addExactRat, negExactRat, ExactRat.eqv, zeroPair] using hnum

theorem neg_add_pair_eqv_zero (a : ExactRat) :
    (addExactRat (negExactRat a) a).eqv zeroPair := by
  have hnum :
      (-a.numerator) * Int.ofNat a.denominator +
          a.numerator * Int.ofNat a.denominator = 0 := by
    rw [← Int.add_mul, Int.add_left_neg, Int.zero_mul]
  simpa [addExactRat, negExactRat, ExactRat.eqv, zeroPair] using hnum

theorem value_add_zero (x : ExactRatValue) :
    x + 0 = x := by
  refine Quotient.inductionOn x ?_
  intro a
  change
    ExactRatValue.add (ExactRatValue.ofPair a)
        ExactRatValue.zeroValue =
      ExactRatValue.ofPair a
  unfold ExactRatValue.zeroValue
  rw [ExactRatValue.add_ofPair]
  exact ExactRatValue.ofPair_eq_of_eqv (add_zero_pair_eqv a)

theorem value_zero_add (x : ExactRatValue) :
    0 + x = x := by
  refine Quotient.inductionOn x ?_
  intro a
  change
    ExactRatValue.add ExactRatValue.zeroValue
        (ExactRatValue.ofPair a) =
      ExactRatValue.ofPair a
  unfold ExactRatValue.zeroValue
  rw [ExactRatValue.add_ofPair]
  exact ExactRatValue.ofPair_eq_of_eqv (zero_add_pair_eqv a)

theorem value_mul_one (x : ExactRatValue) :
    x * 1 = x := by
  refine Quotient.inductionOn x ?_
  intro a
  change
    ExactRatValue.mul (ExactRatValue.ofPair a)
        ExactRatValue.oneValue =
      ExactRatValue.ofPair a
  unfold ExactRatValue.oneValue
  rw [ExactRatValue.mul_ofPair]
  exact ExactRatValue.ofPair_eq_of_eqv (mul_one_pair_eqv a)

theorem value_one_mul (x : ExactRatValue) :
    1 * x = x := by
  refine Quotient.inductionOn x ?_
  intro a
  change
    ExactRatValue.mul ExactRatValue.oneValue
        (ExactRatValue.ofPair a) =
      ExactRatValue.ofPair a
  unfold ExactRatValue.oneValue
  rw [ExactRatValue.mul_ofPair]
  exact ExactRatValue.ofPair_eq_of_eqv (one_mul_pair_eqv a)

theorem value_add_neg (x : ExactRatValue) :
    x + (-x) = 0 := by
  refine Quotient.inductionOn x ?_
  intro a
  change
    ExactRatValue.add (ExactRatValue.ofPair a)
        (ExactRatValue.neg (ExactRatValue.ofPair a)) =
      ExactRatValue.zeroValue
  unfold ExactRatValue.zeroValue
  rw [ExactRatValue.neg_ofPair, ExactRatValue.add_ofPair]
  exact ExactRatValue.ofPair_eq_of_eqv (add_neg_pair_eqv_zero a)

theorem value_neg_add (x : ExactRatValue) :
    (-x) + x = 0 := by
  refine Quotient.inductionOn x ?_
  intro a
  change
    ExactRatValue.add
        (ExactRatValue.neg (ExactRatValue.ofPair a))
        (ExactRatValue.ofPair a) =
      ExactRatValue.zeroValue
  unfold ExactRatValue.zeroValue
  rw [ExactRatValue.neg_ofPair, ExactRatValue.add_ofPair]
  exact ExactRatValue.ofPair_eq_of_eqv (neg_add_pair_eqv_zero a)

structure ExactRatValueLawStatus where
  addLeftIdentityUniversal : Bool
  addRightIdentityUniversal : Bool
  mulLeftIdentityUniversal : Bool
  mulRightIdentityUniversal : Bool
  addLeftInverseUniversal : Bool
  addRightInverseUniversal : Bool
  addAssocUniversal : Bool
  mulAssocUniversal : Bool
  leftDistribUniversal : Bool
  rightDistribUniversal : Bool
  provenanceObjectsRewrittenByValueLaws : Bool
  genericHHSCommutationAuthorized : Bool
  runtimeArithmeticChanged : Bool
deriving Repr, BEq, DecidableEq

def lawStatus : ExactRatValueLawStatus :=
  {
    addLeftIdentityUniversal := true
    addRightIdentityUniversal := true
    mulLeftIdentityUniversal := true
    mulRightIdentityUniversal := true
    addLeftInverseUniversal := true
    addRightInverseUniversal := true
    addAssocUniversal := false
    mulAssocUniversal := false
    leftDistribUniversal := false
    rightDistribUniversal := false
    provenanceObjectsRewrittenByValueLaws := false
    genericHHSCommutationAuthorized := false
    runtimeArithmeticChanged := false
  }

theorem identity_and_inverse_nucleus_closed :
    lawStatus.addLeftIdentityUniversal = true ∧
    lawStatus.addRightIdentityUniversal = true ∧
    lawStatus.mulLeftIdentityUniversal = true ∧
    lawStatus.mulRightIdentityUniversal = true ∧
    lawStatus.addLeftInverseUniversal = true ∧
    lawStatus.addRightInverseUniversal = true := by
  decide

theorem associativity_remains_deferred :
    lawStatus.addAssocUniversal = false ∧
    lawStatus.mulAssocUniversal = false := by
  decide

theorem distributivity_remains_deferred :
    lawStatus.leftDistribUniversal = false ∧
    lawStatus.rightDistribUniversal = false := by
  decide

theorem provenance_not_rewritten_by_quotient_laws :
    lawStatus.provenanceObjectsRewrittenByValueLaws = false := by
  rfl

theorem value_laws_do_not_authorize_generic_hhs_commutation :
    lawStatus.genericHHSCommutationAuthorized = false := by
  rfl

theorem value_laws_do_not_change_runtime_arithmetic :
    lawStatus.runtimeArithmeticChanged = false := by
  rfl

end HHS.Mathlib.Rat.ValueLaws
