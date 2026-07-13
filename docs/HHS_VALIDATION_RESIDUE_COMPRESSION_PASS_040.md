# HHS Validation Residue Compression — Pass 040

## Normative purpose

Validation expansion caches, diagnostic elaborations, and intermediate validator residues must not become a shadow memory layer. Pass 040 compresses validation residue into the canonical HHS state-machine form:

```text
previous_state_root -> compressed_state -> receipt
```

The persistent object is the Hash72/u^72 receipt chain, not the raw expansion cache.

## Invariant

```text
Validation expansion residue may be witnessed, but it may not accumulate as persistent raw memory.
```

## Required compression target

Every validation residue item is reduced to:

```text
HHS_VALIDATION_RESIDUE_COMPRESSED_STATE_V1 {
  previous_state_root,
  residue_class,
  modality_type,
  validation_surface,
  validation_status,
  residue_commitment_hash72,
  source_receipt_hash72,
  state_machine,
  hash_authority
}
```

and then witnessed by:

```text
HHS_VALIDATION_RESIDUE_RECEIPT_V1 {
  previous_state_root,
  state_root_hash72,
  residue_commitment_hash72,
  source_receipt_hash72,
  transition_receipt_hash72
}
```

## Forbidden persistence

The compressed chain rejects:

```text
raw_cache
cache_blob
validation_expansion_cache
intermediate_artifacts
parallel_memory
shadow_memory
unbounded_diagnostic_trace
external_sidecar_cache
duplicate_diagnostic_store
```

## Authority

All commitments are generated through the existing Hash72/u^72 C-kernel authority:

```text
HASH72_U72_C_KERNEL
```
