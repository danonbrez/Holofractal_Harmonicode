# HHS-I134 — Recursive Full-Ancestry Checkpoint Contract (RFACC)

**Version:** 1.0.0  
**Status:** Normative derived checkpoint-governance contract  
**Parent contracts:** HHS-I132 CEUAC; HHS-I133 SCHIC  
**Pass:** 134

## Purpose

HHS-I134 governs the physical persistence and deterministic reconstruction of HHS pass checkpoints.

A pass is a complete system checkpoint, not merely a report bundle or a delta archive:

```text
Complete Parent System Tree
+ witnessed child mutations
+ preserved canonical outputs and receipts
- declared transient caches
= Complete Child System Tree
```

## Invariants

1. **Ω1 Full-copy inheritance** — Every non-cache parent path remains present in the child checkpoint.
2. **Ω2 No system-file deletion** — A pass may modify or supersede a system file at its existing path, but may not remove the inherited path.
3. **Ω3 Evidence is not a filesystem parent** — Reports and receipts preserve results but cannot substitute for source, contracts, schemas, tests, fixtures, or runtime modules.
4. **Ω4 Cache disposability is conditional** — Only recognized transient caches may be omitted. Any unique replay-critical state must first be promoted into a durable output, report, receipt, or checkpoint object.
5. **Ω5 Parent identity admission** — Parent archive SHA-256 and canonical tree root must match the operation contract before mutation.
6. **Ω6 Deterministic reconstruction** — Equivalent parent bytes and ordered operations produce byte-identical child archives.
7. **Ω7 Operation ordering** — Pass mutations are non-commutative and execute only in committed pass order.
8. **Ω8 Append-only correction** — Incorrect completion claims are corrected through errata; historical evidence is not rewritten.
9. **Ω9 Corruption localization** — The first pass that fails parent-path inclusion, parent-root continuity, or manifest recomputation is the first corrupt checkpoint.
10. **Ω10 No fabricated recovery** — Missing ancestor bytes may be retrieved or reconstructed from authoritative operations, but never invented from reports alone.
11. **Ω11 Every reconstructed pass is materialized** — Chain recovery emits a complete full-tree ZIP after each replayed pass operation.
12. **Ω12 Self-application** — The checkpoint compiler must be able to validate and reconstruct a chain containing its own implementation.

## Required full-checkpoint manifest

Every authoritative checkpoint contains `HHS_FULL_CHECKPOINT_MANIFEST.json`, including:

- pass and parent pass identity;
- parent tree root;
- canonical child tree root;
- every non-cache file path, SHA-256, byte length, mode, and artifact class;
- excluded cache paths;
- explicit no-deletion rule;
- Hash72 witness over the manifest payload.

The manifest excludes itself from its own file set to avoid recursive serialization.

## Admission states

- `FULL_SYSTEM_CHECKPOINT`
- `EVIDENCE_BUNDLE`
- `UNAUTHORIZED_PARTIAL_OR_LEGACY_TREE`
- `NONCHECKPOINT_ARTIFACT`

Only `FULL_SYSTEM_CHECKPOINT` is admitted as a normal parent. A legacy tree may be admitted only through an explicit migration operation that creates the first authoritative manifest.

## Terminal states

- `FULL_ANCESTOR_COPY_VERIFIED`
- `FULL_CHECKPOINT_CHAIN_RECONSTRUCTED`
- `EVIDENCE_PARENT_REJECTED`
- `PARENT_IDENTITY_MISMATCH`
- `SYSTEM_FILE_DELETION_REJECTED`
- `ANCESTRY_PATH_MISSING`
- `PATCH_REPLAY_FAILURE`
- `HISTORICAL_RECONSTRUCTION_INPUT_REQUIRED`
