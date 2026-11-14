import HHS.Alignment.ReciprocalTensor

namespace HHS.Pass220.Module194TypedClosure

/-!
Concrete Module 194 finite-address *structural* instance.
These proofs establish source-domain cardinalities, typed operand distinction,
directed AB/BA phase-polarity tags, and no accidental operand reversal.
They do not prove multiplication of the 81-address HNAN tensor, derive
AB=P⁴/BA=-P⁴ as algebraic values, establish delta-e interior/outer
closure, or discharge the existing I051 t.admitted hypothesis.
-/

/-- Exactly one address for each of the inherited 81 tensor groups. -/
abbrev GroupAddress := Fin 81

/-- Exactly 128 inherited particle slots per tensor group. -/
abbrev GroupSlot := Fin 128

theorem group_address_count : Fintype.card GroupAddress = 81 := by
  decide

theorem group_slot_count : Fintype.card GroupSlot = 128 := by
  decide

/-- The source's HNAN operands are typed, not host scalar aliases. -/
inductive Operand
  | lhsTensor
  | rhsBoundary
deriving Repr, BEq, DecidableEq

def lhs : Operand := .lhsTensor
def rhs : Operand := .rhsBoundary

theorem lhs_ne_rhs : lhs ≠ rhs := by
  decide

/-- A source group is an LHS tensor leaf. The RHS is not a group leaf. -/
def sourceOperand (_ : GroupAddress) : Operand := lhs

theorem all_source_leaves_are_lhs (i : GroupAddress) :
    sourceOperand i = lhs := by
  rfl

theorem rhs_not_source_leaf (i : GroupAddress) :
    sourceOperand i ≠ rhs := by
  simp [sourceOperand, lhs_ne_rhs]

/--
Ordered phase labels preserve the specified positive direct and negative
mirror signs. This models their TYPE/ORIENTATION, not their multiplication.
-/
inductive ProductDirection
  | ab
  | ba
deriving Repr, BEq, DecidableEq

def directedPhase : ProductDirection → Int
  | .ab => 1
  | .ba => -1

theorem ab_ba_directions_distinct :
    ProductDirection.ab ≠ ProductDirection.ba := by
  decide

theorem direct_polarity : directedPhase .ab = 1 := by
  rfl

theorem mirror_polarity : directedPhase .ba = -1 := by
  rfl

theorem inverse_polarity :
    directedPhase .ab = - directedPhase .ba := by
  decide

/-- The declared trinary phase order remains (-1,0,+1). -/
def trinary : List Int := [-1, 0, 1]

theorem trinary_exact : trinary = [-1, 0, 1] := by
  rfl

end HHS.Pass220.Module194TypedClosure
