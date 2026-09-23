# Pass 220 I026 Restart Checkpoint — T_QM-03A Exact Quantum Measurement Projectors

Date: 2026-09-21

## Repository state

- repository: danonbrez/Holofractal_Harmonicode
- verified base main: 2738aefe305de490204dbbecd03d3c0b0d7041fe
- predecessor: merged PR #542 / Pass 220 I025
- working branch: pass220/i026-quantum-measurement-projectors-v1
- merge target: main
- theorem: T_QM-03A

## Predecessor closure

The repaired I025 exact-head run:

~~~text
Pass 220 I025 Schrodinger Full Orbit
run 35677258770
conclusion = success
~~~

closed on head:

~~~text
1a98a4e7c240207eb3413e1587f89c86c0ebbddc
~~~

PR #542 was merged to main at:

~~~text
2738aefe305de490204dbbecd03d3c0b0d7041fe
~~~

I026 starts exactly from that verified main head.

## I026 theorem scope

I026 closes the exact projective-measurement algebra on:

~~~text
Q(zeta72)^9
~~~

It proves and implements:

- exact cyclotomic field arithmetic;
- exact firing-order Fourier projectors;
- Hermiticity;
- idempotence;
- orthogonality;
- completeness;
- exact normalized weight carriers;
- repeatable/exclusive collapse candidates;
- deterministic SHA receipts.

It deliberately does not claim canonical collapse admission.

## Exact cyclotomic carrier

The runtime represents:

~~~text
Q(zeta72)
~~~

in the degree-24 basis with:

~~~text
Phi72(x) = x^24 - x^12 + 1
~~~

and exact Fraction coefficients.

Reduction uses:

~~~text
x^24 = x^12 - 1
~~~

which preserves:

~~~text
x^72 = 1
x^36 = -1
zeta9 = x^8
i = x^18
~~~

No numerical root of unity is evaluated.

## Exact projector theorem

For:

~~~text
v_k[j] = zeta72^(8 k j)
P_k = |v_k><v_k| / 9
~~~

the exact identities are:

~~~text
P_k^dagger = P_k
P_k^2 = P_k
P_k P_r = 0 for k != r
Sum_k P_k = I
~~~

The proof reduces to exact primitive ninth-root sums.

## Weight algebra

For nonzero exact psi:

~~~text
N = <psi|psi>
N_k = <psi|P_k|psi>
w_k = N_k/N
~~~

The runtime stores w_k as an exact carrier:

~~~text
weight_numerator = N_k
weight_denominator = N
~~~

rather than forcing field division or floating conversion.

It verifies:

~~~text
Sum_k N_k = N
~~~

exactly.

## Collapse candidate

For an explicitly supplied nonzero-weight outcome k:

~~~text
psi_projected = P_k psi
~~~

and:

~~~text
P_k psi_projected = psi_projected
P_r psi_projected = 0 for r != k
~~~

The normalized state remains symbolic:

~~~text
psi_k =
psi_projected / sqrt(<psi_projected|psi_projected>)
~~~

because the square root need not lie inside Q(zeta72).

The collapse receipt binds:

- source-state receipt SHA;
- measurement receipt SHA;
- supplied admission-witness SHA;
- outcome k;
- exact projected state;
- exact norm2 carrier.

It records:

~~~text
canonical_state_mutated = False
canonical_admission_authority = False
lo_shu_admission_binding_closed = False
admission_witness_semantics_verified = False
~~~

## Why admission remains open

The inherited I021 Lo-Shu closure explicitly records:

~~~text
canonical_admission_authority = False
~~~

I026 therefore does not invent a nine-outcome -> trinary Lo-Shu mapping or
reinterpret an arbitrary SHA as an admission proof.

The remaining theorem is T_QM-03B.

## Born-rule boundary

I026 records:

~~~text
born_weight_algebra_closed = True
stochastic_born_frequency_law_closed = False
random_sampling_authority = False
~~~

The exact standard projector weights are closed algebraically.

No stochastic sampling mechanism and no empirical frequency theorem is inferred
from unitarity alone.

## Wolfram formalization

Authoritative result:

~~~text
schema =
HHS_PASS_220_I026_QUANTUM_MEASUREMENT_WOLFRAM_20260921_V1

status = PASS
checks = 12/12
failed = []
~~~

The proof is warning-free polynomial quotient arithmetic using:

~~~text
Phi9(x) = x^6 + x^3 + 1
Phi72(y) = y^24 - y^12 + 1
PolynomialRemainder
~~~

No numerical roots, eigensolver, or approximate simplifier is required.

## Files added

- hhs_runtime/hhs_pass220_quantum_measurement_projectors_v1.py
- tests/pass220/test_hhs_pass220_quantum_measurement_projectors_v1.py
- docs/pass220/PASS_220_I026_QUANTUM_MEASUREMENT_PROJECTORS.md
- evidence/pass220/i026_quantum_measurement_wolfram_20260921_v1.wl
- evidence/pass220/i026_quantum_measurement_wolfram_20260921_v1.output.json
- .github/workflows/pass220-i026-quantum-measurement-projectors.yml
- this restart record

## Validation performed

- predecessor I025 exact-head: SUCCESS;
- PR #542 merged and main verified;
- repository search found no existing canonical measurement/projector implementation;
- inherited I021 admission boundary inspected directly;
- Wolfram first exponential-root formulation: algebra passed but emitted internal precision warnings;
- proof rewritten as polynomial-quotient arithmetic;
- warning-free authoritative Wolfram receipt: 12/12 PASS;
- exact runtime/tests/docs/evidence/workflow written from verified main.

## Validation remaining

Dedicated I026 exact-head must:

1. AST-audit I026 for float/complex/random/numerical authority;
2. reject bare Python division in the exact runtime;
3. py_compile I025-I026;
4. verify Wolfram source/receipt binding;
5. verify inherited I021 still exposes no canonical admission authority;
6. run I026 regression tests;
7. rerun inherited I025 quantum regressions.

Queued or slow CI does not invalidate this repository-visible checkpoint.

## Authority boundaries

No new:

- VM81 mutation authority;
- Delta admission authority;
- Hash72 mint authority;
- Hash216 persistence authority;
- Lo-Shu canonical admission authority;
- random sampling authority;
- empirical Born-frequency authority;
- floating-point/complex-number authority;
- numerical square-root authority;
- numerical eigensolver authority;
- inverse observational fitting authority.

## Next action

Read the dedicated I026 exact-head workflow.

If green, merge I026 and verify main.

Then continue with:

~~~text
T_QM-03B:
exact outcome k
+ exact nonzero weight
+ repository-defined VM81/Lo-Shu admission witness
+ deterministic outcome/admission map
-> canonical collapse commit or fail-closed rejection
~~~

If the repository still lacks canonical admission authority at that point, do
not invent it; derive or implement that authority first.
