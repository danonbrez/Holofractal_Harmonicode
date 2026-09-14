# Pass 219 SPI — Octonion Reciprocal/Base-Pair Dimensional Lift v1

Status: **ADDITIVE / EXACT / PROJECTION-CANDIDATE ONLY**

Predecessor registry: `HHS_SPI_SCALAR_PROJECTION_REGISTRY_V6`

## 1. Exact source constructor

The source syntax is preserved verbatim:

```text
x=1/y y=-x
(x,y,z,w)²==(Ixy, I-yx, Izw, I-wz)²
```

This contract does not scalarize, normalize, reorder, or independently solve the source expressions.

## 2. Relation separation

The implementation preserves three distinct relation families.

### 2.1 RML2 geometric phase opposite

Inherited same-plane opposite-orientation geometry:

```text
x <-> z
y <-> w
```

These are involutive phase-opposite relations over the gyroscope geometry.

### 2.2 RML4 ordered reciprocal operand

Inherited ordered product-construction relation:

```text
x <-> y
z <-> w
```

This relation identifies the ordered reciprocal operand used by the `xy`, `yx`, `zw`, and `wz` product channels. It is not silently identified with the RML2 geometric phase-opposite relation.

### 2.3 Symbolic base-pair equivalent

The exact source constructor gives the coordinatewise pairing:

```text
x -> Ixy
y -> I-yx
z -> Izw
w -> I-wz
```

These symbolic base-pair values preserve their ordered source identity.

## 3. First-principles dimensional lift

For a primitive source state `s`, define:

```text
D1 = s
D2 = (s, R_phase(s))
D3 = (s, R_phase(s), B(s))
D4 = (s, R_phase(s), B(s), B(R_phase(s)))
```

where `R_phase` is the inherited RML2 geometric phase opposite and `B` is the symbolic base-pair map.

The implementation materializes these four relational coordinates directly.

For dimensions above four:

```text
D[n>4] = recursive reference to the same D4 closure + exact ancestry
```

The higher-dimensional descriptor therefore:

- remains over the same octonion algebra;
- introduces no new octonion basis element;
- does not require exponential table materialization;
- preserves the deterministic closure root and nesting depth.

This is the computational mechanism by which relational dimension can expand while the underlying algebra remains fixed.

## 4. Typed imaginary-phase collapse and restoration

RML4 already represents the gyroscope with exact `u^72` imaginary phase rotations. v1 exposes a typed lossless carrier containing:

```text
source channel
phase72
u^phase72 rotation coordinate
plane
signed orientation
geometric phase opposite
ordered reciprocal operand
symbolic base pair
base pair of the geometric opposite
source relation syntax
```

The complete typed carrier satisfies an exact round trip:

```text
Restore(Collapse(G)) = G
```

for the represented primitive channel and phase coordinate.

The bare `phase72` coordinate alone is not promoted to a lossless representation. Losslessness belongs to the complete typed rotation carrier, because native ordered/orientation ancestry is retained there.

## 5. Compatibility with `a²=1`

The dimensional and gyroscopic state remains native typed structure while the scalar projection retains:

```text
pi_L(a²)=1
```

Therefore:

```text
projection equality != native identity
```

and none of the following is authorized by this contract:

```text
xy == yx
x == z
y == w
native phase state == a²
base-pair equality erases ordered ancestry
```

The unit projection is a normalization layer and does not contradict the richer phase geometry.

## 6. Deterministic redundancy

Each primitive state has independently addressable witnesses for:

```text
native state
geometric phase opposite
ordered reciprocal operand
symbolic base pair
ordinary imaginary/u^72 rotation coordinate
```

The redundancy is intentional. It supplies independent relational witnesses while preserving one underlying octonion algebra.

## 7. Fail-closed conditions

The implementation rejects or fails validation when:

- a primitive phase channel is outside `x,y,z,w`;
- `phase72` is non-integer or outside `0..71`;
- a requested dimension is less than one;
- the RML2 phase-opposite mapping drifts;
- the RML4 ordered reciprocal mapping drifts;
- the symbolic base-pair constructor drifts;
- a typed rotation receipt is altered;
- a bare phase coordinate is claimed sufficient for lossless restoration;
- a higher-dimensional descriptor introduces a new octonion basis;
- the `a²=1` projection is used to collapse native ordered identity;
- VM81/Hash72/Hash216/persistence authority is claimed.

## 8. Authority boundary

This layer has no authority to:

- mutate VM81;
- mint canonical Hash72;
- mint canonical Hash216;
- persist canonical state;
- commute ordered products;
- rewrite the supplied source syntax;
- establish a second transition authority.

## 9. Lifecycle

The cycle follows the canonical development invariant:

```text
FORMALIZE
-> PROVE
-> IMPLEMENT
-> OPTIMIZE
-> CANONIZE
-> ITERATE
```

Here optimization consists structurally of replacing materialized combinatorial higher-dimensional tables with deterministic recursive closure references while retaining exact ancestry. No empirical latency, memory, or compression speedup is claimed until separately measured.

## 10. Implementation

```text
hhs_spi_octonion_dimensional_lift_v1.py
hhs_spi_octonion_dimensional_lift_tests_v1.py
hhs_spi_scalar_projection_registry_v7.py
hhs_spi_scalar_projection_registry_tests_v7.py
.github/workflows/pass219-spi-octonion-dimensional-lift-v7.yml
```
