# Pass 220 — Lo Shu / Pythagorean Collapse Implementation + Optimization Pre-Checkpoint

**Date:** 2026-09-17  
**Branch:** `agent/pass219-u72-unified-scalar-closure-20260917`  
**Merge target:** `main`  
**PR:** `#485`  
**Documentation post-checkpoint:** `032106cf9be16776037c2ce75ec8ec6bf536b9ac`

## Authorized implementation task

Resume implementation/optimization only after the Pass 220 documentation freeze. The runtime work must inherit the formalized Lo Shu nucleus controller and preserve exact behavior against the existing authoritative/reference paths.

### Required invariants

- exact BigInt/rational state identity;
- Lo Shu address/operation identity;
- reciprocal phase exchange `Az=Bx` and `Bz=Ax`;
- `A != B` and distinct ordered `AB` / `BA` dependency histories;
- typed nucleus closure `AB=P^4=BA` without raw commutativity;
- cell `7` collapse-tensor / nested normalization constraint;
- cell `9` invariant boundary `P^4=c^4=9`;
- cell `6` normalization and exact nonary fold;
- `u^72` dynamic resonance state;
- exact reconstruction through the existing base-72 / phase-nonary BigInt path;
- inherited VM81 / C++ RNA / Hash72 / Hash216 authority boundaries;
- no canonical floating-point authority.

## Task order

1. Inspect the existing `u^72` dynamic-state optimization and dependency-scoped workflow history.
2. Repair only demonstrated failures in the existing native/fold path.
3. Add the smallest exact Pass 220 runtime witness needed to enforce/test the nucleus controller over dynamic updates.
4. Compare every optimized update against the inherited exact reference path.
5. Add fail-closed negatives for broken reciprocal exchange, broken cell-7 closure, wrong `P^4` boundary, and BigInt mismatch.
6. Run/trigger dependency-scoped validation.
7. Commit a post-task restart checkpoint before any subsequent optimization cycle.

## Restart state

- base commit: `032106cf9be16776037c2ce75ec8ec6bf536b9ac`
- branch: `agent/pass219-u72-unified-scalar-closure-20260917`
- target: `main`
- PR: `#485`
- validations inherited but still externally queued at the preceding documentation head:
  - `HHS Lane 5 Whitepapers v1` run `35214737008`
  - `Pass 219 Fold Primitive Probe` run `35214737106`
- next action: inspect the current probe implementation and prior failed native/fold workflow logs before modifying code.
