# INTEGRATION REPORT PASS 015

## Objective
Ensure the runtime receipt chain consumes the Hash72 `u^72` Digital DNA state machine rather than treating Hash72 as a static digest/projection helper.

## Integration Result
The unified ledger now calls `hash72_kernel_digest()`, which derives each digest by:

1. canonicalizing the payload;
2. initializing the C-backed `HHSHash72RingState`;
3. applying deterministic toroidal rotations from the canonical payload trace;
4. relying on the C kernel compensatory rotation rule to preserve zero-sum closure;
5. exporting the resulting 72-symbol Digital DNA projection as the digest source.

This makes the ledger authority kernel-backed:

```text
payload → canonical trace → C u^72 ring rotations → zero-sum Digital DNA → Hash72 receipt digest
```

## Migration Rule
If an existing unified ledger lacks `HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1` authority metadata, it is rebuilt before new entries are appended. This prevents mixed static-digest and kernel-ring ledgers from silently coexisting.

## Performance Correction
Ledger-level digesting now uses an ordered entry-hash summary because every entry hash already binds full payload + parent. This preserves chain authority while preventing repeated full-ledger ring transport over deeply nested payloads.

## Guarded Service
`hash72.kernel_authority_self_test` is now exposed through the guarded service registry.
