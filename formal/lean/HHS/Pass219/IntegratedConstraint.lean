import HHS.Pass219.ReversibleCircuit

/-!
Pass 219 — integrated constraint inheritance.

A proof module is admitted only if its complete native input and resulting
output satisfy the applicable globally integrated tensor constraint packet.
The applicability/translation functions are explicit native obligations.
This file proves composition of supplied witnesses, not the truth of any
unimplemented native gate or the completeness of the repository census.
-/

namespace HHS.Pass219

/-- A global constraint frame can inspect the complete typed packet at each
boundary. Its implementations must preserve ordering, phases, addresses,
provenance and open residuals. -/
structure ConstraintFrame (Input Output : Type) where
  inputValid : Input → Prop
  outputValid : Output → Prop

/-- A native circuit plus a proof that it transports globally admitted
inputs to globally admitted outputs. No independent admission authority. -/
structure ConstrainedCircuit (Input Output : Type) where
  circuit : ReversibleCircuit Input Output
  frame : ConstraintFrame Input Output
  preserves : ∀ input, frame.inputValid input →
    frame.outputValid (circuit.ingressEgress input)

/-- Composition requires an explicit agreement witness at the intermediate
boundary; it cannot silently reinterpret incompatible constraint frames. -/
def ConstrainedCircuit.compose
    {Input Middle Output : Type}
    (first : ConstrainedCircuit Input Middle)
    (second : ConstrainedCircuit Middle Output)
    (compatible : ∀ intermediate,
      first.frame.outputValid intermediate →
      second.frame.inputValid intermediate) :
    ConstrainedCircuit Input Output where
  circuit := first.circuit.compose second.circuit
  frame := {
    inputValid := first.frame.inputValid
    outputValid := second.frame.outputValid
  }
  preserves := by
    intro input accepted
    exact second.preserves
      (first.circuit.ingressEgress input)
      (compatible _ (first.preserves input accepted))

theorem integrated_forward_preserves_constraints
    {Input Middle Output : Type}
    (first : ConstrainedCircuit Input Middle)
    (second : ConstrainedCircuit Middle Output)
    (compatible : ∀ intermediate,
      first.frame.outputValid intermediate →
      second.frame.inputValid intermediate)
    (input : Input)
    (h : first.frame.inputValid input) :
    second.frame.outputValid
      ((first.circuit.compose second.circuit).ingressEgress input) :=
  (first.compose second compatible).preserves input h

theorem integrated_round_trip
    {Input Middle Output : Type}
    (first : ConstrainedCircuit Input Middle)
    (second : ConstrainedCircuit Middle Output)
    (input : Input) :
    (first.circuit.compose second.circuit).egressIngress
      ((first.circuit.compose second.circuit).ingressEgress input) = input :=
  (first.circuit.compose second.circuit).roundTrip input

end HHS.Pass219
