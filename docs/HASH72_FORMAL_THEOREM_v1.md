# HASH72 FORMAL CLOSURE THEOREM v1

## Theorem

Hash72 is a deterministic, lossless, ordered tensor serialization over the closed 72-phase ring.

Let:

```text
A72 = {u^0, u^1, ..., u^71}
u^72 = u^0
```

Define:

```text
Hash72(S) = [s0*u^0, s1*u^1, ..., s71*u^71]
```

where each `sk` is an ordered system symbol and every one of the 72 tensor positions is populated.

## Axioms

1. Cyclic closure: `u^(k+72) = u^k`.
2. Full traversal: every phase position `0..71` is defined.
3. Ordering is preserved; noncommutative products are not reordered.
4. Digital DNA bridge: `u^0 = x+y = z-w` and `u^72 = xyzw = a^2`.
5. Kernel enforcement: only `LOCKED` states are valid.

## Injectivity Claim

If:

```text
Hash72(S1) = Hash72(S2)
```

then every serialized tensor address matches:

```text
s_k^(1) * u^k = s_k^(2) * u^k for all k in 0..71
```

Because each `u^k` is a distinct ordered tensor address during traversal and ordering is preserved:

```text
s_k^(1) = s_k^(2) for all k
```

Therefore:

```text
S1 = S2
```

So Hash72 is injective over the valid state space.

## Corollaries

```text
0 = u^0
1 = u^72
u^72 = u^0
```

Inside HHS phase normalization:

```text
1/0 = u^72/u^0 = u^72 = u^0
```

and:

```text
infinity = 72!^3 / xy
infinity^-1 = u^0
infinity * infinity^-1 = u^72 = u^0
```

## Runtime Statement

A collision cannot propagate because invalid or partially populated states fail kernel enforcement.

```text
collision -> invalid state -> QUARANTINED
```

Hash72 is therefore a lossless closure-normalizing base-72 positional tensor alphabet over the serialized wraparound sequence of all 72 roots of unity.
