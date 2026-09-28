# Pass 220 — Native Lane 5 Priority-Offset A/B v1

## Purpose

This cycle moves the already-selected scalar/control-symbol + offset-vector
representation from the host-Python experiment into an additive exact-C
candidate hydration surface.

It does **not** create a new phase engine.

The native surface is bound to the existing literal firing constructor:

```text
sigma_n = 8 + 16 n (mod 72)

8 -> 24 -> 40 -> 56 -> 72 -> 16 -> 32 -> 48 -> 64 -> 8
```

and to the existing Pass 219 Lane 5 mediation boundary:

```text
hhs_exact_pass219_lane5_mediate_candidate
```

which already executes the global HNAN, P^(x^2), polarity and conservation
preflights.

## Native representation

Each VM81 position remains an explicit counted tagged cell:

```text
(counted_value, phase72, rotation4, source_index)
```

The compact transform only moves complete tagged cells through the exact U9
permutation selected by the Lo Shu scalar control. It does not substitute,
recompute, scalarize, or discard any lane value.

The four channel factors remain:

```text
xy = +1
yx = -1
zw = +2
wz = -2
```

over the existing centered Lo Shu controls:

```text
-1, 4, -3,
-2, 0,  2,
 3,-4,  1
```

## Candidate hydration

The new exact-C surface is:

```text
hhs_exact_pass220_priority_offset_transform
hhs_exact_pass220_priority_offset_inverse
hhs_exact_pass220_priority_offset_prepare_lane5_request
hhs_exact_pass220_priority_offset_mediate
```

The caller supplies an existing Lane 5 request template. The adapter preserves
its parent Hash216 references, capability references, RNA signatures and
authority membrane. Candidate/hydration signatures are deterministically bound
to the complete transformed tagged state.

The adapter does not mint canonical Hash72 or Hash216 state.

## HNAN admission

`hhs_exact_pass220_priority_offset_mediate` calls the existing Lane 5
mediation function. Candidate success therefore requires the inherited HNAN
global preflight and returns only a candidate-ready receipt.

The witness requires:

```text
inverse round trip exact
counted values preserved
phase coordinates preserved
rotations preserved
provenance preserved
literal firing pattern bound
HNAN zero-sum closure passed
VM5184 bound
RNA cell wall bound
```

Any failed invariant rejects the candidate.

## Dense reference versus compact candidate

Dense 9x9 substitution matrices remain benchmark/reference-only.

Per four-channel 81-cell state, logical control storage is:

```text
dense:   9 blocks * 4 channels * 9 * 9 = 2916 matrix cells
compact: 324 vector references + 36 scalar controls = 360 controls
```

The native benchmark compares:

```text
dense transform -> Lane 5 request -> HNAN mediation

versus

compact native transform -> Lane 5 request -> HNAN mediation
```

on the same process, compiler, request template and tagged state.

Absolute timings are observational. They are not canonical HHS state.

## Authority

This entire cycle remains candidate-only.

It adds no:

- VM81 mutation authority;
- Hash72 mint authority;
- Hash216 persistence authority;
- canonical persistence authority;
- floating-point canonical authority;
- alternate firing schedule;
- alternate HNAN closure;
- dense-substitution runtime authority.
