# Pass 200C Validation Plan

## Unit validation

The lifecycle suite verifies:

1. two successful canary frontiers are required;
2. at least 12 exact canary invocations are required;
3. a canary rollback disqualifies the bundle;
4. canary frontier and activation-receipt identities must be distinct;
5. candidate-return ordinals must match the admitted canary ratios;
6. compiler, runtime, and operations approvals require distinct principals, capabilities, and receipts;
7. expired, stale, duplicate, and tampered approvals are rejected;
8. guarded active admission records one singleton activation commit;
9. every exact active invocation returns the candidate;
10. lease exhaustion restores reference execution;
11. result, witness, or replay mismatch returns reference and rolls back;
12. expiry restores reference before candidate return;
13. restart preserves evidence, counters, frontier identity, and event-chain tip;
14. persisted frontier mutation is rejected;
15. verified probes use persisted Pass 200A shadow observations.

## Production validation

The production workflow must:

- run the complete Pass 200A holdout and shadow suite;
- create two successful Pass 200B canaries for one bundle;
- close eight invocations at ratio `1/4` and eight at ratio `1/2`;
- aggregate 16 exact canary invocations and six candidate returns;
- admit an active lease after three approvals and one separate activation receipt;
- return the candidate for six continuously guarded active invocations;
- restore a `LEASE_EXHAUSTED` reference frontier;
- admit a second active lease with fresh approvals;
- inject a controlled exact mismatch;
- return reference and restore a `ROLLED_BACK` frontier;
- reopen state and reproduce frontier, counters, return totals, evidence, and event-chain tip.

## Expected production totals

| Measure | Expected |
|---|---:|
| Pass 200A independent envelopes | 4 |
| Pass 200A compiler candidates | 4 |
| Pass 200A shadow matches | 4 |
| Successful Pass 200B canaries | 2 |
| Canary invocations | 16 |
| Canary candidate returns | 6 |
| Canary reference returns | 10 |
| Pass 200C evidence snapshots | 1 |
| Active frontiers | 2 |
| Singleton active commits | 2 |
| Active invocations | 7 |
| Active candidate returns | 6 |
| Active reference returns | 1 |
| Lease-exhausted frontiers | 1 |
| Rollback frontiers | 1 |
| Immutable Pass 200C frontiers including genesis | 5 |
| Pass 200C Hash72 events | 13 |

The 13 events are: one genesis frontier, one canary-evidence aggregation, two active admissions, seven guarded invocations, one lease-exhaustion transition, and one rollback transition.

## Static validation

- Python compilation of runtime, API, server, tests, and the restartable production harness.
- No floating-point canonical operations in Pass 200C authority code.
- Node syntax checks for the active panel and startup coordinator.
- Source checks for the four VM81 receipt roles, exact guard, route registration, and disabled frozen promotion.
