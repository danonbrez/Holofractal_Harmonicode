# Pass 220 NumPy1 — HARMONICODE Native Array Engine

## Status

`IMPLEMENTED ON RESTARTABLE BRANCH — DIFFERENTIAL CI PENDING`

Branch:

`pass220-numpy1-harmonicode-array-engine`

Base:

`main @ 87b6ae4181ac600198f2d76d0ef951f497f42745`

## Objective

Replace NumPy as an internal numerical authority while preserving NumPy as an
ingress/egress compatibility contract.

The NumPy1 execution rule is:

```text
NumPy-compatible input
        ↓
typed external storage identity
        ↓
exact HARMONICODE scalar state
        ↓
native C11 shape/broadcast/index kernel
        ↓
exact symbolic operation
        ↓
dtype-required deterministic rounding/wrap
        ↓
NumPy-compatible observable output
```

NumPy itself is used only by differential tests.

## Float64 semantics

A float64 ingress value is captured by its exact IEEE binary64 storage bits.
The engine does not perform canonical arithmetic using the host float.

The inherited HHS path is:

1. raw IEEE bits;
2. I031 field split and exact dyadic recovery;
3. exact `Fraction` algebra;
4. exact pre-round result retained;
5. I038 integer-only nearest-even binary64 construction at the NumPy-visible
   dtype boundary;
6. I032/I033 full-phase/palindromic witness available without discarding the
   exact or storage views.

This distinction is required for NumPy compatibility. Exact rational arithmetic
alone would diverge from NumPy if intermediate dtype rounding were omitted.

Signed zero is explicitly preserved for the NumPy1 add/subtract/multiply
surface.

## Value-bound 5,184-character BigInt serialization

Each scalar receives a reversible VM81 offset carrier.

For float64:

```text
64-bit IEEE storage integer
  -> base-9 digits
  -> 81 cells padded with zero offsets
  -> Pass 220 64-character rational-scientific cell tokens
  -> 5,184-character object
```

For int64, the source integer is first transformed with a reversible signed
ZigZag mapping and then follows the same base-9/VM81 path.

This makes the BigInt carrier value-bound. It is not an unrelated normalization
placeholder.

The inherited `offsets_to_bigint` scalar projection remains co-resident, and
the NumPy1 layer independently proves that the VM81 offsets reconstruct the
original IEEE or signed-integer identity.

## Native C11 array kernel

Project:

`native_projects/hhs_pass220_numpy_native_array_kernel`

Implemented:

- rank validation through rank 8;
- positive fixed dimensions;
- NumPy trailing-dimension broadcasting;
- row-major element counts;
- native broadcast index projection;
- scalars as rank-0 arrays;
- no dynamic allocation;
- no floating-point arithmetic.

## NumPy1 compatibility surface

Supported now:

- `int64`
- `float64`
- explicit-dtype `array`
- `asarray`
- `add`
- `subtract`
- `multiply`
- scalar/array broadcasting
- nested-list egress
- float64 raw-bit egress
- int64 arithmetic wrap
- mixed int64/float64 promotion

The runtime implementation does **not** import NumPy.

## Differential validation

The NumPy dependency exists only in:

`tests/pass220/test_hhs_pass220_numpy_harmonicode_array_v1.py`

The gate compares HHS against real NumPy for:

- float64 ingress and egress bit identity;
- exact decimal/scientific ingress rounding;
- 2D broadcasting;
- add and multiply result bits;
- signed zero;
- int64 wraparound;
- mixed int64/float64 promotion;
- reversible 5,184-character scalar carriers;
- I033 palindromic symbolic/full-phase witness validity.

## Current limits

NumPy1 is not a claim of complete NumPy replacement.

Not yet admitted:

- empty dimensions;
- automatic dtype inference;
- bool/unsigned/float16/float32/complex dtypes;
- NaN/infinity arithmetic and payload propagation;
- division and NumPy divide-by-zero behavior;
- slicing/views/strides;
- reshape/transpose;
- reductions;
- matrix multiplication;
- ufunc protocol;
- random/FFT/linalg;
- full ndarray subclass/protocol compatibility.

These should be added through differential behavior gates rather than by
relaxing the exact interior.

## Python phase

Python comes after the NumPy compatibility surface because the Python-native
runtime will need this numerical membrane underneath it.

The intended order remains:

```text
FastAPI native compatibility
        ↓
NumPy external compatibility
        ↓
palindromic symbolic / BigInt HARMONICODE math interior
        ↓
Python syntax/object/call/import compatibility
        ↓
HARMONICODE-native Python execution backend
```

Python source compatibility must not reintroduce host Python numeric authority
around the NumPy/HARMONICODE layer.

## Restart commands

```bash
make -C native_projects/hhs_pass220_numpy_native_array_kernel clean all test
python -m pytest -q tests/pass220/test_hhs_pass220_numpy_harmonicode_array_v1.py
```
