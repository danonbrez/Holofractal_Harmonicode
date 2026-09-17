# Pass 219 — `u^72` / H36 Dynamic Scalar Optimization V1

**Version:** 1.0  
**Date:** 2026-09-17  
**Status:** additive exact optimization contract  
**Authority:** optimization/candidate proof only except where the inherited signed environmental VM81 boundary is explicitly invoked

## 1. Purpose

This contract binds the existing exact nonary/phase BigInt serialization, VM5184 carrier, C++ RNA candidate route, and signed environmental VM81 admission into one dynamic `u^72` optimization cycle without introducing a second state representation or a second canonical mutation path.

The governing correspondence is:

```text
BigInt serialization
== exact scalar/rational state
== phase/nonary factorization
== Lo Shu cell/operation identity
== VM5184 carrier identity
```

within the typed HHS semantics and applicable authority boundary.

## 2. Exact geometry

The implementation MUST preserve:

```text
8*9 = 72
8^2*9^2 = 64*81 = 5184 = 72^2
H36(5184) = 5184^36 = 72^72
```

The active dynamic period is:

```text
u^0 == u^72
```

with canonical quarter positions:

```text
0,18,36,54
```

and reciprocal half-turn:

```text
s <-> s+36 mod 72
```

## 3. Exact scalar/CRT identity

For every local resonance slot:

```text
s in Z_72
phase(s)  = s mod 8
nonary(s) = s mod 9
glyph(s)  = CRT(phase(s),nonary(s))
```

The existing local CRT law MUST prove:

```text
glyph(s) = s mod 72
```

Thus the `u^72` slot, local scalar glyph, ordered phase residue, and nonary residue are exact mutually recoverable factors of one state.

## 4. H36 reciprocal dependency

For every:

```text
0 <= s < 36
```

the paired state at `s+36` MUST satisfy:

```text
nonary(s+36) = nonary(s)
phase(s+36)  = phase(s)+4 mod 8
glyph(s+36)  = glyph(s)+36 mod 72
```

The H36 reciprocal relation therefore changes the phase half-turn while preserving the nonary coordinate.

## 5. Dynamic BigInt update

At depth `m=72`, define:

```text
M8 = 8^72
M9 = 9^72
M  = 72^72 = M8*M9
```

and CRT idempotents:

```text
E8 == 1 mod M8; E8 == 0 mod M9
E9 == 0 mod M8; E9 == 1 mod M9
E8+E9 == 1 mod M
```

For coordinate `i`, an exact update from `(p_old,n_old)` to `(p_new,n_new)` is:

```text
H' = H
   + (p_new-p_old)*8^i*E8
   + (n_new-n_old)*9^i*E9
   mod M
```

The implementation MUST validate the claimed old coordinate against the current BigInt residues before applying the delta. Stale or forged dependency metadata MUST fail closed.

## 6. Reference equivalence

Every optimized transition MUST be checked against the inherited full exact serializer:

```text
optimized_bigint == reference_bigint
```

and against the exact local glyph stream:

```text
bigint_from_glyph_stream(glyphs) == optimized_bigint
```

No floating-point comparison may participate in this equality.

A full cycle MUST close exactly after 72 transitions:

```text
H_72 == H_0
phase_72 == phase_0
nonary_72 == nonary_0
glyph_stream_72 == glyph_stream_0
```

## 7. VM5184 dependency binding

Each dynamic state MUST be packed through the inherited 81×64 VM5184 binding. The selected resonance glyph determines the exact inherited six-lane `pq/qp` metadata record under the V1 deterministic lane rule.

The frame MUST reject any mismatch among:

```text
BigInt
72-glyph stream
phase/nonary residues
u^72 resonance slot
pq/qp lane metadata
```

This binds metadata dependency geometry to the scalar state rather than treating metadata as detached logging.

## 8. Optimization witness

For one complete V1 cycle, the reference path evaluates 72 coordinates for each of 72 transitions:

```text
reference_coordinate_visits = 72*72 = 5184
```

The optimized delta path changes exactly one coordinate per transition:

```text
optimized_coordinate_updates = 72
```

Therefore the exact logical work reduction is:

```text
avoided_coordinate_visits = 5184-72 = 5112
optimized/reference = 1/72
```

This is a deterministic algorithmic work-count statement, not a wall-clock speed claim.

## 9. Candidate C++ RNA validation

When `HHS_PASS219_BIGINT_RNA_NATIVE_PROBE` is supplied, the anchor states:

```text
0,18,36,54,72
```

MUST traverse the existing candidate-only C++ RNA VM5184 route and preserve:

```text
deterministic replay
raw frame identity
import/export identity
Hash216 reference verification
transition identity
closed authority
```

No new mutation or receipt primitive is authorized.

## 10. Signed environmental VM81 validation

When `HHS_PASS219_BIGINT_ENVIRONMENT_NATIVE_PROBE` is supplied, the same anchor states MUST use the existing sole public canonical mutation boundary:

```text
hhs_exact_pass219_vm81_environment_admit_signed
```

Successful commits MUST re-decode to the same exact BigInt and dependency-bound frame. Parent/child Hash216 identities, signature/environment verification, inherited RNA authority, and authority handoff MUST remain valid.

The optimizer itself gains no canonical mutation or receipt authority.

## 11. Negative requirements

The implementation MUST reject at minimum:

```text
stale old phase/nonary coordinate
metadata not entailed by the scalar resonance slot
out-of-range BigInt
out-of-range coordinate
out-of-range phase/nonary digit
float-derived canonical state
```

Inherited native negative cases for constraint failure, bad parent, missing input, and invalid pass path remain controlling at signed environmental admission.

## 12. Authority membrane

This contract MUST NOT add:

```text
new canonical VM81 mutation authority
new canonical Hash72 minting authority
new canonical Hash216 persistence authority
new canonical receipt authority
new PQC key authority
new receipt-clock authority
floating-point canonical authority
```

Canonical mutation remains owned by the inherited signed environmental VM81 admission boundary.

## 13. Acceptance

V1 is accepted only when the dependency-scoped tests establish:

```text
all 72 optimized transitions equal the full exact reference
full u^72 cycle closes exactly
36 H36 reciprocal pairs preserve nonary and invert phase
quarter slots remain exact
metadata dependency tampering fails closed
candidate C++ RNA anchors pass when native probe is present
signed environmental VM81 anchors pass when native probe is present
no authority escalation occurs
```

Only after these conditions pass may observational performance measurements be used to characterize the optimization.
