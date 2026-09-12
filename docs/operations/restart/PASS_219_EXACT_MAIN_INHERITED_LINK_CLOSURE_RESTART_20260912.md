# Pass 219 Exact-Main Inherited Link Closure — Restart Checkpoint

Date: 2026-09-12 17:05 America/New_York

## Base / branch / merge target / PR

```text
base main: 506034954c3056f288e654b0c6c62cde54cbb3d3
branch: agent/pass219-exact-main-inherited-link-closure-20260912
merge target: main
PR: #439 — Pass 219: repair exact-main inherited PQC link closure
pre-checkpoint branch head: ac5958648db0503d9668a64c5dffc6b0ff78f787
```

The repair branch was created directly from the exact PR #436 merge because the regression is an inherited build/link failure exposed by the canonical environmental-PQC authority. This work does not intentionally change Pass 219 runtime authority, VM81 transition semantics, Hash72/Hash216 semantics, PQC policy, or canonical mutation surfaces.

PR #439 is open, non-draft, and mergeable. It remains intentionally unmerged until I163 closes.

## Failure classes repaired

Exact main exposed two inherited dependency classes:

1. standalone `hhs_runtime_exact_abi.c` links omitted newly required Hash72/Hash216 support, OpenSSL `libcrypto`, the C++ runtime, and the Pass 219 VM81 PQC/RNA cell-wall object;
2. Pass159-composed I163 already supplied Hash216 and `libcrypto` but omitted `hhs_pass219_vm81_pqc_route_cpp_cell_wall` and the C++ runtime.

The shared link rule is now:

```text
program / exact ABI / inherited objects
  -> hhs_hash216.o when not already supplied by the inherited runtime
  -> hhs_pass219_vm81_pqc_cell_wall.o
  -> -lcrypto -lstdc++ -pthread -lm
```

Objects precede the libraries that satisfy them.

## Shared build surfaces

Added:

```text
tools/pass219/build_exact_abi_link_support.sh
tools/pass219/build_aarch64_openssl35.sh
```

`build_exact_abi_link_support.sh` is compiler-parameterized through `CC` / `CXX`, emits PIC support objects, and provides `full` and `cell-wall-only` modes. Full mode compiles `hhs_runtime/src/hhs_hash216.c` plus `hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp`. Cell-wall-only mode is used where Pass159 already supplies the hash implementation, preventing duplicate hash symbols.

`build_aarch64_openssl35.sh` cross-builds static OpenSSL 3.5 for `linux-aarch64`. I163 and I166 use it with `aarch64-linux-gnu-gcc` / `aarch64-linux-gnu-g++`, preserving the same PQC dependency boundary in ARM64 parity probes instead of compiling the security surface out.

## Affected workflows repaired

```text
.github/workflows/pass219-i149-global-raw5184-serialization-hydration.yml
.github/workflows/pass219-i163-pass169-terminal-reverse-crossarch.yml
.github/workflows/pass219-i166-pass168-terminal-parent-closure.yml
.github/workflows/pass219-i179-pass170-native-audio-replay.yml
.github/workflows/pass219-global-canonical-defaults.yml
.github/workflows/pass219-cross-modal-reversible-state-manifold.yml
```

Each repaired workflow tracks the shared support scripts in its path filter. The repair branch is temporarily present in push triggers so the exact gates can validate before merge.

## Repair commits

```text
d0149c5326a4f0432773253f4f60c8645186a367  add shared exact ABI link support builder
cd1d3015f3f7aea003ae20ba871f8c7cceb39cf2  repair I149 inherited exact ABI link closure
1db58dd4b4aacd68825df3cb80dd2a132d8b1aa5  repair cross-modal exact ABI link closure
1283da536d022d1f5439a3e1c9b5330bdde855cd  repair global defaults exact ABI link closure
ad2b283dd36c2efe2a823b46f307464f04faa7fd  repair I179 inherited exact ABI link closure
6c4fc94ac835df014adb6dfa0a44a27112415e88  add shared ARM64 OpenSSL exact ABI dependency builder
4aa08df445a0c7ffe7f1a0cb7d1f86cc09ba953c  repair I166 cross-architecture exact ABI link closure
55a72b578760868db2b1e4fbdb76cd8dd3d2b9d6  repair I163 cross-architecture exact ABI link closure
ac5958648db0503d9668a64c5dffc6b0ff78f787  repair I163 Python binding through full runtime ABI
```

The I163 Python-binding repair replaced the hand-built exact-only `.so` with the authoritative full runtime build:

```text
make -C hhs_runtime c-abi
nm -D hhs_runtime/builds/libhhs_runtime.so | grep -F ' hhs_runtime_init'
HHS_DISABLE_C_AUTOBUILD=1 python tools/pass219/pass219_i163_python_exact_probe.py ...
```

