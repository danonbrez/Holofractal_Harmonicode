# HHS Metadata Enhancement Block V1

## Purpose

The Metadata Enhancement Block upgrades legacy metadata from descriptive tags into HHS witness metadata.

It records commitments to:

```text
capture context
resolution profile
semantic checksums
observer witness ID
transformation trace root
phase binding
HHS invariants
```

It does not store duplicate payload material.

## Payload Policy

```text
metadata_payload_policy = commitments_only_no_duplicate_payload
```

Raw payload fields, embedded payload fields, and duplicate payload copies are invalid.

## Transformation Trace Requirement

Every metadata enhancement block must include a transformation trace root. Metadata is part of the witnessed state and cannot be detached from the causal history of the carrier.
