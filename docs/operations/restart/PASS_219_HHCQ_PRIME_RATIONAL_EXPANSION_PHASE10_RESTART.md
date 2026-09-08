# Pass 219 HHCQ prime-rational polynomial expansion Phase 10 restart

Date: 2026-09-07

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Frozen Phase 9 checkpoint/base: `715dfbc3f889ea1ec1e1111348f8c2523f0d1288`
- Phase 9 accepted validated implementation head: `e9620d1db390bb08294a8b207351c2708442892e`
- Phase 10 branch: `agent/pass219-hhcq-prime-rational-expansion-phase10-20260907`
- Target: experiment branch only. No PR, merge, deployment, or canonical-authority promotion is authorized.

## Frozen inherited evidence

Preserve Phase 1 through Phase 9 evidence. Do not rerun unrelated history. Phase 9 remains frozen at accepted workflow run `34174828409`, job `101902057129`, with exact reciprocal economy parity 5184, independent 1:1 information closure, 112-byte policy state, deterministic replay, and zero canonical/floating authority.

## New user-supplied higher-resolution constraint source

Preserve the existing 542-byte core equation source unchanged and add the following source verbatim as a second constraint-extension source:

`Sqrt((A*B))*(A*B)/Sqrt((A*B))==A/B*B/A==((-x*y)^(((x+y^2)*(y+x^2))/((x²+y²)²*Sqrt((a*b)))))^x² where A,B are two primes and AB=P⁴`

The runtime must not silently rewrite or replace this source. It may compile explicit exact witnesses from it, as previous HHCQ phases compile runtime invariants from the frozen core equation without claiming executable evaluation of every symbolic term.

## Phase 10 formalization

### 1. Replace the scalar `n` envelope with an exact two-prime rational pair

Phase 9 used the scalar reciprocal envelope

`1/n : 1 : n`.

Phase 10 refines the envelope with two prime-rational boundary terms `A` and `B` constructed from two prime seeds `p` and `q` around a shared symbolic `P²` scale:

`A = P² * (p/q)`

`B = P² * (q/p)`

with `p` and `q` prime.

This gives the exact product witness

`A*B = P⁴`

while the scale cancels in the reciprocal boundary:

`A/B = p²/q²`

`B/A = q²/p²`

and therefore

`(A/B)*(B/A) = 1`.

The economy parity remains the VM81/HHCQ execution parity `E = 5184`. Do **not** conflate this runtime economy parity with the symbolic `P` occurring in the core equation.

For every normalized economy axis `U`, the new exact admissible envelope is evaluated without floating point by cross multiplication:

`min(A/B, B/A) <= U/E <= max(A/B, B/A)`.

No floor/rounded rational comparison is authoritative.

### 2. Normalize the chained source into closure witnesses rather than asserting incompatible scalar magnitudes

The supplied source chain contains a product-scale branch and a reciprocal-neutral branch. The runtime preserves the verbatim chain but tests them as normalized closure witnesses:

- product-scale witness: `Sqrt(AB)*(AB)/Sqrt(AB) = AB = P⁴`, using `Sqrt(AB)=P²` from the product constructor rather than floating-point square root;
- reciprocal-neutral witness: `(A/B)*(B/A)=1`;
- polynomial-phase witness: exact symbolic polynomial exponent geometry derived from the right-hand branch.

Each branch is normalized to its own declared invariant before the circuit requires closure. Phase 10 does not claim the raw scalar value `AB` is numerically equal to the raw scalar value `1` under ordinary arithmetic.

### 3. Exact polynomial expansion witness

For phase coordinates `x,y` the right-hand branch is represented without float evaluation as:

`base = -x*y`

`N = (x + y²)*(y + x²)*x²`

`D = (x² + y²)²`

with the remaining `1/Sqrt(a*b)` factor retained as an explicit symbolic-root tag. `N/D` is reduced exactly by integer gcd. The runtime does not numerically raise a negative base to an irrational exponent.

The reduced polynomial witness, prime pair, and ordered phase coordinates produce a deterministic `u72` expansion phase. That phase maps through the existing 35-member Phase-5 divisor lattice. Expansion is monotone: it may preserve or increase the existing resolution index (finer decomposition), never coarsen it.

### 4. Information and authority constraints remain harder than economy

Phase 10 changes the reciprocal resolution/economy envelope only. It does not weaken Phase 9 admission:

- exact 1:1 lossy/recovered information closure remains mandatory;
- exact reconstruction remains mandatory before any lower-resolution branch is admitted;
- exact semantic closure remains mandatory;
- all-native-modality translatability remains mandatory;
- one-step lane/basis translation remains mandatory;
- Phase-5 coordinate identity remains authoritative;
- 112-byte learned policy state remains fixed unless separately justified;
- candidate-only semantics remain;
- canonical VM81, Hash72, Hash216, persistence, and floating-point authority remain zero.

## Planned implementation

- `hhs_runtime/include/hhs_pass219_hhcq_prime_rational_expansion_1_30.h`
- `hhs_runtime/c/hhs_pass219_hhcq_prime_rational_expansion_1_30.inc`
- additive aggregate ABI bindings
- `tests/pass219/test_pass219_hhcq_prime_rational_expansion_1_30.c`
- `benchmarks/pass219/hhcq_prime_rational_expansion_phase10_benchmark.cpp`
- `.github/workflows/pass219-hhcq-prime-rational-expansion-phase10.yml`
- this restart record updated with accepted evidence.

## Validation gates

1. verbatim extension-source byte/SHA lock;
2. exact prime validation and rejection of composite/zero/unit seeds;
3. exact `A*B=P⁴` constructor witness;
4. exact reciprocal `(A/B)*(B/A)=1` witness;
5. exact rational economy-bound comparisons around execution parity 5184;
6. exact polynomial `N/D` reduction and symbolic-root retention;
7. deterministic `u72` expansion phase and Phase-5 resolution mapping;
8. monotone non-coarsening resolution expansion;
9. all 35 Phase-5 resolutions remain valid and identity-preserving;
10. Phase-9 1:1 information/reconstruction gates remain fail-closed;
11. deterministic replay and zero canonical/floating authority;
12. authenticated Phase-3/Pass-215 hydrated SUMMARY workload evaluation after strict C validation.

## Validation state

- scope checkpoint: committed
- implementation: pending
- strict dependency-scoped C validation: pending
- authenticated Phase10 benchmark: pending
- blockers: none known

## Exact next action

Implement the exact prime-rational constructor, rational envelope, symbolic polynomial witness, and monotone Phase-5 resolution expansion additively on this branch. Then run strict C validation and an authenticated workload benchmark. Preserve all Phase-9 information/reconstruction gates and do not merge, deploy, or promote authority.
