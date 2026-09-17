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

## Lo Shu denominator geometry

The exact row-major denominator tensor is:

```text
4,9,2,
3,5,7,
8,1,6
```

Its standard line sum is 15 and center is 5. The 1.49 C surface returns only integer denominators and never grants host floating-point canonical authority.

## Fibonacci dependency

1.49 reuses the Pass 192 Fibonacci schedule bound:

```text
1 <= fibonacci_depth <= HHS_EXACT_PASS192_FIB_MAX_DEPTH
```

The relation `p+q=2P^(±n)` remains a development candidate until typed exponent/sign lowering is versioned.

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
a2,b2,c2,c4
fibonacci_depth
pass192_fibonacci_version
shared_fourth_power_match
collapse_candidate_admissible
geometry_signature64
```

`collapse_candidate_admissible=1` requires every exact structural check plus:

```text
projected_P4 == 9
```

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
3. all four legal phase slots invert correctly and involutively;
4. all four pair kinds invert orientation involutively;
5. all nine Lo Shu denominators are preserved exactly;
6. the 288 legal `(pair,orientation,phase,cell)` projections admit for `projected_P4=9`;
7. `projected_P4!=9` remains a non-admitted candidate rather than a canonical mutation;
8. illegal phase/pair/orientation/cell/depth inputs fail;
9. inherited Pass 192 Fibonacci version is visible;
10. all canonical authority bits remain zero.
