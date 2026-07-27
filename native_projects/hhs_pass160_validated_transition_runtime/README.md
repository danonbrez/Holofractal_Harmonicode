# HHS Pass 160 Validated Transition Runtime

Contract: `HHS-P160-FPPORT-VTR` with append-only inheritance amendment `1.2.0`.

This directory contains the complete Pass 160 native C11 runtime, independent Python reference implementation, CLI, governed HTTP projection, schemas, manifests, tests, replay tools, fault injection, performance workloads, and evidence/release tooling.

The ordinary inspectable source is retained in two deterministic repository source capsules under `assets/source_capsule/`. `make materialize` verifies both SHA-256 commitments and extracts the source tree without network access. Every extracted file and digest is listed in `assets/source_capsule/SOURCE_CAPSULE_MANIFEST.json`.

## Authority boundaries

```text
stored validation      != current reuse admission
nested execution       != authoritative commit
approximate discovery  != exact lookup
GPU completion         != publication
model request           != capability
```

Only previously VM81-admitted transitions may enter the store. Reuse requires exact ancestry, dual Hash216/SHA-256 verification, sealed segment membership, unrevoked current semantic and implementation roots, and a capability-zero nested runtime. External operations remain inert proposals. Authoritative mutation requires fresh outer VM81 or Pass 158 admission.

## Build and validation

```sh
make materialize
make all
make verify
make package
```

`make verify` executes native, Python, CLI, HTTP, differential, fuzz, fault, concurrency, one-million-lookup performance, inherited regression, and sanitizer gates. Terminal classification additionally requires matching x86_64 and aarch64 canonical roots and executed evidence closure in GitHub Actions.

## Local executed state before publication

```text
native positive checks:       1,000,595
native negative checks:       160
native failures:              0
exact lookup workload:        1,000,000
C/Python differential vectors: 7/7
CLI commands:                 24/24
Python reference tests:       6/6
property fuzz valid checks:   2,048
property fuzz rejections:     512
fault-injection points:       22
partial authoritative states: 0
concurrent conflicting proposals: 2
admitted authoritative commits:   1
```

## Current classification

```text
HHS_PASS_160_IMPLEMENTATION_VERIFIED_PENDING_CROSS_ARCHITECTURE_TERMINAL_EVIDENCE
```

Reserved terminal classification:

```text
HHS_PASS_160_FIBONACCI_PRIME_PSEUDORANDOM_OVERLAP_RECEIPT_TIP_VALIDATED_TRANSITION_RUNTIME_VERIFIED
```
