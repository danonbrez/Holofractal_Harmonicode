import HHS.Mathlib.Native

namespace HHS.Pass220.I082

/-- Literal HHS tensor operators. No scalar cancellation or reordering. -/
inductive TensorExpr where
  | atom : String → TensorExpr
  | nat : Nat → TensorExpr
  | orderedMul : List TensorExpr → TensorExpr
  | orderedAdd : List TensorExpr → TensorExpr
  | orderedDiv : TensorExpr → TensorExpr → TensorExpr
  | orderedPow : TensorExpr → TensorExpr → TensorExpr
  deriving Repr, DecidableEq

open TensorExpr

def neuronCount : Nat := 86805555555
def vm81Width : Nat := 81 * 64
def logicalPositions : Nat := neuronCount * vm81Width

theorem vm81WidthExact : vm81Width = 5184 := by decide
theorem logicalPositionsExact :
    logicalPositions = 449999999997120 := by decide

/-- Exact rational coefficient cross-multiplication, not tensor simplification. -/
theorem exactNumericProjection :
    neuronCount * 5184 * 6 * 312500000000 =
    1406249999991 * 600000000000000 := by decide

/-- The original left-middle-right equation is encoded in source order. -/
def left : TensorExpr :=
  orderedMul [
    orderedDiv
      (orderedMul [nat neuronCount, atom "x"])
      (orderedMul [nat 600000000000000,
        orderedPow (atom "a") (nat 2), atom "x", atom "y"]),
    orderedPow (nat 72) (nat 2), atom "b", nat 6
  ]

def middle : TensorExpr :=
  orderedDiv
    (orderedAdd [
      orderedPow (atom "a") (nat 2),
      orderedPow (atom "b") (nat 2),
      orderedPow (atom "c") (nat 2)])
    (orderedMul [atom "x", atom "y"])

def right : TensorExpr :=
  orderedMul [nat 5184, atom "z", orderedPow (atom "w") (atom "u")]

theorem orderedPairDistinct :
    orderedMul [atom "x", atom "y"] ≠
    orderedMul [atom "y", atom "x"] := by decide

theorem leftPreservesOrderedDenominator :
    left ≠ orderedMul [
      orderedDiv
        (orderedMul [nat neuronCount, atom "x"])
        (orderedMul [nat 600000000000000,
          orderedPow (atom "a") (nat 2), atom "y", atom "x"]),
      orderedPow (nat 72) (nat 2), atom "b", nat 6
    ] := by decide

/-- Native relation is a parameter supplied by Lane 5, never substituted by
    ordinary scalar equality. An implementation must provide both witnesses. -/
def NativeClosureObligation {Carrier : Type}
    (eval : TensorExpr → Carrier)
    (orderedClosure : Carrier → Carrier → Prop) : Prop :=
  orderedClosure (eval left) (eval middle) ∧
  orderedClosure (eval middle) (eval right)

/-- A checked proof of NativeClosureObligation remains an admission prerequisite.
    The numeric and syntax proofs above do not construct it. -/
structure NativeClosureReceipt {Carrier : Type}
    (eval : TensorExpr → Carrier)
    (orderedClosure : Carrier → Carrier → Prop) where
  proof : NativeClosureObligation eval orderedClosure

end HHS.Pass220.I082
