# Pass 219 HHCQ prime-rational polynomial expansion Phase 10 restart

Date: 2026-09-07

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Frozen Phase 9 checkpoint/base: `715dfbc3f889ea1ec1e1111348f8c2523f0d1288`
- Phase 9 accepted validated implementation head: `e9620d1db390bb08294a8b207351c2708442892e`
- Phase 10 branch: `agent/pass219-hhcq-prime-rational-expansion-phase10-20260907`
- Current Phase 10 implementation/workflow head before validation: `443a3cdcc858a7069fdb5226f393e13ad1102ea3`
- Target: experiment branch only. No PR, merge, deployment, or canonical-authority promotion is authorized.

## Frozen inherited evidence

Preserve Phase 1 through Phase 9 evidence. Do not rerun unrelated history. Phase 9 remains frozen at accepted workflow run `34174828409`, job `101902057129`, with exact reciprocal economy parity 5184, independent 1:1 information closure, 112-byte policy state, deterministic replay, and zero canonical/floating authority.

## New user-supplied higher-resolution constraint source

Preserve the existing 542-byte core equation source unchanged and add the following source verbatim as a second constraint-extension source:

`Sqrt((A*B))*(A*B)/Sqrt((A*B))==A/B*B/A==((-x*y)^(((x+y^2)*(y+x^2))/((x²+y²)²*Sqrt((a*b)))))^x² where A,B are two primes and AB=P⁴`

The extension source is 135 UTF-8 bytes and has SHA-256:

`6d91bf7d4a70edf34ec5cd30a4ea7d04cc08af5013f7631576b118c369b2ea14`.

The runtime must not silently rewrite or replace this source. It may compile explicit exact witnesses from it, as previous HHCQ phases compile runtime invariants from the frozen core equation without claiming executable evaluation of every symbolic term.

## Phase 10 formalization

### 1. Replace the scalar `n` envelope with an exact two-prime rational pair

Phase 9 used the scalar reciprocal envelope

`1/n : 1 : n`.

Phase 10 refines the envelope with two prime-rational boundary terms `A` and `B` constructed from two distinct prime seeds `p` and `q` around a shared symbolic `P²` scale:

`A = P² * (p/q)`

`B = P² * (q/p)`

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

## Implemented files

New:

- `hhs_runtime/include/hhs_pass219_hhcq_prime_rational_expansion_1_30.h`
- `hhs_runtime/c/hhs_pass219_hhcq_prime_rational_expansion_1_30.inc`
- `tests/pass219/test_pass219_hhcq_prime_rational_expansion_1_30.c`
- `benchmarks/pass219/hhcq_prime_rational_expansion_phase10_benchmark.cpp`
- `.github/workflows/pass219-hhcq-prime-rational-expansion-phase10.yml`
- this restart record.

Modified additively:

- `hhs_runtime/include/hhs_runtime_exact_abi.h`
- `hhs_runtime/c/hhs_runtime_exact_abi.c`.

Implementation commits:

- scope checkpoint: `dfa3f1ae81364d8272366dbf0ed85e723804fde9`
- initial public ABI: `07c512e556650cdd031d76055707068ab9ae1984`
- clarified symbolic-root field: `a474bbe65c6911d9f2af33ba901e992f959cc851`
- exact C implementation: `d6cc65937c50e420a4c89a0f93660d3019e459a9`
- aggregate ABI header binding: `ab75f087e24d866d257f044a64dd2bbc794fc98b`
- aggregate exact implementation binding: `9563351c5c917acd3dfd87f6bf46e0a372aa5317`
- strict C invariant test: `47ceb7b56248b6dffe71cc23df026faacb5190c5`
- authenticated benchmark: `3a300bcd19e29cd4b8eae793c248b0993986ea58`
- Phase10 workflow: `443a3cdcc858a7069fdb5226f393e13ad1102ea3`.

## Implemented exact runtime behavior

### Public ABI version

`HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_VERSION = 0x0001001E` (1.30).

### Prime-rational constructor

- accepts distinct prime seeds up to 65,521;
- rejects composites, zero/unit values, equal prime seeds, invalid phase72 values, the singular `(x,y)=(0,0)` polynomial point, and invalid Phase-5 resolution indexes;
- emits exact squared ratios `p²/q²` and `q²/p²`;
- records `AB=P⁴`, `Sqrt(AB)=P²`, and reciprocal product closure as constructor witnesses;
- never numerically instantiates the symbolic core `P` for routing because the shared `P²` scale cancels from the boundary.

