# Pass 214 — Operating Compression Gradient Calibration

Pass 214 measures how often real HHS states enter the generator, exact-exception, and raw-fallback tiers established by Pass 212.

## Current state

Iteration one is a contract freeze. It defines measurement records, byte accounting, admission semantics, workload segmentation, transition matrices, correctness gates, and acceptance thresholds. It intentionally contains no workload result claim.

## Sequence constraint

Pass 213 is under development on `agent/pass213-compiled-rom-integrity`. Pass 214 implementation and final merge must rebase onto the authoritative Pass 213 closure state.

## Headline outputs after implementation

- structured snapshot incidence;
- structured byte incidence;
- operating compression-and-protection ratio;
- per-workload tier incidence;
- full tier transition matrix;
- tier-2 exception distributions and break-even points;
- recovery success and fail-closed evidence.

## Validation

```bash
bash scripts/run_pass214_contract_validation.sh
```
