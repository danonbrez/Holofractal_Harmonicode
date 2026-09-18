# Pass 220 I003.1 — Cold x86_64 Raw-Byte Max-Hardware Calibration and Post-Calibration Query Integration

Status: IMPLEMENTED REPAIR CHECKPOINT / COLD-CALIBRATION CI PENDING / CANDIDATE-ONLY QUERY INTEGRATION

## 1. Corrected purpose

The max-hardware calibration is not an HHS workload.

It is a cold-runner Linux/x86_64 raw-byte calibration executed before package installation, project compilation, Python, HHS services, HARMONICODE services, kernel/runtime ABI logic, Lane 5, VM81, Hash72, or Hash216 code.

The I002/I003 query stack is tested only after that calibration and is classified as post-calibration integration.

This separation ensures that the hardware-capacity witness is not circularly measured through the runtime whose search cost is being optimized.

## 2. Cold-runner execution order

The dedicated workflow now begins:

1. checkout repository;
2. immediately execute the raw Bash/coreutils calibration;
3. seal raw runner identity, per-sample timing, and max closed bytes;
4. only then install development packages;
5. only then build HHS/runtime dependencies;
6. only then run I001-I003 integration tests.

No project executable is invoked before step 4.

## 3. Raw workload

The calibrated data is an exact byte stream:

ZERO_BYTES(N) = N occurrences of byte 0x00.

It is sourced directly from Linux `/dev/zero`.

There is no static maximum N.

The initial N is doubled:

N_(k+1) = 2*N_k

until the cold runner hits an actual time/resource membrane.

The default start size is 1 MiB only to avoid calibrating command-startup noise. It is not a maximum or scale ceiling.

## 4. Raw A:B:C arms

All three arms are ordinary Linux commands over exactly N zero bytes.

### A — direct raw byte drain

`head -c N /dev/zero >/dev/null`

### B — raw pipe/copy path

`head -c N /dev/zero | dd of=/dev/null bs=1M status=none`

### C — raw read + SHA-256 path

`head -c N /dev/zero | sha256sum >/dev/null`

No arm imports, calls, links, shells into, or validates through any HHS/HARMONICODE/runtime ABI surface.

The three paths intentionally exercise different ordinary host byte-processing costs. Their role is runner calibration, not semantic feature equivalence.

## 5. Four calibration cohorts

The labels:

xy
yx
zw
wz

are retained solely as four repeated calibration cohorts so the existing four-phase A:B:C experimental shape remains comparable.

Inside the raw hardware calibration they have no HHS phase meaning and do not invoke phase algebra.

Every cohort starts again from the initial byte size and expands independently on the same cold job.

## 6. Arm-order normalization

The order rotates:

ABC
BCA
CAB

across successive byte sizes.

This reduces systematic first/last cache, scheduling, and command-order placement.

## 7. Unbounded-to-runner rule

The workload has:

WORKLOAD_SIZE_STATIC_CEILING = 0.

Scaling continues until one of these runtime-derived stop conditions occurs:

1. an A/B/C raw arm exceeds the common leg time membrane;
2. the global benchmark time membrane is reached;
3. shell integer range would overflow;
4. an ordinary Linux command fails.

There is no configured maximum byte count or candidate count in the hardware calibration.

The observed per-cohort value is:

max_closed_bytes(phase)

and the conservative cold-runner calibration is:

global_max_closed_bytes = min_phase max_closed_bytes(phase).

This value is observational and runner-specific.

## 8. Time membrane

The current workflow uses:

- raw per-arm membrane: 120,000,000 ns;
- raw global membrane: 30,000,000,000 ns;
- repeats per arm/size: 3.

These are time constraints, not workload-size constraints.

Each command is guarded by GNU `timeout`; runaway growth therefore remains bounded by time even though byte size itself has no static ceiling.

## 9. Raw evidence format

The calibration uses shell/coreutils only and emits:

- `records.tsv` — phase/cohort, N, order, arm, integer elapsed nanoseconds, repeats, completion, command class, zero-byte dataset description, SHA-256 witness when available;
- `summary.env` — sourceable integer/raw calibration summary;
- `report.md` — human-readable result;
- `runner.txt` — cold runner identity.

The summary explicitly records:

HHS_SERVICES_USED=0
HHS_RUNTIME_ABI_USED=0
PROJECT_COMPILED_CODE_USED=0
PYTHON_USED=0
WORKLOAD_SIZE_STATIC_CEILING=0
TIMING_OBSERVATIONAL_ONLY=1.

## 10. Relation to the I002/I003 query optimizer

The raw calibration does not rank Hash216 candidates and does not execute the holographic query manifold.

After calibration, the workflow may build and test:

- I001 normalized 5184 state;
- I002 holographic metadata ranking;
- I003 Lane 5 composition bridge.

Those steps are post-calibration integration only.

They cannot modify the already-recorded cold-runner raw-byte capacity evidence.

The workflow additionally records simple dimensional references after calibration, such as:

global_max_closed_bytes / 5184

and

global_max_closed_bytes / 216.

Those are descriptive byte-equivalent counts only. They are not claims that raw bytes executed HARMONICODE or Hash216 semantics.

## 11. I003 query bridge

The existing bridge remains:

`hhs_backend/runtime/hhs_pass220_holographic_hash216_lane5_bridge_v1.py`.

It composes I002 ranking with the inherited Pass 219 Lane 5 search path while preserving:

- candidate-only execution;
- identical query/candidate Hash216 identities;
- no VM81 mutation authority;
- no Hash72 commit authority;
- no Hash216 commit authority;
- exact CPU/VM81 replay requirement.

The bridge is no longer part of the hardware-calibration timing envelope.

## 12. Superseded I003 benchmark interpretation

The earlier Python file:

`benchmarks/pass220/hhs_pass220_i003_four_phase_abc_max_hardware_v1.py`

is retained as a post-calibration query-comparison harness and test dependency.

It must not be cited as the cold max-hardware calibration.

The authoritative I003.1 hardware calibration surface is:

`benchmarks/pass220/hhs_pass220_i003_cold_x86_64_raw_bytes_abc_v1.sh`.

## 13. Authority boundary

Neither the raw calibration nor its timing results have canonical authority.

The query integration continues to require:

candidate_only = true
canonical_vm81_mutation_authority = false
canonical_hash72_authority = false
canonical_hash216_authority = false.

Timing and raw byte capacity are observational environment witnesses only.

## 14. Evidence state

The corrected raw Bash benchmark and corrected workflow ordering are repository-visible.

No cold-runner byte-capacity number is claimed until the dedicated workflow executes and the raw evidence artifact is available.
