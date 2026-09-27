# Pass 220 I047 Restart Record — Unified Lane 5 Production VM

Date: 2026-09-25

## Repository state

- Base main commit: `cf2764c24e85ff4980d599f528218f1328b81627`
- Branch: `pass220-i047-unified-lane5-production-vm`
- Merge target: `main`
- Purpose: replace legacy host-native production application authority with the
  already-specified persistent Ubuntu/Lane-5/VM81 production topology.

## Implemented

- QEMU loopback forwarding for SSH, Runtime OS/IDE, and application-VM API.
- Persistent production VM state root under
  `/var/lib/hhs/ubuntu-guest/machine`.
- Exact-SHA in-guest update of the same persistent Ubuntu machine.
- Existing application-VM and Runtime OS/IDE composition installed inside guest.
- Sealed Runtime OS bundle copied into guest by exact SHA.
- Host `hhs.service` replaced by VM-supervisor unit after guest acceptance.
- Reversible nginx switch from host 8080/8720 to guest 18080/18720.
- Retirement of historical host `hhs-application-vm.service`.
- Pre-cutover guest integration receipt plus post-cutover topology receipt.
- Exact-main assertions forbidding host application listeners on 8080/8720.
- Independent application-VM production workflow converted to validation only.
- I047 regression suite added to canonical `validate-candidate.sh`.

## Authority invariants

```text
host canonical authority = false
host application compute authority = false
QEMU canonical authority = false
Ubuntu transport canonical authority = false
new VM81 authority = false
new Hash72 authority = false
new Hash216 authority = false

canonical mutation path =
  existing Lane 5 zero-bypass interposer
  -> C++ RNA VM5184 cell wall
  -> PQC firewall
  -> signed environmental VM81 admission
  -> Hash72 closure
  -> Hash216 lineage
```

## Validation status

Repository changes are committed incrementally on the branch. Dependency-scoped
CI must still run on the opened PR. No live-host production cutover is claimed
until the exact-main deployment workflow completes successfully.

## Required next action

1. Open PR from `pass220-i047-unified-lane5-production-vm` to `main`.
2. Run/inspect the unified Pass 220 production contract and guarded candidate
   validation.
3. Repair forward any branch-specific failures.
4. Merge only after dependency-scoped checks are green.
5. Let exact-main promotion execute the first migration.
6. Verify the I047 guest integration and production topology receipts on the
   deployed SHA.
