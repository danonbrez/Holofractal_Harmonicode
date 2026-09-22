# Pass 220 I026 — T_QM-03A Exact Quantum Measurement Projector Algebra

Date: 2026-09-21

## 1. Scope

I026 advances the quantum layer from the exact firing-order unitary/spectrum of
I025 to exact projective measurement algebra on the 9-state macrocycle.

It closes:

- exact Q(zeta72) amplitude arithmetic;
- the nine firing-order spectral projectors;
- Hermiticity;
- idempotence;
- mutual orthogonality;
- completeness;
- exact Born-weight numerator/denominator carriers;
- repeatable/exclusive projected collapse candidates;
- SHA binding to a source-state receipt and a supplied admission witness.

It does **not** claim:

- a stochastic outcome-selection mechanism;
- an empirical Born-frequency theorem;
- canonical VM81 mutation authority;
- a proved 9-outcome -> Lo-Shu trinary admission map;
- that a supplied admission-witness SHA has canonical semantics.

Those remaining authority boundaries are explicit.

## 2. Why this is T_QM-03A rather than the complete collapse theorem

The inherited I021 epsilon/Lo-Shu closure provides exact:

~~~text
sgn3(e) in {-1,0,+1}
epsilon phase triplet (-e,0,+e)
zero-centered Lo Shu transport
72-route closure receipts
~~~

but its closure witness explicitly records:

~~~text
canonical_admission_authority = False
~~~

Therefore I026 must not silently reinterpret that transport proof as canonical
measurement-selection authority.

The exact measurement algebra can close now; the admission bridge remains a
separate proof obligation.

## 3. Exact cyclotomic state carrier

The state space remains:

~~~text
Q(zeta72)^9
~~~

I026 implements Q(zeta72) using the degree-24 basis:

~~~text
1, zeta72, ..., zeta72^23
~~~

with exact rational coefficients and reduction by:

~~~text
Phi_72(x) = x^24 - x^12 + 1
~~~

so:

~~~text
x^24 = x^12 - 1
x^72 = 1
x^36 = -1
i = x^18
zeta9 = x^8
~~~

No numerical root-of-unity evaluation occurs.

## 4. Firing-order eigenvectors

For:

~~~text
k = 0,...,8
j = 0,...,8
~~~

define the exact Fourier vector:

~~~text
v_k[j] = zeta9^(k j) = zeta72^(8 k j)
~~~

Under the I025 orientation:

~~~text
U v_k = zeta9^(-k) v_k
~~~

for the nonnegative energy branch.

## 5. Exact spectral projectors

Define:

~~~text
P_k = |v_k><v_k| / 9
~~~

with matrix kernel:

~~~text
P_k[a,b] =
(1/9) zeta9^(k(a-b))
~~~

The primitive-root identity:

~~~text
Sum[j=0..8] zeta9^(m j) =
9, m = 0 mod 9
0, otherwise
~~~

gives all projector laws exactly.

### Hermiticity

~~~text
P_k^dagger = P_k
~~~

### Idempotence

~~~text
P_k^2 = P_k
~~~

### Orthogonality

~~~text
P_k P_r = 0, k != r
~~~

### Completeness

~~~text
Sum[k=0..8] P_k = I_9
~~~

These are exact algebraic identities, not numerical matrix tolerances.

## 6. Exact measurement weights

For any nonzero exact state psi:

~~~text
N = <psi|psi>
N_k = <psi|P_k|psi>
~~~

and the standard projector weight is:

~~~text
w_k = N_k / N
~~~

I026 does not force division into a floating scalar.

It stores:

~~~text
weight_numerator   = N_k
weight_denominator = N
weight_carrier     = numerator/total_norm
~~~

as exact Q(zeta72) objects.

Completeness proves:

~~~text
Sum[k] N_k = N
~~~

so:

~~~text
Sum[k] w_k = 1
~~~

whenever the nonzero norm is interpreted in the ordinary complex embedding.

Each N_k is constructed as the norm-squared of P_k psi and is verified to be
self-conjugate in the exact field representation.

## 7. What "Born-weight algebra closed" means

I026 records:

~~~text
born_weight_algebra_closed = True
stochastic_born_frequency_law_closed = False
~~~

The first statement means the exact projector weights are available and
normalized algebraically.

It does **not** mean that unitarity alone has proved why physical outcome
frequencies must follow those weights.

That empirical/selection correspondence remains a separate theorem boundary.

## 8. Collapse candidate

Given an explicit outcome k with nonzero exact weight, I026 constructs:

~~~text
psi_projected = P_k psi
~~~

and proves:

~~~text
P_k psi_projected = psi_projected
P_r psi_projected = 0, r != k
~~~

The normalized collapse state is carried symbolically as:

~~~text
psi_k =
psi_projected / sqrt(<psi_projected|psi_projected>)
~~~

I026 does not force that square root back into Q(zeta72), because it need not
belong to the same finite cyclotomic field.

The receipt therefore stores:

~~~text
normalization_carrier:
  operation = divide_by_symbolic_sqrt
  norm2 = exact Q(zeta72) value
~~~

This preserves exactness without algebraic preemption.

## 9. Admission-witness boundary

A collapse candidate binds:

~~~text
source_state_receipt_sha256
measurement_receipt_sha256
admission_witness_sha256
outcome k
projected exact state
normalization carrier
~~~

But it also records:

~~~text
canonical_state_mutated = False
canonical_admission_authority = False
lo_shu_admission_binding_closed = False
admission_witness_semantics_verified = False
~~~

Thus a caller cannot convert a SHA string into canonical authority merely by
passing it to the function.

The next admission theorem must prove the witness semantics and the mapping
between the 9 spectral outcomes and the VM81/Lo-Shu admission surface.

## 10. Exact Wolfram proof

The authoritative Wolfram proof uses polynomial quotients rather than
exponential root simplification.

For the ninth-root field:

~~~text
Phi_9(x) = x^6 + x^3 + 1
~~~

For the 72nd-root field:

~~~text
Phi_72(y) = y^24 - y^12 + 1
~~~

Every root-sum and projector identity is reduced with PolynomialRemainder.

Result:

~~~text
schema =
HHS_PASS_220_I026_QUANTUM_MEASUREMENT_WOLFRAM_20260921_V1

status = PASS
checks = 12/12
failed = []
~~~

The 12 checks prove:

1. zeta72 has order 72 under the quotient relation;
2. zeta72^36 = -1;
3. Phi72 closure;
4. zeta9 embeds as zeta72^8;
5. i embeds as zeta72^18;
6. nontrivial ninth-root sums vanish;
7. projector completeness;
8. projector orthogonality;
9. projector Hermiticity;
10. projector idempotence;
11. exact weight-sum normalization;
12. repeatable/exclusive projected collapse.

## 11. Runtime surfaces

Implementation:

~~~text
hhs_runtime/hhs_pass220_quantum_measurement_projectors_v1.py
~~~

Regression:

~~~text
tests/pass220/test_hhs_pass220_quantum_measurement_projectors_v1.py
~~~

Evidence:

~~~text
evidence/pass220/i026_quantum_measurement_wolfram_20260921_v1.wl
evidence/pass220/i026_quantum_measurement_wolfram_20260921_v1.output.json
~~~

## 12. Exact implementation rules

The runtime uses:

- int;
- fractions.Fraction;
- 24-coefficient cyclotomic field elements;
- polynomial reduction modulo Phi72;
- exact conjugation zeta72 -> zeta72^-1;
- exact inner products;
- exact projector actions;
- SHA-256 receipts.

It does not use:

- float;
- complex;
- cmath;
- numpy;
- scipy;
- sympy;
- random;
- secrets;
- numerical square roots;
- numerical normalization;
- host wall-clock time.

## 13. Regression targets

The dependency-scoped suite verifies:

- zeta72^72 = 1;
- zeta72^36 = -1;
- Phi72(zeta72) = 0;
- exact phase conjugation;
- computational-basis states have nine weights of 1/9;
- each Fourier eigenmode measures sharply in its own projector;
- arbitrary exact states satisfy sum N_k = N;
- inner-product conjugate symmetry;
- collapse candidates are repeatable and exclusive;
- zero-weight outcomes fail closed;
- the zero vector cannot be measured;
- outcome bounds and receipt SHAs fail closed;
- deterministic replay gives the same receipt;
- no selection/admission authority is accidentally granted.

## 14. Authority boundaries

I026 adds no:

- VM81 mutation authority;
- Delta admission authority;
- Hash72 mint authority;
- Hash216 persistence authority;
- Lo-Shu canonical admission authority;
- random sampling authority;
- empirical Born-frequency claim;
- floating-point authority;
- numerical root/eigenvalue authority;
- inverse observational fitting authority.

## 15. Next theorem boundary

The remaining half of T_QM-03 is:

~~~text
T_QM-03B:
exact projector outcome k
+ exact nonzero weight
+ repository-defined VM81/Lo-Shu witness
+ deterministic admission rule
-> canonical collapse commit or fail-closed rejection
~~~

Only after T_QM-03B closes can the repository claim an end-to-end canonical
collapse transition rather than a mathematically exact collapse candidate.
