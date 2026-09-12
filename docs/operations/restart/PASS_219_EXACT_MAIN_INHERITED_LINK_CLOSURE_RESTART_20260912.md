# Pass 219 Exact-Main Inherited Link Closure — Restart Checkpoint

Date: 2026-09-12

## Base / branch / merge target

```text
base main: 506034954c3056f288e654b0c6c62cde54cbb3d3
branch: agent/pass219-exact-main-inherited-link-closure-20260912
merge target: main
```

The repair was branched directly from the exact PR #436 merge because the regression is an inherited-build failure exposed by the new canonical environmental-PQC authority. No Pass 219 runtime semantics or authority code is changed by this repair.

## Failure classes repaired

Exact main exposed two dependency classes in historical direct-link workflows:

1. standalone `hhs_runtime_exact_abi.c` links omitted the now-required Hash72/Hash216 implementation, OpenSSL `libcrypto`, C++ runtime, and C++ RNA/PQC cell-wall object;
2. Pass159-composed I163 already supplied Hash216 and `libcrypto` but omitted `hhs_pass219_vm81_pqc_route_cpp_cell_wall` and the C++ runtime.

The shared rule is now:

```text
program / exact ABI / inherited objects
  -> hhs_hash216.o when not already supplied by the inherited runtime
  -> hhs_pass219_vm81_pqc_cell_wall.o
  -> -lcrypto -lstdc++ -pthread -lm
```

Objects always precede the libraries that satisfy them.

## Shared build surfaces

Added:

```text
tools/pass219/build_exact_abi_link_support.sh
tools/pass219/build_aarch64_openssl35.sh
```

`build_exact_abi_link_support.sh` is compiler-parameterized through `CC`/`CXX`, emits PIC support objects, and has `full` and `cell-wall-only` modes. Full mode compiles `hhs_runtime/src/hhs_hash216.c` plus the Pass 219 C++ cell-wall object. Cell-wall-only mode is used where Pass159 already supplies the hash implementation.

`build_aarch64_openssl35.sh` cross-builds static OpenSSL 3.5 for `linux-aarch64`. I163 and I166 use it with `aarch64-linux-gnu-gcc` / `aarch64-linux-gnu-g++`, so ARM64 parity does not bypass or compile out the new PQC dependencies.

## Affected workflows repaired

```text
.github/workflows/pass219-i149-global-raw5184-serialization-hydration.yml
.github/workflows/pass219-i163-pass169-terminal-reverse-crossarch.yml
.github/workflows/pass219-i166-pass168-terminal-parent-closure.yml
.github/workflows/pass219-i179-pass170-native-audio-replay.yml
.github/workflows/pass219-global-canonical-defaults.yml
.github/workflows/pass219-cross-modal-reversible-state-manifold.yml
```

Each repaired workflow tracks the shared support scripts in its path filter. The repair branch is temporarily included in push triggers so the exact gate can validate before merge.

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
```

## Dependency-scoped validation

Green:

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
```

In progress at checkpoint creation:

```text
I166 validate-i166-native
  run 34705959822
  job 103585926680
  head 4aa08df445a0c7ffe7f1a0cb7d1f86cc09ba953c
  completed green through x86-64 exact probe;
  ARM64 OpenSSL/link-support build in progress.

I163 validate-i163
  run 34705986628
  job 103586001430
  head 55a72b578760868db2b1e4fbdb76cd8dd3d2b9d6
  completed green through Pass159 native reverse and x86-64 exact identity;
  ARM64 OpenSSL/link-support build in progress.
```

## Main drift at implementation checkpoint

Immediately before this restart record, comparison against `main` was:

```text
status: ahead
base / merge-base: 506034954c3056f288e654b0c6c62cde54cbb3d3
ahead_by: 8
behind_by: 0
```

## Remaining validation

1. Read I166 run `34705959822` and I163 run `34705986628` to completion.
2. If either fails, repair only the failing cross-build/link stage and rerun that gate.
3. Open/update the repair PR and preserve the exact-main base unless main advances.
4. If main advances, reconcile current main before merge and rerun only impacted gates.
5. Merge after the six requested dependency-scoped gates are green, then verify the same matrix on the new exact main.

## Next action

Resume from this branch. First inspect I166 and I163. Do not revisit the four already-green gates unless a later repair changes the shared host support builder or their workflow surfaces.
