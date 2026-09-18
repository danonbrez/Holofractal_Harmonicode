# Pass 219 Lane 5 Raw Linux Serial-ABI Cache Calibration — Checkpoint — 2026-09-18

## Restart identity
- Base / merge target: `main @ 63cee69390db05bd4b77da1cfd6f1b8cca4d461f`
- Branch: `pass219/saturation-deadline-warm-cache-benchmark-v3`
- PR: #492
- Code head before this checkpoint: `40e125f344dfb545dad778069a48eb4e0eabbea5`

## Corrected capacity authority

The Lane 5 interceptor cache is **not** hardware-calibrated in VM81 records.

Authoritative hardware capacity unit:

```text
RAW_LINUX_SERIAL_ABI_BYTES
```

The capacity benchmark is a standalone Linux/x86_64 C program:
- no HHS headers;
- no `libhhs_runtime` linkage;
- no VM81 service;
- no Lane 5 service;
- no RNA service;
- no Hash72/Hash216 service;
- no PQC service.

It writes and verifies every byte in the probed span linearly.

## Raw benchmark
- source: `benchmarks/pass219/raw_linux_serial_abi_capacity_v1.c`
- output: `max_serial_abi_bytes`
- caller supplies the raw byte probe ceiling;
- child processes isolate failed allocation/touch probes;
- the successful span is verified byte-for-byte;
- `first_failed_bytes`, `failed_boundary_observed`, and `probe_ceiling_reached` are reported.

A result is `MEASURED_MAXIMUM` only if:
1. a failed raw-byte boundary is observed above the largest successful span; or
2. the successful ceiling is independently matched to a Linux/cgroup hard environment byte limit.

Otherwise it is `MEASURED_LOWER_BOUND` and cannot satisfy production calibration.

## Sealed environment identity

The calibration receipt records:
- raw byte maximum/lower bound;
- probe ceiling/page size/attempt count;
- kernel;
- libc;
- compiler;
- CPU model;
- logical CPU count;
- service-contamination flags.

A production-accepted receipt is checked against the local hardware profile when loaded. A GitHub runner receipt cannot silently calibrate the DigitalOcean server.

## Lane 5 derived framing

Only after raw calibration is sealed does Lane 5 derive:

```text
derived_5184_frame_slots = floor(max_serial_abi_bytes / 648)
derived_frame_remainder_bytes = max_serial_abi_bytes mod 648
```

These are cache-framing values, not benchmark capacity units.

The existing 42,467,328-byte plain-x86 saturation-v3 workset is retained only as:
`VERIFIED_RAW_LINUX_SERIAL_BYTE_FLOOR`.

It is not production calibration.

## Queue/cache behavior

All intercepted bypass/direct/compatibility traffic:
1. enters the Lane 5 sandbox queue;
2. is ordered only across independent dependency chains;
3. preserves FIFO within one state-affecting dependency chain;
4. prioritizes exact cache/replay/composition reuse where compatible;
5. remains candidate-only;
6. returns to Lane 5/RNA/PQC mediation before downstream execution;
7. has no direct fallback.

Cache eviction uses the raw byte ceiling. The cache is lazy and never preallocates the full measured maximum.

## Validation

Focused workflow:
`Pass 219 Universal ABI Linux Kernel Lane 5 Intercept`

Exact-head run at checkpoint:
`35340537505`

State when checkpointed: queued.

The CI probe intentionally uses an arbitrary 64 MiB ceiling and therefore must seal as `MEASURED_LOWER_BOUND`, not `MEASURED_MAXIMUM`.

Production acceptance still requires a raw calibration run on the actual DigitalOcean environment using a real failed boundary or verified local Linux/cgroup hard ceiling.

## Next action

1. Resolve the first concrete focused CI failure if one appears.
2. Add the raw calibration probe to the DigitalOcean deployment preflight before HHS runtime startup.
3. Seal the droplet-local `MEASURED_MAXIMUM` receipt.
4. Install that receipt as `HHS_PASS219_LANE5_INTERCEPT_CACHE_CALIBRATION`.
5. Continue central VMRC/retrieval and Linux-host call-site migration through the universal Lane 5 queue.
