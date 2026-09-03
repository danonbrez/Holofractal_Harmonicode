# Pass 219 I153 — Local/Global Equation Search-Space Filter

I153 binds the fixed I152 search manifold to the already-preserved monolithic UQCEL equation and makes the local Hash216/5184 hydration snapshot parameter (P) an explicit search-filter input.

No new copy of the equation is created. The authoritative source remains:

`contracts/pass219/PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode`

with exact identity:

```text
bytes  = 348
sha256 = ac143798146d89a3fe932f39ccb4d612e4fb3e45c471abc1a8bbbebb0f9c0a6a
```

The inherited combined whole-expression source remains:

`contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode`

with:

```text
bytes  = 632
sha256 = 3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53
```

## 1. Fixed global cardinalities remain unchanged

I153 inherits I152 without reopening its cardinalities:

[
|Omega| = 72^{42} = 5184^{21}
]

[
|mathcal M| = 3cdot72^{72}
]

[
|mathcal R_omega| = 3cdot72^{30}
]

and the exhaustion envelope remains:

[
81W_{mathrm{effective}}le 7cdot72^{42}.
]

The local parameter (P) does not resize any of these spaces.

## 2. (P) is local snapshot state

I153 fixes the semantic role:

[
oxed{
P = 	ext{local state Hash216 / 5184-hydration parameter snapshot}
}
]

The snapshot must carry:

- one exact nonzero integer (P);
- `hydration_bits = 5184`;
- one explicit Hash216 identity representation;
- the immutable equation-source identity;
- the immutable I152 target/manifold/route cardinalities.

Supported repository-visible snapshot identity representations are:

1. the inherited Pass 150 Hash216Genome root encoded as a 64-hex SHA-256 root;
2. an explicit 216-glyph three-Hash72 Hash216 representation.

The format is declared rather than guessed. The filter never silently converts one representation into the other.

A deterministic diagnostic SHA-256 binding commits the complete local snapshot descriptor for candidate filtering. That digest is not a new canonical Hash216 authority.

## 3. Local/global search membrane

For each I152 route pair

[
(omega,r),qquad
0leomega<72^{42},quad
0le r<3cdot72^{30},
]

the exact I152 working index remains

[
m_{mathrm{work}}=omega(3cdot72^{30})+r.
]

I153 then applies the equation filter:

```text
I152 target block + route
        ↓
exact working-index reconstruction
        ↓
local Hash216/5184 snapshot P binding
        ↓
348-byte verbatim UQCEL source binding
        ↓
632-byte whole-expression source binding
        ↓
shared global symbol-environment binding
        ↓
five inherited source-offset gate witnesses
        ↓
global environment complete?
        ↓
cross-layer revalidation complete?
        ↓
local symbol shadowing absent?
        ↓
SURVIVES FILTER / REJECT
```

The inherited combined-expression Boolean gate offsets are preserved exactly:

[
oxed{96, 240, 266, 274, 285}.
]

Every gate witness must bind to the same local (P) snapshot and the same global symbol-environment root.

## 4. Filter semantics

A route survives only when all of the following are true:

1. its I152 block/route/working-index relation is exact;
2. the 348-byte equation source identity is exact;
3. the 632-byte combined whole-expression source identity is exact;
4. all five gate witnesses have their inherited source offsets;
5. every gate binds the same local snapshot;
6. every gate binds the same global symbol environment;
7. all five gate witness results are true;
8. the global environment is complete;
9. cross-layer revalidation is complete;
10. local symbol shadowing is absent.

Therefore the optimizer receives:

[
mathcal R_omega
longrightarrow
mathcal R_{omega,P,mathrm{equation}}
longrightarrow
operatorname*{arg,min} C(r).
]

The expensive optimization stage is run only on the survivor set.

## 5. Whole-expression authority remains inherited

The filter consumes source-bound Boolean witness results. It does not manufacture them.

The existing I121.8/I121.9/I121.12 authority boundary remains intact:

- Pass 159 preserves and lowers the whole expression;
- the I121.9 membrane binds the five global gates and one shared environment;
- I121.12 permits only already-proved read-only redundant-work reduction;
- Pass 169 whole-expression authority remains required before any canonical algebraic admission;
- VM81 remains the sole canonical mutation/commit authority.

Consequently an I153 survivor means:

`SURVIVES_LOCAL_GLOBAL_EQUATION_FILTER`

not:

`CANONICAL_MONOLITHIC_PROOF`.

## 6. No local shadow copies

Changing (P) creates a different snapshot binding. A witness produced for one (P) cannot be replayed under another (P).

Likewise, changing:

- target block;
- route index;
- working index;
- source identity;
- gate offset;
- global environment root;
- cross-layer revalidation state;

invalidates the candidate or rejects it.

This prevents the local search optimizer from silently shadowing the global equation environment.

## 7. Benchmark policy

I153 includes a bounded synthetic benchmark whose purpose is to measure filter mechanics, not equation truth.

The synthetic lane may provide deterministic five-gate patterns across a bounded set of valid I152 route addresses and measure:

- input candidate count;
- survivor count;
- rejected count;
- rejection reasons;
- candidate-count reduction;
- whether the bounded synthetic ratio exceeds the local (81/7) threshold.

The synthetic gate pattern is not Pass169 truth and does not establish full (72^{42}) exhaustion.

A full exhaustion claim still requires receipt-bound integrated four-lane evidence under the immutable I152 cardinalities and the exact equation membrane.

## 8. Canonical authority

I153 is read-only and candidate-only:

```text
VM81 mutation authority        = false
Hash72 mint authority          = false
Hash216 persistence authority  = false
floating-point authority       = false
canonical monolithic proof     = false
Pass169 whole-expression gate  = required
```

The result is a narrower search problem without reducing either the target resolution or the available Hash216 working manifold.
