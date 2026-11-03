import HHS.Pass219.ReversibleCircuit
import HHS.Pass220.Base64BalancedTrit5184

/-!
Pass 219 — development-time proof of inherited constraint composition.

Lean constrains coding-agent changes: a claimed typed circuit composition must
supply the applicable input/output predicates, a compatibility witness, and
exact round-trip proofs. These theorems verify supplied proof objects; they do
not execute VM81, impose a new runtime gate, mint canonical state, or replace
existing native enforcement paths. Discover concrete witnesses through the
repository service/dependency index before proposing an implementation change.
This module does not establish corpus-wide completeness or validate unbound
native constructors.
-/

namespace HHS.Pass219

/-- A global constraint frame can inspect the complete typed packet at each
boundary. Its implementations must preserve ordering, phases, addresses,
provenance and open residuals. -/
structure ConstraintFrame (Input Output : Type) where
  inputValid : Input → Prop
  outputValid : Output → Prop

/-- A representation of a supplied native circuit with development-time
proof evidence that it transports inputs satisfying the scoped source predicate
to outputs satisfying the scoped destination predicate. This structure is not
a runtime validator or an independent admission authority. -/
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


/-- Backward-compatible theorem name: given a supplied circuit, a source
predicate witness, and compatible intermediate predicates, prove output
predicate preservation, exact reconstruction, and source predicate preservation.
"Admission" in this name is logical terminology only: Lean does not authorize
VM81 ingress, state mutation, or historical reuse. -/
theorem integrated_reversible_admission
    {Input Middle Output : Type}
    (first : ConstrainedCircuit Input Middle)
    (second : ConstrainedCircuit Middle Output)
    (compatible : ∀ intermediate,
      first.frame.outputValid intermediate →
      second.frame.inputValid intermediate)
    (input : Input)
    (admitted : first.frame.inputValid input) :
    second.frame.outputValid
        ((first.circuit.compose second.circuit).ingressEgress input) ∧
    (first.circuit.compose second.circuit).egressIngress
        ((first.circuit.compose second.circuit).ingressEgress input) = input ∧
    first.frame.inputValid
        ((first.circuit.compose second.circuit).egressIngress
          ((first.circuit.compose second.circuit).ingressEgress input)) := by
  constructor
  · exact integrated_forward_preserves_constraints first second compatible input admitted
  constructor
  · exact integrated_round_trip first second input
  · rw [integrated_round_trip first second input]
    exact admitted


/-!
Concrete inherited proof correspondence (Pass 220 HNAN / Pass 219 composition).
The existing Base64BalancedTrit5184 theorem already establishes that every
admitted full binary frame recovers exactly after its ordered three-bit to
two-trit encoding. Bind that theorem to the *development-time* circuit proof
interface rather than inventing a parallel codec, HNAN gate, or admission test.
The central (neutral, neutral) address remains the pre-existing typed HNAN
gate and is not a ninth binary ingress code.
-/

/-- Adapter to an already proved, full-frame exact ingress/egress pair.
No runtime entrypoint or canonical authority is created. -/
def inheritedHNANBinaryFrameCircuit :
    ReversibleCircuit
      HHS.Pass220.Base64BalancedTrit5184.Binary5184
      HHS.Pass220.Base64BalancedTrit5184.BalancedTrit3456 where
  ingressEgress := HHS.Pass220.Base64BalancedTrit5184.encodeFrame
  egressIngress := HHS.Pass220.Base64BalancedTrit5184.decodeFrame
  roundTrip := HHS.Pass220.Base64BalancedTrit5184.full5184RadixRoundTrip

/-- Exact reconstruction is inherited from the established Pass 220 proof. -/
theorem inheritedHNANBinaryFrameRoundTrip
    (raw : HHS.Pass220.Base64BalancedTrit5184.Binary5184) :
    inheritedHNANBinaryFrameCircuit.egressIngress
      (inheritedHNANBinaryFrameCircuit.ingressEgress raw) = raw :=
  inheritedHNANBinaryFrameCircuit.roundTrip raw

/-- The center stays a typed gate coordinate, never a ninth binary word. -/
theorem inheritedHNANCenterNotBinary :
    HHS.Pass220.Base64BalancedTrit5184.decodePair
      (.neutral, .neutral) = none :=
  HHS.Pass220.Base64BalancedTrit5184.hnanCenterIsNotBinary

end HHS.Pass219
