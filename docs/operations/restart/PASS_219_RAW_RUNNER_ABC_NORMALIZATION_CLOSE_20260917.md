# Pass 219 — Raw Runner A:B:C Normalization — Close Checkpoint

**Date:** 2026-09-17  
**Base commit:** `9e1b8dd71d1f769e139a70e72eff63bb4bd1d854`  
**Branch:** `pass219/raw-runner-abc-normalization-v1`  
**Merge target:** `main`  
**Validated implementation head:** `4b1f1e3ac2190bab42c56233b7d9f1e4d5b679f4`

## Implemented files

```text
benchmarks/pass219/hhs_lane5_raw_runner_abc_gradient_calibration_v1.c
tools/pass219/hhs_raw_runner_abc_calibration_analyze_v1.py
contracts/pass219/PASS_219_RAW_RUNNER_ABC_NORMALIZATION_V1.md
.github/workflows/pass219-raw-runner-abc-normalization-v1.yml
docs/pass219/HHS_RAW_RUNNER_ABC_NORMALIZATION_V1_EVIDENCE.md
docs/operations/restart/PASS_219_RAW_RUNNER_ABC_NORMALIZATION_START_20260917.md
docs/operations/restart/PASS_219_RAW_RUNNER_ABC_NORMALIZATION_CLOSE_20260917.md
```

## Execution model

```text
A = Lane 5 route + direct H36/Hash216 M proof
B = Lane 5 route-only
C = raw native-C same-dataset validation/folding
```

All three arms run in the same executable/job. Timed order rotates `ABC/BCA/CAB`. A/B/C carry an independent same-dataset identity digest; equality is mandatory for every completed triplet.

## Validation executed

Dedicated workflow:

```text
Pass 219 Raw Runner ABC Normalization v1
run: 35259971123
job: 105332937683
result: PASS
```

Validated stages:

```text
runner identity capture                         PASS
aggregate exact ABI strict compile             PASS
inherited exact ABI link support               PASS
A:B:C strict C11 compile                       PASS
Python analyzer compile                        PASS
same-dataset native A:B:C run                  PASS
exact A:B:C analyzer                           PASS
artifact upload                                PASS
```

The native benchmark completed all 36 `(rank,phase)` triplets over ranks 1..9 and phases `xy/yx/zw/wz`.

## Measured baseline

```text
A:B = 9696696/9792865  = 9901 bp floor
A:C = 5455794/9792865  = 5571 bp floor
B:C = 909299/1616116   = 5626 bp floor
```

Approximate descriptive rates:

```text
A ~ 278,297.856 records/s
B ~ 281,057.933 records/s
C ~ 499,530.102 records/s
```

The dominant measured cost relative to raw C is in Lane 5 route/admission work. The direct M proof remains a smaller incremental cost (`A:B ~ 99.018%`).

## Runner

```text
Linux X64
Ubuntu 24.04 hosted runner
kernel 6.17.0-1022-azure
4 logical processors exposed
INTEL(R) XEON(R) PLATINUM 8573C
gcc 13.3.0
```

## Evidence artifact

```text
artifact id: 10514121807
SHA-256: fa34645abd6d8a7500a55ec82184f3dddcc9081952b19bd04532a33fe97f7483
files: native.jsonl, result.json, report.md, runner.txt
```

## Authority state

Unchanged for HHS arms:

```text
candidate_only                               = 1
canonical VM81 mutation authority            = 0
canonical Hash72 authority                   = 0
canonical Hash216 authority                  = 0
canonical persistence authority              = 0
requires signed environmental VM81 admission = 1
translator_required                          = 0
```

Raw arm C has zero Lane 5 receipts and zero M witnesses. The shared 450-unit difficulty denominator does not grant C HHS logical-energy authority. Physical energy was not measured.

## Negative controls

Fail-closed checks passed for:

1. reciprocal phase mismatch;
2. forced translator requirement;
3. corrupted M exponent coordinate;
4. corrupted raw dataset record.

## Validation remaining

- final-head workflow triggered by this restart checkpoint may still be queued/executing; it is not required to delay the restartable checkpoint under the repository forward-progress rule;
- open PR to `main`;
- merge if repository merge state remains clean and no dependency-scoped regression appears;
- verify merged `main`.

## Next action

Use the sealed raw-runner baseline to optimize the Lane 5 route/admission path—especially serialization, invariant checking, and receipt formation—then rerun this exact A:B:C service without changing the dataset contract.
