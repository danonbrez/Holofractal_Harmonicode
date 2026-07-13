# HHS Closure Harness Bounded Runtime — Pass 041

## Purpose

Pass 041 prevents the system closure harness from becoming an unbounded certification path as runtime ledgers and validation artifacts accumulate.

The closure harness remains an integration proof surface. It is not the full-ledger auditor. Full ledger verification remains available through `hhs_unified_hash72_ledger_v1.verify_unified_ledger`; the closure harness now uses a bounded runtime envelope and a compact edge-summary ledger witness during certification execution.

## Invariant

```text
closure harness execution
→ bounded cycles
→ bounded max steps
→ compact ledger summary
→ Hash72/u^72 witness
```

Not:

```text
closure harness execution
→ repeated whole-ledger recomputation
→ runtime proportional to historical ledger residue
```

## Runtime Budget

The bounded certification envelope is:

```text
max_cycles: 3
max_step_budget: 16
include_details: false unless explicitly allowed by bounded policy
```

Invalid expansion attempts are rejected with:

```text
REJECT_CLOSURE_HARNESS_UNBOUNDED_CYCLES
REJECT_CLOSURE_HARNESS_UNBOUNDED_STEPS
REJECT_CLOSURE_HARNESS_DETAILS_EXPANSION
REJECT_CLOSURE_HARNESS_FLOAT_BUDGET
```

## Bounded Artifact Lane

During closure harness execution, Pass 041 uses an isolated bounded runtime output directory:

```text
data/runtime/pass041_bounded_closure/
```

The bounded lane is reset at harness start. This prevents old certification artifacts from making future certification runs slower.

This is not a parallel authority lane. It is a bounded certification lane whose records still emit Hash72/u^72 receipts and compact ledger witnesses.

## Service

```text
closure_harness.bounded_runtime_self_test
```

## Make target

```text
make closure-harness-bounded-runtime
```
