# Pass 219 VM81 PQC Cell-Wall Firewall v1 — Restart Checkpoint

Date: 2026-09-12

## Base and branch

```text
base main: e157ef775f5da94281573a2d428e2ddb811c385e
branch: agent/pass219-vm81-pqc-cell-wall-firewall-v1-20260912
merge target: main
PR: #435
```

The base is the verified merge of PR #434, which freezes Pass 219 as the permanent post-219 compositional lowering and singleton canonical-handoff membrane.

## Contract commits

```text
7d348deb7a679fa85e36662ab189caa1bc439b5e  add VM81 PQC cell-wall firewall contract v1
6e3e46f4a8de1ac40c11febf664d2bf9f0c8803d  require PQC firewall at canonical handoff
eb469db85b6c0b7459ea6212ce5569eaee3bfa0d  bind post-219 development to VM81 PQC firewall
2e474640e24e14f30cf3f25638db94963eff2a9a  bind generic substrate promotion to canonical PQC firewall
b9c07b12f2f2a09159a517011f796921ed3eeff5  freeze restartable contract checkpoint
3dca49dcebd75aee9b653e6515a1a1207fab992c  add environmental witness and verified recovery contract
```

## Changed contract files

```text
contracts/pass219/PASS_219_VM81_PQC_CELL_WALL_FIREWALL_V1.md
contracts/pass219/PASS_219_VM81_ENVIRONMENTAL_WITNESS_RECOVERY_V1.md
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
    ↓ requires fresh valid environmental witness
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
fresh environment witness bound to the active security epoch
no authority escalation
```

Any failure is required to halt the offending canonical execution transaction before VM81 dispatch, mutation, canonical Hash72 issuance, canonical Hash216 issuance, or persistence.

## Environmental witness extension

The new companion contract defines one immutable Genesis Security Root per authorized security epoch.

The root binds the security-critical baseline, including:

```text
Pass 219 contract-set digest
canonical kernel / VM81 ABI / RNA membrane identities
compiled-ROM identity root
canonical Hash216 registry root
persistent inventory root
PQC verifier-bundle root
environmental measurement policy root
recovery policy root
anti-rollback floor
prior security epoch root
```

Runtime measurements are typed as immutable, policy-bounded, or ephemeral. Only authenticated measured surfaces can participate in the integrity claim; unmeasured physical or side-channel conditions are explicitly outside proof scope.

A temporal witness chain binds the current environment, predecessor Hash216 identity, persistent inventory root, Hash216 registry root, PQC verifier root, monotonic state, and timestamp reference.

Canonical dispatch is therefore strengthened to:

```text
CanonicalVM81Dispatch(I_t)
⇒ VM81_PQC_FIREWALL_ADMIT(I_t)
∧ ENVIRONMENT_OK(W_t, G_e)
∧ instruction_binds_witness(I_t, root(W_t))
∧ inherited_singleton_kernel_revalidation(I_t)
```

## Frozen recovery relation

A confirmed environmental divergence latches `FREEZE` and enters:

```text
RUNNING
  ↓
FREEZE
  ↓
ISOLATE
  ↓
SELECT_RECOVERY_CHECKPOINT
  ↓
VERIFY_CHECKPOINT_AUTHORITY
  ↓
VERIFY_TEMPORAL_ANCHOR
  ↓
VERIFY_ANTI_ROLLBACK
  ↓
RECONCILE_PERSISTENT_INVENTORY
  ↓
RECONCILE_HASH216_REGISTRY
  ↓
REBUILD_CANDIDATE_STATE
  ↓
REMEASURE_ENVIRONMENT
  ↓
FIREWALL_REENTRY_CHECK
  ↓
SINGLETON_VM81_REVALIDATION
  ↓
RUNNING
```

Any failure enters `RECOVERY_HALTED`; there is no automatic policy weakening.

The hostile/invalid input may trigger recovery but may not define the recovery program, choose a checkpoint, modify the anti-rollback floor, rotate keys, or mint recovery receipts.

## Hash216 recovery rule

The vector store/cache is an authenticated execution index, not a self-authenticating trust root.

Full resurrection requires exact equality between the locally reconstructed registry and an independently authenticated checkpoint registry:

