# Pass 219 H36 Fibonacci Branch-Cache Benchmark Restart

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base: `main @ ead4e312556179b9a090c7a5b5d898d298be72a0`
- Working branch: `agent/pass219-h36-fibonacci-branch-cache-benchmark`
- Intended target: `main`
- Benchmark source commit: `d880eb40a5b7a01ce8f1331c21829dcbb195d13c`
- Workflow wiring commit: `1bc295d9b7f04beb1cb4192899d08c06fec8efcd`
- Evidence commit: `af0c3eaa6eb23a41ab8a1605c95f283998734839`
- Emergent benchmark commit: `5a413fdd70bb07b54999ffeb5f2acd945438cf0c`
- Emergent evidence commit: `6b04dfea0c6a7ae33fbdd9b37431f4203745e691`
- Restart extension commit: `4e675c3053d0fac3dbb1bd72ecc7d17768e8f975`
- Temporary trigger cleanup commit: `2d1447fd78ce2f68aa86c8f4f2121b67795335ce`
- Unused targeted-workflow removal commit: `5bcb33cbd2b866e699ad27ea70662c2fe0410d21`

## Scope completed

A candidate-only H36/Hash216 cache experiment was added without modifying frozen parent state.

The benchmark constructs:

- four validated resident parent selections as immutable lane roots;
- 144 branch descriptors as `4 × 36` H36 cells;
- Fibonacci asymmetric subdivision beginning at `144 -> 89 + 55`;
- previous-state branch references rather than payload mutation or branch copies;
- deterministic reversible receipt chains for all 144 branches;
- four compatible lane-composition receipts per branch, 576 total;
- a compact Fibonacci identity index for nonlocal equivalent-state lookup.

## Validation

Workflow: `Pass 219 Harmonic36 Nested VM`

- Run: `33747123339`
- Job: `100622062802`
- Conclusion: `SUCCESS`
- Artifact: `9890078974`
- Artifact SHA-256: `b87a5db8148b77a2a6e5778cd5d399a2f9641cc6fba0c995797a1eac12535819`

All inherited H36 conformance, calibrated occupancy-4, capacity-8, manifest, and mandatory-integration gates completed successfully before and after the new benchmark step.

## Measured configuration matrix

Linux x86_64, 11 samples, 5 calibration repeats.

### Local branch resolution

- Existing validated parent-cache path: `453,614,559 ns` total
- Direct immutable branch reference: `449,889 ns` total
- Fibonacci-bucket branch reference: `764,255 ns` total
- Existing / direct ratio: `1,008,281 x1000` = about `1008.281×`
- Existing / Fibonacci-bucket ratio: `593,538 x1000` = about `593.538×`

The direct branch reference is the measured local winner.

### Nonlocal Fibonacci-equivalence resolution

- Full 144-cell scan: `1,498,586 ns` total
- Fibonacci bucket index: `1,500,673 ns` total
- Bucket / scan ratio: `998 x1000`

At exactly 144 cells the full scan is marginally faster; the bucket index is therefore not justified on the hot path by this measurement.

### Storage

- Full selection size: `296 bytes`
- Branch reference size: `40 bytes`
- Fibonacci index size: `316 bytes`
- 144 duplicated full selections: `42,624 bytes`
- Shared immutable parent cache + 144 refs + Fibonacci index: `8,732 bytes`
- Duplicate/shared ratio: `4.881×`
- Storage reduction: about `79.5%`

## Correctness invariants proved

- parent states remain unchanged;
- every branch references either the frozen root or an earlier branch in the same lane;
- every branch receipt recomputes exactly;
- every branch reverses to its frozen lane root;
- every complete parent pair satisfies Fibonacci additive division;
- all 576 compatible lane-composition receipts are deterministic;
- no VM81 mutation authority, Hash72 mint authority, Hash216 persistence authority, canonical persistence authority, or floating-point authority is introduced.

## Current best configuration

`DIRECT_IMMUTABLE_PARENT_REFERENCE_WITH_FIBONACCI_IDENTITY_METADATA_OFF_HOT_PATH`

Use the H36 word/branch address for direct local resolution. Preserve Fibonacci identity and subdivision metadata for equivalence, composition, and reasoning, but do not require a Fibonacci bucket lookup for every 144-cell local cache hit.

## Next implementation step

If productionizing this result:

1. add a versioned runtime branch-reference cache surface beside the existing frozen stack cache;
2. store immutable parent slot + previous-branch reference + receipt witness, not copied parent selections;
3. keep Fibonacci identity metadata attached to the branch descriptor;
4. use direct H36 word addressing for local reads;
5. retain bounded full-scan equivalence lookup at 144 cells until a larger fanout benchmark proves indexing beneficial;
6. rerun exact C ABI, branch-knowledge, Hash216 binding, occupancy-4/8, receipt replay, and artifact sealing gates.

## Blockers

None for the benchmark conclusion.

No production runtime path has been changed yet.


## Emergent-benefit scaling sweep

A second benchmark extended the same immutable-parent construction across:

