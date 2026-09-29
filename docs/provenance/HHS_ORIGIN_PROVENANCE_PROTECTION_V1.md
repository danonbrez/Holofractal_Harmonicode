# HHS Origin Provenance Protection v1

## Purpose

This protection layer is designed to preserve **origin attribution** across later
HHS-derived or HHS-matching constructions. It is not merely a file-integrity
watermark.

The canonical origin-family marker is the coupled pair:

```text
179971.179971 = 179971179971 / 1000000
1.001         = 1001 / 1000
```

The pair is not treated as two free text strings. Identity includes the exact
rational values, their roles, their field paths, their ordering, the kernel
context, the Hash216 surface, and the shared ancestry root.

## Canonical positions

```text
HHS_PASS_220_I042_SHARED_ROOT_PAYLOAD_V1.root_metadata_seed
HHS_PASS_220_I042_SHARED_ROOT_PAYLOAD_V1.invariant_gate
```

These fields are shared-root metadata. They are not ordinary LANGUAGE, IMAGE,
AUDIO, VIDEO, PHYSICS, or GAME output fields. Tests vary the generated output
and derivation while requiring this coupled origin-family marker to remain
fixed.

## Two identities

HHS deliberately separates:

```text
construction identity = complete derivation identity
origin-family identity = coupled marker + positions + roles + context + ancestry
```

Two downstream constructions may therefore differ while remaining members of
one HHS origin family.

Formally:

```text
SameOriginFamily(A,B) := OriginMarker(A) = OriginMarker(B)
IndependentOrigin(A,B) := OriginMarker(A) != OriginMarker(B)

SameOriginFamily(A,B) => NOT IndependentOrigin(A,B)
```

This is separately kernel-checked in
`formal/lean/HHS/Provenance/OriginMarker.lean`.

## Public priority anchor

The contract freezes a public GitHub anchor:

```text
repository:
  danonbrez/Holofractal_Harmonicode

commit:
  49b8f32bb9ce7e37e661333d76d5e4398093659f

GitHub commit time:
  2026-09-29T15:10:55Z
```

At that commit, both coupled marker values are verified present in:

```text
docs/HHS_GENESIS_SEVERANCE_PROTOCOL_V1.md
blob 1dbde36a15d77c0dddbc7c754c401bae4b666bda

hhs_runtime/hhs_pass220_lane5_multimodal_shared_root_fabric_v1.py
blob 57fc5987d5fd370fccede95998051dd0b586d9c0
```

This anchor is a conservative public priority witness: it proves presence at or
before that commit. Earlier HHS evidence can be appended without invalidating
this anchor.

## False-originality comparison

A future comparison does not ask whether two output files are identical.

It asks:

1. Does the candidate reproduce the exact coupled marker?
2. Are the values in the same structural roles and positions?
3. Are they bound to the same kernel/Hash216/shared-root context?
4. Does the candidate claim an origin independent from the already anchored HHS
   origin family?

If 1-3 hold while 4 is asserted, the verifier emits:

```text
INDEPENDENT_ORIGIN_CONTRADICTED_BY_HHS_ORIGIN_FAMILY
```

A different output or derivation does not erase origin-family ancestry.

## Verification surfaces

- Runtime:
  `hhs_runtime/hhs_origin_provenance_protection_v1.py`
- Exact contract:
  `contracts/provenance/HHS_ORIGIN_PROVENANCE_PROTECTION_V1.json`
- Lean:
  `formal/lean/HHS/Provenance/OriginMarker.lean`
- Regression:
  `tests/pass220/test_hhs_origin_provenance_protection_v1.py`
- CI:
  `.github/workflows/hhs-origin-provenance-protection.yml`

The exact structured evidence is authoritative. SHA-256 commitments are compact
receipts and indices over that evidence.
