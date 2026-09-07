# Pass 219 — Core Holographic Outcome-Linked Phase 4 Restart

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/pass219-core-dynamic-circuit-20260907`
- Phase-3 checkpoint head: `5a95d75e351d82426de91b66a1a20877978abeb6`
- Phase-3 validated implementation head: `7fa7b3ed4af2d2605e4454fee9a785515de111d3`
- Phase-3 accepted run: `34138427959`
- Phase-3 evidence artifact: `10025484841`
- Phase-3 frame-binary SHA-256: `63d0f8816d4c04e10eb5d9644c9c60015b8cdd3b1235f114b3f1821ef08a3433`
- Current main observed before Phase 4: `40bce1e30790eb3339da3599ba3be740010dae9a`
- No PR/merge/default-runtime/authority promotion authorized.

## User-authorized Phase-4 scope

Continue from Phase 3 into a held-out outcome-linked experiment. Determine whether the four-lane router can learn to choose the lowest-cost exact downstream lane rather than merely producing context-sensitive lane distributions.

## Frozen input

Reuse the accepted Phase-3 artifact instead of reconstructing Pass-215 again. The Phase-4 workflow shall download run `34138427959` artifact `pass219-core-dynamic-circuit-experiment` and verify the exact Phase-3 frame-binary digest before evaluation.

Only the `SUMMARY` VM81 view is used for lane-quality learning, because it binds all raw bytes of each authenticated chunk into one 5184-bit frame. HEAD/MIDDLE/TAIL remain frozen Phase-3 evidence and are not rerun for the learning split.

## Comparable downstream task

All four lanes are evaluated as alternative exact implementations of the same task: consume one 648-byte / 5184-bit VM81 frame, execute the lane-specific repository path, and recover/validate the exact original frame without canonical mutation.

Lane order remains:

1. `RAW5184_X86_64`
2. `VM81_HASH72_HASH216`
3. `OCTONION_DUAL_STEREO_TERNARY`
4. `HARMONIC36_144X36`

Eligibility rule: a lane cannot win a record unless exact frame semantics are preserved and the lane-specific invariant checks pass.

Planned lane paths:

- RAW5184: global 648-byte bytecode copy plus VM81 import/export equality.
- VM81/Hash216: VM81 validation, exact core-feature extraction, transition-identity validation, and frame export equality.
- Octonion/audio: VM81 -> PCM64 -> VM81 exact roundtrip plus octonion/stereo/ternary hydration validation.
- Harmonic36: exact 5184-bit <-> 144x36 packing/unpacking with repository H36 coordinate validation over all 144 word anchors.

For eligible lanes, bounded repeated native execution is measured with `steady_clock`; the per-record median nanoseconds selects the observed outcome label. Timing is observational and runner-specific, but semantic eligibility is exact and mandatory.

## Held-out identity split

Partition by content-addressed chunk digest, never by record ordinal or checkpoint slot. All references to the same chunk digest, including reused chunks across both Pass-215 checkpoints, must remain in the same partition.

- deterministic training partition: digest bucket != 0 modulo 4;
- deterministic held-out partition: digest bucket == 0 modulo 4;
- required train/held-out digest overlap: `0`.

The router may train only on training identities. Held-out labels are never fed back into the state.

## Learning/evaluation gates

1. accepted Phase-3 artifact digest verified before use;
2. exactly 529 SUMMARY references consumed;
3. all four downstream lanes exact on every evaluated SUMMARY record;
4. every record receives measured median cost for all four lanes;
5. training and held-out chunk identities are disjoint;
6. pre-training held-out accuracy and cost regret recorded;
7. train with positive feedback only toward the measured winning lane on training identities;
8. post-training held-out accuracy and cost regret recorded;
9. repeat held-out inference from cloned trained state and require identical lane decisions;
10. report improvement, regression, or no-improvement honestly; do not weaken or rewrite the outcome after measurement;
11. preserve candidate-only / zero canonical VM81, Hash72, Hash216, persistence and floating-point authority.

A green workflow means the experiment executed validly. It does not predetermine that learning must improve; the classification must reflect the measured held-out result.

## Planned files

- `benchmarks/pass219/core_holographic_pass215_outcome_linked_benchmark.cpp`
- `.github/workflows/pass219-core-outcome-linked-phase4.yml`
- this restart record.

## Restart action

Resume from this file. Implement the benchmark and bounded workflow, reuse the frozen Phase-3 artifact, run the held-out experiment, repair only correctness/build defects, preserve a non-improving learning result if that is what the evidence shows, then update this record with the exact run/artifact/results and commit a final repository-visible checkpoint. Do not open or merge a PR without separate authorization.
