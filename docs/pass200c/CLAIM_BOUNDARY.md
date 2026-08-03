# Pass 200C Claim Boundary

## Proven by this pass

- Active admission requires two completed successful Pass 200B canary frontiers for the same bundle and at least 12 exact canary invocations.
- A Pass 200B rollback for the bundle blocks active admission.
- Compiler, runtime, and operations approval capabilities must come from three distinct principals and three distinct VM81 receipts.
- A separate VM81 receipt authorizes the singleton active-frontier transition.
- The candidate is the default returned path only after exact result, witness, and replay equality is verified on every invocation.
- Any mismatch, expiry, explicit rollback, or lease exhaustion restores reference execution.
- Evidence, frontiers, counters, invocations, and Hash72 events survive restart.

## Not authorized by this pass

- Candidate self-approval, self-admission, lease renewal, or guard suppression.
- Removal of the reference execution path.
- Sampled or periodic exact guards.
- Unbounded active execution without a lease.
- Permanent compiler or runtime constraint freezing.
- Rewriting or deleting prior evidence and frontier history.

## Terminology

`ACTIVE_GUARDED` means the candidate is the default returned path inside an explicitly approved lease, but only after the exact comparison guard succeeds for that invocation. It does not mean the reference implementation or rollback path has been removed.
