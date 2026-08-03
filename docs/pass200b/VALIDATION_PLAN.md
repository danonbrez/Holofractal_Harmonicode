# Pass 200B Validation Plan

## Dependency-scoped unit validation

The unit suite verifies:

1. exactly two promotion approvals are required;
2. approval principals and receipt identities must be distinct;
3. compiler and runtime capabilities must be separated;
4. expired and tampered approvals are rejected;
5. one singleton activation commit is recorded per canary frontier;
6. deterministic ratio selection returns the candidate only on selected exact matches;
7. the invocation limit restores an `EXHAUSTED` reference frontier;
8. exact-result, witness, or replay mismatch restores a `ROLLED_BACK` reference frontier;
9. explicit rollback rejects stale frontier identities;
10. restart preserves counters and event-chain tip;
11. persisted frontier mutation is detected;
12. the verified probe consumes Pass 200A shadow evidence rather than frontend-supplied comparison values.

## Production validation

The production workflow must:

- create four independent Pass 200A holdout envelopes;
- create four compiler-candidate bundles and four exact shadow matches;
- admit one bundle at ratio `1/4` for eight invocations;
- observe candidate returns only at ordinals `0` and `4`;
- restore an `EXHAUSTED` reference frontier after invocation eight;
- admit a second bundle with fresh frontier-bound approvals;
- inject a controlled exact mismatch through the direct authority test surface;
- return the reference result and restore a `ROLLED_BACK` frontier;
- reopen the database and reproduce current frontier, counters, and event-chain tip.

## Expected production totals

| Measure | Expected |
|---|---:|
| Pass 200A independent envelopes | 4 |
| Pass 200A compiler candidates | 4 |
| Pass 200A shadow matches | 4 |
| Canary frontiers | 2 |
| Singleton activation commits | 2 |
| Metered invocations | 9 |
| Candidate returns | 2 |
| Reference returns | 7 |
| Exhausted frontiers | 1 |
| Rollback frontiers | 1 |
| Immutable frontiers including genesis | 5 |
| Hash72 events | 14 |

## Static validation

- Python compilation of runtime, production projection, API, visual server, and tests.
- No floating-point canonical operations in Pass 200B authority code.
- Node syntax validation for the canary panel and startup coordinator.
- Source checks for VM81 ticks, dual principals, visual projection, and disabled unrestricted promotion.
