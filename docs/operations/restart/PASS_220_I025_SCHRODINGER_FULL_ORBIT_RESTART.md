# Pass 220 I025 Restart Checkpoint — T_QM-02 Exact Firing-Order Unitarity and Spectrum

Date: 2026-09-21

## Repository state

- repository: danonbrez/Holofractal_Harmonicode
- verified base main: 72c599586c0035af36f1eb96ca0c93bf8174b85f
- predecessor: merged PR #541 / Pass 220 I024
- working branch: pass220/i025-schrodinger-full-orbit-v1
- merge target: main
- theorem: T_QM-02

## Predecessor closure

Pass 220 I024 exact-head completed successfully and PR #541 merged to main at:

~~~text
72c599586c0035af36f1eb96ca0c93bf8174b85f
~~~

I025 starts exactly from that verified main head.

## Initial supplied fixture audit

The supplied Wolfram suite was executed before implementation.

Two 1-based matrix-index errors were found:

1. U9 used:

~~~text
j == Mod[i - 1, 9] + 1
~~~

which constructs IdentityMatrix[9].

2. U72 used:

~~~text
j == Mod[i - step, 72] + 1
~~~

which constructs a shift-by-15 matrix.

That uncorrected U72 had three cycles of length 24 and failed U72^9=I.

The native firing-order formula itself was not wrong.

Corrected matrices:

~~~text
U9:
j == Mod[i - 2, 9] + 1

U72:
j == Mod[i - step - 1, 72] + 1
~~~

After correction U72 has exactly eight disjoint 9-cycles.

## Characteristic-polynomial correction

Wolfram CharacteristicPolynomial uses Det[M-x I].

I025 compares the monic convention using:

~~~text
(-1)^Length[M] CharacteristicPolynomial[M,x]
~~~

The corrected exact results are:

~~~text
chi_9(x)
=
(x-1)(x^2+x+1)(x^6+x^3+1)

chi_72(x)
=
[(x-1)(x^2+x+1)(x^6+x^3+1)]^8
~~~

## Hamiltonian sign/branch correction

Under the standard evolution convention:

~~~text
U = ExpSym(-i H Delta_t/u72)
~~~

the nonnegative energy branch:

~~~text
E_k =
u72 (2 pi k/9)/(tau theta)
~~~

has eigenphase:

~~~text
U psi_k = zeta_9^(-k) psi_k
~~~

not zeta_9^(+k).

A single U does not uniquely choose one Hermitian logarithm. The selected branch:

~~~text
NONNEGATIVE_K_0_TO_8
~~~

is therefore explicit receipt data.

## Exact gate correction

The exact committed-node identity is:

~~~text
psi[n+1]
=
U psi[n]
=
ExpSym(-i H_n Delta_t_n/u72) psi[n]
~~~

The finite difference:

~~~text
i u72 (psi[n+1]-psi[n])/Delta_t_n
~~~

is not equal to the logarithmic Hermitian generator for k=1..8 at finite step.

Connected Wolfram proves all eight equalities false.

Therefore the finite-difference expression remains a coarse-grained egress
projection, not the exact finite-step Hamiltonian identity.

## Full-orbit theorem

Corrected connected Wolfram result:

~~~text
schema =
HHS_PASS_220_I025_SCHRODINGER_FULL_ORBIT_WOLFRAM_20260921_V1

status = PASS
checks = 25/25
failed = []
cycle lengths = {9,9,9,9,9,9,9,9}
~~~

Thus:

~~~text
U72^dagger U72 = I
U72^9 = I
~~~

and every ninth-root eigenvalue has multiplicity 8 for the firing-order
operator.

## Degeneracy scope

The eightfold multiplicity is guaranteed for:

~~~text
H = selected logarithmic function of U72 only
~~~

Additional cycle-dependent interaction terms could split it.

I025 does not claim degeneracy protection against arbitrary future HHS
interaction Hamiltonians.

## State field

Exact phase representation:

~~~text
Q(zeta72)^9
zeta9 = zeta72^8
i = zeta72^18
~~~

The Python runtime stores multiplicative cyclotomic phases only as integer
exponents modulo 72.

## Runtime implementation

Added:

- hhs_runtime/hhs_pass220_schrodinger_firing_order_v1.py
- tests/pass220/test_hhs_pass220_schrodinger_firing_order_v1.py
- docs/pass220/PASS_220_I025_SCHRODINGER_FULL_ORBIT.md
- evidence/pass220/i025_schrodinger_full_orbit_wolfram_20260921_v1.wl
- evidence/pass220/i025_schrodinger_full_orbit_wolfram_20260921_v1.output.json
- .github/workflows/pass220-i025-schrodinger-full-orbit.yml
- this restart record

Runtime arithmetic:

- integer permutation composition;
- integer polynomial multiplication;
- fractions.Fraction for exact k/9 labels;
- zeta72 exponent arithmetic modulo 72;
- deterministic SHA-256 receipts.

No numerical eigensolver or floating-point phase evaluation exists.

## Constructor support

Wolfram also revalidated:

- both golden roots satisfy m^2-m=1;
- m^2-m-1=0;
- flank p=P-1, q=P+1 on legal P != 0 denominator branch;
- pq=P^2-1;
- p+q=2P;
- d^2=d gives d in {0,1}.

These remain support checks, not separate physical-identification proofs.

## Authority boundaries

No new:

- VM81 mutation authority;
- Delta admission authority;
- Hash72 mint authority;
- Hash216 persistence authority;
- floating-point authority;
- numerical eigensolver authority;
- collapse authority;
- Born-rule authority;
- physical particle-mass identification;
- observational fitting authority.

## Validation performed

- I024 exact-head: SUCCESS;
- PR #541 merged and main verified;
- original supplied Wolfram fixture executed and failure localized;
- matrix indexing repaired;
- characteristic-polynomial sign convention repaired;
- positive-energy phase sign repaired;
- finite-difference/logarithm distinction formalized;
- corrected Wolfram suite: 25/25 PASS;
- implementation/tests/docs/evidence/workflow are repository-visible.

## Validation remaining

Dedicated I025 exact-head must:

1. AST-audit the I025 runtime;
2. py_compile the exact runtime;
3. validate the committed 25/25 Wolfram receipt;
4. run I025 regression tests;
5. rerun inherited I022 firing-order/cadence regressions.

Queued/slow CI does not invalidate this restartable checkpoint.

## Next theorem boundary

After I025 merges, the next quantum theorem is measurement rather than another
spectrum pass:

~~~text
T_QM-03:
unitary exact state
+ observable/projector algebra
+ VM81/Lo-Shu admission
-> normalized outcome weights
-> committed collapse receipt
~~~

The Born-rule correspondence and the proposed nucleus/collapse identifications
must be proved there rather than inferred from unitarity.
