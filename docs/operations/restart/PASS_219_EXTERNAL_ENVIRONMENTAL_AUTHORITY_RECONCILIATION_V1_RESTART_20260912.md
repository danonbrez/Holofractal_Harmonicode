# Pass 219 External + Environmental Authority Reconciliation v1 — Restart Checkpoint

Date: 2026-09-12

## Base / branch / merge target

```text
base main: e157ef775f5da94281573a2d428e2ddb811c385e
branch: agent/pass219-external-runtime-authority-closure-v1-20260912
merge target: main
```

Current comparison at checkpoint creation:

```text
status: ahead
ahead_by: 59
behind_by: 0
merge_base: e157ef775f5da94281573a2d428e2ddb811c385e
```

## Reconciliation ancestry

The previously parallel security lines were reconciled by a true two-parent merge rather than by flattening either history:

```text
0c67f389c6044638731791ca6da8d8976ed4ad42
  parent 1: 3bf5ed3d6fb4ee48ee4d0d1ce5397d376e7c786c
            agent/pass219-external-runtime-authority-closure-v1-20260912
  parent 2: 015f1e29eb2e9032d70991c1a5b7712929398cab
            agent/pass219-vm81-pqc-cell-wall-firewall-v1-20260912
```

The external-authority branch was selected as the executable implementation base because it already contained the native 1.30 firewall, C++ RNA cell-wall bridge, 1.31 asymmetric PQ-signature boundary, public-lowering closure, Python ctypes/runtime authority repairs, tests, and CI.

The sibling environmental/PQC contracts were then carried forward on that implementation lineage.

## Reconciled authority order

```text
Pass 220+ proposal
  -> Pass 219 candidate composition
  -> RNA C++ cell-wall lowering
  -> Hash216 parent provenance validation
  -> 1.32 environmental Genesis/witness gate
  -> environmental PQ signature verification
  -> hidden 1.31 instruction PQ signature boundary
  -> hidden 1.30 provenance/HMAC membrane
  -> hidden RNA composed canonical admission
  -> Hash216 child validation
  -> singleton VM81 canonical commit / inherited receipt
```

Production dynamic mutation authority is intended to be singular:

```text
public:
  hhs_exact_pass219_vm81_environment_admit_signed

hidden mutation primitives:
  hhs_exact_vm81_admit_uqcel
  hhs_exact_pass219_admit_composed
  hhs_exact_pass219_rna_admit_composed
  hhs_exact_pass219_vm81_pqc_admit
  hhs_exact_pass219_vm81_pqc_admit_signed
  hhs_exact_pass219_vm81_environment_checkpoint_seal
```

Public recovery returns a candidate only and owns no VM81/Hash72/Hash216/persistence authority.

## Implementation commits after reconciliation

```text
af4c8a6b29495799c5a26b0f6752f818e20e2c83  add Pass 219 VM81 environmental recovery 1.32 ABI
715da0a37b2963c5f5a9dd3a8e96751686e2beaa  implement VM81 environmental witness freeze recovery 1.32
9b3e6af2a7043196cd8aa054404bb6f74e49cba7  add environmental halt classes to VM81 PQC firewall
14e00165d5b4078937e60cfa205a1d5be7137d60  make PQC 1.31 admission internal beneath environmental 1.32
c824e7b1b887950faeea84949a6c8f15b2286683  aggregate VM81 environmental recovery 1.32
9d5237065907d72bcb5d5b52e9ee41daa6f413df  expose VM81 environmental recovery 1.32 ABI
9b2cdcb9b731d7e5482109cfeb347e2d02dec8b6  route post-219 canonical requests through environmental 1.32
dda2862ede91ff54a4729bcafbb5fe7d1e887d20  route PQC signature regression through environmental 1.32
88cec8e4aa36a6447ed9adc7389d0f714c35a34d  add VM81 environmental recovery and anti-rollback conformance
3e02d95d91dffe037d6eaad1ceab87affc5f25b9  reconcile external and environmental VM81 authority contract
a1175710ead3333e76e1e2834ba7f342fcb4f686  validate reconciled VM81 PQC environmental authority boundary
2beb6b3d84dcdb3d653f55ed9cb35eb1e1ff26d3  make environmental recovery test strict C++17
```

## New native 1.32 mechanics

### Genesis security measurement

The native core freezes a deterministic, domain-separated Genesis measurement under the existing 512-bit VM81 firewall root. The first implementation binds:

```text
1.30 firewall version
1.31 signature version
1.32 environmental version
RNA ABI version
VM81 frame size
OpenSSL runtime/provider identity string
```

Each canonical request re-measures this surface and compares it to the frozen epoch root.

This is a bounded software measurement. It does not claim unimplemented hardware/firmware/physical side-channel attestation.

### Temporal environmental witness

Every accepted request binds:

```text
Genesis root
prior witness root
monotonic witness sequence
anti-rollback floor
parent Hash216 transition identity
candidate Hash72
```

The witness is kernel-authenticated and independently signed/verified using the selected 1.31 ML-DSA or SLH-DSA profile before the hidden 1.31 instruction boundary can run.

### Freeze coupling

Environmental mismatch or environmental PQ-signature failure sets the 1.32 state to `FROZEN` and latches the inherited firewall halt before canonical mutation.

An inner 1.31/1.30 security halt also freezes the 1.32 environment state.

