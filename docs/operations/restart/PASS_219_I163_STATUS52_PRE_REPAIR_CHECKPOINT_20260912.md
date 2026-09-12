# Pass 219 I163 Status-52 — Pre-Repair Checkpoint

Date: 2026-09-12

## Repository state

```text
base main: 506034954c3056f288e654b0c6c62cde54cbb3d3
branch: agent/pass219-exact-main-inherited-link-closure-20260912
merge target: main
PR: #439 — Pass 219: repair exact-main inherited PQC link closure
pre-repair head: 494d6422c74345026652e580fd7e63f7cfcc56df
compare: ahead 11, behind 0
```

PR #439 is open, non-draft, and mergeable. No implementation file is changed by this checkpoint.

## Single active problem

The only active repair target is the I163 Python/full-runtime exact call failure:

```text
RuntimeError: exact ABI failed: status=52 decision=52
```

The purpose of this cycle is strictly to establish the exact repository-defined producer and meaning of `52` before any implementation change.

## Frozen evidence

The following remain frozen and must not be revisited unless the eventual I163 repair changes one of their direct inputs:

```text
I149: PASS
I166: PASS
I179: PASS
global canonical defaults: PASS
cross-modal reversible state manifold: PASS

I163 before Python/full-runtime call:
  Pass159 build/reverse semantics: PASS
  cumulative exact ABI and host link support: PASS
  native reverse conformance: PASS
  x86-64 exact identity probe: PASS
  ARM64 exact identity probe/parity: PASS
  full hhs_runtime c-abi build/link: PASS
  hhs_runtime_init export: PASS
```

## Authority constraints

Do not expose or revive a hidden mutation surface. Do not weaken the environmental-PQC/VM81 boundary. Do not change VM81 transition authority, Hash72/Hash216 semantics, or PQC policy merely to make the probe pass.

## Next action

1. Read the exact failing I163 job log at run `34706363003`, job `103587014706`.
2. Trace `status=52 decision=52` to the exact producer and data layout in repository code.
3. Stop after the diagnosis is evidence-backed.
4. Only then perform one narrowly scoped repair.
5. Run I163 only.
6. If that repair succeeds, immediately create a post-repair restartable checkpoint before beginning any other work.
