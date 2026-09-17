# Pass 219 Contract — H36 / Hash216 Direct M-Exponent Lattice 1.0

Status: NORMATIVE / ADDITIVE / EXACT / NON-AUTHORITATIVE

## Required exact identities

The implementation SHALL preserve the following prime-exponent coordinates over the native generator basis `(2,3)`:

```text
1    <-> (0,0)
2    <-> (1,0)
3    <-> (0,1)
4    <-> (2,0)
6    <-> (1,1)
8    <-> (3,0)
9    <-> (0,2)
36   <-> (2,2)
72   <-> (3,2)
216  <-> (3,3)
5184 <-> (6,4)
M    <-> (216,144)
```

with:

```text
36 = 2^2 * 3^2
72 = 2^3 * 3^2
216 = 2^3 * 3^3
5184 = 72^2 = 2^6 * 3^4
M = 72^72 = 5184^36 = 2^216 * 3^144
```

## Direct-binding rule

For every existing H36/Hash216 occurrence binding, all of the following addresses SHALL agree exactly:

```text
lane_position72 * 72 + symbol_index72
h36_word144 * 36 + h36_bit36
vm81_cell81 * 64 + vm81_operation64
native_hash72_linear5184
```

The new exponent-lattice witness attaches to this already-shared native address. No semantic translator is permitted or required between H36 and Hash216 for this binding.

Required witness state:

```text
direct_shared_m_binding = 1
translator_required = 0
same_linear5184_identity = 1
factor_support_2_3_only = 1
```

## H36 / Hash72 / Hash216 exponent steps

The implementation SHALL witness:

```text
36 -> 72  : +(1,0)  [one binary exponent step]
72 -> 216 : +(0,1)  [one ternary exponent step]
```

and global closure:

```text
(6,4) * 36 = (216,144)
(3,2) * 72 = (216,144)
```

corresponding to:

```text
5184^36 = M
72^72 = M
```

## Lo Shu local exponent geometry

On the licensed phase-inverted Pythagorean projection inherited from the theorem surface:

```text
a^2 = 1
b^2 = 2
c^2 = 3
P^4 = c^4 = 9
AB = P^4
1 = P^4 / 9
```

The implementation SHALL preserve the local Lo Shu exponent coordinates:

```text
1 -> (0,0)
2 -> (1,0)
4 -> (2,0)
8 -> (3,0)
6 -> (1,1)
9 -> (0,2)
```

and SHALL witness:

```text
1 -> 2 -> 4 -> 8  by repeated multiplication by 2
6 = 2 * 3 = 2 * c^2
9 = 3^2 = P^4
1 = P^4 / 9
```

`AB=P^4` and `P^4=c^4=9` remain typed licensed projections. This contract does not select a scalar branch for `P^2`.

## Authority boundary

The exponent lattice is proof/metadata carried by the existing exact runtime. It SHALL NOT acquire:

```text
canonical_mutation_authority = 0
canonical_hash72_authority = 0
canonical_hash216_authority = 0
canonical_persistence_authority = 0
floating_point_authority = 0
```

VM81/Hash72 singleton admission and existing Hash216 lineage remain authoritative.

## Required failures

Validation SHALL fail closed when any of the following occurs:

- H36, Hash72, or VM81 address factorizations disagree;
- an exponent coordinate is mutated away from the exact `(2,3)` lattice witness;
- `translator_required` is asserted for the direct native binding;
- any canonical mutation, Hash72, Hash216, persistence, or floating-point authority bit is introduced.

## Acceptance

Dependency-scoped acceptance requires strict C11 aggregate ABI compilation plus exhaustive traversal of all 216 Hash216 occurrences through the direct M-exponent witness and negative tamper cases.
