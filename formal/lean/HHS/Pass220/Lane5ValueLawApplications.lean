import HHS.Mathlib.Rat.ValueLaws

namespace HHS.Pass220.Lane5ValueLawApplications

open HHS.Mathlib.OrderRat
open HHS.Mathlib.Rat.Equivalence
open HHS.Mathlib.Rat.Congruence
open HHS.Mathlib.Rat.Value
open HHS.Mathlib.Rat.ValueLaws

theorem add_zero_pair_eqv_application (a : ExactRat) :
    (addExactRat a zeroPair).eqv a :=
  HHS.Mathlib.Rat.ValueLaws.add_zero_pair_eqv a

theorem zero_add_pair_eqv_application (a : ExactRat) :
    (addExactRat zeroPair a).eqv a :=
  HHS.Mathlib.Rat.ValueLaws.zero_add_pair_eqv a

theorem mul_one_pair_eqv_application (a : ExactRat) :
    (mulExactRat a onePair).eqv a :=
  HHS.Mathlib.Rat.ValueLaws.mul_one_pair_eqv a

theorem one_mul_pair_eqv_application (a : ExactRat) :
    (mulExactRat onePair a).eqv a :=
  HHS.Mathlib.Rat.ValueLaws.one_mul_pair_eqv a

theorem add_neg_pair_eqv_zero_application (a : ExactRat) :
    (addExactRat a (negExactRat a)).eqv zeroPair :=
  HHS.Mathlib.Rat.ValueLaws.add_neg_pair_eqv_zero a

theorem neg_add_pair_eqv_zero_application (a : ExactRat) :
    (addExactRat (negExactRat a) a).eqv zeroPair :=
  HHS.Mathlib.Rat.ValueLaws.neg_add_pair_eqv_zero a

theorem value_add_zero_application (x : ExactRatValue) :
    x + 0 = x :=
  HHS.Mathlib.Rat.ValueLaws.value_add_zero x

theorem value_zero_add_application (x : ExactRatValue) :
    0 + x = x :=
  HHS.Mathlib.Rat.ValueLaws.value_zero_add x

theorem value_mul_one_application (x : ExactRatValue) :
    x * 1 = x :=
  HHS.Mathlib.Rat.ValueLaws.value_mul_one x

theorem value_one_mul_application (x : ExactRatValue) :
    1 * x = x :=
  HHS.Mathlib.Rat.ValueLaws.value_one_mul x

theorem value_add_neg_application (x : ExactRatValue) :
    x + (-x) = 0 :=
  HHS.Mathlib.Rat.ValueLaws.value_add_neg x

theorem value_neg_add_application (x : ExactRatValue) :
    (-x) + x = 0 :=
  HHS.Mathlib.Rat.ValueLaws.value_neg_add x

end HHS.Pass220.Lane5ValueLawApplications
