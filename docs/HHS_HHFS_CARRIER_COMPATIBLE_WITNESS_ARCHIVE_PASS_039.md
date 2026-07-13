# HHS HHFS Carrier-Compatible Witness Archive Specification — Pass 039

## Normative Rule

HHFS is a carrier-compatible witness layer. It may bind a legacy carrier to HHS state, but it must not create a hidden parallel archive.

```text
legacy carrier payload + carrier-native witness capsule + bounded ECC + transformation history
```

is valid.

```text
legacy file + sidecar archive + hidden resolver + duplicate payload store
```

is invalid.

## Allowed Auxiliary Lanes

Only the following auxiliary lanes are permitted:

```text
carrier_native_payload_commitment
carrier_native_witness_capsule
metadata_enhancement
transformation_history
error_correction
```

## Forbidden Lanes

```text
external_sidecar
sidecar_manifest
remote_resolver
shadow_archive
parallel_archive
duplicate_payload
payload_copy
raw_payload_copy
external_database
alternate_block_store
```

## Carrier Profiles

The initial Pass 039 implementation declares carrier-native witness lanes for PNG, JPEG, MP3, WAV, and plain text.

## Backwards Compatibility Requirement

Every HHFS-bound carrier must remain valid in its original legacy modality. Non-HHS software should still be able to display, play, or read the carrier according to ordinary carrier behavior.

## Phase Continuity Binding

Pass 039 inherits the Pass 038 invariant:

```text
A derived HHS object is either a witnessed continuation or a new Genesis object, never an unwitnessed continuation.
```

HHFS carrier binding does not weaken Genesis severance or transformation permanence.
