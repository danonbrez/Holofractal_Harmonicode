# Pass 220 I001 — Lo Shu normalization-offset bigint and 1,2,3 fractal geometry

Status: **FIRST IMPLEMENTATION CHECKPOINT — ADDITIVE / PROJECTION-ONLY**

Schema: `HHS_PASS_220_LO_SHU_NORMALIZATION_V1`

Implementation:
- `hhs_runtime/hhs_pass220_lo_shu_normalization_v1.py`
- `tests/pass220/test_hhs_pass220_lo_shu_normalization_v1.py`

Repository base: `main @ 63cee69390db05bd4b77da1cfd6f1b8cca4d461f`

This checkpoint is additive to the existing Pass 220 universal IDE/runtime contract. It does not replace that contract and does not widen canonical VM81, Hash72, Hash216, or mutation authority.

## 1. Closure calibration

The canonical bigint carrier is a serialization of **normalization offsets**, not the raw Lo Shu address digits.

For state cell `S_i`, closure reference `R_i`, and local modulus 9:

```text
δ_i := (S_i - R_i) mod 9
```

The closed nucleus is therefore the zero point of the coordinate system:

```text
S_i = R_i for every i
=> δ_i = 0 for every i
=> scalar_bigint = 0
```

The raw Lo Shu sequence

```text
4 9 2 / 3 5 7 / 8 1 6
```

is the reference-address geometry. It is not itself the normalized runtime residual.

Checkpoint 1 uses nine local Lo Shu nuclei as the explicit 81-cell reference surface. Later VM81 orbit bindings may replace the reference constructor without changing the normalization ABI.

## 2. Scalar bigint projection

Normalization does not prevent scalarization. The complete offset vector projects injectively to a non-negative integer using the inherited `72² = 5184` carrier radix:

```text
N(δ) := Σ δ_i * 5184^i
```

with every `δ_i` constrained to `0..8`.

Therefore:

```text
closure <=> δ = 0^81 <=> N(δ) = 0
```

and any admitted nonzero residual has `N(δ) > 0`.

The scalar projection round-trips exactly back to the offset vector. Floating-point authority is absent.

## 3. Fixed 5184-character HARMONICODE rational-scientific carrier

The canonical checkpoint object is fixed width:

```text
81 cells * 64 characters/cell = 5184 characters
```

Each cell carries one exact rational-scientific token with the fixed layout:

```text
S NNNNNNNNNNNNNNNNNNNN / DDDDDDDDDDDDDDDDDDDD e S EEEEEEEEEEEEEEEEEEEE
```

where:
- the first `S` is the numerator sign;
- `N` is a 20-digit zero-padded exact numerator;
- `D` is a 20-digit zero-padded positive denominator;
- `e` introduces the exact decimal exponent;
- the second `S` is the exponent sign;
- `E` is a 20-digit zero-padded exponent.

Checkpoint 1 normalization offsets use exact rationals `δ_i/1` at exponent zero. The explicit exponent field keeps the carrier a rational-scientific surface rather than a plain decimal bigint string.

The 5184-character string and scalar bigint are two reversible projections of the same normalized residual state:

```text
VM81 offset vector
<-> exact 5184-character rational-scientific object
<-> non-negative scalar bigint
```

The zero state is represented as 81 exact zero tokens while its scalar projection is the integer `0`.

## 4. Fixed-width composition surface

Because every canonical object is exactly 5184 characters, object boundaries are intrinsic. No separator or length prefix is required:

```text
O1 || O2 || O3
```

has exact length:

```text
3 * 5184 = 15552 characters
```

Checkpoint 1 implements delimiter-free composition and exact splitting. This is suitable as an input-carrier surface for later Hash216 binding, but the helper does **not** claim to mint canonical Hash216 authority or replace the existing Hash72/Hash216 kernel.

## 5. 1,2,3 multiplicative fractalization

The magnitude layer is the exact rank-one multiplication surface:

```text
F = [[1,2,3],
     [2,4,6],
     [3,6,9]]

F_ij = (i+1)(j+1)
```

Its three magnitude triangles are:

```text
T1 = (1,2,3)
T2 = (2,4,6)
T3 = (3,6,9)
```

The Lo Shu nucleus supplies the address layer:

```text
L = [[4,9,2],
     [3,5,7],
     [8,1,6]]
```

so magnitude fixes address through the Lo Shu position map `π_L(m)`.

## 6. Magnitude/address entanglement

The multiplication surface is symmetric:

```text
F_ij = F_ji
```

Therefore reciprocal source coordinates preserve path identity while sharing both scalar magnitude and Lo Shu destination address:

```text
(1,2),(2,1) -> 2
(1,3),(3,1) -> 3
(2,3),(3,2) -> 6
```

The diagonal is the square channel:

```text
(1,4,9) = (1²,2²,3²)
```

and the off-diagonal reciprocal channel is:

```text
(2,3,6)
```

This is the implemented fixed relation between multiplicative ancestry, scalar magnitude, and nucleus address.

## 7. Exact cell-distance geometry

Checkpoint 1 measures Lo Shu geometry with **squared integer distances**, avoiding square roots and floating-point substitution.

The three Lo Shu triangle spectra are:

```text
π_L(1,2,3): squared edge spectrum (2,5,5)
π_L(2,4,6): squared edge spectrum (4,4,8)
π_L(3,6,9): squared edge spectrum (2,5,5)
```

Consequences:

1. `(2,4,6)` forms an exact right-isosceles address triangle because `4 + 4 = 8`.
2. `(1,2,3)` and `(3,6,9)` have identical address-distance spectra even though their magnitudes differ.
3. The 1,2,3 fractalization therefore entangles magnitude scaling against a fixed Lo Shu positional geometry rather than treating magnitude and cell distance as independent variables.

The dependency path is:

```text
source coordinate (i,j)
-> multiplicative magnitude F_ij
-> Lo Shu address π_L(F_ij)
-> exact squared cell-distance geometry
-> normalized offset carrier
-> scalar bigint / 5184-character serialization
```

## 8. Executed validation

Dependency-scoped local test command:

```text
PYTHONPATH=. pytest -q tests/pass220/test_hhs_pass220_lo_shu_normalization_v1.py
```

Result:

```text
11 passed
```

Covered invariants:
- nucleus and VM81 reference close at offset zero;
- zero offset vector projects to scalar bigint zero;
- positive residuals project to positive bigints and round-trip;
- scalar radix is exactly `72² = 5184`;
- fixed rational-scientific serialization is exactly 5184 characters;
- serialization round-trip is exact;
- three fixed objects concatenate to exactly 15552 characters and split without delimiters;
- the `1,2,3 / 2,4,6 / 3,6,9` multiplication surface is exact;
- reciprocal transpose pairs share magnitude/address while retaining source-path identity;
- the three Lo Shu distance spectra are exact;
- floats, out-of-range offsets, malformed serialization, and noncanonical scalar digits fail closed.

## 9. Boundary conditions and next integration

Checkpoint 1 is intentionally projection-only:
- no new canonical admission authority;
- no replacement of the existing C Hash72/u^72 ring;
- no claim that delimiter-free 5184-character concatenation itself is a Hash216 digest;
- no float authority;
- no silent reinterpretation of ordered q=-1 operations as ordinary scalar multiplication.

Next dependency-scoped integration should bind this zero-calibrated object to the existing three-lane VM81 qudit kernel and canonical Hash72 lineage, then test the 5184-character carrier through the actual Hash216 composition path without changing the scalar/offset closure invariant.