Normal mathematical constraint rejection remains distinct from a security halt.

### Hash216 registry reconciliation

The public pure registry verifier hashes an exact ordered sequence of:

```text
position
live/tombstone state
identity SHA-256
lineage SHA-256
```

Positions must match their ordered index and the registry is bounded to 216 entries in this v1 native surface.

### Verified recovery

Recovery checkpoint verification binds:

```text
security epoch
checkpoint sequence
anti-rollback floor
expected candidate Hash72
ordered registry root/count
exact candidate frame
checkpoint root
kernel HMAC-SHA-512 authenticator
```

Successful recovery:

```text
returns candidate only
advances anti-rollback floor to checkpoint sequence
clears inherited firewall halt only after all implemented recovery predicates pass
returns environment to RUNNING
does not mint canonical receipt or commit VM81 state
```

The recovered candidate must still traverse the ordinary public 1.32 admission path for canonical execution.

Failed recovery transitions to `RECOVERY_HALTED`; no weaker automatic fallback exists.

## Pass 213 integration boundary

The repository already contains Pass 213 persistent inventory, PQC checkpoint, and RFC 3161 timestamp machinery.

This checkpoint does not falsely claim that those Python/runtime records are already wired into the new native 1.32 checkpoint envelope. The implemented native core currently provides the kernel-authenticated checkpoint/registry/anti-rollback mechanics. Direct executable binding to the full Pass 213 persistent-inventory + PQC + RFC3161 lineage remains a successor integration task.

## Tests / CI

Updated dedicated workflow:

```text
.github/workflows/pass219-vm81-pqc-signature-boundary-v1.yml
```

The workflow now requires:

```text
1.32 public mutation symbol present
1.30 / 1.31 / raw / RNA mutation symbols absent from dynamic exports
internal checkpoint seal absent from dynamic exports
public candidate-only recovery verifier present
public Hash216 registry verifier present
system-provider PQC absence fails closed
OpenSSL 3.5 ML-DSA positive execution
OpenSSL 3.5 SLH-DSA positive execution
canonical constraint rejection remains non-security rejection
environmental recovery + anti-rollback conformance
post-219 candidate-development regression
static no-self-vouching authority audit
```

Dedicated run started at this checkpoint lineage:

```text
run: 34695389981
head at launch: 2beb6b3d84dcdb3d653f55ed9cb35eb1e1ff26d3
jobs:
  system-provider: in progress
  openssl-35-positive: in progress
```

Per repository policy, slow external CI is not a reason to withhold a restartable implementation checkpoint. Any CI-discovered defect is repair-forward on this same branch.

## Changed implementation surfaces relative to main

Relevant reconciled/new surfaces include:

```text
contracts/pass219/PASS_219_VM81_PQC_FIREWALL_EXTERNAL_AUTHORITY_CLOSURE_V1.md
contracts/pass219/PASS_219_VM81_PQC_SIGNATURE_BOUNDARY_V1.md
contracts/pass219/PASS_219_VM81_PQC_CELL_WALL_FIREWALL_V1.md
contracts/pass219/PASS_219_VM81_ENVIRONMENTAL_WITNESS_RECOVERY_V1.md
contracts/pass219/PASS_219_VM81_EXTERNAL_ENVIRONMENTAL_AUTHORITY_RECONCILIATION_V1.md
hhs_runtime/include/hhs_pass219_vm81_pqc_firewall_1_30.h
hhs_runtime/include/hhs_pass219_vm81_pqc_signature_1_31.h
hhs_runtime/include/hhs_pass219_vm81_environmental_recovery_1_32.h
hhs_runtime/c/hhs_pass219_vm81_pqc_firewall_1_30.inc
hhs_runtime/c/hhs_pass219_vm81_pqc_signature_1_31.inc
hhs_runtime/c/hhs_pass219_vm81_environmental_recovery_1_32.inc
hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp
hhs_runtime/include/hhs_pass219_post219_compositional_development_1_29.hpp
hhs_runtime/c/hhs_runtime_exact_abi.c
hhs_runtime/include/hhs_runtime_exact_abi.h
tests/pass219/test_pass219_vm81_pqc_firewall_1_30.cpp
tests/pass219/test_pass219_vm81_pqc_signature_1_31.cpp
tests/pass219/test_pass219_vm81_environmental_recovery_1_32.cpp
.github/workflows/pass219-vm81-pqc-signature-boundary-v1.yml
```

The branch also retains all earlier external-runtime-authority closure repairs to Python bridges/controller and public RNA/UQCEL mutation surfaces.

## Remaining validation / repair-forward

1. Read the result of run `34695389981` when available.
2. Repair only any failing build/test/symbol-audit surface; preserve the two-parent reconciliation commit and singleton authority ordering.
3. Re-run the impacted dedicated job(s), not unrelated historical suites.
4. Bind the native recovery checkpoint to Pass 213 persistent-inventory/PQC/RFC3161 records in a successor iteration if full external timestamp authority is required.
5. After dedicated validation is green, merge the unified PR into `main` and verify exact-main authority symbols.

## Next action

Continue from the branch head recorded by GitHub after this restart-record commit. Inspect dedicated CI first; if green, merge-ready the unified external+environmental authority PR. If red, repair the exact failing stage and rerun dependency-scoped validation.
