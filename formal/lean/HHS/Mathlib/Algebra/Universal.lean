import HHS.Mathlib.Algebra.Native

namespace HHS.Mathlib.Algebra.Universal

/--
Universal semiring-law bundle for the native Nat compatibility carrier.

The fields preserve the written operand order. No commutativity theorem is
part of this interface.
-/
structure NatSemiringLaws where
  addAssoc : ∀ a b c : Nat, (a + b) + c = a + (b + c)
  addLeftIdentity : ∀ a : Nat, 0 + a = a
  addRightIdentity : ∀ a : Nat, a + 0 = a
  mulAssoc : ∀ a b c : Nat, (a * b) * c = a * (b * c)
  mulLeftIdentity : ∀ a : Nat, 1 * a = a
  mulRightIdentity : ∀ a : Nat, a * 1 = a
  leftDistrib : ∀ a b c : Nat, a * (b + c) = a * b + a * c
  rightDistrib : ∀ a b c : Nat, (a + b) * c = a * c + b * c

def natSemiringLaws : NatSemiringLaws where
  addAssoc := fun a b c => Nat.add_assoc a b c
  addLeftIdentity := fun a => Nat.zero_add a
  addRightIdentity := fun a => Nat.add_zero a
  mulAssoc := fun a b c => Nat.mul_assoc a b c
  mulLeftIdentity := fun a => Nat.one_mul a
  mulRightIdentity := fun a => Nat.mul_one a
  leftDistrib := fun a b c => Nat.left_distrib a b c
  rightDistrib := fun a b c => Nat.right_distrib a b c

theorem nat_add_assoc (a b c : Nat) :
    (a + b) + c = a + (b + c) :=
  natSemiringLaws.addAssoc a b c

theorem nat_add_left_identity (a : Nat) :
    0 + a = a :=
  natSemiringLaws.addLeftIdentity a

theorem nat_add_right_identity (a : Nat) :
    a + 0 = a :=
  natSemiringLaws.addRightIdentity a

theorem nat_mul_assoc (a b c : Nat) :
    (a * b) * c = a * (b * c) :=
  natSemiringLaws.mulAssoc a b c

theorem nat_mul_left_identity (a : Nat) :
    1 * a = a :=
  natSemiringLaws.mulLeftIdentity a

theorem nat_mul_right_identity (a : Nat) :
    a * 1 = a :=
  natSemiringLaws.mulRightIdentity a

theorem nat_left_distrib (a b c : Nat) :
    a * (b + c) = a * b + a * c :=
  natSemiringLaws.leftDistrib a b c

theorem nat_right_distrib (a b c : Nat) :
    (a + b) * c = a * c + b * c :=
  natSemiringLaws.rightDistrib a b c

/--
Universal ring-law bundle for the native Int compatibility carrier.

As with Nat, these are ordered propositions. The bundle exports no generic
commutativity law.
-/
structure IntRingLaws where
  addAssoc : ∀ a b c : Int, (a + b) + c = a + (b + c)
  addLeftIdentity : ∀ a : Int, 0 + a = a
  addRightIdentity : ∀ a : Int, a + 0 = a
  addLeftInverse : ∀ a : Int, -a + a = 0
  addRightInverse : ∀ a : Int, a + -a = 0
  mulAssoc : ∀ a b c : Int, (a * b) * c = a * (b * c)
  mulLeftIdentity : ∀ a : Int, 1 * a = a
  mulRightIdentity : ∀ a : Int, a * 1 = a
  leftDistrib : ∀ a b c : Int, a * (b + c) = a * b + a * c
  rightDistrib : ∀ a b c : Int, (a + b) * c = a * c + b * c

def intRingLaws : IntRingLaws where
  addAssoc := fun a b c => Int.add_assoc a b c
  addLeftIdentity := fun a => Int.zero_add a
  addRightIdentity := fun a => Int.add_zero a
  addLeftInverse := fun a => Int.add_left_neg a
  addRightInverse := fun a => Int.add_right_neg a
  mulAssoc := fun a b c => Int.mul_assoc a b c
  mulLeftIdentity := fun a => Int.one_mul a
  mulRightIdentity := fun a => Int.mul_one a
  leftDistrib := fun a b c => Int.mul_add a b c
  rightDistrib := fun a b c => Int.add_mul a b c

theorem int_add_assoc (a b c : Int) :
    (a + b) + c = a + (b + c) :=
  intRingLaws.addAssoc a b c

theorem int_add_left_identity (a : Int) :
    0 + a = a :=
  intRingLaws.addLeftIdentity a

theorem int_add_right_identity (a : Int) :
    a + 0 = a :=
  intRingLaws.addRightIdentity a

theorem int_add_left_inverse (a : Int) :
    -a + a = 0 :=
  intRingLaws.addLeftInverse a

theorem int_add_right_inverse (a : Int) :
    a + -a = 0 :=
  intRingLaws.addRightInverse a

theorem int_mul_assoc (a b c : Int) :
    (a * b) * c = a * (b * c) :=
  intRingLaws.mulAssoc a b c

theorem int_mul_left_identity (a : Int) :
    1 * a = a :=
  intRingLaws.mulLeftIdentity a

theorem int_mul_right_identity (a : Int) :
    a * 1 = a :=
  intRingLaws.mulRightIdentity a

theorem int_left_distrib (a b c : Int) :
    a * (b + c) = a * b + a * c :=
  intRingLaws.leftDistrib a b c

theorem int_right_distrib (a b c : Int) :
    (a + b) * c = a * c + b * c :=
  intRingLaws.rightDistrib a b c

/--
I052 promotion state is separate from I050's sampled runtime descriptors.
The historical I050 values remain unchanged.
-/
structure PromotionStatus where
  natSemiringUniversal : Bool
  intRingUniversal : Bool
  exactRatRingUniversal : Bool
  implicitHHSCommutationAuthorized : Bool
deriving Repr, BEq, DecidableEq

def promotionStatus : PromotionStatus :=
  {
    natSemiringUniversal := true
    intRingUniversal := true
    exactRatRingUniversal := false
    implicitHHSCommutationAuthorized := false
  }

theorem nat_semiring_universal_closed :
    promotionStatus.natSemiringUniversal = true := by
  rfl

theorem int_ring_universal_closed :
    promotionStatus.intRingUniversal = true := by
  rfl

theorem exact_rat_universal_not_yet_closed :
    promotionStatus.exactRatRingUniversal = false := by
  rfl

theorem generic_hhs_commutation_still_forbidden :
    promotionStatus.implicitHHSCommutationAuthorized = false := by
  rfl

theorem i050_nat_descriptor_remains_runtime_certificate :
    HHS.Mathlib.Algebra.Native.natSemiring.universalProofClosed = false := by
  rfl

theorem i050_int_descriptor_remains_runtime_certificate :
    HHS.Mathlib.Algebra.Native.intRing.universalProofClosed = false := by
  rfl

end HHS.Mathlib.Algebra.Universal
