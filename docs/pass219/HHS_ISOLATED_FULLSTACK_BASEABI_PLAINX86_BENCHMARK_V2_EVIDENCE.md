# Pass 219 — Isolated Full Stack vs Base ABI vs Plain x86_64 Benchmark v2 — Evidence

**Date:** 2026-09-17  
**Validated head:** `d8faa5bd3d11bd4e148fbffc85354d5894bca982`  
**Workflow:** `Pass 219 Isolated FullStack BaseABI PlainX86 Benchmark v2`  
**Run:** `35261810960`  
**Job:** `105339127180`  
**Result:** **PASS**

## 1. Why v2 supersedes PR #489 for this comparison

PR #489 remains valid only as an internal HHS cost decomposition. Its B arm still executed Lane 5 route/admission logic and its C arm reused HHS-shaped workload construction, so it did not isolate the three systems requested for the external normalization.

This v2 benchmark does not rewrite those measurements. It introduces a separate isolation contract:

```text
A = full aggregate exact ABI serialization
    + Lane 5 route/admission
    + direct H36/Hash216 M proof

B = immutable exact v1.1 base runtime ABI only
    + VM81 frame import/export
    + exact byte equality
    + no aggregate ABI or Pass 219 feature object

C = ordinary Ubuntu/x86_64 native C/libc
    + byte copy
    + byte equality
    + no HHS header, object, runtime call, receipt, or feature
```

All three binaries use the same ordinary compiler flags as a controlled environmental variable:

```text
-O3 -std=c11 -Wall -Wextra -Werror -pedantic -march=x86-64 -mtune=generic
```

Compiler optimization is therefore common to A, B, and C and is not attributed to HHS.

## 2. Binary-level isolation proof

The workflow proves the separation before timing.

### B — immutable base ABI only

`base-abi-only.o` exports only the v1.1 base ABI family, including:

```text
hhs_exact_abi_descriptor
hhs_exact_abi_validate
hhs_exact_abi_version
hhs_exact_hash72_coord_decode
hhs_exact_hash72_coord_encode
hhs_exact_phase_product
hhs_exact_vm5184_address_decode
hhs_exact_vm5184_address_encode
hhs_exact_vm81_frame_export_le
hhs_exact_vm81_frame_import_le
hhs_x86_64_bytecode_copy_exact
hhs_x86_64_egress_exact
hhs_x86_64_ingress_exact
```

The workflow rejects B if its object contains any `pass219`, `lane5`, `harmonic36`, or `hash216` symbol.

B dynamically linked only:

```text
linux-vdso.so.1
libc.so.6
ld-linux-x86-64.so.2
```

### C — plain x86_64 Ubuntu

C is compiled without any HHS include directory or HHS object/library. A full symbol scan rejects the binary if an `hhs_` or `HHS_` symbol appears.

C dynamically linked only:

```text
linux-vdso.so.1
libc.so.6
ld-linux-x86-64.so.2
```

The binary isolation step passed before the benchmark was admitted.

## 3. Runner identity

The successful run used one GitHub-hosted Ubuntu 24.04 x86_64 runner:

```text
runner_os=Linux
runner_arch=X64
kernel=Linux 6.17.0-1022-azure x86_64 GNU/Linux
nproc=4
gcc=gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
cpu_model=INTEL(R) XEON(R) PLATINUM 8573C
```

All A/B/C samples for this run were executed on that runner.

## 4. One neutral dataset

The dataset is generated once outside all timed regions and then supplied unchanged to three independent executables.

```text
schema       = HHS_PASS219_ISOLATED_STACK_DATASET_V2
record bytes = 648
records      = 16,352
bytes        = 10,596,096
SHA-256      = 10596bc21ec6e4f2bee52b1aa39a446d419b5e30702da8d3c82b928e2dc768a1
```

The 36 sample ranges preserve the frozen calibration grouping:

- difficulty ranks `1..9`;
- target counts `8..2048` by powers of two;
- phase labels `xy`, `yx`, `zw`, `wz`.

For C the phase values are inert grouping metadata only. C has no HHS phase interpretation.

Each binary preloads the dataset before its timed region. For every sample A, B, and C must produce the same neutral payload digest over exactly the same record range. All 36 triplets passed this identity test.

## 5. Exact global result

All three arms completed all `16,352` records.

| arm | semantics | completed | elapsed ns | approximate records/s |
|---|---|---:|---:|---:|
| A | full aggregate ABI + Lane 5 + H36/Hash216 M stack | 16,352 | 3,114,947,155 | 5,249.527 |
| B | immutable v1.1 base ABI only | 16,352 | 17,531,668 | 932,712.164 |
| C | plain Ubuntu/x86_64 libc | 16,352 | 14,099,720 | 1,159,739.342 |

Exact normalized throughput ratios:

| comparison | exact ratio | basis-point floor | descriptive percentage |
|---|---:|---:|---:|
| **A:B** | `17531668/3114947155` | `56` | ~0.5628% |
| **A:C** | `2819944/622989431` | `45` | ~0.4526% |
| **B:C** | `3524930/4382917` | `8042` | ~80.4243% |

Per-phase basis-point floors were:

| phase | A:B | A:C | B:C |
|---|---:|---:|---:|
| `xy` | 57 | 45 | 7964 |
| `yx` | 56 | 45 | 8041 |
| `zw` | 56 | 44 | 8012 |
| `wz` | 55 | 45 | 8153 |

## 6. Interpretation boundary

This benchmark measures **end-to-end service cost for three deliberately different execution layers over the same neutral payload**, not equal semantic feature sets.

- C performs ordinary native byte copy/equality work.
- B adds the exact base runtime ABI VM81 import/export representation boundary.
- A performs the full requested HHS service path, including the base serialization work plus Lane 5 admission/receipt logic and direct H36/Hash216 `M` proof validation.

Therefore the result does **not** mean that an optimized algorithm is intrinsically slower than raw x86_64. It means that, for this calibration workload and implementation, the current full HHS service performs substantially more verified work per record and its present end-to-end throughput is about `0.45%` of the plain native control and about `0.56%` of the base ABI-only control.

The base ABI itself retains about `80.42%` of the plain native control on this runner/sample. This cleanly separates base runtime representation overhead from the much larger current Lane 5/full-proof service cost.

A subsequent optimization cycle must use this v2 baseline to reduce A's total service cost **without moving Lane 5, Hash216, H36/M, exactness, receipt, or authority work into B or C** and without weakening A's invariants.

## 7. Authority and energy boundary

This is a performance calibration only.

- No physical joules, watts, package energy, or wall power were measured.
- The benchmark grants no new canonical mutation, Hash72, Hash216, or persistence authority.
- The neutral raw control is not assigned HHS logical-energy semantics.

## 8. Sealed artifact

Run `35261810960` uploaded:

```text
artifact name:
pass219-isolated-fullstack-baseabi-plainx86-v2

artifact id:
10515135246

artifact ZIP SHA-256:
5368498f4140a72534cae46a89567ba208faee958c42e301f6c240784c02fcc0

artifact size:
10,609,627 bytes
```

The artifact contains the neutral dataset and manifest, dataset SHA-256, native JSONL, exact result JSON, report, runner identity, B symbol evidence, C symbol evidence, and B/C dynamic-link evidence.

## 9. Baseline conclusion

The requested isolation is now executable and measured:

```text
A = full HHS optimization/proof service
B = immutable base runtime ABI only
C = ordinary Ubuntu/x86_64 native control
```

No Lane 5 or Pass 219 optimization code is shared with B, and no HHS feature is present in C. The neutral input dataset is identical across all three arms.