# Pass 219 — Prime-Memristive Fifth Hydration Lane I10 Sparse Arbitration

Date: 2026-09-12

Status: **ADDITIVE CANDIDATE-ROUTING CONTRACT**

## Purpose

I10 adds exact distributed route competition and bounded sparse activation arbitration above the frozen-green I9 verified-metabolism layer.

The fifth lane remains an adaptive accessibility manifold. I10 does **not** create a fifth canonical Holo4 lane, does not commit Hash72/Hash216 state, and does not gain VM81 mutation or persistence authority.

## Inherited inputs

For each candidate neighborhood, I10 combines only already-authorized exact metadata:

1. I7 `prefetch_score` — inherited transition + replay routing utility;
2. I9 `vitality` — modified only by verified VM81/Hash216 outcomes;
3. I8 `available` activation budget — remaining exact local work capacity.

The arbitration surface is read-only with respect to all three inherited states.

## Exact score

For an eligible candidate `i`:

```text
route_component_i    = 4 * prefetch_score_i
vitality_component_i = 2 * vitality_i
budget_component_i   = min(available_i, 256)
raw_score_i           = route_component_i + vitality_component_i + budget_component_i
```

All terms are exact integers. Floating-point scoring is forbidden.

## Reciprocal competition

Candidates are ordered deterministically by:

1. larger `raw_score`;
2. larger verified vitality;
3. larger remaining budget;
4. larger inherited prefetch score;
5. smaller neighborhood binding signature;
6. smaller composition signature.

For each pair, the stronger candidate contributes one exact inhibition quantum to the weaker candidate:

```text
inhibition_i = stronger_candidate_count_i * 32
final_score_i = raw_score_i - inhibition_i
```

This is candidate-routing competition only. It is not semantic truth, canonical admission, or a state transition.

## Sparse activation membrane

An arbitration request supplies:

```text
query_context_signature64
active_modality_mask
max_active
per_route_work_cap
```

A candidate is ineligible when any of the following holds:

- its association belongs to another query context;
- its modality does not intersect the active modality mask;
- its inherited authority metadata is invalid;
- no I9 verified-metabolism state exists for its neighborhood;
- no I8 activation budget exists for its neighborhood;
- its exact hop floor `16 + member_count` cannot be funded by both remaining budget and `per_route_work_cap`.

After reciprocal competition, an otherwise eligible candidate is excluded when:

- `final_score <= 0`; or
- it falls outside the deterministic `max_active` winner set.

For every winner:

```text
work_allocation = min(remaining_budget, per_route_work_cap)
work_allocation >= exact_hop_floor
```

I10 does not debit the I8 budget. The allocation is a deterministic upper bound for later candidate hydration work. Actual work still passes through the inherited I8 debit membrane.

## Deterministic receipt

The arbitration receipt records, for every considered route:

```text
query context
active modality
neighborhood binding
composition signature
inherited prefetch score
verified vitality
remaining budget
route component
vitality component
budget component
raw score
stronger candidate count
inhibition
final score
exact hop floor
work allocation
competition rank
winner ordinal
exclusion reason
```

The result also records candidate, eligibility, winner, query-rejection, modality-rejection, budget-rejection, and inhibition-rejection counts plus a deterministic arbitration signature.

Permutation of the same unique candidate set must produce an identical ordered receipt and identical arbitration signature.

Duplicate neighborhood bindings in one request are rejected rather than double-counted.

## Authority boundary

```text
candidate_only = true
exact_integer_only = true
query_scoped_only = true
modality_scoped_only = true
verified_vitality_only = true
inherited_route_score_only = true
remaining_budget_only = true
deterministic_sparse_activation_only = true
reciprocal_inhibition_only = true
bounded_work_allocation_only = true
arbitration_receipt_only = true
inherited_budget_mutation = false
speculative_reinforcement = false
canonical_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false
canonical_persistence_authority = false
floating_point_authority = false
requires_inherited_vm81_hash216_admission = true
HHS_EXACT_PASS219_HOLO4_LANE_COUNT = 4
```

## Acceptance

I10 is accepted only if dependency-scoped validation proves:

1. inherited I9 benchmark remains green;
2. inherited I8 budget state is byte/field-equivalent before and after arbitration;
3. inherited I9 metabolic state is field-equivalent before and after arbitration;
4. deterministic top-K sparse winners are identical under candidate permutation;
5. reciprocal inhibition is exact and reproducible;
6. query and modality mismatches are excluded without mutation;
7. insufficient budget/work cap cannot become a winner;
8. duplicate neighborhood input is rejected;
9. winner work allocations are bounded by both local budget and request cap;
10. no speculative arbitration outcome can reinforce I9 vitality or replenish I8 budget;
11. inherited Holo4 remains exactly four lanes and byte-identical;
12. VM81 / Hash216 remain the sole canonical admission authority.
