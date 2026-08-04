# Pass 207 VM81 GPU Hyperthread Driver

## Implemented path

Pass 207 adds a C11 GPU-driver plugin without changing the frozen Pass 205 or Pass 206 core surfaces.

```text
Pass 205 exact state/projection/delta translation
→ content-keyed host/device buffer lookup
→ 81 OpenCL workgroups per batch
→ 64 stable logical hyperthreads per VM81 cell
→ 5,184 disjoint bit-lane writes per batch
→ fixed-order 64-lane cell packing
→ sparse 32-channel projection
→ q-address hydration validation
→ exact CPU VM5184 comparison
→ verified candidate only
→ singleton VM81 admission remains the sole commit authority
```

## Hyperthread topology

Every logical lane has permanent identity:

```text
lane = 64 * cell + hyperthread
0 <= cell < 81
0 <= hyperthread < 64
0 <= lane < 5184
```

The same lane maps bijectively into the 72×72 phase square:

```text
phase_row = floor(lane / 72)
phase_column = lane mod 72
```

A physical OpenCL dispatch uses exactly 64 work-items per workgroup. One workgroup corresponds to one VM81 cell, and one batch contains 81 workgroups. Each work-item writes one private bit slot, so no two logical hyperthreads write the same address. A second kernel packs hyperthreads `0..63` into the cell word in a fixed order.

## Deterministic safety boundary

The GPU is not an alternate runtime authority. It cannot write Hash72, persist a continuation, bypass hydration validation, or bypass VM81 admission.

A physical GPU result is rejected unless it exactly matches the C CPU reference for:

- all 81 child state words;
- all 32×81 projection words;
- the complete dependency frontier;
- every ordered hydration q-address.

GPU scheduling, subgroup timing, command completion order, and device vendor do not determine canonical output.

## Vector-store buffer cache

The driver retains immutable buffers under 256-bit content keys. The runtime bridge derives keys from exact fixed-width bytes and layout-domain separators. Cacheable buffers include parent state/projection SoA, child state/projection SoA, and Hash72 candidate matrices.

Hash72 vector matrices can remain resident on the device across searches. Distances are computed in parallel, while the host applies the canonical stable ordering:

```text
distance
candidate_hash72
candidate_id
source_ordinal
```

A cache hit is reusable computation only. It never authorizes mutation.

## Files

- `hhs_runtime/c/hhs_pass207_gpu_driver.h`
- `hhs_runtime/c/hhs_pass207_gpu_driver.c`
- `hhs_runtime/c/hhs_pass207_gpu_driver_part1.inc`
- `hhs_runtime/c/hhs_pass207_gpu_driver_part2.inc`
- `hhs_runtime/c/hhs_pass207_gpu_driver_part3.inc`
- `hhs_runtime/c/hhs_pass207_gpu_driver_part4.inc`
- `hhs_runtime/c/hhs_pass207_gpu_driver_part5.inc`
- `hhs_python/runtime/hhs_pass207_gpu_driver_native.py`
- `hhs_python/runtime/hhs_pass207_gpu_driver_bridge.py`
- `hhs_backend/runtime/hhs_pass207_vm81_gpu_runtime_v1.py`
- `tests/test_hhs_pass207_gpu_driver_v1.c`
- `tests/test_hhs_pass207_gpu_driver_v1.py`

## Local validation

```bash
cc -std=c11 -O3 -Wall -Wextra -Werror -pedantic \
  tests/test_hhs_pass207_gpu_driver_v1.c \
  hhs_runtime/c/hhs_pass207_gpu_driver.c \
  -Ihhs_runtime/c -ldl \
  -o /tmp/test_hhs_pass207_gpu_driver
/tmp/test_hhs_pass207_gpu_driver

cc -std=c11 -O1 -g -Wall -Wextra -Werror -pedantic \
  -fsanitize=address,undefined -fno-omit-frame-pointer \
  tests/test_hhs_pass207_gpu_driver_v1.c \
  hhs_runtime/c/hhs_pass207_gpu_driver.c \
  -Ihhs_runtime/c -ldl \
  -o /tmp/test_hhs_pass207_gpu_driver_san
ASAN_OPTIONS=detect_leaks=1 /tmp/test_hhs_pass207_gpu_driver_san

python -m pytest -q tests/test_hhs_pass207_gpu_driver_v1.py
```

## Claim boundary

The native driver, exact CPU backend, 5,184-lane topology, deterministic packing, cache, bridge, and Pass 205 integration are implemented and locally validated. Physical OpenCL execution is not claimed in the implementation environment because no physical GPU is attached. On a GPU host, `require_physical_gpu=True` makes absence or incompatibility fail closed rather than silently falling back.
