import HHS.Mathlib.Rat.ValueAlgebra

/-!
Pass 220 Lane 5: proof-kernel application witnesses for existing I060
normalization declarations. These are exact-rational theorem applications,
not HNAN AB/BA commutation or canonical VM81 mutation authority.
-/

namespace HHS.Pass220.Lane5NormalizationApplications

open HHS.Mathlib.OrderRat
open HHS.Mathlib.Rat.Equivalence
open HHS.Mathlib.Rat.Value
open HHS.Mathlib.Rat.ValueAlgebra

theorem pair_add_assoc_application (a b c : ExactRat) :
    (addExactRat (addExactRat a b) c).eqv
      (addExactRat a (addExactRat b c)) :=
  pair_add_assoc_eqv a b c

theorem pair_mul_assoc_application (a b c : ExactRat) :
    (mulExactRat (mulExactRat a b) c).eqv
      (mulExactRat a (mulExactRat b c)) :=
  pair_mul_assoc_eqv a b c

theorem pair_left_distrib_application (a b c : ExactRat) :
    (mulExactRat a (addExactRat b c)).eqv
      (addExactRat (mulExactRat a b) (mulExactRat a c)) :=
  pair_left_distrib_eqv a b c

theorem pair_right_distrib_application (a b c : ExactRat) :
    (mulExactRat (addExactRat a b) c).eqv
      (addExactRat (mulExactRat a c) (mulExactRat b c)) :=
  pair_right_distrib_eqv a b c

theorem value_add_assoc_application (x y z : ExactRatValue) :
    ExactRatValue.add (ExactRatValue.add x y) z =
      ExactRatValue.add x (ExactRatValue.add y z) :=
  value_add_assoc x y z

theorem value_mul_assoc_application (x y z : ExactRatValue) :
    ExactRatValue.mul (ExactRatValue.mul x y) z =
      ExactRatValue.mul x (ExactRatValue.mul y z) :=
  value_mul_assoc x y z

theorem value_left_distrib_application (x y z : ExactRatValue) :
    ExactRatValue.mul x (ExactRatValue.add y z) =
      ExactRatValue.add (ExactRatValue.mul x y) (ExactRatValue.mul x z) :=
  value_left_distrib x y z

theorem value_right_distrib_application (x y z : ExactRatValue) :
    ExactRatValue.mul (ExactRatValue.add x y) z =
      ExactRatValue.add (ExactRatValue.mul x z) (ExactRatValue.mul y z) :=
  value_right_distrib x y z

end HHS.Pass220.Lane5NormalizationApplications
