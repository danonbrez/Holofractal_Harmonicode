# Pass 207 Restart Record

## Scope

Implement an additive C11 GPU driver that maps VM81 into 81 workgroups × 64 stable logical hyperthreads, preserves exact Pass 205 SoA/CSR layouts, reuses vector-store buffers, and rejects every physical GPU result that differs from the CPU VM5184 oracle.

## Intended branch

`agent/pass207-vm81-gpu-hyperthreads`

## Merge target

`main`

## Changed files

- `.github/workflows/pass207-vm81-gpu-hyperthreads.yml`
- `artifacts/pass207/GPU_DRIVER_PLUGIN_MANIFEST.json`
- `contracts/pass207/PASS_207_CONTRACT.json`
- `docs/pass207/IMPLEMENTATION.md`
- `docs/pass207/RESTART_RECORD.md`
- `hhs_backend/runtime/hhs_pass207_vm81_gpu_runtime_v1.py`
- `hhs_python/runtime/hhs_pass207_gpu_driver_native.py`
- `hhs_python/runtime/hhs_pass207_gpu_driver_bridge.py`
- `hhs_runtime/c/hhs_pass207_gpu_driver.c`
- `hhs_runtime/c/hhs_pass207_gpu_driver_part1.inc`
- `hhs_runtime/c/hhs_pass207_gpu_driver_part2.inc`
- `hhs_runtime/c/hhs_pass207_gpu_driver_part3.inc`
- `hhs_runtime/c/hhs_pass207_gpu_driver_part4.inc`
- `hhs_runtime/c/hhs_pass207_gpu_driver_part5.inc`
- `hhs_runtime/c/hhs_pass207_gpu_driver.h`
- `tests/test_hhs_pass207_gpu_driver_v1.c`
- `tests/test_hhs_pass207_gpu_driver_v1.py`

## Completed validation

- strict C11 shared-library build with `-O3 -Wall -Wextra -Werror -pedantic`;
- strict native test build and execution;
- AddressSanitizer and UndefinedBehaviorSanitizer execution;
- exhaustive 5,184 lane encode/decode and 72×72 phase-coordinate bijection;
- bit-0, middle-bit, and bit-63 mutations through the 64-lane cell packing path;
- exact frontier and sparse projection checks;
- ordered q-address hydration mismatch rejection;
- host/device-style cache store and cache-hit reuse;
- Hash72 vector distance and stable tie ordering;
- Python bridge compilation and temporary-tree integration tests;
- Pass 205 accelerator-batch equality through a local compatibility stub.

## Remaining validation

- repository workflow on the exact pushed branch;
- inherited Pass 205 production regression on repository CI;
- physical OpenCL GPU execution on a host with at least one 64-work-item-capable GPU;
- physical GPU performance and transfer/cache benchmarks;
- post-merge verification on authoritative `main`.

## Claim boundary

No physical GPU execution is claimed by this restart record. The driver fails closed when physical GPU execution is explicitly required and unavailable. CPU fallback remains an exact verification backend, not a substitute claim of GPU execution.

## Next action

Run the Pass 207 workflow, repair any repository-integration failure without altering inherited core functions, then validate the exact branch on a physical OpenCL GPU before marking physical acceleration complete.
