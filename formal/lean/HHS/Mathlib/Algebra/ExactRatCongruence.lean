import HHS.Mathlib.Algebra.Universal

namespace HHS.Mathlib.Algebra.ExactRatCongruence

open HHS.Mathlib.OrderRat

/--
Lean-level exact rational addition matching the I049 native C++ formula.
No normalization or floating-point projection occurs.
-/
def ratAdd (a b : ExactRat) : ExactRat where
  numerator :=
    a.numerator * Int.ofNat b.denominator +
    b.numerator * Int.ofNat a.denominator
  denominator := a.denominator * b.denominator
  denominatorPos := Nat.mul_pos a.denominatorPos b.denominatorPos

/-- Exact additive inverse preserving the positive denominator. -/
def ratNeg (a : ExactRat) : ExactRat where
  numerator := -a.numerator
  denominator := a.denominator
  denominatorPos := a.denominatorPos

/-- Exact subtraction is ordered addition of the reciprocal additive phase. -/
def ratSub (a b : ExactRat) : ExactRat :=
  ratAdd a (ratNeg b)

/--
Lean-level exact rational multiplication matching the I049 native C++ formula.
-/
def ratMul (a b : ExactRat) : ExactRat where
  numerator := a.numerator * b.numerator
  denominator := a.denominator * b.denominator
  denominatorPos := Nat.mul_pos a.denominatorPos b.denominatorPos

/--
Carrier-local four-factor re-association used only inside ExactRat proofs.
This is an explicit Int proof, not a generic HHS rewrite permission.
-/
private theorem int_mul4_cross (a b c d : Int) :
    (a * b) * (c * d) = (a * c) * (b * d) := by
  calc
    (a * b) * (c * d) = a * (b * (c * d)) :=
      Int.mul_assoc a b (c * d)
    _ = a * (c * (b * d)) := by
      rw [Int.mul_left_comm b c d]
    _ = (a * c) * (b * d) :=
      (Int.mul_assoc a c (b * d)).symm

/--
Carrier-local four-factor rotation. The one integer commutation step is
explicitly proved inside this private helper and is not exported as a HHS law.
-/
private theorem int_mul4_rotate (a b c d : Int) :
    (a * b) * (c * d) = (a * d) * (b * c) := by
  calc
    (a * b) * (c * d) = (a * b) * (d * c) := by
      rw [Int.mul_comm c d]
    _ = (a * d) * (b * c) :=
      int_mul4_cross a b d c

private theorem int_mul4_rotate_reverse (a b c d : Int) :
    (a * b) * (c * d) = (a * d) * (c * b) := by
  calc
    (a * b) * (c * d) = (a * d) * (b * c) :=
      int_mul4_rotate a b c d
    _ = (a * d) * (c * b) := by
      rw [Int.mul_comm b c]

