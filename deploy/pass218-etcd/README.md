# Pass 218 Iteration 11 — etcd operational authority

This directory contains the deployment contract for the Pass 218 Iteration 11
multi-member canonical authority. Iteration 11 does **not** replace the I9/I10
protocol. A writer remains authoritative only while it holds the local I9 fence
and the I10 lease/CAS fence. I11 adds operational requirements around the etcd
substrate.

## Required topology

Production I11 mode requires an odd etcd member count of at least three. Members
must be separate failure domains when possible. Every Runtime-OS host receives
all client endpoints through `HHS_PASS218_ETCD_ENDPOINTS`; endpoint order is only
transport preference and never an authority ranking.

Each etcd member must use:

- TLS on client and peer listeners;
- a CA trusted only for the intended cluster;
- `client-cert-auth=true`;
- `peer-client-cert-auth=true`;
- a unique member name and durable data directory;
- a unique member certificate/key whose SANs match its peer/client identities;
- the same initial-cluster token and exact member set during cluster creation.

The Runtime-OS client certificate must be distinct from peer member certificates.
Do not store private keys in the repository.

## Runtime-OS environment

Use `hhs-pass218-distributed.env.example` as the shape. I11 requires:

- `HHS_PASS218_DISTRIBUTED_REQUIRED=1`
- `HHS_PASS218_OPERATIONAL_HARDENING_REQUIRED=1`
- an odd `HHS_PASS218_ETCD_ENDPOINTS` set with at least three HTTPS endpoints
- CA, client certificate, and client key paths
- a stable cluster name and HHS namespace

If this configuration is missing or invalid, Runtime-OS remains diagnostic-only;
it must not fall back to a local I9 writer or a single-endpoint I10 writer.

## Health and quorum

`GET /api/runtime/pass218/lifecycle/status` exposes only safe operational metadata:
cluster member count, quorum size, reachable member count, cluster/member/leader
IDs, linearizable-read readiness, probe Hash72, fence epoch, and canonical
checkpoint identity. Certificate/key material is never returned.

A three-member cluster remains writable with one unavailable member. With two
unavailable members, I11 closes ingestion and releases distributed writer
authority. Recovery requires a successful new quorum probe and a newly acquired
I10 global fence. A previously fenced process cannot resume as writer merely
because its network connection returns.

## Snapshot and disaster recovery

Operational snapshots are etcd snapshots, not HHS-specific substitutes. The
recommended sequence is:

1. Confirm I11 reports quorum ready and the latest I10 distributed checkpoint is
   sealed.
2. Cleanly release the current HHS writer lease, leaving the durable fence,
   last-owner witness, and canonical checkpoint in etcd.
3. Save an etcd snapshot from a healthy quorum and record snapshot status.
4. Compute the snapshot SHA-256.
5. Seal an `HHS-P218-I11-DISASTER-RECOVERY-MANIFEST-V1` that binds the snapshot
   identity/status to the exact I10 distributed checkpoint.
6. Restore the snapshot into a fresh odd-member cluster using etcd's supported
   restore tooling and the intended new member topology.
7. Start Runtime-OS with a new local persistence root and I11 configuration.
8. Require a new global fence before ingestion opens.
9. Verify exact canonical root, VM81 snapshot, consumed I6 receipt, and
   distributed checkpoint identity against the sealed manifest.

A snapshot alone is not authority. HHS authority resumes only after the restored
cluster reaches quorum, the checkpoint validates, and a new I10 fence is acquired.

## Scope boundary

Iteration 11 consumes etcd's consensus implementation. HHS does not claim to
implement Raft, etcd membership consensus, or network-partition resolution itself.
The HHS contribution is the exact binding between that external consensus
substrate and the existing Hash72 / I7 / I9 / I10 / Pass-217 / VM81 authority
chain.
