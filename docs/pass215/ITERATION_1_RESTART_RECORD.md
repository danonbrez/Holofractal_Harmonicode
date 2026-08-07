# Pass 215 Iteration 1 Restart Record

## Repository state

- base `main`: `a4b7f6cf4da9111b036b6d4d93ea2d7b50e3eb2a`
- branch: `agent/pass215-transformer-ingestion-benchmark`
- merge target: `main`
- Pass 214 cumulative-main authority source: `063bcc1426b5bba106e139cb7dba1c540df090df`
- frozen Pass 215 profile Git blob: `b458d674a75a4cfc64a32b9203dd693e3603576e`

## Implemented files

- `contracts/pass215/PASS_215_ITERATION_1_CONTRACT.json`
- `hhs_backend/runtime/hhs_pass215_iteration1_transformer_ingestion_v1.py`
- `tools/pass215_iteration1_transformer_ingestion.py`
- `tests/test_hhs_pass215_iteration1_transformer_ingestion_v1.py`
- `scripts/run_pass215_iteration1_validation.sh`
- `.github/workflows/pass215-iteration1-transformer-ingestion.yml`
- `docs/pass215/ITERATION_1_EXACT_TRANSFORMER_INGESTION.md`
- `docs/pass215/ITERATION_1_RESTART_RECORD.md`

## Implemented behavior

- exact quantized tensor manifest validation;
- packed qint4/quint4 and integer 8/16/32-bit length accounting;
- canonical float rejection;
- safe bounded tensor slice loading with optional SHA-256 validation;
- per-tensor complete hydration-window partitioning;
- inherited Pass 212 encode/decode classification;
- generator-only / generator+exception / raw-fallback incidence;
- conservative raw fallback for incomplete tails without zero padding;
- exact reconstruction requirement for admitted windows;
- integer/rational-only aggregate accounting;
- protected physical-storage accounting from Pass 212;
- Hash216 evidence root and Hash72 receipt;
- frozen Pass 214 benchmark-profile blob guard;
- explicit preservation of Pass 213 canonical-mutation gates.

## Validation command

```bash
bash scripts/run_pass215_iteration1_validation.sh
```

Dedicated hosted gate:

```text
Pass 215 Iteration 1 Transformer Ingestion Incidence
```

## Validation coverage

The dependency-scoped test suite includes:

- exact 4/8/16-bit byte-size accounting;
- float rejection;
- one generator-only full hydration window;
- one sparse-exception full hydration window;
- one deterministic high-entropy full hydration window;
- exact decode/reconstruction for all complete windows;
- conservative incomplete-tail fallback;
- frozen profile binding failure;
- source path traversal failure;
- evidence-root tamper failure.

## Remaining work after Iteration 1 validates

1. Freeze Iteration 1 evidence and open/update the Pass 215 draft PR.
2. Introduce real open-transformer container parsing (safetensors/GGUF or another explicitly selected format) without changing the frozen Pass 214 profile.
3. Measure real-model admission incidence before making any 50B feasibility claim.
4. Add exact quantized operator reproduction and later exact nonlinear transformer operators.
5. Keep runtime mutation/canonical mutation behind the inherited Pass 213 live-admission boundary.

## Blockers

None known at commit time. If hosted validation exposes a defect, repair only the affected Iteration 1 surface, rerun the dedicated gate, commit the repaired state, and continue from this record.
