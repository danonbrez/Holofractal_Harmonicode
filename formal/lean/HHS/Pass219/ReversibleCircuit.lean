import Std

/-!
Pass 219 — reversible ingress/egress composition foundation.

This proves a structural composition property only. Every concrete module
must separately supply its native circuit, its round-trip proof, its typed
constraint/admission witness, and executable replay evidence. This module
does not mint VM81 or Hash72/Hash216 authority.
-/

namespace HHS.Pass219

/-- The packet type includes every item needed for exact return: payload,
ordered operations, phase, addresses, branches, and native metadata. -/
structure ReversibleCircuit (Input Output : Type) where
  ingressEgress : Input → Output
  egressIngress : Output → Input
  roundTrip : ∀ packet : Input, egressIngress (ingressEgress packet) = packet

/-- A reversible pair of modules composes in forward order and reverses
in the opposite order, without discarding the intermediate packet. -/
def ReversibleCircuit.compose
    {Input Middle Output : Type}
    (first : ReversibleCircuit Input Middle)
    (second : ReversibleCircuit Middle Output) :
    ReversibleCircuit Input Output where
  ingressEgress := fun packet => second.ingressEgress (first.ingressEgress packet)
  egressIngress := fun packet => first.egressIngress (second.egressIngress packet)
  roundTrip := by
    intro packet
    change first.egressIngress
      (second.egressIngress (second.ingressEgress (first.ingressEgress packet))) = packet
    rw [second.roundTrip (first.ingressEgress packet)]
    exact first.roundTrip packet

/-- Every admitted composition inherits exact input reconstruction when
the supplied module witnesses are valid for their full packet types. -/
theorem composed_round_trip
    {Input Middle Output : Type}
    (first : ReversibleCircuit Input Middle)
    (second : ReversibleCircuit Middle Output)
    (packet : Input) :
    (first.compose second).egressIngress
      ((first.compose second).ingressEgress packet) = packet :=
  (first.compose second).roundTrip packet

end HHS.Pass219
