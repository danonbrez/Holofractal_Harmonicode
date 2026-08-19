# Pass 219B Iteration 2 — Phase Locality Benchmark Restart Record

## Base and branch

- Repository: `danonbrez/Holofractal_Harmonicode`
- Frozen Pass 219B 1.0 parent: `9d6d00e3f76ce84d0f6874d9e136c468a9faff7e`
- Branch: `agent/pass219b-iteration2-phase-locality-benchmarks`
- Review target: `agent/pass219b-phase-quantized-selective-hydration-i1`
- Canonical `main`: untouched
- Production deployment: not authorized / not performed

## Scope

Benchmark-only extension. No runtime authority or generating-tensor semantics are modified.

Added:

- `benchmarks/pass219b/pass219b_phase_locality_benchmark.cpp`
- `benchmarks/pass219b/pass219b_pass208_cpu_reference_benchmark.py`
- `.github/workflows/pass219b-phase-locality-benchmarks-i2.yml`
- `docs/pass219/PASS_219B_PHASE_LOCALITY_BENCHMARK_I2.md`
- this restart record

## Measurements

1. dense vector candidate scan vs exact phase-origin shortlist over the `5,184 * 81` surface;
2. exact hash-map cache lookup vs exact dense phase address inside one locally hydrated surface;
3. full 419,904-descriptor materialization vs one-origin 5,184-descriptor materialization;
4. actual inherited Pass 208 `CPU_REFERENCE` expansion: 162 branches vs two phase-selected branches.

All optimized paths require equality with the corresponding reference result. No wall-clock speedup threshold is used as an admission criterion.

## Accelerator boundary

GitHub-hosted jobs run Pass 208 with:

```text
HHS_PASS207_GPU_BACKEND=CPU_REFERENCE
HHS_PASS207_REQUIRE_PHYSICAL_GPU=0
```

Therefore physical GPU speedup remains unmeasured. The deterministic branch/lane work reduction can be measured; physical device throughput cannot be claimed from this run.

## Validation state

- benchmark implementation: complete
- dedicated exact-head run: pending PR creation
- dedicated synthetic-merge run: pending PR creation
- frozen measured evidence: pending terminal benchmark results

## Next action

Open a stacked draft PR against frozen Pass 219B 1.0, execute exact and synthetic benchmark jobs, inspect real timing/output artifacts, repair benchmark-owned defects if any, then record measured results and a frozen checkpoint. Do not merge or wire the optimization into inherited vector/cache/GPU paths until the measurements and semantic boundaries are reviewed.
