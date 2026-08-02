# HHS PASS 190 ITERATION 7 — DURABLE WORKER EXECUTION, DEPENDENCY SCHEDULING, CANCELLATION, AND RETRY

## 1. Metadata

| Field | Value |
|---|---|
| Contract | `HHS-P190-I7-DWE-DSCR-WL-VM81-H72-H216` |
| Parent | `HHS-P190-I6-URR-JLC-CF-VM81-H72-H216` |
| Iteration | `7` |
| Baseline | `main @ 1d3c7588a242e3a83304f5083c2ec5a974f19399` |
| Classification | `HHS_PASS_190_ITERATION_7_DURABLE_WORKER_EXECUTION_SCHEDULING_CANCELLATION_RETRY_VERIFIED` |
| Native ABI expansion | Not claimed; inherited ten-operation ABI preserved |
| Full Pass 190 completion | Not claimed |

## 2. Purpose

Iteration 6 made workspaces, artifacts, providers, capability definitions, and jobs first-class resources under one persistent VM81 and Hash72 authority. Iteration 7 makes the internal job path executable without creating a second scheduler, worker, or mutation authority.

```text
registered pure operation
→ durable execution job
→ dependency and schedule admission
→ eligible worker capability match
→ Hash72 execution claim
→ exact target evaluation
→ one outer VM81 admission
→ one Hash72 receipt and event
→ completed, retry-wait, failed, or cancelled job state
```

Every job and worker transition remains part of the inherited atomic SQLite state, lease, fence, kernel witness, receipt, replay, and event topology.

## 3. Governed operation registry

The inherited 31 governed operations remain unchanged. Iteration 7 adds eleven operations:

### Worker authority

```text
worker.register
worker.get
worker.list
worker.heartbeat
worker.set_enabled
```

### Durable job authority

```text
job.submit_execution
job.cancel
job.retry
job.claim_next
job.execute_claimed
```

### Scheduler authority

```text
scheduler.tick
```

Total governed operations:

```text
10 inherited native operations
+ 21 Iteration 6 exact-authority operations
+ 11 Iteration 7 execution operations
= 42 governed operations
```

The C ABI remains exactly ten operations. The remaining 32 operations lower through the inherited exact VM81 authority fallback.

## 4. Canonical execution state

Worker state is stored beside the inherited resource registries:

```text
state = {
  counter,
  resource_registries: {
    workspaces,
    artifacts,
    providers,
    capabilities,
    jobs
  },
  execution_runtime: {
    workers
  }
}
```

The single state identity remains:

```text
H_state = Hash72("pass190.state", state)
```

No worker-local file, process memory, queue, timer, or subprocess is authoritative.

## 5. Exact time model

All schedule, heartbeat, lease, retry, start, and completion coordinates are non-negative exact integer nanoseconds.

Floating-point time is forbidden from canonical authority.

The runtime accepts declared `now_ns` observations and validates monotonic worker heartbeats, bounded worker lease timeouts, bounded execution leases, and bounded retry backoff.

## 6. Worker record

Each worker contains:

```text
schema
worker_id
capabilities[]
labels[]
enabled
registered_at_ns
last_heartbeat_ns
lease_timeout_ns
current_job_id
current_claim_token_hash72
completed_job_count
failed_attempt_count
version
record_hash72
```

Required invariants:

- canonical unique worker identity;
- sorted unique declared capabilities and labels;
- every worker capability is defined by the inherited capability-definition registry;
- exact integer timing;
- one running job maximum;
- worker and running-job claim identities agree in both directions;
- a worker owning a running job cannot be disabled;
- worker records are Hash72 verified at every restore.

## 7. Durable execution job

An Iteration 7 job extends the inherited job record with:

```text
execution_schema_version = 1
dependency_job_ids[]
submitted_at_ns
schedule_not_before_ns
next_attempt_ns
priority
attempt
max_attempts
retry_backoff_ns
execution_request
execution_request_hash72
claim_token_hash72
lease_expires_ns
cancel_requested
started_at_ns
finished_at_ns
execution_hash72
```

Canonical states:

```text
scheduled → queued → running → completed
scheduled → failed
queued → cancelled
running → cancelled
running → retry_wait → queued
running → failed
failed → retry_wait or queued, when attempt budget remains
cancelled → retry_wait or queued, when attempt budget remains
```

Every transition is explicit, typed, durable, and receipt-bound.

## 8. Pure-operation execution membrane

Iteration 7 intentionally executes only registered operations whose `effect_class` is `pure`.

```text
operation.effect_class == pure
```

Mutating target operations are rejected at job submission and checked again at execution.

This prevents nested mutation authority and prevents an execution worker from bypassing the singleton VM81 admission membrane.

Provider-backed or external operations are not executed by this pass. A durable internal job has:

```text
provider_id = null
```

Provider adapters remain a later bounded pass.

## 9. Dependency graph

Dependencies must:

- exist;
- belong to the same workspace;
- be unique;
- exclude the job itself;
- form an acyclic graph.

Admission rules:

```text
all dependencies completed
→ job may become queued when schedule boundary is reached

any dependency failed or cancelled
→ dependent job fails with dependency_terminal witness

otherwise
→ job remains scheduled
```

Cycle detection is executed during state validation and therefore also during restart hydration.

## 10. Deterministic scheduling

Eligible jobs satisfy:

```text
status == queued
next_attempt_ns <= now_ns
all dependencies completed
required_capabilities ⊆ worker.capabilities
worker enabled and heartbeat-valid
```

