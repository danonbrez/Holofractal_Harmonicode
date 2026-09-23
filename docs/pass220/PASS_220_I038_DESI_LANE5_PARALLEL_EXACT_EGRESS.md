# Pass 220 I038 — DESI Lane 5 Parallel Exact Observational Egress

Date: 2026-09-23

## Scope

I038 implements the first T_COSMO-07 observational egress constructor against public DESI measurements.

The key rule is that the released decimal measurement is the exact observational source. The IEEE lane is not allowed to replace it.

Each observation is carried simultaneously through:

~~~text
public DESI decimal string
-> exact rational
-> integer-only nearest-even IEEE binary64 storage image
-> inherited palindromic symbolic/full-phase IEEE path
-> exact decimal-minus-IEEE rational residue
-> fixed 5,184-character BigInt geometry
-> I037 mandatory 24D equation/proof bundle
-> Lane 5 validated constructor composition
~~~

No host float is used by the constructor.

## Initial public DESI fixture

The initial exact fixture is the public DESI DR2 Ly-alpha BAO result:

~~~text
z_eff = 2.33

D_H(z_eff)/r_d = 8.632
statistical sigma = 0.098
systematic sigma  = 0.026

D_M(z_eff)/r_d = 38.99
statistical sigma = 0.52
systematic sigma  = 0.12
~~~

Source references retained by the constructor:

~~~text
https://www.desi.lbl.gov/2025/03/19/desi-dr2-results-march-19-guide/
https://data.desi.lbl.gov/doc/papers/dr2/
https://arxiv.org/abs/2503.14739
~~~

All published numerals are retained as source strings and parsed as exact rationals.

## Exact decimal lane

Examples:

~~~text
2.33  = 233/100
8.632 = 1079/125
38.99 = 3899/100
~~~

No binary floating conversion is used to establish these identities.

## Parallel IEEE lane

I038 constructs the nearest-even IEEE binary64 state with exact integer arithmetic.

Representative storage states:

~~~text
2.33  -> 0x4002a3d70a3d70a4
8.632 -> 0x40214395810624dd
38.99 -> 0x40437eb851eb851f
~~~

The resulting raw bytes are passed through the inherited I031/I032/I033 exact IEEE and palindromic reciprocal machinery.

Thus the IEEE lane keeps:

- exact raw storage bits;
- exact dyadic rational interpretation;
- x/y reciprocal phase path;
- full x/y/z/w ordered phase tensor;
- scalar-bit invariance;
- palindromic reciprocal return;
- no floating-point authority.

## Exact residue

The released decimal and the IEEE dyadic are deliberately not conflated.

For example:

~~~text
8.632 exact decimal
-
binary64(8.632) exact dyadic
=
23 / 70368744177664000
~~~

The residue is stored exactly.

Therefore:

~~~text
temporary IEEE projection allowed
unaccounted IEEE drift forbidden
~~~

The source decimal, raw IEEE state, dyadic projection, and residue remain co-resident.

## BigInt lane

Every observation is simultaneously bound to the existing 81-cell normalized state and serialized through the I001 fixed-width HARMONICODE carrier:

~~~text
81 cells * 64 characters = 5184 characters
~~~

The BigInt state does not replace the observation. It is the parallel deterministic geometry/address carrier used by the existing Lane 5 path.

## I037 equation/proof geometry

Every observation carrier binds the exact root of the I037 mandatory 24D constructor bundle.

Therefore the observational input is associated with the same mandatory:

- ordered q=-1 trinary tensor;
- full variable exchange;
- P⁴ invariant;
- P⁸ trinary fractal scale;
- epsilon residue geometry;
- Lo Shu nucleus;
- proof lemmas;
- 24+24+24=72 phase cover;
- 72+9=81 and 81*64=72²=5184 closure.

I038 does not drop equations merely because an observational representation is numerical.

## Measurement uncertainty

DESI's published statistical and systematic components are retained separately as exact decimal/rational observation metadata.

I038 does not:

- combine them into a Gaussian sigma;
- convert them into a probability weight;
- evaluate a likelihood;
- run MCMC;
- refit the HHS equations;
- alter the I037 constraint bundle.

They are boundary information describing the measurement.

## Variable-binding boundary

I038 intentionally does not invent an implicit assignment such as:

~~~text
D_H/r_d -> p
D_M/r_d -> q
~~~

or any other DESI-to-HHS variable correspondence.

The output boundary is:

~~~text
OBSERVATION_RECEIPT_READY_FOR_EXPLICIT_DESI_TO_HHS_VARIABLE_BINDING
~~~

A later constructor must state that observation map explicitly before equation closure is evaluated.

## Authority

I038 is a read-only observational egress constructor.

It has no:

- VM81 mutation authority;
- canonical constraint creation/enforcement authority;
- Hash72 mint authority;
- Hash216 persistence authority;
- direct cache persistence authority;
- floating-point authority.

The repository OS remains responsible for validated-constructor hydration.
