# Pass 218 Iteration 10 Evidence Summary

## Classification

`HHS_PASS218_ITERATION10_DISTRIBUTED_CANONICAL_OWNERSHIP_EVIDENCE`

Iteration 10 adds a production etcd-v3 linearizable lease/CAS authority above the validated Iteration-9 per-host POSIX ownership fence. A canonical writer must hold both fences. Cross-host restart is reconstructed from the distributed sealed Iteration-7 checkpoint; it does not mint a new Iteration-5 authorization or invoke a new Iteration-6 canonical mutation.

## First complete green authority run

- Branch head: `d10386abdae9bd10b0825b2629ac7a120dc9b1ac`
- Workflow: `Pass 218 Full Iteration 10`
- Run: `31662124800`
- Result: **SUCCESS**
- Real etcd v3 reachability gate: PASS
- Cumulative Pass-218 + Runtime-OS compilation: PASS
- No-authoritative-float gate: PASS
- I1: 12 passed
- I2: 13 passed
- I3: 12 passed
- I4: 14 passed
- I5: 18 passed
- I6: 19 passed
- I7: 21 passed
- I8: 23 passed
- I9: 15 passed
- I10: 26 passed, including real-etcd lease/CAS/expiry tests
- inherited repository-native crawler: 14 passed
- Runtime-OS production-root: 6 passed
- repository-native Iteration-10 distributed evidence: PASS

## Repository-native source identity

Input: `creative_writing/novels/THE_SMALLEST_PERMISSION.md`

- source SHA-256: `42caa64e6d75aeeedb256f8e9c72b773ab9e5e230bcbc63e76bdff59fae37c03`
- structural beats: 61
- transaction Hash72: `9ckHe3R(Hr<W0gU9MA5jYr/UdZCcHHXjY/LZyksp3D>OICUnbFAU<Q-Tw1r/piFmdaZb5D!+`
- transaction Hash216: `6JkYG6603eZtycYAu3YprX-c*Qbfjukhv+cnT1Y+3pvEJ+A0EQZV+F5F*oBJU?UwvLriPuIdiByfNPkuZ<iBALkcXO?AuLZgcHP?X<9/ALmw?Kor7EcU+2h0ui6HnBC>Qg??DRn6G8l0iEQvMETfszWbK-zA3dc8XFpkjFhZ?2MRPrnWOys06icn8MY?NZ9Ulw1Rn>)3xnHorAE7Lii28S1K`
- candidate entry ID SHA-256: `2cb8dffce47850123f6f6878ce8e4c107670e493c4d681963d1fde0051fa2eae`
- VM5184 projection SHA-256: `7496cdb5047f7609397ba06adbc0e9c303efd4d9240f9b6a6198164df70b2baa`

## Distributed canonical checkpoint identity

- canonical root Hash72: `ZnYcA3Vf9WPCp)pvZpVEoGZsW6-jzFEhyUVXiB4-jGp7TP)srG<quL-I3Aqe!atW?JxE6Uj*`
- checkpoint SHA-256: `73ecfe916de2c8a15d85455b2f88b111b48d0563d0bd71fc848baab1dfe56738`
- checkpoint Hash72: `eIKS+ZHOP!*Ku+eXcST+kV?2(cQ3Hzba<<KnknkYR50l+<L3R>P/aob1lpIj1RvGrJ/o?<Pb`
- distributed checkpoint seal Hash72: `3UIwD9jAQu<oyEiSBHOmItOtD9mQ5b-MaKC)aL!B?t-GMOXgrKq4f3iK/ioIeufog>7u9xh1`

The distributed wrapper contains the fully validated Iteration-7 checkpoint, not source prose. It is admitted only by an etcd transaction that compares the exact current lease-bound owner, global fence, and predecessor checkpoint.

## Dual-fence evidence

Initial authority:

- host A local I9 fence epoch: 1
- host A distributed I10 fence epoch: 1
- host A distributed owner: `iteration10-owner-a`
- host A lifecycle state: `DISTRIBUTED_EMPTY_READY`

Concurrent host-B state while host A owns the distributed fence:

- lifecycle state: `DISTRIBUTED_OWNERSHIP_STANDBY`
- distributed writer authority: false
- ingestion enabled: false
- canonical boundary blocked: true

## Lease-expiry takeover evidence

The repository evidence keeps host A's process/local I9 lock alive but intentionally stops distributed lease renewal. The real etcd service expires the lease-bound owner key. Host B, using an unrelated local Iteration-7 store, then acquires the next distributed fence.

- takeover lifecycle state: `DISTRIBUTED_RESTORED_READY`
- takeover distributed fence epoch: 2
- exact previous owner: `iteration10-owner-a`
- exact previous host: `iteration10-host-a`
- canonical root exact after restore: true
- VM81 snapshot exact after restore: true
- consumed I6 receipt exact after restore: true
- distributed checkpoint identity exact after restore: true
- new authorization minted during restart: false
- new canonical mutation invoked during restart: false
- stale host-A canonical boundary blocked after lease expiry: true
- split-brain writer permitted: false

This evidence models two hosts as independent Runtime-OS lifecycle instances with unrelated local persistence roots and distinct host identities against a real etcd-v3 authority service. It validates the production cross-host protocol and recovery path without claiming that the CI runner itself is a multi-machine production cluster.

## Failure and partition semantics

I10 validation also proves:

- distributed transport/quorum unavailability closes effective lifecycle ingress;
- real etcd lease expiry rejects the stale owner and advances the global fence;
- exact predecessor CAS rejects stale checkpoint publication;
- if local I6/I7 mutation succeeds but distributed publication fails, the local target rolls back to the last distributed checkpoint and ingress remains closed;
- after such rollback, the unconsumed I5 authorization remains retryable by the successor owner;
- distributed-required Runtime-OS configuration never silently downgrades to local I9 writer authority.

The in-memory consensus harness exists only for deterministic failure injection. Production distributed ownership is `ETCD_V3_LINEARIZABLE_LEASE_CAS`.

## Source and authority exclusions

The real repository evidence proves:

- source text present in distributed authority: false
- Pass-165 source-retaining path invoked: false
- canonical learning commit invoked: false
- truth promotion: false
- action authority minted: false
- verbatim source retained: false
- authoritative float literals: none

## Scope

Iteration 10 does **not** implement Raft or replace etcd consensus. HHS consumes etcd-v3 linearizable lease/CAS semantics as its distributed authority substrate and cryptographically binds that external authority to HHS's exact ownership, fencing, checkpoint, and Pass-217/VM81 recovery records.

Existing single-host deployments without distributed configuration remain on the validated Iteration-9 local ownership boundary. Distributed mode is activated by configuration; explicitly required but unavailable distributed authority is fail-closed and diagnostic-only.

This summary records evidence from the first complete green implementation run. A complete workflow rerun on the documentation-complete head is required before Iteration 10 is frozen.