Selection order is deterministic:

```text
highest priority first
then lexicographically smallest job_id
```

No random queue ordering or wall-clock float comparison is authoritative.

## 11. Claim identity

A claim is bound by:

```text
claim_payload = {
  job_id,
  worker_id,
  attempt,
  claimed_at_ns,
  lease_duration_ns,
  preclaim_state_root
}

claim_token_hash72 = Hash72("pass190.execution.claim", claim_payload)
```

The job and worker both store the same claim token. Execution rejects:

- wrong worker;
- wrong token;
- expired job lease;
- expired worker heartbeat authority;
- disabled worker;
- missing required capability;
- non-running job;
- pending cancellation.

## 12. Receipt-bound execution

The selected pure operation implementation is evaluated inside `job.execute_claimed`.

It does not create an unpersisted nested receipt. The target result is enclosed by one authoritative outer transition:

```text
execution_payload = {
  job_id,
  worker_id,
  attempt,
  operation_id,
  operation_hash216,
  arguments,
  result,
  executed_at_ns,
  claim_token_hash72
}

execution_hash72 = Hash72("pass190.execution.result", execution_payload)
```

The outer `job.execute_claimed` receipt binds:

- target operation identity;
- target arguments;
- target result or typed error;
- job transition;
- worker release;
- state-before and state-after;
- authority lease and fence;
- Hash72 and Hash216 receipt topology.

## 13. Retry policy

Each job declares:

```text
1 <= max_attempts <= 10
retry_backoff_ns >= 0
```

After an execution failure or stale execution lease:

```text
attempt < max_attempts
→ retry_wait or queued

attempt == max_attempts
→ failed
```

The exact retry coordinate is:

```text
next_attempt_ns = observed_now_ns + retry_backoff_ns × max(1, attempt)
```

Manual retry is admitted only for failed or cancelled jobs with remaining attempt budget.

## 14. Cancellation

Cancellation applies to scheduled, queued, retry-wait, or running durable jobs.

A running cancellation atomically:

- transitions the job to `cancelled`;
- preserves a typed cancellation reason;
- clears claim and lease fields;
- releases the worker;
- increments the worker failed-attempt counter;
- commits one state root and receipt.

Terminal jobs return their existing state idempotently.

## 15. Stale-worker recovery

`scheduler.tick` detects a running job whose:

- execution lease expired;
- worker is absent;
- worker is disabled; or
- worker heartbeat authority expired.

The scheduler atomically releases the worker and moves the job into retry or terminal failure according to the remaining attempt budget.

No indefinitely running state is permitted after a bounded lease expiry observation.

## 16. Worker process

`worker/hhs_pass190_iteration7_worker.py` is a restartable single-host worker process.

Its loop is:

```text
ensure registered
→ heartbeat
→ scheduler tick
→ claim next eligible job
→ execute claimed job
→ repeat
```

The process stores no authoritative queue or result outside the shared database.

The default DigitalOcean worker declares no protected target capability. It therefore executes only public pure operations until capabilities are explicitly defined and assigned.

## 17. HTTP, SDK, compiler, and visual surfaces

Iteration 7 adds:

```text
GET /api/pass190/execution-runtime
```

OpenAPI reports:

- Iteration 7 contract and classification;
- 42 governed operations;
- ten native operations;
- eleven execution operations;
- the execution-runtime endpoint;
- all canonical direct operation paths.

Generated Python and TypeScript SDKs expose all 42 operations and execution-runtime discovery.

`P190_OPERATION_SURFACE_BINDINGS_V3` marks native availability and execution-operation membership for every operation.

The visual authority displays:

- worker count;
- enabled worker count;
- queued, scheduled/retry, and running job counts;
- execution operation count;
- execution runtime Hash72;
- execution-runtime integrity;
- all inherited resource, lease, fence, receipt, event, and kernel-authority indicators.

## 18. DigitalOcean deployment

Two hardened services share one authoritative database:

```text
hhs-pass190.service
hhs-pass190-worker.service
```

Both use:

```text
/var/lib/hhs/pass190-authority.sqlite3
```

The API service runs the Iteration 7 server on `127.0.0.1:8190`.

The worker service is restartable and requires the API authority unit. Installation, rollback, verification, and service status include both units.

Vercel remains outside this deployment and acceptance path.

## 19. Validation

Iteration 7 adds tests for:

1. exact 42-operation registry and Hash216 identity;
2. worker capability-definition enforcement;
3. scheduled dependency submission;
4. deterministic priority claims;
5. receipt-bound successful execution and replay;
6. worker capability coverage;
7. dependency release after parent completion;
8. retry and attempt-budget exhaustion;
9. cancellation and worker release;
10. stale-worker lease recovery;
11. terminal dependency propagation;
12. restart hydration and worker-record tamper rejection;
13. compiler and actual worker-process execution;
14. live HTTP and OpenAPI execution surfaces.

All inherited Iterations 1–6 tests, strict C11 tests, generated native artifacts, SDK/binding parity, GUI/deployment verification, private-evaluation rejection, and no-float authority checks remain binding.

## 20. Honest boundary

Iteration 7 does not claim:

- external provider execution;
- arbitrary subprocess or shell execution;
- mutation-target worker execution;
- distributed multi-host consensus;
- broader native ABI parity;
- complete Python standard-library hydration;
- live DigitalOcean installation or production acceptance;
- final Pass 190 completion.

Those remain explicit later-pass work.
