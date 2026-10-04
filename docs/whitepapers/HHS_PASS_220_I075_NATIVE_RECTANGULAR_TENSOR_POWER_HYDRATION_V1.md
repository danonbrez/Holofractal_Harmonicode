# HHS Pass 220 I075 — Native Rectangular Tensor-Power Hydration

## Scope

I075 begins from merged I074 main `45c1dfa8378541fa141de6d19f347cb88cb37d2c`.

It lowers the two held source nodes

```text
MatrixPower[M_wz,x^2]
MatrixPower[M_xy,x^4]
```

into typed native HARMONICODE rectangular tensor-power AST records.

This cycle does **not** define them as ordinary square-matrix powers and does
not evaluate `x^2` or `x^4` as host numeric exponents.

## Native typed operator

Each node carries:

```text
operator = HARMONICODE_RECTANGULAR_TENSOR_POWER
base role
rows = 4
columns = 2
exponent token
ordered source cells
source-node identity
host_evaluated = false
numeric_exponent_evaluated = false
```

The two bases remain:

```text
M_wz =
[ -w*z   z-w ]
[  z-w   w*z ]
[  w*z  -w*z ]
[  y+x   z-w ]

M_xy =
[ -x*y   y+x ]
[  y+x   x*y ]
[  x*y  -x*y ]
[  y+x   z-w ]
```

Ordered cell identity is preserved exactly.

## Structural hydration

Across the two 4x2 nodes:

```text
source cell occurrences = 16
unique symbolic cells    = 6
source nodes             = 2
```

All 16 occurrence witnesses remain attached to the compact six-expression
dictionary so the original ordered bases are reconstructed exactly.

No native algebra is inferred from the dictionary compression.

## Hash216 binding

I075 emits:

```text
PREVIOUS = Hash72(I074 parent roots + source bundle)
CHANGE   = Hash72(typed rectangular tensor-power descriptor)
RECEIPT  = Hash72(shape/provenance/authority witnesses)
```

and concatenates these lanes to a 216-position candidate.

The inherited I065 hydrator must reconstruct and recompress:

```text
3 * 5184 = 15552
```

attached components exactly.

Expanded geometry is validation material and is not persisted by I075.

## Wolfram formalization

Source:

```text
formal/wolfram/pass220_i075_native_rectangular_tensor_power_hydration_v1.wl
```

Connected-kernel result:

```text
status = PASS
checks = 24 / 24
node count = 2
shapes = 4x2, 4x2
cell occurrences = 16
unique cells = 6
host MatrixPower evaluations = 0
numeric exponent evaluations = 0
Hash216 width = 216
full attached components = 15552
```

The formalization intentionally does not call Wolfram `MatrixPower` on the
rectangular bases.

## Lean 4

Native module:

```text
HHS.Pass220.I075
```

in

```text
formal/lean/HHS/Pass220/NativeRectangularTensorPowerHydration.lean
```

proves:

- exactly two native tensor-power nodes;
- both nodes remain 4x2;
- exact operator tags;
- exact exponent tokens;
- exact source-node identities;
- both host-evaluation flags are false;
- `72^2 = 5184`;
- `3 * 5184 = 15552`;
- inherited I074 hydration geometry;
- no authority widening.

The root `HHS.lean` import is installed in the file header.

## Authority

I075 remains candidate-only.

It does not add:

- ordinary host MatrixPower authority;
- rectangular host MatrixPower authority;
- numeric exponent evaluation authority;
- floating-point authority;
- scalar/projection substitution authority;
- VM81 mutation authority;
- canonical Hash72 or Hash216 commit authority;
- canonical persistence authority;
- external-egress authority.

I075 therefore converts the I074 held nodes from opaque strings into typed
native AST objects while preserving the same semantic membrane.
