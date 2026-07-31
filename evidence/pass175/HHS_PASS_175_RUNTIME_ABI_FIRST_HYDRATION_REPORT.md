# HHS Pass 175 Runtime ABI and First Hydration Report

## Verdict

`HHS_PASS_175_RUNTIME_KERNEL_ABI_AND_FIRST_HYDRATION_VERIFIED`

The Pass 175 Runtime kernel was built under strict C11 flags, loaded through the exported native ABI, benchmarked on the GitHub Actions x86_64 host, and exercised through the first sealed terminal hydration. The test then booted the canonical 18-stage firmware sequence, committed a conflict-free three-candidate batch through one VM81 authority and one Hash72 commit stream, and verified deterministic replay.

## Tested repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Pull request: `#96`
- Tested pull-request merge commit: `d80149721294c2817a9ab10db5d89494e0c66229`
- Merged implementation commit: `1473f9afee97f8df282e158166ebd0eb341d3a53`
- Evidence JSON commit: `31ba882a750fc5cdc676824a817f0555963652d1`
- Workflow run: `30626162861`
- Workflow job: `91141836821`
- Artifact: `8791434481`
- Artifact ZIP SHA-256: `d2d332b35c7baaefaaff9518093e5b54d2c1e3338da2a86520c1821ad9a99118`
- Benchmark report SHA-256 identity: `46867e5bddd12f9119d86f171e372c7ae33acc6da10e5710c8b900ea0a0c5a2a`

The benchmark harness and workflow blobs on the merged implementation commit are byte-identical to those exercised by the pull-request workflow.

## Native ABI correctness

All checks passed:

- ABI version: `0x00017501`
- exact low scalar circuit: preserved
- exact high scalar circuit: preserved
- VM5184 address encode/decode: passed
- all 243 control-word encode/decode round trips: passed
- VM5184 × G243 projected address encode/decode: passed
- candidate preparation and deterministic sorting: passed
- singleton VM81 admission callback and commit: passed

## First hydration correctness

All checks passed:

- permanent instruction count: `5,184`
- permanent identity count: `5,184`
- controls per instruction: `243`
- projected address count: `1,259,712`
- supported x86 instruction forms hydrated: `57`
- Hash216 secure store sealed: `true`
- secure store root SHA-256: `3df841a26c99b8ec6ae09e43f06252fe22ecc1fc81978fbc42e32dde13a26bfa`
- firmware ready: `true`
- firmware stages: `18`
- candidate batch: `3` candidates in `1` wave
- parallel candidate generation: `true`
- parallel state authority: `false`
- singleton VM81 commit authority: `true`
- Hash72 commit streams: `1`
- authority calls/epoch: `20`
- deterministic replay: `true`
- replay journal root SHA-256: `64528f9b5cc649b78e1ffaf8e5764f1caa10a9d487d5baf11cb29ef5e4ac23ba`

## Host benchmark observations

These timings are non-authoritative host observations from Ubuntu 24.04, x86_64, Python 3.12.13. They measure the Python `ctypes` ingress path as well as the native ABI operations and therefore are not raw in-kernel cycle measurements.

| Operation | Work per sample | Median | Median throughput | p95 |
|---|---:|---:|---:|---:|
| Address encode/decode round trip | 50,000 | 114.963 ms | 434,924 round trips/s | 116.863 ms |
| Projected address round trip | 50,000 | 135.830 ms | 368,107 round trips/s | 136.142 ms |
| Prepare + sort + VM81 commit | 32,000 candidates, 64 per batch | 33.482 ms | 955,748 candidates/s | 33.669 ms |

Hydration-path observations:

| Stage | Elapsed |
|---|---:|
| Runtime initialization and permanent fabric construction | 710.388 ms |
| Cold hydration and VM81 seal | 241.381 ms |
| 18-stage firmware boot | 82.897 ms |
| Three-candidate execution | 9.749 ms |
| Deterministic replay | 3.069 ms |
| Complete benchmark process | 2.533 s |

## Regression and artifact closure

- Native artifact build/test: passed
- Benchmark receipt validation: passed
- Pass 175 dependency-scoped regression: `23 passed`, `1` non-failing pytest configuration warning
- Evidence artifact upload: passed
- Native artifacts retained in the Actions artifact include the manifest, native test receipt, Hash216 identity and SHA-256 checksum sidecar.

The unrelated Vercel deployment status was not used as a Runtime-kernel acceptance gate.
