# Pass 219 — Lane 5 vs Raw Workflow Runner A:B:C Normalization v1 — Evidence

**Date:** 2026-09-17  
**Validated implementation head:** `4b1f1e3ac2190bab42c56233b7d9f1e4d5b679f4`  
**Workflow:** `Pass 219 Raw Runner ABC Normalization v1`  
**Run:** `35259971123`  
**Job:** `105332937683`  
**Result:** **PASS**

## 1. Runner identity

The comparison executed in one GitHub-hosted runner job:

```text
runner_os   = Linux
runner_arch = X64
kernel      = Linux 6.17.0-1022-azure x86_64 GNU/Linux
nproc       = 4
gcc         = gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
cpu_model   = INTEL(R) XEON(R) PLATINUM 8573C
```

This is a same-runner normalization. It is not a comparison between different hardware classes.

## 2. A:B:C definitions

```text
A = Lane 5 exact route validation
    + direct H36/Hash216 occurrence binding
    + M exponent-lattice bind/validate

B = matched Lane 5 exact route validation only

C = raw native-C validation/folding of the identical deterministic dataset record
```

C executes zero Lane 5 route admissions and zero M witnesses during the timed arm.

## 3. Same-dataset proof

For each `(rank, phase, iteration)` coordinate, the benchmark generates one deterministic record identity from the previous/current/goal values, five 32-byte digest fields, workload byte count, route cost, evidence and contradiction counts, reciprocal phase slots, and binary/trinary/nested-zero values.

Each arm independently accumulates that dataset identity. For every completed triplet:

```text
A.dataset_digest == B.dataset_digest == C.dataset_digest
```

A and B also retained identical Lane 5 route digests. The analyzer rejected any triplet lacking exact identity equality.

## 4. Four-phase gradient coverage

All four ordered reciprocal gates completed all nine ranks:

```text
xy : 0  -> 36
yx : 36 -> 0
zw : 18 -> 54
wz : 54 -> 18
```

```text
rank:      1     2     3     4    5    6    7    8    9
gradient: -1   -3/4  -1/2  -1/4  0   1/4  1/2  3/4   1
N target:  8    16    32    64   128  256  512  1024  2048
```

Per phase, each arm completed `4,088` records. Across four phases:

```text
A completed = 16,352
B completed = 16,352
C completed = 16,352
triplet phase/rank samples = 36
```

Timed arm order rotated `ABC/BCA/CAB` across samples.

## 5. Time-bound result

```text
global budget          = 1,800,000,000 ns
measured batch elapsed =   149,854,778 ns
within time bound       = true
```

Every arm/rank/phase completed its target before the 15 ms per-arm leg bound.

## 6. Global same-runner rates

Exact analyzer rates:

```text
A rate = 1635200000000 / 5875719 records/s
B rate = 1022000000000 / 3636261 records/s
C rate = 4088000000000 / 8183691 records/s
```

Approximate display values:

```text
A ≈ 278,297.856 records/s
B ≈ 281,057.933 records/s
C ≈ 499,530.102 records/s
```

These decimals are descriptive only; exact rational values are authoritative.

## 7. Exact normalized ratios

Global normalization:

| comparison | exact throughput ratio | bp floor | approximate |
|---|---:|---:|---:|
| A:B | `9696696/9792865` | 9901 | `0.990180` |
| A:C | `5455794/9792865` | 5571 | `0.557119` |
| B:C | `909299/1616116` | 5626 | `0.562645` |

Interpretation of this runner/sample:

- the direct M-proof increment is approximately `0.982%` below the route-only B path (`A:B ≈ 99.018%`);
- Lane 5 route-only B sustains approximately `56.264%` of the raw native C rate;
- full Lane 5 + M A sustains approximately `55.712%` of the raw native C rate;
- equivalently, raw C is approximately `1.777x` the B rate and `1.795x` the A rate on this runner.

The larger difference is therefore located primarily between raw native record validation and Lane 5 route/admission work, while the direct H36/Hash216 M proof remains a much smaller incremental component.

## 8. Phase aggregates

| phase | A:B | A:C | B:C | A:B bp | A:C bp | B:C bp |
|---|---:|---:|---:|---:|---:|---:|
| `xy` | `2085503/2106985` | `8141494/14748895` | `8141494/14598521` | 9898 | 5520 | 5576 |
| `yx` | `14493475/14607684` | `2734793/4869228` | `8204379/14493475` | 9921 | 5616 | 5660 |
| `zw` | `7262870/7393889` | `8214947/14787778` | `8214947/14525740` | 9822 | 5555 | 5655 |
| `wz` | `14562440/14612833` | `8173944/14612833` | `1021743/1820305` | 9965 | 5593 | 5613 |

## 9. Raw-control semantics

Arm C is not a no-op timer. It rebuilds the expected deterministic record, compares the complete defined payload, validates reciprocal phase/state fields, and folds a validation digest. A corrupted raw record is a fail-closed negative control.

Arm C is also deliberately not an HHS route: it emits no Lane 5 receipt and no Hash216 M witness. The benchmark therefore measures the added runtime cost of the HHS route/proof services relative to direct native validation of the same record.

This result should not be generalized to arbitrary application workflows without additional workload classes. It is the real-runner normalization of this exact calibration dataset and service path.

## 10. Difficulty / energy rating

The existing Pass 067.1 quantity remains the shared calibration denominator:

```text
logical tensor quantity          = 225 exact units
logical reciprocal-pair quantity = 450 exact units
rank-r rating denominator        = r * 450
```

The analyzer verified all four Pass 067.1 ordered energy gates. The 450-unit denominator is used only to put A/B/C on the same difficulty scale.

Arm C does **not** acquire HHS logical-energy authority, and physical joules/watts were not measured.

## 11. Authority membrane and negative controls

HHS arms preserved:

```text
candidate_only                               = 1
canonical VM81 mutation authority            = 0
canonical Hash72 authority                   = 0
canonical Hash216 authority                  = 0
canonical persistence authority              = 0
requires signed environmental VM81 admission = 1
translator_required                          = 0
```

Preflight fail-closed controls covered:

1. illegal reciprocal phase/inverse pair;
2. forced translator requirement;
3. corrupted M exponent coordinate;
4. corrupted raw dataset record.

## 12. Artifact receipt

```text
artifact id:   10514121807
artifact name: pass219-raw-runner-abc-normalization-v1
size:          12,869 bytes
SHA-256:       fa34645abd6d8a7500a55ec82184f3dddcc9081952b19bd04532a33fe97f7483
```

Artifact contents:

```text
native.jsonl
result.json
report.md
runner.txt
```

## 13. Optimization conclusion

The sealed A:B benchmark previously isolated the direct M-proof increment. This A:B:C run adds the missing real-runner native baseline and shows that the next high-value optimization target is the Lane 5 route/admission path itself: serialization, invariant checks, receipt formation, and associated exact routing work before the small incremental M-proof layer.