`144, 288, 576, 1152, 2304, 5184` branch states.

Validation:

- workflow run: `33748212696`
- job: `100625507692`
- conclusion: `SUCCESS`
- artifact: `9890486924`
- artifact SHA-256: `5a3855eb8ab09e8a3d21023bb87256f55955f2f198e220e98cac2f909d456293`
- samples: 7
- calibration repeats: 5
- random-access rounds: 32,768
- composition rounds: 65,536
- equivalence rounds: 128

All inherited H36 gates through calibrated occupancy-4, capacity-8, optimization manifests, and mandatory integration remained green in the same run.

### Emergent result 1 — fork creation

Reference-backed branch creation beat full-selection duplication at every tested scale.

- 144 branches: `1.415×`
- 288: `1.430×`
- 576: `1.452×`
- 1152: `1.424×`
- 2304: `1.646×`
- 5184: `1.585×`

This establishes a direct branch-fork creation advantage in addition to the previously measured lookup advantage.

### Emergent result 2 — working-set locality

Random branch access through immutable references also won at every scale, and the advantage increased as duplicated payload pressure grew.

- 144 branches: `1.030×`
- 288: `1.100×`
- 576: `1.118×`
- 1152: `1.124×`
- 2304: `1.296×`
- 5184: `1.549×`

At 5184 branches, duplicated selections occupied `1,575,936 bytes`; the reference-backed representation occupied `270,808 bytes`, a `5.819×` storage ratio.

### Emergent result 3 — Fibonacci identity discovery

When the workload is isolated to discovering all branch identities sharing a Fibonacci class, the Fibonacci bucket index wins strongly:

- 144 branches: `6.815×`
- 288: `8.265×`
- 576: `8.798×`
- 1152: `7.389×`
- 2304: `4.874×`
- 5184: `4.774×`

This does not contradict the earlier 144-cell full-resolution measurement. In that earlier benchmark, every matched branch also executed direct-reference validation and composition resolution, so traversal cost was dominated by downstream work and the full scan was marginally faster. The new sweep isolates identity discovery itself.

The runtime rule is therefore:

`FIBONACCI BUCKET FOR EQUIVALENCE DISCOVERY -> DIRECT BRANCH REFERENCE FOR RESOLUTION`

rather than inserting the bucket into every local lookup.

### Emergent result 4 — compatible-composition receipt reuse

Memoized compatible-lane receipts beat recomputation at all scales:

- 144 branches: `2.527×`, break-even about `3,172` receipt queries
- 288: `2.542×`, break-even `6,254`
- 576: `2.511×`, break-even `12,580`
- 1152: `2.915×`, break-even `19,774`
- 2304: `3.087×`, break-even `35,269`
- 5184: `2.887×`, break-even `87,572`

A repeated composition path should therefore memoize only after its measured/query-count amortization threshold, while infrequent compositions remain computed on demand.

### Emergent result 5 — invariants survived scaling

For every tested scale:

- Fibonacci additive subdivision remained exact;
- full-scan and bucket equivalence sets were identical;
- memoized composition receipts equaled recomputed receipts;
- branch receipts remained deterministic;
- the four frozen parent cache states remained byte-for-byte unchanged;
- no canonical VM81, Hash72, Hash216, or persistence authority was introduced.

## Updated best configuration

The evidence now supports a composite runtime configuration:

1. **Local state lookup:** direct immutable parent/previous-state reference.
2. **Branch creation:** reference fork, never duplicate frozen payload.
3. **Equivalence discovery:** Fibonacci identity bucket.
4. **Equivalent-state resolution:** direct immutable branch reference after discovery.
5. **Repeated compatible compositions:** memoized reversible receipt after the measured amortization threshold.
6. **Infrequent compatible compositions:** compute the reversible receipt on demand.
7. **Frozen state:** immutable; all evolution is append-only branch forking.

The Fibonacci layer is therefore not merely metadata. It has a measured role as a selective nonlocal-equivalence index, while direct branch addressing remains the hot local path.

## Revised next implementation step

Productionization should now implement the branch-reference surface with three distinct paths rather than one:

- direct H36 branch lookup;
- Fibonacci-equivalence discovery index;
- adaptive compatible-composition receipt memoization.

The implementation must preserve the existing frozen parent cache and validate dependency-scoped exact ABI, Hash216 binding, branch-knowledge, receipt replay, occupancy, and artifact gates before merge.


## Final branch state for this test phase

The validated benchmark logic has not changed since workflow head
`735d543e7e1fceda3d73a4e5cfb13f7644418e7f`.

Subsequent commits only:

- sealed measured evidence;
- extended this restart record;
- removed the temporary branch trigger;
- removed an unused targeted workflow file that was not needed because the existing H36 workflow successfully executed the new benchmark.

No candidate benchmark validation remains outstanding.

Production runtime implementation remains intentionally separate. The next repository action, if authorized, is to implement the measured configuration on a new versioned branch-reference cache surface and then run dependency-scoped validation.
