# Pass 213 — Iterations 1 and 2

Pass 213 builds the timestamp-bound authenticated compiled ROM and protects its canonical admission path with inherited Pass 212 physical recovery.

## Iteration 1

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

## Iteration 2

Implemented:

- exact serialization of immutable compiled-ROM entries;
- Pass 212 `ProtectedPayload` physical shard and parity protection;
- keyed Pass 213 carrier roots and authentication tags;
- correction of one or two missing physical shards within the inherited stripe budget;
- fail-closed behavior beyond the recovery budget;
- present-shard corruption rejection;
- recovered payload Hash216 validation before JSON deserialization;
- immutable entry Hash216 validation after deserialization;
- keyed `RecoveredROMAdmission` proofs;
- `RecoveryGatedCompiledROMStore`, which accepts recovery admissions rather than raw entries;
- combined inventory roots covering compiled entries and their admission roots.

The canonical sequence is:

```text
validate carrier
→ correct physical damage
→ validate reconstructed payload Hash216
→ deserialize
→ validate compiled entry Hash216
→ mint admission proof
→ insert into compiled ROM
```

## Validation

```bash
bash scripts/run_pass213_iteration1_validation.sh
```

The script executes both iteration test modules, compiles both runtime modules, and parses the machine-readable contract.

## Current boundary

Pass 213 remains incomplete. Protected-memory enforcement, parametric delta validation, persistent tombstones, PQC enclosure, trusted external timestamp anchoring, native dispatch, APIs, CLI, full performance evidence, final merge, and verified-main closure remain subsequent work.
