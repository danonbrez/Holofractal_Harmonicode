# Pass 219 — Isolated Full-Stack / Base-ABI / Plain-x86 Benchmark v2 — Close

Date: 2026-09-17

## Restart identity

- repository: `danonbrez/Holofractal_Harmonicode`
- base commit: `e197edc7c8e39e56024771a798112d750531e01c`
- branch: `pass219/isolated-fullstack-baseabi-plainx86-benchmark-v2`
- merge target: `main`
- validated implementation head: `d8faa5bd3d11bd4e148fbffc85354d5894bca982`
- dedicated workflow run: `35261810960`
- job: `105339127180`
- validation result: PASS

## Completed work

Implemented a three-binary benchmark that repairs the contamination in PR #489 for the requested external comparison.

### A — full HHS service

- aggregate exact ABI public VM81 serialization;
- Lane 5 route/admission validation and receipt path;
- direct H36/Hash216 `M` bind/validate;
- candidate-only / no-canonical-authority checks.

### B — immutable base runtime ABI only

- compiled directly from `hhs_runtime/c/hhs_runtime_exact_abi_v1_1_base.inc`;
- VM81 frame import/export and exact byte equality;
- no aggregate ABI object;
- no Pass 219 object;
- no Lane 5/H36/Hash216 M call.

### C — ordinary Ubuntu/x86_64

- standalone C/libc binary;
- no HHS header, object, library, symbol, runtime call, receipt, or phase service;
- native byte copy + equality only.

All three use identical ordinary compiler flags as a controlled variable:

`-O3 -std=c11 -Wall -Wextra -Werror -pedantic -march=x86-64 -mtune=generic`

## Dataset

- one neutral deterministic dataset generated once outside timed regions;
- 648 bytes/record;
- 16,352 records;
- 10,596,096 bytes;
- SHA-256 `10596bc21ec6e4f2bee52b1aa39a446d419b5e30702da8d3c82b928e2dc768a1`;
- 36 rank/phase ranges;
- A/B/C payload digest equality required and verified for every range.

## Binary isolation validation

Dedicated run proved before timing:

- B object has no `pass219`, `lane5`, `harmonic36`, or `hash216` symbol;
- C executable has no `hhs_`/`HHS_` symbol;
- B dynamic links: libc + loader only;
- C dynamic links: libc + loader only.

## Measured global totals

- A: 16,352 records / 3,114,947,155 ns / ~5,249.527 records/s
- B: 16,352 records / 17,531,668 ns / ~932,712.164 records/s
- C: 16,352 records / 14,099,720 ns / ~1,159,739.342 records/s

Exact ratios:

- A:B = `17531668/3114947155` = 56 bp floor (~0.5628%)
- A:C = `2819944/622989431` = 45 bp floor (~0.4526%)
- B:C = `3524930/4382917` = 8042 bp floor (~80.4243%)

Interpretation: this is an end-to-end layer-cost comparison over the same neutral payload. A intentionally performs substantially more verified semantics than B/C. It is not an equal-feature microbenchmark and does not establish that an algorithmic optimization is slower than raw x86_64.

## Artifact

- artifact ID: `10515135246`
- ZIP SHA-256: `5368498f4140a72534cae46a89567ba208faee958c42e301f6c240784c02fcc0`
- size: 10,609,627 bytes

Contents include dataset/manifest/digest, native JSONL, exact result/report, runner identity, symbol evidence, and ldd evidence.

## Changed files in this cycle

- `docs/operations/restart/PASS_219_ISOLATED_FULLSTACK_BASEABI_PLAINX86_BENCHMARK_V2_START_20260917.md`
- `benchmarks/pass219/isolated_stack_v2/native_bench_common_v2.h`
- `tools/pass219/generate_isolated_stack_dataset_v2.py`
- `benchmarks/pass219/isolated_stack_v2/base_abi_only_v2.c`
- `benchmarks/pass219/isolated_stack_v2/plain_x86_ubuntu_v2.c`
- `benchmarks/pass219/isolated_stack_v2/full_lane5_stack_v2.c`
- `tools/pass219/run_isolated_stack_benchmark_v2.py`
- `tools/pass219/analyze_isolated_stack_benchmark_v2.py`
- `.github/workflows/pass219-isolated-fullstack-baseabi-plainx86-v2.yml`
- `docs/pass219/HHS_ISOLATED_FULLSTACK_BASEABI_PLAINX86_BENCHMARK_V2_EVIDENCE.md`
- this close checkpoint

## Repair history

- Initial A run failed closed because the neutral-record lowering incorrectly varied Lane 5 `integer_route_cost`.
- The invariant requires `evidence_count + contradiction_check_count + 1 = 5 + 1 + 1 = 7`.
- A was repaired to the exact constant `7`; B, C, and the neutral dataset were unchanged.
- Runner CPU capture command was separately repaired without changing benchmark semantics.

## Validation done

- strict compiler warnings-as-errors: PASS
- A aggregate exact ABI build/link: PASS
- B immutable base ABI build: PASS
- C standalone x86_64/libc build: PASS
- binary isolation scan: PASS
- B/C dynamic-link audit: PASS
- 36 rotated A:B:C samples: PASS
- all 16,352 records per arm completed: PASS
- same neutral payload digests across A/B/C: PASS
- exact analyzer: PASS
- artifact seal/upload: PASS

## Remaining closure

1. Open integration PR from this branch to `main`.
2. Use this restart file/evidence as the durable baseline.
3. If PR exact-head workflow is queued, do not hold forward progress solely on queue latency; implementation head is already dependency-scoped validated.
4. Merge when mergeable and verify `main` contains the feature head.

## Next optimization action after merge

Profile A internally against this frozen v2 baseline. Do not move HHS optimization/proof work into B or C. The first target is the dominant full-service cost while preserving exactness, receipts, Lane 5 authority boundaries, and direct H36/Hash216 `M` proof semantics.
