import HHS.Mathlib.OrderRat
import HHS.Mathlib.Algebra.Universal

namespace HHS.Mathlib.Rat.Equivalence

open HHS.Mathlib.OrderRat

/-- The positive denominator of every admitted ExactRat casts to a nonzero Int. -/
theorem denominator_cast_ne_zero (q : ExactRat) :
    Int.ofNat q.denominator ≠ 0 := by
  exact Int.ofNat_ne_zero.mpr (Nat.ne_of_gt q.denominatorPos)

/-- Local conventional-Int reordering proof used only inside ExactRat
cross-product equivalence. This is not exported as a generic HHS rewrite law. -/
private theorem three_factor_swap_right (a b c : Int) :
    (a * b) * c = (a * c) * b := by
  rw [Int.mul_assoc, Int.mul_comm b c, ← Int.mul_assoc]

theorem eqv_refl (a : ExactRat) :
    a.eqv a :=
  ExactRat.eqv_refl a

theorem eqv_symm {a b : ExactRat}
    (h : a.eqv b) :
    b.eqv a := by
  simpa [ExactRat.eqv] using h.symm

/-- Cross-product equivalence is transitive because the positive middle
denominator is nonzero and can be cancelled after an explicitly proved local
integer-factor reordering. -/
theorem eqv_trans {a b c : ExactRat}
    (hab : a.eqv b)
    (hbc : b.eqv c) :
    a.eqv c := by
  unfold ExactRat.eqv at hab hbc ⊢
  apply Int.eq_of_mul_eq_mul_right (denominator_cast_ne_zero b)
  calc
    (a.numerator * Int.ofNat c.denominator) * Int.ofNat b.denominator
        = (a.numerator * Int.ofNat b.denominator) * Int.ofNat c.denominator := by
            exact three_factor_swap_right
              a.numerator
              (Int.ofNat c.denominator)
              (Int.ofNat b.denominator)
    _ = (b.numerator * Int.ofNat a.denominator) * Int.ofNat c.denominator := by
          rw [hab]
    _ = (b.numerator * Int.ofNat c.denominator) * Int.ofNat a.denominator := by
          exact three_factor_swap_right
            b.numerator
            (Int.ofNat a.denominator)
            (Int.ofNat c.denominator)
    _ = (c.numerator * Int.ofNat b.denominator) * Int.ofNat a.denominator := by
          rw [hbc]
    _ = (c.numerator * Int.ofNat a.denominator) * Int.ofNat b.denominator := by
          exact three_factor_swap_right
            c.numerator
            (Int.ofNat b.denominator)
            (Int.ofNat a.denominator)

/-- Negation preserves the unreduced denominator and reverses only the exact
integer numerator. -/
def negExactRat (q : ExactRat) : ExactRat :=
  {
    numerator := -q.numerator
    denominator := q.denominator
    denominatorPos := q.denominatorPos
  }

theorem eqv_neg_congr {a b : ExactRat}
    (h : a.eqv b) :
    (negExactRat a).eqv (negExactRat b) := by
  unfold ExactRat.eqv at h ⊢
  change (-a.numerator) * Int.ofNat b.denominator =
    (-b.numerator) * Int.ofNat a.denominator
  rw [Int.neg_mul, Int.neg_mul]
  exact congrArg Neg.neg h

/-- Native proof bundle establishing that ExactRat.eqv is an equivalence
relation over the unreduced positive-denominator representation. -/
structure ExactRatEquivalenceProof where
  refl : ∀ a : ExactRat, a.eqv a
  symm : ∀ {a b : ExactRat}, a.eqv b → b.eqv a
  trans : ∀ {a b c : ExactRat}, a.eqv b → b.eqv c → a.eqv c

def exactRatEquivalenceProof : ExactRatEquivalenceProof :=
  {
    refl := eqv_refl
    symm := eqv_symm
    trans := eqv_trans
  }

theorem exact_rat_equivalence_witness_exists :
    Nonempty ExactRatEquivalenceProof :=
  ⟨exactRatEquivalenceProof⟩

structure ExactRatCongruenceStatus where
  negCongruenceUniversal : Bool
  addCongruenceUniversal : Bool
  mulCongruenceUniversal : Bool
  quotientConstructed : Bool
  pairIdentityCollapsedIntoEqv : Bool
  genericHHSCommutationAuthorized : Bool
deriving Repr, BEq, DecidableEq

def congruenceStatus : ExactRatCongruenceStatus :=
  {
    negCongruenceUniversal := true
    addCongruenceUniversal := false
    mulCongruenceUniversal := false
    quotientConstructed := false
    pairIdentityCollapsedIntoEqv := false
    genericHHSCommutationAuthorized := false
  }

theorem neg_congruence_closed :
    congruenceStatus.negCongruenceUniversal = true := by
  rfl

theorem add_congruence_not_yet_closed :
    congruenceStatus.addCongruenceUniversal = false := by
  rfl

theorem mul_congruence_not_yet_closed :
    congruenceStatus.mulCongruenceUniversal = false := by
  rfl

theorem quotient_not_yet_constructed :
    congruenceStatus.quotientConstructed = false := by
  rfl

theorem unreduced_pair_identity_remains_distinct :
    congruenceStatus.pairIdentityCollapsedIntoEqv = false := by
  rfl

theorem local_int_reorder_does_not_authorize_generic_hhs_commutation :
    congruenceStatus.genericHHSCommutationAuthorized = false := by
  rfl

end HHS.Mathlib.Rat.Equivalence
