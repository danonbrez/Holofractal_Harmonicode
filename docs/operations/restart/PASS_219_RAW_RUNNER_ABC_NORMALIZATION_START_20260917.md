# Pass 219 — Raw Runner A:B:C Normalization — Start Checkpoint

**Date:** 2026-09-17  
**Base commit:** `9e1b8dd71d1f769e139a70e72eff63bb4bd1d854`  
**Branch:** `pass219/raw-runner-abc-normalization-v1`  
**Merge target:** `main`

## Objective

Extend the sealed four-phase reciprocal Lane 5 calibration over the same deterministic dataset with a third, real runner-native baseline.

```text
A = Lane 5 exact route validation + direct H36/Hash216 M bind/validate
B = matched Lane 5 exact route validation only
C = raw native runner validation/folding of the same deterministic dataset record
```

The new calibration must preserve the existing four ordered reciprocal gates (`xy`, `yx`, `zw`, `wz`), nine exact difficulty ranks, time bounds, exact rational normalization, and authority membrane.

## Same-dataset requirement

Each arm must consume the same deterministic record identity for the same `(rank, phase, iteration)` coordinate. A branch-local dataset digest will be computed independently of the HHS receipt/proof digest and compared across A, B, and C whenever completed counts match.

Raw arm C must not call Lane 5 admission, Hash72/Hash216 authority, persistence, or M proof APIs. It is a workflow-runner/native-C control, not another HHS route.

## Runner normalization

The workflow will execute all three arms sequentially in one GitHub-hosted `ubuntu-24.04` job using the same compiled executable and rotate timed arm order (`ABC`, `BCA`, `CAB`) across phase/rank samples to reduce order bias.

The analyzer will produce exact rational ratios:

```text
A:B
A:C
B:C
```

plus exact per-phase aggregates and difficulty-normalized rates. The existing 450-unit reciprocal-pair quantity remains a shared calibration denominator; it is not reinterpreted as physical energy for raw arm C. Physical joules are not measured.

## Planned files

- `benchmarks/pass219/hhs_lane5_raw_runner_abc_gradient_calibration_v1.c`
- `tools/pass219/hhs_raw_runner_abc_calibration_analyze_v1.py`
- `contracts/pass219/PASS_219_RAW_RUNNER_ABC_NORMALIZATION_V1.md`
- `.github/workflows/pass219-raw-runner-abc-normalization-v1.yml`
- measured evidence document after successful run
- close restart checkpoint after validation

## Validation requirements

- strict C11 compile with `-O3 -Wall -Wextra -Werror -pedantic`;
- exact aggregate ABI compile and inherited link support;
- same-dataset digest equality for A/B/C;
- all four phases and all nine ranks;
- negative controls for HHS phase/M invariants and raw-record corruption;
- exact rational analyzer output;
- raw C has zero HHS route receipts and zero M witnesses;
- candidate-only authority membrane unchanged for HHS arms;
- no physical-energy claim.

## Next action

Implement the A:B:C benchmark, analyzer, contract, and dedicated workflow; run the dedicated workflow; repair forward only affected surfaces; seal measured evidence; open/merge PR; verify `main`.