### Polynomial resolution expansion

- computes the exact reduced `N/D` witness;
- retains the `Sqrt(a*b)` denominator as an explicit symbolic-root flag;
- hashes the exact prime/polynomial/phase witness into the existing 72-step ring;
- maps that phase into the existing 35-member Phase-5 divisor lattice;
- final expanded resolution index is `max(base_resolution_index, polynomial_resolution_index)`, so expansion cannot coarsen the inherited Phase-5 decomposition.

### Prime-rational economy admission

The Phase10 candidate removes scalar `reciprocal_n` from the new decision surface. Each latency/memory/compression/translation axis is admitted only by exact rational cross multiplication against the `A/B <-> 1 <-> B/A` envelope around execution parity 5184.

Savings/debt settlement remains exact integer arithmetic around parity 5184. Redundancy, ECC, precision, and learning spends remain explicit. Information recovery, semantic closure, exact reconstruction, all-native translation, one-step translation, Phase-5 lock, and zero-authority conditions remain mandatory before admission.

### Deterministic selection

Among admitted candidates:

1. maximum expanded Phase-5 resolution index;
2. maximum net economy surplus;
3. minimum latency;
4. minimum memory;
5. minimum compression;
6. minimum translation;
7. stable lower route id.

## Strict C validation contract

The strict test includes:

- descriptor/version/parity/source SHA lock;
- verbatim 135-byte extension-source comparison;
- exact `p=2,q=3` boundary `4/9 : 1 : 9/4`;
- exact polynomial point `(x,y)=(1,1)` reducing to base `-1`, exponent-rational witness `1/1`;
- composite/equal-prime/invalid-phase/singular-point rejection;
- exhaustive `p=2,q=3`, all valid 72x72 phase-pair coverage proving all 72 ring phases and all 35 polynomial resolution indexes are reachable;
- deterministic point `(x,y)=(0,17)` lifting base resolution index 30 to index 34 / one parameter;
- direct lossless parity admission;
- proven synthetic lower-resolution expansion with 7,776 savings, 4,000 spend, net +3,776 and exact proof flags;
- same candidate with proof flags removed must reject despite positive budget and 1:1 planned information accounting;
- upper/lower rational-bound rejection;
- information mismatch rejection;
- overspend rejection;
- deterministic multi-candidate selection;
- zero canonical/floating authority.

## Authenticated benchmark contract

The benchmark reuses the frozen authenticated Phase3/Pass215 frame artifact from run `34138427959`, SHA-256 `63d0f8816d4c04e10eb5d9644c9c60015b8cdd3b1235f114b3f1821ef08a3433`.

It will:

- read the 529 authenticated SUMMARY records / 489 unique chunk digests;
- prepare all 4,761 existing local Phase-5 regions;
- re-run exact Phase-5 decomposition/recomposition for every region;
- derive deterministic prime pairs and `x,y` phase coordinates from authenticated digest/anchor identity;
- run and replay the Phase10 expansion on all 4,761 regions;
- require no coarsening on every region;
- admit a direct proven lossless parity candidate for every region;
- construct legal factor-2/factor-3 lower-resolution candidates with a wide exact `p=2,q=5` envelope, planned 1:1 information accounting, and positive structural budget, but with reconstruction/semantic/cross-modal proof flags deliberately zero;
- require all such unproven lower-resolution candidates to remain rejected.

Lower-resolution execution is **not** measured in Phase10 and materialized reconstruction is still deferred to the next bounded experiment.

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

- scope checkpoint: complete
- implementation: complete through `443a3cdcc858a7069fdb5226f393e13ad1102ea3`
- aggregate exact ABI binding: complete
- strict dependency-scoped C validation: pending CI
- authenticated Phase10 benchmark: pending CI
- workflow file: registered on branch; this checkpoint push is intended to trigger it after registration
- blockers: none known before CI.

## Exact next action

Run the Phase10 workflow against this branch. If strict build/test/benchmark gates fail, repair only the impacted Phase10 surfaces and preserve the precursor evidence. If green, record the accepted run/job/artifact metrics in this restart record and create the final validated Phase10 checkpoint. Do not merge, deploy, or promote authority.
