# Pass 219 Lane 5 Direct Witness Routing 1.46

## Purpose

1.46 updates Lane 5 so optimization operates on proof-carrying direct composition jumps rather than graph enumeration. A route is admissible only when Lane 5 knows the previous state, current state, replay witness for how the current state was reached, exact goal, and the contradiction/forbidden boundary that constrains the next jump.

Lane 5 does not need to materialize intermediate states. It must instead prove that the direct candidate is compatible with the inherited state geometry, provenance, goal, contradiction boundary, and signed environmental VM81 admission boundary.

## Exact state space and serialization

The inherited canonical address space remains finite and exact:

```text
72^72 = 5184^36
5184 = 72*72 = 81*64
```

BigInt/Hash72 serialization supplies deterministic global addressing. 1.46 does not enlarge that canonical manifold and does not redefine Hash72 or Hash216 authority.

The optimization target is the route relation over already-addressable states, not a new state-count claim.

## Local dual-collapse geometry

Each local state preserves both inherited projections:

```text
9D x,y,z,w relational rotation -> balanced trinary collapse {-1,0,+1}
2D imaginary phase plane       -> binary collapse {0,1}
```

The canonical quarter-cycle positions are:

```text
u^0 == u^72, u^18, u^36, u^54
```

The visible `0` state is not treated as an invalid scalar hole. It is the closed phase-cancellation state and identifies the nested layer below the current collapse surface. A typed `0/0` relation is therefore admissible as a paired lower-layer entanglement/superposition slot inside this system; it is not rejected by importing conventional scalar division-by-zero semantics.

1.46 stores only the exact collapse values and canonical phase slot needed for routing. It does not flatten the inherited symbolic tensor into untyped scalar arithmetic.

## Exact reciprocal inversion

The inherited system law

```text
(a^2+b^2=c^2)^2 = P^4
```

is used as the reciprocal phase-inversion contract for routing. For a canonical quarter-cycle phase `q`, the phase-canceling inverse is exactly:

```text
inverse(q) = (q + 36) mod 72
```

Therefore:

```text
0 <-> 36
18 <-> 54
```

The route descriptor must carry a nonzero reciprocal-inverse state signature and the exact inverse phase slot. Lane 5 cannot accept a candidate that claims reciprocal closure while presenting a different phase relation.

## Direct witness route

A 1.46 route descriptor binds:

```text
previous_state
current_state
provenance_witness
goal_state
forbidden_boundary
reciprocal_inverse_state
candidate_state
route_identity
represented_span
integer_route_cost
```

The candidate state must equal the exact requested goal identity. The goal must not collide with the forbidden-boundary identity, and the descriptor must explicitly assert that the goal/forbidden sets do not conflict.

The route is valid only when:

```text
replay_witness_verified = 1
exact_goal_reached = 1
contradiction_free = 1
reciprocal_phase_verified = 1
bigint_serialization_addressed = 1
materialized_intermediate_states = 0
```

The minimum evidence count is five, covering previous/current/provenance/goal/forbidden evidence. At least one contradiction check is required.

## Integer-only optimization

Lane 5 route optimization is deterministic and integer-only. For each candidate:

```text
integer_route_cost = evidence_count + contradiction_check_count + 1
```

The final `+1` is the direct candidate evaluation itself. The represented span is not charged as materialized work because intermediate states are not visited.

Among valid candidates, the optimizer chooses in this order:

1. lower exact integer route cost;
2. larger represented span, because it closes more route distance with the same proof cost;
3. lower route signature as a deterministic final tie-break.

The receipt records:

```text
avoided_intermediate_states = max(represented_span - 1, 0)
```

This is a logical materialization count, not a wall-clock performance claim.

## Finite runtime candidates versus unlimited route histories

1.46 never attempts to enumerate all possible path histories. The runtime optimizer accepts a finite candidate array on each call. Arbitrarily long branching histories can be reasoned about compositionally, but canonical execution remains bounded to explicit finite evidence and one selected candidate.

## Authority membrane

1.46 is candidate/optimization authority only.

The following are required to remain false:

```text
canonical_vm81_mutation_authority = 0
canonical_hash72_authority = 0
canonical_hash216_authority = 0
canonical_persistence_authority = 0
pqc_key_authority = 0
receipt_clock_authority = 0
floating_point_canonical_authority = 0
```

The route must carry:

```text
requires_signed_environmental_vm81_admission = 1
```

and canonical mutation remains exclusively owned by:

```text
hhs_exact_pass219_vm81_environment_admit_signed
```

A successful Lane 5 optimization receipt therefore proves only that the candidate route is internally admissible under the 1.46 scope. It cannot itself commit VM81 state, mint canonical Hash72/Hash216 lineage, persist canonical state, advance a receipt clock, or create PQC authority.

## Deterministic replay and contradiction closure

For the same ordered route descriptor, validation must reproduce the same descriptor and receipt signatures. Any mutation to provenance, goal, forbidden boundary, reciprocal inverse, phase, collapse state, authority flags, intermediate-state count, or integer cost must either change the deterministic receipt or fail validation.

The operational decision is therefore:

```text
(previous,current,witness,goal,forbidden)
    -> finite candidate set
    -> reject contradictory/unproven candidates
    -> deterministic minimum-cost direct witness route
    -> signed environmental VM81 admission remains required for canonical commit
```

This closes the Lane 5 optimization path without requiring intermediate-state visitation.
