# Pass 219 — Prime-Memristive Fifth Hydration Lane Adaptive Context Utility I4

Date: 2026-09-12

## Purpose

Iteration 4 extends the candidate-only fifth hydration lane with adaptive multi-context route utility. It learns which previously composed prime-fibre routes are useful for a query context without creating a second transition authority and without changing inherited VM81, Hash72, Hash216, or canonical persistence state.

## Authority

The I4 surface is valid only when all of the following remain true:

```text
candidate_only = true
exact_integer_only = true
hash216_reference_only = true
route_utility_only = true
canonical_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false
canonical_persistence_authority = false
floating_point_authority = false
requires_inherited_vm81_hash216_admission = true
HHS_EXACT_PASS219_HOLO4_LANE_COUNT = 4
```

I4 may rank, weaken, decay, reuse, or reject an access route. It MUST NOT mint, rewrite, commit, or persist canonical Hash216 identity.

## Exact route statistics

For a context `c` and cached contextual route `r`, maintain:

```text
U(c,r) = {
  uses,
  positive_feedback,
  negative_feedback,
  candidate_reduction_sum,
  posting_work_sum,
  last_observed_sequence,
  utility_q10
}
```

All fields are integer-only and saturating. `utility_q10` is bounded to the inherited fifth-lane weight bound.

For one observation over corpus size `N`, candidate count `C`, posting work `W`, and trinary admission feedback `f in {-1,0,+1}`:

```text
R = max(N-C, 0)
reduction_q10 = floor(1024 * R / N)
posting_q10   = floor(1024 * min(W,N) / N)
delta         = reduction_q10 - posting_q10 + 128*f
utility_q10'  = clip(utility_q10 + delta, -5184, +5184)
```

This is an accessibility score only. It is not a probability, canonical model weight, or state-transition value.

## Deterministic contextual selection

Among non-stale routes for context `c`, select lexicographically by:

1. greater `utility_q10`;
2. greater positive feedback count;
3. greater accumulated candidate reduction;
4. lower accumulated posting work;
5. newer `last_observed_sequence`;
6. lower contextual composition signature.

A route is stale when it has prior observation history and:

```text
current_sequence > last_observed_sequence + max_age
```

Selection must be deterministic for identical repository-visible state.

## Warm/cold fallback

A contextual warm route may be used only when it exists, is non-stale, and its materialized query reaches the exact candidate budget.

Fallback to inherited cold I1 routing is mandatory when:

```text
context absent
OR no non-stale contextual route exists
OR warm route cannot reach candidate_budget
OR warm route fails validation
```

The cold fallback uses the same query fingerprint and inherited candidate index. For every exercised route:

```text
indexed_candidate_IDs == linear_scan_candidate_IDs
```

Final verification and transition admission remain inherited VM81/Hash216 responsibilities.

## Bounded weakening and decay

Negative admission feedback may reduce route utility without deleting the referenced Hash216 states. Utility decay moves route utility monotonically toward zero using an exact positive integer quantum and never changes canonical knowledge.

Therefore:

```text
knowledge identity != access-route utility
route weakening != knowledge forgetting
route expiry != Hash216 deletion
```

## Required I4 evidence

The first I4 implementation cycle must demonstrate:

1. two or more cached routes under one context;
2. deterministic utility-based route choice;
3. repeated warm-query reuse with structural work counters;
4. exact warm candidate parity with the linear oracle;
5. negative feedback causing route weakening/alternate selection;
6. positive feedback allowing deterministic recovery;
7. bounded decay toward zero;
8. missing-context fallback to cold routing;
9. stale-context fallback to cold routing;
10. insufficient-reduction warm route fallback to cold routing;
11. deliberate Hash216 alias references surviving route weakening/recovery unchanged;
12. inherited Holo4 lane count and authority remaining unchanged.

No latency or universal asymptotic claim is authorized by a single deterministic benchmark.
