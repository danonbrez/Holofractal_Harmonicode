# Pass 219 Real-Source Translation Calibration v1 — Restart Checkpoint

**Date:** 2026-09-16  
**Base commit:** `7e6c3a2546627780ef3a7be9fb650151523d171c`  
**Branch:** `pass219/real-source-translation-calibration-v1`  
**Merge target:** `main`  
**Validated implementation head:** `9512a304d7c184cad05d72cb7164c330d6a9d42f`  
**Pull request:** `#480`

## Implemented

- deterministic calibration kernel over frozen real-source upstream observations;
- immutable GitHub evidence revision and multilingual CLIP model revision binding;
- exact-rational score capture;
- independent `FAMILY`, `SCENE_DETAIL`, and `IDENTITY` semantic scopes;
- exact TP/FP/TN/FN, precision, recall, false-positive rate, and sample separability intervals;
- false-match controls for text and multilingual image labels;
- explicit Eiffel day/night modifier boundary;
- candidate-only warm-hydration hints for threshold-closed family correspondences;
- I29/equivalent validation requirement before any canonical Hash216 routing;
- no automatic production-threshold mutation.

## Validation

Dedicated workflow:

```text
Pass 219 Real-Source Translation Calibration v1
run: 35126858627
head: 9512a304d7c184cad05d72cb7164c330d6a9d42f
result: SUCCESS
```

Successful bounded stages:

```text
compile calibration runtime: PASS
compile calibration tests: PASS
frozen manifest JSON validation: PASS
real-source calibration tests: PASS
```

## Repaired defect

The first workflow run exposed an import/interface-drift defect in the new calibration module: it referenced helper names not exported by the merged translation-ingress runtime.

Repair-forward commit `9512a304d7c184cad05d72cb7164c330d6a9d42f` binds directly to the inherited `ALLOWED_LICENSES` authority and keeps normalization local to the calibration layer. No inherited ingress semantics were changed.

## Calibration findings encoded by the tests

- The pinned Sentence Transformers README paraphrase score `0.6660` is below the current `3/4` diagnostic threshold, while the two unrelated controls remain much lower. This is recorded as a false-negative calibration signal, not threshold-change authority.
- Multilingual CLIP family observations for Russian Paris, German dog, and Spanish cat close above `3/4` with the selected false-match controls below threshold.
- Scene detail is intentionally separate: the night-Eiffel/Chinese-night positive observation is below `3/4`, while the day-Eiffel/Chinese-night control remains correctly negative. A family-level Paris correspondence therefore cannot promote a `night` modifier.

## Authority boundary

The calibration layer performs no network fetch in the deterministic kernel and cannot:

```text
change production thresholds
mint truth
commit canonical learning
mutate VM81
mint canonical Hash72
mint canonical Hash216
grant action authority
authorize permanent pruning
```

## Files changed

```text
hhs_runtime/hhs_pass219_real_source_translation_calibration_v1.py
data/pass219/translation_invariant_real_source_calibration_v1.json
tests/pass219/test_hhs_pass219_real_source_translation_calibration_v1.py
contracts/pass219/PASS_219_REAL_SOURCE_TRANSLATION_INVARIANCE_CALIBRATION_V1.md
.github/workflows/pass219-real-source-translation-calibration-v1.yml
docs/operations/restart/PASS_219_REAL_SOURCE_TRANSLATION_CALIBRATION_V1_RESTART_20260916.md
```

## Next action

If PR #480 remains zero commits behind and mergeable, merge to `main` and verify the resulting main head. The subsequent cycle may add a noncanonical live acquisition/replay worker that downloads revision-pinned assets, executes approved open-source projectors, seals output receipts, and feeds only immutable evidence into this calibration kernel.
