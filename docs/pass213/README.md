# Pass 213 — Iteration 1

This iteration establishes the executable nucleus for the timestamp-bound authenticated compiled ROM.

Implemented:

- exact canonical serialization and framed SHA-256 identities;
- HMAC-SHA-256 domain-separated key derivation;
- exact integer-nanosecond opening and closing boundaries;
- authenticated noncommutative operation-group chaining;
- deterministic keyed full-cycle permutations over declared lattice domains;
- immutable compiled-ROM records with VM81, operation-slot, and G243 identities;
- exact compiled lookup and authenticated inventory roots;
- deterministic authenticated operation-group receipts;
- focused mutation, rollback, ordering, closure, and duplicate-identity tests.

The closure implementation uses an affine bijection `cell(i) = (a*i+b) mod N` with `gcd(a,N)=1`. It proves one visit per cell and exact closure for the declared domain. Later iterations may replace or compose this calibration permutation with the full high-dimensional magic-square/Sudoku tensor generator while preserving the same closure interface and evidence requirements.

## Validation

```bash
bash scripts/run_pass213_iteration1_validation.sh
```

## Current boundary

This iteration does not claim the full Pass 213 contract is complete. Pass 212 recovery integration, protected-memory enforcement, persistent tombstones, PQC enclosure, trusted external timestamp anchoring, native dispatch, APIs, CLI, and full performance evidence remain explicit subsequent iterations.
