import Std

namespace HHS.Pass220.ERSLane5Metadata

/-- Native expressions preserve ordered source syntax, not host scalar equality. -/
structure OrderedGate where
  lhs : String
  rhs : String
  context : String
deriving Repr, BEq, DecidableEq

def delta : String := "1"
def erSForward : OrderedGate := ⟨"AB", "P^4", "ERS forward orientation"⟩
def erSReverse : OrderedGate := ⟨"BA", "-P^4", "ERS reverse orientation"⟩
def composite : OrderedGate := ⟨"P^4", "c^4=(Aa+Ab)(Ba+Bb)", "ordered composition"⟩
def reciprocal : OrderedGate := ⟨"(Aa/Ba:Bb/Ab=Ab/Aa:Bb/Ba)^4/Δ", "Δ", "typed reciprocal quadrature"⟩
def h144 : OrderedGate := ⟨"144", "36*4=(6+6)^2=((a^2+b^2+c^2)+(a^2b^2c^2))^((pxy+qzw)/P)=b^8c^4", "Lane 4 H36 to Lane 5 H144"⟩
def phases : Array String := #["xy", "x+y", "yx", "wz", "z+w", "zw"]
def gates : Array OrderedGate := #[erSForward, erSReverse, composite, reciprocal, h144]
def phaseGearExample : String := "3/4:2/5"

/-- A typed metadata edge must not collapse its opposite orientation. -/
structure HydrationEdge where
  source : String
  target : String
  operandOrder : Array String
  cellAddress : Nat
  context : String
  ancestorHash216 : String
deriving Repr, BEq

def forwardEdge (address : Nat) (receipt : String) : HydrationEdge :=
  ⟨"AB", "P^4", #["A", "B"], address, "ERS", receipt⟩
def reverseEdge (address : Nat) (receipt : String) : HydrationEdge :=
  ⟨"BA", "-P^4", #["B", "A"], address, "ERS", receipt⟩

theorem opposite_edges_distinct (address : Nat) (receipt : String) :
    forwardEdge address receipt ≠ reverseEdge address receipt := by
  intro h
  have hsrc := congrArg HydrationEdge.source h
  simp [forwardEdge, reverseEdge] at hsrc

/-- Exact scalar projection only; not a proof of native operator closure. -/
theorem genesis_h144_projection :
    ((1 + 2 + 3) + (1 * 2 * 3)) ^ (2 : Nat) = 144 := by decide
theorem genesis_register_projection :
    (2 : Nat) ^ 4 * (3 : Nat) ^ 2 = 144 := by decide
theorem h36_fourfold : 36 * 4 = (144 : Nat) := by decide
theorem vm81_address_count : 81 * 64 = (72 : Nat) ^ 2 := by decide

end HHS.Pass220.ERSLane5Metadata
