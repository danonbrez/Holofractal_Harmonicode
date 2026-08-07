# Pass 214 Iteration 7 — Live Admission and Ablation Bridge

Iteration 7 does not promote any optimization and does not authorize Pass 215. It closes the gap between the Iteration 6 repository-native candidate set and the live Pass 213 authorities that must govern any production benchmark.

## Bound inherited state

- base commit: `5be251a3df5bd3f949dbae8e34c71cfd5465bcd6`
- base tree: `8106623e074c5ec939e64c838f102ead403bc832`
- Pass 213 closure: `86ec461818682fc87232740758769602e8f9fe05`
- Iteration 6 candidate-set root: `f11bdbb9940e90500692cd0a0c505727ad94cafc0ea4fca85b134253f72cab9f`

## Live admission requirements

The bridge refuses fixture, synthetic, mock, or dependency-scoped timestamp authority. A production admission requires all of the following in one process:

1. The Pass 213 governed projection chain verifies and contains a non-fixture RFC 3161 timestamp-anchor projection.
2. The full trusted timestamp record is reverified with `TrustedTimestampAnchorRecord.validate`, the Pass 213 PQC verifier bundle, and `RFC3161TimestampVerifier` against an explicit trust bundle.
3. The latest moving tensor is anchored to that exact trusted timestamp root.
4. The configured Pass 213 native-dispatch ledger verifies, contains at least one receipt, and its current runtime state references the exact same tensor and trusted timestamp root.
5. A challenge committing the Iteration 6 candidate-set root, Pass 213 closure, Iteration 6 receipt, nonce, and integer timestamp is appended through the existing Pass 213 governed projection store.
6. The projection chain is reverified after the candidate challenge commitment.

Only this in-process path can set the three live-reverification fields used by the ablation-plan gate.

## Five-family plan

After live admission, the bridge emits a non-promoting plan for:

- `vector_cache`
- `wrapper_duplication`
- `numeric_lookup`
- `serialization_import`
- `coprime_lookup`

Each family requires three trials, bit-exact canonical output, deterministic replay, no floating-point canonical authority, unchanged Git blob identity, stable live admission, representation-byte measurement, and integer-nanosecond observation. Per-family ablations separate baseline, generator/transition, cache reuse, and cross-family compounding.

## Security and authority boundary

A recorded admission JSON can be structurally checked, but it cannot authorize execution after process restart. Live timestamp, governed-surface, and native-dispatch rechecks are mandatory before producing an executable ablation plan.

The bridge does not import candidates for replacement, does not execute migration, does not mint terminal Pass 214 roots, and does not authorize Pass 215.
