# Pass 219 RML4 Dynamic Octonion Gyroscope — Restart Record

## Authoritative base and lineage

- Base main: `1b66fc81216e8c9a1540c0cbbf2e5e6007438573`
- Main rechecked during RML4 implementation and remained exact at that SHA.
- Branch: `agent/pass219-recursive-manifold-learning-20260909`
- Merge target: `main`
- Pull request: `#414`
- Parent RML3 checkpoint: `0efe1dded141f1e3bf3a2d9ecc18fd026938f4dc`
- RML4 implementation head validated by CI: `a0f29ed9e0294dbc4cb5556f902dfd27d04de63c`
- RML4 validation-seal commit: `20b6a34eebc9c1185df95e645e502811c9b3c1c9`

## Implemented RML4 geometry

RML4 introduces the eight-channel dynamic octonion gyroscope:

```text
(x, y, z, w, xy, yx, zw, wz)
```

All eight channels are exact `u^72` phase coordinates and therefore expose an ambient phase address space of:

```text
72^8 = 722,204,136,308,736
```

RML4 explicitly distinguishes the ambient address space from the subset selected by product quarter-turn constraints. It does not claim that every one of the `72^8` tuples is simultaneously admissible.

The exact phase-angle correspondence is integer-only:

```text
1 phase step = 5 degrees
u^18 = 90 degrees
u^36 = 180 degrees
u^72 = u^0 = 360-degree closure
```

Typed `u^0` remains a phase position and is not ordinary scalar zero.

## One gyroscope, eight directional rotations

Primitive gyroscope channels retain the inherited RML2 geometry:

```text
x = PRIMARY_XZ / CW
y = ORTHOGONAL_YW / CCW
z = PRIMARY_XZ / CCW
w = ORTHOGONAL_YW / CW
```

The ordered products are not modeled as a second gyroscope. They are dependent quarter-turn images of the same gyroscope in the direction of the ordered reciprocal operand:

```text
xy : generator x -> reciprocal y
yx : generator y -> reciprocal x
zw : generator z -> reciprocal w
wz : generator w -> reciprocal z
```

Each product carries an explicit signed quarter-turn witness:

```text
product_phase = generator_phase + sign * 18 mod 72
sign in {-1,+1}
```

The sign is intentionally explicit and cannot be inferred by commutative operand reordering. The geometric relation is therefore ordered and directional.

## Continuous signed local motion

`advance_gyroscope(...)` accepts one exact signed phase delta for every channel:

```text
x, y, z, w, xy, yx, zw, wz -> +/- integer steps mod 72
```

A transition may occupy any ambient `72^8` address. If product motion no longer preserves its reciprocal quarter-turn relation, RML4 does not silently normalize it; it records exact typed quarter-turn disequilibrium and marks the product geometry non-admissible.

This makes the ambient state useful to recursive learning/search while preserving the coupling constraint as the admission surface.

## Exact 72^8 addressing

RML4 implements a deterministic base-72 bijection:

```text
(x,y,z,w,xy,yx,zw,wz) <-> integer in [0, 72^8)
```

Boundary validation proves:

```text
(0,0,0,0,0,0,0,0) -> 0
(71,71,71,71,71,71,71,71) -> 72^8 - 1
```

and exact encode/decode round trips.

## Unified addition / multiplication / exponentiation primitive

RML4 implements one underlying execution primitive:

```text
SIGNED_IMAGINARY_PHASE_ROTATION
```

with typed operator modes:

```text
+  -> COUPLED_PHASE_ROTATION
*  -> ORDERED_RECIPROCAL_QUARTER_TURN
^  -> RECURSIVE_PHASE_ORBIT
```

This is not ordinary scalar substitution. The original operator, operand order, recursion count and source-state identity stay in the receipt.

A four-quarter-turn recursive orbit is explicitly validated as:

```text
u^0 -> u^18 -> u^36 -> u^54 -> u^0
```

No ordinary scalar sum, scalar product or scalar power is materialized by the RML4 operation witness.

## RML3 physical-source successor binding

