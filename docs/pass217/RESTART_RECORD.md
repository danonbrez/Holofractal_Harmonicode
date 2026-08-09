# Pass 217 Restart Record

## Current iteration

```text
pass: 217
iteration: 2
classification: HHS_PASS_217_ITERATION_2_SCHEMA_REFERENCE_PROFILE_FROZEN
branch: agent/pass217-genesis-inventory-iteration1
remote PR: 179
merge target: main
frozen main commit: 66c614ae1de0c1b1651451e2c406307a8dee83ed
frozen main tree: 4d8c87797d8844b8868f6b412ba45f936731c6c4
Iteration 1 remote parent: d87f84b4171e9e4085014015ccad4d278b992feb
Iteration 1 tree: f5b1c416afe07d6a1f1abe50447142f5a1ca2c26
validated Iteration 2 implementation commit: 40b750db763b08d02dd45afb05848e2a4953721b
validated Iteration 2 implementation tree: b1cf971ee6c2954e04131af599701ef2135b819d
restart checkpoint: the commit containing this record
```

## Changed files

```text
.github/workflows/pass217-iteration2-machine-contracts.yml
contracts/pass217/address_map.schema.json
contracts/pass217/checksums.sha256
contracts/pass217/golay_profile.schema.json
contracts/pass217/hash216.schema.json
contracts/pass217/hash72.schema.json
contracts/pass217/invariants.json
contracts/pass217/machine_contract.json
contracts/pass217/reference_vectors.json
contracts/pass217/rom_manifest.schema.json
contracts/pass217/vector_store.schema.json
docs/pass217/ITERATION_2_MACHINE_CONTRACTS.md
docs/pass217/RESTART_RECORD.md
evidence/pass217/PASS_217_ITERATION_2_MACHINE_CONTRACTS.json
hhs_backend/runtime/hhs_pass217_machine_contracts_v1.py
scripts/run_pass217_iteration2_validation.sh
tests/test_hhs_pass217_machine_contracts_v1.py
tools/pass217_iteration2_machine_contracts.py
```

## Implemented state

- Canonical machine contract, invariant registry, and six required JSON
  schemas are present.
- All generated JSON and checksum/evidence bytes rebuild deterministically.
- Nine inherited candidate sources are bound to exact frozen-base Git objects
  with explicit reuse, compatibility, defer, or rejection dispositions.
- The inherited canonical Hash72 alphabet is selected; an alternate local
  alphabet cannot override it.
- All 5,184 VM5184 addresses round-trip across cell/operation, phase-pair, and
  Hash72 matrix views.
- G243 projection remains exact and inherited.
- The ordered phase registry and pointwise Lo Shu nucleus are frozen.
- Hash216 `previous/next/receipt` structural layout and 216 positional
  commitments are deterministic but non-authoritative.
- Extended Golay `[24,12,8]` sizes and bounded error/erasure policy are frozen;
  placeholder hooks are not promoted as codecs.
- Vector similarity remains candidate discovery only and cannot bypass VM81.

## Validation state

Completed before the implementation checkpoint:

```text
Iteration 1 baseline validation: passed
Iteration 1 tests: 10 passed
Iteration 2 focused tests: 14 passed
Iteration 2 bundle generation/rebuild: passed
Python compilation: passed
validation command: bash scripts/run_pass217_iteration2_validation.sh
Iteration 1 test wall time: 35.762 seconds
Iteration 2 test wall time: 0.286 seconds
validation result: PASS217_ITERATION2_VALIDATION_OK
```

Frozen generated roots:

```text
bundle root:                 7c26c890eabbe8f4b506186ea738f0a4f2efed3391d02b73477a859edcf031f9
exhaustive address-map root: c5f859161fa99daaaefc63ec540c2595045c27e8193c702d5e58970e16412a07
Hash72 matrix root:          6c0b2e9e354e8d7eb17a746d01c157b19aa95b58296884126cdf5bef7998e286
Hash216 commitment root:     e6f650eb244f99c026b7fa64ccab7e320c6d0ece62865c0039a48cde1baf4543
ordered phase surface root:  29ac857ee06dba02b1c90c68262d0f004633f9363119d12fa49e3e7d3fb822e7
Lo Shu nucleus root:         da7b33fa1a419e00ce81eeeeb5f1c435acd6ae7b95d355e3a1749a6a238e3164
```

Remaining checkpoint procedure:

```text
commit the restart checkpoint
rerun the cumulative validator on the exact checkpoint head
publish the exact validated tree to PR #179
verify the remote exact-head workflow and retained artifact
```

Validation environment:

```text
Python 3.12.13
git 2.51.1
Linux 6.18.35 x86_64
PYTHONHASHSEED=0
PYTHONDONTWRITEBYTECODE=1
```

## Authority and blockers

```text
protected C runtime modified: false
runtime mutation performed: false
canonical authority promoted: false
logical Genesis ROM generated: false
Golay physical ROM generated: false
Golay codec implemented: false
migration active: false
Hash72 authoritative transition minted: false
Hash216 authoritative transition minted: false
Pass 217 implementation complete: false
Pass 219 runtime implementation started: false

inheritance status:
HOLD_FOR_PASS_215_216_AUTHORITATIVE_RECONCILIATION
```

Pass 215 remains unmerged and no Pass 216 branch is repository-visible.  The
hold blocks Iteration 3 authority promotion.  It does not invalidate the
completed Iteration 2 schema/reference-vector freeze.

## Next action

After exact-head checkpointing and remote CI, preserve this bundle.  Begin
Iteration 3 only after the predecessor gate is reconciled or an explicit
bounded authority permits a non-promotional Genesis candidate build.
