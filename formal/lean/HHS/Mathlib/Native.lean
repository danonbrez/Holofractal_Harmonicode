import Std

namespace HHS.Mathlib.Native

/-- Stable identity of one native class exposed through the Mathlib compatibility surface. -/
structure ClassId where
  moduleName : String
  className : String
deriving Repr, BEq, DecidableEq

/-- Proof receipt presented to the HARMONICODE admission membrane after Lean checking. -/
structure ProofReceipt where
  theoremName : String
  leanModule : String
  kernelChecked : Bool
  noSorry : Bool
  noUnapprovedAxioms : Bool
deriving Repr, BEq, DecidableEq

/-- Lean is a proof witness. VM81 remains the mutation/admission authority. -/
def ProofReceipt.admitted (receipt : ProofReceipt) : Prop :=
  receipt.kernelChecked = true ∧
  receipt.noSorry = true ∧
  receipt.noUnapprovedAxioms = true

theorem admitted_requires_kernel
    (receipt : ProofReceipt)
    (h : receipt.admitted) :
    receipt.kernelChecked = true :=
  h.1

theorem admitted_requires_no_sorry
    (receipt : ProofReceipt)
    (h : receipt.admitted) :
    receipt.noSorry = true :=
  h.2.1

theorem admitted_requires_axiom_gate
    (receipt : ProofReceipt)
    (h : receipt.admitted) :
    receipt.noUnapprovedAxioms = true :=
  h.2.2

/-- Runtime arithmetic operations implemented by the native Python1/C11 kernel. -/
inductive ArithmeticOp
  | add
  | sub
  | mul
deriving Repr, BEq, DecidableEq

/-- Exact runtime witness. Decimal text is an ingress/egress projection of the native BigInt state. -/
structure ArithmeticWitness where
  op : ArithmeticOp
  lhsDecimal : String
  rhsDecimal : String
  resultDecimal : String
  python1Executed : Bool
  hostPythonEvaluatorUsed : Bool
deriving Repr, BEq, DecidableEq

def ArithmeticWitness.admitted (witness : ArithmeticWitness) : Prop :=
  witness.python1Executed = true ∧
  witness.hostPythonEvaluatorUsed = false

theorem arithmetic_admission_requires_python1
    (witness : ArithmeticWitness)
    (h : witness.admitted) :
    witness.python1Executed = true :=
  h.1

theorem arithmetic_admission_forbids_host_eval
    (witness : ArithmeticWitness)
    (h : witness.admitted) :
    witness.hostPythonEvaluatorUsed = false :=
  h.2

/-- Initial native rebuild nucleus. This is intentionally bounded and grows by verified slices. -/
def foundationClasses : List ClassId :=
  [
    { moduleName := "HHS.Mathlib.Data.Nat.Basic", className := "Nat" },
    { moduleName := "HHS.Mathlib.Data.Int.Basic", className := "Int" },
    { moduleName := "HHS.Mathlib.Logic.Basic", className := "Eq" }
  ]

theorem foundationClasses_nonempty : foundationClasses ≠ [] := by
  decide

/-- The current nucleus is a native foundation, not a claim of complete Mathlib coverage. -/
def completeMathlibCoverage : Bool := false

theorem foundation_does_not_claim_complete_mathlib :
    completeMathlibCoverage = false := by
  rfl

end HHS.Mathlib.Native
