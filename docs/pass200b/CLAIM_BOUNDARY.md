# Pass 200B Claim Boundary

## Proven by this pass

- A Pass 200A `COMPILER_CANDIDATE` bundle can be admitted to a bounded canary frontier only after two distinct approval principals present the exact compiler and runtime promotion capabilities.
- Every approval is bound to its bundle Hash72, the current frontier Hash72, an expiry, and a VM81 receipt Hash72.
- Canary activation requires a separate singleton VM81 receipt.
- Candidate return is deterministic, ratio-bounded, invocation-bounded, and conditional on exact result, witness, and replay equality.
- Any mismatch, expiry, explicit rollback, or invocation-limit exhaustion restores a reference-only frontier.
- Frontiers and invocations are retained as immutable records with an ordered Hash72 event chain.
- Restart preserves the frontier pointer, counters, invocation history, and event-chain tip.

## Not authorized by this pass

- Candidate self-approval or self-admission.
- Mutation of an admitted ratio, limit, approval, expiry, or frontier body.
- Unrestricted active execution after canary completion.
- Automatic compiler or runtime promotion.
- Automatic frozen-constraint promotion.
- Deletion or rewriting of prior frontier history.

## Terminology

A candidate return during an admitted canary invocation is not unrestricted activation. It is one metered return inside the exact canary ratio and invocation envelope. The authority automatically returns to the reference frontier when the envelope closes or fails.