The full shared runtime now compiles and links successfully with the C++ cell-wall object and `-lcrypto -lstdc++`, and `hhs_runtime_init` is exported.

## Dependency-scoped validation frozen green

```text
I149 exact-i149-global-raw5184
  run 34705840170
  job 103585599951
  head cd1d3015f3f7aea003ae20ba871f8c7cceb39cf2
  result SUCCESS

Cross-modal exact-cross-modal-manifold
  run 34705860234
  job 103585652416
  head 1db58dd4b4aacd68825df3cb80dd2a132d8b1aa5
  result SUCCESS

Global defaults
  run 34705878142
  job 103585702247
  head 1283da536d022d1f5439a3e1c9b5330bdde855cd
  result SUCCESS

I179 validate-i179
  run 34705900224
  job 103585764213
  head ad2b283dd36c2efe2a823b46f307464f04faa7fd
  result SUCCESS

I166 validate-i166-native
  run 34705959822
  head 4aa08df445a0c7ffe7f1a0cb7d1f86cc09ba953c
  result SUCCESS
  x86-64 exact probe: PASS
  ARM64 OpenSSL/link-support build: PASS
  ARM64 exact probe/parity: PASS
  sanitizer/shared-library/export checks: PASS
  benchmark/contract closure: PASS
```

These five gates are frozen evidence. Do not rerun them unless a later repair changes an input surface they depend on.

## I163 current state — sole remaining blocker

Latest refreshed run after the Python full-runtime repair:

```text
I163 validate-i163
  run 34706363003
  job 103587014706
  head ac5958648db0503d9668a64c5dffc6b0ff78f787
  result FAILURE
```

The following I163 stages are green and should be treated as frozen unless their inputs change:

```text
Pass159 build and inherited reverse-transition semantics: PASS
cumulative exact ABI + host link support: PASS
native reverse conformance: PASS
x86-64 exact identity probe: PASS
AArch64 OpenSSL 3.5 + exact link support: PASS
ARM64 exact identity probe: PASS
full hhs_runtime c-abi compilation/link: PASS
hhs_runtime_init shared-library export check: PASS
```

The only current failure occurs when the Python ctypes exact probe calls the successfully built full runtime:

```text
RuntimeError: exact ABI failed: status=52 decision=52
```

This is no longer a missing-object, unresolved-symbol, or missing-`libcrypto` failure. Native x86-64 and ARM64 exact probes admit successfully, while the Python/full-runtime binding path returns exact status/decision `52`.

Do **not** reinterpret or weaken the environmental-PQC boundary to force this test green. The meaning of status `52` must be established from repository definitions before repair.

## Main drift at checkpoint

Immediately before writing this checkpoint, comparison against `main` was:

```text
status: ahead
base / merge-base: 506034954c3056f288e654b0c6c62cde54cbb3d3
ahead_by: 10
behind_by: 0
```

There was no main drift at freeze time.

## Validation environment

```text
GitHub Actions: ubuntu-24.04
Python: 3.11
host compilers: gcc / g++
cross compilers: aarch64-linux-gnu-gcc / aarch64-linux-gnu-g++
ARM execution: qemu-user
ARM PQC dependency: OpenSSL 3.5 static linux-aarch64 cross-build
```

## Remaining work

1. Inspect `tools/pass219/pass219_i163_python_exact_probe.py` and the full-runtime initialization/configuration path used by the Python ctypes binding.
2. Locate the repository definition and all relevant producers/consumers of exact ABI status code `52`; do not assign semantics by guess.
3. Compare the Python/full-runtime exact-call setup with `tools/pass219/pass219_i163_crossarch_exact_probe.c`, including initialization, environment/provider state, canonical input construction, PQC boundary state, and any required predecessor/hash context.
4. Repair only the evidence-supported Python binding/setup/shared-runtime integration surface. Preserve environmental-PQC authority and existing VM81/Hash72/Hash216 semantics.
5. Rerun I163 only. The other five requested gates remain frozen unless this repair changes one of their shared inputs.
6. When I163 is green, compare the branch with current `main`. If main advanced, reconcile and rerun only impacted validation.
7. Merge PR #439.
8. Verify the repaired exact-main matrix after merge: I149, I163, I166, I179, global defaults, and cross-modal.

## Restart command intent

Resume from:

```text
branch: agent/pass219-exact-main-inherited-link-closure-20260912
PR: #439
```

First action: resolve the I163 Python/full-runtime `status=52 decision=52` mismatch from repository-defined semantics. Do not revisit already-green link closure work unless the I163 repair changes its shared build inputs.
