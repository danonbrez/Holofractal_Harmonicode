# Pass 145 Architecture

## Authority flow

```text
Source bytes
  -> bounded deterministic parser
  -> immutable source + separate parse identity
  -> inherited Pass 125 segmentation
  -> inherited Pass 126 claim interpretation
  -> provenance-bound object graph
  -> V1–V9 validation
  -> atomic SQLite transaction
  -> ordered receipt chain
  -> read-only query / deterministic replay
```

The authoritative local store is `HHS145Database`. UI, CLI, API, workbench, and Android projections are adapters over `HHS145Service`; none is permitted to write SQLite directly.

## Storage model

Canonical content tables include sources, parses, segments, objects, relations, validations, workspaces, environments, scripts, LVMs, API collections, and extensions. Operational tables contain transactions, receipts, and executions. Raw source bytes remain immutable. Interpretations and validations are append-only identities rather than replacements for source evidence.

Database roots are calculated from canonical content, not wall-clock timestamps or occurrence-specific receipt identifiers. Execution records retain the complete observed envelope, while deterministic LVM replay hashes a semantic projection that excludes only occurrence-specific transaction identities.

## Exact authority

Canonical JSON rejects IEEE floating-point values. Exact integers, strings, symbolic values, and inherited Hash72 objects retain authority. JSON containing floats is rejected with `RUNTIME_REJECTED`. Float projections may be added only through a separately declared noncanonical lane.

## Script and LVM boundaries

Scripts declare capabilities. Validation infers requested access and classifies undeclared access as `RUNTIME_REJECTED`; execution refuses unvalidated scripts. JavaScript runs only when explicitly invoked through the script workbench and then inside a bounded Node `vm` context. Imported HTML and JavaScript are never executed by ingestion.

LVMs validate component identity, topology, recursive depth, component count, and bounded-cycle policy. Nested machines retain independent manifests, executions, receipts, and failure boundaries.

## Android projection

The Android project contains:

- Gradle application configuration for `arm64-v8a` and `x86_64`;
- JNI bindings to `hhs_runtime_abi.c` and `hhs_hash216.c`;
- a hardened WebView with file/content storage access disabled;
- a loopback-only authenticated bridge;
- Android share-text admission;
- an explicit build failure receipt when required SDK tools are absent.

The source projection is not classified as an installed APK until Android build, signing, installation, and real-device evidence exist.
