# Pass 217 Iteration 2 — Machine Contracts and Reference Vectors

## Outcome

Iteration 2 completes the bounded machine-contract, schema, and reference-vector
preparation authorized by the Pass 217 implementation sequence.  It does not
materialize the 648-byte logical Genesis image, create the 1,296-byte physical
Golay ROM, modify the protected C VM81 runtime, migrate state, admit a runtime
transition, or begin Pass 219 implementation.

The bundle remains anchored to the Iteration 1 inherited-main freeze:

```text
main commit:              66c614ae1de0c1b1651451e2c406307a8dee83ed
main tree:                4d8c87797d8844b8868f6b412ba45f936731c6c4
Iteration 1 remote head:  d87f84b4171e9e4085014015ccad4d278b992feb
Iteration 1 tree:         f5b1c416afe07d6a1f1abe50447142f5a1ca2c26
Iteration 1 freeze root:  cfcacc6708697e8b5af3ccd58fca486150e21a1a6bfd115f667700adf96ed4cb
```

The inheritance gate remains:

```text
HOLD_FOR_PASS_215_216_AUTHORITATIVE_RECONCILIATION
```

Pass 215 is still unmerged and no Pass 216 branch is repository-visible.  The
hold permits this preparatory layer but blocks ROM, migration, runtime, and
transition-authority promotion.

## Generated contract set

Iteration 2 supplies the Pass 217 contract paths required for the preparatory
stage:

```text
contracts/pass217/machine_contract.json
contracts/pass217/invariants.json
contracts/pass217/address_map.schema.json
contracts/pass217/hash72.schema.json
contracts/pass217/hash216.schema.json
contracts/pass217/rom_manifest.schema.json
contracts/pass217/golay_profile.schema.json
contracts/pass217/vector_store.schema.json
contracts/pass217/reference_vectors.json
contracts/pass217/checksums.sha256
```

Every JSON artifact is generated in canonical key order with no floating-point
values.  The checksum manifest covers all nine JSON artifacts, and the evidence
manifest binds the checksum file and all generated JSON bytes.

Frozen roots:

```text
bundle root:                 7c26c890eabbe8f4b506186ea738f0a4f2efed3391d02b73477a859edcf031f9
exhaustive address-map root: c5f859161fa99daaaefc63ec540c2595045c27e8193c702d5e58970e16412a07
Hash72 matrix root:          6c0b2e9e354e8d7eb17a746d01c157b19aa95b58296884126cdf5bef7998e286
Hash216 commitment root:     e6f650eb244f99c026b7fa64ccab7e320c6d0ece62865c0039a48cde1baf4543
ordered phase surface root:  29ac857ee06dba02b1c90c68262d0f004633f9363119d12fa49e3e7d3fb822e7
Lo Shu nucleus root:         da7b33fa1a419e00ce81eeeeb5f1c435acd6ae7b95d355e3a1749a6a238e3164
```

## Exact inherited decisions

Nine source files are bound by Git blob, SHA-256, and byte length from the
Iteration 1 main snapshot.  Their dispositions are fail-closed.

### Reused

- `hhs_runtime/core/hash72_validator_v1.py` remains the canonical Hash72
  format authority.  Its exact ordered alphabet is frozen as:

  ```text
  0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?
  ```

- `hhs_runtime/core/hash72_digest_v1.py` supplies the reference-only,
  domain-separated Hash72 receipt used to test structural Hash216 layout.
- `hhs_runtime/pass175/runtime.py` supplies the exact `81 × 64` and G243
  address identities.
- `hhs_backend/runtime/hhs_pass213_compiled_rom_v1.py` supplies dimension
  constants only.  Reusing dimensions does not promote a Pass 217 ROM.
- `hhs_runtime/core_sandbox/hhs_octonion_digital_dna_u72_table_v1.py`
  supplies the ordered `(x,y,z,w,xy,yx,zw,wz)` basis candidate without
  collapsing `xy/yx` or `zw/wz`.

### Deferred or rejected

- The alternate alphabet and explicitly non-cryptographic local receipt in
  `hhs_runtime/hhs_loshu_phase_embedding_v1.py` remain compatibility material;
  they do not override the canonical Hash72 format.
- Pass 175 `predecessor/current/successor` lanes are not silently relabeled as
  Pass 217 `previous/next/receipt`.  A later migration adapter must prove the
  relation.
- `hhs_runtime/core_sandbox/hhs_security_armor_v1.py` explicitly labels its
  Golay hook a placeholder.  It is rejected as an extended binary Golay
  `[24,12,8]` implementation authority.

## Reference coverage

The reference vector bundle proves the following preparatory identities:

```text
81 × 64 = 5,184 = 72 × 72
5,184 bits = 648 bytes
8 × 8 = 64 ordered phase-pair positions per VM81 cell
81² = 6,561 ordered reciprocal cell relations
5,184 × 243 = 1,259,712 projected addresses
5,184 / 12 = 432 Golay payload words
432 × 24 = 10,368 physical bits = 1,296 bytes
```

All 5,184 permanent addresses are exhaustively reconstructed through:

```text
s = 64*c + o
o = 8*alpha + beta
s = 72*r + k
q = 243*s + g
```

The Hash72 reference matrix uses the contracted circulant phase-index rule and
tests `x`, `y`, `z`, and `w` orbit closure and inversion.  The 5,184-byte
matrix is a phase-coordinate reference only; it is not the logical Genesis
ROM.

The Hash216 structural vector fixes:

```text
previous[72] || next[72] || receipt[72]
```

and produces 216 position-distinct SHA-256 commitments.  Its receipt is
reference-only and was not admitted by VM81, so it is not authoritative
transition evidence.

The Golay vectors freeze `[24,12,8]` dimensions and the mixed bound
`2e+s<=7`.  No generator matrix, codeword, decoder, interleaver, correction,
or physical ROM is created in this iteration.

## Reproduction

Regenerate the complete deterministic bundle:

```bash
python tools/pass217_iteration2_machine_contracts.py \
  --repository-root . \
  --write
```

Validate without rewriting artifacts:

```bash
bash scripts/run_pass217_iteration2_validation.sh
```

The cumulative validator reruns Iteration 1, rebuilds the complete Iteration 2
bundle byte-for-byte, executes exhaustive address and orbit tests, checks all
source-object bindings, rejects bundle tampering, audits authoritative Python
and JSON for floating-point values, and proves the protected C runtime remains
unchanged.

## Next bounded action

The contracted next stage is generation of the canonical Genesis candidate and
address maps.  That stage remains blocked from authority promotion until the
Pass 215/216 predecessor lineage is reconciled into the repository or an
explicit new authority permits a strictly non-promotional candidate build.
