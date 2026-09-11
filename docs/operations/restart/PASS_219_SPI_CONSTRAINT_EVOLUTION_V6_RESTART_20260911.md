# Pass 219 SPI Constraint Evolution v6 — Restart Record

## Repository-visible restart state

- Audited base main: `2def7910b99046821f34e1446bcec33ca4fd4090`
- Working branch: `agent/pass219-spi-scalar-projection-registry-v1-20260910`
- Merge vehicle: PR `#427`
- Validated predecessor checkpoint: `fb2e1b476b7c19708a09de42e4bcf22794374733`
- v6 implementation commits:
  - `56d66d18213b4bcbc65b91a3c310a449e064cc84` — exact constraint/evolution optimizer
  - `12c203a9b4f42886e4d8ccc61cab7444587fbb4d` — optimizer negative/positive tests
  - `b6d6714857db4f01b8da904f03ddc8fa906cf27e` — formal optimizer contract
  - `48e60bb0897733d9457e1a1235c31e849ec52487` — additive SPI registry v6
  - `f3ae2f399c876804d3085e424f9d09c676cbc965` — registry v6 tests
  - `9893ca9afbf07f2a9e0bb0d40896a40a0d21ec01` — dedicated v6 workflow
- This restart-record commit is documentation-only above that implementation head.

## Cycle

```text
FORMALIZE
-> PROVE
-> IMPLEMENT
-> OPTIMIZE
-> CANONIZE
-> ITERATE
```

v6 makes this lifecycle executable over closed SPI tensor-translation
candidates.

## Exact optimization law

Only candidates satisfying:

```text
Formalized(c) ∧ Proved(c) ∧ Implemented(c)
```

enter the optimization set.

Structural work is exact integer state:

```text
unresolved = branch_count - reusable_branch_count
```

Selection is deterministic:

```text
minimum unresolved branches
-> maximum already-proved reuse
-> stable candidate id
```

Semantic labels have zero selection authority. Floats fail closed.

## 5,184 / four-lane binding

Each candidate carries:

```text
(hydration_lane4, cell81, operation64, address5184)
address5184 = cell81 * 64 + operation64
```

The coordinate is knowledge/projection metadata only. It creates no alternate
VM81 transition authority.

## Implemented files

- `hhs_spi_constraint_evolution_optimizer_v1.py`
- `hhs_spi_constraint_evolution_optimizer_tests_v1.py`
- `hhs_spi_scalar_projection_registry_v6.py`
- `hhs_spi_scalar_projection_registry_tests_v6.py`
- `contracts/pass219/PASS_219_SPI_CONSTRAINT_EVOLUTION_LEARNING_OPTIMIZER_V1.md`
- `.github/workflows/pass219-spi-constraint-evolution-v6.yml`
- this restart record

## v6 proof delta

Registry v6 is designed as a one-proof additive successor to v5:

```text
SPI-CONSTRAINT-EVOLUTION-LEARNING-OPTIMIZER
```

Required predecessor invariant:

```text
every v5 proof to_dict() remains unchanged
```

## Authority boundary

Invariant false authorities:

```text
canonical_admission = FALSE
vm81_mutation = FALSE
canonical_hash72 = FALSE
canonical_hash216 = FALSE
canonical_persistence = FALSE
floating_point = FALSE
semantic_selection_authority = FALSE
unmeasured_speedup_claim = FALSE
```

The optimizer may emit `PROJECTION_RECEIPT_ELIGIBLE`; this is not repository
main canonization and is not VM81 state admission.

## Current validation state

Dedicated workflow:

```text
name = Pass 219 SPI Constraint Evolution v6
run = 34612168093
job = 103305092629
implementation head = 9893ca9afbf07f2a9e0bb0d40896a40a0d21ec01
state at checkpoint creation = QUEUED
```

The workflow covers:

1. Python compilation of all new v6 surfaces;
2. exact optimizer positive/negative tests;
3. registry v6 validation/tests;
4. frozen registry v5 regression;
5. Law-of-1 v4 and O2 v2 regression;
6. inherited VM5184/four-lane geometry checks including the existing
   `4×64×72×81=1,492,992` transport cardinality;
7. frozen SPI corpus census/hash regression;
8. deterministic optimizer-cycle and registry-v6 evidence generation;
9. artifact upload.

No green result is claimed by this restart record while the run is queued.

## Deterministic reference cycle

The implemented reference workload compares two already-proved tensor
candidates:

```text
LOSHU-S4-STRUCTURAL: branch=64, reuse=48, unresolved=16
SUDOKU-S4-REUSE:    branch=81, reuse=72, unresolved=9
```

The exact selection law therefore chooses `SUDOKU-S4-REUSE` and emits a
next-cycle seed whose next stage is `FORMALIZE`.

This is structural-work evidence only; no runtime speedup is inferred.

## Remaining validation / next action

1. Inspect run `34612168093` when it resolves.
2. If red, repair only the failing v6/dependency surface and rerun the complete
   dedicated v6 gate.
3. If green, record run/job/artifact/receipt hashes in a validated restart
   successor.
4. Update PR #427 title/body with validated v6 evidence.
5. Do not merge or deploy without an explicit integration action.
