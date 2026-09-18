# Pass 220 I003 pre-implementation checkpoint — four-phase A:B:C max-hardware query calibration

Status: **RESTARTABLE PRE-TASK CHECKPOINT**

## Frozen predecessor

- repository: `danonbrez/Holofractal_Harmonicode`
- merge target: `main`
- working branch: `pass220-lo-shu-normalization-checkpoint-1`
- frozen I002 head: `f6be3098697b00c0a2ce056dca8fbd11388ef5a2`
- current merge base at task start: `63cee69390db05bd4b77da1cfd6f1b8cca4d461f`
- draft PR: `#491`

I001/I002 exact arithmetic and normalization evidence are frozen. I003 may repair forward only impacted surfaces.

## Required calibration basis

I003 SHALL reuse the repository's sealed four-phase time-bounded A:B:C methodology from:

- `contracts/pass219/PASS_219_RAW_RUNNER_ABC_NORMALIZATION_V1.md`
- `benchmarks/pass219/hhs_lane5_raw_runner_abc_gradient_calibration_v1.c`
- `tools/pass219/hhs_raw_runner_abc_calibration_analyze_v1.py`
- `docs/pass219/HHS_RAW_RUNNER_ABC_NORMALIZATION_V1_EVIDENCE.md`

Frozen phase gates:

- `xy: 0 -> 36`
- `yx: 36 -> 0`
- `zw: 18 -> 54`
- `wz: 54 -> 18`

Frozen A:B:C benchmark principles:

1. same deterministic dataset per phase/rank/sample;
2. timed order rotates `ABC/BCA/CAB`;
3. all timing is observational only;
4. exact integer/rational analyzer metrics;
5. negative controls must pass before performance evidence is admissible;
6. candidate-only search may not gain VM81/Hash72/Hash216 commit authority;
7. one common per-arm time membrane and one global time membrane;
8. runner identity and exposed hardware are evidence, not canonical truth.

## I003 arm definitions

For the query-ranking workload:

- **A — holographic composition:** I002 hierarchical metadata rank + deterministic weighted candidate sample over the same validated Hash216 candidates.
- **B — inherited Lane 5 control:** existing Pass 219 1.37 three-Hash72-segment Hash216 ranker, CPU-reference backend unless the runner exposes an explicitly selected compatible accelerator.
- **C — raw exact control:** direct three-lane HARMONICODE-symbol distance and stable ordering on the same query/candidate Hash216 strings; no I002 compositional metadata and no Lane 5 route/phase service.

All three arms MUST receive identical query identity, candidate IDs, Hash216 words, and candidate count. A receives additional pre-hydrated metadata already attached to those same candidate identities; that metadata is part of the dataset digest but not recomputed inside B/C.

## Max-hardware calibration

The benchmark SHALL retain the nine inherited ranks `8..2048` as comparable calibration points, then optionally continue exact doubling up to an environment-bounded `MAX_CANDIDATES` while all three arms remain under the same per-leg deadline.

The largest all-complete candidate count per phase is the observational `max_hardware_closed_n`. It is not a canonical limit and may vary by runner.

## Planned implementation

- add a Pass 220 bridge that composes the I002 ranker with the inherited Lane 5 optimizer without changing authority;
- add a four-phase A:B:C benchmark driver and exact analyzer;
- add focused deterministic tests for same-dataset identity, phase geometry, arm separation, exact ratios, max-N selection, and fail-closed negatives;
- add a dedicated workflow that first executes the inherited raw-runner A:B:C calibration preflight, then executes the I003 query benchmark on the same runner job;
- checkpoint before waiting for external CI.

## Next action

Implement the bridge, benchmark/analyzer/tests/workflow, run dependency-scoped local tests where possible, and seal the I003 restart record.
