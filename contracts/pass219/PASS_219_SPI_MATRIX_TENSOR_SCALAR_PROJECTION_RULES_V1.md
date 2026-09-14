# Pass 219 SPI — Matrix/Tensor Scalar Projection Rules v1

Status: additive scalar-projection proof contract
Audited authority base: `main @ 2def7910b99046821f34e1446bcec33ca4fd4090`
Authority boundary: projection-only; no VM81 mutation, canonical Hash72/Hash216 minting, persistence, floating-point authority, or replacement of native ordered matrix/tensor objects.

## 1. Matrix/tensor-defined scalar projection

HARMONICODE permits a specific ordered matrix/tensor expression to inherit a scalar projection when the native equation graph explicitly defines a registered scalar by that expression.

For an exact source-bound edge

```text
S = E_matrix_or_tensor
```

and an already registered exact scalar proof

```text
pi(S) = v
```

the edge licenses the downstream correspondence

```text
pi_edge(E_matrix_or_tensor) = v
```

subject to all of the following:

- the exact source edge and both node identities remain attached;
- the matrix/tensor expression remains a native ordered object;
- no host-language matrix evaluation is required merely to obtain the scalar projection;
- the scalar result does not substitute for the native expression;
- reverse lift is unavailable unless separately proved;
- generic matrices/tensors do not inherit `v` without their own definition edge.

For O2:

```text
a²=(NcalcMatrixPower((ordered 3x3 tensor / fixed I-phase matrix),4))^b⁴
```

and the registered primitive projection

```text
pi(a²)=1
```

therefore license

```text
pi_O2((NcalcMatrixPower(...,4))^b⁴)=1.
```

This is a scalar correspondence only. `NcalcMatrixPower` remains an exact symbolic matrix-power node.

## 2. Symmetric unit-product projection layer

A complete symmetric matrix/tensor projection surface MAY emit a new scalar unit layer when all symmetry-orbit products close exactly to one.

Let `T` be a projected matrix/tensor surface with a declared involutive symmetry map `sigma`. The rule is admitted only when:

```text
sigma(sigma(i)) = i
```

for every component address, every component occurs in exactly one symmetry orbit, and

```text
Product(orbit_k) = 1
```

for every orbit, including fixed-point/self-symmetric cells under their separately typed closure rules.

Then HARMONICODE may emit the projection layer

```text
a² = xy = 1
```

with the following strict interpretation:

```text
pi_layer(a²)=1
pi_layer(xy)=1
```

but NOT

```text
a² ≡native xy
xy ≡native yx
```

and not a permission to commute, reassociate, or reconstruct the native tensor from scalar one.

The `xy -> 1` side is consistent with the frozen Pass129 rational projection, which records three-way membrane closure at residue one when `xy=zw=1` and `x+y+z+w=0`.

## 3. O2 symmetric unit surface

The frozen O2 denominator-magnitude projection is:

```text
((1,1,1),(1,x+y+z+w=0/u⁷²,1),(1,1,1)) where 1=u⁷²
```

The eight perimeter cells have exact unit phase witnesses. The center is not ordinary scalar division; it closes through the inherited native constraint-intersection rule:

```text
0/0=u^0 mod(u^72)=1.
```

After these typed witnesses, the downstream magnitude surface is:

```text
((1,1,1),(1,1,1),(1,1,1)).
```

That projected surface is symmetric under transpose. Its three fixed diagonal cells and three off-diagonal transpose pairs cover all nine cells exactly once, and every orbit product is exactly one. Therefore the symmetric-unit rule emits:

```text
O2 projection layer: a²=xy=1.
```

The native O2 matrix-power expression, ordered phase roles, center closure context, and `xy/yx` distinction remain preserved outside the scalar layer.

## 4. Fail-closed conditions

Projection MUST fail closed when any of the following holds:

- no exact scalar-definition edge exists for the definition-edge rule;
- the target scalar lacks a registered exact projection;
- the claimed symmetric surface lacks a complete involutive symmetry map;
- any component is omitted or appears in more than one symmetry orbit;
- any orbit product is not exactly one;
- any proof requires floating-point equality;
- the projection attempts to commute `xy/yx` or `zw/wz`;
- the projection attempts to replace native matrix/tensor execution or acquire canonical authority.

## 5. Implementation surfaces

The additive proof implementation is:

- `hhs_spi_defined_scalar_projection_rule_v1.py`
- `hhs_spi_symmetric_unit_product_projection_rule_v1.py`
- `hhs_spi_ordered_matrix_projection_witness_v1.py`
- `hhs_spi_ordered_matrix_projection_witness_v2.py`
- `hhs_spi_scalar_projection_registry_v2.py`

O2 is closed only in the scalar-projection layer. Generic `NcalcMatrixPower` and arbitrary matrix/tensor expressions remain non-scalar until they satisfy one of the registered rules above.
