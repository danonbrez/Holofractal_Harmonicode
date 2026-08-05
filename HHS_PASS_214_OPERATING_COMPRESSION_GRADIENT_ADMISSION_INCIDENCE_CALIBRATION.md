# HHS Pass 214 — Operating Compression Gradient Admission Incidence Calibration

**Contract:** `HHS-P214-OPERATING-COMPRESSION-GRADIENT-ADMISSION-INCIDENCE-CALIBRATION-H72-H216`  
**Contract classification:** `HHS_PASS_214_OPERATING_COMPRESSION_GRADIENT_CONTRACT_FROZEN`

## Sequence authority

Pass 213 is already reserved for compiled-ROM integrity work on `agent/pass213-compiled-rom-integrity`. Pass 214 is therefore the next cumulative pass for measuring how the Pass 212 compression gradient behaves under real HHS workloads.

This contract may be reviewed while Pass 213 is in development, but Pass 214 implementation and final integration must inherit the authoritative Pass 213 closure commit. It must not merge ahead of an unfinished Pass 213 implementation.

## Purpose

Pass 212 proved three exact storage paths over the complete 50,388,480-bit hydration:

1. generator-domain compression;
2. generator plus exact reversible exceptions;
3. raw protected fallback.

Pass 214 measures the operating distribution across those paths. Its objective is to determine whether real VM81 continuation, vector-cache, graphics-control, and ML hydration workloads remain predominantly in tiers 1 and 2, while keeping arbitrary or high-entropy payloads honestly in tier 3.

The Pass 212 values `2546.930853:1` and `590.582278:1` remain reference vectors until measured workload evidence establishes an operating characteristic.

## Canonical operating ratio

The primary aggregate result is:

```text
R_operating = total canonical state bytes
              --------------------------------
              total protected physical bytes
```

The denominator includes every byte required to retain, locate, verify, replay, and recover the state:

- generator seeds and witnesses;
- exact exception positions and values;
- raw fallback bytes;
- GF(256) parity;
- package manifests and framing;
- Hash72 receipts and Hash216 identities;
- retrieval and reconstruction indexes;
- required alignment and padding.

No payload-only ratio may be reported as the full operating ratio.

## Required incidence views

Pass 214 records four complementary incidence measures:

- **snapshot incidence:** state count assigned to each tier;
- **byte-weighted incidence:** canonical bytes represented by each tier;
- **transition incidence:** continuation transitions entering each tier;
- **dwell-time incidence:** runtime duration represented by each tier.

The two headline structure measures are:

```text
I_1,2 = (tier-1 states + tier-2 states) / all states
B_1,2 = canonical bytes represented by tiers 1-2 / all canonical bytes
```

These are reported separately from `R_operating` because a small number of tier-3 states may dominate physical storage even when most state snapshots are structured.

## Tier 2 calibration

Tier 2 is expected to carry ordinary continuation-state mutations. Every workload report therefore includes:

- exception count and exact density over 50,388,480 bits;
- encoded position and value costs;
- minimum, median, p75, p90, p95, p99, maximum, and mean;
- exact break-even point where tier 2 becomes no smaller than tier 3;
- clustering by VM81 cell, control, basis lane, and magnitude row;
- temporal reuse of exception regions;
- distance from the immediate predecessor;
- distance from the nearest retained prior hydration.

Tier 2 is selected only when its complete protected representation is strictly smaller than tier 3.

## Tier transition matrix

The continuation engine accumulates the full 3×3 transition matrix:

```text
M[a,b] = count(tier_n=a and tier_n+1=b) / count(tier_n=a)
```

Required cells are `1→1`, `1→2`, `1→3`, `2→1`, `2→2`, `2→3`, `3→1`, `3→2`, and `3→3`.

This matrix distinguishes deterministic lattice evolution, sparse mutation, convergence back to a pure generator state, entropy ingress, and successful hydration of arbitrary input into structured internal state.

## Workload segmentation

Results remain segmented for:

- VM81 continuation snapshots;
- nearest-state vector-cache continuations;
- graphics scene graphs and control state;
- graphics pixel or codec payloads;
- ML hydration state;
- ML sparse update state;
- receipts and cryptographic identity payloads;
- uploaded arbitrary files.

High-entropy media bytes must not obscure the behavior of their structured scene, timing, object, and control state.

## Admission and correctness gates

Every measurement record must prove:

1. deterministic tier selection under the same policy and predecessor set;
2. exact full-state reconstruction;
3. identical canonical Hash216 before encode and after decode;
4. no tier-1 admission without a valid generator witness;
5. no tier-2 admission without exact reversible exceptions;
6. automatic tier-3 fallback when semantic admission or complete-size advantage fails;
7. exact one- and two-shard recovery within the Pass 212 stripe budget;
8. fail-closed behavior beyond the declared recovery budget;
9. independently retained historical anchors for corruption-history claims;
10. no floating-point canonical authority.

## Iteration one

Iteration one freezes:

- the measurement-record JSON Schema;
- tier-admission evaluator semantics;
- exact byte-accounting rules;
- workload segmentation;
- transition-matrix accumulation;
- percentile and break-even definitions;
- replay and negative-test gates;
- the restartable implementation boundary.

Iteration one does **not** claim workload incidence, an operating compression ratio, or production telemetry deployment.

## Acceptance threshold for measured implementation

Each required workload class must eventually provide at least 1,000 observations and 999 continuation transitions. Decode, replay, and declared recovery success must be exact. False compression claims are not permitted.

## Authority surfaces

- Contract: `contracts/pass214/PASS_214_CONTRACT.json`
- Measurement schema: `contracts/pass214/PASS_214_MEASUREMENT_RECORD.schema.json`
- Iteration-one evidence: `evidence/pass214/PASS_214_ITERATION_1_MEASUREMENT_PLAN.json`
- Documentation: `docs/pass214/README.md`
- Restart record: `docs/pass214/RESTART_RECORD.md`
- Contract validation: `scripts/run_pass214_contract_validation.sh`
