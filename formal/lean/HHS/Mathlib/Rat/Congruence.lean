import HHS.Mathlib.Rat.Equivalence

namespace HHS.Mathlib.Rat.Congruence

open HHS.Mathlib.OrderRat
open HHS.Mathlib.Rat.Equivalence

/-- Lean proof constructor matching the I049 exact runtime addition formula.
No GCD reduction or scalar collapse is performed. -/
def addExactRat (a b : ExactRat) : ExactRat :=
  {
    numerator :=
      a.numerator * Int.ofNat b.denominator +
      b.numerator * Int.ofNat a.denominator
    denominator := a.denominator * b.denominator
    denominatorPos := Nat.mul_pos a.denominatorPos b.denominatorPos
  }

/-- Lean proof constructor matching the I049 exact runtime multiplication formula.
The unreduced ordered pair is preserved. -/
def mulExactRat (a b : ExactRat) : ExactRat :=
  {
    numerator := a.numerator * b.numerator
    denominator := a.denominator * b.denominator
    denominatorPos := Nat.mul_pos a.denominatorPos b.denominatorPos
  }

/-- Explicit local rearrangement of four conventional Int factors.
This proof is scoped only to ExactRat congruence and is not a generic HHS
commutation authorization. -/
private theorem mul_pair_swap_middle (a b c d : Int) :
    (a * b) * (c * d) = (a * c) * (b * d) := by
  calc
    (a * b) * (c * d) = a * (b * (c * d)) := by
      rw [Int.mul_assoc]
    _ = a * (c * (b * d)) := by
      apply congrArg (fun x : Int => a * x)
      calc
        b * (c * d) = (b * c) * d := by
          rw [← Int.mul_assoc]
        _ = (c * b) * d := by
          rw [Int.mul_comm b c]
        _ = c * (b * d) := by
          rw [Int.mul_assoc]
    _ = (a * c) * (b * d) := by
      rw [← Int.mul_assoc]