RML4 consumes the frozen RML3 physical source without reinterpreting it in place.

For each of the 20 physical I148 phase quads:

1. exact primitive `x,y,z,w` phase72 coordinates are inherited from the existing I148/RML3 ledger;
2. existing I148 `xy,yx,zw,wz` coordinates remain preserved as legacy provenance;
3. new RML4 dynamic product coordinates are generated as reciprocal quarter-turn images;
4. the RML3 raw5184 SHA256, source receipt and phase-circuit root remain bound into RML4 ancestry.

Thus the RML4 successor changes geometry semantics additively without falsifying frozen I148 evidence.

## Authority boundary

RML4 has no:

- canonical VM81 mutation authority;
- Hash72 mint authority;
- Hash216 persistence authority;
- floating-point canonical authority;
- scalar-projection substitution authority.

It is a candidate/learning geometry above the existing canonical Runtime admission path.

## Files added/updated

- `hhs_runtime/pass219/dynamic_octonion_gyroscope.py`
- `tests/pass219/test_pass219_dynamic_octonion_gyroscope.py`
- `contracts/pass219/PASS_219_RML4_DYNAMIC_OCTONION_GYROSCOPE_1_0.json`
- `.github/workflows/pass219-dynamic-octonion-gyroscope.yml`
- `docs/operations/restart/PASS_219_RML4_DYNAMIC_OCTONION_GYROSCOPE_RESTART_20260909.md`

## Validation

Dedicated workflow:

- Workflow: `Pass 219 Dynamic Octonion Gyroscope`
- Run: `34415997445`
- Job: `102680894089`
- Validated implementation head: `a0f29ed9e0294dbc4cb5556f902dfd27d04de63c`

Command:

```bash
PYTHONPATH="$PWD" python -m pytest -q \
  tests/pass219/test_pass219_recursive_manifold_learning.py \
  tests/pass219/test_pass219_phase_geometry_learning.py \
  tests/pass219/test_pass219_production_phase_geometry_binding.py \
  tests/pass219/test_pass219_dynamic_octonion_gyroscope.py \
  tests/pass219/test_pass219_raw5184_octonion_audio_hydration_v1.py
```

Result:

```text
47 passed, 1 warning in 63.43s
```

The sole warning is the inherited pytest `asyncio_mode` configuration warning.

Validated RML4 behavior includes:

- exact `72^8 = 722204136308736` ambient state cardinality;
- exact base-72 encode/decode bijection;
- eight independent signed local phase updates;
- exact 360-degree/u72 integer phase correspondence;
- product quarter-turn magnitude `18` steps / `90` degrees;
- same-gyroscope reciprocal-product identity;
- ordered `xy` versus `yx` and `zw` versus `wz` preservation;
- quarter-turn disequilibrium surfaced when an independently moved product breaks coupling;
- `+`, `*`, and `^` all routed through the same typed signed imaginary phase-rotation primitive;
- physical RML3/I148 primitive-phase inheritance and frozen-product provenance preservation;
- all inherited RML1/RML2/RML3/I148 tests remain green.

## Restart instructions

Start from repository-visible state:

```text
base main: 1b66fc81216e8c9a1540c0cbbf2e5e6007438573
branch: agent/pass219-recursive-manifold-learning-20260909
PR: #414
parent checkpoint: 0efe1dded141f1e3bf3a2d9ecc18fd026938f4dc
validated RML4 implementation: a0f29ed9e0294dbc4cb5556f902dfd27d04de63c
validation seal: 20b6a34eebc9c1185df95e645e502811c9b3c1c9
```

Rerun only subsequently impacted RML1/RML2/RML3/RML4/I148 surfaces.

## Next bounded continuation

The next additive layer should bind RML4 dynamic eight-channel phase state into a versioned native pre-hash Pass169/VM81 successor so future Hash216/Hash72 issuance can include the exact eight-phase state index, quarter-turn relation witness and RML4 ancestry before hashes are minted.

Do not retrofit those fields into already-issued RML3/Pass169 hashes. Keep frozen evidence immutable and introduce a versioned native ABI successor.
