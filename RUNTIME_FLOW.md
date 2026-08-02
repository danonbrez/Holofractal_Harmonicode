# HHS Runtime Flow

This document defines the current end-to-end execution flow for Harmonicode programs, registered operations, Pass 190 durable jobs, provider proposals, receipts, replay, persistence, APIs, SDKs, and visual projection.

## 1. Universal transition flow

```text
request or source
→ canonical input capture
→ parsing and source preservation
→ symbolic normalization or macro expansion
→ typed operation/state proposal
→ capability and policy checks
→ singleton VM81 admission
→ exact evaluation
→ kernel/invariant audit
→ LOCKED or QUARANTINED decision
→ Hash72 receipt commitment
→ Hash216 ordered identity/topology witness
→ replay verification
→ persistence and graph ingestion
→ API/SDK/WebSocket/assistant/visual projection
```

No user-facing surface is an alternate authority. The same transition may be invoked from CLI, API, SDK, assistant, worker, or GUI, but its canonical path remains singular.

## 2. Harmonicode source flow

```text
Harmonicode source
→ preserve lexical form and membranes
→ parse typed expressions
→ resolve equality/constraint-join domains
→ normalize symbolic structure without erasing identity
→ bind macro parameters
→ recursively expand nested macros
→ commit source, macro, and expansion Hash72 identities
→ submit expanded operation to AuditedRunner
→ VM81/kernel admission
→ receipt and replay
```

Required preservation includes:

- ordered products such as `xy` and `yx`;
- exact lists, positions, lexical widths, and identity-bearing leading zeros;
- exact reciprocal and rational forms;
- parenthetical membrane depth and scope;
- source spans and nested macro lineage;
- symbolic distinctions such as `O != Pi` where defined by contract.

## 3. `.hhsprog` execution

A program file declares ordered operations.

```text
load `.hhsprog`
→ validate format and program name
→ validate ordered operation records
→ initialize one AuditedRunner
→ execute each operation in order
→ stop on quarantine unless `continue_on_quarantine` is declared
→ collect results and receipts
→ verify the runner receipt chain
→ optionally persist through the database bridge
→ emit `.hhsrun`-compatible result
```

A run result contains:

- program Hash72;
- declared and executed operation counts;
- per-step results;
- receipts;
- chain status;
- replay report;
- optional storage report;
- final `all_ok` state.

## 4. Audited operation flow

```text
registered operation + arguments
→ capture pre-state and current receipt tip
→ execute exact implementation
→ derive audit value and operation witnesses
→ submit to kernel gate
→ evaluate operation-specific conditions
→ build post-state
→ commit input/pre-state/operation/post-state/witness identities
→ commit parent-linked receipt
→ return admitted result or quarantined evidence
```

### Locked result

```text
kernel and operation conditions satisfied
→ gate_status = LOCKED
→ result may enter canonical state
```

### Quarantined result

```text
exception, invariant failure, order breach, invalid capability, stale claim, or other gate failure
→ gate_status = QUARANTINED
→ evidence and reason are committed
→ result is blocked from canonical mutation
```

## 5. Receipt structure

A transition receipt binds at least:

```text
phase or tick
operation
parent_receipt_hash72
input_hash72
pre_state_hash72
operation_hash72
post_state_hash72
witness_hash72
receipt_hash72
integrity_hash72
gate_status
locked/quarantine state
reason
```

The next receipt must name the previous receipt as its parent. Chain continuity is part of execution correctness.

## 6. Replay flow

```text
receipt sequence
→ start from genesis or declared parent boundary
→ verify parent linkage
→ verify canonical receipt fields
→ rederive commitment identities
→ verify expected chain tip
→ compare deterministic reconstruction
→ return verified or explicit mismatch
```

Replay mismatch must not be silently ignored. The outcome must be explicit failure, quarantine, rollback boundary, or unresolved evidence state.

## 7. Pass 190 Iteration 7 durable job flow

Current path:

```text
job.submit_execution
→ verify operation exists
→ require operation effect_class == pure
→ verify workspace, dependency, schedule, retry, and capability fields
→ commit scheduled or queued job
→ scheduler.tick evaluates time and dependencies
→ eligible worker heartbeat and capabilities verified
→ job.claim_next selects deterministically
→ Hash72 claim token committed
→ job.execute_claimed validates token, worker, lease, and capabilities
→ exact target implementation evaluated
→ one outer VM81 admission
→ one execution Hash72 and receipt
→ atomically update job, worker, state root, and event
```

