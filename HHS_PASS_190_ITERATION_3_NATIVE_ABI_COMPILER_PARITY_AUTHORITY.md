# HHS PASS 190 ITERATION 3 — NATIVE C ABI, COMPILER LOWERING, AND CROSS-SURFACE PARITY AUTHORITY

## 1. Metadata

| Field | Value |
|---|---|
| Contract | `HHS-P190-OVRA-HOSS-PCA-FHF-VM81-H72-H216` |
| Iteration | `3` |
| Implementation | `HHS-P190-I3-C11ABI-CST-AST-HIR-VMIR-1.0.0` |
| Baseline | `main @ 570878c2b84ed39da641492eb258aeaf6753af27` |
| Classification | `HHS_PASS_190_ITERATION_3_NATIVE_ABI_COMPILER_PARITY_FOUNDATION_VERIFIED` |
| Full Pass 190 completion | Not claimed |
| Full native type parity | Not claimed |

## 2. Purpose

Iteration 3 extends the same canonical operation registry and singleton authority established by iterations 1 and 2. It does not create a second operation engine.

The implemented path is:

```text
exact HARMONICODE constructor source
→ preserved CST
→ typed operation AST
→ canonical registry HIR
→ VM81/native-binding VMIR
→ singleton HHS authority execution
→ Hash72 receipt chain
```

A generated C11 ABI supplies native projections for every operation currently registered in the Pass 190 nucleus. Native execution is a typed projection and does not independently commit authoritative receipts.

## 3. Registry-generated native ABI

`tools/generate_native_abi.py` reads `HHS_OPERATION_REGISTRY_V1.json` and verifies:

- exact operation ordering;
- complete ten-operation coverage;
- canonical VM81 binding identity;
- one unique C ABI symbol per operation;
- one deterministic native profile and operation slot.

It generates and checks:

```text
native/generated/HHS_NATIVE_ABI_MANIFEST_V1.json
native/generated/hhs_pass190_operation_table.inc
```

A stale or reordered generated artifact fails validation.

## 4. C11 ABI

The public header `native/include/hhs_pass190_abi.h` defines:

- ABI version `1.0.0`;
- typed result codes;
- an explicit native context;
- status and Pass 189 address structures;
- JSON-value lookup records;
- operation descriptors;
- callable symbols for all ten registered operations.

The implementation is dependency-free C11 and compiles with:

```text
-std=c11 -O2 -Wall -Wextra -Werror -pedantic
```

Canonical native authority uses signed and unsigned integers, UTF-8 byte sequences, explicit buffers, and typed structures. Floating-point types, IEEE infinity, and NaN are absent.

## 5. Native operation profiles

The native ABI profiles are deliberately explicit:

| Operation | Native profile |
|---|---|
| `system.status` | ABI/status structure |
| `python.len` | exact host `size_t` length |
| `python.abs` | signed 64-bit integer |
| `python.sorted` | signed 64-bit integer array |
| `list.with_appended` | signed 64-bit integer array |
| `dict.get` | UTF-8 keys and canonical JSON value slices |
| `text.join` | UTF-8 string sequence with caller-owned output buffer |
| `math.gcd` | signed 64-bit integer inputs with exact unsigned magnitude handling |
| `pass189.context.decode` | complete `0 <= A < 51,648,192` address structure |
| `state.counter.advance` | singleton signed 64-bit counter context |

Values outside a declared profile are rejected rather than silently narrowed. This iteration therefore proves native coverage of all operation identities but does not claim complete native representation of every Python value admitted by the higher-level registry schemas.

## 6. Compiler lowering

`HarmonicodeOperationCompiler` accepts one exact constructor instruction per non-empty source line. Comments and blank lines are non-executable.

Each instruction preserves four layers:

### CST

- exact lexical source;
- source line;
- explicit `preserve_exact` witness.

### AST

- canonical constructor identity;
- exact literal arguments;
- `OperationConstructor` node class.

### HIR

- canonical operation identifier;
- operation Hash216 identity;
- effect class;
- capability scope;
- determinism class.

### VMIR

- inherited VM81 binding;
- generated native ABI symbol;
- native representation profile;
- deterministic operation slot;
- mutation-lane witness.

The complete compiled program receives one Hash72 identity and one Hash216 topology identity.

## 7. Authority and native parity

Compiled execution calls `HHSAuthorityContext.invoke(...)` with surface identity `compiler-vmir`. It therefore preserves:

- schema validation;
- capability gates;
- singleton mutation ordering;
- expected-state conflict behavior;
- idempotency policy;
- Hash72 receipt chaining;
- Hash216 topology;
- deterministic replay.

`NativeABI` loads the generated shared library through `ctypes` and performs typed conversion only within the declared native profiles. Tests compare the semantic result of native and canonical Python projections for every non-status field that both profiles share.

Native mutation maintains its own test context for ABI verification. It is not allowed to bypass the VM81/Hash72 authority used by production API, compiler, shell, SDK, and GUI surfaces.

## 8. Compiler API

Iteration 3 adds:

```text
POST /api/pass190/compile
POST /api/pass190/compile-execute
GET  /api/pass190/native-abi
```

`compile-execute` lowers the source and then executes every instruction through the persistent iteration 2 authority context. The response includes the compiled program and normal admitted operation results with receipts.

OpenAPI identifies iteration 3, the compiler routes, the native manifest route, and the inherited WebSocket channel.

## 9. CLI

The compiler module can:

- compile inline source or a source file;
- emit complete CST/AST/HIR/VMIR JSON;
- execute through a fresh canonical authority context;
- invoke the native ABI projection for comparison;
- pass declared capabilities to canonical execution.

## 10. Validation

`make validate` now performs:

- iteration 1 regression tests;
- iteration 2 regression tests;
- iteration 3 compiler and parity tests;
- strict C11 shared-library compilation;
- strict C11 native test compilation and execution;
- ten-operation manifest and symbol verification;
- generated native artifact parity;
- compiler Hash72/Hash216 determinism;
- CST/AST/HIR/VMIR content verification;
- canonical compiled execution and receipt continuity;
- native/Python semantic parity vectors;
- native range, buffer, representation, and conflict failures;
- live compiler HTTP and OpenAPI tests;
- Python bytecode compilation;
- no-float native scan;
- private `eval(...)` and `exec(...)` scan;
- inherited SDK, GUI, binding, and deployment checks.

## 11. Deployment

The systemd unit now launches `hhs_pass190_iteration3_server.py`, retaining the same persistent SQLite authority database and inherited HTTP/WebSocket service port. Deployment verification also checks the native ABI manifest endpoint.

A live DigitalOcean installation is not claimed by this repository-only iteration.

## 12. Remaining Pass 190 work

The following remain incomplete:

- repository-wide discovery and hydration of every public operation;
- complete Python built-in and standard-library parity;
- complete native representation of every canonical schema type;
- native receipt and Hash72 commit integration under one process authority;
- complete expression grammar, control flow, functions, modules, and multi-file compilation;
- complete CST → AST → HIR → VMIR lowering for the full HARMONICODE language;
- migration of every existing API route, GUI action, and workflow to canonical registry resolution;
- complete job, workspace, artifact, provider, and capability registries;
- multi-process distributed mutation arbitration;
- live DigitalOcean installation and production acceptance;
- final full Pass 190 completion classification.

Iteration 3 is committed only for its validated native ABI and compiler foundation. Unimplemented type coverage and language features remain explicit.
