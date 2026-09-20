# HHS Lane 5 RNA Self-Ingestion Bytecode Experiment — Pass 219 1.56

## Abstract

The green T64 invariant makes it possible to ask a precise self-hosting
question: what happens when the RNA constructor reads its own `x/y/z/w`
words back as bytecode numbers?

Pass 1.56 tests two paths.

The typed path retains the existing `operation64` identity. It is perfectly
self-describing: all 64 constructor words are fixed points.

The deliberately untyped path treats the external ASCII spelling itself as one
big-endian BigInt and reduces it modulo 64. That experiment produces a
different and highly structured result: the 64-state space collapses in one
step to exactly four fixed points.

## Typed self-ingestion

For every word:

```text
q0 q1 q2
 -> kappa
 -> operation64
 -> byte
 -> exact byte ingress/egress
 -> operation64
 -> q0 q1 q2
```

The T64 bijection already proves:

```text
Decode(Encode(word)) = word
```

for all 64 ordered words.

Consequently the typed self-ingestion transition graph has:

```text
64 nodes
64 fixed points
64 distinct identities
```

No constructor provenance is lost.

## Untyped multiplicative byte spelling

The second path intentionally removes that type information.

Examples of source data are:

```text
xyz
x*y*z
```

Their ASCII bytes are treated as the digits of a base-256 BigInt and then
projected into operation64:

```text
Pi_ascii(W)=BigInt(ASCII(W)) mod64.
```

This projection is experimental and noncanonical.

## Why the result collapses to four states

For bytes `b0,...,bn`:

```text
N = Sum[b_i * 256^(n-i)].
```

But:

```text
256 = 4*64
```

so every term except the final byte vanishes modulo 64:

```text
N mod64 = bn mod64.
```

The entire projected constructor therefore depends only on its last RNA
symbol.

ASCII gives:

```text
w=119 -> 55 -> wyw
x=120 -> 56 -> wzx
y=121 -> 57 -> wzy
z=122 -> 58 -> wzz
```

Those outputs terminate in `w,x,y,z` respectively, so applying the same
projection again returns the same state.

Hence the exact four attractors are:

```text
wyw
wzx
wzy
wzz
```

## Exhaustive finite-state graph

All 64 source words were evaluated.

The one-step image is exactly four states, and because each possible final
symbol occurs in 16 of the 64 triplets, the basin decomposition is:

```text
16 -> wyw
16 -> wzx
16 -> wzy
16 -> wzz
```

Every nonfixed state reaches its attractor after one transition and every
cycle has length one.

This is not stochastic convergence. It follows exactly from the arithmetic
relationship between the byte radix 256 and the constructor modulus 64.

## Compact and explicit multiplication spellings

The experiment evaluates both:

```text
xyz
x*y*z
```

The inserted `*` bytes do not alter this particular projection because all
higher-position bytes are multiplied by powers of 256, which vanish modulo 64.

Thus both external spellings project to the same operation64 whenever their
final RNA symbol is the same.

## Interaction with T004

The untyped projection loses source identity, but it does not leave the
admitted T64 manifold.

Every projected output is one of operation64 addresses 55–58, so the already
green T004 resolver still executes successfully.

Across all 64 original inputs:

```text
64/64 projected states resolve to (-1,-1)
only 4 unique projected operation64 identities remain
```

This separates terminal closure from provenance preservation.

## Native byte transport

The compiled native bytecode membrane is tested over all 64 words with three
payload forms:

```text
compact ASCII word
explicit multiplicative ASCII word
typed operation64 byte
```

All bytes must round-trip exactly.

The membrane is used strictly as ingress/egress data transport. The experiment
does not jump to, dispatch, or execute the byte strings as machine
instructions.

## Wolfram result

Independent connected Wolfram execution returned 18/18 PASS and reproduced:

```text
typed image size = 64
external image size = 4
fixed points = {wyw,wzx,wzy,wzz}
basin sizes = {16,16,16,16}
projected operations = {55,56,57,58}
```

## Consequence

The self-ingestion experiment reveals a clean architectural boundary.

The RNA layer **can** ingest its own constructor code losslessly when the T64
type accompanies the byte. The same bytes interpreted as an untyped BigInt
under a mod64 projection produce a deterministic four-state quotient.

Therefore the next self-hosting layers should treat:

```text
byte identity
type identity
ordered provenance
numeric projection
```

as co-resident but distinct fields rather than expecting raw numeric byte
identity alone to preserve the recursive constructor manifold.