### Deterministic selection

```text
highest priority first
then lexicographically smallest job_id
```

### Dependency states

```text
all dependencies completed
→ schedule boundary may release job to queued

any dependency failed or cancelled
→ dependent job fails with typed dependency witness

otherwise
→ job remains scheduled
```

### Job states

```text
scheduled → queued → running → completed
scheduled → failed
queued → cancelled
running → cancelled
running → retry_wait → queued
running → failed
failed/cancelled → retry_wait or queued when budget remains
```

### Retry coordinate

```text
next_attempt_ns = observed_now_ns + retry_backoff_ns × max(1, attempt)
```

All time coordinates are exact nonnegative integer nanoseconds.

### Stale-worker recovery

`scheduler.tick` checks running jobs for:

- expired execution lease;
- missing worker;
- disabled worker;
- expired heartbeat authority.

Recovery atomically releases the worker and moves the job to retry or terminal failure according to remaining attempt budget.

## 8. Pass 190 service topology

```text
hhs-pass190.service
hhs-pass190-worker.service
        ↓
shared authoritative SQLite state
/var/lib/hhs/pass190-authority.sqlite3
```

The worker process performs:

```text
ensure registered
→ heartbeat
→ scheduler tick
→ claim next eligible job
→ execute claimed job
→ repeat
```

The worker owns no authoritative local queue or result store.

## 9. API flow

```text
HTTP request
→ route validation and capability extraction
→ orchestrator/runtime call
→ canonical execution path
→ receipt-bearing result
→ response serialization
```

Routes must not contain canonical business or mutation logic.

Pass 190 Iteration 7 exposes:

```text
GET /api/pass190/execution-runtime
```

The route projects already-governed worker, queue, operation, state-root, and execution-runtime evidence.

## 10. WebSocket flow

```text
canonical state transition
→ committed event
→ orchestrator/event bus
→ WebSocket serialization
→ client projection
```

WebSocket handlers transport events. They do not create unreceipted state transitions.

## 11. Visual IDE flow

```text
user action
→ frontend request
→ backend route
→ authoritative runtime operation
→ receipt-bearing response/event
→ update UI from runtime evidence
```

The UI must expose:

- pending/running/completed/failed/cancelled states;
- timeout, retry, and failure reasons;
- degraded backend/provider status;
- receipt and authority evidence where relevant;
- no optimistic success that contradicts runtime state.

## 12. Assistant and provider flow

```text
human request
→ bounded assistant thread
→ allowlisted tool or provider proposal
→ capability and policy gate
→ provider invocation
→ invocation receipt
→ HHS result ingress
→ VM81/kernel admission where mutation is requested
→ bounded assistant or artifact projection
```

Model output is not canonical solely because the provider returned it.

## 13. Graph and persistence flow

```text
locked or quarantined receipt
→ graph ingestion
→ parent/topology indexing
→ state and artifact persistence
→ replay lookup and reconstruction
```

Graph and storage layers preserve execution evidence. They do not create alternate execution authority.

## 14. Pass 191 hydration target

The frozen Pass 191 contract extends the runtime flow to every accepted repository object and surface:

```text
Genesis and inherited pass history
→ repository object discovery
→ canonical object graph
→ canonical operation registry
→ inherited invariant binding
→ VM81 admission path
→ Hash72 lineage
→ Hash216 topology
→ parity across ABI, CLI, API, WebSocket, SDK, automation, assistant, and Visual IDE
```

Full Pass 191 completion requires source, manifests, tests, receipts, replay, integration evidence, and authoritative-main verification.

## 15. Validation

Baseline:

```bash
python hhs_runtime_smoke_tests_v1.py
python hhs_regression_suite_v1.py
python hhs_v1_bundle_runner.py
```

Pass 190 Iteration 7:

```bash
make -C native_projects/hhs_pass190_operation_fabric validate
```

A path, dependency, or environment failure is repaired at the adapter boundary. Invariants, identity preservation, receipt continuity, and replay requirements are not weakened.
