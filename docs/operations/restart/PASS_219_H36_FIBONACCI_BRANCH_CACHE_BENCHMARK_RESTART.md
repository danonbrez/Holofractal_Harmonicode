# Pass 219 H36 Fibonacci Branch-Cache Benchmark Restart

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Authoritative base: `main @ ead4e312556179b9a090c7a5b5d898d298be72a0`
- Working branch: `agent/pass219-h36-fibonacci-branch-cache-benchmark`
- Intended target: `main`
- Benchmark source commit: `d880eb40a5b7a01ce8f1331c21829dcbb195d13c`
- Workflow wiring commit: `1bc295d9b7f04beb1cb4192899d08c06fec8efcd`
- Evidence commit: `af0c3eaa6eb23a41ab8a1605c95f283998734839`

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
