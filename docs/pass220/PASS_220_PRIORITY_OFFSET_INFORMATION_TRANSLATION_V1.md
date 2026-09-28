# Pass 220 — Priority Offset Information-Preserving Translation v1

## Purpose

The NumPy1 A/B experiment established that scalar-symbol permutation control
plus offset vectorization is a substantially cheaper representation than dense
9x9 substitution tensors for the tested U9 path.

This successor changes the promotion question from:

    is the compact representation faster?

to:

    does the compact representation preserve the complete HHS information
    surface while remaining cheaper?

Speed is supporting evidence. Information preservation is the primary gate.

## Priority-default rule

For a compatible layer:

    try scalar/control symbol + permutation/index vector first
    -> validate exact translation witnesses
    -> admit only if every information gate closes
    -> otherwise fall back to the dense/reference representation

The dense form therefore remains the fail-closed reference path.

## Complete tagged state

Each VM81 position carries a tuple:

    (value, phase, rotation, original_position)

The A/B comparison moves the complete tuple. It is not sufficient for the
numeric value alone to match.

For every ordered channel xy, yx, zw, wz, Arm A and Arm B must preserve:

- value;
- phase;
- rotation;
- original positional provenance;
- zero-spacer provenance;
- inverse recovery of all four fields.

## 5184 and RNA

The translated values must serialize to the same exact 5184-character carrier.

Both arms must then produce the same RNA/Hash72/Digital-DNA phase-lock identity,
including the same bound-state root and ordered phase binding.

The required ordered products remain:

    xy +1
    yx -1
    zw +1
    wz -1

They may not collapse into interchangeable channels.

## Qudit topology

The complete translated value/phase/rotation state is serialized through the
canonical Pass 115 81-cell qudit serializer.

Both arms must agree on:

- serialization root;
- source manifold root;
- position-coordinate bijection;
- topology derivation;
- exact value/phase/rotation reconstruction.

## HNAN gate

HNAN is mandatory for priority promotion.

The existing Pass 219 HNAN gate must report PASS and retain the explicit
ordered identity:

    0=∅=HNAN=x+y-z-w+xy+yx-zw-wz

This is preserved together with the inherited shared-denominator closure:

    0=∅=AB/P⁴∅=HNAN

Neither string is substituted away by the other. The HNAN center expression is
therefore bound explicitly to:

    x+y-z-w+xy+yx-zw-wz

The residual projection must additionally retain:

    terminal = xy+epsilon

The following remain forbidden:

    bare xy terminal
    epsilon elision
    ordered-product commutation
    host-scalar epsilon substitution

This matters because a translation that reproduces visible xy while dropping
epsilon, the explicit zero/EmptySet/HNAN center identity, the inherited
AB/P⁴ denominator closure, or ordered residual information is not
information-preserving.

## Supplied U9 circuit tensor

The complete user-supplied circuit tensor from the original NumPy/U9 experiment
remains mandatory. U9 must preserve its byte-identical payload, nine-position
orbit, inverse closure, and slot provenance.

## Performance evidence

The frozen NumPy A/B evidence remains valid supporting evidence:

- semantic identity: true;
- all four channels faster on host Python;
- U9 closure and circuit payload preserved;
- timing explicitly outside Lane 5.

That evidence cannot override an information-preservation failure.

## Promotion decision

Full promotion requires:

    information preservation PASS
    AND measured performance support PASS

If information passes but performance has not yet been measured for a new layer,
the compact representation is an information-valid candidate but the dense
reference remains the selected default until measurement closes.

If any information gate fails:

    FALL_BACK_TO_DENSE_REFERENCE

## Authority

This experiment is read-only/candidate-only. It does not mint Hash72, persist
Hash216, mutate canonical VM81 state, or bypass HNAN/Lane 5/VM81 admission.