/-- Addition respects I053 cross-product equivalence on both arguments. -/
theorem eqv_add_congr {a a' b b' : ExactRat}
    (ha : a.eqv a')
    (hb : b.eqv b') :
    (addExactRat a b).eqv (addExactRat a' b') := by
  unfold ExactRat.eqv at ha hb
  have h₁ :
      (a.numerator * Int.ofNat b.denominator) *
          (Int.ofNat a'.denominator * Int.ofNat b'.denominator) =
        (a'.numerator * Int.ofNat b'.denominator) *
          (Int.ofNat a.denominator * Int.ofNat b.denominator) := by
    calc
      (a.numerator * Int.ofNat b.denominator) *
            (Int.ofNat a'.denominator * Int.ofNat b'.denominator)
          =
        (a.numerator * Int.ofNat a'.denominator) *
            (Int.ofNat b.denominator * Int.ofNat b'.denominator) := by
              exact mul_pair_swap_middle
                a.numerator
                (Int.ofNat b.denominator)
                (Int.ofNat a'.denominator)
                (Int.ofNat b'.denominator)
      _ =
        (a'.numerator * Int.ofNat a.denominator) *
            (Int.ofNat b.denominator * Int.ofNat b'.denominator) := by
              rw [ha]
      _ =
        (a'.numerator * Int.ofNat a.denominator) *
            (Int.ofNat b'.denominator * Int.ofNat b.denominator) := by
              rw [Int.mul_comm (Int.ofNat b.denominator) (Int.ofNat b'.denominator)]
      _ =
        (a'.numerator * Int.ofNat b'.denominator) *
            (Int.ofNat a.denominator * Int.ofNat b.denominator) := by
              exact (mul_pair_swap_middle
                a'.numerator
                (Int.ofNat b'.denominator)
                (Int.ofNat a.denominator)
                (Int.ofNat b.denominator)).symm

  have h₂ :
      (b.numerator * Int.ofNat a.denominator) *
          (Int.ofNat a'.denominator * Int.ofNat b'.denominator) =
        (b'.numerator * Int.ofNat a'.denominator) *
          (Int.ofNat a.denominator * Int.ofNat b.denominator) := by
    calc
      (b.numerator * Int.ofNat a.denominator) *
            (Int.ofNat a'.denominator * Int.ofNat b'.denominator)
          =
        (b.numerator * Int.ofNat a.denominator) *
            (Int.ofNat b'.denominator * Int.ofNat a'.denominator) := by
              rw [Int.mul_comm (Int.ofNat a'.denominator) (Int.ofNat b'.denominator)]
      _ =
        (b.numerator * Int.ofNat b'.denominator) *
            (Int.ofNat a.denominator * Int.ofNat a'.denominator) := by
              exact mul_pair_swap_middle
                b.numerator
                (Int.ofNat a.denominator)
                (Int.ofNat b'.denominator)
                (Int.ofNat a'.denominator)
      _ =
        (b'.numerator * Int.ofNat b.denominator) *
            (Int.ofNat a.denominator * Int.ofNat a'.denominator) := by
              rw [hb]
      _ =
        (b'.numerator * Int.ofNat b.denominator) *
            (Int.ofNat a'.denominator * Int.ofNat a.denominator) := by
              rw [Int.mul_comm (Int.ofNat a.denominator) (Int.ofNat a'.denominator)]
      _ =
        (b'.numerator * Int.ofNat a'.denominator) *
            (Int.ofNat b.denominator * Int.ofNat a.denominator) := by
              exact mul_pair_swap_middle
                b'.numerator
                (Int.ofNat b.denominator)
                (Int.ofNat a'.denominator)
                (Int.ofNat a.denominator)
      _ =
        (b'.numerator * Int.ofNat a'.denominator) *
            (Int.ofNat a.denominator * Int.ofNat b.denominator) := by
              rw [Int.mul_comm (Int.ofNat b.denominator) (Int.ofNat a.denominator)]

  unfold ExactRat.eqv
  simp only [addExactRat, Int.natCast_mul, Int.add_mul]
  calc
    (a.numerator * Int.ofNat b.denominator) *
          (Int.ofNat a'.denominator * Int.ofNat b'.denominator) +
        (b.numerator * Int.ofNat a.denominator) *
          (Int.ofNat a'.denominator * Int.ofNat b'.denominator)
        =
      (a'.numerator * Int.ofNat b'.denominator) *
          (Int.ofNat a.denominator * Int.ofNat b.denominator) +
        (b.numerator * Int.ofNat a.denominator) *
          (Int.ofNat a'.denominator * Int.ofNat b'.denominator) := by
            rw [h₁]
    _ =
      (a'.numerator * Int.ofNat b'.denominator) *
          (Int.ofNat a.denominator * Int.ofNat b.denominator) +
        (b'.numerator * Int.ofNat a'.denominator) *
          (Int.ofNat a.denominator * Int.ofNat b.denominator) := by
            rw [h₂]

/-- Multiplication respects I053 cross-product equivalence on both arguments. -/
theorem eqv_mul_congr {a a' b b' : ExactRat}
    (ha : a.eqv a')
    (hb : b.eqv b') :
    (mulExactRat a b).eqv (mulExactRat a' b') := by
  unfold ExactRat.eqv at ha hb ⊢
  simp only [mulExactRat, Int.natCast_mul]
  calc
    (a.numerator * b.numerator) *
          (Int.ofNat a'.denominator * Int.ofNat b'.denominator)
        =
      (a.numerator * Int.ofNat a'.denominator) *
          (b.numerator * Int.ofNat b'.denominator) := by
            exact mul_pair_swap_middle
              a.numerator
              b.numerator
              (Int.ofNat a'.denominator)
              (Int.ofNat b'.denominator)
    _ =
      (a'.numerator * Int.ofNat a.denominator) *
          (b.numerator * Int.ofNat b'.denominator) := by
            rw [ha]
    _ =
      (a'.numerator * Int.ofNat a.denominator) *
          (b'.numerator * Int.ofNat b.denominator) := by
            rw [hb]
    _ =
      (a'.numerator * b'.numerator) *
          (Int.ofNat a.denominator * Int.ofNat b.denominator) := by
            exact (mul_pair_swap_middle
              a'.numerator
              b'.numerator
              (Int.ofNat a.denominator)
              (Int.ofNat b.denominator)).symm

structure ExactRatBinaryCongruenceProof where
  addCongruence :
    ∀ {a a' b b' : ExactRat},
      a.eqv a' →
      b.eqv b' →
      (addExactRat a b).eqv (addExactRat a' b')
  mulCongruence :
    ∀ {a a' b b' : ExactRat},
      a.eqv a' →
      b.eqv b' →
      (mulExactRat a b).eqv (mulExactRat a' b')

def exactRatBinaryCongruenceProof : ExactRatBinaryCongruenceProof :=
  {
    addCongruence := eqv_add_congr
    mulCongruence := eqv_mul_congr
  }

theorem exact_rat_binary_congruence_witness_exists :
    Nonempty ExactRatBinaryCongruenceProof :=
  ⟨exactRatBinaryCongruenceProof⟩

structure ExactRatOperationStatus where
  negCongruenceUniversal : Bool
  addCongruenceUniversal : Bool
  mulCongruenceUniversal : Bool
  quotientConstructed : Bool
  pairIdentityCollapsedIntoEqv : Bool
  genericHHSCommutationAuthorized : Bool
deriving Repr, BEq, DecidableEq

def operationStatus : ExactRatOperationStatus :=
  {
    negCongruenceUniversal := true
    addCongruenceUniversal := true
    mulCongruenceUniversal := true
    quotientConstructed := false
    pairIdentityCollapsedIntoEqv := false
    genericHHSCommutationAuthorized := false
  }

theorem addition_congruence_closed :
    operationStatus.addCongruenceUniversal = true := by
  rfl

theorem multiplication_congruence_closed :
    operationStatus.mulCongruenceUniversal = true := by
  rfl

theorem quotient_remains_deferred :
    operationStatus.quotientConstructed = false := by
  rfl

theorem pair_identity_remains_unreduced :
    operationStatus.pairIdentityCollapsedIntoEqv = false := by
  rfl

theorem congruence_proofs_do_not_authorize_generic_hhs_commutation :
    operationStatus.genericHHSCommutationAuthorized = false := by
  rfl

end HHS.Mathlib.Rat.Congruence
