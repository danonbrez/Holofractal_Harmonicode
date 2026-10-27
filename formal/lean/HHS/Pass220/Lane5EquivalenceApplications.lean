import HHS.Mathlib.Rat.Congruence

namespace HHS.Pass220.Lane5EquivalenceApplications
open HHS.Mathlib.OrderRat
open HHS.Mathlib.Rat.Equivalence
open HHS.Mathlib.Rat.Congruence

theorem eqv_refl_application (a : ExactRat) : a.eqv a :=
  HHS.Mathlib.Rat.Equivalence.eqv_refl a

theorem eqv_symm_application {a b : ExactRat} (h : a.eqv b) : b.eqv a :=
  HHS.Mathlib.Rat.Equivalence.eqv_symm h

theorem eqv_trans_application {a b c : ExactRat} (hab : a.eqv b) (hbc : b.eqv c) :
    a.eqv c :=
  HHS.Mathlib.Rat.Equivalence.eqv_trans hab hbc

theorem eqv_neg_congr_application {a b : ExactRat} (h : a.eqv b) :
    (negExactRat a).eqv (negExactRat b) :=
  HHS.Mathlib.Rat.Equivalence.eqv_neg_congr h

theorem eqv_add_congr_application {a a' b b' : ExactRat}
    (ha : a.eqv a') (hb : b.eqv b') :
    (addExactRat a b).eqv (addExactRat a' b') :=
  HHS.Mathlib.Rat.Congruence.eqv_add_congr ha hb

theorem eqv_mul_congr_application {a a' b b' : ExactRat}
    (ha : a.eqv a') (hb : b.eqv b') :
    (mulExactRat a b).eqv (mulExactRat a' b') :=
  HHS.Mathlib.Rat.Congruence.eqv_mul_congr ha hb

end HHS.Pass220.Lane5EquivalenceApplications