/--
Multiplication respects I049 cross-product equivalence universally.
-/
theorem ratMul_congr
    {a a' b b' : ExactRat}
    (ha : a.eqv a')
    (hb : b.eqv b') :
    (ratMul a b).eqv (ratMul a' b') := by
  unfold ExactRat.eqv at ha hb ⊢
  simp only [ratMul, Int.natCast_mul]
  calc
    (a.numerator * b.numerator) *
        (Int.ofNat a'.denominator * Int.ofNat b'.denominator)
      =
        (a.numerator * Int.ofNat a'.denominator) *
        (b.numerator * Int.ofNat b'.denominator) :=
      int_mul4_cross
        a.numerator b.numerator
        (Int.ofNat a'.denominator) (Int.ofNat b'.denominator)
    _ =
        (a'.numerator * Int.ofNat a.denominator) *
        (b'.numerator * Int.ofNat b.denominator) := by
      rw [ha, hb]
    _ =
        (a'.numerator * b'.numerator) *
        (Int.ofNat a.denominator * Int.ofNat b.denominator) :=
      int_mul4_cross
        a'.numerator (Int.ofNat a.denominator)
        b'.numerator (Int.ofNat b.denominator)

/-- Additive inverse respects exact rational equivalence universally. -/
theorem ratNeg_congr
    {a a' : ExactRat}
    (ha : a.eqv a') :
    (ratNeg a).eqv (ratNeg a') := by
  unfold ExactRat.eqv at ha ⊢
  simp only [ratNeg]
  calc
    -a.numerator * Int.ofNat a'.denominator
      = -(a.numerator * Int.ofNat a'.denominator) :=
        Int.neg_mul a.numerator (Int.ofNat a'.denominator)
    _ = -(a'.numerator * Int.ofNat a.denominator) :=
      congrArg (fun x : Int => -x) ha
    _ = -a'.numerator * Int.ofNat a.denominator :=
      (Int.neg_mul a'.numerator (Int.ofNat a.denominator)).symm

/--
Addition respects I049 cross-product equivalence universally.

The proof keeps the native numerator formula ordered and uses only private,
carrier-local Int re-association/rotation witnesses to align the cross terms.
-/
theorem ratAdd_congr
    {a a' b b' : ExactRat}
    (ha : a.eqv a')
    (hb : b.eqv b') :
    (ratAdd a b).eqv (ratAdd a' b') := by
  unfold ExactRat.eqv at ha hb ⊢
  simp only [ratAdd, Int.natCast_mul]
  calc
    (a.numerator * Int.ofNat b.denominator +
        b.numerator * Int.ofNat a.denominator) *
        (Int.ofNat a'.denominator * Int.ofNat b'.denominator)
      =
        (a.numerator * Int.ofNat a'.denominator) *
          (Int.ofNat b.denominator * Int.ofNat b'.denominator) +
        (b.numerator * Int.ofNat b'.denominator) *
          (Int.ofNat a.denominator * Int.ofNat a'.denominator) := by
      rw [Int.add_mul]
      rw [int_mul4_cross
        a.numerator (Int.ofNat b.denominator)
        (Int.ofNat a'.denominator) (Int.ofNat b'.denominator)]
      rw [int_mul4_rotate
        b.numerator (Int.ofNat a.denominator)
        (Int.ofNat a'.denominator) (Int.ofNat b'.denominator)]
    _ =
        (a'.numerator * Int.ofNat a.denominator) *
          (Int.ofNat b.denominator * Int.ofNat b'.denominator) +
        (b'.numerator * Int.ofNat b.denominator) *
          (Int.ofNat a.denominator * Int.ofNat a'.denominator) := by
      rw [ha, hb]
    _ =
        (a'.numerator * Int.ofNat b'.denominator) *
          (Int.ofNat a.denominator * Int.ofNat b.denominator) +
        (b'.numerator * Int.ofNat a'.denominator) *
          (Int.ofNat a.denominator * Int.ofNat b.denominator) := by
      rw [int_mul4_rotate
        a'.numerator (Int.ofNat a.denominator)
        (Int.ofNat b.denominator) (Int.ofNat b'.denominator)]
      rw [int_mul4_rotate_reverse
        b'.numerator (Int.ofNat b.denominator)
        (Int.ofNat a.denominator) (Int.ofNat a'.denominator)]
    _ =
        (a'.numerator * Int.ofNat b'.denominator +
          b'.numerator * Int.ofNat a'.denominator) *
        (Int.ofNat a.denominator * Int.ofNat b.denominator) :=
      (Int.add_mul
        (a'.numerator * Int.ofNat b'.denominator)
        (b'.numerator * Int.ofNat a'.denominator)
        (Int.ofNat a.denominator * Int.ofNat b.denominator)).symm

/-- Ordered subtraction respects exact rational equivalence universally. -/
theorem ratSub_congr
    {a a' b b' : ExactRat}
    (ha : a.eqv a')
    (hb : b.eqv b') :
    (ratSub a b).eqv (ratSub a' b') := by
  simpa [ratSub] using ratAdd_congr ha (ratNeg_congr hb)

/--
I053 proves operation congruence but does not yet claim quotient-level ring
closure. Equivalence transitivity and quotient construction remain separate
obligations.
-/
structure CongruenceStatus where
  addCongruent : Bool
  negCongruent : Bool
  subCongruent : Bool
  mulCongruent : Bool
  quotientRingClosed : Bool
  genericHHSCommutationAuthorized : Bool
deriving Repr, BEq, DecidableEq

def congruenceStatus : CongruenceStatus :=
  {
    addCongruent := true
    negCongruent := true
    subCongruent := true
    mulCongruent := true
    quotientRingClosed := false
    genericHHSCommutationAuthorized := false
  }

theorem operation_congruence_closed :
    congruenceStatus.addCongruent = true ∧
    congruenceStatus.negCongruent = true ∧
    congruenceStatus.subCongruent = true ∧
    congruenceStatus.mulCongruent = true := by
  exact ⟨rfl, rfl, rfl, rfl⟩

theorem quotient_ring_not_yet_claimed :
    congruenceStatus.quotientRingClosed = false := by
  rfl

theorem generic_hhs_commutation_remains_forbidden :
    congruenceStatus.genericHHSCommutationAuthorized = false := by
  rfl

end HHS.Mathlib.Algebra.ExactRatCongruence
