import HHS.Mathlib.OrderRat

namespace HHS.Mathlib.Algebra.Native

inductive Carrier
  | nat
  | int
  | exactRat
deriving Repr, BEq, DecidableEq

inductive Law
  | addAssoc
  | addIdentity
  | mulAssoc
  | mulIdentity
  | leftDistrib
  | rightDistrib
  | addInverse
deriving Repr, BEq, DecidableEq

/-- Exact runtime certificate for one algebraic-law check.
This records runtime evidence only; it is not promoted to a universal proof. -/
structure LawReceipt where
  carrier : Carrier
  law : Law
  exact : Bool
  python1Executed : Bool
  operandOrderPreserved : Bool
  hostFloatUsed : Bool
  hostPrimitiveArithmeticUsed : Bool
deriving Repr, BEq, DecidableEq

def LawReceipt.admitted (receipt : LawReceipt) : Prop :=
  receipt.exact = true ∧
  receipt.python1Executed = true ∧
  receipt.operandOrderPreserved = true ∧
  receipt.hostFloatUsed = false ∧
  receipt.hostPrimitiveArithmeticUsed = false

theorem admitted_requires_exact
    (receipt : LawReceipt)
    (h : receipt.admitted) :
    receipt.exact = true :=
  h.1

theorem admitted_requires_python1
    (receipt : LawReceipt)
    (h : receipt.admitted) :
    receipt.python1Executed = true :=
  h.2.1

theorem admitted_preserves_operand_order
    (receipt : LawReceipt)
    (h : receipt.admitted) :
    receipt.operandOrderPreserved = true :=
  h.2.2.1

theorem admitted_forbids_host_float
    (receipt : LawReceipt)
    (h : receipt.admitted) :
    receipt.hostFloatUsed = false :=
  h.2.2.2.1

theorem admitted_forbids_host_primitive_arithmetic
    (receipt : LawReceipt)
    (h : receipt.admitted) :
    receipt.hostPrimitiveArithmeticUsed = false :=
  h.2.2.2.2

structure AlgebraDescriptor where
  name : String
  carrier : Carrier
  laws : List Law
  universalProofClosed : Bool
deriving Repr, BEq, DecidableEq

def natSemiring : AlgebraDescriptor :=
  {
    name := "NatSemiring"
    carrier := .nat
    laws := [
      .addAssoc, .addIdentity, .mulAssoc, .mulIdentity,
      .leftDistrib, .rightDistrib
    ]
    universalProofClosed := false
  }

def intRing : AlgebraDescriptor :=
  {
    name := "IntRing"
    carrier := .int
    laws := [
      .addAssoc, .addIdentity, .mulAssoc, .mulIdentity,
      .leftDistrib, .rightDistrib, .addInverse
    ]
    universalProofClosed := false
  }

def exactRatRing : AlgebraDescriptor :=
  {
    name := "ExactRatRing"
    carrier := .exactRat
    laws := [
      .addAssoc, .addIdentity, .mulAssoc, .mulIdentity,
      .leftDistrib, .rightDistrib, .addInverse
    ]
    universalProofClosed := false
  }

theorem i050_does_not_claim_universal_nat_semiring_closure :
    natSemiring.universalProofClosed = false := by
  rfl

theorem i050_does_not_claim_universal_int_ring_closure :
    intRing.universalProofClosed = false := by
  rfl

theorem i050_does_not_claim_universal_rat_ring_closure :
    exactRatRing.universalProofClosed = false := by
  rfl

/-- Ordered evaluation is a compatibility projection, not permission to commute
arbitrary HHS-native operators. -/
def implicitCommutationAuthorized : Bool := false

theorem implicit_commutation_remains_forbidden :
    implicitCommutationAuthorized = false := by
  rfl

end HHS.Mathlib.Algebra.Native
