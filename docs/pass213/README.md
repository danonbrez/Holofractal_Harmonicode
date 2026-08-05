# Pass 213 — Iterations 1–4

Pass 213 builds the timestamp-bound authenticated compiled ROM, corrects its physical carriers before interpretation, stores admitted entries in native protected memory, and reuses compiled transformations through dependency-scoped parametric validation.

## Iteration 1: compiled-ROM authority

Implemented:

- exact canonical serialization and framed SHA-256 identities;
- domain-separated keyed derivation;
- integer-nanosecond opening and closing boundaries;
- authenticated noncommutative operation-group chaining;
- deterministic keyed full-cycle permutations;
- immutable compiled-ROM records;
- exact lookup, inventory roots, and deterministic receipts.

## Iteration 2: recovery-gated admission

Implemented:

- Pass 212 physical shard and parity protection;
- keyed Pass 213 carrier roots and authentication;
- correction of one or two missing shards within the inherited budget;
- fail-closed rejection outside the budget;
- recovered payload Hash216 validation before deserialization;
- immutable entry Hash216 validation after deserialization;
- keyed `RecoveredROMAdmission` proofs;
- recovery-gated canonical insertion.

## Iteration 3: native secure memory

Implemented:

- guarded native `mmap` arenas;
- non-executable data pages;
- `mlock`, `MADV_DONTDUMP`, and `MADV_DONTFORK` enforcement;
- process dumpability hardening;
- constant-time owner-token authorization;
- bounds-checked access and read-only sealing;
- explicit zeroization and verification before release;
- keyed memory lifecycle receipts;
- sealed native storage and revalidation for recovered compiled-ROM entries.

## Iteration 4: parametric delta admission

Implemented:

- immutable templates bound to protected compiled-ROM entries;
- exact operand and context schemas;
- field-level mutable and immutable declarations;
- deterministic constraint bytecode and explicit dependency sets;
- baseline constraint witnesses;
- complete field-set and type validation on every invocation;
- exact changed-field delta construction;
- dependency-closure selection of affected constraints;
- semantic revalidation only for affected constraints;
- authenticated reuse of unaffected baseline witnesses;
- timestamp-, lineage-, route-, and policy-bound VM81 admission roots;
- sealed native template and admission storage;
- zeroizing template and admission retirement.

Parametric sequence:

```text
protected compiled operation
→ sealed template
→ complete typed invocation validation
→ exact changed-field delta
→ affected constraint dependency closure
→ affected-only semantic revalidation
→ authenticated unaffected-witness reuse
→ timestamp-bound VM81 admission root
→ sealed native admission arena
```

A parametric match never relies on vector similarity. It requires an exact registered template whose protected base entry, schema, dependency graph, baseline witnesses, current timestamp boundary, and VM5184×G243 route all validate.

## Validation

```bash
bash scripts/run_pass213_iteration1_validation.sh
```

The gate builds the C source with `-Wall -Wextra -Werror`, executes every Pass 213 Iteration 1–4 test module, compiles all runtime modules, and validates the JSON contract.

## Current boundary

Pass 213 remains incomplete. Persistent inventories and tombstones, deletion recovery, PQC enclosure, trusted external timestamps, full tensor invariants, API/CLI/native dispatch, performance evidence, final integration, merge, and verified-main closure remain subsequent work.
