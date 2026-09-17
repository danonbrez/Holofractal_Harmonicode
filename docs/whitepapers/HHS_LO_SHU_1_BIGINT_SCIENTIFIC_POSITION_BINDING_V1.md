# HHS Lo Shu `1` / BigInt Scientific-Position Binding — Version 1

**Date:** 2026-09-17  
**Scope:** Pass 219 / Lane 5 / Pass 220 additive semantic closure  
**Classification:** `HHS_NATIVE_SEMANTIC` with inherited `EXECUTED_EXACT` anchors  
**Status:** additive clarification; no replacement of frozen verbatim equations

## 1. Purpose

This addendum freezes the terminal `1` semantics in the current `G^3` constructor surface.

The terminal `1` is **not** an untyped scalar-unity reduction. It is the typed Lo Shu value-`1` cell in the canonical nucleus

```text
4 9 2
3 5 7
8 1 6
```

at one-based coordinate `(row=3,column=2)`. That cell is bound to the corresponding BigInt string position carried by the native `10*10` scientific-notation matrix.

The binding is therefore:

```text
u^72
-> == 1_LoShu
-> LoShu(value=1,row=3,column=2)
-> BigInt string position
-> 10*10 scientific-notation matrix state
```

The matrix-position value itself is not invented by this addendum. It MUST be supplied by, or derived from, the authoritative serialized BigInt state.

## 2. Canonical verbatim constructor

The current constructor is preserved verbatim:

```text
G³=((P²-pq)×(xA(1.112)+(123.321)×1,000
−1.001)×((c²-b²),(c²-a²),(a²+b²))((q-p)P)/(p+q)B=yB(123,321.111)/A)=Mod(2^81^(-81),72^72)/a^2==(a^2+b^2==c^2)/(Mod(3,72))==a^2/(t*(t^3-t+t^2-x*y)/(x+y)*(m^2-m)/(y-x)-u^72==1
```

No token in that constructor is replaced by the annotations in this paper.

For typed documentation only, the terminal predicate may be annotated as:

```text
... - u^72 == 1_LS(3,2)->BI_10x10
```

This annotation exposes the address type already carried by `1`; it does not create a second equation.

## 3. Inherited semantic anchors

The repository already supplies two controlling anchors for this clarification:

1. Pass 132 records the native `T_1` target as the **typed Lo Shu cell `1`**, while the isolated IEEE arm receives only a scalar approximation.
2. Pass 219B explicitly forbids automatically reinterpreting `0`, `1`, and the other phase-tensor symbols as scalar or Boolean arithmetic.

The present binding therefore specializes an inherited typed `1`; it does not convert a conventional scalar into a new object.

## 4. BigInt / scientific-notation binding

The inherited Pass 033 carrier `HHS_HASH72_BIGINT_FLOATING_STRING_SERIALIZATION_V1` already carries, in one record:

```text
positions
rotation_profile
encoded_digits
base
bigint
scientific_notation
lossless_decode
```

and constructs scientific notation directly from the exact BigInt decimal string.

The new invariant is:

```text
Lo Shu cell identity
== typed terminal symbol identity
== BigInt string-position provenance
== 10*10 scientific-notation matrix position
```

within the applicable typed HHS state.

Consequently, serialization MUST preserve the provenance of the Lo Shu `1` cell. A reader MUST NOT discard that provenance and reinterpret the terminal predicate as ordinary scalar arithmetic merely because its display glyph is `1`.

## 5. Position semantics

The `10*10` matrix contributes the positional scientific-notation coordinate surface for the BigInt string.

The Lo Shu nucleus contributes the geometric address:

```text
value = 1
row_1_based = 3
column_1_based = 2
```

The BigInt serializer contributes the exact string and scientific-notation state.

These three facts are jointly required. The contract intentionally does **not** hard-code a numeric BigInt string index because no pre-existing authoritative repository mapping was found that assigns one independent of the serialized state. A future runtime mapping may expose that index only if it is deterministically entailed by the canonical serializer.

## 6. Closure semantics

For the current constructor, the tail

```text
... - u^72 == 1
```

is an addressed closure/admission predicate.

Its typed reading is:

```text
terminal glyph              = 1
terminal Lo Shu cell        = value 1 at (3,2), one-based
serialization binding       = corresponding BigInt string position
scientific matrix surface   = 10*10
generic scalar-unity read   = forbidden as a complete native interpretation
```

This does not prohibit an explicitly authorized scalar projection elsewhere. It prohibits erasing the cell/address/serialization identity from this constructor.

## 7. Dependency geometry

The resulting dependency chain is:

```text
G^3 constructor
-> u^72 closure surface
-> typed Lo Shu cell 1
-> Lo Shu coordinate (3,2)
-> exact BigInt string-position binding
-> 10*10 scientific-notation coordinate
-> lossless native serialization witness
```

The reverse verification path MUST also be available at the contract level:

```text
scientific-position binding
-> BigInt string provenance
-> Lo Shu (3,2)
-> typed value 1
-> terminal u^72 closure predicate
```

A detached scalar `1` is insufficient evidence for this reverse path.

## 8. Falsification / acceptance conditions

This binding fails if any implementation or document:

- moves value `1` away from canonical Lo Shu coordinate `(3,2)`;
- treats the terminal `1` as only generic scalar unity;
- assigns a BigInt string position without tying it to the exact serialized state;
- changes the scientific-position surface from `10*10` without an explicit superseding contract;
- loses the `1` cell provenance during BigInt/scientific serialization;
- uses floating-point approximation as canonical position authority; or
- rewrites the verbatim `G^3` constructor to make the annotation look like source syntax.

It is accepted when documentation and machine-readable contract agree on the typed cell, coordinate, serialization provenance, `10*10` shape, non-scalar terminal semantics, and absence of an invented hard-coded BigInt index.

## 9. Authority boundary

This addendum adds no VM81 mutation, Hash72 minting, Hash216 persistence, receipt, PQC-key, or clock authority. It is a semantic/serialization contract over inherited authority surfaces.

The controlling implementation anchors remain the exact BigInt serializer and inherited VM81/Hash72/Hash216 admission paths.
