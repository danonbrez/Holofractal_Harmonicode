# Pass 219 Lane 5 Pythagorean Phase Geometry 1.49

## Purpose

1.49 is the first executable lowering of HHS-L144-011 from the Lane 5 white-paper corpus. It does not replace the current exact boundary `B` and it does not gain canonical VM81/Hash72/Hash216 authority.

## Exact constants

```text
a² = 1
b² = 2
c² = 3
a²+b² = c²
c⁴ = 9
```

The native shared-fourth-power relation is represented only through an explicit projection witness:

```text
projected_P4 == c⁴
```

This is a typed projection. It does not globally scalarize every existing `P` surface.

## Phase inversion

Legal phase slots are:

```text
{0,18,36,54}
```

with

```text
inverse(q) = (q+36) mod 72
inverse(inverse(q)) = q
```

## Directional pair geometry

The executable pair kinds are:

```text
AB : (a,b) <-> (b,a)
XY : xy    <-> yx
ZW : zw    <-> wz
PQ : (p,q) <-> (q,p)
```

Each pair carries an orientation bit. Inversion toggles that bit exactly once; a second inversion restores the original orientation. No commutation identity is inferred.

## Lo Shu denominator and complement geometry

The exact row-major denominator tensor is:

```text
4,9,2,
3,5,7,
8,1,6
```

Its standard line sum is 15 and center is 5. Define the exact complement involution:

```text
kappa(d) = 10-d
kappa(kappa(d)) = d
```

The row-major complement cell is the 180-degree opposite cell:

```text
inverse_cell(i) = 8-i
```

so the exact denominator pairs are:

```text
4 <-> 6
2 <-> 8
9 <-> 1
3 <-> 7
5 <-> 5
```

The finite phase anchors are exactly the even corners:

```text
4 -> 0
2 -> 18
6 -> 36
8 -> 54
```

and their complements satisfy:

```text
phase(kappa(d)) = phase(d)+36 mod 72
```

The remaining odd cross plus center are continuation cells:

```text
{9,3,5,7,1}
```

Therefore the executable partition is:

```text
4 finite phase anchors + 5 continuation cells = 9 Lo Shu cells
```

The 1.49 C surface returns only integer denominators and integer phase slots and never grants host floating-point canonical authority.

## Fibonacci dependency

1.49 reuses the Pass 192 native Fibonacci schedule bound:

```text
1 <= fibonacci_depth <= HHS_EXACT_PASS192_FIB_MAX_DEPTH
```

The white-paper test also exercises the already-implemented exact SPI Fibonacci/Pythagorean projection, whose finite square-state ladder begins:

```text
1,2,3,5,8,13,21
```

No finite ratio is replaced by floating Phi.

The relation `p+q=2P^(±n)` remains a development candidate until typed exponent/sign lowering is versioned.

## p/q symmetric-antisymmetric dependency

On the already licensed scalar projection branch:

```text
p+q = 2P
pq = P²-1
```

we obtain:

```text
(q-p)² = 4
sigma := (q-p)/2 in {-1,+1}
```

and, for `P != 0`:

```text
((q-p)P)/(p+q) = sigma
```

Under `p <-> q`, the symmetric invariants `p+q` and `pq` remain unchanged while `q-p` and `sigma` reverse sign. This remains a typed white-paper projection in 1.49; the C ABI does not fabricate concrete `p,q,P` values from the pair-orientation bit.

## Candidate admission

For input:

```text
(pair_kind, orientation, phase_slot, lo_shu_cell_index, fibonacci_depth, projected_P4)
```

the projection receipt contains:

```text
inverse_orientation
inverse_phase_slot
lo_shu_denominator
inverse_lo_shu_cell_index
inverse_lo_shu_denominator
a2,b2,c2,c4
fibonacci_depth
pass192_fibonacci_version
lo_shu_complement_verified
lo_shu_phase_half_turn_verified
finite_phase_anchor_cell
finite_phase_anchor_consistent
continuation_cell
shared_fourth_power_match
collapse_candidate_admissible
geometry_signature64
```

A collapse candidate requires a finite corner whose supplied phase matches its exact anchor, the involutive pair/phase/complement checks, the Fibonacci depth bound, and:

```text
projected_P4 == 9
```

Across the exhaustive finite input cross-product used by the native test:

```text
4 pair kinds * 2 orientations * 4 phases * 9 cells = 288 structural projections
32 exact finite-corner collapse candidates
160 continuation-cell projections
```

The other structurally valid projections remain non-admitted rather than being coerced into collapse.

A `projected_P4` mismatch is represented as a valid receipt with `collapse_candidate_admissible=0`; it does not become a canonical failure or mutation.

## Authority membrane

Required:

```text
candidate_only = 1
canonical_vm81_mutation_authority = 0
canonical_hash72_authority = 0
canonical_hash216_authority = 0
canonical_persistence_authority = 0
floating_point_canonical_authority = 0
```

The authoritative canonical admission path remains inherited and separate.

## Explicit non-derivation

1.49 does not encode `ab-ba=0` from a bare `q=-1` assertion. Any cross-term cancellation requires a separately typed phase/conjugation/zero witness.

## Required tests

The dedicated gate must prove:

1. `1+2=3` and `3²=9`;
2. every Lo Shu row/column/principal diagonal sums to 15;
3. `kappa(d)=10-d` is involutive over all nine Lo Shu cells;
4. finite-corner complement equals the `+36 mod72` phase half-turn;
5. all four legal phase slots invert correctly and involutively;
6. all four pair kinds invert orientation involutively;
7. the exact SPI Fibonacci/Pythagorean ladder and zero residuals remain intact;
8. the licensed `p/q` symmetric-antisymmetric projection closes exactly;
9. all 288 structural projections execute, with exactly 32 collapse candidates and 160 continuation-cell projections for `projected_P4=9`;
10. `projected_P4!=9` remains a non-admitted candidate rather than a canonical mutation;
11. illegal phase/pair/orientation/cell/depth inputs fail;
12. all canonical authority bits remain zero.
