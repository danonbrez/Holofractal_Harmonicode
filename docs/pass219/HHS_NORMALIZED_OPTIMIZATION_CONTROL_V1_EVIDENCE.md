# HHS Normalized Optimization Control v1 — Evidence

**Date:** 2026-09-16  
**Status:** EXECUTED / RUNNER-NORMALIZED / ORDINARY-MATERIALIZATION-CONTROL / EXACT-MEMBRANE-PASS

## Delivery identity

```text
pull request: #472
validated implementation head before evidence-only documentation update:
660b73c255985507fc918dade76ea043c29ff975

workflow: HHS Normalized Optimization Control v1
workflow run: 35088407303
job: validate-optimization-control
job id: 104768636949
result: success
artifact: hhs-normalized-optimization-control-v1
artifact id: 10443625205
artifact ZIP SHA-256:
0e1cba471b82b7124fa730305fe0036265fe220a34e88e9493fe4db07e6f5a21
```

## Runner observation

```text
runner label: ubuntu-24.04
runner image: 20260907.300.1
OS: Ubuntu 24.04.5 LTS
Azure region: westus3
CPU: INTEL(R) XEON(R) PLATINUM 8573C
logical CPUs: 4
observed memory: 16,372,440 KiB
kernel: 6.17.0-1022-azure
compiler: GCC 13.3.0
active Lane 5 benchmark threads: 1
```

This is a fresh hosted VM and differs from the Xeon 6973P-C used by the first frozen qinfo reference observation.

## Lane 5 exact control observation

```text
candidate routes: 1,000,000
elapsed_ns: 4,011,378,559
candidate-rate floor: 249,290/s
mean interval: 4,011.378559 ns
full-manifold address: 56 bytes
stream state: 568 bytes
materialized intermediate states: 0
count-saturation continuation: PASS
```

The exact authority membrane passed:

```text
canonical VM81 mutation authority: false
canonical Hash72 authority: false
canonical Hash216 authority: false
signed environmental VM81 admission required: true
observational timing only: true
```

Normalized rates for this runner observation:

```text
Gamma_basis:
110,743,243.45988789152434277171249216955549771525188683891278609941207925431778721
bits-equivalent/s

Gamma_route:
442,972,973.83955156609737108684996867822199086100754735565114439764831701727114884
bits-equivalent/s

Gamma_qudit: 17,948,880 72-level coordinate-symbols/s
Gamma_VM5184: 8,974,440 block-coordinates/s
```

Historical-reference index:

```text
I_shot = I_basis = I_route = I_qudit = I_VM5184
       = 0.770467027448023068578333956613517865476562089523638802436664946207314321742382331397559008
```

This index is not interpreted as a code regression because the underlying hosted CPU changed. It is evidence for using paired same-runner control/candidate measurements for optimization acceptance.

## Executed ordinary von Neumann materialization control

The control compiled against the same exact ABI and compiler.

Native sizes:

```text
route descriptor: 296 bytes
Lane 5 stream reducer: 568 bytes
```

One-million-item storage controls:

```text
1,000,000 route descriptors:
296,000,000 bytes

1,000,000 uint64 IDs:
8,000,000 bytes

1,000,000 56-byte full-manifold coordinates:
56,000,000 bytes
```

Historical 256-million-position controls:

```text
256,000,000 uint64 IDs:
2,048,000,000 bytes

256,000,000 56-byte coordinates:
14,336,000,000 bytes
```

Integer-floor memory ratios against the 568-byte stream reducer:

```text
1M fixed route descriptors / stream = 521,126x
1M full coordinates / stream        = 98,591x
```

Minimal `uint64_t` array memory-traffic control:

```text
items: 1,000,000
fill_ns: 1,830,589
scan_ns: 1,218,198
checksum: 3,261,120
```

These fill/scan timings do not perform Lane 5 route validation. They are intentionally a lower-bound conventional memory/materialization control and must not be presented as a semantic speed comparison.

## Interpretation membrane

Valid comparisons:

```text
memory/materialization:
explicit stored representations vs fixed Lane 5 reducer state

semantic optimization:
paired Lane 5 control vs Lane 5 candidate with identical route validation

end-to-end application:
equivalent complete workloads including generation, lookup, hashing,
validation, admission, persistence, and identical verified outputs
```

Invalid comparison:

```text
minimal uint64 memory scan time
vs
full Lane 5 proof-carrying validation time
```

because those operations do not perform equivalent semantic work.

## Result

```text
normalized optimization-control test: PASS
cumulative exact ABI build: PASS
million-candidate Lane 5 control: PASS
qinfo normalization: PASS
exact optimization membrane: PASS
ordinary materialization control: PASS
artifact upload: PASS
```
