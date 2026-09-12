# Pass 219 VM81 PQC Cell-Wall Firewall v1 — Restart Checkpoint

Date: 2026-09-12

## Base and branch

```text
base main: e157ef775f5da94281573a2d428e2ddb811c385e
branch: agent/pass219-vm81-pqc-cell-wall-firewall-v1-20260912
merge target: main
```

The base is the verified merge of PR #434, which freezes Pass 219 as the permanent post-219 compositional lowering and singleton canonical-handoff membrane.

## Contract commits

```text
7d348deb7a679fa85e36662ab189caa1bc439b5e  add VM81 PQC cell-wall firewall contract v1
6e3e46f4a8de1ac40c11febf664d2bf9f0c8803d  require PQC firewall at canonical handoff
eb469db85b6c0b7459ea6212ce5569eaee3bfa0d  bind post-219 development to VM81 PQC firewall
2e474640e24e14f30cf3f25638db94963eff2a9a  bind generic substrate promotion to canonical PQC firewall
```

## Changed contract files

```text
contracts/pass219/PASS_219_VM81_PQC_CELL_WALL_FIREWALL_V1.md
contracts/pass219/PASS_219_PLUG_AND_PLAY_CANONICAL_HANDOFF_V1.md
contracts/pass219/PASS_219_POST_219_COMPOSITIONAL_DEVELOPMENT_ABI_V1.md
contracts/pass219/PASS_219_PLUG_AND_PLAY_MATHEMATICAL_LOGIC_SUBSTRATE_V1.md
```

## Frozen security relation

```text
canonical request
    ↓
Pass 219 RNA cell-wall lowering
    ↓
exact canonical instruction envelope
    ↓
VM81 PQC cell-wall firewall
    ↓ ADMIT only
inherited singleton VM81 canonical authority
    ↓
canonical mutation + Hash72 / Hash216 lineage
```

Firewall admission requires all of:

```text
valid membrane source and ordered path
valid reciprocal edge/orientation alignment
valid predecessor Hash72 lineage
valid predecessor Hash216 identity
valid required Hash216 array references
valid authorized PQC signature over the exact envelope
valid anti-replay/freshness state
no authority escalation
```

Any failure is required to halt the offending canonical execution transaction before VM81 dispatch, mutation, canonical Hash72 issuance, canonical Hash216 issuance, or persistence.

## PQC inheritance

The contract deliberately reuses the existing Pass 213 PQC authority:

```text
ML-KEM-768  recovery / encrypted-envelope KEM where required
ML-DSA-65   operational instruction authentication
SLH-DSA     archival / optional dual-signature policy
```

The firewall contract does not claim that HARMONICODE geometry replaces the cryptographic security proof of these primitives. The geometry and Hash216 state bind execution context into the signed canonical envelope.

## Validation completed

Repository comparison against the exact base established:

```text
status: ahead
behind_by: 0
ahead_by before this restart record: 4
contract files changed: 4
unrelated files changed: 0
```

The contract relationships are explicit:

```text
substrate candidate promotion -> firewall contract
post-219 canonical request -> firewall contract
canonical handoff -> firewall ADMIT before inherited VM81 authority
```

No runtime implementation was changed in this contract-only checkpoint.

## Required implementation — remaining

The next implementation iteration SHALL add the native firewall immediately in front of canonical VM81 dispatch without creating a second transition authority.

Required surfaces:

```text
canonical instruction-envelope type
deterministic signed serialization
RNA/VM81 cell-wall route verifier
predecessor Hash72 verifier
predecessor Hash216 verifier
Hash216 array-reference membership/identity verifier
Pass 213 PQC verifier-bundle binding
ML-DSA operational signature verification
policy-gated SLH-DSA dual verification
anti-replay state
fail-closed halted-state handling
```

Required negative tests include invalid source/path, missing or stale hashes, unknown/out-of-range/tombstoned Hash216 references, wrong PQC key, signature mutation, stale predecessor, replay, and authority escalation. Every failure must prove zero canonical mutation, zero canonical receipt issuance, and zero persistence.

## Next action

Implement the native Pass 219 VM81 PQC firewall beneath the canonical handoff, wire the handoff so the inherited VM81 authority is callable only after firewall ADMIT, add dependency-scoped positive/negative tests, run inherited handoff/substrate regressions plus the new firewall gate, then commit a restartable implementation checkpoint.
