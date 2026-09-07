# Pass 219 — Core Holographic Real-Workload Phase 3 Restart

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Phase-2 checkpoint head: `3b33b0d35d05a7d19093bcb85a3b0523adb3823c`
- Validated Phase-2 implementation head: `463ffb810fed55537426ee69de4e519348419c36`
- Branch: `agent/pass219-core-dynamic-circuit-20260907`
- Current main observed before Phase 3: `40bce1e30790eb3339da3599ba3be740010dae9a`
- Branch relation inherited from Phase 2: experimental branch, no PR/merge/default promotion authorized.

## User-authorized Phase-3 scope

Extend the validated Phase-2 four-lane experiment from synthetic lane calibration into representative repository workloads, and explicitly run **both** the Phase-1 fused dynamic circuit and the Phase-2 four-lane circuit across the already-ingested/hydrated Pass-215 language-model state.

Required workload families:

1. RAW5184 serialization/hydration;
2. Pass-219 RNA transcription / C++ RNA cell wall;
3. Hash216/cache routing surfaces;
4. octonion/audio hydration and security transport;
5. Harmonic36 / 144x36 stack-selection/cache surfaces;
6. Pass-215 hydrated language-model weights/checkpoints.

## Frozen Pass-215 model provenance

Use the already-validated terminal Pass-215 workload rather than inventing another model fixture:

- source repository: `ggml-org/tiny-llamas`
- source file: `stories15M-q4_0.gguf`
- source SHA-256: `6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04`
- Pass-215 Iteration-20 earlier hydrated checkpoint canonical bytes: `413411982`
- Pass-215 Iteration-20 later hydrated checkpoint canonical bytes: `475300933`
- earlier checkpoint root Hash216: `151113337a143adb29eecfa9cb1f4df41b6458953afb2c5258b97dff5f3643b4`
- later checkpoint root Hash216: `bff3f18e1324caacdbd610b833b3ebd6ebe35e525821c0ffad349fc81ad9474f`
- shared content-store root Hash216: `b7a9eb1678f263f20c5b61c0d9d3f01b76b152e2786b7e887ecb8265cbe454da`
- shared checkpoint bundle root Hash216: `14953737a095ee9365386e436706cedd7a77328a04eb4dc3d5e45935cd367c8a`

The Iteration-20 content store is the hydrated checkpoint representation under test. It contains content-defined chunks over the six large checkpoint components and reconstructs both Iteration-18 checkpoint states exactly.

## Model-weight hydration evaluation contract

For every content-addressed chunk referenced by either hydrated checkpoint:

1. verify the content-store address and canonical zlib transport encoding using the inherited Pass-215 Iteration-20 decoder;
2. feed **all raw bytes** of that chunk into a deterministic domain-separated SHA-512 expansion that produces one exact 648-byte / 5184-bit VM81 hydration frame;
3. additionally derive bounded local raw-segment frames (head/middle/tail, zero-padded only for the final short segment) so local byte structure is exercised separately from the all-byte chunk summary;
4. run the Phase-1 fused dynamic circuit on each derived frame;
5. run the Phase-2 holographic four-lane prepare/score path on the exact same frame with the source checkpoint/manifest/chunk identity bound into its Hash216 transition identity;
6. require exact equality between Phase-1 direct core features and the `core_features` embedded inside the Phase-2 prepared tensor;
7. require deterministic replay of lane scores/selection and zero canonical authority leakage;
8. measure lane-selection distribution and declared logical-work accounting separately for earlier, later, reused, and incremental checkpoint chunks.

This establishes circuit behavior over the entire hydrated checkpoint **chunk set**. It does not claim that one 5184-bit chunk-summary frame is a bijective substitute for the original hundreds of megabytes, nor does it grant the candidate circuit canonical model-execution authority.

## Learning/evaluation rule

Do not train and evaluate on the same content identities. If a bounded learning experiment is included, partition by content-addressed chunk identity or checkpoint role, preserve source identities in the receipt, and report held-out behavior honestly. Do not weaken a failed improvement gate.

## Authority boundary

Phase 3 remains candidate-only. No new surface may independently gain:

- canonical VM81 mutation authority;
- Hash72 mint/commit authority;
- Hash216 commit/persistence authority;
- canonical persistence authority;
- floating-point numerical authority.

Pass-215 transport compression remains storage/transport representation only and is not numerical authority.

## Planned implementation

- add a Phase-3 model-checkpoint workload driver under `benchmarks/pass219/`;
- add focused tests for its deterministic chunk-to-VM81 hydration and receipt binding;
- extend `.github/workflows/pass219-core-dynamic-circuit-experiment.yml` with the real repository workload tests and authenticated Pass-215 model execution;
- upload Phase-1/Phase-2/Phase-3 JSON evidence together;
- repair forward on any behavioral failure;
- update this file with exact validated run, measurements, artifact digest, branch drift, and next action.

## Restart action

Resume from this file. Implement the Phase-3 driver and workflow gates, run dependency-scoped repository-native validation, preserve any failed-run evidence and diagnosis, then seal a new checkpoint. Do not open or merge a PR without separate explicit authorization.
