import HHS.Pass220.Module194TypedClosure

namespace HHS.Pass220.Module194OrderedProduct

/-!
V170 conditional ordered-product certificate for Module194.

This is an exact proof interface, not a witness mint. The caller must supply
the native-verified direct/reverse product equations for the typed 81-entry
source. This module proves their consequences when the required premises
are present; it does NOT independently derive those premises, discharge
I051.admitted, or claim native VM81 mutation authority.
-/

open HHS.Pass220.Module194TypedClosure

/-- Source and boundary retain different typed identities. -/
structure TypedOperandPair where
  a : Operand
  b : Operand
  aIsLhs : a = lhs
  bIsRhs : b = rhs

theorem typed_pair_not_equal (t : TypedOperandPair) : t.a ≠ t.b := by
  rw [t.aIsLhs, t.bIsRhs]
  exact lhs_ne_rhs

/-- Ordered algebra values are distinguished from their source labels. -/
structure OrderedProductCertificate where
  source : TypedOperandPair
  p4 : Int
  abValue : Int
  baValue : Int
  directEquation : abValue = p4
  mirrorEquation : baValue = -p4

theorem direct_product (c : OrderedProductCertificate) :
    c.abValue = c.p4 := c.directEquation

theorem reverse_product (c : OrderedProductCertificate) :
    c.baValue = -c.p4 := c.mirrorEquation

theorem signed_pair_zero_sum (c : OrderedProductCertificate) :
    c.abValue + c.baValue = 0 := by
  rw [c.directEquation, c.mirrorEquation]
  omega

/-- A nonzero exact quartic forbids treating the two ordered products equal. -/
theorem nonzero_quartic_forbids_commutation
    (c : OrderedProductCertificate) (h : c.p4 ≠ 0) :
    c.abValue ≠ c.baValue := by
  intro equalProducts
  rw [c.directEquation, c.mirrorEquation] at equalProducts
  omega

/-- A zero quartic does not license substitution of typed A and B. -/
theorem typed_distinction_independent_of_quartic
    (c : OrderedProductCertificate) : c.source.a ≠ c.source.b :=
  typed_pair_not_equal c.source

end HHS.Pass220.Module194OrderedProduct
