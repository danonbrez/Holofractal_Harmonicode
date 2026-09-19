# Pass 219 Lane 5 — T5184 Ordered Phase-Support Optimizer 1.49

## Status

Implementation contract for the exact Lane 5 successor to 1.48.

## Inheritance

This contract is additive. It inherits:

- Lane 5 1.48 full-manifold BigInt candidate routing and authority boundaries;
- Pass 220 I019 operation64 decoding over the ordered `{x,y,z,w}^3` RNA/Digital-DNA alphabet;
- the repaired ordered q=-1 witness `(xy,yx,zw,wz)=(+1,-1,+1,-1)`;
- the gate-pair wire resolution `z=x`, `w=y`, hence `zw=xy` and `wz=yx`;
- exact CPU/VM81 replay as the admission boundary.

It does not replace the complete 5,184-character serialized-operand binding, Hash216 state identity, or signed environmental VM81 admission.

## Exact support theorem

With operation64 encoded lexicographically over `{x,y,z,w}^3`, the first two symbols carry one of the ordered phase products `xy`, `yx`, `zw`, `wz` exactly at:

```text
{4,5,6,7,
 16,17,18,19,
 44,45,46,47,
 56,57,58,59}
```

The corresponding exact 64-bit support mask is:

```text
0x0f00f000000f00f0
```

Therefore:

```text
support_per_cell = 16
bypass_per_cell = 48
support_fraction = 16/64 = 1/4
phase-specific bypass fraction = 48/64 = 3/4
support_VM81 = 81*16 = 1296 = 36^2 = 18*72
bypass_VM81 = 81*48 = 3888
count(xy)=count(yx)=count(zw)=count(wz)=81*4=324=18^2
```

The word “bypass” is narrowly typed: it means **no ordered-phase-specific slot check is scheduled at that local64 address**. It does not mean that the serialized character, Hash216 identity, route witness, contradiction checks, or final CPU replay may be skipped.

## Ordered-product preservation

The optimizer may use the wire mirror:

```text
zw = xy
wz = yx
yx = -xy
```

to reuse the exact representative phase class, but it MUST preserve the ordered phase code in its receipt. It may not collapse all four labels to an unordered sum.

The native classification is:

| local64 | ordered phase | sign | representative |
|---|---|---:|---|
| 4..7 | xy | +1 | xy |
| 16..19 | yx | -1 | yx |
| 44..47 | zw | +1 | xy |
| 56..59 | wz | -1 | yx |
| all other local64 positions | none | 0 | none |

## Optimization rule

A Lane 5 caller that needs phase-specific inspection SHOULD iterate the 16-entry support table directly rather than scan all 64 local operation addresses and discover 48 non-phase slots.

Across VM81, this changes the structural phase-inspection schedule from:

```text
81*64 = 5184 inspected local slots
```

to:

```text
81*16 = 1296 phase-specific inspections
```

with exactly:

```text
5184 - 1296 = 3888
```

phase-specific slot inspections avoided.

This is an exact structural work reduction of 75% **for the phase-specific slot-inspection subroutine only**. It is not a claim of 75% whole-runtime speedup.

## Authority boundary

The 1.49 optimizer is candidate-only and MUST report:

```text
canonical_vm81_mutation_authority = 0
canonical_hash72_authority = 0
canonical_hash216_authority = 0
canonical_persistence_authority = 0
floating_point_canonical_authority = 0
requires_exact_cpu_vm81_replay = 1
full_state_identity_still_required = 1
serialized_operand_binding_still_required = 1
```

No timing measurement participates in canonical selection.

## Required executable validation

The dedicated gate MUST prove:

1. all 64 operation addresses classify exactly;
2. the support table is strictly ordered and contains 16 unique entries;
3. reconstructing the bit mask yields `0x0f00f000000f00f0`;
4. every one of 81 cells maps to exactly 64 global positions;
5. the full global index range is `0..5183`;
6. support count is exactly 1,296 and bypass count exactly 3,888;
7. each ordered phase occurs exactly 324 times;
8. `zw` maps to the `xy` representative without losing its `zw` ordered label;
9. `wz` maps to the `yx` representative without losing its `wz` ordered label;
10. invalid cell and local64 addresses fail closed;
11. no floating-point canonical authority is introduced;
12. Lane 5 1.48 full-manifold candidate routing remains green;
13. Pass 220 I019 serialized ordered-phase binding remains green;
14. the sealed Wolfram audit input/output hashes reproduce and report 18/18 exact checks.

## Reproducible independent audit

Repository evidence:

```text
evidence/pass219/lane5_t5184_phase_support_1_49.wl
evidence/pass219/lane5_t5184_phase_support_1_49.output.json
evidence/pass219/lane5_t5184_phase_support_1_49.receipt.json
```

The audit is exact integer/matrix arithmetic only.
