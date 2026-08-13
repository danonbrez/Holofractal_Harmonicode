# Pass 215 Iteration 16 Restart Record

## Parent authority

- parent closure: Pass 215 Iteration 15
- parent head: `7d58d29fa9690f4239b8e8f3ad30f34736f47f84`
- parent tree: `d556c1bb07e62cefba8f45df9c6cf8978645cdc8`
- branch: `agent/pass215-transformer-ingestion-benchmark`
- merge target: `main`
- draft PR: `#172`

## Implemented surfaces

- `hhs_backend/runtime/hhs_pass215_iteration16_multistep_certified_greedy_v1.py`
- `tools/pass215_iteration16_multistep_certified_greedy.py`
- `tests/test_hhs_pass215_iteration16_multistep_certified_greedy_v1.py`
- `scripts/run_pass215_iteration16_validation.sh`
- `contracts/pass215/PASS_215_ITERATION_16_CONTRACT.json`
- `evidence/pass215/PASS_215_ITERATION_16_IMPLEMENTATION_RECORD.json`
- `docs/pass215/ITERATION_16_MULTISTEP_CERTIFIED_GREEDY.md`
- `docs/pass215/ITERATION_16_RESTART_RECORD.md`
- `.github/workflows/pass215-iteration16-multistep-certified-greedy.yml`

## Repair-forward history

1. Initial three-step source added persistent symbolic and interval KV state.
2. Before real execution, the inherited Iteration 15 direct trigonometric contract was found to stop at `|argument| <= 4`. Iteration 16 widened the bounded direct domain to `|argument| <= 8` while retaining the same rational Taylor recurrence and explicit global Lagrange remainder. No pi-based range reduction, float, or transcendental point approximation was introduced.
3. Source run `31274979871` passed cumulative Iterations 1–16 validation and authenticated model SHA verification, then failed before runtime execution because direct invocation of the CLI did not place the repository root on `sys.path`.
4. The CLI was repaired to resolve and prepend its own repository root. No runtime mathematics or authority contract changed in that launcher repair.
5. Source run `31275109028`, job `93147306407`, succeeded end-to-end against source head `b975d8e4ae4db3bfb13cf5146ef7bcd130315f2a`, tree `99c2b92fbb55be6ea04b8d9497b14749b7628aa3`.

## Source validation

- cumulative tests: 153 passed
- authenticated model SHA-256: `6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04`
- certification precision: 256 bits
- certified greedy steps: 3
- selected token IDs: `[450, 6575, 471]`
- selected tokens: `["▁The", "▁sun", "▁was"]`
- prefix symbolic reconstructions: 1
- prefix interval replays: 1
- prefix replays after initialization: 0
- final cache sequence length: 7
- cross-process replay: true
- semantic exactness: true

## Frozen source identities

Selection roots:

1. `aac3225975c44b9b761dd131afedfc01123a3c5da187f76bd9de5c9bf2abee94`
2. `ba04d7c30b6734f7229d13e0684d7d9458803f4a5387c9c5547ef4f2d4e23050`
3. `4043e960f6454b4ad0849b3997ddbbe8a5df5e92f827e8d70fcf424999bf7cba`

Step roots:

1. `ed206f708fbcfde331f743c74447f758453836073d7fed5048bb53caf683dc36`
2. `ef520f4059b141fe9cb2be28a14a3fcdda9bf627e2adf4b77a910a827f108487`
3. `9adc01a187186944eb106c364591862dbd528004a2c5103b06860d1ab01a7a21`

Append roots:

1. `c76459385ed0d81c63e37784c6e2094d81322984fae400c9198ddc8a8ae23fcf`
2. `6860a9e610242e40f5663f6504cc38fbfa8fea4e204f5769cc21d2a639475b10`
3. `0a0d6ba7a9745807e1b31c86d27cc194886d4e7626db4977bdc0c0dd46773668`

Strict margin numerators over denominator `2^256`:

1. `70720847530373533701037217556150495820946814614155944479330263861023836594083`
2. `52061193875608784337062928647429738588909619009682567606596774987344451831202`
3. `193657899013710044665666654111106332332304443895809042801962786721935476665245`

Terminal identities:

- chain Hash216: `28d8741be087bcb0ca6016ea7d88a24522408d965b9ee3198185dd93497f7448`
- final interval suite Hash216: `78fe60fdbe4f5d09dfb0c1f39d2478717e08d3a3d5da0cfb50c071235dc13878`
- final symbolic DAG Hash216: `6591757219694e1f375fa8e115f1e4d87496e93ec12d95e7745dd15033b9ac68`
- suite Hash216: `13fe78e5ed5c03d3170dfb5345cf8b373ccb7b0cd98f5188c2a9532710207322`
- evidence Hash216: `8222ea90cb157ccc98049512b7b1a6cdd42bb125e5b90db93bcb614b9f9663fb`
- receipt Hash72: `pkaOYx48D?hAMtg*!bJ1(qSq-zdV/SP2LkOKB7RlZpj2CpIc06vv)6xC28H<FurVOKmP+ZSB`

Source artifact:

- artifact ID: `9026836619`
- artifact bytes: `14272`
- artifact SHA-256: `e1949810df041dbfbbada0f7de463a6f8ac393dab52b544195e474d2558adc46`

## Authority boundary

Promoted by the successful source run, subject to exact-head closure replay:

- bounded three-step complete-vocabulary logit certification;
- bounded three-step true logit-magnitude argmax selection;
- bounded three-step true greedy continuation;
- persistent symbolic and interval KV reuse with no prefix replay after initialization.

Still not promoted:

- probabilistic sampling;
- unbounded/general generation;
- arbitrary sequence-length transformer authority;
- canonical float interpretation;
- approximate transcendental point authority;
- dense-forward replacement;
- runtime mutation, canonical mutation, or migration.

## Remaining closure action

Freeze the implementation record as the final Iteration 16 restart-state commit. Then run `Pass 215 Iteration 16 Multi-Step Certified Greedy` directly against that exact commit. The terminal run must reproduce all source identities above. If it succeeds, do not create a subsequent commit, because doing so would invalidate exact-head closure.
