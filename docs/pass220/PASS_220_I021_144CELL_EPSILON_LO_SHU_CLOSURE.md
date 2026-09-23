# Pass 220 I021 — 144-Cell Epsilon / Lo Shu Trinary Phase Closure

**Current implementation mode:** additive exact-reference/runtime proof surface  
**Authority:** no VM81 mutation, Hash72 mint, Hash216 persistence, or canonical admission widening

## 1. Preserved development surfaces

These source identities are preserved verbatim:

```text
2m²/m(2*f^P(MOD144))-Factorial(f)+e==(t³-t)-(m²-m)-mM
f¹⁴⁴=(2^(1/72))u⁷²
(-e,-e+e,+e)=(-e,0,+e)
```

The equality chain remains an indivisible development-preserved HARMONICODE constraint surface. I021 does not independently scalarize, cancel, commute, or reorder it.

## 2. Exact trinary epsilon projection

For an admitted exact projection of local epsilon:

```text
tau(e)=(-e,-e+e,+e)=(-e,0,+e)
sum(tau(e))=0
sgn3(tau(e))=(-1,0,+1) for e>0
```

The directional phase survives while the local mean closes exactly.

For the G72 phase-gear path, the magnitude of `e` remains symbolic and unresolved. Only its ordered orientation `(-e,0,+e)` is routed; no irrational magnitude is converted to a host float.

## 3. Zero-centered Lo Shu router

```text
[-1,+4,-3]
[-2, 0,+2]
[+3,-4,+1]
```

Every row, column, and diagonal sums to zero. Scaling the coefficient geometry by a local epsilon preserves those line sums without erasing the sign/orientation of the local phase.

## 4. 12 x 12 / 144-cell closure

```text
12 x 12=(4 x 3) x (4 x 3)
144=16 x 9
```

Sixteen 3x3 zero-centered Lo Shu blocks tessellate the complete 12x12 surface. Each local block closes independently, therefore the 144-cell surface inherits exact zero row/column/principal-diagonal/global phase balance rather than relying on a floating statistical mean.

## 5. P mod 144 local address

```text
address(P_n)=P_n mod 144
address(P_n) in {0,...,143}
```

The residue is the local harmonic cell coordinate only. Global reconstruction still requires the inherited relationship/lineage carrier; I021 does not reinterpret residue alone as full state identity.

## 6. G72 algebraic-preemption barrier

The term

```text
2^(1/72)
```

is represented natively as the immutable generator:

```text
G72={
  radicand:2,
  root_order:72,
  scalar_evaluation_allowed:false,
  epsilon_magnitude_unresolved:true,
  lo_shu_route_required:true
}
```

There is deliberately no ABI that returns a scalar approximation of `G72`.

The mandatory execution order is:

```text
G72 phase increment
  -> preserve symbolic epsilon magnitude e
  -> emit (-e,0,+e) orientation
  -> route orientation through zero-centered Lo Shu coefficients
  -> chain route signature
  -> advance exactly one tooth
  -> repeat
```

Closure is rejected for teeth 0 through 71. Only the state that has completed all 72 ordered routes may emit the exact closure witness:

```text
routed_cycles=72
144*72=10368
72*72=5184
emergent_binary_coefficient=2
f^10368=2u^5184
```

The coefficient `2` belongs to the completed closure witness. It is not produced by evaluating `2^(1/72)` early, and the `G72` generator remains structurally unresolved even after the closure witness is emitted.

The route chain is order-sensitive. Each transition binds its previous route signature, source tooth, destination tooth, trinary orientation, and Lo Shu coefficients. A skipped or reordered tooth therefore cannot reproduce the canonical final route signature.

Deterministic replay values for this implementation are:

```text
first route signature64 = 16232031834765037332
final route signature64 = 7534065786915196571
```

## 7. Native exact ABI

The native surface consists of:

- `hhs_runtime/include/hhs_pass220_g72_epsilon_lo_shu_gear_1_0.h`
- `hhs_runtime/cpp/hhs_pass220_g72_epsilon_lo_shu_gear_1_0.cpp`
- `tests/pass220/test_hhs_pass220_g72_epsilon_lo_shu_gear_native_v1.c`

The exported transition protocol is:

```text
hhs_exact_pass220_g72_descriptor
hhs_exact_pass220_g72_state_init
hhs_exact_pass220_g72_advance
hhs_exact_pass220_g72_close
```

The native regression proves that closure fails before the 72nd route, every route keeps the generator and epsilon magnitude unresolved, every local/Lo Shu sum remains zero, and the final closure emits `2,5184,10368` only after the complete traversal.

CI additionally rejects native source that introduces scalar `pow`, `sqrt`, `exp`, `float`, or `double` evaluation into this generator module.

## 8. Python exact projection and 144-cell witness

The Python mirror remains:

- `hhs_runtime/hhs_pass220_144cell_epsilon_lo_shu_closure_v1.py`
- `tests/pass220/test_hhs_pass220_144cell_epsilon_lo_shu_closure_v1.py`

It now executes the same 72-tooth ordered generator state machine before constructing the harmonic root closure witness. The earlier direct exponent shortcut is prohibited by regression.

## 9. Acceptance invariants

I021 is accepted only when:

1. `(-e,-e+e,+e)` preserves the exact `(-e,0,+e)` orientation.
2. The zero-centered Lo Shu router has zero row/column/diagonal sums.
3. Sixteen 3x3 blocks produce exactly 144 cells with total phase balance zero.
4. `P mod 144` remains an exact local address.
5. `G72` is immutable, unresolved, ordered, and has no scalar-evaluation ABI.
6. Every G72 tooth routes epsilon orientation through Lo Shu before the next tooth.
7. Closure is impossible before exactly 72 distinct routes.
8. Only the 72-route closure emits the exact coefficient `2` and exponents `5184/10368`.
9. The generator remains unresolved after closure; only the closure witness is exact.
10. No floating-point or canonical mutation/admission authority is introduced.

## 10. Scope

This iteration establishes an executable system-internal generator/route/closure contract. It does not substitute external scalar arithmetic for the HARMONICODE phase-gear semantics and does not widen the existing Lane 5/VM81 authority chain.
