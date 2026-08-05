# HHS Pass 213 — Timestamp-Bound Authenticated Moving Tensor Compiled ROM and Runtime Memory Integrity Kernel

**Contract:** `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`  
**Status:** `CONTRACT_AUTHORIZED — IMPLEMENTATION IN PROGRESS`  
**Current iteration:** `4`

## Binding inheritance

Pass 213 is an in-place upgrade of the complete pre-pass foundation and Pass 001–212 state. It preserves Pass 212 full hydration compression, physical erasure recovery, correction-before-decompression, Hash216 state validation, deterministic Hash72 receipts, VM5184×G243 addressing, exact BigInt serialization, and singleton VM81 canonical admission.

## Iteration 1 — compiled-ROM nucleus

Iteration 1 established immutable compiled-ROM identity, exact timestamp boundaries, noncommutative ordered-operation authentication, keyed one-visit closure paths, exact lookup, inventory roots, and deterministic receipts.

```text
validated operation
    → immutable compiled-ROM record
    → Hash216 exact identity
    → timestamp-bound operation group
    → keyed one-visit closure path
    → protected vector inventory root
    → deterministic authenticated receipt
```

## Iteration 2 — correction before ROM interpretation

Iteration 2 integrated the inherited Pass 212 physical recovery layer into canonical compiled-ROM admission.

```text
serialized immutable compiled-ROM entry
    → Pass 212 ProtectedPayload shards and parity
    → keyed Pass 213 carrier authentication
    → physical validation and bounded reconstruction
    → reconstructed shard Hash216 validation
    → exact recovered payload bytes
    → recovered payload Hash216 validation
    → canonical deserialization
    → immutable compiled-entry Hash216 validation
    → keyed RecoveredROMAdmission proof
```

JSON decoding occurs only after physical recovery and recovered-payload Hash216 validation. Malformed, altered, over-budget, unauthenticated, or incorrectly keyed carriers fail before canonical insertion.

## Iteration 3 — native protected compiled-ROM memory

Iteration 3 implements the native memory enclosure and connects it to recovered compiled-ROM admission.

Every secure arena is constructed as:

```text
PROT_NONE guard page
    +
mlock + MADV_DONTDUMP + MADV_DONTFORK data pages
    +
PROT_NONE guard page
```

The data pages are never executable. They begin read-write for bounded initialization, then become read-only when sealed. Every operation requires a constant-time validated 256-bit owner token. The process hardening surface disables dumpability through `PR_SET_DUMPABLE`.

The native arena provides:

- page-aligned allocation;
- two inaccessible guard pages;
- no-swap page locking;
- core-dump exclusion;
- fork-inheritance exclusion;
- owner-token authorization;
- bounds-checked reads and writes;
- read-only sealing;
- explicit volatile zeroization;
- zero verification;
- zeroization before unmap and release;
- stable native error codes.

The Python wrapper exposes no raw address. It emits keyed lifecycle receipts for:

```text
ALLOCATE → WRITE → SEAL → ZEROIZE → DESTROY
```

`NativeProtectedCompiledROMStore` closes the recovery and storage path:

```text
Pass 212 correction
    → RecoveredROMAdmission validation
    → canonical entry serialization
    → owner-bound native arena allocation
    → bounded write
    → read-only seal
    → internal re-read and Hash216 validation
    → protected-ROM inventory commitment
```

Canonical entry bytes remain in the sealed native arena. Lookup reads them internally, reconstructs a transient entry object, and revalidates its immutable Hash216 before use. Retirement zeroizes and destroys every arena.

## Iteration 4 — dependency-scoped parametric compiled-ROM admission

Iteration 4 adds the second compiled execution lane. One deeply validated compiled transformation may be reused for compatible typed operands and execution context without repeating unaffected semantic validation.

A parametric template binds:

- one immutable protected compiled-ROM entry;
- its operation identifier and native route;
- the complete operand and context field set;
- exact field types;
- mutable and immutable field classification;
- a finite deterministic semantic-constraint registry;
- the declared field dependencies of every constraint;
- authenticated witnesses proving the baseline candidate satisfied every constraint.

Every invocation performs the following exact sequence:

```text
load protected compiled entry
    → load sealed parametric template
    → validate the complete field set
    → validate every field type
    → compare every field with the authenticated baseline
    → reject changed immutable context
    → construct the sorted changed-field delta
    → select the union of dependent constraints
    → re-evaluate only that affected semantic set
    → reuse authenticated witnesses for unaffected constraints
    → bind the current opening timestamp boundary and parent lineage
    → mint the keyed VM81 parametric admission root
    → store the admission in a sealed native arena
```

This separates mandatory candidate-shape validation from reusable semantic evidence. Every untrusted invocation is still fully parsed, type-checked, canonically serialized, and compared against the complete template. Only semantic constraints proven independent of the changed fields are reused.

The initial deterministic constraint bytecode supports:

```text
INT_RANGE
MAX_BITS
ENUM
NONZERO
EQUAL
NOT_EQUAL
ORDERED_LE
LENGTH_RANGE
SUM_MAX_BITS
```

Each constraint names its exact field dependencies. For changed field set \(\Delta\), the runtime selects:

\[
C_{affected}=\{c\mid dependencies(c)\cap\Delta\neq\varnothing\}
\]

and reuses the baseline witness for:

\[
C_{reused}=C_{all}\setminus C_{affected}.
\]

The admission commits to the candidate hash, exact delta root, changed paths, affected-constraint witnesses, reused-witness root, compiled VM81 cell, operation slot, G243 control, native dispatch identifier, kernel policy, Genesis epoch, group sequence, parent Hash216, and opening timestamp boundary Hash216.

`NativeParametricCompiledROMStore` preserves the Iteration 3 memory gate:

- templates are serialized only after complete validation;
- template bytes reside in sealed owner-bound native arenas;
- candidate admissions reside in separate sealed native arenas;
- public records retain only identity, delta, count, arena, length, and receipt commitments;
- lookup requires the original timestamp boundary and revalidates the keyed admission;
- retirement zeroizes and destroys template and admission arenas.

## Current acceptance path

```text
untrusted carrier
    → physical correction and Hash216 validation
    → recovered admission proof
    → native guarded compiled-ROM arena
    → exact compiled match
         or
      parametric template match
         → exact changed-field delta
         → affected-constraint-only semantic revalidation
         → timestamp-bound VM81 admission
    → singleton VM81 commit authority
    → governed native dispatch
    → successor receipt
```

Similarity never grants authority. A novel operation remains subject to full sandbox validation and compilation before physical protection. A parametric candidate is admitted only through an exact registered template whose protected base entry, field schema, dependency graph, constraint witnesses, current timestamp boundary, and execution route all validate.

## Validation

The focused Pass 213 gate is:

```bash
bash scripts/run_pass213_iteration1_validation.sh
```

It builds the native C arena with warnings treated as errors, executes all Iteration 1–4 test modules, compiles all Python runtime modules, and parses the machine-readable contract.

## Iteration boundary

Pass 213 remains nonterminal. Remaining work includes persistent deletion detection and tombstones, PQC enclosure, trusted external timestamp checkpoints, full high-dimensional tensor invariants, API and CLI surfaces, governed native dispatch, performance evidence, final integration, merge, and verified-main closure.
