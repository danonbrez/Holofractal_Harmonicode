# Pass 220 I040 — Explicit DESI Projection and Fail-Closed Corpus

Date: 2026-09-23

## Scope

I040 closes the observation-map boundary left intentionally open by I038 and
I039.

Public DESI observables are now bound explicitly to the already implemented
I023 relativistic surfaces. The constructor does not infer or fit an implicit
mapping into `A,B,P,p,q,x,y,z,w`.

The projection is:

~~~text
z_eff
  -> redshift target z
  -> one_plus_z = 1 + z

D_H/r_d
  -> normalized I023 Hubble-distance surface
  -> H*r_d/c0 = 1/(D_H/r_d)

D_M/r_d
  -> normalized I023 transverse-comoving-distance surface
  -> D_M/D_H = (D_M/r_d)/(D_H/r_d)

(D_V/r_d)^3
  = z_eff * (D_M/r_d)^2 * (D_H/r_d)
~~~

The exact observation state then enters the existing I038 parallel
decimal/IEEE/BigInt path, binds the I039 shared unification root, and is copied
completely to the three I037 `-,0,+` 24D manifolds.

## Public DESI fixture

The initial row is the DESI DR2 Ly-alpha BAO result:

~~~text
z_eff = 2.33
D_H/r_d = 8.632
D_H stat = 0.098
D_H sys  = 0.026
D_M/r_d = 38.99
D_M stat = 0.52
D_M sys  = 0.12
~~~

The source URLs remain attached through I038:

~~~text
https://www.desi.lbl.gov/2025/03/19/desi-dr2-results-march-19-guide/
https://data.desi.lbl.gov/doc/papers/dr2/
https://arxiv.org/abs/2503.14739
~~~

## Exact solve

The public decimal strings are exact rationals:

~~~text
z_eff       = 233/100
D_H/r_d     = 1079/125
D_M/r_d     = 3899/100
one_plus_z  = 333/100
~~~

The radial BAO definition gives the exact reciprocal solve:

~~~text
H*r_d/c0
=
1/(D_H/r_d)
=
125/1079
~~~

The Alcock-Paczynski ratio is therefore:

~~~text
D_M/D_H
=
(D_M/r_d)/(D_H/r_d)
=
19495/4316
~~~

The isotropic BAO cube remains exact:

~~~text
(D_V/r_d)^3
=
z_eff*(D_M/r_d)^2*(D_H/r_d)
=
3821939746807/125000000
~~~

No numerical root is required. If a later constructor needs `D_V/r_d`
it can retain the exact symbolic cube root of this rational.

## Parallel representation

All seven numeric fields retain their complete I038 state:

- exact released decimal source;
- exact rational;
- integer-only nearest-even IEEE binary64 image;
- exact IEEE dyadic;
- exact decimal-minus-IEEE residue;
- palindromic symbolic/full-phase transport;
- fixed 5,184-character BigInt state;
- I037 equation/proof bundle root;
- Lane 5 validated-constructor metadata.

The observation map does not bypass that stack.

## Three complete phase copies

The explicit projection is copied in full to:

~~~text
G24[-]
G24[0]
G24[+]
~~~

Each copy carries the same:

- projection root;
- I039 shared-state root;
- I037 mandatory equation/proof root;
- seven I038 carrier receipts;
- seven exact IEEE residues;
- exact observational solve.

No branch is a partial information slice.

## U_data predicate

I040 defines the data-bound closure:

~~~text
U_data(S_i) =
  U_I039(S_i)
  AND Pi_DESI(S_i)
  AND all I038 carriers valid
  AND all BigInt widths = 5184
  AND all three 24D phase copies complete
  AND palindromic return closed
  AND Delta e = 0
  AND Psi = 0
  AND Omega = true
~~~

For the initial public DESI row the projection returns:

~~~text
status = CLOSE
~~~

This is the exact observation/projection/substrate closure. It does not invent a
new hidden fit or silently assign the observables to unrelated native variables.

## Fail-closed corpus

The corpus runner evaluates rows independently.

A row returns only:

~~~text
CLOSE
or
REJECT
~~~

If any row rejects:

~~~text
corpus status = REJECT
~~~

There is no averaging of a failed row into the rest of the dataset.

## Uncertainty boundary

Published statistical and systematic terms remain separate exact rationals.

I040 does not:

- combine them into one sigma;
- assign probability weights;
- evaluate a likelihood;
- run MCMC;
- refit parameters;
- alter the white-paper equations to force closure.

They remain observation-boundary metadata available to later tests.

## Authority

I040 is a validated observational projection constructor only.

~~~text
host float arithmetic                 = false
probability weighting                 = false
likelihood                            = false
MCMC                                  = false
parameter refit                       = false
row averaging                         = false
commutative reordering                = false
canonical VM81 mutation authority     = false
canonical Hash72 authority            = false
canonical Hash216 authority           = false
direct canonical persistence          = false
~~~

Repository OS hydration remains downstream.

## Formal result

Connected Wolfram verification:

~~~text
HHS_PASS_220_I040_DESI_EXPLICIT_PROJECTION_CORPUS_WOLFRAM_20260923_V1
PASS
44 / 44
failed = []
~~~
