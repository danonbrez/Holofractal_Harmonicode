# Pass 219 — Isolated Full-Stack / Base-ABI / Plain-x86 Benchmark v2 — Start

Date: 2026-09-17

## Base

- repository: `danonbrez/Holofractal_Harmonicode`
- base/main: `e197edc7c8e39e56024771a798112d750531e01c`
- branch: `pass219/isolated-fullstack-baseabi-plainx86-benchmark-v2`
- merge target: `main`

## Why this repair exists

PR #489 measured an internal HHS cost decomposition but did not isolate the requested three systems. Its B arm still used Lane 5 route/admission behavior, and its C arm reused HHS-shaped record construction. Therefore its ratios remain valid only for that internal benchmark and must not be presented as `full HHS vs base runtime ABI vs ordinary Ubuntu/x86_64`.

## v2 required isolation

- **A / full stack**: aggregate exact ABI public serialization path + Lane 5 exact route/admission + direct H36/Hash216 M proof.
- **B / runtime ABI only**: immutable exact v1.1 base ABI implementation only. No aggregate ABI object, serialization bridge, Lane 5, H36, Hash72/216 proof, optimization fabric, or Pass 219 link-support object.
- **C / ordinary x86_64 Ubuntu**: standalone native C program. No HHS headers, objects, libraries, constants, receipts, VM81 structs, phase services, or Lane 5 code.

All three use the same compiler optimization flags so compiler quality is controlled rather than counted as HHS optimization.

## Dataset rule

Generate one neutral binary dataset once. All three executables read the exact same file and exact same record ranges. Dataset generation is outside every timed region. Each executable preloads the file before timing. A shared neutral payload checksum must match for every sample.

## Calibration schedule

Retain the frozen four reciprocal labels and nine difficulty ranks only as benchmark grouping metadata:

- `xy: 0 -> 36`
- `yx: 36 -> 0`
- `zw: 18 -> 54`
- `wz: 54 -> 18`
- ranks 1..9, target record counts 8..2048 by powers of two

The raw C arm receives the phase values only as inert sample metadata; it does not interpret them through HHS logic.

## Validation / closure

1. Generate dataset + manifest and seal SHA-256.
2. Compile A from aggregate ABI + required exact link support.
3. Compile B from the immutable v1.1 base ABI source only.
4. Compile C standalone with libc only.
5. Execute all 36 A:B:C samples with rotated process order.
6. Verify payload checksums and completed counts are identical.
7. Report exact A:B, A:C, and B:C throughput ratios.
8. Commit measured evidence and close restart checkpoint.
9. Open/merge PR if dependency-scoped validation is green; queued unrelated CI does not block closure.