```text
expected root == checkpoint Hash216 registry root
actual local root == checkpoint Hash216 registry root
expected keyset == actual keyset
all positional indexes equal
all identities equal
all live/tombstone states equal
all predecessor lineage equal
```

Missing, unexpected, reordered, stale, tombstoned-as-live, identity-mismatched, or lineage-mismatched entries abort recovery.

A simultaneously altered runtime image and local cache cannot establish trust merely by agreeing with each other. Recovery must independently validate the expected root through the inherited PQC-signed checkpoint/persistent-inventory/timestamp/verifier lineage.

## Persistent recovery inheritance

The extension reuses Pass 213 rather than creating a second persistence system:

```text
authenticated append-only ADMIT / RECOVER / TOMBSTONE inventory
checkpoint chain
PQC checkpoint signatures
ML-KEM recovery enclosure where required
RFC 3161 timestamp evidence where policy requires it
protected compiled-ROM carriers
reconciliation against protected memory
```

Tombstoned entries cannot be resurrected. Missing live entries can be reconstructed only from authenticated retained carrier/checkpoint material and must re-pass inherited identity/admission checks.

## PQC inheritance

The contract deliberately reuses the existing Pass 213 PQC authority:

```text
ML-KEM-768  recovery / encrypted-envelope KEM where required
ML-DSA-65   operational instruction authentication
SLH-DSA     archival / optional dual-signature policy
```

The firewall contract does not claim that HARMONICODE geometry replaces the cryptographic security proof of these primitives. Geometry, route state, environmental witness state, and Hash216 coordinates are execution context bound into authenticated envelopes.

## Security claim boundary

The contract does not encode universal exploit immunity.

It proves only represented predicates under the trusted-root assumptions. Residual risks include implementation bugs, compromised authorized keys, unmeasured firmware/hardware state, side channels outside the measurement policy, and denial-of-service through repeated valid freeze triggers.

The recovery policy therefore includes bounded retries/backoff/quarantine and ends in `RECOVERY_HALTED` rather than weakening integrity checks.

## Validation completed

Repository comparison against the exact base originally established:

```text
status: ahead
behind_by: 0
contract-only lineage
unrelated files changed: 0
```

The inherited Pass 213 persistent inventory implementation was inspected before defining the recovery extension. It already validates authenticated event/checkpoint chains, detects table/root divergence, preserves tombstones, reconstructs missing live entries from retained authenticated carriers, and reconciles expected live entries against protected storage.

No native runtime implementation has yet been changed on this branch.

## Required implementation — remaining

The next implementation iteration SHALL add the native firewall and environmental recovery membrane immediately in front of canonical VM81 dispatch without creating a second transition authority.

Required instruction-firewall surfaces:

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
```

Required environment/recovery surfaces:

```text
GenesisSecurityRootV1
EnvironmentalMeasurementPolicyV1
EnvironmentalWitnessV1 + witness-chain validator
per-dispatch witness freshness binding
latched VM81 freeze state
quarantine/zeroization of uncommitted candidate state
anti-rollback recovery checkpoint selector
Pass 213 inventory reconciliation adapter
full Hash216 registry reconciliation
replay-equal deterministic rebuild
clean-environment remeasurement
ordinary firewall reentry
singleton VM81 revalidation
```

Required negative tests include invalid source/path, missing/stale hashes, unknown/out-of-range/tombstoned Hash216 references, wrong PQC key, signature mutation, stale predecessor, replay, authority escalation, environment root mismatch, witness-chain discontinuity, stale witness, old checkpoint below rollback floor, invalid PQC/timestamp checkpoint, inventory divergence, Hash216 positional/identity/lineage mismatches, simultaneous local-runtime/local-cache alteration against an independent anchor, nondeterministic rebuild, persistent compromise after rebuild, and repeated recovery failure.

Every failure must prove zero new canonical mutation, zero canonical receipt issuance, and zero unauthorized persistence.

## Next action

Implement the combined native Pass 219 VM81 PQC + environmental witness admission membrane, then implement the isolated verified-recovery state machine beneath the same singleton canonical boundary. Run dependency-scoped firewall/recovery tests plus inherited Pass 213 inventory/PQC/timestamp regressions and Pass 219 handoff/substrate regressions, commit a restartable implementation checkpoint, and only then advance PR #435 toward merge.