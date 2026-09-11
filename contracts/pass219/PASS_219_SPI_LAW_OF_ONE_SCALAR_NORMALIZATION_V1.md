# Pass 219 SPI — HARMONICODE Law-of-1 Scalar Normalization v1

Status: additive scalar-projection proof contract  
Audited predecessor base: `main @ 2def7910b99046821f34e1446bcec33ca4fd4090`  
Authority boundary: scalar projection only; no VM81 mutation, native expression collapse, canonical Hash72/Hash216 minting, persistence, floating-point authority, native commutation/reassociation, or reverse substitution.

## 1. Law-of-1 source clause

The additive HARMONICODE symmetry-normalization clause is preserved exactly:

```harmonicode
1=a²,x⁴,y⁴,z⁴,w⁴,∆,P²-pq,t³-t,m²-m,e^x²O,c²-b²,b²/2u⁷²
```

This clause defines a scalar projection class. It does **not** assert that the native source nodes are interchangeable.

## 2. Primary Law-of-1 invariant

For every registered scalar layer `L` and every admitted member `E` of the Law-of-1 class:

```text
pi_L(E)=1_L.
```

The primary members are:

```text
a²
x⁴
y⁴
z⁴
w⁴
∆
P²-pq
t³-t
m²-m
e^x²O
c²-b²
b²/2u⁷²
```

Each member retains exact source identity, proof ancestry, projection profile, lost-information declaration, and authority boundary.

## 3. Universal denominator unit

`∆` is the system-wide denominator identity for scalar projection and normalization:

```text
D_univ := pi(∆)=1.
```

For any exact scalar projection `v` in an admitted layer:

```text
UniversalNormalize_L(v)=v/pi_L(∆)=v/1=v.
```

This is a scalar normalization rule. It does not authorize rewriting native divisions by `∆`, deleting a native `∆` node, or replacing native denominator semantics with host rational arithmetic.

The repository basis is the frozen Pass 129 common rational residue:

```text
∆=t³-t=m²-m=xy=P²-pq=q-P=P-p,
∆ != 0.
```

Together with `∆²=∆`, the nonzero exact rational projection closes at:

```text
pi(∆)=1.
```

## 4. Local scaling factor

`a²` is the local scalar scale for each admitted projection layer. Its local scale is bridged to the universal denominator:

```text
S_L := pi_L(a²)=pi_L(∆)=1.
```

The bridge is therefore:

```text
a²=∆=1
```

**only in the registered scalar projection relation**.

Native `a²` and native `∆` remain distinct typed source nodes.

Local normalization is:

```text
LocalNormalize_L(v)=v/pi_L(a²)=v/1=v.
```

The local-to-global bridge then composes as:

```text
v/pi_L(a²)
→ v/1
→ v/pi_L(∆)
→ v/1
→ v.
```

Thus local scaling and global denominator normalization share one exact unit without scalar drift.

## 5. Local/global normalization law

For every valid scalar normalization edge `L_i -> L_j`:

```text
N[L_i -> L_j](1_Li)=1_Lj.
```

The stronger hierarchy statement is:

```text
pi_L(a²)=pi_L(∆)=1
```

for every admitted local scalar layer, and:

```text
N[L_i -> L_j](pi_Li(∆))=pi_Lj(∆)=1.
```

Therefore the unit is both:

- locally represented by the scale `a²`, and
- globally represented by the denominator `∆`.

## 6. Repository-backed Law-of-1 members

### 6.1 `a²`

The primitive scalar registry already proves:

```text
pi(a²)=1.
```

### 6.2 `∆`, `P²-pq`, `t³-t`, `m²-m`

Pass 129 places these surfaces in the same nonzero rational residue class:

```text
∆=t³-t=m²-m=xy=P²-pq.
```

The scalar residue is exactly one, without solving native `t` or native `m` as conventional scalar roots.

### 6.3 `c²-b²`

From:

```text
pi(c²)=3
pi(b²)=2
```

it follows in the registered scalar difference projection that:

```text
pi(c²-b²)=1.
```

## 7. Operator-supplied source-bound unit members

The following are registered by this additive projection contract unless a stronger repository derivation later supersedes their ancestry:

```text
x⁴
y⁴
z⁴
w⁴
e^x²O
b²/2u⁷²
```

`e^x²O` and `b²/2u⁷²` are preserved exactly as source-bound expressions. No conventional precedence or algebraic reinterpretation is inserted by this projection contract.

The quartic phase members project to unit without collapsing native `x,y,z,w` phase identities.

## 8. Conditional `xy` unit bridge

`xy` is not added to the unconditional operator clause. It joins the same scalar unit class only when a separately validated projection profile permits it.

The current valid bridge is the symmetric-unit matrix/tensor rule:

```text
a²=xy=1
```

as a scalar projection layer only.

This does not imply:

```text
native a² ≡ native xy
xy = yx
```

and it does not commute or reassociate ordered phase products.

## 9. Symmetric matrix/tensor interaction

A complete symmetric matrix/tensor projection surface whose every symmetry-orbit product is exactly one may emit a scalar unit layer. For O2, the validated downstream magnitude surface is:

```text
((1,1,1),(1,1,1),(1,1,1))
```

which supports the conditional scalar layer:

```text
a²=xy=1.
```

That unit layer then inherits the same universal denominator:

```text
∆=1.
```

Hence the local matrix/tensor scale is `a²`, while `∆` remains the universal denominator unit across the layer boundary.

## 10. Finite projected-product closure

For any finite sequence of already-admitted Law-of-1 scalar members:

```text
Product(pi_L(E_k))=Product(1)=1.
```

The product is formed **after scalar projection**. It cannot be used to reorder, multiply, commute, or reassociate native HARMONICODE objects.

## 11. Fail-closed rules

The Law-of-1 projection must fail closed if a caller attempts to:

- use floating-point equality;
- promote `a²=∆` to native identity;
- rewrite native division by `∆` merely because its scalar projection is one;
- commute `xy/yx` or any other ordered products;
- infer that all native Law-of-1 source expressions are identical;
- reverse-lift scalar one without a separately registered unique lift;
- acquire VM81 mutation or canonical state authority;
- mint canonical Hash72/Hash216 lineage from a scalar proof receipt.

## 12. Implementation surfaces

The additive implementation is:

- `hhs_spi_law_of_one_projection_rule_v1.py`
- `hhs_spi_law_of_one_projection_rule_tests_v1.py`
- `hhs_spi_scalar_projection_registry_v3.py`
- `hhs_spi_scalar_projection_registry_tests_v3.py`
- `hhs_spi_scalar_projection_registry_v4.py`
- `hhs_spi_scalar_projection_registry_tests_v4.py`

The predecessor O2 projection rules remain independently implemented in:

- `hhs_spi_defined_scalar_projection_rule_v1.py`
- `hhs_spi_symmetric_unit_product_projection_rule_v1.py`
- `hhs_spi_ordered_matrix_projection_witness_v1.py`
- `hhs_spi_ordered_matrix_projection_witness_v2.py`
- `hhs_spi_scalar_projection_registry_v2.py`

The hierarchy is therefore:

```text
native constraint graph
  -> registered scalar projection
  -> local scale a²=1
  -> local/global bridge a²=∆=1
  -> universal scalar denominator ∆=1
  -> unit-preserving cross-layer normalization
```

with native identities and canonical execution authority preserved outside the scalar projection membrane.
